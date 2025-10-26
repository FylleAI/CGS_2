"""Pipeline responsible for exporting onboarding snapshots to the card service."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import List, Optional, Protocol

from packages.contracts.cards import CardSummary
from packages.contracts.onboarding import ClarifyingAnswers, CompanySnapshot
from packages.contracts.workflows import WorkflowContext
from services.onboarding.domain.models import OnboardingSession

logger = logging.getLogger(__name__)


class CardServiceClient(Protocol):
    """Protocol representing the required card service client interface."""

    async def create_cards_from_snapshot(
        self, tenant_id: str, snapshot: CompanySnapshot
    ) -> List[dict]:
        ...


@dataclass
class CardExportResult:
    """Result of the card export pipeline."""

    cards: List[CardSummary]
    context: WorkflowContext


class CardExportPipeline:
    """Coordinate transformation and export of onboarding snapshots to cards."""

    def __init__(
        self,
        card_client: CardServiceClient,
        max_retries: int = 2,
        retry_delay_seconds: float = 1.0,
    ) -> None:
        self.card_client = card_client
        self.max_retries = max(1, max_retries)
        self.retry_delay_seconds = max(0.0, retry_delay_seconds)

    async def export(
        self,
        session: OnboardingSession,
        tenant_id: Optional[str] = None,
    ) -> CardExportResult:
        """Export the session snapshot and return created card summaries."""

        if not session.snapshot:
            logger.info("Skipping card export - session has no snapshot")
            return CardExportResult(cards=[], context=self._build_context(session, []))

        contract_snapshot = session.snapshot.to_contract()
        resolved_tenant = tenant_id or session.user_email

        last_exception: Optional[Exception] = None
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(
                    "Exporting onboarding snapshot to card service (attempt %s/%s)",
                    attempt,
                    self.max_retries,
                )
                response = await self.card_client.create_cards_from_snapshot(
                    tenant_id=resolved_tenant,
                    snapshot=contract_snapshot,
                )
                summaries = self._to_summaries(response)
                context = self._build_context(session, summaries)
                return CardExportResult(cards=summaries, context=context)
            except Exception as exc:  # pragma: no cover - network failures are external
                last_exception = exc
                logger.warning(
                    "Card export attempt %s failed: %s", attempt, exc, exc_info=True
                )
                if attempt < self.max_retries and self.retry_delay_seconds > 0:
                    await asyncio.sleep(self.retry_delay_seconds)

        assert last_exception is not None  # for mypy
        raise last_exception

    def _to_summaries(self, response: List[dict]) -> List[CardSummary]:
        """Convert raw API response to summaries."""

        summaries: List[CardSummary] = []
        for item in response:
            try:
                summaries.append(CardSummary.model_validate(item))
            except Exception:  # pragma: no cover - fallback for partial data
                summaries.append(
                    CardSummary(
                        id=item.get("id"),
                        card_type=str(item.get("card_type", "")),
                        title=item.get("title", ""),
                        summary=item.get("summary"),
                        content=item.get("content", {}),
                        metrics=item.get("metrics", {}),
                        updated_at=item.get("updated_at"),
                    )
                )
        return summaries

    def _build_context(
        self, session: OnboardingSession, cards: List[CardSummary]
    ) -> WorkflowContext:
        """Create workflow context combining snapshot, cards and metadata."""

        snapshot_contract = session.snapshot.to_contract() if session.snapshot else None
        answers = (
            snapshot_contract.clarifying_answers
            if snapshot_contract is not None
            else ClarifyingAnswers()
        )

        context = WorkflowContext(
            tenant_id=session.user_email,
            snapshot=snapshot_contract,
            cards=cards,
            clarifying_answers=answers,
            extra={
                "session_id": str(session.session_id),
                "goal": session.goal.value,
            },
        )
        return context
