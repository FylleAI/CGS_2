"""
Domain Entities for Fylle Onboarding v3
"""

from .user import User, CreateUserRequest, UserResponse
from .card import (
    Card,
    CardType,
    CreateCardRequest,
    UpdateCardRequest,
    CardResponse,
    CardsSnapshot,
    ProductCardData,
    TargetCardData,
    BrandVoiceCardData,
)
from .pack import Pack, PackResponse, DEFAULT_PACKS
from .brief import (
    Brief,
    BriefDocument,
    BriefSection,
    BrandVoiceSpec,
    EditorialStructureSpec,
    CitationRulesSpec,
    CreateBriefRequest,
    BriefQuestionRequest,
    BriefAnswersRequest,
    BriefResponse,
    BriefQuestion,
    BriefQuestionsResponse,
)

__all__ = [
    # User
    "User",
    "CreateUserRequest",
    "UserResponse",
    # Card
    "Card",
    "CardType",
    "CreateCardRequest",
    "UpdateCardRequest",
    "CardResponse",
    "CardsSnapshot",
    "ProductCardData",
    "TargetCardData",
    "BrandVoiceCardData",
    # Pack
    "Pack",
    "PackResponse",
    "DEFAULT_PACKS",
    # Brief
    "Brief",
    "BriefDocument",
    "BriefSection",
    "BrandVoiceSpec",
    "EditorialStructureSpec",
    "CitationRulesSpec",
    "CreateBriefRequest",
    "BriefQuestionRequest",
    "BriefAnswersRequest",
    "BriefResponse",
    "BriefQuestion",
    "BriefQuestionsResponse",
]
