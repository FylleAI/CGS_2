"""Use case for collecting user answers."""

import logging
from typing import Any, Dict, Optional
from uuid import UUID

from onboarding.domain.models import OnboardingSession, SessionState
from onboarding.infrastructure.repositories.supabase_repository import SupabaseSessionRepository

logger = logging.getLogger(__name__)


class CollectAnswersUseCase:
    """
    Use case for collecting and validating user answers.
    
    Validates answers against clarifying questions and updates snapshot.
    """
    
    def __init__(self, repository: Optional[SupabaseSessionRepository] = None):
        """
        Initialize use case.
        
        Args:
            repository: Optional repository for persistence
        """
        self.repository = repository
    
    async def execute(
        self, session: OnboardingSession, answers: Dict[str, Any]
    ) -> OnboardingSession:
        """
        Collect and validate answers.
        
        Args:
            session: OnboardingSession with snapshot
            answers: Dict of question_id -> answer
        
        Returns:
            Updated OnboardingSession
        """
        logger.info(f"Collecting answers for session: {session.session_id}")
        
        if not session.snapshot:
            raise ValueError("Session has no snapshot")
        
        if session.state != SessionState.AWAITING_USER:
            raise ValueError(f"Invalid state for collecting answers: {session.state}")
        
        # Validate and add answers
        for question_id, answer in answers.items():
            # Find question
            question = next(
                (q for q in session.snapshot.clarifying_questions if q.id == question_id),
                None,
            )
            
            if not question:
                logger.warning(f"Unknown question ID: {question_id}")
                continue
            
            # Validate answer type
            self._validate_answer(question, answer)
            
            # Add answer
            session.snapshot.add_answer(question_id, answer)
            logger.debug(f"Answer added: {question_id} = {answer}")
        
        # Check completeness
        if not session.snapshot.is_complete():
            missing = [
                q.id
                for q in session.snapshot.clarifying_questions
                if q.required and q.id not in session.snapshot.clarifying_answers
            ]
            raise ValueError(f"Missing required answers: {missing}")
        
        # Update state
        session.update_state(SessionState.PAYLOAD_READY)
        
        # Persist
        if self.repository:
            await self.repository.save_session(session)
        
        logger.info(f"Answers collected: {len(answers)} answers")
        
        return session
    
    def _validate_answer(self, question, answer: Any) -> None:
        """Validate answer against question type."""
        expected_type = question.expected_response_type
        
        if expected_type == "boolean":
            if not isinstance(answer, bool):
                raise ValueError(
                    f"Question {question.id} expects boolean, got {type(answer)}"
                )
        
        elif expected_type == "number":
            if not isinstance(answer, (int, float)):
                raise ValueError(
                    f"Question {question.id} expects number, got {type(answer)}"
                )
        
        elif expected_type == "enum":
            if question.options and answer not in question.options:
                raise ValueError(
                    f"Question {question.id} expects one of {question.options}, got {answer}"
                )
        
        elif expected_type == "string":
            if not isinstance(answer, str):
                raise ValueError(
                    f"Question {question.id} expects string, got {type(answer)}"
                )

