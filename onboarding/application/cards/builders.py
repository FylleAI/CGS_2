"""
Card Builders - Functions to create typed cards from raw input.

Each builder function:
  1. Takes OnboardingRawInput (or subset)
  2. Returns a validated card instance
  3. Handles missing data gracefully (uses defaults)

Design:
  - One function per card type
  - Builders are pure functions (no side effects)
  - All validation happens via Pydantic models
"""

from typing import List, Optional
from datetime import datetime

from onboarding.domain.cards import (
    # Card types
    ProductCard,
    TargetCard,
    CampaignsCard,
    TopicCard,
    BrandVoiceCard,
    CompetitorCard,
    PerformanceCard,
    FeedbackCard,
    # Nested models
    PerformanceMetric,
    Demographics,
    Trend,
    # Input
    OnboardingRawInput,
    InferredCompetitorData,
    InferredTopicData,
)


def build_product_card(raw: OnboardingRawInput) -> ProductCard:
    """
    Build ProductCard from raw input.
    
    Sources:
      - inferred.company.value_proposition → valueProposition
      - inferred.company.key_offerings → features
      - inferred.company.differentiators → differentiators
      - inferred.company.metrics → performanceMetrics
    """
    company = raw.inferred.company
    
    # Build value proposition - required field
    value_prop = company.value_proposition
    if not value_prop:
        # Fallback: construct from description + differentiators
        value_prop = company.description or f"{raw.user_input.brand_name} provides innovative solutions."
        if company.differentiators:
            value_prop += f" Key differentiators: {', '.join(company.differentiators[:2])}."
    
    # Convert metrics to PerformanceMetric objects
    perf_metrics = [
        PerformanceMetric(metric=m.get("metric", "Metric"), value=m.get("value", "N/A"))
        for m in company.metrics
    ]
    
    return ProductCard(
        title=f"{raw.user_input.brand_name} - Product",
        sessionId=raw.session_id,
        valueProposition=value_prop,
        features=company.key_offerings,
        differentiators=company.differentiators,
        useCases=[],  # Will be populated from clarifying questions or future inference
        performanceMetrics=perf_metrics,
    )


def build_target_cards(raw: OnboardingRawInput) -> List[TargetCard]:
    """
    Build TargetCard(s) from raw input.
    
    Returns 1-3 cards depending on data richness.
    First card is primary audience, others are secondary.
    """
    audience = raw.inferred.audience
    cards: List[TargetCard] = []
    
    # Primary target
    if audience.primary_audience:
        # Try to create a persona name
        persona_name = _infer_persona_name(audience.primary_audience)
        
        demographics = None
        if audience.demographics:
            demographics = Demographics(
                ageRange=audience.demographics.get("age_range"),
                location=audience.demographics.get("location"),
                role=audience.demographics.get("role"),
                industry=audience.demographics.get("industry"),
            )
        
        cards.append(TargetCard(
            title=f"Target: {persona_name}",
            sessionId=raw.session_id,
            icpName=persona_name,
            description=audience.primary_audience,
            painPoints=audience.pain_points,
            goals=audience.goals,
            communicationChannels=audience.communication_channels or raw.user_input.target_channels,
            demographics=demographics,
        ))
    
    # Secondary targets (up to 2)
    for i, secondary in enumerate(audience.secondary_audiences[:2]):
        persona_name = _infer_persona_name(secondary)
        cards.append(TargetCard(
            title=f"Target: {persona_name}",
            sessionId=raw.session_id,
            icpName=persona_name,
            description=secondary,
            painPoints=[],  # Less detailed for secondary
            goals=[],
            communicationChannels=[],
        ))
    
    # Fallback: create at least one generic card if no data
    if not cards:
        cards.append(TargetCard(
            title="Target Audience",
            sessionId=raw.session_id,
            icpName="Target Customer",
            description=f"Target customer for {raw.user_input.brand_name}",
            painPoints=[],
            goals=[],
        ))
    
    return cards


