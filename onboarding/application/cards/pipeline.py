"""
Onboarding Cards Pipeline - Main orchestration for card generation.

This module provides the main entry point for generating cards from onboarding data.
It orchestrates:
  1. Converting existing CompanySnapshot to OnboardingRawInput
  2. Running all card builders
  3. Validating and returning CardsOutput

Design:
  - Single entry point: run_onboarding_pipeline()
  - Integrates with existing onboarding flow (CompanySnapshot)
  - Returns CardsOutput as the ONLY output format
"""

import logging
from datetime import datetime
from typing import Optional

from onboarding.domain.models import CompanySnapshot
from onboarding.domain.cards import (
    CardsOutput,
    Card,
    OnboardingRawInput,
    UserInput,
    InferredData,
    InferredCompanyData,
    InferredAudienceData,
    InferredVoiceData,
    InferredCompetitorData,
    InferredTopicData,
)
from onboarding.application.cards.builders import (
    build_product_card,
    build_target_cards,
    build_brand_voice_card,
    build_competitor_cards,
    build_topic_cards,
    build_campaigns_card,
    build_performance_card,
)

logger = logging.getLogger(__name__)


async def run_onboarding_pipeline(
    raw_input: OnboardingRawInput,
) -> CardsOutput:
    """
    Main pipeline for generating cards from onboarding data.
    
    This is the ONLY entry point for card generation.
    Returns CardsOutput which is the canonical output format.
    
    Args:
        raw_input: OnboardingRawInput with user input + inferred data
        
    Returns:
        CardsOutput with all generated cards
    """
    logger.info(f"🎯 Running onboarding pipeline for session: {raw_input.session_id}")
    
    cards: list[Card] = []
    
    # 1. Product Card (always one)
    try:
        product_card = build_product_card(raw_input)
        cards.append(product_card)
        logger.debug(f"✅ Built ProductCard: {product_card.title}")
    except Exception as e:
        logger.error(f"❌ Failed to build ProductCard: {e}")
    
    # 2. Target Cards (1-3)
    try:
        target_cards = build_target_cards(raw_input)
        cards.extend(target_cards)
        logger.debug(f"✅ Built {len(target_cards)} TargetCards")
    except Exception as e:
        logger.error(f"❌ Failed to build TargetCards: {e}")
    
    # 3. Brand Voice Card (always one)
    try:
        voice_card = build_brand_voice_card(raw_input)
        cards.append(voice_card)
        logger.debug(f"✅ Built BrandVoiceCard: {voice_card.title}")
    except Exception as e:
        logger.error(f"❌ Failed to build BrandVoiceCard: {e}")
    
    # 4. Topic Cards (1-3)
    try:
        topic_cards = build_topic_cards(raw_input)
        cards.extend(topic_cards)
        logger.debug(f"✅ Built {len(topic_cards)} TopicCards")
    except Exception as e:
        logger.error(f"❌ Failed to build TopicCards: {e}")
    
    # 5. Competitor Cards (0-3)
    try:
        competitor_cards = build_competitor_cards(raw_input)
        cards.extend(competitor_cards)
        logger.debug(f"✅ Built {len(competitor_cards)} CompetitorCards")
    except Exception as e:
        logger.error(f"❌ Failed to build CompetitorCards: {e}")
    
    # 6. Campaign Card (stub)
    try:
        campaign_card = build_campaigns_card(raw_input)
        cards.append(campaign_card)
        logger.debug(f"✅ Built CampaignsCard: {campaign_card.title}")
    except Exception as e:
        logger.error(f"❌ Failed to build CampaignsCard: {e}")
    
    # 7. Performance Card (stub)
    try:
        performance_card = build_performance_card(raw_input)
        cards.append(performance_card)
        logger.debug(f"✅ Built PerformanceCard: {performance_card.title}")
    except Exception as e:
        logger.error(f"❌ Failed to build PerformanceCard: {e}")
    
    # Build output
    output = CardsOutput(
        sessionId=raw_input.session_id,
        generatedAt=datetime.utcnow(),
        cards=cards,
    )
    
    logger.info(f"🎉 Pipeline complete: generated {len(cards)} cards for session {raw_input.session_id}")
    
    return output


