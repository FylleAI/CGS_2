"""
Card Schema - Centralized card type definitions based on mock_cards.json.

This module defines the canonical card schema that ALL card generation must conform to.
The mock JSON is the source of truth - code adapts to schema, never vice versa.

Card Types (8 total):
  1. product      - Product/service value proposition
  2. target       - Target audience ICP (Ideal Customer Profile)
  3. campaigns    - Marketing campaign definitions
  4. topic        - Content topic/theme clusters
  5. brand_voice  - Brand voice and tone guidelines
  6. competitor   - Competitive analysis
  7. performance  - Performance metrics and analytics
  8. feedback     - User feedback and learnings

Design Decisions:
  - All cards share base fields (id, type, title, createdAt, updatedAt, sessionId)
  - Optional fields allow partial data during inference phase
  - Discriminated union via `type` field enables type-safe polymorphism
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


# =============================================================================
# ENUMS
# =============================================================================

class CardType(str, Enum):
    """Supported card types - mirrors mock JSON exactly."""
    PRODUCT = "product"
    TARGET = "target"
    CAMPAIGNS = "campaigns"
    TOPIC = "topic"
    BRAND_VOICE = "brand_voice"
    COMPETITOR = "competitor"
    PERFORMANCE = "performance"
    FEEDBACK = "feedback"


class FeedbackSource(str, Enum):
    """Source of feedback data."""
    CUSTOMER_FEEDBACK = "customer_feedback"
    AB_TEST = "ab_test"
    SURVEY = "survey"
    ANALYTICS = "analytics"


class FeedbackPriority(str, Enum):
    """Priority level for feedback items."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# =============================================================================
# NESTED MODELS (used by specific card types)
# =============================================================================

class PerformanceMetric(BaseModel):
    """Performance metric with value."""
    metric: str = Field(..., description="Metric name (e.g., 'Tempo risparmiato')")
    value: str = Field(..., description="Metric value (e.g., '70%', '+45%', '3.2x')")


class Demographics(BaseModel):
    """Demographic information for target audience."""
    ageRange: Optional[str] = Field(default=None, description="e.g., '32-45'")
    location: Optional[str] = Field(default=None, description="e.g., 'Nord Italia'")
    role: Optional[str] = Field(default=None, description="e.g., 'Marketing Manager'")
    industry: Optional[str] = Field(default=None, description="e.g., 'SaaS B2B, Tech'")


class CampaignAsset(BaseModel):
    """Asset for a marketing campaign."""
    name: str = Field(..., description="Asset name")
    type: str = Field(..., description="Asset type: web, video, email, social, content")
    status: str = Field(default="pianificato", description="Status: completato, in produzione, draft, pianificato, in revisione")


class CampaignResult(BaseModel):
    """Result metric for a campaign."""
    metric: str = Field(..., description="Metric name")
    value: str = Field(..., description="Metric value")
    trend: Optional[str] = Field(default=None, description="Trend: up, down, stable")


class RelatedContent(BaseModel):
    """Related content reference for topics."""
    title: str = Field(..., description="Content title")
    type: str = Field(..., description="Content type: blog, webinar, resource, case-study")
    url: Optional[str] = Field(default=None, description="Content URL")


class Trend(BaseModel):
    """Market or industry trend."""
    trend: str = Field(..., description="Trend description")
    relevance: str = Field(default="medium", description="Relevance: high, medium, low")


class ChannelMetric(BaseModel):
    """Performance metric for a specific channel."""
    channel: str = Field(..., description="Channel name: LinkedIn, Email, Blog, etc.")
    contentType: str = Field(..., description="Content type")
    ctr: Optional[float] = Field(default=None, description="Click-through rate")
    engagement: Optional[float] = Field(default=None, description="Engagement rate")
    impressions: Optional[int] = Field(default=None, description="Number of impressions")
    conversions: Optional[int] = Field(default=None, description="Number of conversions")


class TopContent(BaseModel):
    """Top performing content item."""
    title: str = Field(..., description="Content title")
    type: str = Field(..., description="Content type")
    metric: str = Field(..., description="Primary metric name")
    value: str = Field(..., description="Metric value")


# =============================================================================
# BASE CARD
# =============================================================================

