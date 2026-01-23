"""
Onboarding Routes for Fylle Onboarding v3
Onboarding flow endpoints.
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr

from app.api.dependencies import get_onboarding_service
from app.domain.services import OnboardingService


router = APIRouter(prefix="/onboarding", tags=["onboarding"])


class StartOnboardingRequest(BaseModel):
    """Request to start onboarding."""
    brand_name: str
    user_email: EmailStr
    website: Optional[str] = None
    goal: str = "company_snapshot"
    additional_context: Optional[str] = None


class StartOnboardingResponse(BaseModel):
    """Response after starting onboarding."""
    session_id: str
    user_id: str
    state: str
    snapshot_summary: Optional[Dict[str, Any]] = None
    clarifying_questions: list
    message: str
    next_action: str


class SubmitAnswersRequest(BaseModel):
    """Request to submit answers."""
    answers: Dict[str, Any]


class SubmitAnswersResponse(BaseModel):
    """Response after submitting answers."""
    session_id: str
    user_id: str
    state: str
    message: str
    card_ids: list = []
    cards_created: int = 0
    redirect_url: Optional[str] = None


class SessionStatusResponse(BaseModel):
    """Session status response."""
    session_id: str
    user_id: str
    state: str
    has_snapshot: bool
    snapshot_complete: bool
    error_message: Optional[str] = None


@router.post("/start", response_model=StartOnboardingResponse)
async def start_onboarding(
    request: StartOnboardingRequest,
    service: OnboardingService = Depends(get_onboarding_service),
):
    """
    Start the onboarding process.
    
    1. Creates or retrieves user
    2. Researches company
    3. Generates clarifying questions
    """
    try:
        result = await service.start_onboarding(
            email=request.user_email,
            brand_name=request.brand_name,
            website=request.website,
            additional_context=request.additional_context,
        )
        
        return StartOnboardingResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore durante l'onboarding: {str(e)}",
        )


@router.post("/{session_id}/answers", response_model=SubmitAnswersResponse)
async def submit_answers(
    session_id: str,
    request: SubmitAnswersRequest,
    service: OnboardingService = Depends(get_onboarding_service),
):
    """
    Submit answers to clarifying questions.
    
    Generates cards based on answers and snapshot.
    """
    try:
        result = await service.submit_answers(
            session_id=session_id,
            answers=request.answers,
        )
        
        return SubmitAnswersResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore durante la generazione delle cards: {str(e)}",
        )


@router.get("/{session_id}", response_model=SessionStatusResponse)
async def get_session_status(
    session_id: str,
    service: OnboardingService = Depends(get_onboarding_service),
):
    """Get the status of an onboarding session."""
    result = await service.get_session(session_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessione non trovata",
        )
    
    return SessionStatusResponse(**result)
