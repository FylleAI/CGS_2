"""
Briefs Routes for Fylle Onboarding v3
Brief generation endpoints.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from app.api.dependencies import get_brief_generator_service, get_brief_repository
from app.domain.services import BriefGeneratorService
from app.infrastructure.repositories import BriefRepository
from app.domain.entities import BriefQuestion, BriefQuestionsResponse, BriefResponse


router = APIRouter(prefix="/briefs", tags=["briefs"])


class StartBriefRequest(BaseModel):
    """Request to start brief generation."""
    pack_id: str


class StartBriefResponse(BaseModel):
    """Response with brief questions."""
    brief_session_id: str
    questions: List[Dict[str, Any]]
    message: str


class SubmitBriefAnswersRequest(BaseModel):
    """Request to submit brief answers."""
    answers: Dict[str, str]


class SubmitBriefAnswersResponse(BaseModel):
    """Response after generating brief."""
    brief_id: str
    brief: Dict[str, Any]
    message: str


@router.post("/start", response_model=StartBriefResponse)
async def start_brief(
    request: StartBriefRequest,
    user_id: str = Query(..., description="User ID"),
    service: BriefGeneratorService = Depends(get_brief_generator_service),
):
    """
    Start brief generation.
    
    Generates questions based on pack type and user context.
    """
    try:
        result = await service.start_brief(
            user_id=user_id,
            pack_id=request.pack_id,
        )
        
        return StartBriefResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore durante l'avvio del brief: {str(e)}",
        )


@router.post("/{brief_session_id}/answers", response_model=SubmitBriefAnswersResponse)
async def submit_brief_answers(
    brief_session_id: str,
    request: SubmitBriefAnswersRequest,
    service: BriefGeneratorService = Depends(get_brief_generator_service),
):
    """
    Submit answers and generate brief.
    """
    try:
        result = await service.submit_answers(
            brief_session_id=brief_session_id,
            answers=request.answers,
        )
        
        return SubmitBriefAnswersResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore durante la generazione del brief: {str(e)}",
        )


@router.get("", response_model=List[Dict[str, Any]])
async def get_user_briefs(
    user_id: str = Query(..., description="User ID"),
    pack_id: Optional[str] = Query(None, description="Filter by pack ID"),
    service: BriefGeneratorService = Depends(get_brief_generator_service),
):
    """Get all briefs for a user."""
    return await service.get_user_briefs(user_id, pack_id)


@router.get("/{brief_id}", response_model=Dict[str, Any])
async def get_brief(
    brief_id: str,
    service: BriefGeneratorService = Depends(get_brief_generator_service),
):
    """Get a specific brief by ID."""
    result = await service.get_brief(brief_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brief non trovato",
        )
    
    return result


@router.delete("/{brief_id}")
async def delete_brief(
    brief_id: str,
    brief_repo: BriefRepository = Depends(get_brief_repository),
):
    """Delete a brief."""
    success = await brief_repo.delete(brief_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brief non trovato",
        )
    
    return {"message": "Brief eliminato con successo"}
