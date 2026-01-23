"""
Settings for Fylle Onboarding v3
Pydantic-based configuration with environment variable support.
"""

from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Server
    api_host: str = "0.0.0.0"
    api_port: int = 8001
    debug: bool = False
    log_level: str = "INFO"
    
    # Supabase
    supabase_url: str = Field(..., description="Supabase project URL")
    supabase_anon_key: str = Field(..., description="Supabase anonymous key")
    supabase_service_role_key: str = Field(..., description="Supabase service role key")
    
    # LLM Providers
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4-turbo-preview"
    
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-3-sonnet-20240229"
    
    gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-1.5-pro"
    use_vertex_gemini: bool = False
    gcp_project_id: Optional[str] = None
    gcp_location: str = "us-central1"
    
    deepseek_api_key: Optional[str] = None
    deepseek_model: str = "deepseek-chat"
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    
    perplexity_api_key: Optional[str] = None
    perplexity_model: str = "sonar-pro"
    
    # Default providers
    default_llm_provider: str = "gemini"
    default_research_provider: str = "perplexity"
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3002", "http://localhost:5173"]
    
    # Paths
    @property
    def prompts_dir(self) -> Path:
        return Path(__file__).parent.parent.parent / "prompts"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
