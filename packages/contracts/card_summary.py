"""CardSummary contract - shared between Card Service and other services."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class CardType(str, Enum):
    """Types of atomic cards."""
    
    PRODUCT = "product"
    PERSONA = "persona"
    CAMPAIGN = "campaign"
    TOPIC = "topic"


class CardSummary(BaseModel):
    """Summary of a card for use in workflows and frontends.
    
    This is a lightweight version of the full Card entity,
    used for communication between services.
    """
    
    id: UUID = Field(..., description="Card ID")
    tenant_id: UUID = Field(..., description="Tenant ID")
    card_type: CardType = Field(..., description="Type of card")
    title: str = Field(..., description="Card title")
    content: Dict[str, Any] = Field(default_factory=dict, description="Card content")
    
    # Metadata
    created_at: datetime = Field(..., description="When card was created")
    updated_at: datetime = Field(..., description="When card was last updated")
    is_active: bool = Field(default=True, description="Is card active?")
    
    # Relationships
    related_card_ids: list[UUID] = Field(
        default_factory=list,
        description="IDs of related cards"
    )
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "tenant_id": "550e8400-e29b-41d4-a716-446655440001",
                "card_type": "product",
                "title": "Acme Product",
                "content": {
                    "description": "Our flagship product",
                    "features": ["Feature 1", "Feature 2"],
                    "pricing": "Enterprise",
                },
                "created_at": "2025-10-26T18:00:00Z",
                "updated_at": "2025-10-26T18:00:00Z",
                "is_active": True,
                "related_card_ids": [],
            }
        }

