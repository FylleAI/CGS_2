"""
Card Service API - Dependencies
Provides Supabase repository and other dependencies for card service routes
"""

import logging
import os
from typing import Optional
from functools import lru_cache

from core.card_service.infrastructure.supabase_card_repository import SupabaseCardRepository

logger = logging.getLogger(__name__)

# Global Supabase repository (created once)
_supabase_repository: Optional[SupabaseCardRepository] = None


def get_supabase_repository() -> SupabaseCardRepository:
    """
    Get or create Supabase card repository.

    Uses Supabase REST API instead of direct PostgreSQL connection
    to avoid firewall issues with port 5432.
    """
    global _supabase_repository

    if _supabase_repository is not None:
        logger.info("✅ Returning cached Supabase repository")
        return _supabase_repository

    try:
        logger.info("🔧 Creating new Supabase repository...")

        # Get Supabase credentials from environment
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")

        logger.info(f"📌 SUPABASE_URL: {supabase_url}")
        logger.info(f"📌 SUPABASE_ANON_KEY: {'SET' if supabase_key else 'NOT SET'}")

        if not supabase_url or not supabase_key:
            logger.error("❌ Supabase credentials not configured. Set SUPABASE_URL and SUPABASE_ANON_KEY")
            raise RuntimeError("Supabase credentials not configured")

        # Create repository
        _supabase_repository = SupabaseCardRepository(supabase_url, supabase_key)
        logger.info("✅ Supabase repository created successfully")
        return _supabase_repository

    except Exception as e:
        logger.error(f"❌ Failed to create Supabase repository: {type(e).__name__}: {str(e)}", exc_info=True)
        raise


async def get_card_repository() -> SupabaseCardRepository:
    """
    Get card repository for dependency injection.

    Usage in routes:
        @router.get("/cards")
        async def list_cards(repo: SupabaseCardRepository = Depends(get_card_repository)):
            ...
    """
    logger.info("🔌 get_card_repository() called")
    return get_supabase_repository()

