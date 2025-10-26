"""
Card Service API - Dependencies
Provides database session and other dependencies for card service routes
"""

from typing import AsyncGenerator, Optional
from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from core.infrastructure.config.settings import get_settings


# Global session maker (created once)
_async_session_maker: Optional[sessionmaker] = None


def _get_async_session_maker() -> Optional[sessionmaker]:
    """Get or create async session maker"""
    global _async_session_maker
    
    if _async_session_maker is not None:
        return _async_session_maker
    
    try:
        settings = get_settings()
        
        # Get database URL from settings (Supabase)
        db_url = settings.database_url
        if not db_url:
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

