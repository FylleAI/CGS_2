"""
Card Service Application - Update Card Use Case
"""

import logging
from typing import Optional
from uuid import UUID

from services.content_workflow.card_service.domain.card_entity import CardResponse, UpdateCardRequest
from services.content_workflow.card_service.infrastructure.supabase_card_repository import SupabaseCardRepository

logger = logging.getLogger(__name__)


class UpdateCardUseCase:
    """Use case for updating a card"""

    def __init__(self, card_repository: SupabaseCardRepository):
        self.card_repository = card_repository

    async def execute(
        self,
        card_id: UUID,
        tenant_id: UUID,
        request: UpdateCardRequest,
        updated_by: Optional[UUID] = None,
    ) -> Optional[CardResponse]:
        """
        Update a card.

        Args:
            card_id: Card identifier
            tenant_id: Tenant identifier (for security)
            request: UpdateCardRequest with fields to update
            updated_by: User who updated the card

        Returns:
            Updated CardResponse, or None if card not found
        """

        # Check card exists
        card = await self.card_repository.get_by_id(card_id, tenant_id)
        if not card:
            return None

        # Update card
        updated_card = await self.card_repository.update(
            card_id=card_id,
            tenant_id=tenant_id,
            title=request.title,
            content=request.content,
            metrics=request.metrics,
            notes=request.notes,
        )

        if not updated_card:
            return None

        # Get relationships
        relationships = await self.card_repository.get_relationships(card_id)

        # Build response
        response = CardResponse(
            id=updated_card.id,
            tenant_id=updated_card.tenant_id,
            card_type=updated_card.card_type,
            title=updated_card.title,
            content=updated_card.content,
            metrics=updated_card.metrics or {},
            notes=updated_card.notes or "",
            version=updated_card.version or 1,
            is_active=updated_card.is_active if updated_card.is_active is not None else True,
            created_by=updated_card.created_by,
            updated_by=None,
            created_at=updated_card.created_at,
            updated_at=updated_card.updated_at,
            relationships=relationships,
        )

        return response

