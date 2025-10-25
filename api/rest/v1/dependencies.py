"""FastAPI dependencies for dependency injection."""

from functools import lru_cache
from typing import Optional

from core.application.use_cases.generate_content import GenerateContentUseCase
from core.infrastructure.repositories.file_content_repository import (
    FileContentRepository,
)
from core.infrastructure.repositories.yaml_agent_repository import YamlAgentRepository
from core.infrastructure.repositories.file_workflow_repository import (
    FileWorkflowRepository,
)
from core.infrastructure.external_services.openai_adapter import OpenAIAdapter
from core.infrastructure.factories.provider_factory import LLMProviderFactory
from core.infrastructure.config.settings import get_settings
from core.domain.value_objects.provider_config import LLMProvider
from core.card_service.infrastructure.card_repository import CardRepository


@lru_cache()
def get_content_repository() -> FileContentRepository:
    """Get content repository instance."""
    settings = get_settings()
    return FileContentRepository(settings.output_dir)


@lru_cache()
def get_agent_repository() -> YamlAgentRepository:
    """Get agent repository instance."""
    settings = get_settings()
    return YamlAgentRepository(settings.profiles_dir)


@lru_cache()
def get_workflow_repository() -> FileWorkflowRepository:
    """Get workflow repository instance."""
    settings = get_settings()
    return FileWorkflowRepository(settings.workflows_dir)


@lru_cache()
def get_card_repository() -> Optional[CardRepository]:
    """Get card repository instance for Card Service integration."""
    try:
        # Import here to avoid circular imports
        from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
        from sqlalchemy.orm import sessionmaker

        settings = get_settings()

        # Get database URL from settings (Supabase)
        db_url = settings.database_url
        if not db_url:
            return None

        # Create async engine
        engine = create_async_engine(db_url, echo=False)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        # Return card repository with session
        return CardRepository(async_session())
    except Exception as e:
        # If card repository setup fails, continue without it
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to initialize card repository: {str(e)}")
        return None


def get_llm_provider(provider_type: Optional[str] = None):
    """Get LLM provider instance with dynamic provider selection."""
    settings = get_settings()

    # Use factory to create provider
    if provider_type:
        try:
            provider_enum = LLMProvider(provider_type)
            return LLMProviderFactory.create_provider(provider_enum, settings)
        except ValueError:
            # Invalid provider type, fall back to default
            pass

    # Use default provider
    provider_enum = LLMProviderFactory.get_default_provider(settings)
    return LLMProviderFactory.create_provider(provider_enum, settings)


def get_content_use_case(
    provider_type: Optional[str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
) -> GenerateContentUseCase:
    """Get content generation use case with dynamic provider selection.
    Allows overriding model/temperature/max_tokens so that the AgentExecutor
    uses exactly the configuration selected in the frontend for this request.
    """
    settings = get_settings()

    # Resolve provider enum
    if provider_type:
        try:
            provider_enum = LLMProvider(provider_type)
        except ValueError:
            provider_enum = LLMProviderFactory.get_default_provider(settings)
    else:
        provider_enum = LLMProviderFactory.get_default_provider(settings)

    # Create provider instance
    llm_provider = LLMProviderFactory.create_provider(provider_enum, settings)

    # Use overrides when provided, otherwise fallback to settings/defaults
    eff_temperature = (
        temperature if temperature is not None else settings.default_temperature
    )
    provider_config = LLMProviderFactory.create_provider_config(
        provider_enum,
        settings,
        model=model,
        temperature=eff_temperature,
        max_tokens=max_tokens,
    )

    return GenerateContentUseCase(
        content_repository=get_content_repository(),
        workflow_repository=get_workflow_repository(),
        agent_repository=get_agent_repository(),
        llm_provider=llm_provider,
        provider_config=provider_config,
        rag_service=None,  # Would be implemented later
        serper_api_key=settings.serper_api_key,
        perplexity_api_key=settings.perplexity_api_key,
        card_repository=get_card_repository(),  # Card Service integration
    )
