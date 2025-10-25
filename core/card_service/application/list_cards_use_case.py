"""
Card Service Application - List Cards Use Case
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from core.card_service.domain.card_entity import CardResponse
from core.card_service.domain.card_types import CardType
from core.card_service.infrastructure.card_relationship_repository import (
    CardRelationshipRepository,
)
from core.card_service.infrastructure.card_repository import CardRepository


class ListCardsUseCase:
    """Use case for listing cards for a tenant"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.card_repository = CardRepository(session)
        self.relationship_repository = CardRelationshipRepository(session)

    async def execute(
        self, tenant_id: UUID, card_type: Optional[str] = None
    ) -> List[CardResponse]:
        """
        List cards for a tenant, optionally filtered by type.
        
        Args:
            tenant_id: Tenant identifier
            card_type: Optional card type filter (product, persona, campaign, topic)
            
        Returns:
            List of CardResponse objects
        """
        
        # Validate card type if provided
        if card_type:
            if card_type not in [ct.value for ct in CardType]:
                raise ValueError(f"Invalid card type: {card_type}")
            card_type_enum = CardType(card_type)
        else:
            card_type_enum = None
        
        # Get cards
        cards = await self.card_repository.list_by_tenant(tenant_id, card_type_enum)
        
        # Build responses with relationships
        responses = []
        for card in cards:
            relationships = await self.relationship_repository.get_by_source_card(card.id)
            
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
            responses.append(response)
        
        return responses

