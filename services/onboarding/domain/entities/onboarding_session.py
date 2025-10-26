"""Compatibility layer mapping to onboarding domain models."""

from __future__ import annotations

from typing import Any, Dict
from uuid import UUID, uuid4

from pydantic import model_validator

from services.onboarding.domain.models import (
    OnboardingGoal,
    OnboardingSession as DomainOnboardingSession,
    SessionState,
    CompanySnapshot,
    ClarifyingQuestion,
)
from packages.contracts.onboarding import ClarifyingAnswers

LEGACY_STATUS_MAPPING = {
    "completed": SessionState.PAYLOAD_READY,
    "payload_ready": SessionState.PAYLOAD_READY,
    "ready": SessionState.PAYLOAD_READY,
    "done": SessionState.DONE,
    "finished": SessionState.DONE,
    "failed": SessionState.FAILED,
    "in_progress": SessionState.EXECUTING,
    "running": SessionState.EXECUTING,
    "pending": SessionState.CREATED,
    "created": SessionState.CREATED,
}


class OnboardingSession(DomainOnboardingSession):
    """Domain session model with backwards compatibility shims."""

    @model_validator(mode="before")
    @classmethod
    def _compat_from_legacy(cls, data: Any) -> Any:
        """Allow initializing from legacy keyword arguments."""

        if not isinstance(data, dict):
            return data

        adapted: Dict[str, Any] = dict(data)

        legacy_id = adapted.pop("id", None)
        if legacy_id is not None and "session_id" not in adapted:
            try:
                adapted["session_id"] = UUID(str(legacy_id))
            except (ValueError, TypeError):
                adapted["session_id"] = uuid4()
                metadata = dict(adapted.get("metadata") or {})
                metadata.setdefault("legacy_session_id", legacy_id)
                adapted["metadata"] = metadata

        if "company_name" in adapted and "brand_name" not in adapted:
            adapted["brand_name"] = adapted.pop("company_name")

        if "status" in adapted and "state" not in adapted:
            status_value = str(adapted.pop("status")).lower()
            adapted["state"] = LEGACY_STATUS_MAPPING.get(
                status_value, SessionState.CREATED
            )

        adapted.setdefault("goal", OnboardingGoal.CONTENT_GENERATION)

        snapshot = adapted.get("snapshot")
        if isinstance(snapshot, dict):
            adapted["snapshot"] = CompanySnapshot(**snapshot)

        return adapted


__all__ = [
    "OnboardingSession",
    "CompanySnapshot",
    "ClarifyingQuestion",
    "ClarifyingAnswers",
]
