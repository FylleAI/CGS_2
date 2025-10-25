"""Unit tests for CardServiceAdapter."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from onboarding.infrastructure.adapters.card_service_adapter import CardServiceAdapter
from onboarding.config.settings import OnboardingSettings


@pytest.fixture
def settings():
    """Create test settings."""
    return OnboardingSettings(
        card_service_api_url="http://localhost:8000",
        card_service_api_timeout=30,
        card_service_api_key="test-key",
    )


@pytest.fixture
def adapter(settings):
    """Create adapter instance."""
    return CardServiceAdapter(settings)


@pytest.mark.asyncio
async def test_create_cards_from_snapshot_success(adapter):
    """Test successful card creation from snapshot."""
    snapshot = {
        "company_info": {
            "name": "Test Company",
            "description": "Test Description",
        },
        "audience_info": {
            "target_audience": "Tech professionals",
        },
        "goal": "content_generation",
        "insights": {},
    }

    expected_response = [
        {
            "id": "card-1",
            "card_type": "product",
            "title": "Test Product",
            "content": {"name": "Test Product"},
        },
        {
            "id": "card-2",
            "card_type": "persona",
            "title": "Test Persona",
            "content": {"name": "Test Persona"},
        },
    ]

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = expected_response
        mock_response.raise_for_status = MagicMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client

        result = await adapter.create_cards_from_snapshot(
            tenant_id="test@example.com",
            snapshot=snapshot,
        )

        assert result == expected_response
        assert len(result) == 2
        mock_client.post.assert_called_once()


@pytest.mark.asyncio
async def test_create_cards_from_snapshot_http_error(adapter):
    """Test HTTP error handling."""
    snapshot = {"company_info": {}}

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"detail": "Internal server error"}
        mock_response.raise_for_status.side_effect = Exception("HTTP 500")
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client

        with pytest.raises(Exception):
            await adapter.create_cards_from_snapshot(
                tenant_id="test@example.com",
                snapshot=snapshot,
            )


@pytest.mark.asyncio
async def test_create_cards_invalid_response(adapter):
    """Test invalid response handling."""
    snapshot = {"company_info": {}}

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"invalid": "response"}  # Not a list
        mock_response.raise_for_status = MagicMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client

        with pytest.raises(ValueError):
            await adapter.create_cards_from_snapshot(
                tenant_id="test@example.com",
                snapshot=snapshot,
            )


@pytest.mark.asyncio
async def test_health_check_success(adapter):
    """Test successful health check."""
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client

        result = await adapter.health_check()

        assert result is True
        mock_client.get.assert_called_once()


@pytest.mark.asyncio
async def test_health_check_failure(adapter):
    """Test health check failure."""
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.get.side_effect = Exception("Connection failed")
        mock_client_class.return_value.__aenter__.return_value = mock_client

        result = await adapter.health_check()

        assert result is False


def test_build_headers_with_api_key(adapter):
    """Test header building with API key."""
    headers = adapter._build_headers()

    assert "Content-Type" in headers
    assert headers["Content-Type"] == "application/json"
    assert "Authorization" in headers
    assert headers["Authorization"] == "Bearer test-key"


def test_build_headers_without_api_key(settings):
    """Test header building without API key."""
    settings.card_service_api_key = None
    adapter = CardServiceAdapter(settings)

    headers = adapter._build_headers()

    assert "Content-Type" in headers
    assert "Authorization" not in headers

