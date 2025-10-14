"""FastAPI endpoints for onboarding service."""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, status

from onboarding.domain.models import OnboardingInput
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
    get_execute_onboarding_use_case,
    get_repository,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/onboarding", tags=["onboarding"])


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
        
        questions = [
            QuestionResponse(
                id=q.id,
                question=q.question,
                reason=q.reason,
                expected_response_type=q.expected_response_type,
                options=q.options,
                required=q.required,
            )
            for q in snapshot.clarifying_questions
        ]
        
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
    execute_uc = Depends(get_execute_onboarding_use_case),
    repository = Depends(get_repository),
):
    """
    Submit answers to clarifying questions and execute workflow.
    
    Validates answers, builds payload, executes CGS workflow, and delivers content.
    """
    logger.info(f"Submitting answers for session: {session_id}")
    
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
        
        # Collect answers
        session = await collect_answers_uc.execute(session, request.answers)
        
        # Execute workflow
        result = await execute_uc.execute(session)
        
        # Build response
        response = SubmitAnswersResponse(
            session_id=session.session_id,
            state=session.state,
            message="Onboarding completed successfully!" if result.is_successful() else "Workflow execution failed",
        )
        
        if result.content:
            response.content_title = result.content.title
            response.content_preview = result.content.body[:200] + "..."
            response.word_count = result.content.word_count
        
        if session.delivery_status:
            response.delivery_status = session.delivery_status
        
        if result.workflow_metrics:
            response.workflow_metrics = result.workflow_metrics.model_dump()
        
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

