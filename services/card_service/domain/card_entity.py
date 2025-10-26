"""
Card Service Domain - Card Entities
"""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator

from .card_types import CardType, RelationshipType


class BaseCard(BaseModel):
    """Base card model - parent for all card types"""

    id: UUID
    tenant_id: UUID
    card_type: CardType
    title: str = Field(..., min_length=1, max_length=500)
    content: Dict[str, Any]
    metrics: Dict[str, Any] = Field(default_factory=dict)
    notes: str = Field(default="", max_length=2000)
    version: int = Field(default=1, ge=1)
    is_active: bool = Field(default=True)
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime


class ProductContent(BaseModel):
    """Content schema for ProductCard"""
    
    value_proposition: str = Field(..., min_length=1, max_length=1000)
    features: List[str] = Field(default_factory=list)
    differentiators: List[str] = Field(default_factory=list)
    use_cases: List[str] = Field(default_factory=list)
    target_market: str = Field(default="", max_length=500)


class ProductCard(BaseCard):
    """Product/Service card"""

    card_type: Literal[CardType.PRODUCT] = CardType.PRODUCT
    content: ProductContent


class PersonaContent(BaseModel):
    """Content schema for PersonaCard"""

    icp_profile: str = Field(..., min_length=1, max_length=1000)
    pain_points: List[str] = Field(default_factory=list)
    goals: List[str] = Field(default_factory=list)
    preferred_language: str = Field(default="", max_length=50)
    communication_channels: List[str] = Field(default_factory=list)
    demographics: Optional[Dict[str, Any]] = None
    psychographics: Optional[Dict[str, Any]] = None


class PersonaCard(BaseCard):
    """Persona/Target card"""

    card_type: Literal[CardType.PERSONA] = CardType.PERSONA
    content: PersonaContent


class CampaignContent(BaseModel):
    """Content schema for CampaignCard"""

    objective: str = Field(..., min_length=1, max_length=1000)
    key_messages: List[str] = Field(default_factory=list)
    tone: str = Field(default="", max_length=200)
    target_personas: List[str] = Field(default_factory=list)
    assets_produced: List[str] = Field(default_factory=list)
    results: Optional[str] = Field(default=None, max_length=2000)
    learnings: Optional[str] = Field(default=None, max_length=2000)


class CampaignCard(BaseCard):
    """Campaign/Project card"""

    card_type: Literal[CardType.CAMPAIGN] = CardType.CAMPAIGN
    content: CampaignContent


class TopicContent(BaseModel):
    """Content schema for TopicCard"""

    keywords: List[str] = Field(default_factory=list)
    angles: List[str] = Field(default_factory=list)
    related_content: List[str] = Field(default_factory=list)
    trend_status: str = Field(default="stable")  # emerging, stable, declining
    frequency: str = Field(default="", max_length=200)
    audience_interest: str = Field(default="", max_length=500)


class TopicCard(BaseCard):
    """Topic/Theme card"""

    card_type: Literal[CardType.TOPIC] = CardType.TOPIC
    content: TopicContent


# Union type for all card types
AnyCard = ProductCard | PersonaCard | CampaignCard | TopicCard


class CardRelationship(BaseModel):
    """Card relationship entity"""
    
    id: UUID
    source_card_id: UUID
    target_card_id: UUID
    relationship_type: RelationshipType
    strength: float = Field(default=1.0, ge=0.0, le=1.0)
    created_at: datetime

    class Config:
        use_enum_values = True


class CreateCardRequest(BaseModel):
    """Request model for creating a card"""
    
    card_type: CardType
    title: str = Field(..., min_length=1, max_length=500)
    content: Dict[str, Any]
    metrics: Dict[str, Any] = Field(default_factory=dict)
    notes: str = Field(default="", max_length=2000)


class UpdateCardRequest(BaseModel):
    """Request model for updating a card"""
    
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None
    notes: Optional[str] = Field(None, max_length=2000)


class CreateRelationshipRequest(BaseModel):
    """Request model for creating a relationship"""
    
    target_card_id: UUID
    relationship_type: RelationshipType
    strength: float = Field(default=1.0, ge=0.0, le=1.0)


class CardResponse(BaseModel):
    """Response model for card"""
    
    id: UUID
    tenant_id: UUID
    card_type: CardType
    title: str
    content: Dict[str, Any]
    metrics: Dict[str, Any]
    notes: str
    version: int
    is_active: bool
    created_by: Optional[UUID]
    updated_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    relationships: List[CardRelationship] = Field(default_factory=list)

    class Config:
        use_enum_values = True

