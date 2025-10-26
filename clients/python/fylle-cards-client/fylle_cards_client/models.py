"""
Data models for Fylle Cards API.

Auto-generated from OpenAPI spec: contracts/cards-api-v1.yaml
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CardType(str, Enum):
    """Card type enum (LOCKED - from fylle-shared)."""

    COMPANY = "company"
    AUDIENCE = "audience"
    VOICE = "voice"
    INSIGHT = "insight"


class ContextCard(BaseModel):
    """Context card model."""

    card_id: UUID
    tenant_id: UUID
    card_type: CardType
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    content: Dict[str, Any]
    tags: List[str] = Field(default_factory=list)
    version: int = Field(default=1, ge=1)
    is_active: bool = True
    confidence_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    quality_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    usage_count: int = 0
    last_used_at: Optional[datetime] = None
    source_session_id: Optional[UUID] = None
    source_workflow_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    created_by: str


class CreateCardRequest(BaseModel):
    """Request to create a single card."""

    tenant_id: UUID
    card_type: CardType
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    content: Dict[str, Any]
    tags: List[str] = Field(default_factory=list)
    source_session_id: Optional[UUID] = None
    created_by: str


class CreateCardsBatchRequest(BaseModel):
    """Request to create multiple cards from CompanySnapshot."""

    tenant_id: UUID
    company_snapshot: Dict[str, Any]
    source_session_id: UUID
    created_by: str


class CardBatchResponse(BaseModel):
    """Response from batch card creation."""

    cards: List[ContextCard]
    created_count: int


class RetrieveCardsRequest(BaseModel):
    """Request to retrieve cards by IDs."""

    tenant_id: UUID
    card_ids: List[UUID] = Field(min_length=1)


class CardListResponse(BaseModel):
    """Response with list of cards."""

    cards: List[ContextCard]
    total: int
    page: Optional[int] = None
    page_size: Optional[int] = None


class TrackUsageRequest(BaseModel):
    """Request to track card usage."""

    workflow_id: Optional[UUID] = None
    workflow_type: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str
    detail: Optional[str] = None
    request_id: Optional[str] = None