class CardBase(BaseModel):
    """
    Base fields shared by ALL card types.

    Design: These fields are required for every card to enable:
    - Unique identification (id)
    - Type discrimination (type)
    - Display (title)
    - Audit trail (createdAt, updatedAt)
    - Session correlation (sessionId)
    """
    id: str = Field(default_factory=lambda: f"card-{uuid4().hex[:8]}", description="Unique card ID")
    title: str = Field(..., description="Card display title")
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
    sessionId: str = Field(..., description="Onboarding session ID that generated this card")


# =============================================================================
# CARD TYPE DEFINITIONS (matching mock exactly)
# =============================================================================

class ProductCard(CardBase):
    """
    Product/service card - describes what the company offers.

    Purpose: Central value proposition and product capabilities.
    Source: Inferred from company research, website, user input.
    """
    type: Literal["product"] = "product"

    # Core value proposition - REQUIRED
    valueProposition: str = Field(..., description="Main value proposition (2-3 sentences)")

    # Product details - Optional for progressive enhancement
    features: List[str] = Field(default_factory=list, description="Key product features")
    differentiators: List[str] = Field(default_factory=list, description="Competitive differentiators")
    useCases: List[str] = Field(default_factory=list, description="Primary use cases")
    performanceMetrics: List[PerformanceMetric] = Field(default_factory=list, description="Key metrics/KPIs")


class TargetCard(CardBase):
    """
    Target audience card - Ideal Customer Profile (ICP).

    Purpose: Define who the content is for.
    Source: Inferred from company research, website, user clarification.
    Note: Multiple target cards can exist (primary, secondary audiences).
    """
    type: Literal["target"] = "target"

    # Core ICP - REQUIRED
    icpName: str = Field(..., description="Persona name (e.g., 'Marco, il Marketing Manager')")
    description: str = Field(..., description="Detailed persona description")

    # Pain points and goals - Critical for content generation
    painPoints: List[str] = Field(default_factory=list, description="Customer pain points")
    goals: List[str] = Field(default_factory=list, description="Customer goals")

    # Communication preferences - Optional
    preferredLanguage: Optional[str] = Field(default=None, description="Language and style preference")
    communicationChannels: List[str] = Field(default_factory=list, description="Preferred channels")
    demographics: Optional[Demographics] = Field(default=None, description="Demographic details")


class CampaignsCard(CardBase):
    """
    Marketing campaign card - planned or active campaigns.

    Purpose: Track campaign objectives, assets, and results.
    Source: User input, inferred from goals.
    Note: Initially stub - populated as campaigns are created.
    """
    type: Literal["campaigns"] = "campaigns"

    # Campaign definition - REQUIRED
    objective: str = Field(..., description="Campaign objective with measurable goal")

    # Messaging
    keyMessages: List[str] = Field(default_factory=list, description="Key campaign messages")
    tone: Optional[str] = Field(default=None, description="Campaign tone of voice")

    # Assets and results - Progressive
    assets: List[CampaignAsset] = Field(default_factory=list, description="Campaign assets")
    results: List[CampaignResult] = Field(default_factory=list, description="Campaign results")
    learnings: List[str] = Field(default_factory=list, description="Key learnings from campaign")


class TopicCard(CardBase):
    """
    Content topic card - thematic clusters for content.

    Purpose: Define content pillars and topic areas.
    Source: Inferred from company, industry, target audience.
    """
    type: Literal["topic"] = "topic"

    # Topic definition - REQUIRED
    description: str = Field(..., description="Topic description and relevance")

    # SEO and content planning
    keywords: List[str] = Field(default_factory=list, description="Related keywords for SEO")
    angles: List[str] = Field(default_factory=list, description="Content angles to explore")

    # Related content and trends
    relatedContent: List[RelatedContent] = Field(default_factory=list, description="Related content pieces")
    trends: List[Trend] = Field(default_factory=list, description="Relevant market trends")


class BrandVoiceCard(CardBase):
    """
    Brand voice card - tone and style guidelines.

    Purpose: Ensure consistent brand voice across all content.
    Source: Inferred from website, existing content, user input.
    """
    type: Literal["brand_voice"] = "brand_voice"

    # Voice definition - REQUIRED
    toneDescription: str = Field(..., description="Detailed tone of voice description")

    # Style guidelines
    styleGuidelines: List[str] = Field(default_factory=list, description="Writing style rules")

    # Examples - Critical for LLM prompting
    dosExamples: List[str] = Field(default_factory=list, description="Good examples (DO this)")
    dontsExamples: List[str] = Field(default_factory=list, description="Bad examples (DON'T do this)")

    # Vocabulary
    termsToUse: List[str] = Field(default_factory=list, description="Preferred terminology")
    termsToAvoid: List[str] = Field(default_factory=list, description="Terms to avoid")


