"""
OnboardingRawInput - Raw data collected during onboarding.

This module defines the intermediate data structure that sits between:
  - User input (minimal required fields)
  - Inferred data (from research, scraping, LLM)
  - Final cards output

Design Principles:
  1. Separate "user_input" from "inferred" data clearly
  2. All inferred fields are Optional (progressive enhancement)
  3. User input should be minimal - only what CANNOT be inferred
  4. This structure is the INPUT to card builders
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


# =============================================================================
# USER INPUT - Minimal required data from the user
# =============================================================================

class UserInput(BaseModel):
    """
    Minimal input required from the user.
    
    Design: Only ask for what CANNOT be reliably inferred.
    Everything else comes from research/scraping/LLM.
    """
    # Identity - REQUIRED
    brand_name: str = Field(..., min_length=1, description="Company/brand name")
    user_email: str = Field(..., description="Contact email for delivery")
    
    # Optional hints (help inference but not required)
    website: Optional[str] = Field(default=None, description="Company website URL")
    industry_hint: Optional[str] = Field(default=None, description="Industry if known")
    additional_context: Optional[str] = Field(default=None, description="Free-form context")
    
    # User preferences (cannot be inferred)
    target_channels: List[str] = Field(
        default_factory=lambda: ["linkedin"],
        description="Preferred content channels"
    )
    content_frequency: Optional[str] = Field(
        default=None,
        description="Desired content frequency (e.g., '3x/week')"
    )
    budget_range: Optional[str] = Field(
        default=None,
        description="Marketing budget range if relevant"
    )


# =============================================================================
# INFERRED DATA - From research/scraping/LLM
# =============================================================================

class InferredCompanyData(BaseModel):
    """Company data inferred from research."""
    legal_name: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[str] = None
    headquarters: Optional[str] = None
    size_range: Optional[str] = None
    key_offerings: List[str] = Field(default_factory=list)
    differentiators: List[str] = Field(default_factory=list)
    value_proposition: Optional[str] = None
    
    # Performance metrics if found
    metrics: List[Dict[str, str]] = Field(default_factory=list)


class InferredAudienceData(BaseModel):
    """Audience data inferred from research."""
    primary_audience: Optional[str] = None
    secondary_audiences: List[str] = Field(default_factory=list)
    pain_points: List[str] = Field(default_factory=list)
    goals: List[str] = Field(default_factory=list)
    demographics: Optional[Dict[str, str]] = None
    communication_channels: List[str] = Field(default_factory=list)


class InferredVoiceData(BaseModel):
    """Brand voice inferred from existing content."""
    tone: Optional[str] = None
    style_guidelines: List[str] = Field(default_factory=list)
    dos_examples: List[str] = Field(default_factory=list)
    donts_examples: List[str] = Field(default_factory=list)
    terms_to_use: List[str] = Field(default_factory=list)
    terms_to_avoid: List[str] = Field(default_factory=list)


class InferredCompetitorData(BaseModel):
    """Single competitor data."""
    name: str
    positioning: Optional[str] = None
    key_messages: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)


class InferredTopicData(BaseModel):
    """Content topic data."""
    name: str
    description: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    angles: List[str] = Field(default_factory=list)
    trends: List[Dict[str, str]] = Field(default_factory=list)


class InferredData(BaseModel):
    """All inferred data from research phase."""
    company: InferredCompanyData = Field(default_factory=InferredCompanyData)
    audience: InferredAudienceData = Field(default_factory=InferredAudienceData)
    voice: InferredVoiceData = Field(default_factory=InferredVoiceData)
    competitors: List[InferredCompetitorData] = Field(default_factory=list)
    topics: List[InferredTopicData] = Field(default_factory=list)
    
    # Raw research content for reference
    raw_research: Optional[str] = None
    research_sources: List[str] = Field(default_factory=list)


# =============================================================================
# ONBOARDING RAW INPUT - Combined user input + inferred data
# =============================================================================

class OnboardingRawInput(BaseModel):
    """
    Complete raw input for card generation pipeline.
    
    This is the canonical input to runOnboardingPipeline().
    It combines:
      - user_input: Minimal data from user
      - inferred: Data from research/scraping/LLM
      - clarifying_answers: Answers to follow-up questions
    """
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    trace_id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # User-provided data
    user_input: UserInput
    
    # Research-inferred data
    inferred: InferredData = Field(default_factory=InferredData)
    
    # Clarifying Q&A (from existing flow)
    clarifying_answers: Dict[str, Any] = Field(default_factory=dict)
    
    # Processing metadata
    research_completed: bool = False
    synthesis_completed: bool = False

