"""
Onboarding API v1 - Session management and card creation.

Implements POST /api/v1/onboarding/sessions, GET /api/v1/onboarding/sessions/{id},
and POST /api/v1/onboarding/sessions/{id}/answers following OpenAPI contract.
"""

import json
import logging
import time
import uuid
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Header, Response
from fylle_cards_client import CardsClient
from fylle_cards_client.client import CardsAPIError

from api.rest.v1.models.onboarding import (
    CreateSessionRequest,
    OnboardingSessionResponse,
    SubmitAnswersRequest,
    SubmitAnswersResponse,
    SessionStatus,
    ErrorResponse,
)
from api.rest.v1.storage.session_storage import get_session_storage
from core.services.card_creation_service import CardCreationService
from core.infrastructure.metrics.onboarding_metrics import (
    onboarding_cards_created_total,
    onboarding_batch_duration_ms,
    onboarding_sessions_total,
    onboarding_sessions_completed_total,
    onboarding_errors_total,
)
from onboarding.domain.models import CompanySnapshot

logger = logging.getLogger(__name__)

router = APIRouter()

# Global instances (initialized on startup)
_cards_api_url: Optional[str] = None
_card_service: Optional[CardCreationService] = None


def init_onboarding_v1(cards_api_url: str):
    """Initialize onboarding v1 dependencies."""
    global _cards_api_url, _card_service
    _cards_api_url = cards_api_url
    _card_service = CardCreationService()
    logger.info(f"✅ Onboarding v1 initialized with Cards API URL: {cards_api_url}")


# Endpoints


@router.post("/sessions", response_model=OnboardingSessionResponse, status_code=201)
async def create_session(
    request: CreateSessionRequest,
    x_trace_id: Optional[str] = Header(None, alias="X-Trace-ID"),
) -> OnboardingSessionResponse:
    """
    Create a new onboarding session.

    Args:
        request: Session creation request
        x_trace_id: Trace ID for distributed tracing (optional)

    Returns:
        Created session

    Raises:
        400: Bad request - validation error
    """
    trace_id = x_trace_id or str(uuid.uuid4())
    tenant_id_str = str(request.tenant_id)

    logger.info(
        json.dumps({
            "event": "session_create_start",
            "trace_id": trace_id,
            "tenant_id": tenant_id_str,
            "company_domain": request.company_domain,
        })
    )

    try:
        # Generate session ID
        session_id = uuid.uuid4()

        # Create session in storage
        storage = get_session_storage()
        session = storage.create_session(
            session_id=session_id,
            tenant_id=request.tenant_id,
            company_domain=request.company_domain,
            user_email=request.user_email,
        )

        # Metrics
        onboarding_sessions_total.labels(tenant_id=tenant_id_str).inc()

        logger.info(
            json.dumps({
                "event": "session_created",
                "trace_id": trace_id,
                "tenant_id": tenant_id_str,
                "session_id": str(session_id),
            })
        )

        return session

    except Exception as e:
        logger.error(
            json.dumps({
                "event": "session_create_error",
                "trace_id": trace_id,
                "tenant_id": tenant_id_str,
                "error": str(e),
            })
        )
        onboarding_errors_total.labels(tenant_id=tenant_id_str, error_type="session_create").inc()
        raise HTTPException(
            status_code=500,
            detail={"error": "InternalServerError", "detail": str(e), "request_id": trace_id},
        )


@router.get("/sessions/{session_id}", response_model=OnboardingSessionResponse)
async def get_session(
    session_id: UUID,
    x_trace_id: Optional[str] = Header(None, alias="X-Trace-ID"),
) -> OnboardingSessionResponse:
    """
    Get an onboarding session by ID.

    Args:
        session_id: Session ID
        x_trace_id: Trace ID for distributed tracing (optional)

    Returns:
        Session details

    Raises:
        404: Session not found
    """
    trace_id = x_trace_id or str(uuid.uuid4())
    logger.info(f"🔍 Getting session {session_id} (trace_id={trace_id})")

    storage = get_session_storage()
    session = storage.get_session(session_id)

    if not session:
        logger.warning(f"❌ Session not found: {session_id}")
        raise HTTPException(
            status_code=404,
            detail={"error": "NotFound", "detail": "Session not found", "request_id": trace_id},
        )

    return session


