"""Supabase repository for onboarding session persistence.

Handles CRUD operations for onboarding sessions in Supabase.
"""

import logging
from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import datetime

from supabase import create_client, Client

from onboarding.config.settings import OnboardingSettings
from onboarding.domain.models import OnboardingSession, SessionState

logger = logging.getLogger(__name__)


class SupabaseSessionRepository:
    """
    Repository for persisting onboarding sessions to Supabase.
    
    Handles session CRUD operations and state tracking.
    """
    
    TABLE_NAME = "onboarding_sessions"
    
    def __init__(self, settings: OnboardingSettings):
        """
        Initialize Supabase repository.
        
        Args:
            settings: Onboarding settings with Supabase configuration
        """
        self.settings = settings
        
        if not settings.is_supabase_configured():
            raise ValueError("Supabase not configured")
        
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_anon_key,
        )
        
        logger.info(f"Supabase repository initialized: {settings.supabase_url}")
    
    async def save_session(self, session: OnboardingSession) -> None:
        """
        Save or update session.
        
        Args:
            session: OnboardingSession to persist
        """
        logger.info(f"Saving session: {session.session_id}")
        
        data = self._session_to_dict(session)
        
        try:
            # Upsert (insert or update)
            result = self.client.table(self.TABLE_NAME).upsert(data).execute()
            
            logger.info(f"Session saved: {session.session_id}")
            
        except Exception as e:
            logger.error(f"Failed to save session: {str(e)}")
            raise
    
    async def get_session(self, session_id: UUID) -> Optional[OnboardingSession]:
        """
        Get session by ID.
        
        Args:
            session_id: Session UUID
        
        Returns:
            OnboardingSession or None if not found
        """
        logger.info(f"Fetching session: {session_id}")
        
        try:
            result = (
                self.client.table(self.TABLE_NAME)
                .select("*")
                .eq("session_id", str(session_id))
                .execute()
            )
            
            if not result.data:
                logger.warning(f"Session not found: {session_id}")
                return None
            
            session = self._dict_to_session(result.data[0])
            logger.info(f"Session fetched: {session_id}")
            
            return session
            
        except Exception as e:
            logger.error(f"Failed to fetch session: {str(e)}")
            raise
    
    async def update_session_state(
        self, session_id: UUID, state: SessionState, error_message: Optional[str] = None
    ) -> None:
        """
        Update session state.
        
        Args:
            session_id: Session UUID
            state: New state
            error_message: Optional error message if failed
        """
        logger.info(f"Updating session state: {session_id} -> {state}")
        
        data = {
            "state": state.value,
            "updated_at": datetime.utcnow().isoformat(),
        }
        
        if error_message:
            data["error_message"] = error_message
        
        try:
            result = (
                self.client.table(self.TABLE_NAME)
                .update(data)
                .eq("session_id", str(session_id))
                .execute()
            )
            
            logger.info(f"Session state updated: {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to update session state: {str(e)}")
            raise
    
    async def list_sessions(
        self,
        limit: int = 50,
        offset: int = 0,
        state: Optional[SessionState] = None,
    ) -> List[OnboardingSession]:
        """
        List sessions with optional filtering.
        
        Args:
            limit: Max number of sessions to return
            offset: Offset for pagination
            state: Optional state filter
        
        Returns:
            List of OnboardingSession
        """
        logger.info(f"Listing sessions: limit={limit}, offset={offset}, state={state}")
        
        try:
            query = self.client.table(self.TABLE_NAME).select("*")
            
            if state:
                query = query.eq("state", state.value)
            
            result = (
                query.order("created_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )
            
            sessions = [self._dict_to_session(row) for row in result.data]
            
            logger.info(f"Found {len(sessions)} sessions")
            
            return sessions
            
        except Exception as e:
            logger.error(f"Failed to list sessions: {str(e)}")
            raise
    
    async def delete_session(self, session_id: UUID) -> None:
        """
        Delete session.
        
        Args:
            session_id: Session UUID
        """
        logger.info(f"Deleting session: {session_id}")
        
        try:
            result = (
                self.client.table(self.TABLE_NAME)
                .delete()
                .eq("session_id", str(session_id))
                .execute()
            )
            
            logger.info(f"Session deleted: {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to delete session: {str(e)}")
            raise
    
    def _session_to_dict(self, session: OnboardingSession) -> Dict[str, Any]:
        """Convert OnboardingSession to dict for Supabase."""
        return {
            "session_id": str(session.session_id),
            "trace_id": session.trace_id,
            "brand_name": session.brand_name,
            "website": session.website,
            "goal": session.goal.value,
            "user_email": session.user_email,
            "state": session.state.value,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "snapshot": session.snapshot.model_dump(mode="json") if session.snapshot else None,
            "cgs_payload": session.cgs_payload,
            "cgs_run_id": str(session.cgs_run_id) if session.cgs_run_id else None,
            "cgs_response": session.cgs_response,
            "delivery_status": session.delivery_status,
            "delivery_message_id": session.delivery_message_id,
            "delivery_timestamp": session.delivery_timestamp.isoformat() if session.delivery_timestamp else None,
            "error_message": session.error_message,
            "metadata": session.metadata,
        }
    
    def _dict_to_session(self, data: Dict[str, Any]) -> OnboardingSession:
        """Convert Supabase dict to OnboardingSession."""
        from onboarding.domain.models import OnboardingGoal, CompanySnapshot
        
        # Parse snapshot if present
        snapshot = None
        if data.get("snapshot"):
            snapshot = CompanySnapshot(**data["snapshot"])
        
        # Parse timestamps
        created_at = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
        updated_at = datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))
        
        delivery_timestamp = None
        if data.get("delivery_timestamp"):
            delivery_timestamp = datetime.fromisoformat(
                data["delivery_timestamp"].replace("Z", "+00:00")
            )
        
        return OnboardingSession(
            session_id=UUID(data["session_id"]),
            trace_id=data["trace_id"],
            brand_name=data["brand_name"],
            website=data.get("website"),
            goal=OnboardingGoal(data["goal"]),
            user_email=data.get("user_email"),
            state=SessionState(data["state"]),
            created_at=created_at,
            updated_at=updated_at,
            snapshot=snapshot,
            cgs_payload=data.get("cgs_payload"),
            cgs_run_id=UUID(data["cgs_run_id"]) if data.get("cgs_run_id") else None,
            cgs_response=data.get("cgs_response"),
            delivery_status=data.get("delivery_status"),
            delivery_message_id=data.get("delivery_message_id"),
            delivery_timestamp=delivery_timestamp,
            error_message=data.get("error_message"),
            metadata=data.get("metadata", {}),
        )


def get_session_repository(
    settings: Optional[OnboardingSettings] = None,
) -> Optional[SupabaseSessionRepository]:
    """
    Factory function to get session repository.
    
    Args:
        settings: Optional settings (will use default if not provided)
    
    Returns:
        SupabaseSessionRepository or None if not configured
    """
    if settings is None:
        from onboarding.config.settings import get_onboarding_settings
        settings = get_onboarding_settings()
    
    if not settings.is_supabase_configured():
        logger.warning("Supabase not configured, repository unavailable")
        return None
    
    return SupabaseSessionRepository(settings)

