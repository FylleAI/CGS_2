#!/usr/bin/env python3
"""
Test workflow execution with card_ids (new path).

This script tests the card-based context path by:
1. Creating test cards in Cards API (real database)
2. Executing a workflow with card_ids instead of legacy context
3. Verifying that cards are retrieved and used correctly

NOTE: This script now uses the REAL Cards API (port 8002) instead of mock.
      Requires Cards API to be running with Supabase connection.
"""

import json
import subprocess
import sys
import time
from typing import Any, Dict, List
from uuid import uuid4

import httpx

# Configuration
WORKFLOW_API_URL = "http://localhost:8000"
CARDS_API_URL = "http://localhost:8002"
TENANT_ID = "123e4567-e89b-12d3-a456-426614174000"  # Valid UUID
TRACE_ID = "test-card-path-001"

# Test card IDs will be created dynamically
TEST_CARD_IDS: List[str] = []


def check_server_health(url: str, service_name: str) -> bool:
    """Check if a server is healthy."""
    try:
        response = httpx.get(f"{url}/health", timeout=5.0)
        if response.status_code == 200:
            print(f"✅ {service_name} is healthy")
            return True
        else:
            print(f"❌ {service_name} returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {service_name} is not reachable: {e}")
        return False


def create_test_cards() -> bool:
    """Create test cards in Cards API (real database)."""
    print("\n" + "=" * 80)
    print("SETUP: Creating Test Cards")
    print("=" * 80)

    # Define test cards matching the old mock data
    test_cards = [
        {
            "card_type": "company",
            "content": {
                "name": "Fylle AI",
                "domain": "fylle.ai",
                "industry": "Artificial Intelligence",
                "description": "Fylle AI is a cutting-edge content generation platform that leverages advanced AI to create high-quality, personalized content for businesses.",
                "key_offerings": ["AI Content Generation", "Workflow Automation", "Multi-agent Systems"],
                "differentiators": ["Advanced AI models", "Customizable workflows", "Enterprise-ready"]
            }
        },
        {
            "card_type": "audience",
            "content": {
                "primary": "Tech Decision Makers",
                "pain_points": ["Content creation bottlenecks", "Inconsistent brand voice", "Time-consuming research"],
                "desired_outcomes": ["Faster content production", "Consistent quality", "Data-driven insights"]
            }
        },
        {
            "card_type": "voice",
            "content": {
                "tone": "Professional & Insightful",
                "style_guidelines": ["Clear and concise", "Data-driven", "Action-oriented", "Thought leadership"]
            }
        },
        {
            "card_type": "insight",
            "content": {
                "positioning": "AI Innovation Leader",
                "key_messages": ["Cutting-edge AI technology", "Proven ROI", "Enterprise-ready solutions"],
                "recent_news": ["Series B funding announced", "Fortune 500 client acquisition", "New AI model release"]
            }
        }
    ]

    try:
        # Create cards via batch endpoint
        response = httpx.post(
            f"{CARDS_API_URL}/api/v1/cards/batch",
            headers={
                "Content-Type": "application/json",
                "X-Tenant-ID": TENANT_ID,
                "X-Trace-ID": TRACE_ID,
                "Idempotency-Key": f"test-workflow-setup-{uuid4()}",
            },
            json={"cards": test_cards},
            timeout=10.0,
        )

        print(f"Status: {response.status_code}")

        if response.status_code == 201:
            data = response.json()
            print(f"✅ Created {data['created_count']} cards")

            # Store card IDs for later use
            global TEST_CARD_IDS
            TEST_CARD_IDS = [card["card_id"] for card in data["cards"]]

            for card in data["cards"]:
                print(f"  - {card['card_id']}: {card['card_type']}")

            return True
        else:
            print(f"❌ Card creation failed: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Card creation error: {e}")
        return False


def test_card_retrieval() -> bool:
    """Test card retrieval from Cards API."""
    print("\n" + "=" * 80)
    print("TEST 1: Card Retrieval")
    print("=" * 80)

    try:
        response = httpx.post(
            f"{CARDS_API_URL}/api/v1/cards/retrieve",
            headers={
                "Content-Type": "application/json",
                "X-Tenant-ID": TENANT_ID,
                "X-Trace-ID": TRACE_ID,
            },
            json={"card_ids": TEST_CARD_IDS},
            timeout=10.0,
        )

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            cards_found = len(data["cards"])
            print(f"✅ Retrieved {cards_found}/{len(TEST_CARD_IDS)} cards")

            for card in data["cards"]:
                content_preview = str(card['content'])[:50] + "..." if len(str(card['content'])) > 50 else str(card['content'])
                print(f"  - {card['card_id']}: {card['card_type']} - {content_preview}")

            # Check for partial result header
            partial_result = response.headers.get("X-Partial-Result", "false")
            if partial_result == "true":
                print(f"⚠️ Partial result: some cards not found")

            return cards_found == len(TEST_CARD_IDS)
        else:
            print(f"❌ Card retrieval failed: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Card retrieval error: {e}")
        return False


