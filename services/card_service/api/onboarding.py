"""Onboarding integration endpoints for the card service."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from packages.contracts.onboarding import CompanySnapshot
from services.card_service.api.card_schemas import CardResponseSchema
from services.card_service.application.create_cards_from_snapshot_use_case import (
    CreateCardsFromSnapshotUseCase,
)
from services.card_service.api.dependencies import get_db_session
from services.card_service.api.utils import normalize_tenant_id

router = APIRouter(prefix="/api/v1/cards/onboarding", tags=["cards-onboarding"])


@router.post(
    "/create-from-snapshot",
    response_model=List[CardResponseSchema],
    status_code=status.HTTP_201_CREATED,
)
async def create_cards_from_snapshot(
    snapshot: CompanySnapshot,
    tenant_id: str = Query(..., description="Tenant ID (email, UUID or 'admin')"),
    session: AsyncSession = Depends(get_db_session),
) -> List[CardResponseSchema]:
    """Create atomic cards from the onboarding snapshot artifact."""

    try:
        normalized_tenant_id = normalize_tenant_id(tenant_id)
        use_case = CreateCardsFromSnapshotUseCase(session)
        cards = await use_case.execute(normalized_tenant_id, snapshot)

        return [
            CardResponseSchema(
                id=card.id,
                tenant_id=card.tenant_id,
                card_type=card.card_type,
                title=card.title,
                content=card.content,
                metrics=card.metrics,
                notes=card.notes,
                version=card.version,
                is_active=card.is_active,
                created_by=card.created_by,
                updated_by=card.updated_by,
                created_at=card.created_at,
                updated_at=card.updated_at,
                relationships=card.relationships,
            )
            for card in cards
        ]
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail="Internal server error") from exc
