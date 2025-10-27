"""
Integration tests for Cards API usage tracking endpoint.

Tests usage tracking with deduplication per run.
"""

import os
from uuid import uuid4

import pytest
from httpx import AsyncClient

from cards.api.main import app
from cards.infrastructure.database import DatabaseConnection
from cards.api.v1.endpoints import init_cards_endpoints, init_usage_endpoints

# Test configuration
TENANT_ID = "123e4567-e89b-12d3-a456-426614174000"
TRACE_ID = "test-usage-001"


@pytest.fixture(scope="module")
async def db_connection():
    """Initialize database connection for tests."""
    database_url = os.getenv("SUPABASE_DATABASE_URL")
    if not database_url:
        pytest.skip("SUPABASE_DATABASE_URL not set")
    
    # Remove asyncpg+ prefix if present
    if database_url.startswith("postgresql+asyncpg://"):
        database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    
    db = DatabaseConnection(database_url, min_size=2, max_size=5)
    await db.connect()
    
    # Initialize endpoints
    init_cards_endpoints(db)
    init_usage_endpoints(db)
    
    yield db
    
    await db.disconnect()


@pytest.fixture
async def test_card_id(db_connection):
    """Create a test card and return its ID."""
    # Create a test card
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/cards/batch",
            headers={
                "X-Tenant-ID": TENANT_ID,
                "X-Trace-ID": TRACE_ID,
                "Idempotency-Key": f"test-usage-setup-{uuid4()}",
            },
            json={
                "cards": [
                    {
                        "card_type": "company",
                        "content": {
                            "name": "Test Company",
                            "domain": "test.com",
                            "industry": "Technology",
                        },
                    }
                ]
            },
        )
        
        assert response.status_code == 201
        data = response.json()
        return data["cards"][0]["card_id"]


@pytest.mark.asyncio
async def test_track_usage_happy_path(db_connection, test_card_id):
    """Test tracking card usage - happy path."""
    workflow_id = f"workflow-{uuid4()}"
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            f"/api/v1/cards/{test_card_id}/usage",
            headers={
                "X-Tenant-ID": TENANT_ID,
                "X-Trace-ID": TRACE_ID,
            },
            json={
                "workflow_id": workflow_id,
                "workflow_type": "premium_newsletter",
                "session_id": "session-123",
            },
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["card_id"] == test_card_id
        assert data["usage_count"] >= 1
        assert data["last_used_at"] is not None
        assert data["event_recorded"] is True
        
        # Check custom header
        assert response.headers.get("X-Event-Recorded") == "true"


@pytest.mark.asyncio
async def test_track_usage_deduplication(db_connection, test_card_id):
    """Test usage tracking deduplication - same workflow_id should not create duplicate events."""
    workflow_id = f"workflow-dedup-{uuid4()}"
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First usage - should record event
        response1 = await client.post(
            f"/api/v1/cards/{test_card_id}/usage",
            headers={
                "X-Tenant-ID": TENANT_ID,
                "X-Trace-ID": TRACE_ID,
            },
            json={
                "workflow_id": workflow_id,
                "workflow_type": "premium_newsletter",
            },
        )
        
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["event_recorded"] is True
        assert response1.headers.get("X-Event-Recorded") == "true"
        
        usage_count_1 = data1["usage_count"]
        
        # Second usage - same workflow_id, should NOT record event (deduplication)
        response2 = await client.post(
            f"/api/v1/cards/{test_card_id}/usage",
            headers={
                "X-Tenant-ID": TENANT_ID,
                "X-Trace-ID": TRACE_ID,
            },
            json={
                "workflow_id": workflow_id,  # Same workflow_id
                "workflow_type": "premium_newsletter",
            },
        )
        
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["event_recorded"] is False  # Duplicate detected
        assert response2.headers.get("X-Event-Recorded") == "false"
        
        # Usage count should still increment (even for duplicates)
        usage_count_2 = data2["usage_count"]
        assert usage_count_2 > usage_count_1


@pytest.mark.asyncio
async def test_track_usage_different_workflows(db_connection, test_card_id):
    """Test usage tracking with different workflow_ids - should record separate events."""
    workflow_id_1 = f"workflow-1-{uuid4()}"
    workflow_id_2 = f"workflow-2-{uuid4()}"
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First workflow
        response1 = await client.post(
            f"/api/v1/cards/{test_card_id}/usage",
            headers={
                "X-Tenant-ID": TENANT_ID,
                "X-Trace-ID": TRACE_ID,
            },
            json={
                "workflow_id": workflow_id_1,
                "workflow_type": "premium_newsletter",
            },
        )
        
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["event_recorded"] is True
        
        # Second workflow (different workflow_id)
        response2 = await client.post(
            f"/api/v1/cards/{test_card_id}/usage",
            headers={
                "X-Tenant-ID": TENANT_ID,
                "X-Trace-ID": TRACE_ID,
            },
            json={
                "workflow_id": workflow_id_2,  # Different workflow_id
                "workflow_type": "premium_newsletter",
            },
        )
        
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["event_recorded"] is True  # New event recorded
        
        # Both should have incremented usage count
        assert data2["usage_count"] > data1["usage_count"]


@pytest.mark.asyncio
async def test_track_usage_invalid_card_id(db_connection):
    """Test usage tracking with invalid card ID."""
    invalid_card_id = str(uuid4())  # Non-existent card
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            f"/api/v1/cards/{invalid_card_id}/usage",
            headers={
                "X-Tenant-ID": TENANT_ID,
                "X-Trace-ID": TRACE_ID,
            },
            json={
                "workflow_id": f"workflow-{uuid4()}",
                "workflow_type": "premium_newsletter",
            },
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_track_usage_missing_tenant_id(db_connection, test_card_id):
    """Test usage tracking without X-Tenant-ID header."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            f"/api/v1/cards/{test_card_id}/usage",
            headers={
                "X-Trace-ID": TRACE_ID,
                # Missing X-Tenant-ID
            },
            json={
                "workflow_id": f"workflow-{uuid4()}",
                "workflow_type": "premium_newsletter",
            },
        )
        
        assert response.status_code == 422  # Validation error