@router.post("/sessions/{session_id}/answers", response_model=SubmitAnswersResponse)
async def submit_answers(
    session_id: UUID,
    request: SubmitAnswersRequest,
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
    x_trace_id: Optional[str] = Header(None, alias="X-Trace-ID"),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
) -> SubmitAnswersResponse:
    """
    Submit answers and create cards.

    **v1.0 Behavior**:
    1. Validate answers
    2. Build CompanySnapshot from answers (simplified for MVP)
    3. Create 4 cards using CardCreationService
    4. Call Cards API to create cards (POST /cards for each)
    5. Return session with `card_ids`

    **Idempotency**: Uses session_id as idempotency key for Cards API if not provided.

    Args:
        session_id: Session ID
        request: Answers submission request
        x_tenant_id: Tenant ID (required)
        x_trace_id: Trace ID for distributed tracing (optional)
        idempotency_key: Idempotency key for safe retries (optional)

    Returns:
        Response with created card IDs

    Raises:
        400: Bad request - validation error
        404: Session not found
        502: Cards API error
    """
    trace_id = x_trace_id or str(uuid.uuid4())
    idem_key = idempotency_key or f"onboarding-{session_id}-batch"

    logger.info(f"🚀 Submitting answers for session {session_id} (trace_id={trace_id})")

    # Get session
    storage = get_session_storage()
    session = storage.get_session(session_id)

    if not session:
        logger.warning(f"❌ Session not found: {session_id}")
        raise HTTPException(
            status_code=404,
            detail={"error": "NotFound", "detail": "Session not found", "request_id": trace_id},
        )

    try:
        start_time = time.time()

        logger.info(
            json.dumps({
                "event": "answers_submit_start",
                "trace_id": trace_id,
                "tenant_id": x_tenant_id,
                "session_id": str(session_id),
                "answers_count": len(request.answers),
            })
        )

        # Build simplified CompanySnapshot from answers (MVP - no research/synthesis)
        # In production, this would come from Perplexity + Gemini
        snapshot = _build_snapshot_from_answers(session, request.answers)

        logger.info(
            json.dumps({
                "event": "snapshot_created",
                "trace_id": trace_id,
                "tenant_id": x_tenant_id,
                "session_id": str(session_id),
                "snapshot_id": str(snapshot.snapshot_id),
            })
        )

        # Call Cards API batch endpoint to create 4 cards atomically
        cards_client = CardsClient(
            base_url=_cards_api_url,
            tenant_id=x_tenant_id,
            trace_id=trace_id,
            session_id=str(session_id),
        )

        # Use batch creation with idempotency
        # Convert snapshot to dict with proper JSON serialization
        snapshot_dict = json.loads(snapshot.model_dump_json())

        try:
            batch_response = cards_client.create_cards_batch(
                company_snapshot=snapshot_dict,
                source_session_id=session_id,
                created_by="onboarding-api",
                idempotency_key=idem_key,
            )
        except CardsAPIError as e:
            logger.error(
                json.dumps({
                    "event": "cards_batch_error",
                    "trace_id": trace_id,
                    "tenant_id": x_tenant_id,
                    "session_id": str(session_id),
                    "error": str(e),
                })
            )
            # Update session to failed
            storage.update_session(session_id=session_id, status=SessionStatus.FAILED)
            onboarding_errors_total.labels(tenant_id=x_tenant_id, error_type="cards_api").inc()
            raise HTTPException(
                status_code=502,
                detail={
                    "error": "BadGateway",
                    "detail": f"Cards API error: {str(e)}",
                    "request_id": trace_id,
                },
            )

        created_card_ids = [card.card_id for card in batch_response.cards]
        created_count = batch_response.created_count

        # Check if partial creation (should be 4 cards)
        if created_count < 4:
            logger.warning(
                json.dumps({
                    "event": "cards_batch_partial",
                    "trace_id": trace_id,
                    "tenant_id": x_tenant_id,
                    "session_id": str(session_id),
                    "created_count": created_count,
                    "expected_count": 4,
                })
            )
            # Update session to partial status
            storage.update_session(
                session_id=session_id,
                status=SessionStatus.FAILED,  # Or create a PARTIAL status
                card_ids=created_card_ids,
                cards_created_count=created_count,
            )
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "PartialCreation",
                    "detail": f"Only {created_count}/4 cards created",
                    "request_id": trace_id,
                },
            )

        logger.info(
            json.dumps({
                "event": "cards_batch_created",
                "trace_id": trace_id,
                "tenant_id": x_tenant_id,
                "session_id": str(session_id),
                "created_count": created_count,
                "idempotency_key": idem_key,
            })
        )

        # Metrics per card type
        for card in batch_response.cards:
            onboarding_cards_created_total.labels(
                tenant_id=x_tenant_id,
                card_type=card.card_type.value if hasattr(card.card_type, 'value') else str(card.card_type),
            ).inc()

        # Calculate duration
        duration_ms = int((time.time() - start_time) * 1000)
        onboarding_batch_duration_ms.labels(tenant_id=x_tenant_id).observe(duration_ms)

        # Update session with created card IDs
        storage.update_session(
            session_id=session_id,
            status=SessionStatus.COMPLETED,
            card_ids=created_card_ids,
            cards_created_count=len(created_card_ids),
        )

        # Metrics
        onboarding_sessions_completed_total.labels(
            tenant_id=x_tenant_id,
            status="completed",
        ).inc()

        logger.info(
            json.dumps({
                "event": "answers_submit_complete",
                "trace_id": trace_id,
                "tenant_id": x_tenant_id,
                "session_id": str(session_id),
                "created_count": len(created_card_ids),
                "duration_ms": duration_ms,
            })
        )

        return SubmitAnswersResponse(
            session_id=session_id,
            status=SessionStatus.COMPLETED,
            card_ids=created_card_ids,
            cards_created_count=len(created_card_ids),
            updated_at=session.updated_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            json.dumps({
                "event": "answers_submit_error",
                "trace_id": trace_id,
                "tenant_id": x_tenant_id,
                "session_id": str(session_id),
                "error": str(e),
            })
        )

        # Update session to failed
        storage.update_session(session_id=session_id, status=SessionStatus.FAILED)

        # Metrics
        onboarding_errors_total.labels(tenant_id=x_tenant_id, error_type="internal").inc()
        onboarding_sessions_completed_total.labels(
            tenant_id=x_tenant_id,
            status="failed",
        ).inc()

        raise HTTPException(
            status_code=500,
            detail={"error": "InternalServerError", "detail": str(e), "request_id": trace_id},
        )


