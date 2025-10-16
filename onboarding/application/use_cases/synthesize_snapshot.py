"""Use case for synthesizing company snapshot."""

import logging
from typing import Any, Dict, Optional
from uuid import UUID

from onboarding.domain.models import OnboardingSession, SessionState, CompanySnapshot
from onboarding.infrastructure.adapters.gemini_adapter import GeminiSynthesisAdapter
from onboarding.infrastructure.repositories.supabase_repository import SupabaseSessionRepository
from onboarding.infrastructure.repositories.company_context_repository import CompanyContextRepository

logger = logging.getLogger(__name__)


class SynthesizeSnapshotUseCase:
    """
    Use case for synthesizing company snapshot via Gemini.

    RAG-enabled: Loads snapshot from context if RAG hit, otherwise synthesizes.
    Saves new contexts to RAG after synthesis.
    """

    def __init__(
        self,
        gemini_adapter: GeminiSynthesisAdapter,
        repository: Optional[SupabaseSessionRepository] = None,
        context_repository: Optional[CompanyContextRepository] = None,
    ):
        """
        Initialize use case.

        Args:
            gemini_adapter: Gemini adapter for synthesis
            repository: Optional repository for persistence
            context_repository: Optional context repository for RAG
        """
        self.gemini = gemini_adapter
        self.repository = repository
        self.context_repository = context_repository
    
    async def execute(
        self, session: OnboardingSession, research_result: Dict[str, Any]
    ) -> CompanySnapshot:
        """
        Synthesize company snapshot with RAG support.

        Flow:
        1. If RAG hit: Load snapshot from research_result
        2. If RAG miss: Synthesize with Gemini, then save to RAG

        Args:
            session: OnboardingSession
            research_result: Research result from Perplexity (or RAG)

        Returns:
            CompanySnapshot with clarifying questions
        """
        logger.info(f"Synthesizing snapshot for: {session.brand_name}")

        # Update state
        session.update_state(SessionState.SYNTHESIZING)

        if self.repository:
            await self.repository.update_session_state(
                session.session_id, SessionState.SYNTHESIZING
            )

        try:
            # Check if this is a RAG hit
            is_rag_hit = research_result.get("rag_hit", False)

            if is_rag_hit:
                # RAG HIT: Load snapshot from context
                logger.info(
                    f"✅ RAG: Loading snapshot from context "
                    f"{research_result.get('context_id')}"
                )

                snapshot_dict = research_result.get("company_snapshot")
                if not snapshot_dict:
                    raise ValueError("RAG hit but no company_snapshot in research_result")

                # Parse snapshot from dict
                snapshot = CompanySnapshot(**snapshot_dict)

                logger.info(
                    f"✅ RAG: Snapshot loaded from cache "
                    f"({len(snapshot.clarifying_questions)} questions)"
                )

            else:
                # RAG MISS: Synthesize with Gemini
                logger.info("🤖 Gemini: Synthesizing new snapshot...")

                snapshot = await self.gemini.synthesize_snapshot(
                    brand_name=session.brand_name,
                    research_result=research_result,
                    trace_id=session.trace_id,
                )

                logger.info(
                    f"✅ Gemini: Snapshot synthesized "
                    f"({len(snapshot.clarifying_questions)} questions)"
                )

                # Save to RAG for future reuse
                if self.context_repository:
                    try:
                        logger.info("💾 RAG: Saving context for future reuse...")

                        context = await self.context_repository.create_context(
                            company_name=session.brand_name,
                            company_display_name=session.brand_name,
                            website=session.website,
                            snapshot=snapshot,
                            source_session_id=session.session_id,
                        )

                        # Link session to context
                        session.company_context_id = UUID(context["context_id"])

                        logger.info(
                            f"✅ RAG: Context saved {context['context_id']} "
                            f"(v{context['version']})"
                        )

                    except Exception as e:
                        logger.warning(f"RAG save failed (non-critical): {str(e)}")
                        # Don't fail the whole flow if RAG save fails

            # Update session
            session.snapshot = snapshot
            session.update_state(SessionState.AWAITING_USER)

            # Persist session
            if self.repository:
                await self.repository.save_session(session)

            logger.info(
                f"Snapshot ready: {len(snapshot.clarifying_questions)} questions"
            )

            return snapshot

        except Exception as e:
            logger.error(f"Synthesis failed: {str(e)}")
            session.mark_failed(f"Synthesis failed: {str(e)}")

            if self.repository:
                await self.repository.update_session_state(
                    session.session_id, SessionState.FAILED, str(e)
                )

            raise

