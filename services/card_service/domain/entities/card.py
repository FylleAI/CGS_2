"""Compatibility entities for card service tests and integrations."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from services.card_service.domain.card_types import CardType


@dataclass
class CardContent:
    """Lightweight container mirroring legacy CardContent structure."""

    def __init__(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self) -> Dict[str, Any]:
        """Return content as dictionary."""

        return {key: value for key, value in self.__dict__.items()}


@dataclass
class Card:
    """Simplified card entity used by unit tests and adapters."""

    id: UUID = field(default_factory=uuid4)
    tenant_id: str = ""
    card_type: CardType = CardType.PRODUCT
    title: str = ""
    content: CardContent = field(default_factory=CardContent)
    metrics: Dict[str, Any] = field(default_factory=dict)
    notes: str = ""
    version: int = 1
    is_active: bool = True
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    relationships: List[Any] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize card to dictionary form."""

        return {
            "id": str(self.id),
            "tenant_id": self.tenant_id,
            "card_type": self.card_type.value,
            "title": self.title,
            "content": self.content.to_dict(),
            "metrics": self.metrics,
            "notes": self.notes,
            "version": self.version,
            "is_active": self.is_active,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class CardMetadata:
    """Placeholder for legacy metadata structure."""

    data: Dict[str, Any] = field(default_factory=dict)


__all__ = [
    "Card",
    "CardType",
    "CardContent",
    "CardMetadata",
]
