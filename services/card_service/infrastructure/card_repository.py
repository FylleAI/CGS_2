"""
Card Service Infrastructure - Card Repository
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base

from services.content_workflow.card_service.domain.card_entity import (
    BaseCard,
    CardResponse,
    CardType,
)
from services.content_workflow.card_service.domain.card_types import CardType as CardTypeEnum

Base = declarative_base()


class CardRepository:
    """Repository for card CRUD operations"""

    def __init__(self, session: AsyncSession):
        self.session = session

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

        # Soft delete existing active card of same type
        await self._soft_delete_existing_card(tenant_id, card_type)

        # Create new card
        query = text("""
            INSERT INTO context_cards
            (tenant_id, card_type, title, content, metrics, notes, created_by, version)
            VALUES (:tenant_id, :card_type, :title, :content, :metrics, :notes, :created_by, 1)
            RETURNING *
        """)

        result = await self.session.execute(
            query,
            {
                "tenant_id": str(tenant_id),
                "card_type": card_type.value,
                "title": title,
                "content": content,
                "metrics": metrics or {},
                "notes": notes,
                "created_by": str(created_by) if created_by else None,
            },
        )
        await self.session.commit()

        return result.fetchone()

    async def get_by_id(self, card_id: UUID, tenant_id: UUID) -> Optional[BaseCard]:
        """Get card by ID"""

        query = text("""
            SELECT * FROM context_cards
            WHERE id = :card_id AND tenant_id = :tenant_id AND is_active = true
        """)

        result = await self.session.execute(
            query,
            {"card_id": str(card_id), "tenant_id": str(tenant_id)},
        )

        return result.fetchone()

    async def get_active_card_by_type(
        self, tenant_id: UUID, card_type: CardTypeEnum
    ) -> Optional[BaseCard]:
        """Get active card by type for tenant"""

        query = text("""
            SELECT * FROM context_cards
            WHERE tenant_id = :tenant_id AND card_type = :card_type AND is_active = true
            LIMIT 1
        """)

        result = await self.session.execute(
            query,
            {"tenant_id": str(tenant_id), "card_type": card_type.value},
        )

        return result.fetchone()

    async def list_by_tenant(
        self, tenant_id: UUID, card_type: Optional[CardTypeEnum] = None
    ) -> List[BaseCard]:
        """List cards for tenant"""

        if card_type:
            query = text("""
                SELECT * FROM context_cards
                WHERE tenant_id = :tenant_id AND card_type = :card_type AND is_active = true
                ORDER BY created_at DESC
            """)
            result = await self.session.execute(
                query,
                {"tenant_id": str(tenant_id), "card_type": card_type.value},
            )
        else:
            query = text("""
                SELECT * FROM context_cards
                WHERE tenant_id = :tenant_id AND is_active = true
                ORDER BY created_at DESC
            """)
            result = await self.session.execute(
                query,
                {"tenant_id": str(tenant_id)},
            )

        return result.fetchall()

    async def update(
        self,
        card_id: UUID,
        tenant_id: UUID,
        title: Optional[str] = None,
        content: Optional[dict] = None,
        metrics: Optional[dict] = None,
        notes: Optional[str] = None,
        updated_by: Optional[UUID] = None,
    ) -> Optional[BaseCard]:
        """Update card"""
        
        # Get current card
        card = await self.get_by_id(card_id, tenant_id)
        if not card:
            return None
        
        # Build update query
        updates = []
        params = {"card_id": str(card_id), "tenant_id": str(tenant_id)}
        
        if title is not None:
            updates.append("title = :title")
            params["title"] = title
        
        if content is not None:
            updates.append("content = :content")
            params["content"] = content
        
        if metrics is not None:
            updates.append("metrics = :metrics")
            params["metrics"] = metrics
        
        if notes is not None:
            updates.append("notes = :notes")
            params["notes"] = notes
        
        if updated_by is not None:
            updates.append("updated_by = :updated_by")
            params["updated_by"] = str(updated_by)
        
        # Increment version
        updates.append("version = version + 1")

        query = text(f"""
            UPDATE context_cards
            SET {', '.join(updates)}
            WHERE id = :card_id AND tenant_id = :tenant_id
            RETURNING *
        """)

        result = await self.session.execute(query, params)
        await self.session.commit()

        return result.fetchone()

    async def soft_delete(self, card_id: UUID, tenant_id: UUID) -> bool:
        """Soft delete card"""

        query = text("""
            UPDATE context_cards
            SET is_active = false
            WHERE id = :card_id AND tenant_id = :tenant_id
        """)

        result = await self.session.execute(
            query,
            {"card_id": str(card_id), "tenant_id": str(tenant_id)},
        )
        await self.session.commit()

        return result.rowcount > 0

    async def _soft_delete_existing_card(
        self, tenant_id: UUID, card_type: CardTypeEnum
    ) -> None:
        """Soft delete existing active card of same type"""
        
        existing = await self.get_active_card_by_type(tenant_id, card_type)
        if existing:
            await self.soft_delete(existing.id, tenant_id)

