#!/usr/bin/env python3
"""
End-to-End Test Script for Analytics Workflow

This script tests the complete analytics workflow:
1. Start onboarding session
2. Submit answers to clarifying questions
3. Verify CGS receives content_type="analytics"
4. Verify analytics JSON parsing
5. Verify metadata propagation to frontend
6. Verify display_type="analytics_dashboard"

Usage:
    python3 scripts/test_analytics_workflow.py [company_name]

Example:
    python3 scripts/test_analytics_workflow.py ikea
"""

import sys
import json
import time
import requests
from typing import Dict, Any, Optional

# Configuration
ONBOARDING_SERVICE_URL = "http://localhost:8001"
CGS_SERVICE_URL = "http://localhost:8000"
COMPANY_NAME = sys.argv[1] if len(sys.argv) > 1 else "ikea"

# Test answers for clarifying questions
# These will be mapped to question IDs dynamically based on question type
TEST_ANSWERS_MAP = {
    "q1": "Young families",  # Target demographic (enum)
    "q2": "Increase brand awareness",  # Primary goal (enum)
    "q3": True  # Product category focus (boolean)
}


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_success(message: str):
    """Print a success message."""
    print(f"✅ {message}")


def print_error(message: str):
    """Print an error message."""
    print(f"❌ {message}")


def print_info(message: str):
    """Print an info message."""
    print(f"ℹ️  {message}")


def print_json(data: Dict[str, Any], title: str = "Response"):
    """Print formatted JSON."""
    print(f"\n📦 {title}:")
    print(json.dumps(data, indent=2))


def step1_start_onboarding() -> Optional[tuple]:
    """Step 1: Start onboarding session."""
    print_section("STEP 1: Start Onboarding Session")

    print_info(f"Starting onboarding for company: {COMPANY_NAME}")
    print_info(f"Goal: COMPANY_ANALYTICS")

    try:
        response = requests.post(
            f"{ONBOARDING_SERVICE_URL}/api/v1/onboarding/start",
            json={
                "brand_name": COMPANY_NAME,
                "user_email": "test@example.com",
                "goal": "company_analytics"
            },
            timeout=60
        )

        if response.status_code != 201:
            print_error(f"Failed to start onboarding: {response.status_code}")
            print_json(response.json(), "Error Response")
            return None

        data = response.json()
        session_id = data.get("session_id")
        questions = data.get("clarifying_questions", [])

        print_success(f"Session created: {session_id}")
        print_info(f"Received {len(questions)} clarifying questions")

        for i, q in enumerate(questions, 1):
            print(f"  {i}. {q.get('question')}")

        return (session_id, questions)

    except Exception as e:
        print_error(f"Exception during start onboarding: {e}")
        return None


def step2_submit_answers(session_id: str, questions: list) -> bool:
    """Step 2: Submit answers to clarifying questions."""
    print_section("STEP 2: Submit Answers")

    # Build answers dict from questions
    answers_dict = {}
    for i, question in enumerate(questions):
        question_id = question.get("id")  # Use 'id' field, not 'question_id'

        # Get answer from map, or use first option if available
        if question_id in TEST_ANSWERS_MAP:
            answer_text = TEST_ANSWERS_MAP[question_id]
        elif question.get("options"):
            answer_text = question["options"][0]  # Use first option
        else:
            answer_text = "Default answer"

        answers_dict[question_id] = answer_text
        print(f"  {i+1}. [{question_id}] Q: {question.get('question')}")
        print(f"     A: {answer_text}")

    print_info(f"Submitting {len(answers_dict)} answers for session: {session_id}")

    try:
        response = requests.post(
            f"{ONBOARDING_SERVICE_URL}/api/v1/onboarding/{session_id}/answers",
            json={
                "answers": answers_dict
            },
            timeout=120  # Analytics workflow can take time
        )
        
        if response.status_code != 200:
            print_error(f"Failed to submit answers: {response.status_code}")
            print_json(response.json(), "Error Response")
            return False
        
        data = response.json()

        print_success("Answers submitted successfully")
        print_info(f"Session state: {data.get('state')}")

        # Note: CGS response will be available after workflow completes
        # We'll verify it in Step 3 after waiting for completion

        return True
        
    except Exception as e:
        print_error(f"Exception during submit answers: {e}")
        return False


