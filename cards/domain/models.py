"""Domain models for Cards API.

These models represent the core business entities for the Cards system.
They are independent of the database implementation.
"""

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID
from pydantic import BaseModel, Field
from enum import Enum


class CardType(str, Enum):
    """Card type enumeration."""
    
    COMPANY = "company"
    AUDIENCE = "audience"
    VOICE = "voice"
    INSIGHT = "insight"


class CardCreate(BaseModel):
    """Model for creating a new card."""
    
    tenant_id: UUID = Field(..., description="Tenant identifier")
    card_type: CardType = Field(..., description="Type of card")
    content: Dict[str, Any] = Field(..., description="Card content as JSON")
    source_session_id: Optional[UUID] = Field(None, description="Source onboarding session ID")
    created_by: str = Field(..., description="User or system that created the card")
    
    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "123e4567-e89b-12d3-a456-426614174000",
                "card_type": "company",
                "content": {
                    "name": "Acme Corp",
                    "domain": "acme.com",
                    "industry": "Technology",
                    "description": "Leading AI solutions provider"
                },
                "source_session_id": "550e8400-e29b-41d4-a716-446655440000",
                "created_by": "onboarding-api"
            }
        }


class CardUpdate(BaseModel):
    """Model for updating an existing card."""
    
    content: Optional[Dict[str, Any]] = Field(None, description="Updated card content")
    is_active: Optional[bool] = Field(None, description="Active status (for soft delete)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": {
                    "name": "Acme Corporation",
                    "domain": "acme.com",
                    "industry": "Technology",
                    "description": "Leading AI solutions provider - Updated"
                }
            }
        }


class Card(BaseModel):
    """Complete card model with all fields."""
    
    card_id: UUID = Field(..., description="Unique card identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")
    card_type: CardType = Field(..., description="Type of card")
    content: Dict[str, Any] = Field(..., description="Card content as JSON")
    content_hash: str = Field(..., description="SHA-256 hash of content for deduplication")
    source_session_id: Optional[UUID] = Field(None, description="Source onboarding session ID")
    created_by: str = Field(..., description="User or system that created the card")
    is_active: bool = Field(True, description="Active status (false = soft deleted)")
    deleted_at: Optional[datetime] = Field(None, description="Soft delete timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "card_id": "550e8400-e29b-41d4-a716-446655440001",
                "tenant_id": "123e4567-e89b-12d3-a456-426614174000",
                "card_type": "company",
                "content": {
                    "name": "Acme Corp",
                    "domain": "acme.com",
                    "industry": "Technology",
                    "description": "Leading AI solutions provider"
                },
                "content_hash": "a1b2c3d4e5f6...",
                "source_session_id": "550e8400-e29b-41d4-a716-446655440000",
                "created_by": "onboarding-api",
                "is_active": True,
                "deleted_at": None,
                "created_at": "2025-10-27T00:00:00Z",
                "updated_at": "2025-10-27T00:00:00Z"
            }
        }


class CardFilter(BaseModel):
    """Filter criteria for listing cards."""
    
    tenant_id: UUID = Field(..., description="Tenant identifier (required)")
    card_type: Optional[CardType] = Field(None, description="Filter by card type")
    is_active: bool = Field(True, description="Filter by active status")
    source_session_id: Optional[UUID] = Field(None, description="Filter by source session")
    limit: int = Field(100, ge=1, le=1000, description="Maximum number of results")
    offset: int = Field(0, ge=0, description="Number of results to skip")
    
    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "123e4567-e89b-12d3-a456-426614174000",
                "card_type": "company",
                "is_active": True,
                "limit": 100,
                "offset": 0
            }
        }


class CardUsageCreate(BaseModel):
    """Model for creating a card usage record."""
    
    card_id: UUID = Field(..., description="Card identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")
    workflow_id: Optional[UUID] = Field(None, description="Workflow execution ID")
    workflow_type: Optional[str] = Field(None, description="Type of workflow")
    
    class Config:
        json_schema_extra = {
            "example": {
                "card_id": "550e8400-e29b-41d4-a716-446655440001",
                "tenant_id": "123e4567-e89b-12d3-a456-426614174000",
                "workflow_id": "660e8400-e29b-41d4-a716-446655440002",
                "workflow_type": "premium_newsletter"
            }
        }


class CardUsage(BaseModel):
    """Complete card usage model."""
    
    usage_id: UUID = Field(..., description="Unique usage identifier")
    card_id: UUID = Field(..., description="Card identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")
    workflow_id: Optional[UUID] = Field(None, description="Workflow execution ID")
    workflow_type: Optional[str] = Field(None, description="Type of workflow")
    used_at: datetime = Field(..., description="Usage timestamp")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "usage_id": "770e8400-e29b-41d4-a716-446655440003",
                "card_id": "550e8400-e29b-41d4-a716-446655440001",
                "tenant_id": "123e4567-e89b-12d3-a456-426614174000",
                "workflow_id": "660e8400-e29b-41d4-a716-446655440002",
                "workflow_type": "premium_newsletter",
                "used_at": "2025-10-27T00:00:00Z"
            }
        }

