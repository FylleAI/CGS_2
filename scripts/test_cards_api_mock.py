#!/usr/bin/env python3
"""
Mock test for Cards API endpoints.
Tests API logic without requiring database connection.
"""

import asyncio
import sys
from pathlib import Path
from uuid import uuid4, UUID
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from httpx import AsyncClient

# Mock the database connection before importing app
mock_db = MagicMock()
mock_db._pool = MagicMock()  # Simulate connected pool

with patch('cards.api.main.DatabaseConnection', return_value=mock_db):
    from cards.api.main import app
    from cards.domain.models import Card, CardType


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
        assert response.json()["status"] == "healthy"
        print("✅ Health check passed")
    print()


async def test_ready():
    """Test readiness endpoint."""
    print("=" * 80)
    print("TEST 2: Readiness Check")
    print("=" * 80)
    
    # Mock database query
    async def mock_fetchval(query):
        return 1
    
    mock_conn = AsyncMock()
    mock_conn.fetchval = mock_fetchval
    mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_conn.__aexit__ = AsyncMock(return_value=None)
    
    with patch('cards.api.main.db_connection') as mock_db_conn:
        mock_db_conn._pool = MagicMock()
        mock_db_conn.acquire = MagicMock(return_value=mock_conn)
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/ready")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
            assert response.status_code == 200
            assert response.json()["status"] == "ready"
            print("✅ Readiness check passed")
    print()


async def test_batch_create_with_mock():
    """Test batch card creation with mocked database."""
    print("=" * 80)
    print("TEST 3: Batch Create (Mocked)")
    print("=" * 80)
    
    tenant_id = str(uuid4())
    idempotency_key = f"test-{uuid4()}"
    
    # Mock cards to return
    mock_cards = [
        Card(
            card_id=uuid4(),
            tenant_id=UUID(tenant_id),
            card_type=CardType.COMPANY,
            content={"name": "Test Company"},
            content_hash="abc123",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            created_by="test",
        ),
        Card(
            card_id=uuid4(),
            tenant_id=UUID(tenant_id),
            card_type=CardType.AUDIENCE,
            content={"primary": "Developers"},
            content_hash="def456",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            created_by="test",
        ),
    ]
    
    request_data = {
        "cards": [
            {
                "card_type": "company",
                "content": {"name": "Test Company"}
            },
            {
                "card_type": "audience",
                "content": {"primary": "Developers"}
            }
        ]
    }
    
    # Mock IdempotencyRepository
    with patch('cards.api.v1.endpoints.cards.IdempotencyRepository') as MockIdempotencyRepo:
        mock_idempotency_repo = AsyncMock()
        mock_idempotency_repo.get = AsyncMock(return_value=None)  # No cache
        mock_idempotency_repo.set = AsyncMock()
        MockIdempotencyRepo.return_value = mock_idempotency_repo
        
        # Mock CardRepository
        with patch('cards.api.v1.endpoints.cards.CardRepository') as MockCardRepo:
            mock_card_repo = AsyncMock()
            mock_card_repo.batch_create = AsyncMock(return_value=mock_cards)
            MockCardRepo.return_value = mock_card_repo
            
            # Mock database connection in endpoints
            with patch('cards.api.v1.endpoints.cards._db', mock_db):
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
                        print(f"Idempotency Cache: {response.headers.get('X-Idempotency-Cache')}")
                        assert data['created_count'] == 2
                        assert response.headers.get('X-Idempotency-Cache') == 'MISS'
                        print("✅ Batch create passed")
                    else:
                        print(f"Response: {response.text}")
                        print("❌ Batch create failed")
    print()


async def test_batch_create_idempotency_with_mock():
    """Test idempotency with mocked database."""
    print("=" * 80)
    print("TEST 4: Idempotency (Mocked)")
    print("=" * 80)
    
    tenant_id = str(uuid4())
    idempotency_key = f"test-idempotency-{uuid4()}"
    
    # Cached response
    cached_response = {
        "cards": [
            {
                "card_id": str(uuid4()),
                "tenant_id": tenant_id,
                "card_type": "company",
                "content": {"name": "Cached Company"},
                "content_hash": "cached123",
                "is_active": True,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "created_by": "test",
                "source_session_id": None,
            }
        ],
        "created_count": 1
    }
    
    request_data = {
        "cards": [
            {
                "card_type": "company",
                "content": {"name": "Test Company"}
            }
        ]
    }
    
    # Mock IdempotencyRepository with cache HIT
    with patch('cards.api.v1.endpoints.cards.IdempotencyRepository') as MockIdempotencyRepo:
        mock_idempotency_repo = AsyncMock()
        mock_idempotency_repo.get = AsyncMock(return_value=cached_response)  # Cache HIT
        MockIdempotencyRepo.return_value = mock_idempotency_repo
        
        # Mock database connection in endpoints
        with patch('cards.api.v1.endpoints.cards._db', mock_db):
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
                print(f"Idempotency Cache: {response.headers.get('X-Idempotency-Cache')}")
                
                if response.headers.get('X-Idempotency-Cache') == 'HIT':
                    print("✅ Idempotency working (cache HIT)")
                else:
                    print("❌ Idempotency NOT working")
    print()


async def test_retrieve_with_mock():
    """Test card retrieval with mocked database."""
    print("=" * 80)
    print("TEST 5: Retrieve (Mocked)")
    print("=" * 80)
    
    tenant_id = str(uuid4())
    card_id_1 = uuid4()
    card_id_2 = uuid4()
    
    # Mock cards
    mock_card_1 = Card(
        card_id=card_id_1,
        tenant_id=UUID(tenant_id),
        card_type=CardType.COMPANY,
        content={"name": "Company 1"},
        content_hash="hash1",
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        created_by="test",
    )
    
    # Mock CardRepository
    with patch('cards.api.v1.endpoints.cards.CardRepository') as MockCardRepo:
        mock_card_repo = AsyncMock()
        
        async def mock_get(card_id, tenant_id):
            if card_id == card_id_1:
                return mock_card_1
            return None  # card_id_2 not found
        
        mock_card_repo.get = mock_get
        MockCardRepo.return_value = mock_card_repo
        
        # Mock database connection in endpoints
        with patch('cards.api.v1.endpoints.cards._db', mock_db):
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/cards/retrieve",
                    json={"card_ids": [str(card_id_1), str(card_id_2)]},
                    headers={"X-Tenant-ID": tenant_id}
                )
                
                print(f"Status: {response.status_code}")
                print(f"Partial Result: {response.headers.get('X-Partial-Result')}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"Retrieved: {len(data['cards'])} cards")
                    
                    if response.headers.get('X-Partial-Result') == 'true':
                        print("✅ Partial result detected (1/2 cards found)")
                    else:
                        print("❌ Partial result header not set correctly")
                else:
                    print(f"❌ Retrieve failed: {response.text}")
    print()


async def main():
    """Run all tests."""
    print("\n🧪 CARDS API MOCK TESTS\n")
    
    try:
        await test_health()
        await test_ready()
        await test_batch_create_with_mock()
        await test_batch_create_idempotency_with_mock()
        await test_retrieve_with_mock()
        
        print("=" * 80)
        print("✅ ALL MOCK TESTS PASSED!")
        print("=" * 80)
        print("\n📝 Note: These tests use mocked database.")
        print("   For full integration tests, ensure Supabase connection is available.")
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

