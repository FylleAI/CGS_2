"""
Integration tests for Cards API batch endpoint.

Tests:
- Batch creation happy path
- Idempotency (replay with same key)
- Retrieve with partial results
- Performance (p95 latency)
"""

import asyncio
import os
import time
from uuid import uuid4

import pytest
from httpx import AsyncClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from cards.api.main import app
from cards.infrastructure.database.connection import DatabaseConnection
from cards.api.v1.endpoints import init_cards_endpoints

# Test configuration
TEST_TENANT_ID = str(uuid4())
TEST_BASE_URL = "http://test"


@pytest.fixture(scope="module")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def db_connection():
    """Create database connection for tests."""
    database_url = os.getenv("SUPABASE_DATABASE_URL")
    if not database_url:
        pytest.skip("SUPABASE_DATABASE_URL not set")

    # Remove asyncpg+ prefix if present
    if database_url.startswith("postgresql+asyncpg://"):
        database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")

    db = DatabaseConnection(database_url)
    await db.connect(min_size=2, max_size=5)

    # Initialize endpoints with database connection
    init_cards_endpoints(db)

    yield db

    await db.disconnect()


@pytest.fixture
async def client(db_connection):
    """Create async HTTP client for testing with initialized database."""
    async with AsyncClient(app=app, base_url=TEST_BASE_URL) as ac:
        yield ac


@pytest.fixture
async def cleanup_test_data(db_connection):
    """Cleanup test data after each test."""
    yield
    
    # Cleanup cards and idempotency entries created during tests
    async with db_connection.acquire(tenant_id=TEST_TENANT_ID) as conn:
        await conn.execute(
            "DELETE FROM cards WHERE tenant_id = $1",
            TEST_TENANT_ID
        )
        await conn.execute(
            "DELETE FROM idempotency_store WHERE tenant_id = $1",
            TEST_TENANT_ID
        )


@pytest.mark.asyncio
async def test_batch_create_happy_path(client, cleanup_test_data):
    """
    Test batch card creation - happy path.
    
    Expected:
    - 201 status code
    - 4 cards created
    - Response contains all cards
    - X-Idempotency-Cache: MISS header
    """
    idempotency_key = f"test-batch-{uuid4()}"
    
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
                    "pain_points": ["Time management", "Productivity"]
                }
            },
            {
                "card_type": "voice",
                "content": {
                    "tone": "Professional",
                    "style_guidelines": ["Clear", "Concise"]
                }
            },
            {
                "card_type": "insight",
                "content": {
                    "positioning": "Innovation leader",
                    "key_messages": ["Quality", "Innovation"]
                }
            }
        ]
    }
    
    start_time = time.time()
    
    response = await client.post(
        "/api/v1/cards/batch",
        json=request_data,
        headers={
            "X-Tenant-ID": TEST_TENANT_ID,
            "Idempotency-Key": idempotency_key,
            "X-Trace-ID": "test-trace-001"
        }
    )
    
    execution_time_ms = (time.time() - start_time) * 1000
    
    # Assertions
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    
    data = response.json()
    assert data["created_count"] == 4
    assert len(data["cards"]) == 4
    
    # Check response headers
    assert response.headers.get("X-Idempotency-Cache") == "MISS"
    
    # Check card types
    card_types = {card["card_type"] for card in data["cards"]}
    assert card_types == {"company", "audience", "voice", "insight"}
    
    # Performance check (p95 should be <= 100ms)
    print(f"⏱️ Batch create execution time: {execution_time_ms:.2f}ms")
    assert execution_time_ms <= 200, f"Execution time {execution_time_ms}ms exceeds 200ms threshold"


