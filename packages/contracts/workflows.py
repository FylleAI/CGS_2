"""Workflow context contracts consumed by the content workflow service."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .cards import CardSummary
from .onboarding import ClarifyingAnswers, CompanySnapshot


class WorkflowContext(BaseModel):
    """Structured context passed to workflow handlers."""

    tenant_id: Optional[str] = Field(default=None, description="Identifier of the tenant")
    snapshot: Optional[CompanySnapshot] = None
    cards: List[CardSummary] = Field(default_factory=list)
    clarifying_answers: ClarifyingAnswers = Field(default_factory=ClarifyingAnswers)
    extra: Dict[str, Any] = Field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to primitive dictionary for legacy consumers."""

        return {
            "tenant_id": self.tenant_id,
            "snapshot": self.snapshot.model_dump() if self.snapshot else None,
            "cards": [card.model_dump() for card in self.cards],
            "clarifying_answers": self.clarifying_answers.to_mapping(),
            "extra": self.extra,
        }

    def merge_extra(self, **kwargs: Any) -> "WorkflowContext":
        """Return a new instance with extra data merged."""

        updated_extra = {**self.extra, **kwargs}
        return WorkflowContext(
            tenant_id=self.tenant_id,
            snapshot=self.snapshot,
            cards=self.cards,
            clarifying_answers=self.clarifying_answers,
            extra=updated_extra,
        )

    @classmethod
    def from_raw(cls, data: Dict[str, Any]) -> "WorkflowContext":
        """Construct context from raw dictionary data."""

        snapshot_data = data.get("snapshot")
        cards_data = data.get("cards", [])
        clarifying_data = data.get("clarifying_answers") or {}

        snapshot = CompanySnapshot.model_validate(snapshot_data) if snapshot_data else None
        cards = [CardSummary.model_validate(card) for card in cards_data]
        clarifying_answers = (
            ClarifyingAnswers.from_mapping(clarifying_data)
            if isinstance(clarifying_data, dict)
            else ClarifyingAnswers.model_validate(clarifying_data)
        )

        return cls(
            tenant_id=data.get("tenant_id"),
            snapshot=snapshot,
            cards=cards,
            clarifying_answers=clarifying_answers,
            extra=data.get("extra", {}),
        )
