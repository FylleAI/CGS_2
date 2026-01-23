"""
FastAPI Dependencies for Fylle Onboarding v3
Dependency injection for services and repositories.
"""

from functools import lru_cache

from app.config.settings import get_settings, Settings
from app.infrastructure.database.supabase import get_supabase_client
from app.infrastructure.repositories import (
    UserRepository,
    CardRepository,
    SessionRepository,
    BriefRepository,
    PackRepository,
)
from app.core.llm import LLMRouter, LLMProvider
from app.core.prompts import PromptEngine
from app.core.context import ContextManager
from app.domain.services import OnboardingService, BriefGeneratorService


def get_user_repository() -> UserRepository:
    """Get user repository instance."""
    return UserRepository(get_supabase_client())


def get_card_repository() -> CardRepository:
    """Get card repository instance."""
    return CardRepository(get_supabase_client())


def get_session_repository() -> SessionRepository:
    """Get session repository instance."""
    return SessionRepository(get_supabase_client())


def get_brief_repository() -> BriefRepository:
    """Get brief repository instance."""
    return BriefRepository(get_supabase_client())


def get_pack_repository() -> PackRepository:
    """Get pack repository instance."""
    return PackRepository(get_supabase_client())


@lru_cache()
def get_llm_router() -> LLMRouter:
    """Get LLM router instance."""
    settings = get_settings()
    
    # Map string provider to enum
    default_provider = LLMProvider(settings.default_llm_provider)
    research_provider = LLMProvider(settings.default_research_provider)
    
    return LLMRouter(
        openai_api_key=settings.openai_api_key,
        anthropic_api_key=settings.anthropic_api_key,
        gemini_api_key=settings.gemini_api_key,
        deepseek_api_key=settings.deepseek_api_key,
        perplexity_api_key=settings.perplexity_api_key,
        use_vertex_gemini=settings.use_vertex_gemini,
        gcp_project_id=settings.gcp_project_id,
        gcp_location=settings.gcp_location,
        default_provider=default_provider,
        default_research_provider=research_provider,
    )


@lru_cache()
def get_prompt_engine() -> PromptEngine:
    """Get prompt engine instance."""
    settings = get_settings()
    return PromptEngine(
        yaml_prompts_dir=settings.prompts_dir,
        supabase_repository=None,  # Can add Supabase prompts repo later
    )


def get_context_manager() -> ContextManager:
    """Get context manager instance."""
    return ContextManager(get_card_repository())


def get_onboarding_service() -> OnboardingService:
    """Get onboarding service instance."""
    return OnboardingService(
        llm_router=get_llm_router(),
        prompt_engine=get_prompt_engine(),
        user_repository=get_user_repository(),
        session_repository=get_session_repository(),
        cards_repository=get_card_repository(),
    )


def get_brief_generator_service() -> BriefGeneratorService:
    """Get brief generator service instance."""
    return BriefGeneratorService(
        llm_router=get_llm_router(),
        prompt_engine=get_prompt_engine(),
        context_manager=get_context_manager(),
        briefs_repository=get_brief_repository(),
        packs_repository=get_pack_repository(),
    )
