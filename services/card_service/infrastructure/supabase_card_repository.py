"""
Card Service Infrastructure - Supabase Card Repository

Uses Supabase REST API Client instead of direct PostgreSQL connection.
This avoids firewall issues with port 5432.
"""

import logging
from typing import List, Optional
from uuid import UUID
from datetime import datetime
import json

from supabase import create_client, Client

from core.card_service.domain.card_entity import BaseCard, CardResponse
from core.card_service.domain.card_types import CardType as CardTypeEnum

logger = logging.getLogger(__name__)


class SupabaseCardRepository:
    """Repository for card CRUD operations using Supabase REST API"""

    TABLE_NAME = "context_cards"

    def __init__(self, supabase_url: str, supabase_key: str):
        """
        Initialize Supabase card repository.
        
        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase API key (anon or service role)
        """
        self.client: Client = create_client(supabase_url, supabase_key)
        logger.info(f"✅ Supabase card repository initialized: {supabase_url}")

    async def create(
        self,
        tenant_id: UUID,
        card_type: CardTypeEnum,
        title: str,
        content: dict,
        metrics: dict = None,
        notes: str = "",
        created_by: Optional[UUID] = None,
    ) -> BaseCard:
        """Create a new card"""
        logger.info(f"📝 Creating card: {card_type.value} for tenant {tenant_id}")

        # Soft delete existing active card of same type
        await self._soft_delete_existing_card(tenant_id, card_type)

        # Prepare data
        data = {
            "tenant_id": str(tenant_id),
            "card_type": card_type.value,
            "title": title,
            "content": content,
            "metrics": metrics or {},
            "notes": notes,
            "created_by": str(created_by) if created_by else None,
            "version": 1,
            "is_active": True,
        }

        try:
            result = self.client.table(self.TABLE_NAME).insert(data).execute()
            card_dict = result.data[0]
            logger.info(f"✅ Card created: {card_dict['id']}")
            return self._dict_to_card(card_dict)
        except Exception as e:
            logger.error(f"❌ Failed to create card: {str(e)}")
            raise

    async def get_by_id(self, card_id: UUID, tenant_id: UUID) -> Optional[BaseCard]:
        """Get card by ID"""
        logger.info(f"🔍 Getting card: {card_id}")

        try:
            result = (
                self.client.table(self.TABLE_NAME)
                .select("*")
                .eq("id", str(card_id))
                .eq("tenant_id", str(tenant_id))
                .eq("is_active", True)
                .execute()
            )

            if result.data:
                logger.info(f"✅ Card found: {card_id}")
                return self._dict_to_card(result.data[0])
            else:
                logger.info(f"⚠️ Card not found: {card_id}")
                return None
        except Exception as e:
            logger.error(f"❌ Failed to get card: {str(e)}")
            raise

    async def list_by_tenant(
        self, tenant_id: UUID, card_type: Optional[CardTypeEnum] = None
    ) -> List[BaseCard]:
        """List all cards for a tenant"""
        logger.info(f"📋 Listing cards for tenant: {tenant_id}, type: {card_type}")

        try:
            query = (
                self.client.table(self.TABLE_NAME)
                .select("*")
                .eq("tenant_id", str(tenant_id))
                .eq("is_active", True)
            )

            if card_type:
                query = query.eq("card_type", card_type.value)

            result = query.execute()
            logger.info(f"✅ Found {len(result.data)} cards")
            return [self._dict_to_card(card_dict) for card_dict in result.data]
        except Exception as e:
            logger.error(f"❌ Failed to list cards: {str(e)}")
            raise

    async def update(
        self,
        card_id: UUID,
        tenant_id: UUID,
        title: Optional[str] = None,
        content: Optional[dict] = None,
        metrics: Optional[dict] = None,
        notes: Optional[str] = None,
    ) -> BaseCard:
        """Update a card"""
        logger.info(f"✏️ Updating card: {card_id}")

        # Build update data (only include provided fields)
        update_data = {
            "updated_at": datetime.utcnow().isoformat(),
        }

        if title is not None:
            update_data["title"] = title
        if content is not None:
            update_data["content"] = content
        if metrics is not None:
            update_data["metrics"] = metrics
        if notes is not None:
            update_data["notes"] = notes

        try:
            result = (
                self.client.table(self.TABLE_NAME)
                .update(update_data)
                .eq("id", str(card_id))
                .eq("tenant_id", str(tenant_id))
                .execute()
            )
            logger.info(f"✅ Card updated: {card_id}")
            return self._dict_to_card(result.data[0])
        except Exception as e:
            logger.error(f"❌ Failed to update card: {str(e)}")
            raise

    async def delete(self, card_id: UUID, tenant_id: UUID) -> None:
        """Soft delete a card"""
        logger.info(f"🗑️ Deleting card: {card_id}")

        try:
            self.client.table(self.TABLE_NAME).update(
                {"is_active": False, "updated_at": datetime.utcnow().isoformat()}
            ).eq("id", str(card_id)).eq("tenant_id", str(tenant_id)).execute()
            logger.info(f"✅ Card deleted: {card_id}")
        except Exception as e:
            logger.error(f"❌ Failed to delete card: {str(e)}")
            raise

    async def _soft_delete_existing_card(
        self, tenant_id: UUID, card_type: CardTypeEnum
    ) -> None:
        """Soft delete existing active card of same type"""
        logger.info(f"🔄 Soft deleting existing {card_type.value} card for tenant {tenant_id}")

        try:
            # Find existing active card of same type
            result = (
                self.client.table(self.TABLE_NAME)
                .select("id")
                .eq("tenant_id", str(tenant_id))
                .eq("card_type", card_type.value)
                .eq("is_active", True)
                .execute()
            )

            if result.data:
                # Soft delete it
                for card in result.data:
                    self.client.table(self.TABLE_NAME).update(
                        {"is_active": False, "updated_at": datetime.utcnow().isoformat()}
                    ).eq("id", card["id"]).execute()
                    logger.info(f"✅ Soft deleted existing card: {card['id']}")
        except Exception as e:
            logger.error(f"⚠️ Failed to soft delete existing card: {str(e)}")
            # Don't raise - continue with creation

    async def get_relationships(self, card_id: UUID) -> List[dict]:
        """Get card relationships"""
        logger.info(f"🔗 Getting relationships for card: {card_id}")

        try:
            result = (
                self.client.table("card_relationships")
                .select("*")
                .eq("source_card_id", str(card_id))
                .execute()
            )
            logger.info(f"✅ Found {len(result.data)} relationships")
            return result.data
        except Exception as e:
            logger.error(f"❌ Failed to get relationships: {str(e)}")
            raise

    async def create_relationship(
        self,
        source_card_id: UUID,
        target_card_id: UUID,
        relationship_type: str,
        strength: float = 0.8,
    ) -> dict:
        """Create a relationship between two cards"""
        logger.info(
            f"🔗 Creating relationship: {source_card_id} -> {target_card_id} ({relationship_type})"
        )

        data = {
            "source_card_id": str(source_card_id),
            "target_card_id": str(target_card_id),
            "relationship_type": relationship_type,
            "strength": strength,
        }

        try:
            result = self.client.table("card_relationships").insert(data).execute()
            logger.info(f"✅ Relationship created")
            return result.data[0]
        except Exception as e:
            logger.error(f"❌ Failed to create relationship: {str(e)}")
            raise

    def _dict_to_card(self, card_dict: dict) -> BaseCard:
        """Convert dict from Supabase to BaseCard object"""
        return BaseCard(
            id=UUID(card_dict["id"]) if isinstance(card_dict["id"], str) else card_dict["id"],
            tenant_id=UUID(card_dict["tenant_id"]) if isinstance(card_dict["tenant_id"], str) else card_dict["tenant_id"],
            card_type=CardTypeEnum(card_dict["card_type"]),
            title=card_dict["title"],
            content=card_dict.get("content", {}),
            metrics=card_dict.get("metrics", {}),
            notes=card_dict.get("notes", ""),
            version=card_dict.get("version", 1),
            is_active=card_dict.get("is_active", True),
            created_by=UUID(card_dict["created_by"]) if card_dict.get("created_by") else None,
            created_at=datetime.fromisoformat(card_dict["created_at"]) if card_dict.get("created_at") else datetime.utcnow(),
            updated_at=datetime.fromisoformat(card_dict["updated_at"]) if card_dict.get("updated_at") else datetime.utcnow(),
        )

