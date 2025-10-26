"""CompanySnapshot contract - shared between Onboarding and Card Service."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class CompanyInfo(BaseModel):
    """Company information."""
    
    name: str = Field(..., description="Company name")
    industry: str = Field(..., description="Industry")
    size: Optional[str] = Field(None, description="Company size")
    website: Optional[str] = Field(None, description="Company website")
    description: Optional[str] = Field(None, description="Company description")


class AudienceInfo(BaseModel):
    """Target audience information."""
    
    primary_segment: str = Field(..., description="Primary audience segment")
    demographics: Optional[Dict[str, Any]] = Field(None, description="Demographics")
    pain_points: List[str] = Field(default_factory=list, description="Audience pain points")
    needs: List[str] = Field(default_factory=list, description="Audience needs")


class VoiceInfo(BaseModel):
    """Brand voice and tone guidelines."""
    
    tone: str = Field(..., description="Brand tone")
    style_guidelines: List[str] = Field(default_factory=list, description="Style guidelines")
    forbidden_phrases: List[str] = Field(default_factory=list, description="Forbidden phrases")
    cta_preferences: List[str] = Field(default_factory=list, description="CTA preferences")


class InsightsInfo(BaseModel):
    """Key insights about the company."""
    
    key_differentiators: List[str] = Field(default_factory=list, description="Key differentiators")
    competitive_advantages: List[str] = Field(default_factory=list, description="Competitive advantages")
    market_position: Optional[str] = Field(None, description="Market position")
    growth_opportunities: List[str] = Field(default_factory=list, description="Growth opportunities")


class ClarifyingQuestion(BaseModel):
    """Clarifying question for user feedback."""
    
    id: str = Field(..., description="Question ID")
    question: str = Field(..., description="Question text")
    reason: str = Field(..., description="Why this question is asked")
    expected_response_type: str = Field(..., description="Expected response type")
    options: Optional[List[str]] = Field(None, description="Multiple choice options")
    required: bool = Field(default=True, description="Is this question required?")


class SourceMetadata(BaseModel):
    """Metadata about information sources."""
    
    source: str = Field(..., description="Source name")
    tool: str = Field(..., description="Tool used to gather information")
    timestamp: datetime = Field(..., description="When information was gathered")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Confidence score")


class CompanySnapshot(BaseModel):
    """Complete snapshot of company information.
    
    This is the main contract between Onboarding Service and Card Service.
    It contains all information needed to create atomic cards.
    """
    
    version: str = Field(default="1.0", description="Schema version")
    snapshot_id: UUID = Field(..., description="Unique snapshot ID")
    generated_at: datetime = Field(..., description="When snapshot was generated")
    trace_id: Optional[str] = Field(None, description="Trace ID for debugging")
    
    # Core information
    company: CompanyInfo = Field(..., description="Company information")
    audience: AudienceInfo = Field(..., description="Target audience")
    voice: VoiceInfo = Field(..., description="Brand voice")
    insights: InsightsInfo = Field(..., description="Key insights")
    
    # User feedback
    clarifying_questions: List[ClarifyingQuestion] = Field(
        default_factory=list,
        description="Questions for user clarification"
    )
    clarifying_answers: Dict[str, Any] = Field(
        default_factory=dict,
        description="User answers to clarifying questions"
    )
    
    # Source tracking
    source_metadata: List[SourceMetadata] = Field(
        default_factory=list,
        description="Metadata about information sources"
    )
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "version": "1.0",
                "snapshot_id": "550e8400-e29b-41d4-a716-446655440000",
                "generated_at": "2025-10-26T18:00:00Z",
                "company": {
                    "name": "Acme Corp",
                    "industry": "Technology",
                    "size": "50-100",
                    "website": "https://acme.com",
                },
                "audience": {
                    "primary_segment": "Enterprise",
                    "pain_points": ["High costs", "Complexity"],
                    "needs": ["Simplification", "Cost reduction"],
                },
                "voice": {
                    "tone": "Professional",
                    "style_guidelines": ["Clear", "Concise"],
                },
                "insights": {
                    "key_differentiators": ["Innovation", "Quality"],
                },
            }
        }

