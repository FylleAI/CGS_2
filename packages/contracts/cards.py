"""Shared card service contracts."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CardSummary(BaseModel):
    """Minimal representation of a card for cross-service context."""

    id: UUID | str
    card_type: str = Field(..., description="Card type identifier (product, persona, etc.)")
    title: str
    summary: Optional[str] = None
    content: Dict[str, Any] = Field(default_factory=dict)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    updated_at: Optional[datetime] = None

    @classmethod
    def from_card(cls, card: Any) -> "CardSummary":
        """Create a summary from a card domain object or schema."""

        return cls(
            id=getattr(card, "id"),
            card_type=str(getattr(card, "card_type")),
            title=getattr(card, "title", ""),
            summary=getattr(card, "summary", None),
            content=getattr(card, "content", {}),
            metrics=getattr(card, "metrics", {}),
            updated_at=getattr(card, "updated_at", None),
        )
