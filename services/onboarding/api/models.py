"""API request/response models."""

from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

from services.onboarding.domain.models import (
    OnboardingGoal,
    SessionState,
    CompanySnapshot,
    ClarifyingQuestion,
)


# Request models
class StartOnboardingRequest(BaseModel):
    """Request to start services.onboarding."""

    brand_name: str = Field(..., min_length=1, description="Company/brand name")
    website: Optional[str] = Field(default=None, description="Company website URL")
    goal: OnboardingGoal = Field(..., description="Content generation goal")
    user_email: str = Field(..., min_length=1, description="Email for content delivery")
    additional_context: Optional[str] = Field(
        default=None, description="Additional context or instructions"
    )


class SubmitAnswersRequest(BaseModel):
    """Request to submit answers to clarifying questions."""
    
    answers: Dict[str, Any] = Field(
        ..., description="Map of question_id to answer"
    )


class ExecuteWorkflowRequest(BaseModel):
    """Request to execute workflow (optional, for manual trigger)."""
    
    dry_run: bool = Field(default=False, description="Dry run mode")
    requested_provider: Optional[str] = Field(
        default=None, description="Override LLM provider"
    )


# Response models
class QuestionResponse(BaseModel):
    """Clarifying question response."""
    
    id: str
    question: str
    reason: str
    expected_response_type: str
    options: Optional[List[str]] = None
    required: bool


class SnapshotSummary(BaseModel):
    """Summary of company snapshot."""
    
    company_name: str
    industry: Optional[str]
    description: str
    target_audience: Optional[str]
    tone: Optional[str]
    questions_count: int


class StartOnboardingResponse(BaseModel):
    """Response from starting services.onboarding."""
    
    session_id: UUID
    trace_id: str
    state: SessionState
    snapshot_summary: Optional[SnapshotSummary] = None
    clarifying_questions: List[QuestionResponse]
    message: str
    next_action: str


class SubmitAnswersResponse(BaseModel):
    """Response from submitting answers."""
    
    session_id: UUID
    state: SessionState
    content_title: Optional[str] = None
    content_preview: Optional[str] = None
    word_count: Optional[int] = None
    delivery_status: Optional[str] = None
    message: str
    workflow_metrics: Optional[Dict[str, Any]] = None


class SessionStatusResponse(BaseModel):
    """Session status response."""
    
    session_id: UUID
    trace_id: str
    brand_name: str
    goal: OnboardingGoal
    state: SessionState
    created_at: str
    updated_at: str
    has_snapshot: bool
    snapshot_complete: bool
    cgs_run_id: Optional[UUID] = None
    delivery_status: Optional[str] = None
    error_message: Optional[str] = None


class SessionDetailResponse(BaseModel):
    """Detailed session response."""

    session_id: UUID
    trace_id: str
    brand_name: str
    website: Optional[str]
    goal: OnboardingGoal
    user_email: Optional[str]
    state: SessionState
    created_at: str
    updated_at: str
    snapshot: Optional[CompanySnapshot] = None
    cgs_run_id: Optional[UUID] = None
    cgs_response: Optional[Dict[str, Any]] = None  # ✨ NEW: Include full CGS response with content
    delivery_status: Optional[str] = None
    delivery_message_id: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any]


class HealthCheckResponse(BaseModel):
    """Health check response."""
    
    status: str
    version: str
    services: Dict[str, bool]
    cgs_healthy: bool


class ErrorResponse(BaseModel):
    """Error response."""
    
    error: str
    detail: Optional[str] = None
    session_id: Optional[UUID] = None

