"""Helpers for building card context artifacts consumed by other services."""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from packages.contracts.cards import CardSummary
from packages.contracts.onboarding import ClarifyingAnswers, CompanySnapshot
from packages.contracts.workflows import WorkflowContext
from services.card_service.application.get_cards_for_context_use_case import (
    GetCardsForContextUseCase,
)
from services.card_service.api.utils import normalize_tenant_id


class CardContextProvider:
    """High level helper that returns card context in shared contract format."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.use_case = GetCardsForContextUseCase(session)

    async def get_card_summaries(
        self, tenant_id: str, card_types: Optional[Iterable[str]] = None
    ) -> Dict[str, List[CardSummary]]:
        """Return card summaries grouped by type."""

        normalized_tenant_id = normalize_tenant_id(tenant_id)
        cards = await self.use_case.execute(normalized_tenant_id, card_types)
        return {
            card_type: [CardSummary.from_card(card) for card in card_list]
            for card_type, card_list in cards.items()
        }

    async def build_workflow_context(
        self,
        tenant_id: str,
        snapshot: Optional[CompanySnapshot] = None,
        clarifying_answers: Optional[ClarifyingAnswers] = None,
    ) -> WorkflowContext:
        """Create a workflow context merging snapshot, cards and answers."""

        summaries = await self.get_card_summaries(tenant_id)
        flattened_cards = [card for cards in summaries.values() for card in cards]

        return WorkflowContext(
            tenant_id=tenant_id,
            snapshot=snapshot,
            cards=flattened_cards,
            clarifying_answers=clarifying_answers or ClarifyingAnswers(),
            extra={"card_types": list(summaries.keys())},
        )

    async def get_rag_context(self, tenant_id: str) -> str:
        """Return cards formatted as RAG context text."""

        normalized_tenant_id = normalize_tenant_id(tenant_id)
        return await self.use_case.get_as_rag_context(normalized_tenant_id)
