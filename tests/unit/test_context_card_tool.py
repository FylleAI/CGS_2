"""
Unit tests for ContextCardTool.

Tests:
- Cache eviction (TTL expired, LRU)
- Batch retrieval with partial results
- Usage tracking with dedup
- Metrics (cache hit rate)
"""

import asyncio
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4, UUID

from core.infrastructure.tools.context_card_tool import (
    ContextCardTool,
    CacheEntry,
    CACHE_TTL_BY_TYPE,
)
from fylle_cards_client import CardsClient, CardType, ContextCard
from fylle_cards_client.models import CardListResponse


@pytest.fixture
def mock_cards_client():
    """Create mock Cards API client."""
    client = Mock(spec=CardsClient)
    return client


@pytest.fixture
def context_card_tool(mock_cards_client):
    """Create ContextCardTool with mock client."""
    return ContextCardTool(
        cards_client=mock_cards_client,
        max_cache_size=100,
    )


@pytest.fixture
def sample_card():
    """Create sample context card."""
    return ContextCard(
        card_id=uuid4(),
        tenant_id=uuid4(),
        card_type=CardType.COMPANY,
        title="Test Company",
        content={"name": "Acme Corp", "industry": "Technology"},
        tags=[],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        created_by="test-user",
    )


class TestCacheEntry:
    """Test CacheEntry class."""
    
    def test_cache_entry_not_expired(self, sample_card):
        """Test cache entry is not expired within TTL."""
        entry = CacheEntry(sample_card, ttl_seconds=3600)
        assert not entry.is_expired()
    
    def test_cache_entry_expired(self, sample_card):
        """Test cache entry is expired after TTL."""
        entry = CacheEntry(sample_card, ttl_seconds=0)
        # Manually set expiration to past
        entry.expires_at = datetime.utcnow() - timedelta(seconds=1)
        assert entry.is_expired()
    
    def test_cache_entry_hit_count(self, sample_card):
        """Test cache entry hit count tracking."""
        entry = CacheEntry(sample_card, ttl_seconds=3600)
        assert entry.hit_count == 0
        
        entry.record_hit()
        assert entry.hit_count == 1
        
        entry.record_hit()
        assert entry.hit_count == 2


