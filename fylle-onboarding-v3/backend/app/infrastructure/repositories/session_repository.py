"""
Onboarding Session Repository for Fylle Onboarding v3
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from uuid import UUID

from supabase import Client


@dataclass
class Session:
    """Onboarding session data object."""
    id: UUID
    user_id: UUID
    state: str
    snapshot: Dict[str, Any]
    clarifying_questions: List[Dict[str, Any]]
    answers: Dict[str, Any]
    error_message: Optional[str]
    created_at: str
    updated_at: str


class SessionRepository:
    """Repository for onboarding session operations."""
    
    def __init__(self, supabase: Client):
        self.client = supabase
        self.table = "onboarding_sessions"
    
    async def create(
        self,
        id: UUID,
        user_id: UUID,
        state: str = "created",
    ) -> Session:
        """Create a new session."""
        data = {
            "id": str(id),
            "user_id": str(user_id),
            "state": state,
            "snapshot": {},
            "clarifying_questions": [],
            "answers": {},
        }
        
        response = self.client.table(self.table).insert(data).execute()
        
        if not response.data:
            raise Exception("Failed to create session")
        
        return self._to_entity(response.data[0])
    
    async def get(self, session_id: str) -> Optional[Session]:
        """Get session by ID."""
        try:
            response = self.client.table(self.table).select("*").eq("id", session_id).single().execute()
            
            if not response.data:
                return None
            
            return self._to_entity(response.data)
        except Exception:
            return None
    
    async def update(
        self,
        session_id: str,
        state: Optional[str] = None,
        snapshot: Optional[Dict[str, Any]] = None,
        clarifying_questions: Optional[List[Dict[str, Any]]] = None,
        answers: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
    ) -> Optional[Session]:
        """Update a session."""
        update_data = {}
        
        if state is not None:
            update_data["state"] = state
        if snapshot is not None:
            update_data["snapshot"] = snapshot
        if clarifying_questions is not None:
            update_data["clarifying_questions"] = clarifying_questions
        if answers is not None:
            update_data["answers"] = answers
        if error_message is not None:
            update_data["error_message"] = error_message
        
        if not update_data:
            return await self.get(session_id)
        
        response = self.client.table(self.table).update(update_data).eq("id", session_id).execute()
        
        if not response.data:
            return None
        
        return self._to_entity(response.data[0])
    
    async def get_by_user(self, user_id: str) -> List[Session]:
        """Get all sessions for a user."""
        response = self.client.table(self.table).select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        
        return [self._to_entity(row) for row in (response.data or [])]
    
    async def delete(self, session_id: str) -> bool:
        """Delete a session."""
        try:
            self.client.table(self.table).delete().eq("id", session_id).execute()
            return True
        except Exception:
            return False
    
    def _to_entity(self, data: dict) -> Session:
        """Convert database row to entity."""
        return Session(
            id=UUID(data["id"]),
            user_id=UUID(data["user_id"]),
            state=data["state"],
            snapshot=data.get("snapshot", {}),
            clarifying_questions=data.get("clarifying_questions", []),
            answers=data.get("answers", {}),
            error_message=data.get("error_message"),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
        )
