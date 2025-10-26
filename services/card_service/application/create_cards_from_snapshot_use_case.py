"""
Card Service Application - Create Cards from Snapshot Use Case
Integration point with Onboarding Microservice
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from packages.contracts.onboarding import CompanySnapshot
from services.card_service.application.create_card_use_case import CreateCardUseCase
from services.card_service.application.link_cards_use_case import LinkCardsUseCase
from services.card_service.domain.card_entity import BaseCard, CreateCardRequest
from services.card_service.domain.card_types import CardType, RelationshipType
from services.card_service.infrastructure.card_repository import CardRepository


class CreateCardsFromSnapshotUseCase:
    """
    Use case for creating 4 atomic cards from CompanySnapshot.
    
    This is the integration point between Onboarding and Card Service.
    Called after Onboarding completes and creates:
    - ProductCard (from company info)
    - PersonaCard (from audience info)
    - CampaignCard (from goal)
    - TopicCard (from insights)
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.create_card_use_case = CreateCardUseCase(session)
        self.link_cards_use_case = LinkCardsUseCase(session)
        self.card_repository = CardRepository(session)

    async def execute(
        self,
        tenant_id: UUID,
        snapshot: CompanySnapshot,
        created_by: Optional[UUID] = None,
    ) -> List[BaseCard]:
        """
        Create 4 atomic cards from CompanySnapshot and auto-link them.
        
        Args:
            tenant_id: Tenant identifier
            snapshot: CompanySnapshot dict with company_info, audience_info, goal, insights
            created_by: User who created the cards
            
        Returns:
            List of created cards [ProductCard, PersonaCard, CampaignCard, TopicCard]
        """
        
        cards = []
        
        # 1. Create ProductCard from company_info
        product_card = await self._create_product_card(
            tenant_id, snapshot, created_by
        )
        cards.append(product_card)
        
        # 2. Create PersonaCard from audience_info
        persona_card = await self._create_persona_card(
            tenant_id, snapshot, created_by
        )
        cards.append(persona_card)
        
        # 3. Create CampaignCard from goal
        campaign_card = await self._create_campaign_card(
            tenant_id, snapshot, created_by
        )
        cards.append(campaign_card)
        
        # 4. Create TopicCard from insights
        topic_card = await self._create_topic_card(
            tenant_id, snapshot, created_by
        )
        cards.append(topic_card)
        
        # 5. Auto-link cards
        await self._auto_link_cards(tenant_id, cards)
        
        return cards

    async def _create_product_card(
        self,
        tenant_id: UUID,
        snapshot: CompanySnapshot,
        created_by: Optional[UUID],
    ) -> BaseCard:
        """Create ProductCard from company profile information."""

        company = snapshot.company

        request = CreateCardRequest(
            card_type=CardType.PRODUCT,
            title=company.name or "Product",
            content={
                "value_proposition": company.value_proposition or company.description,
                "features": company.features or company.key_offerings,
                "differentiators": company.differentiators,
                "use_cases": company.use_cases,
                "target_market": company.target_market,
                "key_offerings": company.key_offerings,
                "description": company.description,
                "industry": company.industry,
                "website": company.website,
            },
            metrics=company.metrics,
        )
        
        return await self.create_card_use_case.execute(
            tenant_id, request, created_by
        )

    async def _create_persona_card(
        self,
        tenant_id: UUID,
        snapshot: CompanySnapshot,
        created_by: Optional[UUID],
    ) -> BaseCard:
        """Create PersonaCard from audience profile."""

        audience = snapshot.audience

        request = CreateCardRequest(
            card_type=CardType.PERSONA,
            title=audience.persona_name or "Target Audience",
            content={
                "icp_profile": audience.icp_profile,
                "pain_points": audience.pain_points,
                "goals": audience.goals,
                "preferred_language": audience.preferred_language,
                "communication_channels": audience.communication_channels,
                "demographics": audience.demographics,
                "psychographics": audience.psychographics,
            },
        )
        
        return await self.create_card_use_case.execute(
            tenant_id, request, created_by
        )

    async def _create_campaign_card(
        self,
        tenant_id: UUID,
        snapshot: CompanySnapshot,
        created_by: Optional[UUID],
    ) -> BaseCard:
        """Create CampaignCard from goal information."""

        goal = snapshot.goal

        request = CreateCardRequest(
            card_type=CardType.CAMPAIGN,
            title=goal.campaign_name if goal else "Campaign",
            content={
                "objective": goal.objective if goal else "",
                "key_messages": goal.key_messages if goal else [],
                "tone": goal.tone if goal else "",
                "target_personas": [],
                "assets_produced": goal.assets_produced if goal else [],
                "results": None,
                "learnings": None,
            },
            metrics=goal.metrics if goal else {},
        )
        
        return await self.create_card_use_case.execute(
            tenant_id, request, created_by
        )

    async def _create_topic_card(
        self,
        tenant_id: UUID,
        snapshot: CompanySnapshot,
        created_by: Optional[UUID],
    ) -> BaseCard:
        """Create TopicCard from insight profile."""

        insights = snapshot.insights

        request = CreateCardRequest(
            card_type=CardType.TOPIC,
            title=insights.topic_name or "Topics",
            content={
                "keywords": insights.keywords,
                "angles": insights.angles,
                "related_content": insights.related_content,
                "trend_status": insights.trend_status or "stable",
                "frequency": insights.frequency,
                "audience_interest": insights.audience_interest,
            },
            metrics={
                "search_volume": insights.search_volume,
                "trend_score": insights.trend_score,
            },
        )
        
        return await self.create_card_use_case.execute(
            tenant_id, request, created_by
        )

    async def _auto_link_cards(self, tenant_id: UUID, cards: List[BaseCard]) -> None:
        """Auto-link cards with predefined relationships"""
        
        if len(cards) != 4:
            return
        
        product_card, persona_card, campaign_card, topic_card = cards
        
        # Define auto-linking rules
        links = [
            (product_card.id, persona_card.id, RelationshipType.TARGETS, 1.0),
            (product_card.id, campaign_card.id, RelationshipType.PROMOTED_IN, 0.8),
            (persona_card.id, campaign_card.id, RelationshipType.IS_TARGET_OF, 1.0),
            (campaign_card.id, topic_card.id, RelationshipType.DISCUSSES, 0.9),
        ]
        
        await self.link_cards_use_case.link_multiple(tenant_id, links)

