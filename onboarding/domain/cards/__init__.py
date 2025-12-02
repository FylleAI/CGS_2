"""
Cards domain module.

Exports the canonical card schema for the onboarding pipeline.
"""

from .schema import (
    # Enums
    CardType,
    FeedbackSource,
    FeedbackPriority,

    # Nested models
    PerformanceMetric,
    Demographics,
    CampaignAsset,
    CampaignResult,
    RelatedContent,
    Trend,
    ChannelMetric,
    TopContent,

    # Card types
    CardBase,
    ProductCard,
    TargetCard,
    CampaignsCard,
    TopicCard,
    BrandVoiceCard,
    CompetitorCard,
    PerformanceCard,
    FeedbackCard,

    # Union type
    Card,

    # Output envelope
    CardsOutput,
)

from .raw_input import (
    # User input
    UserInput,

    # Inferred data
    InferredCompanyData,
    InferredAudienceData,
    InferredVoiceData,
    InferredCompetitorData,
    InferredTopicData,
    InferredData,

    # Combined raw input
    OnboardingRawInput,
)

__all__ = [
    # Enums
    "CardType",
    "FeedbackSource",
    "FeedbackPriority",

    # Nested models
    "PerformanceMetric",
    "Demographics",
    "CampaignAsset",
    "CampaignResult",
    "RelatedContent",
    "Trend",
    "ChannelMetric",
    "TopContent",

    # Card types
    "CardBase",
    "ProductCard",
    "TargetCard",
    "CampaignsCard",
    "TopicCard",
    "BrandVoiceCard",
    "CompetitorCard",
    "PerformanceCard",
    "FeedbackCard",

    # Union type
    "Card",

    # Output envelope
    "CardsOutput",

    # Raw input
    "UserInput",
    "InferredCompanyData",
    "InferredAudienceData",
    "InferredVoiceData",
    "InferredCompetitorData",
    "InferredTopicData",
    "InferredData",
    "OnboardingRawInput",
]

