"""Card types and field mappings for dynamic question generation.

This module defines the card types and their required fields,
enabling Gemini to generate targeted clarifying questions.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class CardType(str, Enum):
    """Supported card types for CardsSnapshot."""
    
    PRODUCT = "product"
    TARGET = "target"
    BRAND_VOICE = "brand_voice"
    COMPETITOR = "competitor"
    TOPIC = "topic"
    CAMPAIGNS = "campaigns"
    PERFORMANCE = "performance"
    FEEDBACK = "feedback"


class CardFieldMapping(BaseModel):
    """Maps a card field to its data sources and priority."""
    
    field_name: str
    description: str
    required: bool = True
    data_sources: List[str] = Field(
        default_factory=lambda: ["user_input", "perplexity", "gemini"]
    )
    fallback_strategy: str = "gemini_generate"  # or "placeholder", "skip"


class CardTypeConfig(BaseModel):
    """Configuration for a card type including required fields."""
    
    card_type: CardType
    min_count: int = 1
    max_count: int = 1
    description: str
    required_fields: List[CardFieldMapping]
    optional_fields: List[CardFieldMapping] = Field(default_factory=list)


# ============================================================================
# CARD TYPE CONFIGURATIONS
# ============================================================================

CARD_TYPE_CONFIGS: Dict[CardType, CardTypeConfig] = {
    CardType.PRODUCT: CardTypeConfig(
        card_type=CardType.PRODUCT,
        min_count=1,
        max_count=1,
        description="Product/Service value proposition and features",
        required_fields=[
            CardFieldMapping(
                field_name="valueProposition",
                description="Main value proposition of the product/service",
            ),
            CardFieldMapping(
                field_name="features",
                description="Key features and capabilities",
            ),
            CardFieldMapping(
                field_name="differentiators",
                description="What makes this product unique vs competitors",
            ),
        ],
        optional_fields=[
            CardFieldMapping(
                field_name="useCases",
                description="Primary use cases",
                required=False,
            ),
            CardFieldMapping(
                field_name="performanceMetrics",
                description="Key performance metrics",
                required=False,
            ),
        ],
    ),
    
    CardType.TARGET: CardTypeConfig(
        card_type=CardType.TARGET,
        min_count=1,
        max_count=5,
        description="Ideal Customer Profile (ICP) definition",
        required_fields=[
            CardFieldMapping(
                field_name="icpName",
                description="Name/label for this ICP",
            ),
            CardFieldMapping(
                field_name="painPoints",
                description="Key pain points and challenges",
            ),
            CardFieldMapping(
                field_name="goals",
                description="Desired outcomes and objectives",
            ),
        ],
        optional_fields=[
            CardFieldMapping(
                field_name="demographics",
                description="Demographic information",
                required=False,
            ),
            CardFieldMapping(
                field_name="communicationChannels",
                description="Preferred communication channels",
                required=False,
            ),
        ],
    ),
    
    CardType.BRAND_VOICE: CardTypeConfig(
        card_type=CardType.BRAND_VOICE,
        min_count=1,
        max_count=1,
        description="Brand voice and style guidelines",
        required_fields=[
            CardFieldMapping(
                field_name="toneDescription",
                description="Overall tone of voice description",
            ),
            CardFieldMapping(
                field_name="styleGuidelines",
                description="Writing style guidelines",
            ),
        ],
        optional_fields=[
            CardFieldMapping(
                field_name="dosExamples",
                description="Examples of do's",
                required=False,
            ),
            CardFieldMapping(
                field_name="dontsExamples",
                description="Examples of don'ts",
                required=False,
            ),
            CardFieldMapping(
                field_name="termsToUse",
                description="Preferred terminology",
                required=False,
            ),
            CardFieldMapping(
                field_name="termsToAvoid",
                description="Terms to avoid",
                required=False,
            ),
        ],
    ),
    
    CardType.COMPETITOR: CardTypeConfig(
        card_type=CardType.COMPETITOR,
        min_count=0,
        max_count=10,
        description="Competitor analysis and differentiation",
        required_fields=[
            CardFieldMapping(
                field_name="competitorName",
                description="Competitor company name",
            ),
            CardFieldMapping(
                field_name="positioning",
                description="Competitor's market positioning",
            ),
        ],
        optional_fields=[
            CardFieldMapping(
                field_name="strengths",
                description="Competitor strengths",
                required=False,
            ),
            CardFieldMapping(
                field_name="weaknesses",
                description="Competitor weaknesses",
                required=False,
            ),
            CardFieldMapping(
                field_name="differentiationOpportunities",
                description="Opportunities to differentiate",
                required=False,
            ),
        ],
    ),

    CardType.TOPIC: CardTypeConfig(
        card_type=CardType.TOPIC,
        min_count=1,
        max_count=5,
        description="Content topics and themes",
        required_fields=[
            CardFieldMapping(
                field_name="description",
                description="Topic description and relevance",
            ),
            CardFieldMapping(
                field_name="keywords",
                description="Related keywords for SEO/content",
            ),
        ],
        optional_fields=[
            CardFieldMapping(
                field_name="angles",
                description="Content angles to explore",
                required=False,
            ),
            CardFieldMapping(
                field_name="trends",
                description="Related market trends",
                required=False,
            ),
        ],
    ),

    CardType.CAMPAIGNS: CardTypeConfig(
        card_type=CardType.CAMPAIGNS,
        min_count=1,
        max_count=3,
        description="Marketing campaign templates",
        required_fields=[
            CardFieldMapping(
                field_name="objective",
                description="Campaign objective",
            ),
            CardFieldMapping(
                field_name="keyMessages",
                description="Key messages to communicate",
            ),
        ],
        optional_fields=[
            CardFieldMapping(
                field_name="tone",
                description="Campaign tone",
                required=False,
            ),
            CardFieldMapping(
                field_name="assets",
                description="Required campaign assets",
                required=False,
            ),
        ],
    ),

    CardType.PERFORMANCE: CardTypeConfig(
        card_type=CardType.PERFORMANCE,
        min_count=1,
        max_count=1,
        description="Performance metrics placeholder",
        required_fields=[
            CardFieldMapping(
                field_name="period",
                description="Reporting period",
                fallback_strategy="placeholder",
            ),
        ],
        optional_fields=[],
    ),

    CardType.FEEDBACK: CardTypeConfig(
        card_type=CardType.FEEDBACK,
        min_count=1,
        max_count=1,
        description="Feedback collection placeholder",
        required_fields=[
            CardFieldMapping(
                field_name="summary",
                description="Feedback summary",
                fallback_strategy="placeholder",
            ),
        ],
        optional_fields=[],
    ),
}


# ============================================================================
# QUESTION TO CARD FIELD MAPPING
# ============================================================================

class QuestionCardMapping(BaseModel):
    """Maps a clarifying question to card fields it populates."""

    card_type: CardType
    field_name: str


# Questions can map to multiple card fields
QUESTION_FIELD_MAPPINGS: Dict[str, List[QuestionCardMapping]] = {
    # Example mappings - these are populated dynamically by Gemini
    "tone_of_voice": [
        QuestionCardMapping(card_type=CardType.BRAND_VOICE, field_name="toneDescription"),
        QuestionCardMapping(card_type=CardType.CAMPAIGNS, field_name="tone"),
    ],
    "target_goals": [
        QuestionCardMapping(card_type=CardType.TARGET, field_name="goals"),
        QuestionCardMapping(card_type=CardType.CAMPAIGNS, field_name="objective"),
    ],
    "competitors": [
        QuestionCardMapping(card_type=CardType.COMPETITOR, field_name="competitorName"),
    ],
    "content_topics": [
        QuestionCardMapping(card_type=CardType.TOPIC, field_name="keywords"),
        QuestionCardMapping(card_type=CardType.TOPIC, field_name="angles"),
    ],
    "communication_channels": [
        QuestionCardMapping(card_type=CardType.TARGET, field_name="communicationChannels"),
    ],
}


def get_missing_fields_for_cards(
    available_data: Dict[str, Any],
    target_cards: Optional[List[CardType]] = None,
) -> Dict[CardType, List[str]]:
    """
    Identify which card fields are missing based on available data.

    Args:
        available_data: Data already collected (user input + Perplexity)
        target_cards: Specific cards to check (None = all)

    Returns:
        Dict mapping card types to list of missing required field names
    """
    if target_cards is None:
        target_cards = list(CardType)

    missing = {}

    for card_type in target_cards:
        config = CARD_TYPE_CONFIGS.get(card_type)
        if not config:
            continue

        missing_fields = []
        for field in config.required_fields:
            # Check if field data is available
            field_key = f"{card_type.value}.{field.field_name}"
            if field_key not in available_data and field.field_name not in available_data:
                missing_fields.append(field.field_name)

        if missing_fields:
            missing[card_type] = missing_fields

    return missing


def build_question_context_for_gemini(
    missing_fields: Dict[CardType, List[str]],
    min_questions: int = 3,
    max_questions: int = 5,
) -> str:
    """
    Build context for Gemini prompt to generate targeted questions.

    Args:
        missing_fields: Dict of card types to missing fields
        min_questions: Minimum questions to generate
        max_questions: Maximum questions to generate

    Returns:
        Prompt context string for Gemini
    """
    context_parts = [
        f"Generate {min_questions} to {max_questions} clarifying questions.",
        "Each question should help populate specific card fields.",
        "",
        "MISSING DATA FOR CARDS:",
    ]

    for card_type, fields in missing_fields.items():
        config = CARD_TYPE_CONFIGS.get(card_type)
        if config:
            context_parts.append(f"\n{card_type.value.upper()} Card ({config.description}):")
            for field_name in fields:
                field_config = next(
                    (f for f in config.required_fields if f.field_name == field_name),
                    None
                )
                if field_config:
                    context_parts.append(f"  - {field_name}: {field_config.description}")

    context_parts.extend([
        "",
        "RULES:",
        "1. Each question MUST include 'maps_to' array with card_type and field_name",
        "2. Prioritize questions that fill multiple card fields",
        "3. Questions should be specific and actionable",
        "4. Use Italian language for questions",
    ])

    return "\n".join(context_parts)


