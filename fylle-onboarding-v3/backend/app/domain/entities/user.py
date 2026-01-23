"""
User Entity for Fylle Onboarding v3
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    """User domain entity."""
    
    id: UUID
    email: EmailStr
    brand_name: Optional[str] = None
    website: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class CreateUserRequest(BaseModel):
    """Request to create a new user."""
    
    email: EmailStr
    brand_name: Optional[str] = None
    website: Optional[str] = None


class UserResponse(BaseModel):
    """User response model."""
    
    id: str
    email: str
    brand_name: Optional[str] = None
    website: Optional[str] = None
    created_at: str
    
    @classmethod
    def from_entity(cls, user: User) -> "UserResponse":
        return cls(
            id=str(user.id),
            email=user.email,
            brand_name=user.brand_name,
            website=user.website,
            created_at=user.created_at.isoformat(),
        )
