#!/usr/bin/env python3
"""
Sprint 4 Day 1: End-to-End Test
Onboarding → Cards API → Workflow

Tests:
1. Install dependencies (if needed)
2. Prepare test payload with CompanySnapshot v1
3. Submit Onboarding (creates 4 cards via Cards API)
4. Verify idempotency (replay with same Idempotency-Key)
5. Cards retrieve (verify consistency)
6. Workflow execution (optional, uses card_ids)
7. Metrics and logs verification
8. Final report

Prerequisites:
- Onboarding API: http://localhost:8001
- Cards API: http://localhost:8002
- Workflow API: http://localhost:8000
"""

import asyncio
import httpx
import json
import sys
from uuid import uuid4
from datetime import datetime


# Service URLs
ONBOARDING_URL = "http://localhost:8001"
CARDS_URL = "http://localhost:8002"
WORKFLOW_URL = "http://localhost:8000"

# Test identifiers
TENANT_ID = str(uuid4())
SESSION_ID = str(uuid4())
TRACE_ID = str(uuid4())


def print_header(title: str):
    """Print formatted header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_step(step: int, title: str):
    """Print step header."""
    print(f"\n{'─' * 80}")
    print(f"STEP {step}: {title}")
    print(f"{'─' * 80}\n")


async def check_services():
    """Check if all services are running."""
    print_step(0, "Checking Services")
    
    services = {
        "Onboarding API": f"{ONBOARDING_URL}/health",
        "Cards API": f"{CARDS_URL}/health",
        "Workflow API": f"{WORKFLOW_URL}/health",
    }
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        all_ok = True
        for name, url in services.items():
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    print(f"✅ {name}: OK")
                else:
                    print(f"❌ {name}: HTTP {response.status_code}")
                    all_ok = False
            except Exception as e:
                print(f"❌ {name}: {str(e)}")
                all_ok = False
        
        return all_ok


async def create_onboarding_session():
    """Step 1: Create onboarding session."""
    print_step(1, "Create Onboarding Session")
    
    payload = {
        "brand_name": "Acme Corp",
        "website": "https://acme.com",
        "goal": "LINKEDIN_POST",
        "user_email": "test@acme.com",
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-Tenant-ID": TENANT_ID,
        "X-Trace-ID": TRACE_ID,
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{ONBOARDING_URL}/api/v1/onboarding/start",
            json=payload,
            headers=headers,
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code != 201:
            print(f"❌ Failed to create session: {response.text}")
            return None
        
        data = response.json()
        session_id = data["session_id"]
        
        print(f"✅ Session created: {session_id}")
        print(f"   State: {data['state']}")
        print(f"   Questions: {len(data.get('questions', []))}")
        
        return session_id


async def submit_answers_and_create_cards(session_id: str):
    """Step 2-3: Submit answers (triggers Cards API batch creation)."""
    print_step(2, "Submit Answers (Triggers Cards API Batch Creation)")
    
    # Prepare answers
    answers_payload = {
        "answers": [
            {
                "question_id": 1,
                "answer": "We focus on enterprise SaaS solutions for AI-powered automation"
            },
            {
                "question_id": 2,
                "answer": "Our main differentiator is real-time AI processing with 99.9% uptime"
            },
            {
                "question_id": 3,
                "answer": "We target CTOs, engineering leaders, and product managers in tech companies"
            },
        ]
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-Tenant-ID": TENANT_ID,
        "X-Trace-ID": TRACE_ID,
        "Idempotency-Key": f"onboarding-{session_id}-batch",
    }
    
    print(f"Session ID: {session_id}")
    print(f"Tenant ID: {TENANT_ID}")
    print(f"Trace ID: {TRACE_ID}")
    print(f"Idempotency-Key: onboarding-{session_id}-batch")
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{ONBOARDING_URL}/api/v1/onboarding/{session_id}/answers",
            json=answers_payload,
            headers=headers,
        )
        
        print(f"\nStatus: {response.status_code}")
        
        if response.status_code == 502:
            print("❌ Cards API error (502 Bad Gateway)")
            print(f"   Detail: {response.json()}")
            return None
        
        if response.status_code not in [200, 201]:
            print(f"❌ Failed to submit answers: {response.text}")
            return None
        
        data = response.json()
        
        print(f"✅ Answers submitted successfully")
        print(f"   State: {data['state']}")
        print(f"   Message: {data.get('message', 'N/A')}")
        
        # Get session to extract card_ids
        response = await client.get(
            f"{ONBOARDING_URL}/api/v1/onboarding/{session_id}",
            headers={"X-Tenant-ID": TENANT_ID},
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to get session: {response.text}")
            return None
        
        session_data = response.json()
        metadata = session_data.get("metadata", {})
        card_ids = metadata.get("card_ids", [])
        cards_created_count = metadata.get("cards_created_count", 0)
        cards_status = metadata.get("cards_status", "unknown")
        
        print(f"\n📋 Cards Created:")
        print(f"   Card IDs: {card_ids}")
        print(f"   Created count: {cards_created_count}")
        print(f"   Status: {cards_status}")
        
        if cards_created_count == 4:
            print("   ✅ All 4 cards created successfully")
        elif cards_created_count > 0:
            print(f"   ⚠️  Partial creation: {cards_created_count}/4 cards")
        else:
            print("   ❌ No cards created")
            return None
        
        return {
            "session_id": session_id,
            "card_ids": card_ids,
            "created_count": cards_created_count,
            "status": cards_status,
        }


async def test_idempotency(session_id: str, original_card_ids: list):
    """Step 4: Test idempotency (replay with same Idempotency-Key)."""
    print_step(4, "Test Idempotency (Replay)")
    
    answers_payload = {
        "answers": [
            {"question_id": 1, "answer": "We focus on enterprise SaaS solutions for AI-powered automation"},
            {"question_id": 2, "answer": "Our main differentiator is real-time AI processing with 99.9% uptime"},
            {"question_id": 3, "answer": "We target CTOs, engineering leaders, and product managers in tech companies"},
        ]
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-Tenant-ID": TENANT_ID,
        "X-Trace-ID": TRACE_ID,
        "Idempotency-Key": f"onboarding-{session_id}-batch",  # Same key
    }
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{ONBOARDING_URL}/api/v1/onboarding/{session_id}/answers",
            json=answers_payload,
            headers=headers,
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code not in [200, 201]:
            print(f"❌ Replay failed: {response.text}")
            return False
        
        # Get session to extract card_ids
        response = await client.get(
            f"{ONBOARDING_URL}/api/v1/onboarding/{session_id}",
            headers={"X-Tenant-ID": TENANT_ID},
        )
        
        session_data = response.json()
        metadata = session_data.get("metadata", {})
        replay_card_ids = metadata.get("card_ids", [])
        
        print(f"\n📋 Idempotency Check:")
        print(f"   Original card_ids: {original_card_ids}")
        print(f"   Replay card_ids:   {replay_card_ids}")
        
        if original_card_ids == replay_card_ids:
            print("   ✅ Idempotency verified: Same card_ids returned")
            return True
        else:
            print("   ❌ Idempotency failed: Different card_ids returned")
            return False


async def verify_cards_retrieve(card_ids: list):
    """Step 5: Verify cards via Cards API retrieve endpoint."""
    print_step(5, "Verify Cards via Retrieve Endpoint")
    
    payload = {
        "tenant_id": TENANT_ID,
        "card_ids": card_ids,
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-Tenant-ID": TENANT_ID,
        "X-Trace-ID": TRACE_ID,
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{CARDS_URL}/api/v1/cards/retrieve",
            json=payload,
            headers=headers,
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Retrieve failed: {response.text}")
            return False
        
        data = response.json()
        partial_result = response.headers.get("X-Partial-Result", "unknown")
        
        print(f"X-Partial-Result: {partial_result}")
        print(f"Cards retrieved: {len(data.get('cards', []))}")
        
        if len(data.get("cards", [])) == 4 and partial_result == "false":
            print("✅ All 4 cards retrieved successfully")
            
            # Print card details
            for card in data["cards"]:
                print(f"   - {card['card_type']}: {card.get('title', 'N/A')}")
            
            return True
        else:
            print(f"⚠️  Partial result or missing cards")
            return False


async def execute_workflow(card_ids: list):
    """Step 6: Execute workflow with card_ids (optional)."""
    print_step(6, "Execute Workflow (Optional)")
    
    payload = {
        "workflow_type": "premium_newsletter",
        "card_ids": card_ids,
        "parameters": {
            "topic": "AI trends in enterprise automation"
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-Tenant-ID": TENANT_ID,
        "X-Trace-ID": TRACE_ID,
    }
    
    async with httpx.AsyncClient(timeout=180.0) as client:
        try:
            response = await client.post(
                f"{WORKFLOW_URL}/api/v1/workflow/execute",
                json=payload,
                headers=headers,
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Workflow executed successfully")
                print(f"   Workflow ID: {data.get('workflow_id', 'N/A')}")
                print(f"   Output length: {len(data.get('output', ''))}")
                return True
            else:
                print(f"⚠️  Workflow execution failed: {response.text}")
                return False
        except Exception as e:
            print(f"⚠️  Workflow execution error: {str(e)}")
            return False


async def verify_metrics():
    """Step 7: Verify Prometheus metrics."""
    print_step(7, "Verify Prometheus Metrics")
    
    services = {
        "Onboarding": ONBOARDING_URL,
        "Cards": CARDS_URL,
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for service_name, base_url in services.items():
            print(f"\n📊 {service_name} Metrics:")
            
            try:
                response = await client.get(f"{base_url}/metrics")
                
                if response.status_code != 200:
                    print(f"   ❌ Failed to get metrics: HTTP {response.status_code}")
                    continue
                
                metrics_text = response.text
                
                # Check for key metrics
                if service_name == "Onboarding":
                    key_metrics = [
                        "onboarding_cards_created_total",
                        "onboarding_batch_duration_ms",
                    ]
                else:  # Cards
                    key_metrics = [
                        "cards_api_requests_total",
                        "cards_api_request_duration_seconds",
                    ]
                
                for metric in key_metrics:
                    if metric in metrics_text:
                        print(f"   ✅ {metric}")
                    else:
                        print(f"   ⚠️  {metric} (not found)")
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")


async def main():
    """Main test flow."""
    print_header("SPRINT 4 DAY 1: END-TO-END TEST")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Tenant ID: {TENANT_ID}")
    print(f"Trace ID: {TRACE_ID}")
    
    # Step 0: Check services
    if not await check_services():
        print("\n❌ Some services are not running. Please start all services first.")
        print("\nTo start services:")
        print("  - Onboarding: cd onboarding && python -m onboarding.api.main")
        print("  - Cards: cd cards-api && docker-compose up -d")
        print("  - Workflow: cd api && uvicorn rest.main:app --port 8000")
        return 1
    
    # Step 1: Create session
    session_id = await create_onboarding_session()
    if not session_id:
        return 1
    
    # Step 2-3: Submit answers and create cards
    result = await submit_answers_and_create_cards(session_id)
    if not result:
        return 1
    
    card_ids = result["card_ids"]
    
    # Step 4: Test idempotency
    idempotency_ok = await test_idempotency(session_id, card_ids)
    
    # Step 5: Verify cards retrieve
    retrieve_ok = await verify_cards_retrieve(card_ids)
    
    # Step 6: Execute workflow (optional)
    workflow_ok = await execute_workflow(card_ids)
    
    # Step 7: Verify metrics
    await verify_metrics()
    
    # Final report
    print_header("FINAL REPORT")
    
    print(f"📋 Test Summary:")
    print(f"   Session ID: {session_id}")
    print(f"   Tenant ID: {TENANT_ID}")
    print(f"   Trace ID: {TRACE_ID}")
    print(f"\n📊 Results:")
    print(f"   Cards created: {result['created_count']}/4")
    print(f"   Status: {result['status']}")
    print(f"   Card IDs: {card_ids}")
    print(f"\n✅ Tests:")
    print(f"   Idempotency: {'✅ PASS' if idempotency_ok else '❌ FAIL'}")
    print(f"   Retrieve: {'✅ PASS' if retrieve_ok else '❌ FAIL'}")
    print(f"   Workflow: {'✅ PASS' if workflow_ok else '⚠️  SKIP/FAIL'}")
    
    all_ok = idempotency_ok and retrieve_ok
    
    if all_ok:
        print("\n" + "=" * 80)
        print("✅ SPRINT 4 DAY 1: END-TO-END TEST PASSED")
        print("=" * 80 + "\n")
        return 0
    else:
        print("\n" + "=" * 80)
        print("❌ SPRINT 4 DAY 1: END-TO-END TEST FAILED")
        print("=" * 80 + "\n")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

