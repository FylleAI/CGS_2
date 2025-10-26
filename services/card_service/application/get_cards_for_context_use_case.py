"""
Card Service Application - Get Cards for Context Use Case
"""

import logging
from typing import List, Optional
from uuid import UUID

from services.card_service.domain.card_entity import BaseCard
from services.card_service.domain.card_types import CardType
from services.card_service.infrastructure.supabase_card_repository import SupabaseCardRepository

logger = logging.getLogger(__name__)


class GetCardsForContextUseCase:
    """Use case for retrieving cards as RAG context for content generation"""

    def __init__(self, card_repository: SupabaseCardRepository):
        self.card_repository = card_repository

    async def execute(self, tenant_id: str, card_types: Optional[List[str]] = None) -> dict:
        """
        Get cards organized by type.

        Args:
            tenant_id: Tenant identifier
            card_types: Optional list of card types to filter

        Returns:
            Dict with card types as keys and lists of cards as values
        """
        try:
            tenant_uuid = UUID(tenant_id) if isinstance(tenant_id, str) and len(tenant_id) == 36 else tenant_id

            result = {}

            if card_types:
                for card_type in card_types:
                    cards = await self.get_by_type(str(tenant_uuid), card_type)
                    result[card_type] = cards
            else:
                # Get all cards and group by type
                all_cards = await self.get_all(str(tenant_uuid))
                for card in all_cards:
                    card_type = card.card_type.value
                    if card_type not in result:
                        result[card_type] = []
                    result[card_type].append(card)

            return result
        except Exception as e:
            logger.error(f"Error in execute: {str(e)}")
            raise

    async def get_all(self, tenant_id: str) -> List[BaseCard]:
        """
        Get all active cards for a tenant.

        Args:
            tenant_id: Tenant identifier (email)

        Returns:
            List of active cards
        """
        try:
            cards = await self.card_repository.list_by_tenant(UUID(tenant_id) if isinstance(tenant_id, str) and len(tenant_id) == 36 else tenant_id)
            # Filter only active cards
            return [card for card in cards if card.is_active]
        except Exception as e:
            raise Exception(f"Failed to retrieve cards: {str(e)}")

    async def get_by_type(self, tenant_id: str, card_type: str) -> List[BaseCard]:
        """
        Get cards by type for a tenant.

        Args:
            tenant_id: Tenant identifier
            card_type: Card type (product, persona, campaign, topic)

        Returns:
            List of cards of specified type
        """
        try:
            tenant_uuid = UUID(tenant_id) if isinstance(tenant_id, str) and len(tenant_id) == 36 else tenant_id
            # Convert string card_type to enum
            card_type_enum = CardType(card_type) if isinstance(card_type, str) else card_type
            cards = await self.card_repository.list_by_tenant(tenant_uuid, card_type_enum)
            return [card for card in cards if card.is_active]
        except Exception as e:
            raise Exception(f"Failed to retrieve cards by type: {str(e)}")

    async def get_as_rag_context(self, tenant_id: str) -> str:
        """
        Get all cards formatted as RAG context text for LLM.

        Args:
            tenant_id: Tenant identifier

        Returns:
            Formatted text context for LLM
        """
        try:
            cards = await self.get_all(tenant_id)

            if not cards:
                return ""

            # Format cards as context text
            context_lines = []
            context_lines.append("=== CARD CONTEXT ===\n")

            # Group by card type
            by_type = {}
            for card in cards:
                card_type = card.card_type.value
                if card_type not in by_type:
                    by_type[card_type] = []
                by_type[card_type].append(card)

            # Format each card type section
            for card_type, type_cards in by_type.items():
                context_lines.append(f"\n## {card_type.upper()} CARDS\n")

                for card in type_cards:
                    context_lines.append(f"### {card.title}")
                    context_lines.append(f"Type: {card.card_type.value}")
                    context_lines.append(f"Version: {card.version or 1}")

                    # Add content
                    if isinstance(card.content, dict):
                        for key, value in card.content.items():
                            if isinstance(value, list):
                                context_lines.append(f"{key}: {', '.join(str(v) for v in value)}")
                            else:
                                context_lines.append(f"{key}: {value}")

                    # Add notes if present
                    if card.notes:
                        context_lines.append(f"Notes: {card.notes}")

                    context_lines.append("")

            return "\n".join(context_lines)

        except Exception as e:
            raise Exception(f"Failed to generate RAG context: {str(e)}")
