"""
Pack Repository for Fylle Onboarding v3
"""

from typing import List, Optional
from uuid import UUID

from supabase import Client

from app.domain.entities import Pack


class PackRepository:
    """Repository for pack operations."""
    
    def __init__(self, supabase: Client):
        self.client = supabase
        self.table = "packs"
    
    async def get_all(self, active_only: bool = True) -> List[Pack]:
        """Get all packs."""
        query = self.client.table(self.table).select("*")
        
        if active_only:
            query = query.eq("is_active", True)
        
        response = query.execute()
        
        return [self._to_entity(row) for row in (response.data or [])]
    
    async def get(self, pack_id: str) -> Optional[Pack]:
        """Get pack by ID."""
        try:
            response = self.client.table(self.table).select("*").eq("id", pack_id).single().execute()
            
            if not response.data:
                return None
            
            return self._to_entity(response.data)
        except Exception:
            return None
    
    async def get_by_name(self, name: str) -> Optional[Pack]:
        """Get pack by name."""
        try:
            response = self.client.table(self.table).select("*").eq("name", name).single().execute()
            
            if not response.data:
                return None
            
            return self._to_entity(response.data)
        except Exception:
            return None
    
    def _to_entity(self, data: dict) -> Pack:
        """Convert database row to entity."""
        return Pack(
            id=UUID(data["id"]),
            name=data["name"],
            display_name=data["display_name"],
            description=data.get("description"),
            icon=data.get("icon"),
            prompt_template_key=data.get("prompt_template_key"),
            is_active=data.get("is_active", True),
            created_at=data.get("created_at"),
        )
