"""Application settings configuration."""

import os
from typing import Optional, Dict, Any
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables and .env files.
    
    This class centralizes all configuration management using Pydantic
    for validation and type safety.
    """
    
    # Application settings
    app_name: str = Field(default="CGSRef", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # API settings
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_reload: bool = Field(default=True, env="API_RELOAD")
    
    # Security settings
    secret_key: str = Field(default="dev-secret-key", env="SECRET_KEY")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # AI Provider API Keys
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    deepseek_api_key: Optional[str] = Field(default=None, env="DEEPSEEK_API_KEY")
    gemini_api_key: Optional[str] = Field(default=None, env="GEMINI_API_KEY")
    serper_api_key: Optional[str] = Field(default=None, env="SERPER_API_KEY")
    perplexity_api_key: Optional[str] = Field(default=None, env="PERPLEXITY_API_KEY")
    
    # Database settings
    database_url: str = Field(default="sqlite:///./cgsref.db", env="DATABASE_URL")
    database_echo: bool = Field(default=False, env="DATABASE_ECHO")
    
    # File storage settings
    data_dir: str = Field(default="data", env="DATA_DIR")
    output_dir: str = Field(default="data/output", env="OUTPUT_DIR")
    profiles_dir: str = Field(default="data/profiles", env="PROFILES_DIR")
    workflows_dir: str = Field(default="data/workflows", env="WORKFLOWS_DIR")
    knowledge_base_dir: str = Field(default="data/knowledge_base", env="KNOWLEDGE_BASE_DIR")
    cache_dir: str = Field(default="data/cache", env="CACHE_DIR")
    
    # RAG settings
    rag_enabled: bool = Field(default=True, env="RAG_ENABLED")
    rag_chunk_size: int = Field(default=1000, env="RAG_CHUNK_SIZE")
    rag_chunk_overlap: int = Field(default=200, env="RAG_CHUNK_OVERLAP")
    rag_max_results: int = Field(default=5, env="RAG_MAX_RESULTS")
    
    # ChromaDB settings
    chroma_host: str = Field(default="localhost", env="CHROMA_HOST")
    chroma_port: int = Field(default=8000, env="CHROMA_PORT")
    chroma_persist_directory: str = Field(default="data/chroma", env="CHROMA_PERSIST_DIRECTORY")
    
    # Logging settings
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    
    # Content generation settings
    default_provider: str = Field(default="openai", env="DEFAULT_PROVIDER")
    default_model: str = Field(default="gpt-4o", env="DEFAULT_MODEL")
    default_temperature: float = Field(default=0.7, env="DEFAULT_TEMPERATURE")
    max_tokens: Optional[int] = Field(default=None, env="MAX_TOKENS")
    
    # Workflow settings
    workflow_timeout_seconds: int = Field(default=600, env="WORKFLOW_TIMEOUT_SECONDS")  # 10 minutes for complex workflows
    max_retries: int = Field(default=3, env="MAX_RETRIES")
    
    # WebSocket settings
    websocket_enabled: bool = Field(default=True, env="WEBSOCKET_ENABLED")
    websocket_path: str = Field(default="/ws", env="WEBSOCKET_PATH")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        directories = [
            self.data_dir,
            self.output_dir,
            self.profiles_dir,
            self.workflows_dir,
            self.knowledge_base_dir,
            self.cache_dir,
            self.chroma_persist_directory
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def get_available_providers(self) -> Dict[str, bool]:
        """Get available AI providers based on API keys."""
        return {
            "openai": bool(self.openai_api_key),
            "anthropic": bool(self.anthropic_api_key),
            "deepseek": bool(self.deepseek_api_key),
            "gemini": bool(self.gemini_api_key)
        }
    
    def has_any_provider(self) -> bool:
        """Check if at least one AI provider is configured."""
        return any(self.get_available_providers().values())
    
    def get_provider_api_key(self, provider: str) -> Optional[str]:
        """Get API key for specific provider."""
        provider_keys = {
            "openai": self.openai_api_key,
            "anthropic": self.anthropic_api_key,
            "deepseek": self.deepseek_api_key,
            "gemini": self.gemini_api_key
        }
        return provider_keys.get(provider.lower())
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"
    
    def get_database_url(self) -> str:
        """Get database URL with proper formatting."""
        return self.database_url
    
    def get_chroma_settings(self) -> Dict[str, Any]:
        """Get ChromaDB settings."""
        return {
            "host": self.chroma_host,
            "port": self.chroma_port,
            "persist_directory": self.chroma_persist_directory
        }
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": self.log_format,
                },
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
            },
            "root": {
                "level": self.log_level,
                "handlers": ["default"],
            },
        }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
