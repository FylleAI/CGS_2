"""Provider configuration value object."""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum


class LLMProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    DEEPSEEK = "deepseek"
    GEMINI = "gemini"


@dataclass(frozen=True)
class ProviderConfig:
    """
    Immutable configuration for LLM providers.
    
    This value object encapsulates all configuration needed
    to interact with a specific LLM provider.
    """
    
    provider: LLMProvider = LLMProvider.OPENAI
    model: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    additional_params: Dict[str, Any] = None
    
    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if self.additional_params is None:
            object.__setattr__(self, 'additional_params', {})
        
        # Validate temperature
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")
        
        # Validate top_p
        if not 0.0 <= self.top_p <= 1.0:
            raise ValueError("Top_p must be between 0.0 and 1.0")
        
        # Validate penalties
        if not -2.0 <= self.frequency_penalty <= 2.0:
            raise ValueError("Frequency penalty must be between -2.0 and 2.0")
        
        if not -2.0 <= self.presence_penalty <= 2.0:
            raise ValueError("Presence penalty must be between -2.0 and 2.0")
        
        # Validate max_tokens
        if self.max_tokens is not None and self.max_tokens <= 0:
            raise ValueError("Max tokens must be positive")
        
        # Set default model for provider if not specified
        if not self.model:
            object.__setattr__(self, 'model', self._get_default_model())
    
    def _get_default_model(self) -> str:
        """Get default model for the provider."""
        defaults = {
            LLMProvider.OPENAI: "gpt-4o",
            LLMProvider.ANTHROPIC: "claude-3-7-sonnet-latest",
            LLMProvider.DEEPSEEK: "deepseek-chat",
            LLMProvider.GEMINI: "gemini-2.5-pro"
        }
        return defaults.get(self.provider, "gpt-4o")
    
    def get_available_models(self) -> list[str]:
        """Get list of available models for the provider."""
        models = {
            LLMProvider.OPENAI: [
                "gpt-3.5-turbo",
                "gpt-4",
                "gpt-4-turbo",
                "gpt-4o",
                "gpt-4o-mini",
                "o1",
                "o1-mini",
                "o1-pro",
                "o3-mini"
            ],
            LLMProvider.ANTHROPIC: [
                "claude-3-5-haiku-20241022",
                "claude-3-5-haiku-latest",
                "claude-3-7-sonnet-20250219",
                "claude-3-7-sonnet-latest",
                "claude-sonnet-4-20250514",
                "claude-opus-4-20250514"
            ],
            LLMProvider.DEEPSEEK: [
                "deepseek-chat",
                "deepseek-coder"
            ],
            LLMProvider.GEMINI: [
                "gemini-2.5-pro",
                "gemini-2.5-flash",
                "gemini-2.5-flash-lite",
                "gemini-2.5-flash-live",
                "gemini-1.5-pro",
                "gemini-1.5-flash",
                "gemini-pro",
                "gemini-1.5-pro-latest",
                "gemini-1.5-flash-latest"
            ]
        }
        return models.get(self.provider, [])
    
    def is_model_available(self) -> bool:
        """Check if the configured model is available for the provider."""
        return self.model in self.get_available_models()
    
    def with_temperature(self, temperature: float) -> "ProviderConfig":
        """Create a new config with different temperature."""
        return ProviderConfig(
            provider=self.provider,
            model=self.model,
            temperature=temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
            api_key=self.api_key,
            base_url=self.base_url,
            additional_params=self.additional_params
        )
    
    def with_model(self, model: str) -> "ProviderConfig":
        """Create a new config with different model."""
        return ProviderConfig(
            provider=self.provider,
            model=model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
            api_key=self.api_key,
            base_url=self.base_url,
            additional_params=self.additional_params
        )
    
    def with_provider(self, provider: LLMProvider) -> "ProviderConfig":
        """Create a new config with different provider and default model."""
        return ProviderConfig(
            provider=provider,
            model="",  # Will be set to default in __post_init__
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
            api_key=self.api_key,
            base_url=self.base_url,
            additional_params=self.additional_params
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "provider": self.provider.value,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "api_key": self.api_key,
            "base_url": self.base_url,
            "additional_params": self.additional_params
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProviderConfig":
        """Create from dictionary representation."""
        return cls(
            provider=LLMProvider(data.get("provider", "openai")),
            model=data.get("model", ""),
            temperature=data.get("temperature", 0.7),
            max_tokens=data.get("max_tokens"),
            top_p=data.get("top_p", 1.0),
            frequency_penalty=data.get("frequency_penalty", 0.0),
            presence_penalty=data.get("presence_penalty", 0.0),
            api_key=data.get("api_key"),
            base_url=data.get("base_url"),
            additional_params=data.get("additional_params", {})
        )
    
    @classmethod
    def create_openai_config(cls, model: str = "gpt-4o", temperature: float = 0.7) -> "ProviderConfig":
        """Create OpenAI configuration."""
        return cls(
            provider=LLMProvider.OPENAI,
            model=model,
            temperature=temperature
        )
    
    @classmethod
    def create_anthropic_config(cls, model: str = "claude-3-7-sonnet-latest", temperature: float = 0.7) -> "ProviderConfig":
        """Create Anthropic configuration."""
        return cls(
            provider=LLMProvider.ANTHROPIC,
            model=model,
            temperature=temperature
        )
    
    @classmethod
    def create_deepseek_config(cls, model: str = "deepseek-chat", temperature: float = 0.7) -> "ProviderConfig":
        """Create DeepSeek configuration."""
        return cls(
            provider=LLMProvider.DEEPSEEK,
            model=model,
            temperature=temperature
        )

    @classmethod
    def create_gemini_config(cls, model: str = "gemini-2.5-pro", temperature: float = 0.7) -> "ProviderConfig":
        """Create Google Gemini configuration."""
        return cls(
            provider=LLMProvider.GEMINI,
            model=model,
            temperature=temperature
        )
