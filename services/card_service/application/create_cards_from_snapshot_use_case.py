"""
Card Service Application - Create Cards from Snapshot Use Case
Integration point with Onboarding Microservice
"""

import logging
from typing import List, Optional
from uuid import UUID

from core.card_service.application.create_card_use_case import CreateCardUseCase
from core.card_service.application.link_cards_use_case import LinkCardsUseCase
from core.card_service.domain.card_entity import BaseCard, CreateCardRequest
from core.card_service.domain.card_types import CardType, RelationshipType
from core.card_service.infrastructure.supabase_card_repository import SupabaseCardRepository

logger = logging.getLogger(__name__)


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

    def __init__(self, repository: SupabaseCardRepository):
        self.repository = repository
        self.create_card_use_case = CreateCardUseCase(repository)
        self.link_cards_use_case = LinkCardsUseCase(repository)

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
            snapshot: CompanySnapshot dict with new schema:
                - company: CompanyInfo (name, description, key_offerings, differentiators)
                - audience: AudienceInfo (primary, secondary, pain_points, desired_outcomes)
                - voice: VoiceInfo (tone, style_guidelines, cta_preferences)
                - insights: InsightsInfo (positioning, key_messages, recent_news, competitors)
                - clarifying_answers: Dict with user answers to clarifying questions
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
        """Create ProductCard from company info"""

        # Read from new schema: snapshot.company
        company = snapshot.get("company", {})
        insights = snapshot.get("insights", {})

        # Fallback to old schema for backwards compatibility
        if not company:
            company = snapshot.get("company_info", {})

        request = CreateCardRequest(
            card_type=CardType.PRODUCT,
            title=company.get("name", "Product"),
            content={
                "value_proposition": insights.get("positioning", "") or company.get("description", ""),
                "features": company.get("key_offerings", []),
                "differentiators": company.get("differentiators", []),
                "use_cases": [],  # Not in new schema, can be populated from clarifying_answers
                "target_market": company.get("industry", ""),
                "description": company.get("description", ""),
                "website": company.get("website", ""),
                "headquarters": company.get("headquarters", ""),
                "size_range": company.get("size_range", ""),
            },
            metrics={
                "industry": company.get("industry"),
                "size_range": company.get("size_range"),
            },
        )

        return await self.create_card_use_case.execute(
            tenant_id, request, created_by
        )

    async def _create_persona_card(
        self, tenant_id: UUID, snapshot: dict, created_by: Optional[UUID]
    ) -> BaseCard:
        """Create PersonaCard from audience info"""

        # Read from new schema: snapshot.audience
        audience = snapshot.get("audience", {})

        # Fallback to old schema for backwards compatibility
        if not audience:
            audience = snapshot.get("audience_info", {})

        request = CreateCardRequest(
            card_type=CardType.PERSONA,
            title=audience.get("primary", "Target Audience"),
            content={
                "icp_profile": audience.get("primary", ""),
                "pain_points": audience.get("pain_points", []),
                "goals": audience.get("desired_outcomes", []),
                "preferred_language": "",  # Not in new schema
                "communication_channels": [],  # Not in new schema
                "demographics": {},
                "psychographics": {},
                "secondary_audiences": audience.get("secondary", []),
            },
        )

        return await self.create_card_use_case.execute(
            tenant_id, request, created_by
        )

    async def _create_campaign_card(
        self, tenant_id: UUID, snapshot: dict, created_by: Optional[UUID]
    ) -> BaseCard:
        """Create CampaignCard from voice and insights"""

        # Read from new schema: snapshot.voice and snapshot.insights
        voice = snapshot.get("voice", {})
        insights = snapshot.get("insights", {})
        company = snapshot.get("company", {})

        # Fallback to old schema for backwards compatibility
        goal = snapshot.get("goal", {})

        request = CreateCardRequest(
            card_type=CardType.CAMPAIGN,
            title=goal.get("campaign_name", f"{company.get('name', 'Campaign')} Campaign"),
            content={
                "objective": goal.get("objective", insights.get("positioning", "")),
                "key_messages": insights.get("key_messages", []),
                "tone": voice.get("tone", ""),
                "style_guidelines": voice.get("style_guidelines", []),
                "cta_preferences": voice.get("cta_preferences", []),
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

        # Read from new schema: snapshot.insights
        insights = snapshot.get("insights", {})
        company = snapshot.get("company", {})

        request = CreateCardRequest(
            card_type=CardType.TOPIC,
            title=f"{company.get('name', 'Topics')} - Key Topics",
            content={
                "keywords": [],  # Not in new schema, can be extracted from key_messages
                "angles": [],  # Not in new schema
                "related_content": insights.get("recent_news", []),
                "key_messages": insights.get("key_messages", []),
                "positioning": insights.get("positioning", ""),
                "competitors": insights.get("competitors", []),
                "trend_status": "stable",  # Not in new schema
                "frequency": "",  # Not in new schema
                "audience_interest": "",  # Not in new schema
            },
            metrics={
                "search_volume": None,
                "trend_score": None,
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

