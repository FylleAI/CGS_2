"""FastAPI endpoints for onboarding service."""

import json
import logging
import os
import time
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, status, Header

# Conditional import for Cards client (may not be available during development)
try:
    from fylle_cards_client import CardsClient
    from fylle_cards_client.client import CardsAPIError
    CARDS_CLIENT_AVAILABLE = True
except ImportError:
    CARDS_CLIENT_AVAILABLE = False
    CardsClient = None
    CardsAPIError = Exception
    import logging
    logging.getLogger(__name__).warning(
        "⚠️ fylle_cards_client not available - Cards creation will be skipped. "
        "This is expected during development before Cards microservice is ready."
    )

from onboarding.domain.models import OnboardingInput, SessionState
from onboarding.api.models import (
    StartOnboardingRequest,
    StartOnboardingResponse,
    SubmitAnswersRequest,
    SubmitAnswersResponse,
    SessionStatusResponse,
    SessionDetailResponse,
    QuestionResponse,
    SnapshotSummary,
)
from onboarding.api.dependencies import (
    get_create_session_use_case,
    get_research_company_use_case,
    get_synthesize_snapshot_use_case,
    get_collect_answers_use_case,
    get_execute_onboarding_use_case,  # DEPRECATED: Will be removed
    get_create_cards_use_case,
    get_repository,
)
# Conditional import for metrics (may not be available)
try:
    from onboarding.infrastructure.metrics import (
        onboarding_cards_created_total,
        onboarding_batch_duration_ms,
        onboarding_errors_total,
        onboarding_partial_creation_total,
    )
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False
    # Create dummy metrics objects
    class DummyMetric:
        def labels(self, **kwargs):
            return self
        def inc(self):
            pass
        def observe(self, value):
            pass

    onboarding_cards_created_total = DummyMetric()
    onboarding_batch_duration_ms = DummyMetric()
    onboarding_errors_total = DummyMetric()
    onboarding_partial_creation_total = DummyMetric()

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/onboarding", tags=["onboarding"])

# Cards API configuration
CARDS_API_URL = os.getenv("CARDS_API_URL", "http://localhost:8002")
CARDS_FRONTEND_URL = os.getenv("CARDS_FRONTEND_URL", "http://localhost:3002")


@router.post("/start", response_model=StartOnboardingResponse, status_code=status.HTTP_201_CREATED)
async def start_onboarding(
    request: StartOnboardingRequest,
    create_session_uc = Depends(get_create_session_use_case),
    research_uc = Depends(get_research_company_use_case),
    synthesize_uc = Depends(get_synthesize_snapshot_use_case),
):
    """
    Start onboarding process.
    
    Creates session, researches company, and generates clarifying questions.
    """
    logger.info(f"Starting onboarding for: {request.brand_name}")
    
    # Check if required services are configured
    if not research_uc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Perplexity research service not configured",
        )
    
    if not synthesize_uc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gemini synthesis service not configured",
        )
    
    try:
        # Step 1: Create session
        input_data = OnboardingInput(
            brand_name=request.brand_name,
            website=request.website,
            goal=request.goal,
            user_email=request.user_email,
            additional_context=request.additional_context,
        )
        
        session = await create_session_uc.execute(input_data)
        
        # Step 2: Research company
        research_result = await research_uc.execute(session)
        
        # Step 3: Synthesize snapshot
        snapshot = await synthesize_uc.execute(session, research_result)
        
        # Build response
        snapshot_summary = SnapshotSummary(
            company_name=snapshot.company.name,
            industry=snapshot.company.industry,
            description=snapshot.company.description,
            target_audience=snapshot.audience.primary,
            tone=snapshot.voice.tone,
            questions_count=len(snapshot.clarifying_questions),
        )
        
        # Map question types for frontend compatibility
        questions = []
        for q in snapshot.clarifying_questions:
            # Convert 'enum' to 'select' for frontend
            response_type = q.expected_response_type
            if response_type == 'enum':
                response_type = 'select'

            questions.append(
                QuestionResponse(
                    id=q.id,
                    question=q.question,
                    reason=q.reason,
                    expected_response_type=response_type,
                    options=q.options,
                    required=q.required,
                )
            )
        
        return StartOnboardingResponse(
            session_id=session.session_id,
            trace_id=session.trace_id,
            state=session.state,
            snapshot_summary=snapshot_summary,
            clarifying_questions=questions,
            message=f"Onboarding started for {request.brand_name}. Please answer the clarifying questions.",
            next_action=f"POST /api/v1/onboarding/{session.session_id}/answers",
        )
        
    except Exception as e:
        logger.error(f"Failed to start onboarding: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start onboarding: {str(e)}",
        )


