"""Integration tests for CGS → Card retrieval flow."""

import pytest
from unittest.mock import AsyncMock, MagicMock
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
    """Create use case instance."""
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
    """Create sample cards for RAG context."""
    return [
        Card(
            id="card-1",
            tenant_id="test@example.com",
            card_type=CardType.PRODUCT,
            title="Test Product",
            content=CardContent(
                product_name="Test Product",
                description="A test product for tech professionals",
                key_features=["Feature 1", "Feature 2"],
            ),
            is_active=True,
            version=1,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        ),
        Card(
            id="card-2",
            tenant_id="test@example.com",
            card_type=CardType.PERSONA,
            title="Tech Professional",
            content=CardContent(
                persona_name="Tech Professional",
                description="A tech professional persona",
                demographics={"age": "25-35", "role": "Developer"},
            ),
            is_active=True,
            version=1,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        ),
        Card(
            id="card-3",
            tenant_id="test@example.com",
            card_type=CardType.CAMPAIGN,
            title="Q1 Campaign",
            content=CardContent(
                campaign_name="Q1 Campaign",
                description="Q1 marketing campaign",
                objectives=["Increase awareness", "Drive engagement"],
            ),
            is_active=True,
            version=1,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        ),
        Card(
            id="card-4",
            tenant_id="test@example.com",
            card_type=CardType.TOPIC,
            title="AI & Machine Learning",
            content=CardContent(
                topic_name="AI & Machine Learning",
                description="Topics related to AI and ML",
                subtopics=["Deep Learning", "NLP", "Computer Vision"],
            ),
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
        topic="AI in Product Development",
        content_type=ContentType.ARTICLE,
        content_format=ContentFormat.MARKDOWN,
        client_profile="test@example.com",
        workflow_type="enhanced_article",
    )


@pytest.mark.asyncio
async def test_cgs_retrieves_cards_for_context(
    use_case, mock_repositories, content_request, sample_cards
):
    """Test that CGS retrieves cards for RAG context."""
    mock_repositories["card"].get_all_by_tenant.return_value = sample_cards
    mock_repositories["workflow"].get_by_type.return_value = []
    mock_repositories["agent"].get_all.return_value = []

    context = await use_case._build_dynamic_context(content_request)

    # Verify cards were retrieved
    mock_repositories["card"].get_all_by_tenant.assert_called_with("test@example.com")

    # Verify cards are in context
    assert "cards_context" in context
    assert len(context["cards_context"]) > 0


@pytest.mark.asyncio
async def test_cgs_card_context_includes_all_card_types(
    use_case, mock_repositories, content_request, sample_cards
):
    """Test that card context includes all card types."""
    mock_repositories["card"].get_all_by_tenant.return_value = sample_cards
    mock_repositories["workflow"].get_by_type.return_value = []
    mock_repositories["agent"].get_all.return_value = []

    context = await use_case._build_dynamic_context(content_request)

    cards_context = context["cards_context"]

    # Verify all card types are in context
    assert "Test Product" in cards_context
    assert "Tech Professional" in cards_context
    assert "Q1 Campaign" in cards_context
    assert "AI & Machine Learning" in cards_context


@pytest.mark.asyncio
async def test_cgs_card_context_formatted_for_llm(
    use_case, mock_repositories, content_request, sample_cards
):
    """Test that card context is properly formatted for LLM."""
    mock_repositories["card"].get_all_by_tenant.return_value = sample_cards
    mock_repositories["workflow"].get_by_type.return_value = []
    mock_repositories["agent"].get_all.return_value = []

    context = await use_case._build_dynamic_context(content_request)

    cards_context = context["cards_context"]

    # Verify formatting
    assert isinstance(cards_context, str)
    assert len(cards_context) > 100  # Should have substantial content
    # Should have card information
    assert "product" in cards_context.lower() or "Product" in cards_context
    assert "persona" in cards_context.lower() or "Persona" in cards_context


@pytest.mark.asyncio
async def test_cgs_no_cards_available(
    use_case, mock_repositories, content_request
):
    """Test CGS behavior when no cards are available."""
    mock_repositories["card"].get_all_by_tenant.return_value = []
    mock_repositories["workflow"].get_by_type.return_value = []
    mock_repositories["agent"].get_all.return_value = []

    context = await use_case._build_dynamic_context(content_request)

    # Should not have cards_context or it should be empty
    assert "cards_context" not in context or context.get("cards_context") == ""


@pytest.mark.asyncio
async def test_cgs_card_retrieval_uses_tenant_id(
    use_case, mock_repositories, content_request, sample_cards
):
    """Test that card retrieval uses correct tenant_id."""
    mock_repositories["card"].get_all_by_tenant.return_value = sample_cards
    mock_repositories["workflow"].get_by_type.return_value = []
    mock_repositories["agent"].get_all.return_value = []

    await use_case._build_dynamic_context(content_request)

    # Verify tenant_id is from client_profile
    mock_repositories["card"].get_all_by_tenant.assert_called_with("test@example.com")


@pytest.mark.asyncio
async def test_cgs_card_context_non_blocking_on_error(
    use_case, mock_repositories, content_request
):
    """Test that card retrieval failure doesn't block content generation."""
    # Mock card retrieval to fail
    mock_repositories["card"].get_all_by_tenant.side_effect = Exception(
        "Database connection error"
    )
    mock_repositories["workflow"].get_by_type.return_value = []
    mock_repositories["agent"].get_all.return_value = []

    # Should not raise exception
    context = await use_case._build_dynamic_context(content_request)

    # Context should still be built
    assert context is not None
    # But cards_context should not be present
    assert "cards_context" not in context or context.get("cards_context") is None


@pytest.mark.asyncio
async def test_cgs_only_active_cards_in_context(
    use_case, mock_repositories, content_request
):
    """Test that only active cards are included in context."""
    active_card = Card(
        id="card-1",
        tenant_id="test@example.com",
        card_type=CardType.PRODUCT,
        title="Active Product",
        content=CardContent(product_name="Active Product"),
        is_active=True,
        version=1,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    # Repository should only return active cards
    mock_repositories["card"].get_all_by_tenant.return_value = [active_card]
    mock_repositories["workflow"].get_by_type.return_value = []
    mock_repositories["agent"].get_all.return_value = []

    context = await use_case._build_dynamic_context(content_request)

    cards_context = context["cards_context"]
    assert "Active Product" in cards_context

