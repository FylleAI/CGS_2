#!/usr/bin/env python3
"""
Smoke test for Fylle API clients.

Tests that clients can be imported and instantiated correctly.
Does NOT make actual API calls (no running server required).
"""

import sys
from uuid import UUID, uuid4


def test_cards_client():
    """Test Cards client import and instantiation."""
    print("🔍 Testing fylle-cards-client...")
    
    try:
        from fylle_cards_client import CardsClient, CardType, ContextCard
        
        # Test instantiation
        client = CardsClient(
            base_url="http://localhost:8002",
            tenant_id=str(uuid4()),
            trace_id="test-trace-123",
            session_id="test-session-456",
        )
        
        # Test enum
        assert CardType.COMPANY == "company"
        assert CardType.AUDIENCE == "audience"
        assert CardType.VOICE == "voice"
        assert CardType.INSIGHT == "insight"
        
        # Test model validation
        card_data = {
            "card_id": str(uuid4()),
            "tenant_id": str(uuid4()),
            "card_type": "company",
            "title": "Test Card",
            "content": {"test": "data"},
            "tags": [],
            "version": 1,
            "is_active": True,
            "usage_count": 0,
            "created_at": "2025-10-26T10:00:00Z",
            "updated_at": "2025-10-26T10:00:00Z",
            "created_by": "test",
        }
        card = ContextCard(**card_data)
        assert card.title == "Test Card"
        assert card.card_type == CardType.COMPANY
        
        client.close()
        
        print("✅ fylle-cards-client: OK")
        return True
        
    except Exception as e:
        print(f"❌ fylle-cards-client: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False


def test_workflow_client():
    """Test Workflow client import and instantiation."""
    print("🔍 Testing fylle-workflow-client...")
    
    try:
        from fylle_workflow_client import WorkflowClient, WorkflowType
        
        # Test instantiation
        client = WorkflowClient(
            base_url="http://localhost:8001",
            tenant_id=str(uuid4()),
            trace_id="test-trace-123",
            session_id="test-session-456",
        )
        
        # Test enum
        assert WorkflowType.PREMIUM_NEWSLETTER == "premium_newsletter"
        assert WorkflowType.ONBOARDING_CONTENT == "onboarding_content"
        
        client.close()
        
        print("✅ fylle-workflow-client: OK")
        return True
        
    except Exception as e:
        print(f"❌ fylle-workflow-client: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all smoke tests."""
    print("=" * 60)
    print("Fylle API Clients - Smoke Test")
    print("=" * 60)
    print()
    
    results = []
    
    # Test Cards client
    results.append(test_cards_client())
    print()
    
    # Test Workflow client
    results.append(test_workflow_client())
    print()
    
    # Summary
    print("=" * 60)
    if all(results):
        print("✅ All smoke tests passed!")
        print("=" * 60)
        return 0
    else:
        failed = sum(1 for r in results if not r)
        print(f"❌ {failed} smoke test(s) failed")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())

