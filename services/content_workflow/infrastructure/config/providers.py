"""Provider-specific configuration."""

from typing import Dict, Any, Optional
from pydantic import BaseModel

from ...domain.value_objects.provider_config import ProviderConfig, LLMProvider


class ProviderSettings(BaseModel):
    """Provider-specific settings."""

    # OpenAI settings
    openai_api_key: Optional[str] = None
    openai_base_url: Optional[str] = None
    openai_default_model: str = "gpt-4o"

    # Anthropic settings
    anthropic_api_key: Optional[str] = None
    anthropic_base_url: Optional[str] = None
    anthropic_default_model: str = "claude-3-7-sonnet-latest"

    # DeepSeek settings
    deepseek_api_key: Optional[str] = None
    deepseek_base_url: Optional[str] = None
    deepseek_default_model: str = "deepseek-chat"

    # Gemini settings
    gemini_api_key: Optional[str] = None
    gemini_default_model: str = "gemini-2.5-pro"

    def get_provider_config(self, provider: LLMProvider) -> ProviderConfig:
        """Get provider configuration for specific provider."""
        if provider == LLMProvider.OPENAI:
            return ProviderConfig(
                provider=provider,
                model=self.openai_default_model,
                api_key=self.openai_api_key,
                base_url=self.openai_base_url,
            )
        elif provider == LLMProvider.ANTHROPIC:
            return ProviderConfig(
                provider=provider,
                model=self.anthropic_default_model,
                api_key=self.anthropic_api_key,
                base_url=self.anthropic_base_url,
            )
        elif provider == LLMProvider.DEEPSEEK:
            return ProviderConfig(
                provider=provider,
                model=self.deepseek_default_model,
                api_key=self.deepseek_api_key,
                base_url=self.deepseek_base_url,
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def get_available_providers(self) -> Dict[str, bool]:
        """Get available providers based on API keys."""
        return {
            "openai": bool(self.openai_api_key),
            "anthropic": bool(self.anthropic_api_key),
            "deepseek": bool(self.deepseek_api_key),
        }

    def has_any_provider(self) -> bool:
        """Check if at least one provider is configured."""
        return any(self.get_available_providers().values())
