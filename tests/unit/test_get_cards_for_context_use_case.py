"""Unit tests for GetCardsForContextUseCase."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from services.card_service.application.get_cards_for_context_use_case import (
    GetCardsForContextUseCase,
)
from services.card_service.domain.entities.card import Card, CardType, CardContent


@pytest.fixture
def mock_repository():
    """Create mock card repository."""
    return AsyncMock()


@pytest.fixture
def use_case(mock_repository):
    """Create use case instance."""
    return GetCardsForContextUseCase(mock_repository)


@pytest.fixture
def sample_cards():
    """Create sample cards for testing."""
    return [
        Card(
            id="card-1",
            tenant_id="test@example.com",
            card_type=CardType.PRODUCT,
            title="Test Product",
            content=CardContent(
                product_name="Test Product",
                description="A test product",
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
            title="Test Persona",
            content=CardContent(
                persona_name="Test Persona",
                description="A test persona",
                demographics={"age": "25-35", "role": "Developer"},
            ),
            is_active=True,
            version=1,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        ),
    ]


@pytest.mark.asyncio
async def test_get_all_cards_success(use_case, mock_repository, sample_cards):
    """Test successful retrieval of all cards."""
    mock_repository.get_all_by_tenant.return_value = sample_cards

    result = await use_case.get_all(tenant_id="test@example.com")

    assert len(result) == 2
    assert result[0].card_type == CardType.PRODUCT
    assert result[1].card_type == CardType.PERSONA
    mock_repository.get_all_by_tenant.assert_called_once_with("test@example.com")


@pytest.mark.asyncio
async def test_get_all_cards_empty(use_case, mock_repository):
    """Test retrieval when no cards exist."""
    mock_repository.get_all_by_tenant.return_value = []

    result = await use_case.get_all(tenant_id="test@example.com")

    assert result == []
    mock_repository.get_all_by_tenant.assert_called_once()


@pytest.mark.asyncio
async def test_get_as_rag_context_success(use_case, mock_repository, sample_cards):
    """Test successful RAG context generation."""
    mock_repository.get_all_by_tenant.return_value = sample_cards

    result = await use_case.get_as_rag_context(tenant_id="test@example.com")

    assert isinstance(result, str)
    assert "Test Product" in result
    assert "Test Persona" in result
    assert "PRODUCT CARD" in result or "product" in result.lower()
    assert "PERSONA CARD" in result or "persona" in result.lower()


@pytest.mark.asyncio
async def test_get_as_rag_context_empty(use_case, mock_repository):
    """Test RAG context generation with no cards."""
    mock_repository.get_all_by_tenant.return_value = []

    result = await use_case.get_as_rag_context(tenant_id="test@example.com")

    assert result == ""


@pytest.mark.asyncio
async def test_get_by_type_success(use_case, mock_repository, sample_cards):
    """Test retrieval by card type."""
    product_cards = [sample_cards[0]]
    mock_repository.get_by_type.return_value = product_cards

    result = await use_case.get_by_type(
        tenant_id="test@example.com",
        card_type=CardType.PRODUCT,
    )

    assert len(result) == 1
    assert result[0].card_type == CardType.PRODUCT
    mock_repository.get_by_type.assert_called_once()


@pytest.mark.asyncio
async def test_get_active_cards_only(use_case, mock_repository, sample_cards):
    """Test that only active cards are retrieved."""
    # Mark one card as inactive
    sample_cards[1].is_active = False
    mock_repository.get_all_by_tenant.return_value = [sample_cards[0]]

    result = await use_case.get_all(tenant_id="test@example.com")

    assert len(result) == 1
    assert result[0].is_active is True


@pytest.mark.asyncio
async def test_get_as_rag_context_formatting(use_case, mock_repository, sample_cards):
    """Test RAG context formatting."""
    mock_repository.get_all_by_tenant.return_value = sample_cards

    result = await use_case.get_as_rag_context(tenant_id="test@example.com")

    # Check that context is properly formatted
    lines = result.split("\n")
    assert len(lines) > 0
    # Should contain card information
    assert any("Test Product" in line for line in lines)
    assert any("Test Persona" in line for line in lines)


@pytest.mark.asyncio
async def test_get_as_rag_context_with_relationships(use_case, mock_repository):
    """Test RAG context includes relationship information."""
    cards = [
        Card(
            id="card-1",
            tenant_id="test@example.com",
            card_type=CardType.PRODUCT,
            title="Product",
            content=CardContent(product_name="Product"),
            is_active=True,
            version=1,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        ),
    ]
    mock_repository.get_all_by_tenant.return_value = cards

    result = await use_case.get_as_rag_context(tenant_id="test@example.com")

    assert isinstance(result, str)
    assert len(result) > 0

