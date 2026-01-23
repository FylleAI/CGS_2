"""
Brief Repository for Fylle Onboarding v3
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from supabase import Client

from app.domain.entities import Brief, BriefDocument


class BriefRepository:
    """Repository for brief operations."""
    
    def __init__(self, supabase: Client):
        self.client = supabase
        self.table = "briefs"
    
    async def create(
        self,
        user_id: str,
        pack_id: str,
        title: Optional[str] = None,
        content: Optional[Dict[str, Any]] = None,
        answers: Optional[Dict[str, str]] = None,
        context_snapshot: Optional[Dict[str, Any]] = None,
        llm_provider: Optional[str] = None,
        llm_model: Optional[str] = None,
        generation_time_ms: Optional[int] = None,
    ) -> Brief:
        """Create a new brief."""
        data = {
            "user_id": str(user_id),
            "pack_id": str(pack_id),
            "title": title,
            "content": content or {},
            "answers": answers or {},
            "context_snapshot": context_snapshot or {},
            "llm_provider": llm_provider,
            "llm_model": llm_model,
            "generation_time_ms": generation_time_ms,
        }
        
        response = self.client.table(self.table).insert(data).execute()
        
        if not response.data:
            raise Exception("Failed to create brief")
        
        return self._to_entity(response.data[0])
    
    async def get(self, brief_id: str) -> Optional[Brief]:
        """Get brief by ID."""
        try:
            response = self.client.table(self.table).select("*").eq("id", brief_id).single().execute()
            
            if not response.data:
                return None
            
            return self._to_entity(response.data)
        except Exception:
            return None
    
    async def get_by_user(
        self,
        user_id: str,
        pack_id: Optional[str] = None,
    ) -> List[Brief]:
        """Get all briefs for a user, optionally filtered by pack."""
        query = self.client.table(self.table).select("*").eq("user_id", user_id)
        
        if pack_id:
            query = query.eq("pack_id", pack_id)
        
        response = query.order("created_at", desc=True).execute()
        
        return [self._to_entity(row) for row in (response.data or [])]
    
    async def delete(self, brief_id: str) -> bool:
        """Delete a brief."""
        try:
            self.client.table(self.table).delete().eq("id", brief_id).execute()
            return True
        except Exception:
            return False
    
    def _to_entity(self, data: dict) -> Brief:
        """Convert database row to entity."""
        content_data = data.get("content", {})
        
        return Brief(
            id=UUID(data["id"]),
            user_id=UUID(data["user_id"]),
            pack_id=UUID(data["pack_id"]),
            title=data.get("title"),
            content=BriefDocument(**content_data) if content_data else BriefDocument(),
            answers=data.get("answers", {}),
            context_snapshot=data.get("context_snapshot", {}),
            llm_provider=data.get("llm_provider"),
            llm_model=data.get("llm_model"),
            generation_time_ms=data.get("generation_time_ms"),
            created_at=data.get("created_at"),
        )
