"""Database connection management for Cards API.

This module provides:
- Async PostgreSQL connection pool using asyncpg
- Tenant-scoped connections with RLS (Row-Level Security)
- Connection lifecycle management
"""

import asyncpg
import os
from typing import Optional
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """
    Manages PostgreSQL connection pool with tenant isolation.
    
    Uses asyncpg for high-performance async PostgreSQL access.
    Supports Row-Level Security (RLS) via SET LOCAL app.current_tenant_id.
    """
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize database connection manager.
        
        Args:
            database_url: PostgreSQL connection string (asyncpg format)
                         If None, reads from DATABASE_URL env var
        """
        self.database_url = database_url or os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL not configured")
        
        # Convert SQLAlchemy-style URL to asyncpg format if needed
        if self.database_url.startswith("postgresql+asyncpg://"):
            self.database_url = self.database_url.replace("postgresql+asyncpg://", "postgresql://")
        
        self._pool: Optional[asyncpg.Pool] = None
        logger.info(f"📦 DatabaseConnection initialized with URL: {self._mask_password(self.database_url)}")
    
    @staticmethod
    def _mask_password(url: str) -> str:
        """Mask password in connection string for logging."""
        if "://" not in url:
            return url
        
        protocol, rest = url.split("://", 1)
        if "@" not in rest:
            return url
        
        credentials, host = rest.split("@", 1)
        if ":" in credentials:
            user, _ = credentials.split(":", 1)
            return f"{protocol}://{user}:***@{host}"
        
        return url
    
    async def connect(self, min_size: int = 5, max_size: int = 20) -> None:
        """
        Create connection pool.
        
        Args:
            min_size: Minimum number of connections in pool
            max_size: Maximum number of connections in pool
        """
        if self._pool is not None:
            logger.warning("⚠️ Connection pool already exists")
            return
        
        logger.info(f"🔌 Creating connection pool (min={min_size}, max={max_size})")
        
        self._pool = await asyncpg.create_pool(
            self.database_url,
            min_size=min_size,
            max_size=max_size,
            command_timeout=60,
        )
        
        logger.info("✅ Connection pool created successfully")
    
    async def disconnect(self) -> None:
        """Close connection pool."""
        if self._pool is None:
            logger.warning("⚠️ No connection pool to close")
            return
        
        logger.info("🔌 Closing connection pool")
        await self._pool.close()
        self._pool = None
        logger.info("✅ Connection pool closed")
    
    @asynccontextmanager
    async def acquire(self, tenant_id: Optional[str] = None):
        """
        Acquire a connection from the pool with optional tenant isolation.
        
        Args:
            tenant_id: Tenant UUID for RLS isolation (optional)
        
        Yields:
            asyncpg.Connection: Database connection
        
        Example:
            async with db.acquire(tenant_id="123e4567-...") as conn:
                result = await conn.fetch("SELECT * FROM cards")
        """
        if self._pool is None:
            raise RuntimeError("Connection pool not initialized. Call connect() first.")
        
        async with self._pool.acquire() as connection:
            # Set tenant_id for Row-Level Security if provided
            if tenant_id:
                await connection.execute(
                    "SET LOCAL app.current_tenant_id = $1",
                    tenant_id
                )
                logger.debug(f"🔒 RLS enabled for tenant: {tenant_id}")
            
            try:
                yield connection
            finally:
                # Reset tenant_id after use (optional, connection is returned to pool)
                if tenant_id:
                    await connection.execute("RESET app.current_tenant_id")
    
    @asynccontextmanager
    async def transaction(self, tenant_id: Optional[str] = None):
        """
        Acquire a connection and start a transaction with optional tenant isolation.
        
        Args:
            tenant_id: Tenant UUID for RLS isolation (optional)
        
        Yields:
            asyncpg.Connection: Database connection in transaction
        
        Example:
            async with db.transaction(tenant_id="123e4567-...") as conn:
                await conn.execute("INSERT INTO cards ...")
                await conn.execute("INSERT INTO card_usage ...")
                # Auto-commit on success, auto-rollback on exception
        """
        if self._pool is None:
            raise RuntimeError("Connection pool not initialized. Call connect() first.")
        
        async with self._pool.acquire() as connection:
            # Set tenant_id for Row-Level Security if provided
            if tenant_id:
                await connection.execute(
                    "SET LOCAL app.current_tenant_id = $1",
                    tenant_id
                )
                logger.debug(f"🔒 RLS enabled for tenant: {tenant_id}")
            
            # Start transaction
            async with connection.transaction():
                try:
                    yield connection
                finally:
                    # Reset tenant_id after use
                    if tenant_id:
                        await connection.execute("RESET app.current_tenant_id")
    
    async def execute_script(self, script_path: str) -> None:
        """
        Execute a SQL script file.
        
        Args:
            script_path: Path to SQL script file
        
        Raises:
            FileNotFoundError: If script file not found
            asyncpg.PostgresError: If SQL execution fails
        """
        if self._pool is None:
            raise RuntimeError("Connection pool not initialized. Call connect() first.")
        
        logger.info(f"📜 Executing SQL script: {script_path}")
        
        with open(script_path, "r") as f:
            script = f.read()
        
        async with self._pool.acquire() as connection:
            await connection.execute(script)
        
        logger.info(f"✅ SQL script executed successfully: {script_path}")
    
    @property
    def is_connected(self) -> bool:
        """Check if connection pool is initialized."""
        return self._pool is not None


# Global database connection instance
_db_connection: Optional[DatabaseConnection] = None


def get_db_connection() -> DatabaseConnection:
    """
    Get the global database connection instance.
    
    Returns:
        DatabaseConnection: Global database connection
    
    Raises:
        RuntimeError: If database connection not initialized
    """
    global _db_connection
    
    if _db_connection is None:
        _db_connection = DatabaseConnection()
    
    return _db_connection


async def init_database() -> None:
    """
    Initialize database connection pool.
    
    Should be called on application startup.
    """
    db = get_db_connection()
    await db.connect()


async def close_database() -> None:
    """
    Close database connection pool.
    
    Should be called on application shutdown.
    """
    global _db_connection
    
    if _db_connection is not None:
        await _db_connection.disconnect()
        _db_connection = None

