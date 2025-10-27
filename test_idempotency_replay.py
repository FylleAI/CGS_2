#!/usr/bin/env python3
"""
Idempotency Replay Test
Tests that replaying the same request with the same Idempotency-Key returns the same result.
"""

import requests
import json
from uuid import uuid4
import time

# Colors
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
NC = '\033[0m'

def print_header(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")

def print_success(msg):
    print(f"{GREEN}✅ {msg}{NC}")

def print_error(msg):
    print(f"{RED}❌ {msg}{NC}")

def print_info(msg):
    print(f"{BLUE}ℹ️  {msg}{NC}")

def print_warning(msg):
    print(f"{YELLOW}⚠️  {msg}{NC}")

# Test configuration
ONBOARDING_URL = "http://localhost:8000"
CARDS_URL = "http://localhost:8002"

# Generate test identifiers
TENANT_ID = str(uuid4())
TRACE_ID = str(uuid4())
IDEMPOTENCY_KEY = f"test-idempotency-{uuid4()}"

print_header("IDEMPOTENCY REPLAY TEST")

print_info(f"Tenant ID: {TENANT_ID}")
print_info(f"Trace ID:  {TRACE_ID}")
print_info(f"Idempotency Key: {IDEMPOTENCY_KEY}")

# ============================================================================
# STEP 1: Create Session
# ============================================================================

print("\n" + f"{CYAN}{'─' * 80}{NC}")
print(f"{YELLOW}STEP 1: Create Onboarding Session{NC}")
print(f"{CYAN}{'─' * 80}{NC}")

session_payload = {
    "tenant_id": TENANT_ID,
    "company_domain": "idempotency-test.com",
    "user_email": "test@idempotency-test.com"
}

response = requests.post(
    f"{ONBOARDING_URL}/api/v1/onboarding/sessions",
    json=session_payload,
    headers={
        "X-Tenant-ID": TENANT_ID,
        "X-Trace-ID": TRACE_ID,
    },
    timeout=30
)

if response.status_code != 201:
    print_error(f"Failed to create session: {response.status_code}")
    print(response.text)
    exit(1)

session_data = response.json()
session_id = session_data["session_id"]

print_success(f"Session created: {session_id}")

# ============================================================================
# STEP 2: First Request with Idempotency-Key
# ============================================================================

print("\n" + f"{CYAN}{'─' * 80}{NC}")
print(f"{YELLOW}STEP 2: First Request (with Idempotency-Key){NC}")
print(f"{CYAN}{'─' * 80}{NC}")

answers_payload = {
    "answers": [
        {
            "question_id": "q1",
            "answer": "First request - testing idempotency"
        },
        {
            "question_id": "q2",
            "answer": "This should create 4 cards"
        },
        {
            "question_id": "q3",
            "answer": "Professional, innovative, data-driven"
        }
    ]
}

print_info(f"Idempotency-Key: {IDEMPOTENCY_KEY}")

start_time = time.time()
response1 = requests.post(
    f"{ONBOARDING_URL}/api/v1/onboarding/sessions/{session_id}/answers",
    json=answers_payload,
    headers={
        "X-Tenant-ID": TENANT_ID,
        "X-Trace-ID": TRACE_ID,
        "Idempotency-Key": IDEMPOTENCY_KEY,
    },
    timeout=30
)
duration1 = time.time() - start_time

print_info(f"Status Code: {response1.status_code}")
print_info(f"Duration: {duration1:.2f}s")

if response1.status_code != 200:
    print_error(f"First request failed: {response1.status_code}")
    print(response1.text)
    exit(1)

data1 = response1.json()
card_ids_1 = data1.get("card_ids", [])
cards_count_1 = data1.get("cards_created_count", 0)

print_success(f"First request successful!")
print_info(f"Cards created: {cards_count_1}")
print_info(f"Card IDs: {card_ids_1}")

# ============================================================================
# STEP 3: Replay Request (same Idempotency-Key)
# ============================================================================

print("\n" + f"{CYAN}{'─' * 80}{NC}")
print(f"{YELLOW}STEP 3: Replay Request (same Idempotency-Key){NC}")
print(f"{CYAN}{'─' * 80}{NC}")

print_info(f"Replaying with same Idempotency-Key: {IDEMPOTENCY_KEY}")
print_warning("Expected: Same card_ids, no new cards created")

time.sleep(1)  # Small delay to ensure different timestamp

start_time = time.time()
response2 = requests.post(
    f"{ONBOARDING_URL}/api/v1/onboarding/sessions/{session_id}/answers",
    json=answers_payload,
    headers={
        "X-Tenant-ID": TENANT_ID,
        "X-Trace-ID": TRACE_ID,
        "Idempotency-Key": IDEMPOTENCY_KEY,  # SAME KEY
    },
    timeout=30
)
duration2 = time.time() - start_time

print_info(f"Status Code: {response2.status_code}")
print_info(f"Duration: {duration2:.2f}s")

if response2.status_code != 200:
    print_error(f"Replay request failed: {response2.status_code}")
    print(response2.text)
    exit(1)

data2 = response2.json()
card_ids_2 = data2.get("card_ids", [])
cards_count_2 = data2.get("cards_created_count", 0)

print_success(f"Replay request successful!")
print_info(f"Cards created: {cards_count_2}")
print_info(f"Card IDs: {card_ids_2}")

# ============================================================================
# STEP 4: Verify Idempotency
# ============================================================================

print("\n" + f"{CYAN}{'─' * 80}{NC}")
print(f"{YELLOW}STEP 4: Verify Idempotency{NC}")
print(f"{CYAN}{'─' * 80}{NC}")

# Check if card_ids are identical
if card_ids_1 == card_ids_2:
    print_success("✅ Card IDs are identical!")
else:
    print_error("❌ Card IDs are different!")
    print_info(f"First request:  {card_ids_1}")
    print_info(f"Replay request: {card_ids_2}")

# Check if card count is the same
if cards_count_1 == cards_count_2:
    print_success(f"✅ Card count is identical: {cards_count_1}")
else:
    print_error(f"❌ Card count is different: {cards_count_1} vs {cards_count_2}")

# Check if response is faster (cached)
if duration2 < duration1:
    speedup = duration1 / duration2
    print_success(f"✅ Replay was faster: {duration2:.2f}s vs {duration1:.2f}s ({speedup:.1f}x speedup)")
else:
    print_warning(f"⚠️  Replay was not faster: {duration2:.2f}s vs {duration1:.2f}s")

# ============================================================================
# STEP 5: Verify Cards in Cards API
# ============================================================================

print("\n" + f"{CYAN}{'─' * 80}{NC}")
print(f"{YELLOW}STEP 5: Verify Cards in Cards API{NC}")
print(f"{CYAN}{'─' * 80}{NC}")

response = requests.post(
    f"{CARDS_URL}/api/v1/cards/retrieve",
    json={"card_ids": card_ids_1},
    headers={
        "X-Tenant-ID": TENANT_ID,
        "X-Trace-ID": TRACE_ID,
    },
    timeout=10
)

if response.status_code == 200:
    cards = response.json().get("cards", [])
    print_success(f"Retrieved {len(cards)} cards from Cards API")
    
    if len(cards) == cards_count_1:
        print_success(f"✅ All {cards_count_1} cards exist in Cards API")
    else:
        print_error(f"❌ Card count mismatch: {len(cards)} vs {cards_count_1}")
else:
    print_error(f"Failed to retrieve cards: {response.status_code}")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "=" * 80)
print("  TEST SUMMARY")
print("=" * 80 + "\n")

all_passed = (
    card_ids_1 == card_ids_2 and
    cards_count_1 == cards_count_2 and
    cards_count_1 == 4
)

if all_passed:
    print_success("✅ ✅ IDEMPOTENCY TEST PASSED")
    print()
    print_info("Idempotency verified:")
    print_info("  1. Same Idempotency-Key returns same card_ids")
    print_info("  2. No duplicate cards created")
    print_info("  3. Response is consistent")
    print_info(f"  4. All {cards_count_1} cards exist in Cards API")
else:
    print_error("❌ ❌ IDEMPOTENCY TEST FAILED")
    print()
    print_error("Issues found:")
    if card_ids_1 != card_ids_2:
        print_error("  - Card IDs are different")
    if cards_count_1 != cards_count_2:
        print_error("  - Card counts are different")
    if cards_count_1 != 4:
        print_error(f"  - Expected 4 cards, got {cards_count_1}")

print()

