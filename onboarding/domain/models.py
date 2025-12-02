"""Domain models for onboarding service.

These models represent the core business entities and value objects
following the contracts defined in PianoOnboarding.md.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, field_validator


class OnboardingGoal(str, Enum):
    """Supported onboarding goals.

    SIMPLIFIED VERSION - Only 2 goals:
    1. company_snapshot: Visual card of company profile
    2. content_generation: Generic content generation (unified)
    """

    COMPANY_SNAPSHOT = "company_snapshot"     # Visual card view of company profile
    CONTENT_GENERATION = "content_generation" # Generic content generation


class SessionState(str, Enum):
    """Onboarding session states."""
    
    CREATED = "created"
    RESEARCHING = "researching"
    SYNTHESIZING = "synthesizing"
    AWAITING_USER = "awaiting_user"
    PAYLOAD_READY = "payload_ready"
    EXECUTING = "executing"
    DELIVERING = "delivering"
    DONE = "done"
    FAILED = "failed"


class Evidence(BaseModel):
    """Evidence from research sources."""
    
    source: str = Field(..., description="Source URL or reference")
    excerpt: str = Field(..., description="Relevant excerpt from source")
    confidence: Optional[float] = Field(
        default=None, ge=0.0, le=1.0, description="Confidence score"
    )


class CompanyInfo(BaseModel):
    """Company information extracted from research."""
    
    name: str = Field(..., min_length=1)
    legal_name: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    headquarters: Optional[str] = None
    size_range: Optional[str] = None
    description: str = Field(..., description="Company description")
    key_offerings: List[str] = Field(default_factory=list)
    differentiators: List[str] = Field(default_factory=list)
    evidence: List[Evidence] = Field(default_factory=list)


class AudienceInfo(BaseModel):
    """Target audience information."""
    
    primary: Optional[str] = None
    secondary: List[str] = Field(default_factory=list)
    pain_points: List[str] = Field(default_factory=list)
    desired_outcomes: List[str] = Field(default_factory=list)


class VoiceInfo(BaseModel):
    """Brand voice and style information."""
    
    tone: Optional[str] = None
    style_guidelines: List[str] = Field(default_factory=list)
    forbidden_phrases: List[str] = Field(default_factory=list)
    cta_preferences: List[str] = Field(default_factory=list)


class InsightsInfo(BaseModel):
    """Market and competitive insights."""
    
    positioning: Optional[str] = None
    key_messages: List[str] = Field(default_factory=list)
    recent_news: List[str] = Field(default_factory=list)
    competitors: List[str] = Field(default_factory=list)


class QuestionCardMapping(BaseModel):
    """Maps a question to a card field it populates."""

    card_type: str = Field(..., description="Card type (e.g., 'target', 'brand_voice')")
    field_name: str = Field(..., description="Field name in the card")


class ClarifyingQuestion(BaseModel):
    """A clarifying question to ask the user."""

    id: str = Field(..., description="Question ID (e.g., 'q1', 'q2')")
    question: str = Field(..., description="The question text")
    reason: str = Field(..., description="Why this question is being asked")
    expected_response_type: str = Field(
        ..., description="Expected response type: string, select, boolean, number"
    )
    options: Optional[List[str]] = Field(
        default=None, description="Options for select-type questions"
    )
    required: bool = Field(default=True, description="Whether answer is required")
    maps_to: List[QuestionCardMapping] = Field(
        default_factory=list,
        description="Card fields this question populates"
    )

    @field_validator("options")
    @classmethod
    def validate_enum_options(cls, v: Optional[List[str]], info) -> Optional[List[str]]:
        """Ensure select questions have options."""
        response_type = info.data.get("expected_response_type")
        if response_type in ("enum", "select") and (not v or len(v) == 0):
            raise ValueError("Questions with select type must have options")
        return v


class SourceMetadata(BaseModel):
    """Metadata about a research source."""
    
    tool: str = Field(..., description="Tool used (perplexity, web_search, etc.)")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    cost_usd: Optional[float] = Field(default=None, ge=0.0)
    token_usage: Optional[int] = Field(default=None, ge=0)


class CompanySnapshot(BaseModel):
    """
    Company snapshot v1.0 - consolidated research and synthesis.
    
    This is the core artifact produced by the onboarding research phase.
    """
    
    version: str = Field(default="1.0", description="Schema version")
    snapshot_id: UUID = Field(default_factory=uuid4)
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    trace_id: Optional[str] = None
    
    company: CompanyInfo
    audience: AudienceInfo = Field(default_factory=AudienceInfo)
    voice: VoiceInfo = Field(default_factory=VoiceInfo)
    insights: InsightsInfo = Field(default_factory=InsightsInfo)
    
    clarifying_questions: List[ClarifyingQuestion] = Field(
        ..., min_length=1, max_length=10
    )
    clarifying_answers: Dict[str, Any] = Field(default_factory=dict)
    
    source_metadata: List[SourceMetadata] = Field(default_factory=list)
    
    @field_validator("clarifying_questions")
    @classmethod
    def validate_question_ids(cls, v: List[ClarifyingQuestion]) -> List[ClarifyingQuestion]:
        """Ensure question IDs are unique and follow pattern."""
        ids = [q.id for q in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Question IDs must be unique")
        return v
    
    def add_answer(self, question_id: str, answer: Any) -> None:
        """Add an answer to a clarifying question."""
        self.clarifying_answers[question_id] = answer
    
    def is_complete(self) -> bool:
        """Check if all required questions have been answered."""
        required_ids = {q.id for q in self.clarifying_questions if q.required}
        answered_ids = set(self.clarifying_answers.keys())
        return required_ids.issubset(answered_ids)


class OnboardingSession(BaseModel):
    """
    Onboarding session tracking the complete flow.
    
    Persisted to Supabase for state management and audit trail.
    """
    
    session_id: UUID = Field(default_factory=uuid4)
    trace_id: str = Field(default_factory=lambda: str(uuid4()))
    
    # Input
    brand_name: str = Field(..., min_length=1)
    website: Optional[str] = None
    goal: OnboardingGoal
    user_email: str = Field(..., min_length=1)
    
    # State
    state: SessionState = Field(default=SessionState.CREATED)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Artifacts
    snapshot: Optional[CompanySnapshot] = None
    cgs_payload: Optional[Dict[str, Any]] = None
    cgs_run_id: Optional[UUID] = None
    cgs_response: Optional[Dict[str, Any]] = None

    # RAG: Reference to company context (if reused)
    company_context_id: Optional[UUID] = None
    
    # Delivery
    delivery_status: Optional[str] = None
    delivery_message_id: Optional[str] = None
    delivery_timestamp: Optional[datetime] = None
    
    # Metadata
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def update_state(self, new_state: SessionState) -> None:
        """Update session state and timestamp."""
        self.state = new_state
        self.updated_at = datetime.utcnow()
    
    def mark_failed(self, error: str) -> None:
        """Mark session as failed with error message."""
        self.state = SessionState.FAILED
        self.error_message = error
        self.updated_at = datetime.utcnow()
    
    def is_terminal_state(self) -> bool:
        """Check if session is in a terminal state."""
        return self.state in {SessionState.DONE, SessionState.FAILED}


class OnboardingInput(BaseModel):
    """Input for starting an onboarding session."""
    
    brand_name: str = Field(..., min_length=1, description="Company/brand name")
    website: Optional[str] = Field(default=None, description="Company website URL")
    goal: OnboardingGoal = Field(..., description="Content generation goal")
    user_email: Optional[str] = Field(
        default=None, description="Email for delivery (optional)"
    )
    additional_context: Optional[str] = Field(
        default=None, description="Additional context from user"
    )


class OnboardingResponse(BaseModel):
    """Response from onboarding operations."""
    
    session_id: UUID
    state: SessionState
    snapshot: Optional[CompanySnapshot] = None
    message: Optional[str] = None
    next_action: Optional[str] = None

