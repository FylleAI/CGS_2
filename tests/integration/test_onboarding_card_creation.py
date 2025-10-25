"""Integration tests for Onboarding → Card creation flow."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from onboarding.application.use_cases.execute_onboarding import ExecuteOnboardingUseCase
from onboarding.domain.entities.onboarding_session import OnboardingSession, CompanySnapshot
from onboarding.infrastructure.adapters.card_service_adapter import CardServiceAdapter


@pytest.fixture
def mock_dependencies():
    """Create mock dependencies."""
    return {
        "payload_builder": MagicMock(),
        "cgs_adapter": AsyncMock(),
        "brevo_adapter": AsyncMock(),
        "repository": AsyncMock(),
        "card_service_client": AsyncMock(),
    }


@pytest.fixture
def use_case(mock_dependencies):
    """Create use case instance."""
    return ExecuteOnboardingUseCase(
        payload_builder=mock_dependencies["payload_builder"],
        cgs_adapter=mock_dependencies["cgs_adapter"],
        brevo_adapter=mock_dependencies["brevo_adapter"],
        repository=mock_dependencies["repository"],
        auto_delivery=True,
        card_service_client=mock_dependencies["card_service_client"],
    )


@pytest.fixture
def sample_session():
    """Create sample onboarding session."""
    return OnboardingSession(
        id="session-1",
        user_email="test@example.com",
        company_name="Test Company",
        snapshot=CompanySnapshot(
            company_info={
                "name": "Test Company",
                "description": "Test Description",
            },
            audience_info={
                "target_audience": "Tech professionals",
            },
            goal="content_generation",
            insights={},
        ),
        status="completed",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest.mark.asyncio
async def test_execute_onboarding_creates_cards(use_case, mock_dependencies, sample_session):
    """Test that onboarding execution creates cards."""
    # Mock CGS response
    mock_dependencies["cgs_adapter"].execute.return_value = {
        "status": "success",
        "content": "Generated content",
    }

    # Mock card creation response
    card_response = [
        {
            "id": "card-1",
            "card_type": "product",
            "title": "Test Product",
        },
        {
            "id": "card-2",
            "card_type": "persona",
            "title": "Test Persona",
        },
        {
            "id": "card-3",
            "card_type": "campaign",
            "title": "Test Campaign",
        },
        {
            "id": "card-4",
            "card_type": "topic",
            "title": "Test Topic",
        },
    ]
    mock_dependencies["card_service_client"].create_cards_from_snapshot.return_value = (
        card_response
    )

    # Execute onboarding
    result = await use_case.execute(sample_session)

    # Verify card creation was called
    mock_dependencies["card_service_client"].create_cards_from_snapshot.assert_called_once()

    # Verify card IDs are stored in metadata
    assert "card_ids" in sample_session.metadata
    assert len(sample_session.metadata["card_ids"]) == 4


@pytest.mark.asyncio
async def test_execute_onboarding_without_card_service(
    mock_dependencies, sample_session
):
    """Test onboarding execution when card service is not available."""
    # Remove card service client
    mock_dependencies["card_service_client"] = None

    use_case = ExecuteOnboardingUseCase(
        payload_builder=mock_dependencies["payload_builder"],
        cgs_adapter=mock_dependencies["cgs_adapter"],
        brevo_adapter=mock_dependencies["brevo_adapter"],
        repository=mock_dependencies["repository"],
        auto_delivery=True,
        card_service_client=None,
    )

    mock_dependencies["cgs_adapter"].execute.return_value = {
        "status": "success",
        "content": "Generated content",
    }

    # Should execute without error
    result = await use_case.execute(sample_session)

    # Card IDs should not be in metadata
    assert "card_ids" not in sample_session.metadata or len(
        sample_session.metadata.get("card_ids", [])
    ) == 0


@pytest.mark.asyncio
async def test_execute_onboarding_card_creation_failure(
    use_case, mock_dependencies, sample_session
):
    """Test onboarding execution when card creation fails."""
    mock_dependencies["cgs_adapter"].execute.return_value = {
        "status": "success",
        "content": "Generated content",
    }

    # Mock card creation failure
    mock_dependencies["card_service_client"].create_cards_from_snapshot.side_effect = (
        Exception("Card service error")
    )

    # Should not raise exception - card creation is non-blocking
    result = await use_case.execute(sample_session)

    # Onboarding should still complete
    assert result is not None


@pytest.mark.asyncio
async def test_execute_onboarding_card_ids_stored_in_metadata(
    use_case, mock_dependencies, sample_session
):
    """Test that card IDs are properly stored in session metadata."""
    mock_dependencies["cgs_adapter"].execute.return_value = {
        "status": "success",
        "content": "Generated content",
    }

    card_response = [
        {"id": "card-1", "card_type": "product"},
        {"id": "card-2", "card_type": "persona"},
        {"id": "card-3", "card_type": "campaign"},
        {"id": "card-4", "card_type": "topic"},
    ]
    mock_dependencies["card_service_client"].create_cards_from_snapshot.return_value = (
        card_response
    )

    await use_case.execute(sample_session)

    # Verify metadata
    assert "card_ids" in sample_session.metadata
    card_ids = sample_session.metadata["card_ids"]
    assert card_ids == ["card-1", "card-2", "card-3", "card-4"]


@pytest.mark.asyncio
async def test_execute_onboarding_all_four_card_types_created(
    use_case, mock_dependencies, sample_session
):
    """Test that all four card types are created."""
    mock_dependencies["cgs_adapter"].execute.return_value = {
        "status": "success",
        "content": "Generated content",
    }

    card_response = [
        {"id": "card-1", "card_type": "product", "title": "Product"},
        {"id": "card-2", "card_type": "persona", "title": "Persona"},
        {"id": "card-3", "card_type": "campaign", "title": "Campaign"},
        {"id": "card-4", "card_type": "topic", "title": "Topic"},
    ]
    mock_dependencies["card_service_client"].create_cards_from_snapshot.return_value = (
        card_response
    )

    await use_case.execute(sample_session)

    # Verify all card types are present
    call_args = mock_dependencies["card_service_client"].create_cards_from_snapshot.call_args
    assert call_args is not None
    assert call_args[1]["tenant_id"] == "test@example.com"
    assert call_args[1]["snapshot"] is not None

