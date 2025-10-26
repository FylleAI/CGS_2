"""Card Service integration endpoints for CGS core engine."""

from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from services.card_service.api.card_schemas import CardResponseSchema
from services.card_service.application.get_cards_for_context_use_case import (
    GetCardsForContextUseCase,
)
from services.card_service.api.dependencies import get_db_session
from services.card_service.api.utils import normalize_tenant_id

router = APIRouter(prefix="/api/v1/cards", tags=["cards-integration"])


@router.get("/context/all")
async def get_all_cards_for_context(
    tenant_id: str = Query(..., description="Tenant ID (email or UUID)"),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, List[CardResponseSchema]]:
    """Return all cards grouped by type for a tenant."""

    try:
        normalized_tenant_id = normalize_tenant_id(tenant_id)
        use_case = GetCardsForContextUseCase(session)
        cards_dict = await use_case.execute(normalized_tenant_id)

        return {
            card_type: [
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
            for card_type, cards in cards_dict.items()
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - database errors bubbled up
        raise HTTPException(status_code=500, detail="Internal server error") from exc


@router.get("/context/rag-text")
async def get_rag_context_text(
    tenant_id: str = Query(..., description="Tenant ID (email or UUID)"),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, str]:
    """Return a formatted RAG context string for the tenant cards."""

    try:
        normalized_tenant_id = normalize_tenant_id(tenant_id)
        use_case = GetCardsForContextUseCase(session)
        context_text = await use_case.get_as_rag_context(normalized_tenant_id)
        return {"context": context_text}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail="Internal server error") from exc


@router.get("/context/by-type")
async def get_cards_by_type(
    tenant_id: str = Query(..., description="Tenant ID (email or UUID)"),
    card_types: Optional[List[str]] = Query(
        None,
        description="Card types to retrieve (product, persona, campaign, topic)",
    ),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, List[CardResponseSchema]]:
    """Return cards filtered by the provided types."""

    try:
        normalized_tenant_id = normalize_tenant_id(tenant_id)
        use_case = GetCardsForContextUseCase(session)
        cards_dict = await use_case.execute(normalized_tenant_id, card_types)

        return {
            card_type: [
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
            for card_type, cards in cards_dict.items()
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail="Internal server error") from exc
