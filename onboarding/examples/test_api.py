"""
Test script for onboarding API endpoints.

Usage:
    python -m onboarding.examples.test_api
"""

import asyncio
import httpx
import json
from typing import Dict, Any


BASE_URL = "http://localhost:8001"


async def test_health_check():
    """Test health check endpoint."""
    print("\n" + "="*60)
    print("TEST 1: Health Check")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        
        print(f"Status: {response.status_code}")
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")
        
        return response.status_code == 200


async def test_start_onboarding():
    """Test start onboarding endpoint."""
    print("\n" + "="*60)
    print("TEST 2: Start Onboarding")
    print("="*60)
    
    payload = {
        "brand_name": "Acme Corp",
        "website": "https://acme.com",
        "goal": "linkedin_post",
        "user_email": "test@acme.com",
        "additional_context": "Focus on AI automation and productivity"
    }
    
    print(f"Request:\n{json.dumps(payload, indent=2)}")
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/onboarding/start",
            json=payload
        )
        
        print(f"\nStatus: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"Response:\n{json.dumps(data, indent=2)}")
            
            # Extract session_id and questions
            session_id = data.get("session_id")
            questions = data.get("clarifying_questions", [])
            
            print(f"\n✅ Session created: {session_id}")
            print(f"✅ Questions received: {len(questions)}")
            
            return session_id, questions
        else:
            print(f"❌ Error: {response.text}")
            return None, None


async def test_submit_answers(session_id: str, questions: list):
    """Test submit answers endpoint."""
    print("\n" + "="*60)
    print("TEST 3: Submit Answers")
    print("="*60)
    
    # Build answers based on question types
    answers = {}
    for q in questions:
        q_id = q["id"]
        q_type = q["expected_response_type"]
        
        if q_type == "boolean":
            answers[q_id] = True
        elif q_type == "number":
            answers[q_id] = 500
        elif q_type == "enum" and q.get("options"):
            answers[q_id] = q["options"][0]
        else:
            answers[q_id] = "AI automation and productivity benefits"
    
    payload = {"answers": answers}
    
    print(f"Session ID: {session_id}")
    print(f"Answers:\n{json.dumps(payload, indent=2)}")
    
    async with httpx.AsyncClient(timeout=180.0) as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/onboarding/{session_id}/answers",
            json=payload
        )
        
        print(f"\nStatus: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response:\n{json.dumps(data, indent=2)}")
            
            print(f"\n✅ Workflow executed successfully!")
            if data.get("content_title"):
                print(f"✅ Content generated: {data['content_title']}")
            if data.get("delivery_status"):
                print(f"✅ Delivery status: {data['delivery_status']}")
            
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False


async def test_get_status(session_id: str):
    """Test get status endpoint."""
    print("\n" + "="*60)
    print("TEST 4: Get Session Status")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/api/v1/onboarding/{session_id}/status"
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response:\n{json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False


async def test_get_detail(session_id: str):
    """Test get detail endpoint."""
    print("\n" + "="*60)
    print("TEST 5: Get Session Detail")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/api/v1/onboarding/{session_id}"
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            # Print without snapshot to keep output readable
            summary = {
                "session_id": data.get("session_id"),
                "brand_name": data.get("brand_name"),
                "goal": data.get("goal"),
                "state": data.get("state"),
                "has_snapshot": data.get("snapshot") is not None,
                "cgs_run_id": data.get("cgs_run_id"),
                "delivery_status": data.get("delivery_status"),
            }
            print(f"Response (summary):\n{json.dumps(summary, indent=2)}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False


async def run_full_test():
    """Run complete test flow."""
    print("\n" + "🚀"*30)
    print("ONBOARDING API - FULL TEST SUITE")
    print("🚀"*30)
    
    try:
        # Test 1: Health check
        health_ok = await test_health_check()
        if not health_ok:
            print("\n❌ Health check failed. Is the service running?")
            return
        
        # Test 2: Start onboarding
        session_id, questions = await test_start_onboarding()
        if not session_id:
            print("\n❌ Failed to start onboarding")
            return
        
        # Test 3: Submit answers
        submit_ok = await test_submit_answers(session_id, questions)
        if not submit_ok:
            print("\n❌ Failed to submit answers")
            return
        
        # Test 4: Get status
        await test_get_status(session_id)
        
        # Test 5: Get detail
        await test_get_detail(session_id)
        
        print("\n" + "✅"*30)
        print("ALL TESTS PASSED!")
        print("✅"*30)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


async def run_quick_test():
    """Run quick test (health check only)."""
    print("\n🔍 Quick Test - Health Check Only\n")
    
    try:
        health_ok = await test_health_check()
        if health_ok:
            print("\n✅ Service is healthy!")
        else:
            print("\n❌ Service is not healthy")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        asyncio.run(run_quick_test())
    else:
        print("\n📝 Note: This test requires:")
        print("  1. Onboarding service running on http://localhost:8001")
        print("  2. CGS backend running and accessible")
        print("  3. All API keys configured in .env")
        print("  4. Supabase database configured")
        print("\nPress Enter to continue or Ctrl+C to cancel...")
        
        try:
            input()
        except KeyboardInterrupt:
            print("\n\nTest cancelled.")
            sys.exit(0)
        
        asyncio.run(run_full_test())