@router.post("/{session_id}/answers", response_model=SubmitAnswersResponse)
async def submit_answers(
    session_id: UUID,
    request: SubmitAnswersRequest,
    collect_answers_uc = Depends(get_collect_answers_use_case),
    create_cards_uc = Depends(get_create_cards_use_case),
    repository = Depends(get_repository),
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID"),
    x_trace_id: Optional[str] = Header(None, alias="X-Trace-ID"),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
):
    """
    Submit answers to clarifying questions and create cards.

    **Onboarding → Cards Integration**:
    1. Collect answers
    2. Build CompanySnapshot (from Gemini synthesis + user answers)
    3. Create 4 cards via Cards API /batch (idempotent)
    4. Save card_ids in session
    5. Return card_ids to frontend

    Note: Workflow execution is separate - frontend will call Workflow API
    when content generation is needed.
    """
    trace_id = x_trace_id or str(session_id)
    logger.info(f"Submitting answers for session: {session_id} (trace_id={trace_id})")
    
    if not repository:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Session repository not configured",
        )
    
    try:
        # Get session
        session = await repository.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session not found: {session_id}",
            )

        # Check if already executing or done (idempotency)
        if session.state in [SessionState.EXECUTING, SessionState.DELIVERING, SessionState.DONE]:
            logger.info(f"Session {session_id} already in state {session.state}, returning current status")

            # Build response with current state
            response = SubmitAnswersResponse(
                session_id=session.session_id,
                state=session.state,
                message=f"Session already {session.state.value}. Please check status endpoint for updates.",
                snapshot=session.snapshot,  # ✨ Include snapshot for idempotent requests
            )

            # Add CGS response data if available
            if session.cgs_response:
                # Extract content from cgs_response dict
                content_data = session.cgs_response.get("content")
                if content_data:
                    response.content_title = content_data.get("title")
                    body = content_data.get("body", "")
                    if body:
                        response.content_preview = body[:200] + ("..." if len(body) > 200 else "")
                    response.word_count = content_data.get("word_count")

                # Extract workflow metrics
                metrics_data = session.cgs_response.get("workflow_metrics")
                if metrics_data:
                    response.workflow_metrics = metrics_data

            if session.delivery_status:
                response.delivery_status = session.delivery_status

            return response

        # Collect answers
        session = await collect_answers_uc.execute(session, request.answers)

        # ========================================================================
        # SPRINT 4 DAY 1: CARDS API INTEGRATION
        # ========================================================================

        # STEP 1: Build CompanySnapshot v1 from session
        # The snapshot is already available in session.snapshot after collect_answers
        if not session.snapshot:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="CompanySnapshot not available after collecting answers",
            )

        # STEP 2: Call Cards API /batch to create 4 cards atomically
        tenant_id = x_tenant_id or str(session.session_id)  # Fallback to session_id if no tenant header
        idem_key = idempotency_key or f"onboarding-{session_id}-batch"

        start_time = time.time()
        card_ids = []
        created_count = 0
        partial = False

        # Check if Cards client is available
        if not CARDS_CLIENT_AVAILABLE:
            logger.warning(
                json.dumps({
                    "event": "cards_batch_skipped",
                    "trace_id": trace_id,
                    "tenant_id": tenant_id,
                    "session_id": str(session_id),
                    "reason": "Cards client not available - development mode",
                })
            )
            # Skip cards creation - continue with empty card_ids
            card_ids = []
            created_count = 0
            partial = False
        else:
            logger.info(
                json.dumps({
                    "event": "cards_batch_start",
                    "trace_id": trace_id,
                    "tenant_id": tenant_id,
                    "session_id": str(session_id),
                    "idempotency_key": idem_key,
                })
            )

            try:
                # Initialize Cards API client
                cards_client = CardsClient(
                    base_url=CARDS_API_URL,
                    tenant_id=tenant_id,
                    trace_id=trace_id,
                    session_id=str(session_id),
                )

                # Convert snapshot to dict for Cards API
                snapshot_dict = json.loads(session.snapshot.model_dump_json())

                # Call batch endpoint with idempotency
                batch_response = cards_client.create_cards_batch(
                    company_snapshot=snapshot_dict,
                    source_session_id=session_id,
                    created_by="onboarding-service",
                    idempotency_key=idem_key,
                )

                # Extract card IDs
                card_ids = [card.card_id for card in batch_response.cards]
                created_count = batch_response.created_count
                partial = created_count < 4

                # Calculate duration
                duration_ms = int((time.time() - start_time) * 1000)

                logger.info(
                    json.dumps({
                        "event": "cards_batch_created",
                        "trace_id": trace_id,
                        "tenant_id": tenant_id,
                        "session_id": str(session_id),
                        "created_count": created_count,
                        "partial": partial,
                        "duration_ms": duration_ms,
                        "idempotency_key": idem_key,
                    })
                )

                # STEP 5: Metrics - Record cards created per type
                for card in batch_response.cards:
                    onboarding_cards_created_total.labels(
                        tenant_id=tenant_id,
                        card_type=card.card_type.value if hasattr(card.card_type, 'value') else str(card.card_type),
                    ).inc()

                # Record batch duration
                onboarding_batch_duration_ms.labels(tenant_id=tenant_id).observe(duration_ms)

                # Record partial creation if applicable
                if partial:
                    onboarding_partial_creation_total.labels(tenant_id=tenant_id).inc()
                    logger.warning(
                        json.dumps({
                            "event": "cards_batch_partial",
                            "trace_id": trace_id,
                            "tenant_id": tenant_id,
                            "session_id": str(session_id),
                            "created_count": created_count,
                            "expected_count": 4,
                        })
                    )

            except CardsAPIError as e:
                # Cards API error - return 502 with trace_id
                logger.error(
                    json.dumps({
                        "event": "cards_batch_error",
                        "trace_id": trace_id,
                        "tenant_id": tenant_id,
                        "session_id": str(session_id),
                        "error": str(e),
                    })
                )

                # Record error metric
                onboarding_errors_total.labels(
                    tenant_id=tenant_id,
                    error_type="cards_api",
                ).inc()

                # Update session to failed
                session.update_state(SessionState.FAILED)
                session.error_message = f"Cards API error: {str(e)}"
                await repository.save_session(session)

                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail={
                        "error": "BadGateway",
                        "detail": f"Cards API error: {str(e)}",
                        "request_id": trace_id,
                    },
                )

        # STEP 3: Save card_ids in session metadata (whether cards were created or not)
        session.metadata["card_ids"] = [str(cid) for cid in card_ids]
        session.metadata["cards_created_count"] = created_count
        session.metadata["cards_status"] = "skipped" if not CARDS_CLIENT_AVAILABLE else ("partial" if partial else "created")
        session.metadata["cards_trace_id"] = trace_id

        # ========================================================================
        # END CARDS API INTEGRATION
        # ========================================================================

        # Update session state to DONE (cards created successfully)
        session.update_state(SessionState.DONE)
        await repository.save_session(session)

        # Build Cards Service frontend URL for redirect
        # Format: http://localhost:3002/cards?session_id=xxx&tenant_id=yyy
        cards_service_url = f"{CARDS_FRONTEND_URL}/cards?session_id={session_id}&tenant_id={tenant_id}"

        # Build response with card_ids and enriched snapshot
        response = SubmitAnswersResponse(
            session_id=session.session_id,
            state=session.state,
            message=f"Cards created successfully! Created {created_count} cards.",
            snapshot=session.snapshot,  # ✨ Return enriched snapshot with user answers
            card_ids=[str(cid) for cid in card_ids],  # Return card_ids to frontend
            cards_created=created_count,
            partial=partial,
            cards_service_url=cards_service_url,  # ✨ URL for automatic redirect
        )

        logger.info(
            f"✅ Onboarding completed for session {session_id}: "
            f"{created_count} cards created, card_ids={card_ids}, redirect_url={cards_service_url}"
        )

        return response
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Failed to submit answers: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit answers: {str(e)}",
        )