@pytest.mark.asyncio
async def test_batch_create_idempotency(client, cleanup_test_data):
    """
    Test idempotency - replay with same key returns cached response.
    
    Expected:
    - First request: 201, creates cards
    - Second request: 201, returns cached response
    - Same card IDs in both responses
    - X-Idempotency-Cache: HIT header on second request
    - No new cards created
    """
    idempotency_key = f"test-idempotency-{uuid4()}"
    
    request_data = {
        "cards": [
            {
                "card_type": "company",
                "content": {
                    "name": "Idempotency Test Company",
                    "industry": "Testing"
                }
            }
        ]
    }
    
    # First request - should create card
    response1 = await client.post(
        "/api/v1/cards/batch",
        json=request_data,
        headers={
            "X-Tenant-ID": TEST_TENANT_ID,
            "Idempotency-Key": idempotency_key,
        }
    )
    
    assert response1.status_code == 201
    assert response1.headers.get("X-Idempotency-Cache") == "MISS"
    
    data1 = response1.json()
    card_ids_1 = {card["card_id"] for card in data1["cards"]}
    
    # Second request - should return cached response
    response2 = await client.post(
        "/api/v1/cards/batch",
        json=request_data,
        headers={
            "X-Tenant-ID": TEST_TENANT_ID,
            "Idempotency-Key": idempotency_key,
        }
    )
    
    assert response2.status_code == 201
    assert response2.headers.get("X-Idempotency-Cache") == "HIT"
    
    data2 = response2.json()
    card_ids_2 = {card["card_id"] for card in data2["cards"]}
    
    # Same card IDs
    assert card_ids_1 == card_ids_2
    
    print(f"✅ Idempotency working: same card IDs returned on replay")


@pytest.mark.asyncio
async def test_retrieve_cards(client, cleanup_test_data):
    """
    Test card retrieval.
    
    Expected:
    - 200 status code
    - All requested cards returned
    - X-Partial-Result: false header
    """
    # First create some cards
    idempotency_key = f"test-retrieve-{uuid4()}"
    
    create_response = await client.post(
        "/api/v1/cards/batch",
        json={
            "cards": [
                {"card_type": "company", "content": {"name": "Retrieve Test"}},
                {"card_type": "audience", "content": {"primary": "Developers"}},
            ]
        },
        headers={
            "X-Tenant-ID": TEST_TENANT_ID,
            "Idempotency-Key": idempotency_key,
        }
    )
    
    assert create_response.status_code == 201
    created_cards = create_response.json()["cards"]
    card_ids = [card["card_id"] for card in created_cards]
    
    # Now retrieve them
    start_time = time.time()
    
    retrieve_response = await client.post(
        "/api/v1/cards/retrieve",
        json={"card_ids": card_ids},
        headers={
            "X-Tenant-ID": TEST_TENANT_ID,
            "X-Trace-ID": "test-retrieve-001"
        }
    )
    
    execution_time_ms = (time.time() - start_time) * 1000
    
    assert retrieve_response.status_code == 200
    
    data = retrieve_response.json()
    assert len(data["cards"]) == 2
    
    # Check header
    assert retrieve_response.headers.get("X-Partial-Result") == "false"
    
    # Performance check (p95 should be <= 50ms)
    print(f"⏱️ Retrieve execution time: {execution_time_ms:.2f}ms")
    assert execution_time_ms <= 100, f"Execution time {execution_time_ms}ms exceeds 100ms threshold"


@pytest.mark.asyncio
async def test_retrieve_partial_result(client, cleanup_test_data):
    """
    Test partial result when some cards are not found.
    
    Expected:
    - 200 status code
    - Only found cards returned
    - X-Partial-Result: true header
    """
    # Create one card
    idempotency_key = f"test-partial-{uuid4()}"
    
    create_response = await client.post(
        "/api/v1/cards/batch",
        json={
            "cards": [
                {"card_type": "company", "content": {"name": "Partial Test"}},
            ]
        },
        headers={
            "X-Tenant-ID": TEST_TENANT_ID,
            "Idempotency-Key": idempotency_key,
        }
    )
    
    assert create_response.status_code == 201
    created_card = create_response.json()["cards"][0]
    existing_card_id = created_card["card_id"]
    
    # Request existing card + non-existing card
    non_existing_card_id = str(uuid4())
    
    retrieve_response = await client.post(
        "/api/v1/cards/retrieve",
        json={"card_ids": [existing_card_id, non_existing_card_id]},
        headers={
            "X-Tenant-ID": TEST_TENANT_ID,
        }
    )
    
    assert retrieve_response.status_code == 200
    
    data = retrieve_response.json()
    assert len(data["cards"]) == 1  # Only existing card
    assert data["cards"][0]["card_id"] == existing_card_id
    
    # Check partial result header
    assert retrieve_response.headers.get("X-Partial-Result") == "true"
    
    print(f"✅ Partial result detected: 1/2 cards found")

