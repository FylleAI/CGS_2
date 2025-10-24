"""FastAPI dependencies for onboarding service."""

from functools import lru_cache
from typing import Optional

from onboarding.config.settings import OnboardingSettings, get_onboarding_settings
from onboarding.infrastructure.adapters.perplexity_adapter import PerplexityAdapter
from onboarding.infrastructure.adapters.gemini_adapter import GeminiSynthesisAdapter
from onboarding.infrastructure.adapters.cgs_adapter import CgsAdapter
from onboarding.infrastructure.adapters.brevo_adapter import BrevoAdapter
from onboarding.infrastructure.repositories.supabase_repository import (
    SupabaseSessionRepository,
    get_session_repository,
)
from onboarding.infrastructure.repositories.company_context_repository import (
    CompanyContextRepository,
)
from onboarding.application.builders.payload_builder import PayloadBuilder
from onboarding.application.use_cases.create_session import CreateSessionUseCase
from onboarding.application.use_cases.research_company import ResearchCompanyUseCase
from onboarding.application.use_cases.synthesize_snapshot import SynthesizeSnapshotUseCase
from onboarding.application.use_cases.collect_answers import CollectAnswersUseCase
from onboarding.application.use_cases.execute_onboarding import ExecuteOnboardingUseCase


# Settings
def get_settings() -> OnboardingSettings:
    """Get onboarding settings."""
    return get_onboarding_settings()


# Adapters
@lru_cache()
def get_perplexity_adapter() -> Optional[PerplexityAdapter]:
    """Get Perplexity adapter."""
    settings = get_settings()
    if not settings.is_perplexity_configured():
        return None
    return PerplexityAdapter(settings)


@lru_cache()
def get_gemini_adapter() -> Optional[GeminiSynthesisAdapter]:
    """Get Gemini adapter."""
    settings = get_settings()
    if not settings.is_gemini_configured():
        return None
    return GeminiSynthesisAdapter(settings)


@lru_cache()
def get_cgs_adapter() -> CgsAdapter:
    """Get CGS adapter."""
    settings = get_settings()
    return CgsAdapter(settings)


@lru_cache()
def get_brevo_adapter() -> Optional[BrevoAdapter]:
    """Get Brevo adapter."""
    settings = get_settings()
    if not settings.is_brevo_configured():
        return None
    return BrevoAdapter(settings)


@lru_cache()
def get_repository() -> Optional[SupabaseSessionRepository]:
    """Get Supabase repository."""
    return get_session_repository()


@lru_cache()
def get_context_repository() -> Optional[CompanyContextRepository]:
    """Get company context repository (RAG)."""
    settings = get_settings()
    if not settings.is_supabase_configured():
        return None
    return CompanyContextRepository(settings)


# Builders
@lru_cache()
def get_payload_builder() -> PayloadBuilder:
    """Get payload builder."""
    return PayloadBuilder()


# Use Cases
def get_create_session_use_case() -> CreateSessionUseCase:
    """Get create session use case."""
    return CreateSessionUseCase(repository=get_repository())


def get_research_company_use_case() -> Optional[ResearchCompanyUseCase]:
    """Get research company use case."""
    perplexity = get_perplexity_adapter()
    if not perplexity:
        return None
    return ResearchCompanyUseCase(
        perplexity_adapter=perplexity,
        repository=get_repository(),
        context_repository=get_context_repository(),
    )


def get_synthesize_snapshot_use_case() -> Optional[SynthesizeSnapshotUseCase]:
    """Get synthesize snapshot use case."""
    gemini = get_gemini_adapter()
    if not gemini:
        return None
    return SynthesizeSnapshotUseCase(
        gemini_adapter=gemini,
        repository=get_repository(),
        context_repository=get_context_repository(),
    )


def get_collect_answers_use_case() -> CollectAnswersUseCase:
    """Get collect answers use case."""
    return CollectAnswersUseCase(repository=get_repository())


def get_execute_onboarding_use_case() -> ExecuteOnboardingUseCase:
    """Get execute onboarding use case."""
    settings = get_settings()
    return ExecuteOnboardingUseCase(
        payload_builder=get_payload_builder(),
        cgs_adapter=get_cgs_adapter(),
        brevo_adapter=get_brevo_adapter(),
        repository=get_repository(),
        auto_delivery=settings.enable_auto_delivery,
    )

