"""
API Routes for Fylle Onboarding v3
"""

from .auth import router as auth_router
from .onboarding import router as onboarding_router
from .cards import router as cards_router
from .packs import router as packs_router
from .briefs import router as briefs_router

__all__ = [
    "auth_router",
    "onboarding_router",
    "cards_router",
    "packs_router",
    "briefs_router",
]
