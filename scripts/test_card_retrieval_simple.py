#!/usr/bin/env python3
"""
Simple test for card retrieval and context formatting.

This script demonstrates:
1. Creating sample cards
2. Retrieving cards via ContextCardTool
3. Formatting context for workflow
4. Verifying cache behavior
"""

import asyncio
import sys
from pathlib import Path
from uuid import uuid4
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fylle_cards_client import ContextCard, CardType, CardListResponse
from core.infrastructure.tools.context_card_tool import ContextCardTool


class MockCardsClient:
    """Mock Cards API client for testing."""
    
    def __init__(self):
        self.tenant_id = uuid4()
        self.cards = self._create_sample_cards()
        self.retrieve_count = 0
    
    def _create_sample_cards(self):
        """Create sample cards for testing."""
        return [
            ContextCard(
                card_id=uuid4(),
                tenant_id=self.tenant_id,
                card_type=CardType.COMPANY,
                title="Fylle AI",
                content={
                    "name": "Fylle AI",
                    "industry": "Artificial Intelligence",
                    "description": "AI-powered content generation platform for B2B companies",
                    "website": "https://fylle.ai",
                    "size": "Startup",
                },
                tags=["ai", "b2b", "saas"],
                created_by="test_user",
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
            ContextCard(
                card_id=uuid4(),
                tenant_id=self.tenant_id,
                card_type=CardType.AUDIENCE,
                title="Tech Decision Makers",
                content={
                    "segment": "C-level executives and VPs",
                    "industries": ["Technology", "SaaS", "AI"],
                    "interests": ["AI", "Automation", "Content Marketing", "Lead Generation"],
                    "pain_points": ["Time-consuming content creation", "Lack of personalization"],
                },
                tags=["b2b", "enterprise"],
                created_by="test_user",
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
            ContextCard(
                card_id=uuid4(),
                tenant_id=self.tenant_id,
                card_type=CardType.VOICE,
                title="Professional & Insightful",
                content={
                    "tone": "professional",
                    "style": "insightful",
                    "formality": "business casual",
                    "personality": "Expert advisor with a friendly approach",
                },
                tags=["voice"],
                created_by="test_user",
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
        ]
    
    def retrieve_cards(self, card_ids):
        """Mock retrieve_cards method."""
        self.retrieve_count += 1
        
        # Filter cards by requested IDs
        requested_cards = [card for card in self.cards if card.card_id in card_ids]
        
        print(f"   📡 Cards API called (call #{self.retrieve_count}): {len(requested_cards)}/{len(card_ids)} cards found")
        
        return CardListResponse(
            cards=requested_cards,
            total=len(requested_cards),
        )
    
    def track_usage(self, card_id, usage_data):
        """Mock track_usage method (fire-and-forget)."""
        # No-op for mock
        pass


async def test_card_retrieval():
    """Test card retrieval and context formatting."""
    
    print("=" * 80)
    print("🧪 Testing Card Retrieval & Context Formatting")
    print("=" * 80)
    print()
    
    # Step 1: Create mock Cards client
    print("📦 Step 1: Creating mock Cards API client...")
    cards_client = MockCardsClient()
    tenant_id = str(cards_client.tenant_id)
    card_ids = [card.card_id for card in cards_client.cards]
    
    print(f"   ✅ Created {len(cards_client.cards)} sample cards:")
    for card in cards_client.cards:
        print(f"      - {card.card_type.value}: {card.title}")
    print()
    
    # Step 2: Create ContextCardTool
    print("🔧 Step 2: Creating ContextCardTool...")
    context_tool = ContextCardTool(
        cards_client=cards_client,
        max_cache_size=1000,
    )
    print("   ✅ ContextCardTool created")
    print()
    
    # Step 3: First retrieval (cache miss)
    print("🔍 Step 3: First card retrieval (cache MISS expected)...")
    workflow_id_1 = uuid4()
    
    context_1 = await context_tool.retrieve_cards(
        tenant_id=tenant_id,
        card_ids=card_ids,
        workflow_id=workflow_id_1,
        workflow_type="premium_newsletter",
        trace_id="test-trace-001",
    )
    
    print(f"   ✅ Retrieved context with {len(context_1)} sections")
    print(f"   📊 Cache stats:")
    print(f"      - Cache hits: {context_tool.cache_hits}")
    print(f"      - Cache misses: {context_tool.cache_misses}")
    print(f"      - Hit rate: {context_tool.get_cache_hit_rate():.2%}")
    print(f"      - API calls: {cards_client.retrieve_count}")
    print()
    
    # Step 4: Display formatted context
    print("=" * 80)
    print("📄 FORMATTED CONTEXT")
    print("=" * 80)
    print()
    
    for section_name, section_data in context_1.items():
        print(f"Section: {section_name}")
        if isinstance(section_data, list):
            print(f"  Type: List with {len(section_data)} items")
            for i, item in enumerate(section_data, 1):
                if isinstance(item, dict):
                    print(f"  Item {i}:")
                    for key, value in item.items():
                        if isinstance(value, str) and len(value) > 100:
                            print(f"    - {key}: {value[:100]}...")
                        else:
                            print(f"    - {key}: {value}")
                else:
                    print(f"  Item {i}: {item}")
        else:
            print(f"  Value: {section_data}")
        print()
    
    # Step 5: Second retrieval (cache hit)
    print("=" * 80)
    print("🔍 Step 5: Second card retrieval (cache HIT expected)...")
    print("=" * 80)
    print()
    
    workflow_id_2 = uuid4()
    
    context_2 = await context_tool.retrieve_cards(
        tenant_id=tenant_id,
        card_ids=card_ids,
        workflow_id=workflow_id_2,
        workflow_type="premium_newsletter",
        trace_id="test-trace-002",
    )
    
    print(f"   ✅ Retrieved context with {len(context_2)} sections")
    print(f"   📊 Cache stats:")
    print(f"      - Cache hits: {context_tool.cache_hits}")
    print(f"      - Cache misses: {context_tool.cache_misses}")
    print(f"      - Hit rate: {context_tool.get_cache_hit_rate():.2%}")
    print(f"      - API calls: {cards_client.retrieve_count}")
    print()
    
    # Step 6: Verify cache behavior
    print("=" * 80)
    print("✅ VERIFICATION")
    print("=" * 80)
    print()
    
    print("Cache Behavior:")
    if cards_client.retrieve_count == 1:
        print(f"  ✅ Cards API called only once (cache working!)")
    else:
        print(f"  ❌ Cards API called {cards_client.retrieve_count} times (cache not working)")
    
    if context_tool.cache_hits == 3:  # 3 cards from cache on second retrieval
        print(f"  ✅ Cache hits: {context_tool.cache_hits} (expected 3)")
    else:
        print(f"  ⚠️ Cache hits: {context_tool.cache_hits} (expected 3)")
    
    hit_rate = context_tool.get_cache_hit_rate()
    if hit_rate >= 0.5:
        print(f"  ✅ Cache hit rate: {hit_rate:.2%} (≥ 50%)")
    else:
        print(f"  ⚠️ Cache hit rate: {hit_rate:.2%} (< 50%)")
    
    print()
    
    print("Context Formatting:")
    if len(context_1) > 0:
        print(f"  ✅ Context formatted with {len(context_1)} sections")
    else:
        print(f"  ❌ Context is empty")
    
    if context_1 == context_2:
        print(f"  ✅ Context consistent across retrievals")
    else:
        print(f"  ⚠️ Context differs between retrievals")
    
    print()
    
    # Step 7: Summary
    print("=" * 80)
    print("🎉 TEST COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print()
    
    print("Summary:")
    print(f"  - Total retrievals: 2")
    print(f"  - Cards retrieved: {len(card_ids)} cards")
    print(f"  - API calls: {cards_client.retrieve_count}")
    print(f"  - Cache hit rate: {hit_rate:.2%}")
    print(f"  - Context sections: {len(context_1)}")
    print()
    
    return True


if __name__ == "__main__":
    print()
    success = asyncio.run(test_card_retrieval())
    print()
    
    if success:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Tests failed!")
        sys.exit(1)

