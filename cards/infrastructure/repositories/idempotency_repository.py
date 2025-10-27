"""
Idempotency Repository for Cards API.

Provides persistent idempotency storage using PostgreSQL.
Ensures exactly-once semantics for batch card creation.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from uuid import UUID

from ...infrastructure.database.connection import DatabaseConnection

logger = logging.getLogger(__name__)


class IdempotencyRepository:
    """Repository for idempotency key storage and retrieval."""

    def __init__(self, db: DatabaseConnection):
        """
        Initialize idempotency repository.

        Args:
            db: Database connection instance
        """
        self.db = db

    async def get(
        self, idempotency_key: str, tenant_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached response for an idempotency key.

        Args:
            idempotency_key: Unique idempotency key
            tenant_id: Tenant ID for isolation

        Returns:
            Cached response payload if found and not expired, None otherwise
        """
        query = """
            SELECT response_payload, expires_at
            FROM idempotency_store
            WHERE idempotency_key = $1
              AND tenant_id = $2
              AND expires_at > NOW()
        """

        async with self.db.acquire(tenant_id=str(tenant_id)) as conn:
            row = await conn.fetchrow(query, idempotency_key, tenant_id)

        if row:
            logger.info(
                f"✅ Idempotency cache HIT: key={idempotency_key}, tenant={tenant_id}"
            )
            # Parse JSONB to dict
            response_payload = row["response_payload"]
            if isinstance(response_payload, str):
                response_payload = json.loads(response_payload)
            return response_payload
        else:
            logger.debug(
                f"⚪ Idempotency cache MISS: key={idempotency_key}, tenant={tenant_id}"
            )
            return None

    async def set(
        self,
        idempotency_key: str,
        tenant_id: UUID,
        response_payload: Dict[str, Any],
        ttl_hours: int = 24,
    ) -> None:
        """
        Store response payload for an idempotency key.

        Args:
            idempotency_key: Unique idempotency key
            tenant_id: Tenant ID for isolation
            response_payload: Response to cache
            ttl_hours: Time-to-live in hours (default: 24)
        """
        expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)

        query = """
            INSERT INTO idempotency_store (
                idempotency_key,
                tenant_id,
                response_payload,
                expires_at
            )
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (idempotency_key, tenant_id)
            DO UPDATE SET
                response_payload = EXCLUDED.response_payload,
                expires_at = EXCLUDED.expires_at,
                updated_at = NOW()
        """

        async with self.db.acquire(tenant_id=str(tenant_id)) as conn:
            await conn.execute(
                query,
                idempotency_key,
                tenant_id,
                json.dumps(response_payload),
                expires_at,
            )

        logger.info(
            f"💾 Idempotency stored: key={idempotency_key}, tenant={tenant_id}, ttl={ttl_hours}h"
        )

    async def delete(self, idempotency_key: str, tenant_id: UUID) -> bool:
        """
        Delete an idempotency entry.

        Args:
            idempotency_key: Unique idempotency key
            tenant_id: Tenant ID for isolation

        Returns:
            True if deleted, False if not found
        """
        query = """
            DELETE FROM idempotency_store
            WHERE idempotency_key = $1
              AND tenant_id = $2
        """

        async with self.db.acquire(tenant_id=str(tenant_id)) as conn:
            result = await conn.execute(query, idempotency_key, tenant_id)

        # Parse result like "DELETE 1" or "DELETE 0"
        deleted_count = int(result.split()[-1])
        if deleted_count > 0:
            logger.info(
                f"🗑️ Idempotency deleted: key={idempotency_key}, tenant={tenant_id}"
            )
            return True
        else:
            logger.debug(
                f"⚪ Idempotency not found: key={idempotency_key}, tenant={tenant_id}"
            )
            return False

    async def cleanup_expired(self) -> int:
        """
        Clean up expired idempotency entries.

        Returns:
            Number of entries deleted
        """
        query = """
            DELETE FROM idempotency_store
            WHERE expires_at <= NOW()
        """

        # Note: This query doesn't use RLS context since it's a maintenance operation
        # We need to temporarily disable RLS or run as superuser
        # For now, we'll skip tenant context
        async with self.db.acquire() as conn:
            result = await conn.execute(query)

        deleted_count = int(result.split()[-1])
        if deleted_count > 0:
            logger.info(f"🧹 Cleaned up {deleted_count} expired idempotency entries")
        return deleted_count

