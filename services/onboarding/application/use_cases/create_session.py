"""Use case for creating onboarding session."""

import logging
from typing import Optional

from onboarding.domain.models import OnboardingSession, OnboardingInput, SessionState
from onboarding.infrastructure.repositories.supabase_repository import SupabaseSessionRepository

logger = logging.getLogger(__name__)


class CreateSessionUseCase:
    """
    Use case for creating a new onboarding session.
    
    Creates session and optionally persists to Supabase.
    """
    
    def __init__(self, repository: Optional[SupabaseSessionRepository] = None):
        """
        Initialize use case.
        
        Args:
            repository: Optional Supabase repository for persistence
        """
        self.repository = repository
    
    async def execute(self, input_data: OnboardingInput) -> OnboardingSession:
        """
        Create onboarding session.
        
        Args:
            input_data: OnboardingInput with brand info and goal
        
        Returns:
            Created OnboardingSession
        """
        logger.info(f"Creating session for: {input_data.brand_name}")
        
        # Create session
        session = OnboardingSession(
            brand_name=input_data.brand_name,
            website=input_data.website,
            goal=input_data.goal,
            user_email=input_data.user_email,
            state=SessionState.CREATED,
        )
        
        # Add additional context to metadata
        if input_data.additional_context:
            session.metadata["additional_context"] = input_data.additional_context
        
        logger.info(
            f"Session created: id={session.session_id}, trace={session.trace_id}"
        )
        
        # Persist if repository available
        if self.repository:
            try:
                await self.repository.save_session(session)
                logger.info(f"Session persisted: {session.session_id}")
            except Exception as e:
                logger.warning(f"Failed to persist session: {str(e)}")
                # Continue anyway - persistence is optional
        
        return session

