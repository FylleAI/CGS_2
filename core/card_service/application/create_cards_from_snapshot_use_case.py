"""
Card Service Application - Create Cards from Snapshot Use Case
Integration point with Onboarding Microservice
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from core.card_service.application.create_card_use_case import CreateCardUseCase
from core.card_service.application.link_cards_use_case import LinkCardsUseCase
from core.card_service.domain.card_entity import BaseCard, CreateCardRequest
from core.card_service.domain.card_types import CardType, RelationshipType
from core.card_service.infrastructure.card_repository import CardRepository


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
        snapshot: dict,
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
        self, tenant_id: UUID, snapshot: dict, created_by: Optional[UUID]
    ) -> BaseCard:
        """Create ProductCard from company_info"""
        
        company_info = snapshot.get("company_info", {})
        
        request = CreateCardRequest(
            card_type=CardType.PRODUCT,
            title=company_info.get("company_name", "Product"),
            content={
                "value_proposition": company_info.get("value_proposition", ""),
                "features": company_info.get("features", []),
                "differentiators": company_info.get("differentiators", []),
                "use_cases": company_info.get("use_cases", []),
                "target_market": company_info.get("target_market", ""),
            },
            metrics={
                "conversion_rate": company_info.get("conversion_rate"),
                "avg_deal_size": company_info.get("avg_deal_size"),
            },
        )
        
        return await self.create_card_use_case.execute(
            tenant_id, request, created_by
        )

    async def _create_persona_card(
        self, tenant_id: UUID, snapshot: dict, created_by: Optional[UUID]
    ) -> BaseCard:
        """Create PersonaCard from audience_info"""
        
        audience_info = snapshot.get("audience_info", {})
        
        request = CreateCardRequest(
            card_type=CardType.PERSONA,
            title=audience_info.get("persona_name", "Target Audience"),
            content={
                "icp_profile": audience_info.get("icp_profile", ""),
                "pain_points": audience_info.get("pain_points", []),
                "goals": audience_info.get("goals", []),
                "preferred_language": audience_info.get("preferred_language", ""),
                "communication_channels": audience_info.get("communication_channels", []),
                "demographics": audience_info.get("demographics"),
                "psychographics": audience_info.get("psychographics"),
            },
        )
        
        return await self.create_card_use_case.execute(
            tenant_id, request, created_by
        )

    async def _create_campaign_card(
        self, tenant_id: UUID, snapshot: dict, created_by: Optional[UUID]
    ) -> BaseCard:
        """Create CampaignCard from goal"""
        
        goal = snapshot.get("goal", {})
        
        request = CreateCardRequest(
            card_type=CardType.CAMPAIGN,
            title=goal.get("campaign_name", "Campaign"),
            content={
                "objective": goal.get("objective", ""),
                "key_messages": goal.get("key_messages", []),
                "tone": goal.get("tone", ""),
                "target_personas": [],  # Will be linked
                "assets_produced": goal.get("assets_produced", []),
                "results": None,
                "learnings": None,
            },
            metrics={
                "reach": goal.get("reach"),
                "conversions": goal.get("conversions"),
                "roi": goal.get("roi"),
            },
        )
        
        return await self.create_card_use_case.execute(
            tenant_id, request, created_by
        )

    async def _create_topic_card(
        self, tenant_id: UUID, snapshot: dict, created_by: Optional[UUID]
    ) -> BaseCard:
        """Create TopicCard from insights"""
        
        insights = snapshot.get("insights", {})
        
        request = CreateCardRequest(
            card_type=CardType.TOPIC,
            title=insights.get("topic_name", "Topics"),
            content={
                "keywords": insights.get("keywords", []),
                "angles": insights.get("angles", []),
                "related_content": insights.get("related_content", []),
                "trend_status": insights.get("trend_status", "stable"),
                "frequency": insights.get("frequency", ""),
                "audience_interest": insights.get("audience_interest", ""),
            },
            metrics={
                "search_volume": insights.get("search_volume"),
                "trend_score": insights.get("trend_score"),
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

