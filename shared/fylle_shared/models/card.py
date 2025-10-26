"""
Fylle Shared Card Models

Domain models for context cards and usage events.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from fylle_shared.enums import CardType


class ContextCard(BaseModel):
    """
    Context Card - Atomic unit of knowledge in Fylle system.
    
    Represents a single piece of context (company info, audience, voice, etc.)
    that can be used by workflows and agents.
    """
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

    class Config:
        json_schema_extra = {
            "example": {
                "card_id": "123e4567-e89b-12d3-a456-426614174000",
                "tenant_id": "456e7890-e89b-12d3-a456-426614174001",
                "card_type": "company",
                "title": "Acme Corp",
                "description": "Cloud CRM platform for tech companies",
                "content": {
                    "name": "Acme Corp",
                    "industry": "SaaS",
                    "description": "Cloud CRM platform"
                },
                "tags": ["SaaS", "CRM"],
                "version": 1,
                "is_active": True,
                "confidence_score": 0.95,
                "quality_score": 0.88,
                "usage_count": 42,
                "last_used_at": "2025-10-26T10:30:00Z",
                "source_session_id": "789e0123-e89b-12d3-a456-426614174002",
                "created_at": "2025-10-26T09:00:00Z",
                "updated_at": "2025-10-26T10:30:00Z",
                "created_by": "onboarding-service"
            }
        }


class CardUsageEvent(BaseModel):
    """
    Card Usage Event - Tracks when and how a card is used.
    
    Used for analytics, quality scoring, and transparency.
    """
    event_id: UUID
    card_id: UUID
    tenant_id: UUID
    workflow_id: Optional[UUID] = None
    workflow_type: Optional[str] = None
    used_at: datetime
    trace_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "abc12345-e89b-12d3-a456-426614174003",
                "card_id": "123e4567-e89b-12d3-a456-426614174000",
                "tenant_id": "456e7890-e89b-12d3-a456-426614174001",
                "workflow_id": "def67890-e89b-12d3-a456-426614174004",
                "workflow_type": "premium_newsletter",
                "used_at": "2025-10-26T10:30:00Z",
                "trace_id": "trace-abc123",
                "session_id": "session-xyz789",
                "metadata": {
                    "agent_name": "content_generator",
                    "context_position": 1
                }
            }
        }

