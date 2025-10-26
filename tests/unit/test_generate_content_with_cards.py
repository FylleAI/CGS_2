"""Unit tests for GenerateContentUseCase with Card Service integration."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from services.content_workflow.application.use_cases.generate_content import GenerateContentUseCase
from services.content_workflow.application.dto.content_request import ContentGenerationRequest
from services.content_workflow.domain.entities.content import ContentType, ContentFormat
from services.content_workflow.domain.value_objects.provider_config import ProviderConfig, LLMProvider
from services.card_service.domain.entities.card import Card, CardType, CardContent


@pytest.fixture
def mock_repositories():
    """Create mock repositories."""
    return {
        "content": AsyncMock(),
        "workflow": AsyncMock(),
        "agent": AsyncMock(),
        "card": AsyncMock(),
    }


@pytest.fixture
def mock_llm_provider():
    """Create mock LLM provider."""
    return AsyncMock()


@pytest.fixture
def provider_config():
    """Create provider config."""
    return ProviderConfig(
        provider=LLMProvider.OPENAI,
        model="gpt-4",
        api_key="test-key",
    )


@pytest.fixture
def use_case(mock_repositories, mock_llm_provider, provider_config):
    """Create use case instance with card repository."""
    return GenerateContentUseCase(
        content_repository=mock_repositories["content"],
        workflow_repository=mock_repositories["workflow"],
        agent_repository=mock_repositories["agent"],
        llm_provider=mock_llm_provider,
        provider_config=provider_config,
        rag_service=None,
        serper_api_key="test-key",
        perplexity_api_key="test-key",
        card_repository=mock_repositories["card"],
    )


@pytest.fixture
def sample_cards():
    """Create sample cards."""
    return [
        Card(
            id="card-1",
            tenant_id="test@example.com",
            card_type=CardType.PRODUCT,
            title="Test Product",
            content=CardContent(product_name="Test Product"),
            is_active=True,
            version=1,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        ),
    ]


@pytest.fixture
def content_request():
    """Create content generation request."""
    return ContentGenerationRequest(
        topic="Test Topic",
        content_type=ContentType.ARTICLE,
        content_format=ContentFormat.MARKDOWN,
        client_profile="test@example.com",
        workflow_type="enhanced_article",
    )


@pytest.mark.asyncio
async def test_build_dynamic_context_with_cards(
    use_case, mock_repositories, content_request, sample_cards
):
    """Test that cards are added to dynamic context."""
    # Mock card repository to return cards
    mock_repositories["card"].get_all_by_tenant.return_value = sample_cards

    # Mock other dependencies
    mock_repositories["workflow"].get_by_type.return_value = []
    mock_repositories["agent"].get_all.return_value = []

    # Build context
    context = await use_case._build_dynamic_context(content_request)

    # Verify cards_context is in context
    assert "cards_context" in context
    assert isinstance(context["cards_context"], str)
    assert len(context["cards_context"]) > 0


@pytest.mark.asyncio
async def test_build_dynamic_context_without_card_repository(
    mock_repositories, mock_llm_provider, provider_config, content_request
):
    """Test context building when card repository is None."""
    use_case = GenerateContentUseCase(
        content_repository=mock_repositories["content"],
        workflow_repository=mock_repositories["workflow"],
        agent_repository=mock_repositories["agent"],
        llm_provider=mock_llm_provider,
        provider_config=provider_config,
        rag_service=None,
        serper_api_key="test-key",
        perplexity_api_key="test-key",
        card_repository=None,  # No card repository
    )

    mock_repositories["workflow"].get_by_type.return_value = []
    mock_repositories["agent"].get_all.return_value = []

    context = await use_case._build_dynamic_context(content_request)

    # Should not have cards_context
    assert "cards_context" not in context


@pytest.mark.asyncio
async def test_build_dynamic_context_card_retrieval_failure(
    use_case, mock_repositories, content_request
):
    """Test that card retrieval failure doesn't block context building."""
    # Mock card repository to raise exception
    mock_repositories["card"].get_all_by_tenant.side_effect = Exception(
        "Database error"
    )

    mock_repositories["workflow"].get_by_type.return_value = []
    mock_repositories["agent"].get_all.return_value = []

    # Should not raise exception
    context = await use_case._build_dynamic_context(content_request)

    # Context should be built without cards
    assert "cards_context" not in context or context.get("cards_context") is None


@pytest.mark.asyncio
async def test_build_dynamic_context_no_cards_found(
    use_case, mock_repositories, content_request
):
    """Test context building when no cards are found."""
    # Mock card repository to return empty list
    mock_repositories["card"].get_all_by_tenant.return_value = []

    mock_repositories["workflow"].get_by_type.return_value = []
    mock_repositories["agent"].get_all.return_value = []

    context = await use_case._build_dynamic_context(content_request)

    # Should not have cards_context or it should be empty
    assert "cards_context" not in context or context.get("cards_context") == ""


@pytest.mark.asyncio
async def test_build_dynamic_context_uses_client_profile_as_tenant(
    use_case, mock_repositories, content_request, sample_cards
):
    """Test that client_profile is used as tenant_id for card retrieval."""
    mock_repositories["card"].get_all_by_tenant.return_value = sample_cards
    mock_repositories["workflow"].get_by_type.return_value = []
    mock_repositories["agent"].get_all.return_value = []

    await use_case._build_dynamic_context(content_request)

    # Verify get_all_by_tenant was called with client_profile
    mock_repositories["card"].get_all_by_tenant.assert_called_with(
        "test@example.com"
    )


@pytest.mark.asyncio
async def test_build_dynamic_context_multiple_cards(
    use_case, mock_repositories, content_request
):
    """Test context building with multiple cards."""
    cards = [
        Card(
            id=f"card-{i}",
            tenant_id="test@example.com",
            card_type=CardType(["product", "persona", "campaign", "topic"][i % 4]),
            title=f"Card {i}",
            content=CardContent(name=f"Card {i}"),
            is_active=True,
            version=1,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        for i in range(4)
    ]

    mock_repositories["card"].get_all_by_tenant.return_value = cards
    mock_repositories["workflow"].get_by_type.return_value = []
    mock_repositories["agent"].get_all.return_value = []

    context = await use_case._build_dynamic_context(content_request)

    assert "cards_context" in context
    # All cards should be in context
    for card in cards:
        assert card.title in context["cards_context"]

