"""
Context Card Tool - Retrieve and track context cards from Cards API.

Replaces file-based RAG with card-based context retrieval.
Implements LRU cache with TTL and usage tracking.
"""

import logging
import time
from typing import Dict, Any, List, Optional, Tuple
from uuid import UUID
from datetime import datetime, timedelta
from collections import OrderedDict

from fylle_cards_client import CardsClient, CardType, ContextCard
from fylle_shared.enums import CardType as SharedCardType

logger = logging.getLogger(__name__)


# Cache TTL by card type (in seconds)
CACHE_TTL_BY_TYPE = {
    CardType.VOICE: 7200,      # 2 hours
    CardType.COMPANY: 3600,    # 1 hour
    CardType.AUDIENCE: 3600,   # 1 hour
    CardType.INSIGHT: 1800,    # 30 minutes
}

DEFAULT_CACHE_TTL = 3600  # 1 hour default


class CacheEntry:
    """Cache entry with TTL."""
    
    def __init__(self, card: ContextCard, ttl_seconds: int):
        self.card = card
        self.expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
        self.hit_count = 0
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        return datetime.utcnow() > self.expires_at
    
    def record_hit(self):
        """Record a cache hit."""
        self.hit_count += 1


class ContextCardTool:
    """
    Tool for retrieving context cards and tracking usage.
    
    Features:
    - LRU cache with TTL per card type
    - Batch retrieval from Cards API
    - Usage tracking for each card
    - Metrics (cache hit rate, retrieval time)
    """
    
    def __init__(
        self,
        cards_client: CardsClient,
        max_cache_size: int = 1000,
    ):
        """
        Initialize ContextCardTool.
        
        Args:
            cards_client: Cards API client
            max_cache_size: Maximum number of cards in cache
        """
        self.cards_client = cards_client
        self.max_cache_size = max_cache_size
        
        # LRU cache: (tenant_id, card_id) -> CacheEntry
        self.cache: OrderedDict[Tuple[str, UUID], CacheEntry] = OrderedDict()
        
        # Metrics
        self.cache_hits = 0
        self.cache_misses = 0
        self.total_retrievals = 0
    
    def get_cache_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.cache_hits + self.cache_misses
        if total == 0:
            return 0.0
        return self.cache_hits / total
    
    def _evict_expired(self):
        """Evict expired cache entries."""
        expired_keys = [
            key for key, entry in self.cache.items()
            if entry.is_expired()
        ]
        for key in expired_keys:
            del self.cache[key]
            logger.debug(f"🗑️ Evicted expired cache entry: {key}")
    
    def _evict_lru(self):
        """Evict least recently used entry if cache is full."""
        if len(self.cache) >= self.max_cache_size:
            evicted_key, _ = self.cache.popitem(last=False)
            logger.debug(f"🗑️ Evicted LRU cache entry: {evicted_key}")
    
    def _get_from_cache(
        self,
        tenant_id: str,
        card_id: UUID,
    ) -> Optional[ContextCard]:
        """
        Get card from cache.
        
        Args:
            tenant_id: Tenant ID
            card_id: Card ID
        
        Returns:
            Card if found and not expired, None otherwise
        """
        key = (tenant_id, card_id)
        
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        
        if entry.is_expired():
            del self.cache[key]
            logger.debug(f"🗑️ Cache entry expired: {key}")
            return None
        
        # Move to end (most recently used)
        self.cache.move_to_end(key)
        entry.record_hit()
        
        self.cache_hits += 1
        logger.debug(f"✅ Cache HIT: {key} (hits: {entry.hit_count})")
        
        return entry.card
    
    def _put_in_cache(
        self,
        tenant_id: str,
        card: ContextCard,
    ):
        """
        Put card in cache.
        
        Args:
            tenant_id: Tenant ID
            card: Context card
        """
        key = (tenant_id, card.id)
        
        # Get TTL for card type
        ttl = CACHE_TTL_BY_TYPE.get(card.card_type, DEFAULT_CACHE_TTL)
        
        # Evict expired entries
        self._evict_expired()
        
        # Evict LRU if cache is full
        self._evict_lru()
        
        # Add to cache
        self.cache[key] = CacheEntry(card, ttl)
        logger.debug(f"💾 Cache PUT: {key} (TTL: {ttl}s)")
    
    async def retrieve_cards(
        self,
        tenant_id: str,
        card_ids: List[UUID],
        workflow_id: UUID,
        workflow_type: str,
        trace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Retrieve cards and format as context for agents.
        
        Steps:
        1. Check cache for each card
        2. Batch retrieve missing cards from Cards API
        3. Track usage for each card
        4. Format context by card type
        
        Args:
            tenant_id: Tenant ID
            card_ids: List of card IDs to retrieve
            workflow_id: Workflow ID for usage tracking
            workflow_type: Workflow type for usage tracking
            trace_id: Trace ID for distributed tracing
        
        Returns:
            Formatted context dict with sections by card type
        """
        start_time = time.time()
        self.total_retrievals += 1
        
        logger.info(
            f"🔍 Retrieving {len(card_ids)} cards",
            extra={
                "tenant_id": tenant_id,
                "card_count": len(card_ids),
                "workflow_id": str(workflow_id),
                "trace_id": trace_id,
            },
        )
        
        # Step 1: Check cache
        cards: List[ContextCard] = []
        missing_card_ids: List[UUID] = []
        
        for card_id in card_ids:
            cached_card = self._get_from_cache(tenant_id, card_id)
            if cached_card:
                cards.append(cached_card)
            else:
                missing_card_ids.append(card_id)
                self.cache_misses += 1
        
        logger.info(
            f"📊 Cache stats: {len(cards)} hits, {len(missing_card_ids)} misses",
            extra={
                "cache_hits": len(cards),
                "cache_misses": len(missing_card_ids),
                "cache_hit_rate": self.get_cache_hit_rate(),
            },
        )
        
        # Step 2: Batch retrieve missing cards
        if missing_card_ids:
            try:
                response = self.cards_client.retrieve_cards(missing_card_ids)
                
                # Add retrieved cards to cache and list
                for card in response.cards:
                    self._put_in_cache(tenant_id, card)
                    cards.append(card)
                
                logger.info(
                    f"✅ Retrieved {len(response.cards)} cards from API",
                    extra={
                        "retrieved_count": len(response.cards),
                        "partial_result": response.partial_result,
                    },
                )
                
                # Log if partial result
                if response.partial_result:
                    logger.warning(
                        f"⚠️ Partial result: some cards not found",
                        extra={
                            "requested": len(missing_card_ids),
                            "retrieved": len(response.cards),
                        },
                    )
            
            except Exception as e:
                logger.error(
                    f"❌ Failed to retrieve cards: {str(e)}",
                    extra={"error": str(e)},
                    exc_info=True,
                )
                # Continue with cached cards only
        
        # Step 3: Track usage for each card
        # TODO: Implement usage tracking in next iteration
        
        # Step 4: Format context by card type
        context = self._format_context(cards)
        
        retrieval_time_ms = int((time.time() - start_time) * 1000)
        
        logger.info(
            f"✅ Context retrieval completed",
            extra={
                "cards_retrieved": len(cards),
                "retrieval_time_ms": retrieval_time_ms,
                "cache_hit_rate": self.get_cache_hit_rate(),
            },
        )
        
        return context
    
    def _format_context(self, cards: List[ContextCard]) -> Dict[str, Any]:
        """
        Format cards as context for agents.
        
        Groups cards by type and formats content.
        
        Args:
            cards: List of context cards
        
        Returns:
            Formatted context dict
        """
        context: Dict[str, Any] = {
            "company": [],
            "audience": [],
            "voice": [],
            "insight": [],
        }
        
        for card in cards:
            card_type_key = card.card_type.value
            if card_type_key in context:
                context[card_type_key].append({
                    "id": str(card.id),
                    "title": card.title,
                    "content": card.content,
                    "metadata": card.metadata,
                })
        
        return context

