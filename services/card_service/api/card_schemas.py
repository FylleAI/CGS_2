"""
Card Service API - Pydantic Schemas for Request/Response
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from services.content_workflow.card_service.domain.card_types import CardType, RelationshipType


class CreateCardRequestSchema(BaseModel):
    """Schema for creating a card"""
    
    card_type: CardType
    title: str = Field(..., min_length=1, max_length=500)
    content: Dict[str, Any]
    metrics: Dict[str, Any] = Field(default_factory=dict)
    notes: str = Field(default="", max_length=2000)


class UpdateCardRequestSchema(BaseModel):
    """Schema for updating a card"""
    
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None
    notes: Optional[str] = Field(None, max_length=2000)


class CardRelationshipSchema(BaseModel):
    """Schema for card relationship"""
    
    id: UUID
    source_card_id: UUID
    target_card_id: UUID
    relationship_type: RelationshipType
    strength: float = Field(ge=0.0, le=1.0)
    created_at: datetime

    class Config:
        use_enum_values = True


class CardResponseSchema(BaseModel):
    """Schema for card response"""
    
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
    relationships: List[CardRelationshipSchema] = Field(default_factory=list)

    class Config:
        use_enum_values = True


class CreateRelationshipRequestSchema(BaseModel):
    """Schema for creating a relationship"""
    
    target_card_id: UUID
    relationship_type: RelationshipType
    strength: float = Field(default=1.0, ge=0.0, le=1.0)

    class Config:
        use_enum_values = True


class RelationshipResponseSchema(BaseModel):
    """Schema for relationship response"""
    
    id: UUID
    source_card_id: UUID
    target_card_id: UUID
    relationship_type: RelationshipType
    strength: float
    created_at: datetime

    class Config:
        use_enum_values = True


class ErrorResponseSchema(BaseModel):
    """Schema for error response"""
    
    detail: str
    error_code: Optional[str] = None

