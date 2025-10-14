"""Use case for researching company."""

import logging
from typing import Any, Dict, Optional

from onboarding.domain.models import OnboardingSession, SessionState
from onboarding.infrastructure.adapters.perplexity_adapter import PerplexityAdapter
from onboarding.infrastructure.repositories.supabase_repository import SupabaseSessionRepository

logger = logging.getLogger(__name__)


class ResearchCompanyUseCase:
    """
    Use case for researching company via Perplexity.
    
    Updates session state and returns research results.
    """
    
    def __init__(
        self,
        perplexity_adapter: PerplexityAdapter,
        repository: Optional[SupabaseSessionRepository] = None,
    ):
        """
        Initialize use case.
        
        Args:
            perplexity_adapter: Perplexity adapter for research
            repository: Optional repository for persistence
        """
        self.perplexity = perplexity_adapter
        self.repository = repository
    
    async def execute(self, session: OnboardingSession) -> Dict[str, Any]:
        """
        Research company.
        
        Args:
            session: OnboardingSession
        
        Returns:
            Research result dict
        """
        logger.info(f"Researching company: {session.brand_name}")
        
        # Update state
        session.update_state(SessionState.RESEARCHING)
        
        if self.repository:
            await self.repository.update_session_state(
                session.session_id, SessionState.RESEARCHING
            )
        
        # Get additional context from metadata
        additional_context = session.metadata.get("additional_context")
        
        try:
            # Execute research with retry
            research_result = await self.perplexity.research_with_retry(
                brand_name=session.brand_name,
                website=session.website,
                additional_context=additional_context,
            )
            
            # Store research metadata in session
            session.metadata["research_cost_usd"] = research_result.get("cost_usd", 0)
            session.metadata["research_tokens"] = research_result.get("usage_tokens", 0)
            session.metadata["research_duration_ms"] = research_result.get("duration_ms", 0)
            
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

