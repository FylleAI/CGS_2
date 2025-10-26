#!/usr/bin/env python3
"""
End-to-end test for Card Service V1
Tests the complete flow: Onboarding → Card Creation → Card Retrieval
"""

import asyncio
import httpx
import json
from uuid import uuid4
from datetime import datetime

# Configuration
API_BASE_URL = "http://127.0.0.1:8001/api/v1"
TENANT_ID = "test-e2e-" + str(uuid4())[:8]

# Sample CompanySnapshot with new schema
SAMPLE_SNAPSHOT = {
    "version": "1.0",
    "snapshot_id": str(uuid4()),
    "generated_at": datetime.utcnow().isoformat(),
    "company": {
        "name": "TechCorp AI",
        "description": "Leading AI solutions provider",
        "key_offerings": ["AI Platform", "ML Services", "Data Analytics"],
        "differentiators": ["Real-time processing", "99.9% uptime", "Enterprise support"],
        "website": "https://techcorp.ai",
        "industry": "Technology",
        "headquarters": "San Francisco, CA",
        "size_range": "100-500"
    },
    "audience": {
        "primary": "Enterprise CTOs",
        "secondary": ["Data Scientists", "ML Engineers"],
        "pain_points": ["Data silos", "Model deployment complexity", "Cost optimization"],
        "desired_outcomes": ["Faster time-to-market", "Better ROI", "Reduced technical debt"]
    },
    "voice": {
        "tone": "Professional, innovative, trustworthy",
        "style_guidelines": "Clear, concise, data-driven",
        "forbidden_phrases": ["Bleeding edge", "Disruptive"],
        "cta_preferences": ["Learn more", "Get started"]
    },
    "insights": {
        "positioning": "Enterprise AI platform for data-driven decision making",
        "key_messages": ["Accelerate AI adoption", "Reduce deployment time", "Enterprise-grade security"],
        "recent_news": ["Series B funding", "New partnership with AWS"],
        "competitors": ["DataRobot", "H2O", "Databricks"]
    },
    "clarifying_questions": [],
    "clarifying_answers": {},
    "source_metadata": []
}


async def test_card_creation():
    """Test card creation from snapshot"""
    print("\n" + "="*60)
    print("TEST 1: Create Cards from Snapshot")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        # Create cards from snapshot
        response = await client.post(
            f"{API_BASE_URL}/cards/onboarding/create-from-snapshot",
            params={"tenant_id": TENANT_ID},
            json=SAMPLE_SNAPSHOT,
            timeout=30.0
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 201:
            cards = response.json()
            print(f"✅ Created {len(cards)} cards")
            
            for card in cards:
                print(f"  - {card['card_type'].upper()}: {card['title']}")
                print(f"    ID: {card['id']}")
                print(f"    Content keys: {list(card.get('content', {}).keys())}")
            
            return cards
        else:
            print(f"❌ Error: {response.text}")
            return None


async def test_list_cards():
    """Test listing cards"""
    print("\n" + "="*60)
    print("TEST 2: List Cards")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE_URL}/cards",
            params={"tenant_id": TENANT_ID},
            timeout=30.0
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            cards = response.json()
            print(f"✅ Retrieved {len(cards)} cards")
            
            for card in cards:
                print(f"  - {card['card_type'].upper()}: {card['title']}")
            
            return cards
        else:
            print(f"❌ Error: {response.text}")
            return None


async def test_get_card_by_id(card_id: str):
    """Test getting a specific card"""
    print("\n" + "="*60)
    print(f"TEST 3: Get Card by ID ({card_id})")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE_URL}/cards/{card_id}",
            params={"tenant_id": TENANT_ID},
            timeout=30.0
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            card = response.json()
            print(f"✅ Retrieved card: {card['title']}")
            print(f"   Type: {card['card_type']}")
            print(f"   Content: {json.dumps(card.get('content', {}), indent=2)}")
            
            return card
        else:
            print(f"❌ Error: {response.text}")
            return None


async def test_get_context_all():
    """Test getting all cards for context"""
    print("\n" + "="*60)
    print("TEST 4: Get All Cards for Context")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE_URL}/cards/context/all",
            params={"tenant_id": TENANT_ID},
            timeout=30.0
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            context = response.json()
            print(f"✅ Retrieved context with card types:")
            
            for card_type, cards in context.items():
                print(f"  - {card_type.upper()}: {len(cards)} card(s)")
            
            return context
        else:
            print(f"❌ Error: {response.text}")
            return None


async def test_get_rag_context():
    """Test getting RAG context text"""
    print("\n" + "="*60)
    print("TEST 5: Get RAG Context Text")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE_URL}/cards/context/rag-text",
            params={"tenant_id": TENANT_ID},
            timeout=30.0
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            context_text = data.get("context", "")
            print(f"✅ Retrieved RAG context ({len(context_text)} chars)")
            print(f"\nContext preview:\n{context_text[:500]}...")
            
            return context_text
        else:
            print(f"❌ Error: {response.text}")
            return None


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("CARD SERVICE V1 - END-TO-END TEST")
    print("="*60)
    print(f"Tenant ID: {TENANT_ID}")
    print(f"API Base URL: {API_BASE_URL}")
    
    try:
        # Test 1: Create cards
        cards = await test_card_creation()
        if not cards:
            print("\n❌ Card creation failed. Stopping tests.")
            return
        
        # Test 2: List cards
        listed_cards = await test_list_cards()
        if not listed_cards:
            print("\n❌ Card listing failed.")
        
        # Test 3: Get specific card
        if cards:
            first_card_id = cards[0]["id"]
            card = await test_get_card_by_id(first_card_id)
        
        # Test 4: Get context
        context = await test_get_context_all()
        
        # Test 5: Get RAG context
        rag_context = await test_get_rag_context()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

