"""Unit tests for CardRepository.

Tests:
- Content hash computation
- Card creation
- Card retrieval
- Card listing with filters
- Soft delete
- Batch creation
- Row-Level Security (tenant isolation)
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
import hashlib
import json
from uuid import UUID, uuid4
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from cards.domain.models import Card, CardCreate, CardFilter, CardType
from cards.infrastructure.repositories.card_repository import CardRepository
from cards.infrastructure.database.connection import DatabaseConnection


class TestCardRepository:
    """Test suite for CardRepository."""
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database connection."""
        db = MagicMock(spec=DatabaseConnection)
        return db
    
    @pytest.fixture
    def repository(self, mock_db):
        """Create a CardRepository instance with mock database."""
        return CardRepository(mock_db)
    
    @pytest.fixture
    def tenant_id(self):
        """Sample tenant ID."""
        return UUID("123e4567-e89b-12d3-a456-426614174000")
    
    @pytest.fixture
    def card_data(self, tenant_id):
        """Sample card creation data."""
        return CardCreate(
            tenant_id=tenant_id,
            card_type=CardType.COMPANY,
            content={
                "name": "Acme Corp",
                "domain": "acme.com",
                "industry": "Technology",
                "description": "Leading AI solutions provider"
            },
            source_session_id=UUID("550e8400-e29b-41d4-a716-446655440000"),
            created_by="onboarding-api"
        )
    
    def test_compute_content_hash(self, repository):
        """Test content hash computation."""
        content1 = {"name": "Acme", "domain": "acme.com"}
        content2 = {"domain": "acme.com", "name": "Acme"}  # Different order
        content3 = {"name": "Acme", "domain": "different.com"}
        
        hash1 = repository._compute_content_hash(content1)
        hash2 = repository._compute_content_hash(content2)
        hash3 = repository._compute_content_hash(content3)
        
        # Same content, different order -> same hash
        assert hash1 == hash2
        
        # Different content -> different hash
        assert hash1 != hash3
        
        # Hash is SHA-256 (64 hex characters)
        assert len(hash1) == 64
        assert all(c in "0123456789abcdef" for c in hash1)
    
    @pytest.mark.asyncio
    async def test_create_card(self, repository, mock_db, card_data, tenant_id):
        """Test card creation."""
        # Mock database response
        card_id = uuid4()
        now = datetime.now()
        
        mock_conn = AsyncMock()
        mock_conn.fetchrow = AsyncMock(return_value={
            "card_id": card_id,
            "tenant_id": tenant_id,
            "card_type": "company",
            "content": json.dumps(card_data.content),
            "content_hash": repository._compute_content_hash(card_data.content),
            "source_session_id": card_data.source_session_id,
            "created_by": "onboarding-api",
            "is_active": True,
            "deleted_at": None,
            "created_at": now,
            "updated_at": now,
        })
        
        mock_db.acquire = AsyncMock()
        mock_db.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_db.acquire.return_value.__aexit__ = AsyncMock(return_value=None)
        
        # Create card
        card = await repository.create(card_data)
        
        # Verify result
        assert card.card_id == card_id
        assert card.tenant_id == tenant_id
        assert card.card_type == CardType.COMPANY
        assert card.content == card_data.content
        assert card.is_active is True
        assert card.deleted_at is None
        
        # Verify database was called with tenant_id for RLS
        mock_db.acquire.assert_called_once_with(tenant_id=str(tenant_id))
    
    @pytest.mark.asyncio
    async def test_get_card(self, repository, mock_db, tenant_id):
        """Test card retrieval."""
        card_id = uuid4()
        now = datetime.now()
        content = {"name": "Acme Corp"}
        
        mock_conn = AsyncMock()
        mock_conn.fetchrow = AsyncMock(return_value={
            "card_id": card_id,
            "tenant_id": tenant_id,
            "card_type": "company",
            "content": json.dumps(content),
            "content_hash": "abc123",
            "source_session_id": None,
            "created_by": "test",
            "is_active": True,
            "deleted_at": None,
            "created_at": now,
            "updated_at": now,
        })
        
        mock_db.acquire = AsyncMock()
        mock_db.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_db.acquire.return_value.__aexit__ = AsyncMock(return_value=None)
        
        # Get card
        card = await repository.get(card_id, tenant_id)
        
        # Verify result
        assert card is not None
        assert card.card_id == card_id
        assert card.content == content
        
        # Verify RLS was applied
        mock_db.acquire.assert_called_once_with(tenant_id=str(tenant_id))
    
    @pytest.mark.asyncio
    async def test_get_card_not_found(self, repository, mock_db, tenant_id):
        """Test card retrieval when card doesn't exist."""
        card_id = uuid4()
        
        mock_conn = AsyncMock()
        mock_conn.fetchrow = AsyncMock(return_value=None)
        
        mock_db.acquire = AsyncMock()
        mock_db.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_db.acquire.return_value.__aexit__ = AsyncMock(return_value=None)
        
        # Get card
        card = await repository.get(card_id, tenant_id)
        
        # Verify result
        assert card is None
    
    @pytest.mark.asyncio
    async def test_list_cards(self, repository, mock_db, tenant_id):
        """Test card listing with filters."""
        now = datetime.now()
        
        mock_conn = AsyncMock()
        mock_conn.fetch = AsyncMock(return_value=[
            {
                "card_id": uuid4(),
                "tenant_id": tenant_id,
                "card_type": "company",
                "content": json.dumps({"name": "Acme"}),
                "content_hash": "hash1",
                "source_session_id": None,
                "created_by": "test",
                "is_active": True,
                "deleted_at": None,
                "created_at": now,
                "updated_at": now,
            },
            {
                "card_id": uuid4(),
                "tenant_id": tenant_id,
                "card_type": "company",
                "content": json.dumps({"name": "Beta"}),
                "content_hash": "hash2",
                "source_session_id": None,
                "created_by": "test",
                "is_active": True,
                "deleted_at": None,
                "created_at": now,
                "updated_at": now,
            },
        ])
        
        mock_db.acquire = AsyncMock()
        mock_db.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_db.acquire.return_value.__aexit__ = AsyncMock(return_value=None)
        
        # List cards
        filter_criteria = CardFilter(
            tenant_id=tenant_id,
            card_type=CardType.COMPANY,
            is_active=True,
            limit=100,
            offset=0
        )
        
        cards = await repository.list(filter_criteria)
        
        # Verify result
        assert len(cards) == 2
        assert all(card.card_type == CardType.COMPANY for card in cards)
        
        # Verify RLS was applied
        mock_db.acquire.assert_called_once_with(tenant_id=str(tenant_id))
    
    @pytest.mark.asyncio
    async def test_soft_delete(self, repository, mock_db, tenant_id):
        """Test soft delete."""
        card_id = uuid4()
        
        mock_conn = AsyncMock()
        mock_conn.fetchrow = AsyncMock(return_value={"card_id": card_id})
        
        mock_db.acquire = AsyncMock()
        mock_db.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_db.acquire.return_value.__aexit__ = AsyncMock(return_value=None)
        
        # Soft delete
        result = await repository.soft_delete(card_id, tenant_id)
        
        # Verify result
        assert result is True
        
        # Verify RLS was applied
        mock_db.acquire.assert_called_once_with(tenant_id=str(tenant_id))
    
    @pytest.mark.asyncio
    async def test_soft_delete_not_found(self, repository, mock_db, tenant_id):
        """Test soft delete when card doesn't exist."""
        card_id = uuid4()
        
        mock_conn = AsyncMock()
        mock_conn.fetchrow = AsyncMock(return_value=None)
        
        mock_db.acquire = AsyncMock()
        mock_db.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_db.acquire.return_value.__aexit__ = AsyncMock(return_value=None)
        
        # Soft delete
        result = await repository.soft_delete(card_id, tenant_id)
        
        # Verify result
        assert result is False
    
    @pytest.mark.asyncio
    async def test_batch_create(self, repository, mock_db, tenant_id):
        """Test batch card creation."""
        now = datetime.now()
        
        cards_data = [
            CardCreate(
                tenant_id=tenant_id,
                card_type=CardType.COMPANY,
                content={"name": "Acme"},
                created_by="test"
            ),
            CardCreate(
                tenant_id=tenant_id,
                card_type=CardType.AUDIENCE,
                content={"primary": "Tech Leaders"},
                created_by="test"
            ),
        ]
        
        mock_conn = AsyncMock()
        
        # Mock fetchrow to return different results for each call
        mock_conn.fetchrow = AsyncMock(side_effect=[
            {
                "card_id": uuid4(),
                "tenant_id": tenant_id,
                "card_type": "company",
                "content": json.dumps(cards_data[0].content),
                "content_hash": "hash1",
                "source_session_id": None,
                "created_by": "test",
                "is_active": True,
                "deleted_at": None,
                "created_at": now,
                "updated_at": now,
            },
            {
                "card_id": uuid4(),
                "tenant_id": tenant_id,
                "card_type": "audience",
                "content": json.dumps(cards_data[1].content),
                "content_hash": "hash2",
                "source_session_id": None,
                "created_by": "test",
                "is_active": True,
                "deleted_at": None,
                "created_at": now,
                "updated_at": now,
            },
        ])
        
        mock_db.transaction = AsyncMock()
        mock_db.transaction.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_db.transaction.return_value.__aexit__ = AsyncMock(return_value=None)
        
        # Batch create
        cards = await repository.batch_create(cards_data, tenant_id)
        
        # Verify result
        assert len(cards) == 2
        assert cards[0].card_type == CardType.COMPANY
        assert cards[1].card_type == CardType.AUDIENCE
        
        # Verify transaction was used with RLS
        mock_db.transaction.assert_called_once_with(tenant_id=str(tenant_id))

