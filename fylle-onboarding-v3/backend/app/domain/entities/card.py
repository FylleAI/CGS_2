"""
Card Entity for Fylle Onboarding v3
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CardType(str, Enum):
    """Card types for company profiling."""
    
    PRODUCT = "product"
    TARGET = "target"
    CAMPAIGNS = "campaigns"
    TOPIC = "topic"
    BRAND_VOICE = "brand_voice"
    COMPETITOR = "competitor"
    PERFORMANCE = "performance"
    FEEDBACK = "feedback"


class Card(BaseModel):
    """Card domain entity."""
    
    id: UUID
    user_id: UUID
    type: CardType
    title: str
    data: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class CreateCardRequest(BaseModel):
    """Request to create a new card."""
    
    user_id: str
    type: CardType
    title: str
    data: Dict[str, Any] = Field(default_factory=dict)


class UpdateCardRequest(BaseModel):
    """Request to update a card."""
    
    title: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class CardResponse(BaseModel):
    """Card response model."""
    
    id: str
    user_id: str
    type: str
    title: str
    data: Dict[str, Any]
    created_at: str
    updated_at: str
    
    @classmethod
    def from_entity(cls, card: Card) -> "CardResponse":
        return cls(
            id=str(card.id),
            user_id=str(card.user_id),
            type=card.type.value,
            title=card.title,
            data=card.data,
            created_at=card.created_at.isoformat(),
            updated_at=card.updated_at.isoformat(),
        )


class CardsSnapshot(BaseModel):
    """Snapshot of all user's cards."""
    
    user_id: str
    generated_at: str
    cards: List[CardResponse]
    
    @classmethod
    def from_cards(cls, user_id: str, cards: List[Card]) -> "CardsSnapshot":
        return cls(
            user_id=user_id,
            generated_at=datetime.utcnow().isoformat(),
            cards=[CardResponse.from_entity(c) for c in cards],
        )


# Card type specific data schemas

class ProductCardData(BaseModel):
    """Data schema for Product cards."""
    
    value_proposition: str = ""
    features: List[str] = Field(default_factory=list)
    differentiators: List[str] = Field(default_factory=list)
    use_cases: List[str] = Field(default_factory=list)
    performance_metrics: List[Dict[str, str]] = Field(default_factory=list)


class TargetCardData(BaseModel):
    """Data schema for Target cards."""
    
    icp_name: str = ""
    description: str = ""
    pain_points: List[str] = Field(default_factory=list)
    goals: List[str] = Field(default_factory=list)
    preferred_language: str = ""
    communication_channels: List[str] = Field(default_factory=list)
    demographics: Optional[Dict[str, str]] = None


class BrandVoiceCardData(BaseModel):
    """Data schema for Brand Voice cards."""
    
    tone_description: str = ""
    style_guidelines: List[str] = Field(default_factory=list)
    dos_examples: List[str] = Field(default_factory=list)
    donts_examples: List[str] = Field(default_factory=list)
    terms_to_use: List[str] = Field(default_factory=list)
    terms_to_avoid: List[str] = Field(default_factory=list)
