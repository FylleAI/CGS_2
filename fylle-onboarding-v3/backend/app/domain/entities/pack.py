"""
Pack Entity for Fylle Onboarding v3
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class Pack(BaseModel):
    """Pack domain entity (e.g., Newsletter Pack, Blog Post Pack)."""
    
    id: UUID
    name: str
    display_name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    prompt_template_key: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class PackResponse(BaseModel):
    """Pack response model."""
    
    id: str
    name: str
    display_name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    is_active: bool = True
    
    @classmethod
    def from_entity(cls, pack: Pack) -> "PackResponse":
        return cls(
            id=str(pack.id),
            name=pack.name,
            display_name=pack.display_name,
            description=pack.description,
            icon=pack.icon,
            is_active=pack.is_active,
        )


# Default packs
DEFAULT_PACKS = [
    {
        "name": "newsletter",
        "display_name": "Newsletter Pack",
        "description": "Genera brief per newsletter professionali",
        "icon": "📧",
        "prompt_template_key": "brief.newsletter",
    },
    {
        "name": "blog_post",
        "display_name": "Blog Post Pack",
        "description": "Genera brief per articoli di blog",
        "icon": "📝",
        "prompt_template_key": "brief.blog_post",
    },
]
