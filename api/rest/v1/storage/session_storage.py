"""In-memory session storage for Onboarding API.

This is a simple MVP implementation. In production, this should be replaced
with a persistent storage solution (e.g., PostgreSQL, Redis).
"""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from api.rest.v1.models.onboarding import OnboardingSessionResponse, SessionStatus


class SessionStorage:
    """In-memory session storage."""

    def __init__(self):
        """Initialize storage."""
        self._sessions: Dict[UUID, OnboardingSessionResponse] = {}

    def create_session(
        self,
        session_id: UUID,
        tenant_id: UUID,
        company_domain: str,
        user_email: str,
    ) -> OnboardingSessionResponse:
        """Create a new session."""
        now = datetime.utcnow()
        session = OnboardingSessionResponse(
            session_id=session_id,
            tenant_id=tenant_id,
            status=SessionStatus.RESEARCH,
            company_domain=company_domain,
            user_email=user_email,
            created_at=now,
            updated_at=now,
        )
        self._sessions[session_id] = session
        return session

    def get_session(self, session_id: UUID) -> Optional[OnboardingSessionResponse]:
        """Get a session by ID."""
        return self._sessions.get(session_id)

    def update_session(
        self,
        session_id: UUID,
        status: Optional[SessionStatus] = None,
        card_ids: Optional[List[UUID]] = None,
        cards_created_count: Optional[int] = None,
    ) -> Optional[OnboardingSessionResponse]:
        """Update a session."""
        session = self._sessions.get(session_id)
        if not session:
            return None

        if status is not None:
            session.status = status
        if card_ids is not None:
            session.card_ids = card_ids
        if cards_created_count is not None:
            session.cards_created_count = cards_created_count

        session.updated_at = datetime.utcnow()
        return session

    def list_sessions(self, tenant_id: Optional[UUID] = None) -> List[OnboardingSessionResponse]:
        """List all sessions, optionally filtered by tenant_id."""
        sessions = list(self._sessions.values())
        if tenant_id:
            sessions = [s for s in sessions if s.tenant_id == tenant_id]
        return sessions


# Global singleton instance
_session_storage: Optional[SessionStorage] = None


def get_session_storage() -> SessionStorage:
    """Get the global session storage instance."""
    global _session_storage
    if _session_storage is None:
        _session_storage = SessionStorage()
    return _session_storage

