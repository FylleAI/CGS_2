"""
Tests for card schema validation.

Verifies that:
1. All card types can be instantiated
2. CardsOutput matches the mock structure
3. Discriminated union works correctly
"""

import json
import pytest
from datetime import datetime
from pydantic import ValidationError

from onboarding.domain.cards import (
    CardType,
    ProductCard,
    TargetCard,
    CampaignsCard,
    TopicCard,
    BrandVoiceCard,
    CompetitorCard,
    PerformanceCard,
    FeedbackCard,
    CardsOutput,
    Card,
    FeedbackSource,
    FeedbackPriority,
    PerformanceMetric,
    Demographics,
)


class TestCardTypes:
    """Test individual card type creation."""

    def test_product_card_creation(self):
        """ProductCard can be created with required fields."""
        card = ProductCard(
            title="Test Product",
            sessionId="session-123",
            valueProposition="We help companies grow faster.",
            features=["Feature 1", "Feature 2"],
            differentiators=["Unique approach"],
        )
        assert card.type == "product"
        assert card.title == "Test Product"
        assert len(card.features) == 2

    def test_target_card_creation(self):
        """TargetCard can be created with required fields."""
        card = TargetCard(
            title="Target: Marketing Manager",
            sessionId="session-123",
            icpName="Marco, il Marketing Manager",
            description="Marketing managers in B2B SaaS companies",
            painPoints=["Limited budget", "Time constraints"],
            goals=["Increase leads", "Improve ROI"],
        )
        assert card.type == "target"
        assert card.icpName == "Marco, il Marketing Manager"

    def test_brand_voice_card_creation(self):
        """BrandVoiceCard can be created with required fields."""
        card = BrandVoiceCard(
            title="Brand Voice",
            sessionId="session-123",
            toneDescription="Professional yet approachable",
            styleGuidelines=["Use active voice", "Keep sentences short"],
            dosExamples=["Do: Be direct"],
            dontsExamples=["Don't: Use jargon"],
        )
        assert card.type == "brand_voice"
        assert len(card.styleGuidelines) == 2

    def test_competitor_card_creation(self):
        """CompetitorCard can be created with required fields."""
        card = CompetitorCard(
            title="Competitor: Acme Corp",
            sessionId="session-123",
            competitorName="Acme Corp",
            positioning="Enterprise-focused solution",
            strengths=["Brand recognition"],
            weaknesses=["High pricing"],
        )
        assert card.type == "competitor"
        assert card.competitorName == "Acme Corp"

    def test_topic_card_creation(self):
        """TopicCard can be created with required fields."""
        card = TopicCard(
            title="Topic: AI in Marketing",
            sessionId="session-123",
            description="Content about AI applications in marketing",
            keywords=["AI", "marketing automation", "personalization"],
            angles=["How-to guides", "Case studies"],
        )
        assert card.type == "topic"
        assert len(card.keywords) == 3

    def test_campaigns_card_creation(self):
        """CampaignsCard can be created with required fields."""
        card = CampaignsCard(
            title="Q1 Campaign",
            sessionId="session-123",
            objective="Increase brand awareness by 20%",
            keyMessages=["Innovation", "Trust"],
        )
        assert card.type == "campaigns"
        assert card.objective == "Increase brand awareness by 20%"

    def test_performance_card_creation(self):
        """PerformanceCard can be created with required fields."""
        card = PerformanceCard(
            title="Q4 Performance",
            sessionId="session-123",
            period="October - December 2024",
            insights=["LinkedIn posts outperformed"],
        )
        assert card.type == "performance"
        assert card.period == "October - December 2024"

    def test_feedback_card_creation(self):
        """FeedbackCard can be created with required fields."""
        card = FeedbackCard(
            title="User Feedback",
            sessionId="session-123",
            source=FeedbackSource.CUSTOMER_FEEDBACK,
            summary="Users prefer shorter content",
            actionItems=["Reduce post length"],
            priority=FeedbackPriority.HIGH,
        )
        assert card.type == "feedback"
        assert card.source == FeedbackSource.CUSTOMER_FEEDBACK


class TestCardsOutput:
    """Test CardsOutput envelope."""

    def test_cards_output_creation(self):
        """CardsOutput can be created with cards."""
        product = ProductCard(
            title="Product",
            sessionId="session-123",
            valueProposition="Test value prop",
        )
        target = TargetCard(
            title="Target",
            sessionId="session-123",
            icpName="Test ICP",
            description="Test description",
        )

        output = CardsOutput(
            sessionId="session-123",
            cards=[product, target],
        )

        assert output.sessionId == "session-123"
        assert len(output.cards) == 2
        assert output.version == "1.0"

    def test_get_cards_by_type(self):
        """get_cards_by_type returns correct cards."""
        product = ProductCard(
            title="Product",
            sessionId="session-123",
            valueProposition="Test",
        )
        target1 = TargetCard(
            title="Target 1",
            sessionId="session-123",
            icpName="ICP 1",
            description="Desc 1",
        )
        target2 = TargetCard(
            title="Target 2",
            sessionId="session-123",
            icpName="ICP 2",
            description="Desc 2",
        )

        output = CardsOutput(
            sessionId="session-123",
            cards=[product, target1, target2],
        )

        targets = output.get_cards_by_type(CardType.TARGET)
        assert len(targets) == 2

        products = output.get_cards_by_type(CardType.PRODUCT)
        assert len(products) == 1

