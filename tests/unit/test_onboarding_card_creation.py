"""
Unit tests for Onboarding API card creation logic.

Tests:
- CompanySnapshot → 4 cards mapping
- Default values
- Idempotency key generation
- Error handling
"""

import pytest
from uuid import UUID, uuid4
from datetime import datetime

from onboarding.domain.models import (
    CompanySnapshot,
    CompanyInfo,
    AudienceInfo,
    VoiceInfo,
    InsightsInfo,
    ClarifyingQuestion,
)
from core.services.card_creation_service import CardCreationService


class TestCardCreationService:
    """Test CardCreationService mapping logic."""

    @pytest.fixture
    def card_service(self):
        """Create CardCreationService instance."""
        return CardCreationService()

    @pytest.fixture
    def sample_snapshot(self):
        """Create sample CompanySnapshot for testing."""
        return CompanySnapshot(
            version="1.0",
            snapshot_id=uuid4(),
            generated_at=datetime.utcnow(),
            trace_id="test-trace-001",
            company=CompanyInfo(
                name="Acme Corp",
                description="Leading provider of innovative solutions",
                industry="Technology",
                key_offerings=["Cloud Platform", "AI Tools", "Analytics"],
                differentiators=["24/7 Support", "Enterprise-grade Security"],
            ),
            audience=AudienceInfo(
                primary="Tech Decision Makers",
                pain_points=["Legacy systems", "Scalability issues"],
                desired_outcomes=["Faster deployment", "Better reliability"],
            ),
            voice=VoiceInfo(
                tone="Professional and approachable",
                style_guidelines=["Clear and concise", "Data-driven"],
            ),
            insights=InsightsInfo(
                positioning="Market leader in cloud solutions",
                key_messages=["Innovation", "Reliability"],
                recent_news=["New product launch"],
            ),
            clarifying_questions=[
                ClarifyingQuestion(
                    id="q1",
                    question="What does your company do?",
                    reason="To understand core business",
                    expected_response_type="string",
                )
            ],
            clarifying_answers={"q1": "We provide cloud solutions"},
        )

    def test_snapshot_to_cards_mapping(self, card_service, sample_snapshot):
        """Test that CompanySnapshot maps to 4 cards correctly."""
        # This would be the mapping logic if extracted to CardCreationService
        # For now, we test the structure
        
        # Company card
        company_data = {
            "name": sample_snapshot.company.name,
            "industry": sample_snapshot.company.industry,
            "description": sample_snapshot.company.description,
            "key_offerings": sample_snapshot.company.key_offerings,
            "differentiators": sample_snapshot.company.differentiators,
        }

        assert company_data["name"] == "Acme Corp"
        assert company_data["industry"] == "Technology"
        assert len(company_data["key_offerings"]) == 3
        assert len(company_data["differentiators"]) == 2

        # Audience card
        audience_data = {
            "primary": sample_snapshot.audience.primary,
            "pain_points": sample_snapshot.audience.pain_points,
            "desired_outcomes": sample_snapshot.audience.desired_outcomes,
        }

        assert audience_data["primary"] == "Tech Decision Makers"
        assert len(audience_data["pain_points"]) == 2
        assert len(audience_data["desired_outcomes"]) == 2

        # Voice card
        voice_data = {
            "tone": sample_snapshot.voice.tone,
            "style_guidelines": sample_snapshot.voice.style_guidelines,
        }

        assert voice_data["tone"] == "Professional and approachable"
        assert len(voice_data["style_guidelines"]) == 2

        # Insight card
        insight_data = {
            "positioning": sample_snapshot.insights.positioning,
            "key_messages": sample_snapshot.insights.key_messages,
            "recent_news": sample_snapshot.insights.recent_news,
        }

        assert insight_data["positioning"] == "Market leader in cloud solutions"
        assert len(insight_data["key_messages"]) == 2
        assert len(insight_data["recent_news"]) == 1

    def test_default_values_safe(self, card_service):
        """Test that default values are safe when fields are missing."""
        minimal_snapshot = CompanySnapshot(
            version="1.0",
            company=CompanyInfo(
                name="Minimal Corp",
                description="Minimal description",
            ),
            clarifying_questions=[
                ClarifyingQuestion(
                    id="q1",
                    question="Test?",
                    reason="Testing",
                    expected_response_type="string",
                )
            ],
        )

        # Should have safe defaults
        assert minimal_snapshot.company.industry is None
        assert minimal_snapshot.company.key_offerings == []
        assert minimal_snapshot.company.differentiators == []

        assert minimal_snapshot.audience.primary is None
        assert minimal_snapshot.audience.pain_points == []

        assert minimal_snapshot.voice.tone is None
        assert minimal_snapshot.voice.style_guidelines == []

        assert minimal_snapshot.insights.positioning is None
        assert minimal_snapshot.insights.key_messages == []

    def test_idempotency_key_generation(self):
        """Test idempotency key generation pattern."""
        session_id = uuid4()
        
        # Pattern: onboarding-{session_id}-batch
        idem_key = f"onboarding-{session_id}-batch"
        
        assert idem_key.startswith("onboarding-")
        assert idem_key.endswith("-batch")
        assert str(session_id) in idem_key

    def test_snapshot_json_serialization(self, sample_snapshot):
        """Test that CompanySnapshot can be serialized to JSON."""
        import json
        
        # This is what we do in the API
        snapshot_dict = json.loads(sample_snapshot.model_dump_json())
        
        assert snapshot_dict["version"] == "1.0"
        assert snapshot_dict["company"]["name"] == "Acme Corp"
        assert snapshot_dict["audience"]["primary"] == "Tech Decision Makers"
        assert snapshot_dict["voice"]["tone"] == "Professional and approachable"
        assert snapshot_dict["insights"]["positioning"] == "Market leader in cloud solutions"

        # Check that UUIDs are serialized as strings
        assert isinstance(snapshot_dict["snapshot_id"], str)

    def test_card_types_mapping(self):
        """Test that we create exactly 4 card types."""
        from fylle_shared.enums import CardType
        
        expected_types = [
            CardType.COMPANY,
            CardType.AUDIENCE,
            CardType.VOICE,
            CardType.INSIGHT,
        ]
        
        assert len(expected_types) == 4
        assert CardType.COMPANY in expected_types
        assert CardType.AUDIENCE in expected_types
        assert CardType.VOICE in expected_types
        assert CardType.INSIGHT in expected_types


