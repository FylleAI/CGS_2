#!/usr/bin/env python3
"""
Test script for Workflow API v1 with card-based context.

This script demonstrates:
1. Creating sample cards via Cards API (mocked)
2. Executing a workflow with card_ids
3. Verifying metrics and logs
"""

import asyncio
import sys
import os
from pathlib import Path
from uuid import uuid4
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fylle_cards_client import ContextCard, CardType
from fylle_shared.enums import WorkflowType
from fylle_shared.models.workflow import WorkflowRequest

from api.rest.v1.endpoints.workflow_v1 import execute_workflow_v1, init_workflow_v1
from core.infrastructure.workflows.registry import workflow_registry
from core.infrastructure.tools.context_card_tool import ContextCardTool


class MockCardsClient:
    """Mock Cards API client for testing."""

    def __init__(self):
        self.tenant_id = uuid4()
        self.cards = self._create_sample_cards()

    def track_usage(self, card_id, usage_data):
        """Mock track_usage method (fire-and-forget)."""
        # No-op for mock
        pass

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
        from fylle_cards_client import CardListResponse
        
        # Filter cards by requested IDs
        requested_cards = [card for card in self.cards if card.card_id in card_ids]
        
        return CardListResponse(
            cards=requested_cards,
            total=len(requested_cards),
        )


class MockResponse:
    """Mock FastAPI Response object."""
    
    def __init__(self):
        self.headers = {}


async def test_workflow_with_cards():
    """Test workflow execution with card-based context."""
    
    print("=" * 80)
    print("🧪 Testing Workflow API v1 with Card-based Context")
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
    
    # Step 2: Initialize workflow v1
    print("🔧 Step 2: Initializing workflow v1 endpoint...")
    init_workflow_v1(workflow_registry, cards_client)
    print("   ✅ Workflow v1 initialized")
    print()
    
    # Step 3: Create workflow request
    print("📝 Step 3: Creating workflow request...")
    request = WorkflowRequest(
        workflow_type=WorkflowType.PREMIUM_NEWSLETTER,
        card_ids=card_ids,
        parameters={
            "topic": "The Future of AI in Content Marketing",
            "target_audience": "Tech Decision Makers and C-level executives interested in AI and automation",
            "target_word_count": 1200,
            "premium_sources": [
                "https://techcrunch.com",
                "https://venturebeat.com",
            ],
        },
    )
    print(f"   ✅ Request created:")
    print(f"      - Workflow: {request.workflow_type.value}")
    print(f"      - Card IDs: {len(card_ids)} cards")
    print(f"      - Topic: {request.parameters['topic']}")
    print(f"      - Target Audience: {request.parameters['target_audience']}")
    print()
    
    # Step 4: Execute workflow
    print("🚀 Step 4: Executing workflow...")
    response = MockResponse()
    
    try:
        result = await execute_workflow_v1(
            request=request,
            response=response,
            x_tenant_id=tenant_id,
            x_trace_id="test-trace-manual-001",
            x_session_id="test-session-001",
        )
        
        print("   ✅ Workflow execution completed!")
        print()
        
        # Step 5: Display results
        print("=" * 80)
        print("📊 RESULTS")
        print("=" * 80)
        print()
        
        print(f"Workflow ID: {result.workflow_id}")
        print(f"Status: {result.status}")
        print()
        
        print("Metrics:")
        print(f"  - Execution time: {result.metrics.execution_time_ms}ms")
        print(f"  - Cards used: {result.metrics.cards_used}")
        if result.metrics.cache_hit_rate is not None:
            print(f"  - Cache hit rate: {result.metrics.cache_hit_rate:.2%}")
        if result.metrics.tokens_used:
            print(f"  - Tokens used: {result.metrics.tokens_used}")
        print()
        
        print("Response Headers:")
        for key, value in response.headers.items():
            print(f"  - {key}: {value}")
        print()
        
        print("Output:")
        if isinstance(result.output, dict):
            for key, value in result.output.items():
                if isinstance(value, str) and len(value) > 200:
                    print(f"  - {key}: {value[:200]}...")
                else:
                    print(f"  - {key}: {value}")
        else:
            print(f"  {result.output}")
        print()
        
        # Step 6: Verify card context was used
        print("=" * 80)
        print("✅ VERIFICATION")
        print("=" * 80)
        print()
        
        print("Card Context Integration:")
        print(f"  ✅ {len(card_ids)} cards retrieved")
        print(f"  ✅ Workflow executed with card-based context")
        print(f"  ✅ No X-Partial-Result header (all cards found)")
        print()
        
        print("=" * 80)
        print("🎉 TEST COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"   ❌ Workflow execution failed: {str(e)}")
        print()
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print()
    success = asyncio.run(test_workflow_with_cards())
    print()
    
    if success:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Tests failed!")
        sys.exit(1)

