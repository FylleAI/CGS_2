"""
Card Service Application - Create Card Use Case
"""

from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from services.card_service.domain.card_entity import (
    BaseCard,
    CreateCardRequest,
)
from services.card_service.domain.card_types import CardType
from services.card_service.infrastructure.card_repository import CardRepository


class CreateCardUseCase:
    """Use case for creating a new card"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = CardRepository(session)

    async def execute(
        self,
        tenant_id: UUID,
        request: CreateCardRequest,
        created_by: Optional[UUID] = None,
    ) -> BaseCard:
        """
        Create a new card for a tenant.
        
        If a card of the same type already exists and is active,
        it will be soft-deleted and replaced with the new one.
        
        Args:
            tenant_id: Tenant identifier
            request: CreateCardRequest with card data
            created_by: User who created the card
            
        Returns:
            Created card
        """
        
        # Validate card type
        if request.card_type not in [ct.value for ct in CardType]:
            raise ValueError(f"Invalid card type: {request.card_type}")
        
        # Validate content based on card type
        self._validate_content(request.card_type, request.content)
        
        # Create card (repository handles soft delete of existing)
        card = await self.repository.create(
            tenant_id=tenant_id,
            card_type=CardType(request.card_type),
            title=request.title,
            content=request.content,
            metrics=request.metrics,
            notes=request.notes,
            created_by=created_by,
        )
        
        return card

    def _validate_content(self, card_type: str, content: dict) -> None:
        """Validate content based on card type"""
        
        required_fields = {
            "product": ["value_proposition"],
            "persona": ["icp_profile"],
            "campaign": ["objective"],
            "topic": ["keywords"],
        }
        
        if card_type not in required_fields:
            raise ValueError(f"Unknown card type: {card_type}")
        
        for field in required_fields[card_type]:
            if field not in content:
                raise ValueError(f"Missing required field '{field}' for {card_type} card")