@router.get("/{session_id}/status", response_model=SessionStatusResponse)
async def get_session_status(
    session_id: UUID,
    repository = Depends(get_repository),
):
    """Get session status."""
    logger.info(f"Getting status for session: {session_id}")
    
    if not repository:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Session repository not configured",
        )
    
    try:
        session = await repository.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session not found: {session_id}",
            )
        
        return SessionStatusResponse(
            session_id=session.session_id,
            trace_id=session.trace_id,
            brand_name=session.brand_name,
            goal=session.goal,
            state=session.state,
            created_at=session.created_at.isoformat(),
            updated_at=session.updated_at.isoformat(),
            has_snapshot=session.snapshot is not None,
            snapshot_complete=session.snapshot.is_complete() if session.snapshot else False,
            cgs_run_id=session.cgs_run_id,
            delivery_status=session.delivery_status,
            error_message=session.error_message,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session status: {str(e)}",
        )


@router.get("/{session_id}", response_model=SessionDetailResponse)
async def get_session_detail(
    session_id: UUID,
    repository = Depends(get_repository),
):
    """Get detailed session information."""
    logger.info(f"Getting details for session: {session_id}")
    
    if not repository:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Session repository not configured",
        )
    
    try:
        session = await repository.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session not found: {session_id}",
            )
        
        return SessionDetailResponse(
            session_id=session.session_id,
            trace_id=session.trace_id,
            brand_name=session.brand_name,
            website=session.website,
            goal=session.goal,
            user_email=session.user_email,
            state=session.state,
            created_at=session.created_at.isoformat(),
            updated_at=session.updated_at.isoformat(),
            snapshot=session.snapshot,
            cgs_run_id=session.cgs_run_id,
            cgs_response=session.cgs_response,  # ✨ NEW: Include full CGS response
            delivery_status=session.delivery_status,
            delivery_message_id=session.delivery_message_id,
            error_message=session.error_message,
            metadata=session.metadata,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session detail: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session detail: {str(e)}",
        )