def convert_snapshot_to_raw_input(
    snapshot: CompanySnapshot,
    session_id: str,
    user_email: str,
    website: Optional[str] = None,
) -> OnboardingRawInput:
    """
    Convert existing CompanySnapshot to OnboardingRawInput.
    
    This is the bridge between the legacy onboarding flow and the new card pipeline.
    It maps:
      - snapshot.company → inferred.company
      - snapshot.audience → inferred.audience
      - snapshot.voice → inferred.voice
      - snapshot.insights → inferred topics/competitors
      - snapshot.clarifying_answers → clarifying_answers
    
    Args:
        snapshot: Existing CompanySnapshot from research phase
        session_id: Session ID
        user_email: User email
        website: Optional website URL
        
    Returns:
        OnboardingRawInput ready for pipeline
    """
    # Map company data
    company_data = InferredCompanyData(
        legal_name=snapshot.company.legal_name,
        description=snapshot.company.description,
        industry=snapshot.company.industry,
        headquarters=snapshot.company.headquarters,
        size_range=snapshot.company.size_range,
        key_offerings=snapshot.company.key_offerings,
        differentiators=snapshot.company.differentiators,
        value_proposition=snapshot.company.description,  # Use description as value prop
    )

    # Map audience data
    audience_data = InferredAudienceData(
        primary_audience=snapshot.audience.primary,
        secondary_audiences=snapshot.audience.secondary,
        pain_points=snapshot.audience.pain_points,
        goals=snapshot.audience.desired_outcomes,
    )

    # Map voice data
    voice_data = InferredVoiceData(
        tone=snapshot.voice.tone,
        style_guidelines=snapshot.voice.style_guidelines,
        terms_to_avoid=snapshot.voice.forbidden_phrases,
    )

    # Map competitors from insights
    competitors = [
        InferredCompetitorData(name=name)
        for name in snapshot.insights.competitors
    ]

    # Create topic from key messages and positioning
    topics = []
    if snapshot.insights.positioning:
        topics.append(InferredTopicData(
            name=snapshot.company.industry or "Industry Insights",
            description=snapshot.insights.positioning,
            keywords=[],
            angles=snapshot.insights.key_messages,
        ))

    # Build InferredData
    inferred = InferredData(
        company=company_data,
        audience=audience_data,
        voice=voice_data,
        competitors=competitors,
        topics=topics,
    )

    # Build UserInput
    user_input = UserInput(
        brand_name=snapshot.company.name,
        user_email=user_email,
        website=website or snapshot.company.website,
        industry_hint=snapshot.company.industry,
    )

    # Build OnboardingRawInput
    return OnboardingRawInput(
        session_id=session_id,
        trace_id=snapshot.trace_id or session_id,
        user_input=user_input,
        inferred=inferred,
        clarifying_answers=snapshot.clarifying_answers,
        research_completed=True,
        synthesis_completed=True,
    )


async def run_pipeline_from_snapshot(
    snapshot: CompanySnapshot,
    session_id: str,
    user_email: str,
    website: Optional[str] = None,
) -> CardsOutput:
    """
    Convenience function to run pipeline directly from CompanySnapshot.

    This is the recommended entry point when integrating with the existing
    onboarding flow that produces CompanySnapshot.

    Args:
        snapshot: CompanySnapshot from research phase
        session_id: Session ID
        user_email: User email
        website: Optional website URL

    Returns:
        CardsOutput with all generated cards
    """
    raw_input = convert_snapshot_to_raw_input(
        snapshot=snapshot,
        session_id=session_id,
        user_email=user_email,
        website=website,
    )

    return await run_onboarding_pipeline(raw_input)