class TestContextCardTool:
    """Test ContextCardTool class."""
    
    def test_cache_hit_rate_empty(self, context_card_tool):
        """Test cache hit rate with no retrievals."""
        assert context_card_tool.get_cache_hit_rate() == 0.0
    
    def test_cache_hit_rate_calculation(self, context_card_tool):
        """Test cache hit rate calculation."""
        context_card_tool.cache_hits = 75
        context_card_tool.cache_misses = 25
        assert context_card_tool.get_cache_hit_rate() == 0.75
    
    def test_get_from_cache_miss(self, context_card_tool):
        """Test cache miss."""
        tenant_id = "tenant-123"
        card_id = uuid4()
        
        result = context_card_tool._get_from_cache(tenant_id, card_id)
        assert result is None
    
    def test_get_from_cache_hit(self, context_card_tool, sample_card):
        """Test cache hit."""
        tenant_id = "tenant-123"
        
        # Put in cache
        context_card_tool._put_in_cache(tenant_id, sample_card)
        
        # Get from cache
        result = context_card_tool._get_from_cache(tenant_id, sample_card.card_id)
        assert result is not None
        assert result.card_id == sample_card.card_id
        assert context_card_tool.cache_hits == 1
    
    def test_cache_eviction_expired(self, context_card_tool, sample_card):
        """Test cache eviction of expired entries."""
        tenant_id = "tenant-123"
        
        # Put in cache with 0 TTL
        key = (tenant_id, sample_card.card_id)
        context_card_tool.cache[key] = CacheEntry(sample_card, ttl_seconds=0)
        context_card_tool.cache[key].expires_at = datetime.utcnow() - timedelta(seconds=1)

        # Try to get (should evict)
        result = context_card_tool._get_from_cache(tenant_id, sample_card.card_id)
        assert result is None
        assert key not in context_card_tool.cache
    
    def test_cache_eviction_lru(self, context_card_tool):
        """Test LRU eviction when cache is full."""
        tenant_id = "tenant-123"
        context_card_tool.max_cache_size = 2
        
        # Add 3 cards (should evict first one)
        cards = [
            ContextCard(
                card_id=uuid4(),
                tenant_id=uuid4(),
                card_type=CardType.COMPANY,
                title=f"Card {i}",
                content={},
                tags=[],
                created_at=datetime.now(),
                updated_at=datetime.now(),
                created_by="test-user",
            )
            for i in range(3)
        ]

        for card in cards:
            context_card_tool._put_in_cache(tenant_id, card)

        # First card should be evicted
        assert len(context_card_tool.cache) == 2
        assert (tenant_id, cards[0].card_id) not in context_card_tool.cache
        assert (tenant_id, cards[1].card_id) in context_card_tool.cache
        assert (tenant_id, cards[2].card_id) in context_card_tool.cache
    
    @pytest.mark.asyncio
    async def test_retrieve_cards_all_cached(self, context_card_tool, sample_card):
        """Test retrieve cards when all are in cache."""
        tenant_id = "tenant-123"
        workflow_id = uuid4()
        
        # Put in cache
        context_card_tool._put_in_cache(tenant_id, sample_card)
        
        # Retrieve
        context = await context_card_tool.retrieve_cards(
            tenant_id=tenant_id,
            card_ids=[sample_card.card_id],
            workflow_id=workflow_id,
            workflow_type="premium_newsletter",
        )
        
        # Should not call API
        context_card_tool.cards_client.retrieve_cards.assert_not_called()
        
        # Should have cache hit
        assert context_card_tool.cache_hits == 1
        assert context_card_tool.cache_misses == 0
        assert context_card_tool.get_cache_hit_rate() == 1.0
    
    @pytest.mark.asyncio
    async def test_retrieve_cards_partial_cached(self, context_card_tool, sample_card):
        """Test retrieve cards with partial cache hit."""
        tenant_id = "tenant-123"
        workflow_id = uuid4()
        
        # Create second card
        card2 = ContextCard(
            card_id=uuid4(),
            tenant_id=uuid4(),
            card_type=CardType.VOICE,
            title="Voice Card",
            content={},
            tags=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by="test-user",
        )
        
        # Put first card in cache
        context_card_tool._put_in_cache(tenant_id, sample_card)
        
        # Mock API response for second card
        context_card_tool.cards_client.retrieve_cards.return_value = CardListResponse(
            cards=[card2],
            total=1,
        )
        
        # Retrieve both cards
        context = await context_card_tool.retrieve_cards(
            tenant_id=tenant_id,
            card_ids=[sample_card.card_id, card2.card_id],
            workflow_id=workflow_id,
            workflow_type="premium_newsletter",
        )

        # Should call API for missing card
        context_card_tool.cards_client.retrieve_cards.assert_called_once_with([card2.card_id])
        
        # Should have 1 hit, 1 miss
        assert context_card_tool.cache_hits == 1
        assert context_card_tool.cache_misses == 1
        assert context_card_tool.get_cache_hit_rate() == 0.5
    
    def test_format_context(self, context_card_tool):
        """Test context formatting by card type."""
        cards = [
            ContextCard(
                card_id=uuid4(),
                tenant_id=uuid4(),
                card_type=CardType.COMPANY,
                title="Company Card",
                content={"name": "Acme"},
                tags=[],
                created_at=datetime.now(),
                updated_at=datetime.now(),
                created_by="test-user",
            ),
            ContextCard(
                card_id=uuid4(),
                tenant_id=uuid4(),
                card_type=CardType.VOICE,
                title="Voice Card",
                content={"tone": "professional"},
                tags=[],
                created_at=datetime.now(),
                updated_at=datetime.now(),
                created_by="test-user",
            ),
        ]
        
        context = context_card_tool._format_context(cards)
        
        assert "company" in context
        assert "voice" in context
        assert len(context["company"]) == 1
        assert len(context["voice"]) == 1
        assert context["company"][0]["title"] == "Company Card"
        assert context["voice"][0]["title"] == "Voice Card"

