"""LLM Provider Factory for dynamic provider selection."""

import logging
from typing import Optional, Dict, Any

from ...application.interfaces.llm_provider_interface import LLMProviderInterface
from ...domain.value_objects.provider_config import ProviderConfig, LLMProvider
from ...infrastructure.config.settings import Settings
from ...infrastructure.external_services.openai_adapter import OpenAIAdapter
from ...infrastructure.external_services.anthropic_adapter import AnthropicAdapter
from ...infrastructure.external_services.deepseek_adapter import DeepSeekAdapter
from ...infrastructure.external_services.gemini_adapter import GeminiAdapter

logger = logging.getLogger(__name__)


class LLMProviderFactory:
    """
    Factory for creating LLM provider instances.

    This factory handles the creation and configuration of different
    LLM providers based on the requested provider type and settings.
    """

    @staticmethod
    def create_provider(
        provider_type: LLMProvider, settings: Settings
    ) -> LLMProviderInterface:
        """
        Create an LLM provider instance.

        Args:
            provider_type: Type of provider to create
            settings: Application settings containing API keys

        Returns:
            Configured LLM provider instance

        Raises:
            ValueError: If provider type is unsupported or API key is missing
        """
        logger.info(f"🏭 Creating provider: {provider_type.value}")

        if provider_type == LLMProvider.OPENAI:
            api_key = settings.openai_api_key
            if not api_key:
                logger.warning(
                    "⚠️ OpenAI provider requested but API key is not configured"
                )
                raise ValueError("OpenAI API key not configured")
            return OpenAIAdapter(api_key)

        elif provider_type == LLMProvider.ANTHROPIC:
            api_key = settings.anthropic_api_key
            if not api_key:
                logger.warning(
                    "⚠️ Anthropic provider requested but API key is not configured"
                )
                raise ValueError("Anthropic API key not configured")
            return AnthropicAdapter(api_key)

        elif provider_type == LLMProvider.DEEPSEEK:
            api_key = settings.deepseek_api_key
            if not api_key:
                logger.warning(
                    "⚠️ DeepSeek provider requested but API key is not configured"
                )
                raise ValueError("DeepSeek API key not configured")
            return DeepSeekAdapter(api_key)

        elif provider_type == LLMProvider.GEMINI:
            api_key = settings.gemini_api_key
            use_vertex = settings.use_vertex_gemini
            sa_path = settings.google_application_credentials
            # Allow Vertex-only setup without API key when Service Account is configured
            if not api_key and not (use_vertex and sa_path):
                logger.warning(
                    "⚠️ Gemini provider requested but neither API key nor Vertex Service Account is configured"
                )
                raise ValueError("Gemini credentials not configured")
            return GeminiAdapter(
                api_key,
                project_id=settings.gcp_project_id,
                location=settings.gcp_location,
                use_vertex=use_vertex,
                endpoint=settings.vertex_api_endpoint,
                api_version=settings.vertex_api_version,
                sa_credentials_path=sa_path,
            )

        else:
            raise ValueError(f"Unsupported provider type: {provider_type}")

    @staticmethod
    def create_provider_config(
        provider_type: LLMProvider,
        settings: Settings,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> ProviderConfig:
        """
        Create a provider configuration.

        Args:
            provider_type: Type of provider
            settings: Application settings
            model: Specific model to use (optional, uses default if not provided)
            temperature: Temperature setting
            max_tokens: Maximum tokens
            **kwargs: Additional provider-specific parameters

        Returns:
            Configured ProviderConfig instance
        """
        logger.debug(f"🔧 Creating config for provider: {provider_type.value}")

        # Get API key for the provider
        api_key = settings.get_provider_api_key(provider_type.value)
        if not api_key:
            logger.warning(
                f"⚠️ Provider config requested for {provider_type.value} but API key is not configured"
            )
            raise ValueError(
                f"API key not configured for provider: {provider_type.value}"
            )

        # Use default model if not specified
        if not model:
            if provider_type == LLMProvider.OPENAI:
                model = (
                    settings.default_model
                    if settings.default_provider == "openai"
                    else "gpt-4o"
                )
            elif provider_type == LLMProvider.ANTHROPIC:
                model = "claude-3-7-sonnet-latest"
            elif provider_type == LLMProvider.DEEPSEEK:
                model = "deepseek-chat"
            elif provider_type == LLMProvider.GEMINI:
                model = "gemini-2.5-pro"

        return ProviderConfig(
            provider=provider_type,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=api_key,
            additional_params=kwargs,
        )

    @staticmethod
    def get_available_providers(settings: Settings) -> Dict[str, bool]:
        """
        Get available providers based on configured API keys.

        Args:
            settings: Application settings

        Returns:
            Dictionary mapping provider names to availability status
        """
        availability = {}
        provider_keys = {
            "openai": settings.openai_api_key,
            "anthropic": settings.anthropic_api_key,
            "deepseek": settings.deepseek_api_key,
            "gemini": settings.gemini_api_key,
        }

        for provider_name, api_key in provider_keys.items():
            available = bool(api_key)
            # Special handling for Gemini: available if API key OR Vertex SA is configured
            if provider_name == "gemini":
                if settings.use_vertex_gemini and settings.google_application_credentials:
                    available = True
            availability[provider_name] = available
            if not available:
                logger.debug(
                    f"🔍 Provider '{provider_name}' is not configured (missing API key/credentials)"
                )

        return availability

    @staticmethod
    def get_default_provider(settings: Settings) -> LLMProvider:
        """
        Get the default provider based on settings and availability.

        Args:
            settings: Application settings

        Returns:
            Default LLM provider

        Raises:
            ValueError: If no providers are available
        """
        available = LLMProviderFactory.get_available_providers(settings)

        # Try to use the configured default provider
        default_provider = settings.default_provider
        if default_provider in available and available[default_provider]:
            return LLMProvider(default_provider)

        # Fallback order: OpenAI -> Anthropic -> DeepSeek -> Gemini
        for provider_name in ["openai", "anthropic", "deepseek", "gemini"]:
            if available.get(provider_name, False):
                logger.info(f"🔄 Using fallback provider: {provider_name}")
                return LLMProvider(provider_name)

        raise ValueError("No LLM providers are configured with valid API keys")

    @staticmethod
    def create_default_provider_and_config(
        settings: Settings, provider_override: Optional[str] = None
    ) -> tuple[LLMProviderInterface, ProviderConfig]:
        """
        Create default provider and config, with optional override.

        Args:
            settings: Application settings
            provider_override: Optional provider type override

        Returns:
            Tuple of (provider_instance, provider_config)
        """
        # Determine provider type
        if provider_override:
            try:
                provider_type = LLMProvider(provider_override)
            except ValueError:
                logger.warning(
                    f"⚠️ Invalid provider override: {provider_override}, using default"
                )
                provider_type = LLMProviderFactory.get_default_provider(settings)
        else:
            provider_type = LLMProviderFactory.get_default_provider(settings)

        # Create provider and config
        provider = LLMProviderFactory.create_provider(provider_type, settings)
        config = LLMProviderFactory.create_provider_config(provider_type, settings)

        logger.info(
            f"✅ Created provider: {provider_type.value} with model: {config.model}"
        )
        return provider, config


class ProviderManager:
    """
    Manager for handling multiple provider instances.

    This class provides a higher-level interface for managing
    multiple LLM providers and their configurations.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self._providers: Dict[LLMProvider, LLMProviderInterface] = {}
        self._configs: Dict[LLMProvider, ProviderConfig] = {}

    def get_provider(self, provider_type: LLMProvider) -> LLMProviderInterface:
        """Get or create a provider instance."""
        if provider_type not in self._providers:
            self._providers[provider_type] = LLMProviderFactory.create_provider(
                provider_type, self.settings
            )
        return self._providers[provider_type]

    def get_config(self, provider_type: LLMProvider, **kwargs) -> ProviderConfig:
        """Get or create a provider configuration."""
        cache_key = provider_type
        if cache_key not in self._configs:
            self._configs[cache_key] = LLMProviderFactory.create_provider_config(
                provider_type, self.settings, **kwargs
            )
        return self._configs[cache_key]

    def get_available_providers(self) -> Dict[str, bool]:
        """Get available providers."""
        return LLMProviderFactory.get_available_providers(self.settings)
