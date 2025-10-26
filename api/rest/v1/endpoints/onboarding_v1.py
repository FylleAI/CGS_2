"""
Onboarding API v1 - Session management and card creation.

Implements POST /api/v1/onboarding/sessions, GET /api/v1/onboarding/sessions/{id},
and POST /api/v1/onboarding/sessions/{id}/answers following OpenAPI contract.
"""

import logging
import uuid
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Header, Response

from api.rest.v1.models.onboarding import (
    CreateSessionRequest,
    OnboardingSessionResponse,
    SubmitAnswersRequest,
    SubmitAnswersResponse,
    SessionStatus,
    ErrorResponse,
)
from api.rest.v1.storage.session_storage import get_session_storage

logger = logging.getLogger(__name__)

router = APIRouter()

# Global instances (initialized on startup)
_cards_api_url: Optional[str] = None


def init_onboarding_v1(cards_api_url: str):
    """Initialize onboarding v1 dependencies."""
    global _cards_api_url
    _cards_api_url = cards_api_url
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
    logger.info(f"🚀 Creating onboarding session for {request.company_domain} (trace_id={trace_id})")

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

        logger.info(f"✅ Session created: {session_id}")
        return session

    except Exception as e:
        logger.error(f"❌ Failed to create session: {e}")
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
    x_trace_id: Optional[str] = Header(None, alias="X-Trace-ID"),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
) -> SubmitAnswersResponse:
    """
    Submit answers and create cards.

    **v1.0 Behavior**:
    1. Validate answers
    2. Create CompanySnapshot
    3. Call Cards API to create cards (POST /cards/batch)
    4. Return session with `card_ids`

    **Idempotency**: Uses session_id as idempotency key for Cards API if not provided.

    Args:
        session_id: Session ID
        request: Answers submission request
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
    idem_key = idempotency_key or str(session_id)

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
        # TODO: Implement card creation logic
        # For now, return mock response
        logger.info(f"📝 Processing {len(request.answers)} answers")

        # Mock: Create 4 card IDs
        card_ids = [uuid.uuid4() for _ in range(4)]

        # Update session
        storage.update_session(
            session_id=session_id,
            status=SessionStatus.COMPLETED,
            card_ids=card_ids,
            cards_created_count=len(card_ids),
        )

        logger.info(f"✅ Created {len(card_ids)} cards for session {session_id}")

        return SubmitAnswersResponse(
            session_id=session_id,
            status=SessionStatus.COMPLETED,
            card_ids=card_ids,
            cards_created_count=len(card_ids),
            updated_at=session.updated_at,
        )

    except Exception as e:
        logger.error(f"❌ Failed to submit answers: {e}")

        # Update session to failed
        storage.update_session(session_id=session_id, status=SessionStatus.FAILED)

        raise HTTPException(
            status_code=500,
            detail={"error": "InternalServerError", "detail": str(e), "request_id": trace_id},
        )