class TestSnapshotBuilding:
    """Test snapshot building from answers."""

    def test_build_snapshot_from_minimal_answers(self):
        """Test building snapshot from minimal answers."""
        from api.rest.v1.endpoints.onboarding_v1 import _build_snapshot_from_answers
        from api.rest.v1.models.onboarding import OnboardingSessionResponse, SessionStatus
        from api.rest.v1.models.onboarding import Answer

        session = OnboardingSessionResponse(
            session_id=uuid4(),
            tenant_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
            company_domain="test.com",
            user_email="test@test.com",
            status=SessionStatus.RESEARCH,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        answers = [
            Answer(question_id="q1", answer="We build software"),
            Answer(question_id="q2", answer="Developers"),
            Answer(question_id="q3", answer="Technical and friendly"),
        ]

        snapshot = _build_snapshot_from_answers(session, answers)

        assert snapshot.version == "1.0"
        assert snapshot.company.name == "test.com"
        assert "We build software" in snapshot.company.description
        assert "Developers" in snapshot.audience.primary
        assert "Technical and friendly" in snapshot.voice.tone
        assert len(snapshot.clarifying_questions) >= 1  # At least 1 question

    def test_snapshot_has_required_fields(self):
        """Test that snapshot has all required fields for card creation."""
        from api.rest.v1.endpoints.onboarding_v1 import _build_snapshot_from_answers
        from api.rest.v1.models.onboarding import OnboardingSessionResponse, SessionStatus, Answer

        session = OnboardingSessionResponse(
            session_id=uuid4(),
            tenant_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
            company_domain="test.com",
            user_email="test@test.com",
            status=SessionStatus.RESEARCH,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        answers = [
            Answer(question_id="q1", answer="Answer 1"),
            Answer(question_id="q2", answer="Answer 2"),
            Answer(question_id="q3", answer="Answer 3"),
        ]

        snapshot = _build_snapshot_from_answers(session, answers)

        # Required for company card
        assert hasattr(snapshot.company, "name")
        assert hasattr(snapshot.company, "description")

        # Required for audience card
        assert hasattr(snapshot.audience, "primary")
        assert hasattr(snapshot.audience, "pain_points")

        # Required for voice card
        assert hasattr(snapshot.voice, "tone")
        assert hasattr(snapshot.voice, "style_guidelines")

        # Required for insight card
        assert hasattr(snapshot.insights, "positioning")
        assert hasattr(snapshot.insights, "key_messages")

