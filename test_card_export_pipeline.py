"""
Test for CardExportPipeline - Integration test with Card Service.

This test verifies that:
1. CardExportPipeline can export CompanySnapshot to Card Service
2. Card Service creates 4 atomic cards
3. CardExportPipeline returns CardSummary list
"""

import asyncio
import logging
from datetime import datetime
from uuid import uuid4

from onboarding.domain.models import (
    CompanySnapshot,
    CompanyInfo,
    AudienceInfo,
    VoiceInfo,
    InsightsInfo,
    ClarifyingQuestion,
    SourceMetadata,
)
from onboarding.infrastructure.card_service_client import CardServiceClient
from onboarding.application.card_export_pipeline import CardExportPipeline

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_card_export_pipeline():
    """Test CardExportPipeline with real Card Service."""
    
    print("\n" + "="*60)
    print("CARD EXPORT PIPELINE - INTEGRATION TEST")
    print("="*60)
    
    # Create Card Service client
    card_service_client = CardServiceClient(
        base_url="http://localhost:8001",
        timeout=30,
        retry_attempts=3,
    )
    
    # Create CardExportPipeline
    pipeline = CardExportPipeline(card_service_client=card_service_client)
    
    # Create test CompanySnapshot
    snapshot = CompanySnapshot(
        version="1.0",
        snapshot_id=uuid4(),
        generated_at=datetime.utcnow(),
        trace_id=str(uuid4()),
        company=CompanyInfo(
            name="TestCorp AI",
            description="AI solutions for enterprises",
            key_offerings=["AI Platform", "ML Services", "Data Analytics"],
            differentiators=["Real-time processing", "99.9% uptime"],
            website="https://testcorp.ai",
            industry="Technology",
            headquarters="San Francisco, CA",
            size_range="100-500",
        ),
        audience=AudienceInfo(
            primary="Enterprise CTOs",
            secondary=["VP Engineering", "Tech Leads"],
            pain_points=["Slow deployment", "High costs"],
            desired_outcomes=["Faster time-to-market", "Better ROI"],
        ),
        voice=VoiceInfo(
            tone="Professional, innovative",
            style_guidelines=["Clear", "concise", "data-driven"],
            forbidden_phrases=["Proprietary", "Closed-source"],
            cta_preferences=["Learn more", "Get started"],
        ),
        insights=InsightsInfo(
            positioning="Enterprise AI platform for data-driven decision making",
            key_messages=["Accelerate AI adoption", "Reduce deployment time"],
            recent_news=["Series B funding", "New partnership"],
            competitors=["Competitor A", "Competitor B"],
        ),
        clarifying_questions=[
            ClarifyingQuestion(
                id="q1",
                question="What is your primary use case?",
                reason="To tailor content to your business needs",
                expected_response_type="string",
            ),
        ],
        clarifying_answers={},
        source_metadata=[
            SourceMetadata(
                source="perplexity",
                tool="perplexity_research",
                timestamp=datetime.utcnow(),
                confidence=0.95,
            ),
        ],
    )
    
    # Test 1: Export snapshot
    print("\n" + "="*60)
    print("TEST 1: Export CompanySnapshot to Card Service")
    print("="*60)
    
    tenant_id = "test-pipeline-" + str(uuid4())[:8]
    
    try:
        result = await pipeline.export_snapshot(
            tenant_id=tenant_id,
            snapshot=snapshot,
        )
        
        print(f"✅ Export successful!")
        print(f"   Status: {result['status']}")
        print(f"   Snapshot ID: {result['snapshot_id']}")
        print(f"   Cards created: {len(result['cards'])}")
        print(f"   Message: {result['message']}")
        
        # Verify cards
        if result['status'] == 'success' and len(result['cards']) == 4:
            print("\n✅ TEST 1 PASSED: 4 cards created successfully")
            
            # Print card details
            for card in result['cards']:
                print(f"\n   Card: {card.get('title', 'N/A')}")
                print(f"   Type: {card.get('card_type', 'N/A')}")
                print(f"   ID: {card.get('id', 'N/A')}")
        else:
            print(f"\n❌ TEST 1 FAILED: Expected 4 cards, got {len(result['cards'])}")
            return False
    
    except Exception as e:
        print(f"❌ TEST 1 FAILED: {str(e)}")
        logger.error(f"Export failed: {str(e)}", exc_info=True)
        return False
    
    # Test 2: Verify cards are readable from Card Service
    print("\n" + "="*60)
    print("TEST 2: Verify cards are readable from Card Service")
    print("="*60)
    
    try:
        cards = await card_service_client.get_cards(tenant_id=tenant_id)
        
        print(f"✅ Retrieved {len(cards)} cards from Card Service")
        
        if len(cards) == 4:
            print("✅ TEST 2 PASSED: All 4 cards are readable")
            
            # Print card types
            card_types = [card.get('card_type') for card in cards]
            print(f"   Card types: {card_types}")
        else:
            print(f"❌ TEST 2 FAILED: Expected 4 cards, got {len(cards)}")
            return False
    
    except Exception as e:
        print(f"❌ TEST 2 FAILED: {str(e)}")
        logger.error(f"Failed to retrieve cards: {str(e)}", exc_info=True)
        return False
    
    # Test 3: Verify card content
    print("\n" + "="*60)
    print("TEST 3: Verify card content")
    print("="*60)
    
    try:
        # Check that cards have expected content
        for card in cards:
            card_type = card.get('card_type')
            content = card.get('content', {})
            
            print(f"\n   {card_type.upper()} Card:")
            print(f"   - Title: {card.get('title')}")
            print(f"   - Content keys: {list(content.keys())[:5]}...")
            
            # Verify content is not empty
            if not content:
                print(f"   ❌ Content is empty!")
                return False
        
        print("\n✅ TEST 3 PASSED: All cards have content")
    
    except Exception as e:
        print(f"❌ TEST 3 FAILED: {str(e)}")
        logger.error(f"Content verification failed: {str(e)}", exc_info=True)
        return False
    
    # Cleanup
    await card_service_client.close()
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)
    
    return True


async def main():
    """Run all tests."""
    success = await test_card_export_pipeline()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)

