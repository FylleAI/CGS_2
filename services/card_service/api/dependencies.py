"""
Card Service API - Dependencies
Provides database session and other dependencies for card service routes
"""

from typing import AsyncGenerator, Optional
from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from services.content_workflow.infrastructure.config.settings import get_settings


# Global session maker (created once)
_async_session_maker: Optional[sessionmaker] = None


def _get_async_session_maker() -> Optional[sessionmaker]:
    """Get or create async session maker"""
    global _async_session_maker

    if _async_session_maker is not None:
        return _async_session_maker

    try:
        import os

        # Try to get Card Service database URL from environment
        db_url = os.getenv("CARD_SERVICE_DATABASE_URL")

        # Fallback to Supabase if not set
        if not db_url:
            supabase_url = os.getenv("SUPABASE_URL")
            if supabase_url:
                # Convert Supabase URL to PostgreSQL async connection string
                # Format: https://project.supabase.co -> postgresql+asyncpg://postgres:password@project.supabase.co:5432/postgres
                db_url = f"postgresql+asyncpg://postgres:postgres@{supabase_url.replace('https://', '').replace('http://', '')}:5432/postgres"

        if not db_url:
            import logging
            logger = logging.getLogger(__name__)
            logger.error("No database URL configured. Set CARD_SERVICE_DATABASE_URL or SUPABASE_URL")
            return None

        # Create async engine
        engine = create_async_engine(db_url, echo=False)

        # Create session maker
        _async_session_maker = sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

        return _async_session_maker
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to create async session maker: {str(e)}")
        return None


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session for dependency injection.
    
    Usage in routes:
        @router.get("/cards")
        async def list_cards(session: AsyncSession = Depends(get_db_session)):
            ...
    """
    session_maker = _get_async_session_maker()
    
    if session_maker is None:
        raise RuntimeError("Database session maker not initialized")
    
    session = session_maker()
    try:
        yield session
    finally:
        await session.close()

