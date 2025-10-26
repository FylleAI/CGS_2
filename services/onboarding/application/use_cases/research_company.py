"""Use case for researching company."""

import logging
from typing import Any, Dict, Optional
from uuid import UUID

from services.onboarding.domain.models import OnboardingSession, SessionState, CompanySnapshot
from services.onboarding.infrastructure.adapters.perplexity_adapter import PerplexityAdapter
from services.onboarding.infrastructure.repositories.supabase_repository import SupabaseSessionRepository
from services.onboarding.infrastructure.repositories.company_context_repository import CompanyContextRepository

logger = logging.getLogger(__name__)


class ResearchCompanyUseCase:
    """
    Use case for researching company via Perplexity.

    RAG-enabled: Checks for existing context before calling Perplexity.
    Updates session state and returns research results.
    """

    def __init__(
        self,
        perplexity_adapter: PerplexityAdapter,
        repository: Optional[SupabaseSessionRepository] = None,
        context_repository: Optional[CompanyContextRepository] = None,
    ):
        """
        Initialize use case.

        Args:
            perplexity_adapter: Perplexity adapter for research
            repository: Optional repository for persistence
            context_repository: Optional context repository for RAG
        """
        self.perplexity = perplexity_adapter
        self.repository = repository
        self.context_repository = context_repository
    
    async def execute(self, session: OnboardingSession) -> Dict[str, Any]:
        """
        Research company with RAG lookup.

        Flow:
        1. Check RAG for existing context (if enabled)
        2. If found: Load snapshot, skip Perplexity, increment usage
        3. If not found: Call Perplexity as usual

        Args:
            session: OnboardingSession

        Returns:
            Research result dict (with 'rag_hit' flag if from cache)
        """
        logger.info(f"Researching company: {session.brand_name}")

        # Update state
        session.update_state(SessionState.RESEARCHING)

        if self.repository:
            await self.repository.update_session_state(
                session.session_id, SessionState.RESEARCHING
            )

        # RAG LOOKUP: Check for existing context
        if self.context_repository:
            try:
                logger.info(f"🔍 RAG: Checking for existing context...")
                existing_context = await self.context_repository.find_by_company_name(
                    company_name=session.brand_name,
                    max_age_days=30,  # Reuse contexts up to 30 days old
                )

                if existing_context:
                    logger.info(
                        f"✅ RAG HIT: Found context {existing_context['context_id']} "
                        f"(v{existing_context['version']}, "
                        f"used {existing_context['usage_count']} times)"
                    )

                    # Link session to context
                    session.company_context_id = UUID(existing_context["context_id"])

                    # Increment usage counter
                    await self.context_repository.increment_usage(
                        UUID(existing_context["context_id"])
                    )

                    # Store metadata
                    session.metadata["rag_hit"] = True
                    session.metadata["rag_context_id"] = existing_context["context_id"]
                    session.metadata["rag_context_version"] = existing_context["version"]
                    session.metadata["rag_context_age_days"] = (
                        existing_context.get("updated_at", "")
                    )

                    # Save session with context link
                    if self.repository:
                        await self.repository.save_session(session)

                    # Return mock research result (will be used by synthesize)
                    # The snapshot will be loaded from context in SynthesizeSnapshotUseCase
                    return {
                        "rag_hit": True,
                        "context_id": existing_context["context_id"],
                        "company_snapshot": existing_context["company_snapshot"],
                        "cost_usd": 0.0,  # No Perplexity cost
                        "usage_tokens": 0,
                        "duration_ms": 0,
                    }
                else:
                    logger.info(f"❌ RAG MISS: No context found, proceeding with Perplexity")
                    session.metadata["rag_hit"] = False

            except Exception as e:
                logger.warning(f"RAG lookup failed (non-critical): {str(e)}")
                # Continue with Perplexity if RAG fails
                session.metadata["rag_hit"] = False
                session.metadata["rag_error"] = str(e)

        # Get additional context from metadata
        additional_context = session.metadata.get("additional_context")

        try:
            # Execute research with retry (Perplexity)
            research_result = await self.perplexity.research_with_retry(
                brand_name=session.brand_name,
                website=session.website,
                additional_context=additional_context,
            )

            # Store research metadata in session
            session.metadata["research_cost_usd"] = research_result.get("cost_usd", 0)
            session.metadata["research_tokens"] = research_result.get("usage_tokens", 0)
            session.metadata["research_duration_ms"] = research_result.get("duration_ms", 0)
            session.metadata["rag_hit"] = False  # Explicit: this was NOT from RAG

            logger.info(
                f"Research completed: {research_result.get('usage_tokens', 0)} tokens, "
                f"${research_result.get('cost_usd', 0):.4f}"
            )

            return research_result

        except Exception as e:
            logger.error(f"Research failed: {str(e)}")
            session.mark_failed(f"Research failed: {str(e)}")

            if self.repository:
                await self.repository.update_session_state(
                    session.session_id, SessionState.FAILED, str(e)
                )

            raise

