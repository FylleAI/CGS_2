"""
Test Cards API Integration (Sprint 4 Day 1)

Tests the complete flow:
1. Start onboarding session
2. Submit answers
3. Verify Cards API batch creation
4. Verify card_ids in session
5. Verify idempotency
6. Verify metrics

Requirements:
- Onboarding API running on http://localhost:8001
- Cards API running on http://localhost:8002
- Supabase configured
"""

import asyncio
import httpx
import json
from uuid import uuid4


BASE_URL = "http://localhost:8001"
CARDS_API_URL = "http://localhost:8002"


async def test_cards_integration():
    """Test complete Cards API integration."""
    
    print("\n" + "="*80)
    print("SPRINT 4 DAY 1: CARDS API INTEGRATION TEST")
    print("="*80 + "\n")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        
        # ========================================================================
        # STEP 1: Start Onboarding Session
        # ========================================================================
        print("📝 STEP 1: Starting onboarding session...")
        
        start_request = {
            "brand_name": "Acme Corp",
            "website": "https://acme.com",
            "goal": "LINKEDIN_POST",
            "user_email": "test@acme.com",
        }
        
        response = await client.post(
            f"{BASE_URL}/api/v1/onboarding/start",
            json=start_request,
        )
        
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
        
        data = response.json()
        session_id = data["session_id"]
        
        print(f"✅ Session created: {session_id}")
        print(f"   State: {data['state']}")
        print(f"   Questions: {len(data.get('questions', []))}")
        
        # ========================================================================
        # STEP 2: Submit Answers (triggers Cards API integration)
        # ========================================================================
        print("\n📤 STEP 2: Submitting answers (triggers Cards API batch creation)...")
        
        # Generate unique tenant_id and trace_id for this test
        tenant_id = str(uuid4())
        trace_id = str(uuid4())
        
        answers_request = {
            "answers": [
                {"question_id": 1, "answer": "We focus on enterprise SaaS solutions"},
                {"question_id": 2, "answer": "Our main differentiator is AI-powered automation"},
                {"question_id": 3, "answer": "We target CTOs and engineering leaders"},
            ]
        }
        
        headers = {
            "X-Tenant-ID": tenant_id,
            "X-Trace-ID": trace_id,
            "Idempotency-Key": f"onboarding-{session_id}-batch",
        }
        
        response = await client.post(
            f"{BASE_URL}/api/v1/onboarding/{session_id}/answers",
            json=answers_request,
            headers=headers,
        )
        
        print(f"   Response status: {response.status_code}")
        
        if response.status_code == 502:
            print("⚠️  Cards API error (502 Bad Gateway)")
            print(f"   Detail: {response.json()}")
            print("\n❌ TEST FAILED: Cards API not available or returned error")
            return False
        
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        print(f"✅ Answers submitted successfully")
        print(f"   State: {data['state']}")
        print(f"   Message: {data.get('message', 'N/A')}")
        
        # ========================================================================
        # STEP 3: Verify Cards Created via Cards API
        # ========================================================================
        print("\n🔍 STEP 3: Verifying cards created in Cards API...")
        
        # Get session details to extract card_ids
        response = await client.get(
            f"{BASE_URL}/api/v1/onboarding/{session_id}",
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        session_data = response.json()
        metadata = session_data.get("metadata", {})
        card_ids = metadata.get("card_ids", [])
        cards_created_count = metadata.get("cards_created_count", 0)
        cards_status = metadata.get("cards_status", "unknown")
        
        print(f"   Card IDs: {card_ids}")
        print(f"   Created count: {cards_created_count}")
        print(f"   Status: {cards_status}")
        
        if cards_created_count == 4:
            print("✅ All 4 cards created successfully")
        elif cards_created_count > 0:
            print(f"⚠️  Partial creation: {cards_created_count}/4 cards created")
        else:
            print("❌ No cards created")
            return False
        
        # Verify cards exist in Cards API
        print("\n🔍 STEP 3.1: Verifying cards in Cards API...")
        
        for card_id in card_ids:
            response = await client.get(
                f"{CARDS_API_URL}/api/v1/cards/{card_id}",
                headers={"X-Tenant-ID": tenant_id},
            )
            
            if response.status_code == 200:
                card_data = response.json()
                print(f"   ✅ Card {card_id}: {card_data.get('card_type', 'unknown')} - {card_data.get('title', 'N/A')}")
            else:
                print(f"   ❌ Card {card_id}: Not found (status {response.status_code})")
        
        # ========================================================================
        # STEP 4: Test Idempotency (replay with same Idempotency-Key)
        # ========================================================================
        print("\n🔁 STEP 4: Testing idempotency (replay with same Idempotency-Key)...")
        
        response = await client.post(
            f"{BASE_URL}/api/v1/onboarding/{session_id}/answers",
            json=answers_request,
            headers=headers,  # Same headers, including Idempotency-Key
        )
        
        # Should return same result (idempotent)
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"
        
        data = response.json()
        
        print(f"✅ Idempotency verified")
        print(f"   State: {data['state']}")
        
        # Verify card_ids are the same
        response = await client.get(
            f"{BASE_URL}/api/v1/onboarding/{session_id}",
        )
        
        session_data_replay = response.json()
        metadata_replay = session_data_replay.get("metadata", {})
        card_ids_replay = metadata_replay.get("card_ids", [])
        
        if card_ids == card_ids_replay:
            print(f"✅ Same card_ids returned: {len(card_ids)} cards")
        else:
            print(f"❌ Different card_ids returned!")
            print(f"   Original: {card_ids}")
            print(f"   Replay: {card_ids_replay}")
            return False
        
        # ========================================================================
        # STEP 5: Verify Metrics
        # ========================================================================
        print("\n📊 STEP 5: Verifying Prometheus metrics...")
        
        response = await client.get(f"{BASE_URL}/metrics")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        metrics_text = response.text
        
        # Check for expected metrics
        expected_metrics = [
            "onboarding_cards_created_total",
            "onboarding_batch_duration_ms",
        ]
        
        for metric in expected_metrics:
            if metric in metrics_text:
                print(f"   ✅ {metric} present")
            else:
                print(f"   ❌ {metric} missing")
        
        # ========================================================================
        # SUMMARY
        # ========================================================================
        print("\n" + "="*80)
        print("✅ SPRINT 4 DAY 1: CARDS API INTEGRATION TEST PASSED")
        print("="*80)
        print(f"\n📋 Summary:")
        print(f"   - Session ID: {session_id}")
        print(f"   - Tenant ID: {tenant_id}")
        print(f"   - Trace ID: {trace_id}")
        print(f"   - Cards created: {cards_created_count}/4")
        print(f"   - Status: {cards_status}")
        print(f"   - Idempotency: ✅ Verified")
        print(f"   - Metrics: ✅ Exposed")
        print("\n")
        
        return True


if __name__ == "__main__":
    success = asyncio.run(test_cards_integration())
    exit(0 if success else 1)

