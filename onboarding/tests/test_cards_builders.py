"""
Tests for card builders.

Verifies that builders correctly convert OnboardingRawInput to typed cards.
"""

import pytest
from datetime import datetime

from onboarding.domain.cards import (
    OnboardingRawInput,
    UserInput,
    InferredData,
    InferredCompanyData,
    InferredAudienceData,
    InferredVoiceData,
    InferredCompetitorData,
    InferredTopicData,
    ProductCard,
    TargetCard,
    BrandVoiceCard,
    CompetitorCard,
    TopicCard,
)
from onboarding.application.cards import (
    build_product_card,
    build_target_cards,
    build_brand_voice_card,
    build_competitor_cards,
    build_topic_cards,
)


@pytest.fixture
def sample_raw_input() -> OnboardingRawInput:
    """Create a sample OnboardingRawInput for testing."""
    return OnboardingRawInput(
        session_id="test-session-123",
        user_input=UserInput(
            brand_name="TestCorp",
            user_email="test@example.com",
            website="https://testcorp.com",
            industry_hint="SaaS",
            target_channels=["linkedin", "twitter"],
        ),
        inferred=InferredData(
            company=InferredCompanyData(
                legal_name="TestCorp Inc.",
                description="TestCorp helps businesses automate their workflows.",
                industry="SaaS",
                key_offerings=["Workflow automation", "Integration platform"],
                differentiators=["AI-powered", "No-code interface"],
                value_proposition="Automate your business in minutes, not months.",
            ),
            audience=InferredAudienceData(
                primary_audience="Operations managers in mid-size companies",
                secondary_audiences=["IT directors", "Business analysts"],
                pain_points=["Manual processes", "Integration challenges"],
                goals=["Reduce operational costs", "Improve efficiency"],
                communication_channels=["LinkedIn", "Email"],
            ),
            voice=InferredVoiceData(
                tone="Professional yet friendly",
                style_guidelines=["Use active voice", "Be concise"],
                dos_examples=["Do: Speak directly to pain points"],
                donts_examples=["Don't: Use technical jargon"],
                terms_to_use=["automation", "efficiency"],
                terms_to_avoid=["complicated", "difficult"],
            ),
            competitors=[
                InferredCompetitorData(
                    name="Competitor A",
                    positioning="Enterprise-focused",
                    strengths=["Brand recognition"],
                    weaknesses=["High pricing"],
                ),
                InferredCompetitorData(
                    name="Competitor B",
                    positioning="SMB-focused",
                    strengths=["Easy to use"],
                    weaknesses=["Limited features"],
                ),
            ],
            topics=[
                InferredTopicData(
                    name="Workflow Automation",
                    description="Content about automating business processes",
                    keywords=["automation", "workflow", "efficiency"],
                    angles=["How-to guides", "ROI calculators"],
                ),
            ],
        ),
    )


class TestBuildProductCard:
    """Test build_product_card function."""

    def test_builds_product_card_with_value_proposition(self, sample_raw_input):
        """Product card uses inferred value proposition."""
        card = build_product_card(sample_raw_input)

        assert isinstance(card, ProductCard)
        assert card.type == "product"
        assert card.sessionId == "test-session-123"
        assert "Automate your business" in card.valueProposition
        assert "Workflow automation" in card.features
        assert "AI-powered" in card.differentiators

    def test_builds_product_card_with_fallback(self):
        """Product card uses fallback when value proposition missing."""
        raw = OnboardingRawInput(
            session_id="test-123",
            user_input=UserInput(
                brand_name="MinimalCorp",
                user_email="test@example.com",
            ),
        )

        card = build_product_card(raw)

        assert card.type == "product"
        assert "MinimalCorp" in card.valueProposition


class TestBuildTargetCards:
    """Test build_target_cards function."""

    def test_builds_multiple_target_cards(self, sample_raw_input):
        """Creates cards for primary and secondary audiences."""
        cards = build_target_cards(sample_raw_input)

        assert len(cards) >= 1
        assert all(isinstance(c, TargetCard) for c in cards)
        assert all(c.type == "target" for c in cards)

        # Primary audience should have pain points
        primary = cards[0]
        assert len(primary.painPoints) > 0
        assert len(primary.goals) > 0

    def test_builds_fallback_target_card(self):
        """Creates fallback card when no audience data."""
        raw = OnboardingRawInput(
            session_id="test-123",
            user_input=UserInput(
                brand_name="MinimalCorp",
                user_email="test@example.com",
            ),
        )

        cards = build_target_cards(raw)

        assert len(cards) == 1
        assert cards[0].type == "target"


class TestBuildBrandVoiceCard:
    """Test build_brand_voice_card function."""

    def test_builds_brand_voice_card(self, sample_raw_input):
        """Brand voice card uses inferred voice data."""
        card = build_brand_voice_card(sample_raw_input)

        assert isinstance(card, BrandVoiceCard)
        assert card.type == "brand_voice"
        assert "Professional" in card.toneDescription
        assert len(card.styleGuidelines) > 0
        assert len(card.dosExamples) > 0
        assert len(card.dontsExamples) > 0