def _infer_persona_name(description: str) -> str:
    """Infer a persona name from audience description."""
    # Simple heuristic: take first 3-4 words, capitalize
    words = description.split()[:4]
    name = " ".join(words)
    if len(name) > 40:
        name = name[:37] + "..."
    return name


def build_brand_voice_card(raw: OnboardingRawInput) -> BrandVoiceCard:
    """
    Build BrandVoiceCard from raw input.

    Critical for content generation - defines how content should sound.
    """
    voice = raw.inferred.voice

    # Build tone description
    tone_desc = voice.tone
    if not tone_desc:
        # Default professional tone
        tone_desc = f"Professional and approachable tone for {raw.user_input.brand_name}."

    return BrandVoiceCard(
        title="Brand Voice Guidelines",
        sessionId=raw.session_id,
        toneDescription=tone_desc,
        styleGuidelines=voice.style_guidelines,
        dosExamples=voice.dos_examples,
        dontsExamples=voice.donts_examples,
        termsToUse=voice.terms_to_use,
        termsToAvoid=voice.terms_to_avoid,
    )


def build_competitor_cards(raw: OnboardingRawInput) -> List[CompetitorCard]:
    """
    Build CompetitorCard(s) from raw input.

    Returns 0-3 cards depending on competitors found.
    """
    cards: List[CompetitorCard] = []

    for comp in raw.inferred.competitors[:3]:  # Max 3 competitors
        cards.append(CompetitorCard(
            title=f"Competitor: {comp.name}",
            sessionId=raw.session_id,
            competitorName=comp.name,
            positioning=comp.positioning or f"{comp.name} competitive positioning",
            keyMessages=comp.key_messages,
            strengths=comp.strengths,
            weaknesses=comp.weaknesses,
            differentiationOpportunities=[],  # Requires analysis
        ))

    return cards


def build_topic_cards(raw: OnboardingRawInput) -> List[TopicCard]:
    """
    Build TopicCard(s) from raw input.

    Returns 1-3 topic cards for content pillars.
    """
    cards: List[TopicCard] = []

    for topic in raw.inferred.topics[:3]:  # Max 3 topics
        trends = [
            Trend(trend=t.get("trend", ""), relevance=t.get("relevance", "medium"))
            for t in topic.trends
        ]

        cards.append(TopicCard(
            title=f"Topic: {topic.name}",
            sessionId=raw.session_id,
            description=topic.description or f"Content about {topic.name}",
            keywords=topic.keywords,
            angles=topic.angles,
            relatedContent=[],  # Empty initially
            trends=trends,
        ))

    # Fallback: create a default topic based on company
    if not cards:
        company = raw.inferred.company
        default_topic = company.industry or raw.user_input.brand_name
        cards.append(TopicCard(
            title=f"Topic: {default_topic}",
            sessionId=raw.session_id,
            description=f"Content about {default_topic} and industry trends",
            keywords=[],
            angles=[],
        ))

    return cards


def build_campaigns_card(raw: OnboardingRawInput) -> CampaignsCard:
    """
    Build initial CampaignsCard - mostly stub for future campaigns.

    This card is a template - actual campaign data comes from user input later.
    """
    return CampaignsCard(
        title="Marketing Campaign",
        sessionId=raw.session_id,
        objective=f"Marketing campaign for {raw.user_input.brand_name}",
        keyMessages=[],
        tone=raw.inferred.voice.tone,
        assets=[],
        results=[],
        learnings=[],
    )


def build_performance_card(raw: OnboardingRawInput) -> PerformanceCard:
    """
    Build initial PerformanceCard - stub for future analytics.

    This card is empty initially - populated as content is published and tracked.
    """
    return PerformanceCard(
        title="Content Performance",
        sessionId=raw.session_id,
        period="Current Quarter",
        metrics=[],
        topPerformingContent=[],
        insights=[],
    )