class CompetitorCard(CardBase):
    """
    Competitor analysis card - competitive intelligence.

    Purpose: Understand competitive landscape for differentiation.
    Source: Inferred from research, user input.
    """
    type: Literal["competitor"] = "competitor"

    # Competitor identity - REQUIRED
    competitorName: str = Field(..., description="Competitor company name")
    positioning: str = Field(..., description="Competitor's market positioning")

    # Competitive analysis
    keyMessages: List[str] = Field(default_factory=list, description="Competitor's key messages")
    strengths: List[str] = Field(default_factory=list, description="Competitor strengths")
    weaknesses: List[str] = Field(default_factory=list, description="Competitor weaknesses")
    differentiationOpportunities: List[str] = Field(default_factory=list, description="Opportunities to differentiate")


class PerformanceCard(CardBase):
    """
    Performance analytics card - content performance data.

    Purpose: Track what content works and inform future strategy.
    Source: Analytics integration, manual input.
    Note: Initially empty - populated as content is published.
    """
    type: Literal["performance"] = "performance"

    # Period - REQUIRED
    period: str = Field(..., description="Reporting period (e.g., 'Ottobre - Dicembre 2024')")

    # Metrics by channel
    metrics: List[ChannelMetric] = Field(default_factory=list, description="Performance metrics by channel")
    topPerformingContent: List[TopContent] = Field(default_factory=list, description="Best performing content")

    # Insights
    insights: List[str] = Field(default_factory=list, description="Data-driven insights")


class FeedbackCard(CardBase):
    """
    Feedback card - user feedback and learnings.

    Purpose: Capture feedback for continuous improvement.
    Source: User input, A/B tests, customer feedback.
    """
    type: Literal["feedback"] = "feedback"

    # Feedback source - REQUIRED
    source: FeedbackSource = Field(..., description="Source of feedback")
    summary: str = Field(..., description="Brief summary of feedback")

    # Details
    details: Optional[str] = Field(default=None, description="Detailed feedback analysis")
    actionItems: List[str] = Field(default_factory=list, description="Action items from feedback")

    # Relations and priority
    relatedCards: List[str] = Field(default_factory=list, description="Related card IDs")
    priority: FeedbackPriority = Field(default=FeedbackPriority.MEDIUM, description="Priority level")


# =============================================================================
# UNION TYPE - Discriminated by 'type' field
# =============================================================================

Card = Union[
    ProductCard,
    TargetCard,
    CampaignsCard,
    TopicCard,
    BrandVoiceCard,
    CompetitorCard,
    PerformanceCard,
    FeedbackCard,
]
"""
Card is the discriminated union of all card types.

Usage:
    card_data = {"type": "product", "title": "...", ...}
    card = Card.model_validate(card_data)  # Returns ProductCard instance
"""


# =============================================================================
# OUTPUT ENVELOPE - The contract for onboarding output
# =============================================================================

class CardsOutput(BaseModel):
    """
    The canonical output of the onboarding pipeline.

    This is the ONLY output format - no legacy alternatives.
    The UI consumes this JSON directly to render cards.
    """
    sessionId: str = Field(..., description="Onboarding session ID")
    generatedAt: datetime = Field(default_factory=datetime.utcnow, description="ISO timestamp of generation")
    cards: List[Card] = Field(default_factory=list, description="Generated cards array")

    # Metadata for debugging/audit
    version: str = Field(default="1.0", description="Schema version")

    def get_cards_by_type(self, card_type: CardType) -> List[Card]:
        """Get all cards of a specific type."""
        return [c for c in self.cards if c.type == card_type.value]

    def get_product_card(self) -> Optional[ProductCard]:
        """Get the product card (should be exactly one)."""
        cards = self.get_cards_by_type(CardType.PRODUCT)
        return cards[0] if cards else None

    def get_brand_voice_card(self) -> Optional[BrandVoiceCard]:
        """Get the brand voice card (should be exactly one)."""
        cards = self.get_cards_by_type(CardType.BRAND_VOICE)
        return cards[0] if cards else None

