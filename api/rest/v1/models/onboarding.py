"""Pydantic models for Onboarding API v1.

These models match the OpenAPI contract in contracts/onboarding-api-v1.yaml.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SessionStatus(str, Enum):
    """Onboarding session status."""

    RESEARCH = "research"
    SYNTHESIS = "synthesis"
    QUESTIONS = "questions"
    ANSWERS = "answers"
    COMPLETED = "completed"
    FAILED = "failed"


class CreateSessionRequest(BaseModel):
    """Request to create a new onboarding session."""

    tenant_id: UUID = Field(..., description="Tenant ID for multi-tenant isolation")
    company_domain: str = Field(..., description="Company domain for research (e.g., 'acme.com')")
    user_email: str = Field(..., description="User email address")


class OnboardingSessionResponse(BaseModel):
    """Onboarding session response."""

    session_id: UUID = Field(..., description="Session ID")
    tenant_id: UUID = Field(..., description="Tenant ID")
    status: SessionStatus = Field(..., description="Session status")
    company_domain: Optional[str] = Field(None, description="Company domain")
    user_email: Optional[str] = Field(None, description="User email")
    card_ids: Optional[List[UUID]] = Field(
        None, description="IDs of cards created from this session (available after answers submission)"
    )
    cards_created_count: Optional[int] = Field(
        None, description="Number of cards created (available after answers submission)"
    )
    created_at: datetime = Field(..., description="Session creation timestamp")
    updated_at: datetime = Field(..., description="Session last update timestamp")


class Answer(BaseModel):
    """Answer to a clarifying question."""

    question_id: str = Field(..., description="Question ID")
    answer: str = Field(..., description="Answer text")


class SubmitAnswersRequest(BaseModel):
    """Request to submit answers to clarifying questions."""

    answers: List[Answer] = Field(..., description="List of answers")


class SubmitAnswersResponse(BaseModel):
    """Response after submitting answers and creating cards."""

    session_id: UUID = Field(..., description="Session ID")
    status: SessionStatus = Field(..., description="Session status (completed or failed)")
    card_ids: List[UUID] = Field(..., description="IDs of cards created in Cards API")
    cards_created_count: int = Field(..., description="Number of cards created")
    updated_at: datetime = Field(..., description="Session last update timestamp")


class ErrorResponse(BaseModel):
    """Error response."""

    error: str = Field(..., description="Error type")
    detail: str = Field(..., description="Error details")
    request_id: str = Field(..., description="Request ID for tracing")

