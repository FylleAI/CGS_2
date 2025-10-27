"""Card repository for database operations.

This module provides the CardRepository class for CRUD operations on cards.
Uses asyncpg for high-performance async PostgreSQL access.
"""

import hashlib
import json
import logging
from datetime import datetime
from typing import List, Optional
from uuid import UUID

import asyncpg

from cards.domain.models import Card, CardCreate, CardFilter, CardType
from cards.infrastructure.database.connection import DatabaseConnection

logger = logging.getLogger(__name__)


class CardRepository:
    """
    Repository for card database operations.
    
    Provides CRUD operations with:
    - Tenant isolation via RLS
    - Content deduplication via hash
    - Soft delete support
    - Pagination
    """
    
    def __init__(self, db: DatabaseConnection):
        """
        Initialize card repository.
        
        Args:
            db: Database connection instance
        """
        self.db = db
    
    @staticmethod
    def _compute_content_hash(content: dict) -> str:
        """
        Compute SHA-256 hash of card content for deduplication.
        
        Args:
            content: Card content dictionary
        
        Returns:
            str: Hex-encoded SHA-256 hash
        """
        # Sort keys for consistent hashing
        content_json = json.dumps(content, sort_keys=True)
        return hashlib.sha256(content_json.encode()).hexdigest()
    
    async def create(self, card_data: CardCreate) -> Card:
        """
        Create a new card.
        
        Args:
            card_data: Card creation data
        
        Returns:
            Card: Created card with generated ID and timestamps
        
        Raises:
            asyncpg.UniqueViolationError: If duplicate card exists (same tenant, type, content_hash)
        """
        content_hash = self._compute_content_hash(card_data.content)
        
        query = """
            INSERT INTO cards (
                tenant_id, card_type, content, content_hash,
                source_session_id, created_by
            )
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING
                card_id, tenant_id, card_type, content, content_hash,
                source_session_id, created_by, is_active, deleted_at,
                created_at, updated_at
        """
        
        async with self.db.acquire(tenant_id=str(card_data.tenant_id)) as conn:
            row = await conn.fetchrow(
                query,
                card_data.tenant_id,
                card_data.card_type.value,
                json.dumps(card_data.content),
                content_hash,
                card_data.source_session_id,
                card_data.created_by,
            )
        
        logger.info(f"✅ Created card: {row['card_id']} (type={card_data.card_type.value})")
        
        return Card(
            card_id=row["card_id"],
            tenant_id=row["tenant_id"],
            card_type=CardType(row["card_type"]),
            content=json.loads(row["content"]) if isinstance(row["content"], str) else row["content"],
            content_hash=row["content_hash"],
            source_session_id=row["source_session_id"],
            created_by=row["created_by"],
            is_active=row["is_active"],
            deleted_at=row["deleted_at"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
    
    async def get(self, card_id: UUID, tenant_id: UUID) -> Optional[Card]:
        """
        Get a card by ID.
        
        Args:
            card_id: Card identifier
            tenant_id: Tenant identifier (for RLS)
        
        Returns:
            Card if found, None otherwise
        """
        query = """
            SELECT
                card_id, tenant_id, card_type, content, content_hash,
                source_session_id, created_by, is_active, deleted_at,
                created_at, updated_at
            FROM cards
            WHERE card_id = $1 AND is_active = true
        """
        
        async with self.db.acquire(tenant_id=str(tenant_id)) as conn:
            row = await conn.fetchrow(query, card_id)
        
        if row is None:
            logger.debug(f"❌ Card not found: {card_id}")
            return None
        
        logger.debug(f"✅ Retrieved card: {card_id}")
        
        return Card(
            card_id=row["card_id"],
            tenant_id=row["tenant_id"],
            card_type=CardType(row["card_type"]),
            content=json.loads(row["content"]) if isinstance(row["content"], str) else row["content"],
            content_hash=row["content_hash"],
            source_session_id=row["source_session_id"],
            created_by=row["created_by"],
            is_active=row["is_active"],
            deleted_at=row["deleted_at"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
    
    async def list(self, filter_criteria: CardFilter) -> List[Card]:
        """
        List cards with filtering and pagination.
        
        Args:
            filter_criteria: Filter and pagination criteria
        
        Returns:
            List of cards matching criteria
        """
        # Build query dynamically based on filters
        conditions = ["is_active = $1"]
        params = [filter_criteria.is_active]
        param_index = 2
        
        if filter_criteria.card_type:
            conditions.append(f"card_type = ${param_index}")
            params.append(filter_criteria.card_type.value)
            param_index += 1
        
        if filter_criteria.source_session_id:
            conditions.append(f"source_session_id = ${param_index}")
            params.append(filter_criteria.source_session_id)
            param_index += 1
        
        where_clause = " AND ".join(conditions)
        
        query = f"""
            SELECT
                card_id, tenant_id, card_type, content, content_hash,
                source_session_id, created_by, is_active, deleted_at,
                created_at, updated_at
            FROM cards
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT ${param_index} OFFSET ${param_index + 1}
        """
        
        params.extend([filter_criteria.limit, filter_criteria.offset])
        
        async with self.db.acquire(tenant_id=str(filter_criteria.tenant_id)) as conn:
            rows = await conn.fetch(query, *params)
        
        cards = [
            Card(
                card_id=row["card_id"],
                tenant_id=row["tenant_id"],
                card_type=CardType(row["card_type"]),
                content=json.loads(row["content"]) if isinstance(row["content"], str) else row["content"],
                content_hash=row["content_hash"],
                source_session_id=row["source_session_id"],
                created_by=row["created_by"],
                is_active=row["is_active"],
                deleted_at=row["deleted_at"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            for row in rows
        ]
        
        logger.info(f"✅ Listed {len(cards)} cards (limit={filter_criteria.limit}, offset={filter_criteria.offset})")
        
        return cards
    
    async def soft_delete(self, card_id: UUID, tenant_id: UUID) -> bool:
        """
        Soft delete a card (set is_active=false).
        
        Args:
            card_id: Card identifier
            tenant_id: Tenant identifier (for RLS)
        
        Returns:
            True if card was deleted, False if not found
        """
        query = """
            UPDATE cards
            SET is_active = false, deleted_at = NOW()
            WHERE card_id = $1 AND is_active = true
            RETURNING card_id
        """
        
        async with self.db.acquire(tenant_id=str(tenant_id)) as conn:
            row = await conn.fetchrow(query, card_id)
        
        if row is None:
            logger.warning(f"❌ Card not found for deletion: {card_id}")
            return False
        
        logger.info(f"✅ Soft deleted card: {card_id}")
        return True
    
    async def batch_create(self, cards_data: List[CardCreate], tenant_id: UUID) -> List[Card]:
        """
        Create multiple cards in a single transaction.
        
        Args:
            cards_data: List of card creation data
            tenant_id: Tenant identifier (for RLS and transaction)
        
        Returns:
            List of created cards
        
        Raises:
            asyncpg.UniqueViolationError: If duplicate card exists
        """
        created_cards = []
        
        async with self.db.transaction(tenant_id=str(tenant_id)) as conn:
            for card_data in cards_data:
                content_hash = self._compute_content_hash(card_data.content)
                
                query = """
                    INSERT INTO cards (
                        tenant_id, card_type, content, content_hash,
                        source_session_id, created_by
                    )
                    VALUES ($1, $2, $3, $4, $5, $6)
                    RETURNING
                        card_id, tenant_id, card_type, content, content_hash,
                        source_session_id, created_by, is_active, deleted_at,
                        created_at, updated_at
                """
                
                row = await conn.fetchrow(
                    query,
                    card_data.tenant_id,
                    card_data.card_type.value,
                    json.dumps(card_data.content),
                    content_hash,
                    card_data.source_session_id,
                    card_data.created_by,
                )
                
                created_cards.append(
                    Card(
                        card_id=row["card_id"],
                        tenant_id=row["tenant_id"],
                        card_type=CardType(row["card_type"]),
                        content=json.loads(row["content"]) if isinstance(row["content"], str) else row["content"],
                        content_hash=row["content_hash"],
                        source_session_id=row["source_session_id"],
                        created_by=row["created_by"],
                        is_active=row["is_active"],
                        deleted_at=row["deleted_at"],
                        created_at=row["created_at"],
                        updated_at=row["updated_at"],
                    )
                )
        
        logger.info(f"✅ Batch created {len(created_cards)} cards")
        
        return created_cards

