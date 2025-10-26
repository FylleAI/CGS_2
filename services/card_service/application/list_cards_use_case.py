"""
Card Service Application - List Cards Use Case
"""

import logging
from typing import List, Optional
from uuid import UUID

from services.content_workflow.card_service.domain.card_entity import CardResponse
from services.content_workflow.card_service.domain.card_types import CardType
from services.content_workflow.card_service.infrastructure.supabase_card_repository import SupabaseCardRepository

logger = logging.getLogger(__name__)


class ListCardsUseCase:
    """Use case for listing cards for a tenant"""

    def __init__(self, card_repository: SupabaseCardRepository):
        self.card_repository = card_repository

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
        logger.info(f"📋 ListCardsUseCase.execute() - tenant_id={tenant_id}, card_type={card_type}")

        # Validate card type if provided
        if card_type:
            if card_type not in [ct.value for ct in CardType]:
                raise ValueError(f"Invalid card type: {card_type}")
            card_type_enum = CardType(card_type)
        else:
            card_type_enum = None

        # Get cards
        cards = await self.card_repository.list_by_tenant(tenant_id, card_type_enum)
        logger.info(f"✅ Retrieved {len(cards)} cards")

        # Build responses with relationships
        responses = []
        for card in cards:
            # Get relationships for this card
            relationships = await self.card_repository.get_relationships(card.id)

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
            responses.append(response)

        logger.info(f"✅ Built {len(responses)} card responses")
        return responses

