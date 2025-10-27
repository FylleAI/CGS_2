"""
Cards API v1 Endpoints.

Implements POST /api/v1/cards/batch and POST /api/v1/cards/retrieve
following OpenAPI contract.
"""

import logging
import time
from typing import List, Optional, Dict, Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, Header, Response
from pydantic import BaseModel, Field

from ....domain.models import CardCreate, Card, CardType
from ....infrastructure.repositories.card_repository import CardRepository
from ....infrastructure.repositories.idempotency_repository import IdempotencyRepository
from ....infrastructure.database.connection import DatabaseConnection

logger = logging.getLogger(__name__)

router = APIRouter()

# Global dependencies (initialized on startup)
_db: Optional[DatabaseConnection] = None


def init_cards_endpoints(db: DatabaseConnection):
    """Initialize cards endpoints with database connection."""
    global _db
    _db = db
    logger.info("✅ Cards endpoints initialized with database connection")


# Request/Response Models


class CardInput(BaseModel):
    """Input model for a single card in batch creation."""

    card_type: CardType
    content: Dict[str, Any]
    source_session_id: Optional[UUID] = None


class BatchCreateRequest(BaseModel):
    """Request model for batch card creation."""

    cards: List[CardInput] = Field(..., min_items=1, max_items=100)


class BatchCreateResponse(BaseModel):
    """Response model for batch card creation."""

    cards: List[Card]
    created_count: int


class RetrieveRequest(BaseModel):
    """Request model for card retrieval."""

    card_ids: List[UUID] = Field(..., min_items=1, max_items=100)


class RetrieveResponse(BaseModel):
    """Response model for card retrieval."""

    cards: List[Card]


# Endpoints


@router.post("/batch", response_model=BatchCreateResponse, status_code=201)
async def batch_create_cards(
    request: BatchCreateRequest,
    response: Response,
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    x_trace_id: Optional[str] = Header(None, alias="X-Trace-ID"),
):
    """
    Create multiple cards in a single atomic transaction.

    Supports idempotency: if the same Idempotency-Key is used,
    returns the cached response without creating new cards.

    Headers:
        X-Tenant-ID: Required tenant identifier
        Idempotency-Key: Required unique key for idempotency
        X-Trace-ID: Optional trace ID for distributed tracing

    Returns:
        201: Cards created successfully
        400: Invalid request
        409: Conflict (duplicate content)
        500: Internal server error
    """
    start_time = time.time()

    if not _db:
        raise HTTPException(status_code=500, detail="Database not initialized")

    try:
        tenant_id = UUID(x_tenant_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid X-Tenant-ID format")

    logger.info(
        f"📥 Batch create request: tenant={tenant_id}, cards={len(request.cards)}, "
        f"idempotency_key={idempotency_key}, trace_id={x_trace_id}"
    )

    # Initialize repositories
    card_repo = CardRepository(_db)
    idempotency_repo = IdempotencyRepository(_db)

    # Check idempotency cache
    cached_response = await idempotency_repo.get(idempotency_key, tenant_id)
    if cached_response:
        logger.info(
            f"♻️ Idempotency HIT: returning cached response for key={idempotency_key}"
        )
        # Add custom header to indicate cache hit
        response.headers["X-Idempotency-Cache"] = "HIT"
        return BatchCreateResponse(**cached_response)

    # Idempotency MISS - create cards
    logger.info(f"🆕 Idempotency MISS: creating new cards for key={idempotency_key}")

    try:
        # Prepare card data
        cards_data = [
            CardCreate(
                tenant_id=tenant_id,
                card_type=card_input.card_type,
                content=card_input.content,
                source_session_id=card_input.source_session_id,
                created_by=f"api_batch_{x_trace_id or 'unknown'}",
            )
            for card_input in request.cards
        ]

        # Create cards in atomic transaction
        created_cards = await card_repo.batch_create(cards_data, tenant_id)

        # Build response
        response_data = {
            "cards": [card.model_dump() for card in created_cards],
            "created_count": len(created_cards),
        }

        # Store in idempotency cache
        await idempotency_repo.set(idempotency_key, tenant_id, response_data, ttl_hours=24)

        execution_time_ms = int((time.time() - start_time) * 1000)
        logger.info(
            f"✅ Batch create success: created={len(created_cards)}, "
            f"time={execution_time_ms}ms, tenant={tenant_id}"
        )

        # Add custom headers
        response.headers["X-Idempotency-Cache"] = "MISS"
        response.headers["X-Execution-Time-Ms"] = str(execution_time_ms)

        return BatchCreateResponse(**response_data)

    except Exception as e:
        logger.error(f"❌ Batch create failed: {e}", exc_info=True)
        # Check if it's a duplicate content error
        if "unique constraint" in str(e).lower() or "duplicate" in str(e).lower():
            raise HTTPException(
                status_code=409,
                detail="Duplicate card content detected. Cards with identical content already exist.",
            )
        raise HTTPException(status_code=500, detail=f"Failed to create cards: {str(e)}")


@router.post("/retrieve", response_model=RetrieveResponse)
async def retrieve_cards(
    request: RetrieveRequest,
    response: Response,
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
    x_trace_id: Optional[str] = Header(None, alias="X-Trace-ID"),
):
    """
    Retrieve multiple cards by IDs.

    Returns partial results if some cards are not found.
    Sets X-Partial-Result header to 'true' if any cards are missing.

    Headers:
        X-Tenant-ID: Required tenant identifier
        X-Trace-ID: Optional trace ID for distributed tracing

    Returns:
        200: Cards retrieved successfully (may be partial)
        400: Invalid request
        500: Internal server error
    """
    start_time = time.time()

    if not _db:
        raise HTTPException(status_code=500, detail="Database not initialized")

    try:
        tenant_id = UUID(x_tenant_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid X-Tenant-ID format")

    logger.info(
        f"📥 Retrieve request: tenant={tenant_id}, card_ids={len(request.card_ids)}, "
        f"trace_id={x_trace_id}"
    )

    # Initialize repository
    card_repo = CardRepository(_db)

    try:
        # Retrieve cards
        cards = []
        for card_id in request.card_ids:
            card = await card_repo.get(card_id, tenant_id)
            if card:
                cards.append(card)

        # Check if partial result
        is_partial = len(cards) < len(request.card_ids)

        execution_time_ms = int((time.time() - start_time) * 1000)
        logger.info(
            f"✅ Retrieve success: found={len(cards)}/{len(request.card_ids)}, "
            f"partial={is_partial}, time={execution_time_ms}ms, tenant={tenant_id}"
        )

        # Add custom headers
        if is_partial:
            response.headers["X-Partial-Result"] = "true"
            logger.warning(
                f"⚠️ Partial result: {len(request.card_ids) - len(cards)} cards not found"
            )
        else:
            response.headers["X-Partial-Result"] = "false"

        response.headers["X-Execution-Time-Ms"] = str(execution_time_ms)

        return RetrieveResponse(cards=cards)

    except Exception as e:
        logger.error(f"❌ Retrieve failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve cards: {str(e)}")

