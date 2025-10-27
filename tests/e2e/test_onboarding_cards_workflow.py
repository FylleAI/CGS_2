"""
E2E Test: Onboarding → Cards → Workflow

Tests the complete flow:
1. Onboarding creates cards via POST /api/v1/cards/batch
2. Workflow retrieves cards via POST /api/v1/cards/retrieve
3. Workflow tracks usage via POST /api/v1/cards/{id}/usage
4. Verify metrics are exposed on /metrics
"""

import os
from uuid import uuid4

import pytest
import httpx

# Test configuration
CARDS_API_URL = os.getenv("CARDS_API_URL", "http://localhost:8002")
TENANT_ID = "123e4567-e89b-12d3-a456-426614174000"
TRACE_ID = f"e2e-test-{uuid4()}"


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_onboarding_cards_workflow_e2e():
    """
    E2E Test: Complete flow from onboarding to workflow execution.
    
    Flow:
    1. Onboarding: Create 4 cards (company, audience, voice, insight)
    2. Workflow: Retrieve cards by IDs
    3. Workflow: Track usage for each card
    4. Verify: Usage count incremented, events recorded
    5. Verify: Metrics exposed on /metrics
    """
    
    # ========================================================================
    # STEP 1: ONBOARDING - Create Cards
    # ========================================================================
    print("\n" + "=" * 80)
    print("STEP 1: ONBOARDING - Create Cards")
    print("=" * 80)
    
    idempotency_key = f"onboarding-session-{uuid4()}"
    
    cards_to_create = [
        {
            "card_type": "company",
            "content": {
                "name": "E2E Test Company",
                "domain": "e2etest.com",
                "industry": "Technology",
                "description": "E2E test company for integration testing",
                "key_offerings": ["Product A", "Product B"],
                "differentiators": ["Innovation", "Quality"],
            },
        },
        {
            "card_type": "audience",
            "content": {
                "primary": "Tech Decision Makers",
                "pain_points": ["Complexity", "Cost"],
                "desired_outcomes": ["Simplicity", "ROI"],
            },
        },
        {
            "card_type": "voice",
            "content": {
                "tone": "Professional",
                "style_guidelines": ["Clear", "Concise", "Data-driven"],
            },
        },
        {
            "card_type": "insight",
            "content": {
                "positioning": "Market Leader",
                "key_messages": ["Innovation", "Trust", "Results"],
                "recent_news": ["Product launch", "Award won"],
            },
        },
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{CARDS_API_URL}/api/v1/cards/batch",
            headers={
                "X-Tenant-ID": TENANT_ID,
                "X-Trace-ID": TRACE_ID,
                "Idempotency-Key": idempotency_key,
            },
            json={"cards": cards_to_create},
        )
        
        assert response.status_code == 201, f"Failed to create cards: {response.text}"
        
        batch_data = response.json()
        assert batch_data["created_count"] == 4
        assert len(batch_data["cards"]) == 4
        
        card_ids = [card["card_id"] for card in batch_data["cards"]]
        
        print(f"✅ Created {batch_data['created_count']} cards")
        for card in batch_data["cards"]:
            print(f"  - {card['card_id']}: {card['card_type']}")
        
        # Verify idempotency cache
        cache_status = response.headers.get("X-Idempotency-Cache", "UNKNOWN")
        print(f"  - Idempotency Cache: {cache_status}")
        assert cache_status == "MISS"  # First time
    
    # ========================================================================
    # STEP 2: WORKFLOW - Retrieve Cards
    # ========================================================================
    print("\n" + "=" * 80)
    print("STEP 2: WORKFLOW - Retrieve Cards")
    print("=" * 80)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{CARDS_API_URL}/api/v1/cards/retrieve",
            headers={
                "X-Tenant-ID": TENANT_ID,
                "X-Trace-ID": TRACE_ID,
            },
            json={"card_ids": card_ids},
        )
        
        assert response.status_code == 200, f"Failed to retrieve cards: {response.text}"
        
        retrieve_data = response.json()
        assert len(retrieve_data["cards"]) == 4
        
        print(f"✅ Retrieved {len(retrieve_data['cards'])} cards")
        for card in retrieve_data["cards"]:
            print(f"  - {card['card_id']}: {card['card_type']}")
        
        # Verify partial result header
        partial_result = response.headers.get("X-Partial-Result", "false")
        print(f"  - Partial Result: {partial_result}")
        assert partial_result == "false"  # All cards found
    
    # ========================================================================
    # STEP 3: WORKFLOW - Track Usage
    # ========================================================================
    print("\n" + "=" * 80)
    print("STEP 3: WORKFLOW - Track Usage")
    print("=" * 80)
    
    workflow_id = f"workflow-e2e-{uuid4()}"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for card_id in card_ids:
            response = await client.post(
                f"{CARDS_API_URL}/api/v1/cards/{card_id}/usage",
                headers={
                    "X-Tenant-ID": TENANT_ID,
                    "X-Trace-ID": TRACE_ID,
                },
                json={
                    "workflow_id": workflow_id,
                    "workflow_type": "premium_newsletter",
                    "session_id": f"session-{uuid4()}",
                },
            )
            
            assert response.status_code == 200, f"Failed to track usage: {response.text}"
            
            usage_data = response.json()
            assert usage_data["card_id"] == card_id
            assert usage_data["usage_count"] >= 1
            assert usage_data["event_recorded"] is True
            
            event_recorded = response.headers.get("X-Event-Recorded", "false")
            print(f"  - {card_id}: usage_count={usage_data['usage_count']}, event_recorded={event_recorded}")
    
    print("✅ Usage tracked for all cards")
    
    # ========================================================================
    # STEP 4: VERIFY - Usage Count Incremented
    # ========================================================================
    print("\n" + "=" * 80)
    print("STEP 4: VERIFY - Usage Count Incremented")
    print("=" * 80)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{CARDS_API_URL}/api/v1/cards/retrieve",
            headers={
                "X-Tenant-ID": TENANT_ID,
                "X-Trace-ID": TRACE_ID,
            },
            json={"card_ids": card_ids},
        )
        
        assert response.status_code == 200
        
        retrieve_data = response.json()
        for card in retrieve_data["cards"]:
            assert card["usage_count"] >= 1, f"Card {card['card_id']} has usage_count={card['usage_count']}"
            print(f"  - {card['card_id']}: usage_count={card['usage_count']}")
    
    print("✅ All cards have usage_count >= 1")
    
    # ========================================================================
    # STEP 5: VERIFY - Metrics Exposed
    # ========================================================================
    print("\n" + "=" * 80)
    print("STEP 5: VERIFY - Metrics Exposed")
    print("=" * 80)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{CARDS_API_URL}/metrics")
        
        assert response.status_code == 200
        
        metrics_text = response.text
        
        # Check for key metrics
        assert "cards_api_requests_total" in metrics_text
        assert "cards_api_request_duration_seconds" in metrics_text
        assert "card_usage_events_total" in metrics_text
        assert "cards_usage_write_duration_ms" in metrics_text
        
        print("✅ Metrics exposed:")
        print("  - cards_api_requests_total")
        print("  - cards_api_request_duration_seconds")
        print("  - card_usage_events_total")
        print("  - cards_usage_write_duration_ms")
    
    # ========================================================================
    # STEP 6: VERIFY - Idempotency Replay
    # ========================================================================
    print("\n" + "=" * 80)
    print("STEP 6: VERIFY - Idempotency Replay")
    print("=" * 80)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Replay the same batch create request
        response = await client.post(
            f"{CARDS_API_URL}/api/v1/cards/batch",
            headers={
                "X-Tenant-ID": TENANT_ID,
                "X-Trace-ID": TRACE_ID,
                "Idempotency-Key": idempotency_key,  # Same key as Step 1
            },
            json={"cards": cards_to_create},
        )
        
        assert response.status_code == 201
        
        replay_data = response.json()
        assert replay_data["created_count"] == 4
        
        # Verify idempotency cache HIT
        cache_status = response.headers.get("X-Idempotency-Cache", "UNKNOWN")
        print(f"  - Idempotency Cache: {cache_status}")
        assert cache_status == "HIT"  # Replay detected
    
    print("✅ Idempotency replay successful (cache HIT)")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "=" * 80)
    print("E2E TEST SUMMARY")
    print("=" * 80)
    print("✅ STEP 1: Onboarding created 4 cards")
    print("✅ STEP 2: Workflow retrieved 4 cards")
    print("✅ STEP 3: Workflow tracked usage for 4 cards")
    print("✅ STEP 4: Usage count incremented for all cards")
    print("✅ STEP 5: Metrics exposed on /metrics")
    print("✅ STEP 6: Idempotency replay successful")
    print("=" * 80)
    print("🎉 E2E TEST PASSED!")
    print("=" * 80)

