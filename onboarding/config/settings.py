"""Onboarding service settings configuration."""

from typing import Optional, List
from pathlib import Path
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from functools import lru_cache


class OnboardingSettings(BaseSettings):
    """
    Onboarding service settings loaded from environment variables.
    
    Extends CGS settings with onboarding-specific configuration.
    """
    
    # Service metadata
    service_name: str = Field(default="OnboardingService", env="ONBOARDING_SERVICE_NAME")
    service_version: str = Field(default="1.0.0", env="ONBOARDING_SERVICE_VERSION")
    
    # API settings
    onboarding_api_host: str = Field(default="0.0.0.0", env="ONBOARDING_API_HOST")
    onboarding_api_port: int = Field(default=8001, env="ONBOARDING_API_PORT")
    
    # CGS integration
    cgs_api_url: str = Field(default="http://localhost:8000", env="CGS_API_URL")
    cgs_api_timeout: int = Field(default=600, env="CGS_API_TIMEOUT")  # 10 minutes
    cgs_api_key: Optional[str] = Field(default=None, env="CGS_API_KEY")
    default_llm_provider: str = Field(default="gemini", env="DEFAULT_LLM_PROVIDER")
    
    # Perplexity settings (research)
    perplexity_api_key: Optional[str] = Field(default=None, env="PERPLEXITY_API_KEY")
    perplexity_model: str = Field(default="sonar-pro", env="PERPLEXITY_MODEL")
    perplexity_timeout: int = Field(default=30, env="PERPLEXITY_TIMEOUT")
    perplexity_max_retries: int = Field(default=3, env="PERPLEXITY_MAX_RETRIES")
    
    # Gemini settings (synthesis)
    gemini_api_key: Optional[str] = Field(default=None, env="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-2.5-pro", env="GEMINI_MODEL")
    gemini_timeout: int = Field(default=60, env="GEMINI_TIMEOUT")
    gemini_temperature: float = Field(default=0.7, env="GEMINI_TEMPERATURE")
    gemini_max_tokens: int = Field(default=8192, env="GEMINI_MAX_TOKENS")
    
    # Vertex AI settings (optional, for Gemini)
    use_vertex_gemini: bool = Field(default=True, env="USE_VERTEX_GEMINI")
    gcp_project_id: Optional[str] = Field(default=None, env="GCP_PROJECT_ID")
    gcp_location: str = Field(default="us-central1", env="GCP_LOCATION")
    google_application_credentials: Optional[str] = Field(
        default=None, env="GOOGLE_APPLICATION_CREDENTIALS"
    )
    
    # Brevo settings (email delivery)
    brevo_api_key: Optional[str] = Field(default=None, env="BREVO_API_KEY")
    brevo_sender_email: str = Field(
        default="onboarding@fylle.ai", env="BREVO_SENDER_EMAIL"
    )
    brevo_sender_name: str = Field(default="Fylle Onboarding", env="BREVO_SENDER_NAME")
    brevo_template_id: Optional[int] = Field(default=None, env="BREVO_TEMPLATE_ID")
    brevo_timeout: int = Field(default=30, env="BREVO_TIMEOUT")
    
    # Supabase settings (persistence)
    supabase_url: Optional[str] = Field(default=None, env="SUPABASE_URL")
    supabase_anon_key: Optional[str] = Field(default=None, env="SUPABASE_ANON_KEY")
    use_supabase: bool = Field(default=True, env="USE_SUPABASE")
    
    # Onboarding workflow settings
    max_clarifying_questions: int = Field(
        default=3, env="ONBOARDING_MAX_CLARIFYING_QUESTIONS"
    )
    session_timeout_minutes: int = Field(
        default=60, env="ONBOARDING_SESSION_TIMEOUT_MINUTES"
    )
    enable_auto_delivery: bool = Field(
        default=True, env="ONBOARDING_ENABLE_AUTO_DELIVERY"
    )
    
    # Retry and resilience settings
    max_retries: int = Field(default=3, env="ONBOARDING_MAX_RETRIES")
    retry_backoff_seconds: float = Field(
        default=2.0, env="ONBOARDING_RETRY_BACKOFF_SECONDS"
    )
    
    # Storage settings
    onboarding_data_dir: str = Field(
        default="data/onboarding", env="ONBOARDING_DATA_DIR"
    )
    onboarding_sessions_dir: str = Field(
        default="data/onboarding/sessions", env="ONBOARDING_SESSIONS_DIR"
    )
    onboarding_snapshots_dir: str = Field(
        default="data/onboarding/snapshots", env="ONBOARDING_SNAPSHOTS_DIR"
    )
    
    # Logging
    log_level: str = Field(default="INFO", env="ONBOARDING_LOG_LEVEL")
    enable_debug_logging: bool = Field(default=False, env="ONBOARDING_DEBUG")
    
    # Feature flags
    enable_snapshot_caching: bool = Field(
        default=True, env="ONBOARDING_ENABLE_SNAPSHOT_CACHING"
    )
    enable_cost_tracking: bool = Field(
        default=True, env="ONBOARDING_ENABLE_COST_TRACKING"
    )
    
    # Default workflow mappings (goal -> CGS workflow_type)
    default_workflow_mappings: dict = Field(
        default={
            # Analytics workflow (NEW)
            "company_analytics": "onboarding_analytics_generator",
            # Content workflows (Legacy)
            "linkedin_post": "onboarding_content_generator",
            "linkedin_article": "onboarding_content_generator",
            "newsletter": "onboarding_content_generator",
            "newsletter_premium": "onboarding_content_generator",
            "blog_post": "onboarding_content_generator",
            "article": "onboarding_content_generator",
        }
    )

    # Content type mappings (goal -> content_type)
    content_type_mappings: dict = Field(
        default={
            # Analytics (no content_type needed)
            "company_analytics": "analytics",  # Special type for analytics
            # Content types (Legacy)
            "linkedin_post": "linkedin_post",
            "linkedin_article": "linkedin_article",
            "newsletter": "newsletter",
            "newsletter_premium": "newsletter",
            "blog_post": "blog_post",
            "article": "blog_post",  # Fallback to blog_post
        }
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "allow"  # Allow extra fields for flexibility
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure directories exist
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        directories = [
            self.onboarding_data_dir,
            self.onboarding_sessions_dir,
            self.onboarding_snapshots_dir,
        ]
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    @field_validator("cgs_api_url")
    @classmethod
    def validate_cgs_url(cls, v: str) -> str:
        """Ensure CGS URL doesn't have trailing slash."""
        return v.rstrip("/")
    
    def get_workflow_type(self, goal: str) -> str:
        """Map onboarding goal to CGS workflow type."""
        return self.default_workflow_mappings.get(
            goal.lower(), "onboarding_content_generator"
        )

    def get_content_type(self, goal: str) -> str:
        """Map onboarding goal to content type."""
        return self.content_type_mappings.get(
            goal.lower(), "linkedin_post"  # Default fallback
        )
    
    def is_perplexity_configured(self) -> bool:
        """Check if Perplexity is configured."""
        return bool(self.perplexity_api_key)
    
    def is_gemini_configured(self) -> bool:
        """Check if Gemini is configured (API key or Vertex)."""
        if self.use_vertex_gemini:
            return bool(self.gcp_project_id and self.google_application_credentials)
        return bool(self.gemini_api_key)
    
    def is_brevo_configured(self) -> bool:
        """Check if Brevo is configured."""
        return bool(self.brevo_api_key)
    
    def is_supabase_configured(self) -> bool:
        """Check if Supabase is configured."""
        return self.use_supabase and bool(
            self.supabase_url and self.supabase_anon_key
        )
    
    def validate_required_services(self) -> dict:
        """Validate that all required services are configured."""
        return {
            "perplexity": self.is_perplexity_configured(),
            "gemini": self.is_gemini_configured(),
            "brevo": self.is_brevo_configured(),
            "supabase": self.is_supabase_configured(),
            "cgs": bool(self.cgs_api_url),
        }


@lru_cache()
def get_onboarding_settings() -> OnboardingSettings:
    """Get cached onboarding settings instance."""
    return OnboardingSettings()