def test_workflow_with_cards() -> bool:
    """Test workflow execution with card_ids."""
    print("\n" + "=" * 80)
    print("TEST 2: Workflow Execution with Card IDs")
    print("=" * 80)

    workflow_request = {
        "workflow_type": "premium_newsletter",
        "card_ids": TEST_CARD_IDS,
        "context": {
            "topic": "The Future of AI in Enterprise",
            "target_audience": "Tech Decision Makers and C-level executives",
            "target_word_count": 800,
            "premium_sources": ["https://techcrunch.com", "https://venturebeat.com"],
            "company_name": "Fylle AI",
            "company_industry": "Artificial Intelligence",
        },
        "parameters": {},
    }

    print(f"Request:")
    print(f"  - Workflow: {workflow_request['workflow_type']}")
    print(f"  - Card IDs: {len(workflow_request['card_ids'])}")
    print(f"  - Topic: {workflow_request['context']['topic']}")

    try:
        response = httpx.post(
            f"{WORKFLOW_API_URL}/api/v1/workflow/execute",
            headers={
                "Content-Type": "application/json",
                "X-Tenant-ID": TENANT_ID,
                "X-Trace-ID": TRACE_ID,
            },
            json=workflow_request,
            timeout=120.0,
        )

        print(f"\nStatus: {response.status_code}")

        # Check headers
        if "X-Partial-Result" in response.headers:
            print(f"⚠️ Partial Result: {response.headers['X-Partial-Result']}")

        if "X-API-Deprecation-Warning" in response.headers:
            print(f"⚠️ Deprecation: {response.headers['X-API-Deprecation-Warning']}")

        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Workflow completed successfully!")
            print(f"  - Workflow ID: {data['workflow_id']}")
            print(f"  - Status: {data['status']}")

            # Check metrics
            if "metrics" in data:
                metrics = data["metrics"]
                print(f"\n📊 Metrics:")
                print(f"  - Execution time: {metrics.get('execution_time_ms')}ms")
                print(f"  - Cards used: {metrics.get('cards_used')}")
                print(f"  - Cache hit rate: {metrics.get('cache_hit_rate')}")
                print(f"  - Tokens used: {metrics.get('tokens_used')}")

            # Check output
            if "output" in data:
                output = data["output"]
                if "final_word_count" in output:
                    print(f"\n📄 Output:")
                    print(f"  - Word count: {output['final_word_count']}")
                    print(f"  - Accuracy: {output.get('word_count_accuracy', 'N/A')}%")

                if "final_output" in output:
                    preview = output["final_output"][:200]
                    print(f"\n📝 Content preview:")
                    print(f"  {preview}...")

            return True
        else:
            print(f"❌ Workflow execution failed: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Workflow execution error: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 80)
    print("WORKFLOW CARD-BASED CONTEXT TEST (Real Cards API)")
    print("=" * 80)

    # Check if servers are running
    print("\n🔍 Checking server health...")

    cards_healthy = check_server_health(CARDS_API_URL, "Cards API")
    workflow_healthy = check_server_health(WORKFLOW_API_URL, "Workflow API")

    if not cards_healthy:
        print("\n❌ Cards API is not running!")
        print("Start it with: ./scripts/start_cards_api.sh")
        print("Or: uvicorn cards.api.main:app --port 8002")
        sys.exit(1)

    if not workflow_healthy:
        print("\n❌ Workflow API is not running!")
        print("Start it with: python3 -m uvicorn api.rest.main:app --port 8000")
        sys.exit(1)

    # Run tests
    results = []

    # Setup: Create test cards
    if not create_test_cards():
        print("\n❌ Failed to create test cards!")
        sys.exit(1)

    # Test 1: Card retrieval
    results.append(("Card Retrieval", test_card_retrieval()))

    # Test 2: Workflow with cards
    results.append(("Workflow with Card IDs", test_workflow_with_cards()))

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
        if not passed:
            all_passed = False

    print("=" * 80)

    if all_passed:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()

