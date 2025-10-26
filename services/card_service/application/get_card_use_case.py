"""
Card Service Application - Get Card Use Case
"""

from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from services.card_service.domain.card_entity import BaseCard, CardResponse
from services.card_service.infrastructure.card_relationship_repository import (
    CardRelationshipRepository,
)
from services.card_service.infrastructure.card_repository import CardRepository


class GetCardUseCase:
    """Use case for retrieving a card with its relationships"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.card_repository = CardRepository(session)
        self.relationship_repository = CardRelationshipRepository(session)

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
        relationships = await self.relationship_repository.get_by_source_card(card_id)
        
        # Build response
        response = CardResponse(
            id=card.id,
            tenant_id=card.tenant_id,
            card_type=card.card_type,
            title=card.title,
            content=card.content,
            metrics=card.metrics,
            notes=card.notes,
            version=card.version,
            is_active=card.is_active,
            created_by=card.created_by,
            updated_by=card.updated_by,
            created_at=card.created_at,
            updated_at=card.updated_at,
            relationships=relationships,
        )
        
        return response

