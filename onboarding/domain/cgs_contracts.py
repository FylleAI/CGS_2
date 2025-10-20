"""CGS payload contracts for onboarding service.

These models define the payload structure for invoking CGS workflows,
following the contracts defined in PianoOnboarding.md.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

from .models import CompanySnapshot


class LinkedInPostInput(BaseModel):
    """Input parameters for LinkedIn post (enhanced_article workflow)."""
    
    topic: str = Field(..., min_length=3)
    client_name: str = Field(..., min_length=1)
    client_profile: str = Field(default="default")
    context: Optional[str] = None
    target_audience: str
    tone: str = Field(
        default="professional",
        description="Tone: professional, authoritative, conversational, playful, bold"
    )
    call_to_action: Optional[str] = None
    key_points: List[str] = Field(default_factory=list)
    hashtags: List[str] = Field(default_factory=list, max_length=10)
    target_word_count: int = Field(default=220, ge=50, le=800)
    include_statistics: bool = Field(default=True)
    include_examples: bool = Field(default=True)
    include_sources: bool = Field(default=True)
    custom_instructions: Optional[str] = None
    post_format: str = Field(
        default="thought_leadership",
        description="Format: thought_leadership, event_promo, product_launch, talent_branding"
    )
    hero_quote: Optional[str] = None
    image_prompt: Optional[str] = None


class NewsletterInput(BaseModel):
    """Input parameters for newsletter (premium_newsletter workflow)."""
    
    topic: str = Field(..., min_length=5)
    newsletter_topic: Optional[str] = None
    client_name: Optional[str] = None
    client_profile: str = Field(default="default")
    target_audience: str = Field(..., min_length=3)
    target_word_count: int = Field(default=1200, ge=800, le=2500)
    edition_number: int = Field(default=1, ge=1)
    premium_sources: List[str] = Field(default_factory=list, max_length=10)
    exclude_topics: List[str] = Field(default_factory=list)
    priority_sections: List[str] = Field(default_factory=list)
    custom_instructions: Optional[str] = None
    section_overrides: Dict[str, str] = Field(default_factory=dict)
    cta_variants: List[str] = Field(default_factory=list)
    compliance_notes: Optional[str] = None


class CgsPayloadMetadata(BaseModel):
    """Metadata for CGS payload."""
    
    source: str = Field(default="onboarding_adapter")
    dry_run: bool = Field(default=False)
    requested_provider: Optional[str] = None
    language: str = Field(default="it")


class CgsPayloadLinkedInPost(BaseModel):
    """
    CGS Payload v1.0 for LinkedIn post (enhanced_article workflow).
    
    Maps onboarding goal 'linkedin_post' to CGS 'enhanced_article' workflow.
    """
    
    version: str = Field(default="1.0")
    session_id: UUID
    workflow: str = Field(default="enhanced_article")
    goal: str = Field(default="linkedin_post")
    trace_id: Optional[str] = None
    
    company_snapshot: CompanySnapshot
    clarifying_answers: Dict[str, Any] = Field(default_factory=dict)
    input: LinkedInPostInput
    metadata: CgsPayloadMetadata = Field(default_factory=CgsPayloadMetadata)


class CgsPayloadNewsletter(BaseModel):
    """
    CGS Payload v1.0 for newsletter (premium_newsletter workflow).
    
    Maps onboarding goal 'newsletter' to CGS 'premium_newsletter' workflow.
    """
    
    version: str = Field(default="1.0")
    session_id: UUID
    workflow: str = Field(default="premium_newsletter")
    goal: str = Field(default="newsletter_premium")
    trace_id: Optional[str] = None
    
    company_snapshot: CompanySnapshot
    clarifying_answers: Dict[str, Any] = Field(default_factory=dict)
    input: NewsletterInput
    metadata: CgsPayloadMetadata = Field(default_factory=CgsPayloadMetadata)


class WorkflowMetrics(BaseModel):
    """Workflow execution metrics from CGS."""
    
    total_cost: Optional[float] = Field(default=None, ge=0.0)
    total_tokens: Optional[int] = Field(default=None, ge=0)
    duration_seconds: Optional[float] = Field(default=None, ge=0.0)
    agents_used: Optional[int] = Field(default=None, ge=0)
    success_rate: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    tasks_completed: Optional[int] = Field(default=None, ge=0)
    tasks_failed: Optional[int] = Field(default=None, ge=0)
    tool_calls: Optional[int] = Field(default=None, ge=0)
    llm_calls: Optional[int] = Field(default=None, ge=0)
    cost_by_provider: Dict[str, float] = Field(default_factory=dict)
    cost_by_agent: Dict[str, float] = Field(default_factory=dict)


class ContentResult(BaseModel):
    """Content result from CGS workflow."""

    content_id: Optional[UUID] = None
    title: str
    body: str
    format: str = Field(default="markdown")
    display_type: str = Field(
        default="content_preview",
        description="Frontend display type: content_preview, analytics_dashboard, etc."
    )
    word_count: int = Field(default=0, ge=0)
    character_count: int = Field(default=0, ge=0)
    reading_time_minutes: Optional[float] = Field(default=None, ge=0.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    generated_image: Optional[Dict[str, Any]] = None
    image_metadata: Optional[Dict[str, Any]] = None


class DeliveryInfo(BaseModel):
    """Delivery information for content."""
    
    channel: str = Field(default="email")
    recipient: Optional[str] = None
    status: str = Field(default="pending")
    timestamp: Optional[str] = None
    message_id: Optional[str] = None


class KnowledgeBaseCard(BaseModel):
    """Knowledge base card information."""
    
    storage_url: Optional[str] = None
    format: str = Field(default="html")


class LogEntry(BaseModel):
    """Log entry from workflow execution."""
    
    timestamp: str
    level: str
    message: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ResultEnvelope(BaseModel):
    """
    Result envelope v1.0 from CGS execution.
    
    Wraps the CGS response with onboarding-specific metadata.
    """
    
    version: str = Field(default="1.0")
    session_id: UUID
    trace_id: Optional[str] = None
    workflow: str
    goal: str
    status: str  # "completed" or "failed"
    
    cgs_run_id: Optional[UUID] = None
    supabase_run_id: Optional[UUID] = None
    
    error: Optional[Dict[str, Any]] = None
    content: Optional[ContentResult] = None
    workflow_metrics: Optional[WorkflowMetrics] = None
    delivery: Optional[DeliveryInfo] = None
    knowledge_base_card: Optional[KnowledgeBaseCard] = None
    logs: List[LogEntry] = Field(default_factory=list)
    
    def is_successful(self) -> bool:
        """Check if workflow execution was successful."""
        return self.status == "completed" and self.content is not None
    
    def get_error_message(self) -> Optional[str]:
        """Get error message if failed."""
        if self.error:
            return self.error.get("message")
        return None


# ============================================================================
# NEW: Unified Onboarding Content Payload (v2.0)
# ============================================================================


class OnboardingContentInput(BaseModel):
    """Unified input for onboarding content generation."""

    # Content type
    content_type: str = Field(
        ...,
        description="Type of content: linkedin_post, linkedin_article, newsletter, blog_post"
    )

    # Common fields
    topic: str = Field(..., min_length=1)
    client_name: str = Field(..., min_length=1)
    client_profile: str = Field(default="onboarding")
    target_audience: str = Field(default="Business professionals")
    tone: str = Field(default="professional")
    context: str = Field(default="")
    custom_instructions: Optional[str] = None

    # Content-specific configuration
    content_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Content type specific configuration (word_count, include_emoji, etc.)"
    )


class CgsPayloadOnboardingContent(BaseModel):
    """
    CGS Payload v2.0 for unified onboarding content generation.

    Supports multiple content types via onboarding_content_generator workflow:
    - linkedin_post: Short engaging post (200-400 words)
    - linkedin_article: Long-form thought leadership (800-1500 words)
    - newsletter: Multi-section newsletter (1000-1500 words)
    - blog_post: SEO-optimized blog article (1200-2000 words)
    """

    version: str = Field(default="2.0")
    session_id: UUID
    workflow: str = Field(default="onboarding_content_generator")
    goal: str  # Original onboarding goal (linkedin_post, linkedin_article, etc.)
    trace_id: Optional[str] = None

    company_snapshot: CompanySnapshot
    clarifying_answers: Dict[str, Any] = Field(default_factory=dict)
    input: OnboardingContentInput
    metadata: CgsPayloadMetadata = Field(default_factory=CgsPayloadMetadata)

