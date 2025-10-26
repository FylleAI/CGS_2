"""
Card Service Application - Update Card Use Case
"""

from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from services.card_service.domain.card_entity import CardResponse, UpdateCardRequest
from services.card_service.infrastructure.card_relationship_repository import (
    CardRelationshipRepository,
)
from services.card_service.infrastructure.card_repository import CardRepository


class UpdateCardUseCase:
    """Use case for updating a card"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.card_repository = CardRepository(session)
        self.relationship_repository = CardRelationshipRepository(session)

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
            updated_by=updated_by,
        )
        
        if not updated_card:
            return None
        
        # Get relationships
        relationships = await self.relationship_repository.get_by_source_card(card_id)
        
        # Build response
        response = CardResponse(
            id=updated_card.id,
            tenant_id=updated_card.tenant_id,
            card_type=updated_card.card_type,
            title=updated_card.title,
            content=updated_card.content,
            metrics=updated_card.metrics,
            notes=updated_card.notes,
            version=updated_card.version,
            is_active=updated_card.is_active,
            created_by=updated_card.created_by,
            updated_by=updated_card.updated_by,
            created_at=updated_card.created_at,
            updated_at=updated_card.updated_at,
            relationships=relationships,
        )
        
        return response

