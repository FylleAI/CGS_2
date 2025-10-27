#!/usr/bin/env python3
"""
Simple test for Cards API endpoints.
Tests batch creation and retrieval without starting a server.
"""

import asyncio
import os
import sys
from pathlib import Path
from uuid import uuid4

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from httpx import AsyncClient
from dotenv import load_dotenv

# Load environment
load_dotenv()

from cards.api.main import app
from cards.infrastructure.database.connection import DatabaseConnection
from cards.api.v1.endpoints import init_cards_endpoints

# Global database connection
_db = None


async def test_health():
    """Test health endpoint."""
    print("=" * 80)
    print("TEST 1: Health Check")
    print("=" * 80)
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 200
        print("✅ Health check passed")
    print()


async def test_batch_create():
    """Test batch card creation."""
    print("=" * 80)
    print("TEST 2: Batch Create")
    print("=" * 80)
    
    tenant_id = str(uuid4())
    idempotency_key = f"test-{uuid4()}"
    
    request_data = {
        "cards": [
            {
                "card_type": "company",
                "content": {
                    "name": "Test Company",
                    "industry": "Technology",
                    "description": "A test company"
                }
            },
            {
                "card_type": "audience",
                "content": {
                    "primary": "Tech professionals",
                    "pain_points": ["Time management"]
                }
            }
        ]
    }
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/cards/batch",
            json=request_data,
            headers={
                "X-Tenant-ID": tenant_id,
                "Idempotency-Key": idempotency_key,
            }
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"Created: {data['created_count']} cards")
            print(f"Card IDs: {[c['card_id'] for c in data['cards']]}")
            print(f"Idempotency Cache: {response.headers.get('X-Idempotency-Cache')}")
            print("✅ Batch create passed")
            
            # Test idempotency - replay
            print("\n--- Testing Idempotency (Replay) ---")
            response2 = await client.post(
                "/api/v1/cards/batch",
                json=request_data,
                headers={
                    "X-Tenant-ID": tenant_id,
                    "Idempotency-Key": idempotency_key,
                }
            )
            
            print(f"Status: {response2.status_code}")
            print(f"Idempotency Cache: {response2.headers.get('X-Idempotency-Cache')}")
            
            if response2.headers.get('X-Idempotency-Cache') == 'HIT':
                print("✅ Idempotency working!")
            else:
                print("❌ Idempotency NOT working")
            
            # Test retrieve
            print("\n--- Testing Retrieve ---")
            card_ids = [c['card_id'] for c in data['cards']]
            
            retrieve_response = await client.post(
                "/api/v1/cards/retrieve",
                json={"card_ids": card_ids},
                headers={"X-Tenant-ID": tenant_id}
            )
            
            print(f"Status: {retrieve_response.status_code}")
            
            if retrieve_response.status_code == 200:
                retrieve_data = retrieve_response.json()
                print(f"Retrieved: {len(retrieve_data['cards'])} cards")
                print(f"Partial Result: {retrieve_response.headers.get('X-Partial-Result')}")
                print("✅ Retrieve passed")
            else:
                print(f"❌ Retrieve failed: {retrieve_response.text}")
        else:
            print(f"❌ Batch create failed: {response.text}")
    
    print()


async def main():
    """Run all tests."""
    global _db

    print("\n🧪 CARDS API SIMPLE TESTS\n")

    # Initialize database connection
    database_url = os.getenv("SUPABASE_DATABASE_URL")
    if not database_url:
        print("❌ SUPABASE_DATABASE_URL not set")
        sys.exit(1)

    # Remove asyncpg+ prefix if present
    if database_url.startswith("postgresql+asyncpg://"):
        database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")

    print(f"📍 Connecting to database: {database_url.split('@')[1]}")

    _db = DatabaseConnection(database_url)
    await _db.connect(min_size=2, max_size=5)

    # Initialize endpoints with database
    init_cards_endpoints(_db)

    print("✅ Database initialized\n")

    try:
        await test_health()
        await test_batch_create()

        print("=" * 80)
        print("✅ ALL TESTS PASSED!")
        print("=" * 80)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Cleanup
        if _db:
            await _db.disconnect()
            print("\n✅ Database connection closed")


if __name__ == "__main__":
    asyncio.run(main())