def _build_snapshot_from_answers(
    session: OnboardingSessionResponse,
    answers: list,
) -> CompanySnapshot:
    """
    Build simplified CompanySnapshot from session and answers.

    This is a MVP implementation. In production, this would be replaced
    with full Perplexity research + Gemini synthesis.

    Args:
        session: Onboarding session
        answers: List of answers

    Returns:
        CompanySnapshot with minimal data
    """
    from onboarding.domain.models import (
        CompanyInfo,
        AudienceInfo,
        VoiceInfo,
        InsightsInfo,
        ClarifyingQuestion,
    )

    # Build answers dict
    answers_dict = {a.question_id: a.answer for a in answers}

    # Create minimal CompanySnapshot
    return CompanySnapshot(
        trace_id=str(uuid.uuid4()),
        company=CompanyInfo(
            name=session.company_domain or "Unknown Company",
            website=session.company_domain,
            description=answers_dict.get("q1", "No description provided"),
            key_offerings=[],
            differentiators=[],
        ),
        audience=AudienceInfo(
            primary=answers_dict.get("q2", "General audience"),
            pain_points=[],
            desired_outcomes=[],
        ),
        voice=VoiceInfo(
            tone=answers_dict.get("q3", "professional"),
            style_guidelines=[],
        ),
        insights=InsightsInfo(),
        clarifying_questions=[
            ClarifyingQuestion(
                id="q1",
                question="What does your company do?",
                reason="To understand company offering",
                expected_response_type="string",
            )
        ],
    )

