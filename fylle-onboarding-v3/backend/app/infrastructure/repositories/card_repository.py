"""
Card Repository for Fylle Onboarding v3
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from supabase import Client

from app.domain.entities import Card, CardType


class CardRepository:
    """Repository for card operations."""
    
    def __init__(self, supabase: Client):
        self.client = supabase
        self.table = "cards"
    
    async def create(
        self,
        user_id: str,
        type: str,
        title: str,
        data: Dict[str, Any],
    ) -> Card:
        """Create a new card."""
        card_data = {
            "user_id": str(user_id),
            "type": type,
            "title": title,
            "data": data,
        }
        
        response = self.client.table(self.table).insert(card_data).execute()
        
        if not response.data:
            raise Exception("Failed to create card")
        
        return self._to_entity(response.data[0])
    
    async def get(self, card_id: str) -> Optional[Card]:
        """Get card by ID."""
        response = self.client.table(self.table).select("*").eq("id", card_id).single().execute()
        
        if not response.data:
            return None
        
        return self._to_entity(response.data)
    
    async def get_by_user(
        self,
        user_id: str,
        card_type: Optional[str] = None,
    ) -> List[Card]:
        """Get all cards for a user, optionally filtered by type."""
        query = self.client.table(self.table).select("*").eq("user_id", user_id)
        
        if card_type:
            query = query.eq("type", card_type)
        
        response = query.execute()
        
        return [self._to_entity(row) for row in (response.data or [])]
    
    async def update(
        self,
        card_id: str,
        title: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Optional[Card]:
        """Update a card."""
        update_data = {}
        if title is not None:
            update_data["title"] = title
        if data is not None:
            update_data["data"] = data
        
        if not update_data:
            return await self.get(card_id)
        
        response = self.client.table(self.table).update(update_data).eq("id", card_id).execute()
        
        if not response.data:
            return None
        
        return self._to_entity(response.data[0])
    
    async def delete(self, card_id: str) -> bool:
        """Delete a card."""
        try:
            self.client.table(self.table).delete().eq("id", card_id).execute()
            return True
        except Exception:
            return False
    
    async def delete_by_user(self, user_id: str) -> int:
        """Delete all cards for a user."""
        response = self.client.table(self.table).delete().eq("user_id", user_id).execute()
        return len(response.data or [])
    
    def _to_entity(self, data: dict) -> Card:
        """Convert database row to entity."""
        return Card(
            id=UUID(data["id"]),
            user_id=UUID(data["user_id"]),
            type=CardType(data["type"]),
            title=data["title"],
            data=data.get("data", {}),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
