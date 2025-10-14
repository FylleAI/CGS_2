"""Use case for synthesizing company snapshot."""

import logging
from typing import Any, Dict, Optional

from onboarding.domain.models import OnboardingSession, SessionState, CompanySnapshot
from onboarding.infrastructure.adapters.gemini_adapter import GeminiSynthesisAdapter
from onboarding.infrastructure.repositories.supabase_repository import SupabaseSessionRepository

logger = logging.getLogger(__name__)


class SynthesizeSnapshotUseCase:
    """
    Use case for synthesizing company snapshot via Gemini.
    
    Generates structured snapshot with clarifying questions.
    """
    
    def __init__(
        self,
        gemini_adapter: GeminiSynthesisAdapter,
        repository: Optional[SupabaseSessionRepository] = None,
    ):
        """
        Initialize use case.
        
        Args:
            gemini_adapter: Gemini adapter for synthesis
            repository: Optional repository for persistence
        """
        self.gemini = gemini_adapter
        self.repository = repository
    
    async def execute(
        self, session: OnboardingSession, research_result: Dict[str, Any]
    ) -> CompanySnapshot:
        """
        Synthesize company snapshot.
        
        Args:
            session: OnboardingSession
            research_result: Research result from Perplexity
        
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
            # Synthesize snapshot
            snapshot = await self.gemini.synthesize_snapshot(
                brand_name=session.brand_name,
                research_result=research_result,
                trace_id=session.trace_id,
            )
            
            # Update session
            session.snapshot = snapshot
            session.update_state(SessionState.AWAITING_USER)
            
            # Persist
            if self.repository:
                await self.repository.save_session(session)
            
            logger.info(
                f"Snapshot synthesized: {len(snapshot.clarifying_questions)} questions"
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

