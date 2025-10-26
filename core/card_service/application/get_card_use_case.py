"""
Card Service Application - Get Card Use Case
"""

import logging
from typing import Optional
from uuid import UUID

from core.card_service.domain.card_entity import BaseCard, CardResponse
from core.card_service.infrastructure.supabase_card_repository import SupabaseCardRepository

logger = logging.getLogger(__name__)


class GetCardUseCase:
    """Use case for retrieving a card with its relationships"""

    def __init__(self, card_repository: SupabaseCardRepository):
        self.card_repository = card_repository

    async def execute(self, card_id: UUID, tenant_id: UUID) -> Optional[CardResponse]:
        """
        Get a card by ID with all its relationships.

        Args:
            card_id: Card identifier
            tenant_id: Tenant identifier (for security)

        Returns:
            CardResponse with card and relationships, or None if not found
        """

        # Get card
        card = await self.card_repository.get_by_id(card_id, tenant_id)
        if not card:
            return None

        # Get relationships
        relationships = await self.card_repository.get_relationships(card_id)

        # Build response
        response = CardResponse(
            id=card.id,
            tenant_id=card.tenant_id,
            card_type=card.card_type,
            title=card.title,
            content=card.content,
            metrics=card.metrics or {},
            notes=card.notes or "",
            version=card.version or 1,
            is_active=card.is_active if card.is_active is not None else True,
            created_by=card.created_by,
            updated_by=None,
            created_at=card.created_at,
            updated_at=card.updated_at,
            relationships=relationships,
        )

        return response