def step3_verify_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Step 3: Verify session data and extract results."""
    print_section("STEP 3: Verify Session Data")
    
    print_info(f"Fetching session: {session_id}")
    
    try:
        response = requests.get(
            f"{ONBOARDING_SERVICE_URL}/api/v1/onboarding/{session_id}",
            timeout=30
        )
        
        if response.status_code != 200:
            print_error(f"Failed to fetch session: {response.status_code}")
            return None
        
        data = response.json()
        
        print_success("Session fetched successfully")
        
        # Extract key fields
        state = data.get("state")
        cgs_response = data.get("cgs_response", {})
        content = cgs_response.get("content", {})
        
        print_info(f"Session state: {state}")

        # Verify state (onboarding service uses 'done' instead of 'completed')
        if state not in ["completed", "done"]:
            print_error(f"Expected state 'completed' or 'done', got '{state}'")
            return None
        
        print_success("Session state is 'completed'")
        
        return data
        
    except Exception as e:
        print_error(f"Exception during verify session: {e}")
        return None


def step4_verify_content_type(session_data: Dict[str, Any]) -> bool:
    """Step 4: Verify content_type was correctly passed."""
    print_section("STEP 4: Verify Content Type")

    cgs_response = session_data.get("cgs_response", {})
    content = cgs_response.get("content", {})

    # Debug: Print full CGS response structure
    print_info("CGS Response structure:")
    print_json(cgs_response, "CGS Response")

    # Check display_type
    display_type = content.get("display_type")

    print_info(f"Display type: {display_type}")

    if display_type != "analytics_dashboard":
        print_error(f"Expected display_type='analytics_dashboard', got '{display_type}'")
        # Check if it's in metadata instead
        metadata = content.get("metadata", {})
        metadata_display_type = metadata.get("display_type")
        print_info(f"Metadata display_type: {metadata_display_type}")
        return False

    print_success("Display type is 'analytics_dashboard'")

    return True


def step5_verify_analytics_data(session_data: Dict[str, Any]) -> bool:
    """Step 5: Verify analytics_data structure."""
    print_section("STEP 5: Verify Analytics Data")
    
    cgs_response = session_data.get("cgs_response", {})
    content = cgs_response.get("content", {})
    analytics_data = content.get("analytics_data")
    
    if not analytics_data:
        print_error("No analytics_data found in content")
        return False
    
    print_success("Analytics data found")
    
    # Verify required keys
    required_keys = ["company_score", "content_opportunities", "optimization_insights"]
    missing_keys = [k for k in required_keys if k not in analytics_data]
    
    if missing_keys:
        print_error(f"Missing required keys: {missing_keys}")
        return False
    
    print_success(f"All required keys present: {required_keys}")
    
    # Print structure
    print_info("Analytics data structure:")
    for key in required_keys:
        value = analytics_data.get(key)
        if isinstance(value, dict):
            print(f"  • {key}: {len(value)} fields")
        elif isinstance(value, list):
            print(f"  • {key}: {len(value)} items")
        else:
            print(f"  • {key}: {type(value).__name__}")
    
    # Print sample data
    print_json(analytics_data, "Analytics Data (Full)")
    
    return True


def step6_verify_metadata(session_data: Dict[str, Any]) -> bool:
    """Step 6: Verify metadata propagation."""
    print_section("STEP 6: Verify Metadata Propagation")
    
    cgs_response = session_data.get("cgs_response", {})
    metadata = cgs_response.get("metadata", {})
    
    print_info(f"Metadata keys: {list(metadata.keys())}")
    
    # Check display_type in metadata
    display_type = metadata.get("display_type")
    if display_type != "analytics_dashboard":
        print_error(f"Metadata display_type should be 'analytics_dashboard', got '{display_type}'")
        return False
    
    print_success("Metadata contains correct display_type")
    
    # Check analytics_data in metadata
    analytics_data = metadata.get("analytics_data")
    if not analytics_data:
        print_error("Metadata missing analytics_data")
        return False
    
    print_success("Metadata contains analytics_data")
    
    return True


def main():
    """Run the complete end-to-end test."""
    print_section(f"🧪 ANALYTICS WORKFLOW END-TO-END TEST")
    print_info(f"Company: {COMPANY_NAME}")
    print_info(f"Onboarding Service: {ONBOARDING_SERVICE_URL}")
    print_info(f"CGS Service: {CGS_SERVICE_URL}")
    
    # Step 1: Start onboarding
    result = step1_start_onboarding()
    if not result:
        print_error("Test failed at Step 1")
        sys.exit(1)

    session_id, questions = result

    # Wait a bit for processing
    time.sleep(2)

    # Step 2: Submit answers
    if not step2_submit_answers(session_id, questions):
        print_error("Test failed at Step 2")
        sys.exit(1)
    
    # Wait for CGS workflow to complete
    print_info("Waiting for CGS workflow to complete...")
    time.sleep(5)
    
    # Step 3: Verify session
    session_data = step3_verify_session(session_id)
    if not session_data:
        print_error("Test failed at Step 3")
        sys.exit(1)
    
    # Step 4: Verify content_type
    if not step4_verify_content_type(session_data):
        print_error("Test failed at Step 4")
        sys.exit(1)
    
    # Step 5: Verify analytics_data
    if not step5_verify_analytics_data(session_data):
        print_error("Test failed at Step 5")
        sys.exit(1)
    
    # Step 6: Verify metadata
    if not step6_verify_metadata(session_data):
        print_error("Test failed at Step 6")
        sys.exit(1)
    
    # Final summary
    print_section("🎉 TEST COMPLETED SUCCESSFULLY!")
    print_success("All steps passed")
    print_info(f"Session ID: {session_id}")
    print_info(f"View results at: http://localhost:3001")
    print("\n")


if __name__ == "__main__":
    main()

