"""
User Repository for Fylle Onboarding v3
"""

from typing import Optional
from uuid import UUID

from supabase import Client

from app.domain.entities import User


class UserRepository:
    """Repository for user operations."""
    
    def __init__(self, supabase: Client):
        self.client = supabase
        self.table = "users"
    
    async def create(
        self,
        email: str,
        brand_name: Optional[str] = None,
        website: Optional[str] = None,
    ) -> User:
        """Create a new user."""
        data = {
            "email": email,
            "brand_name": brand_name,
            "website": website,
        }
        
        response = self.client.table(self.table).insert(data).execute()
        
        if not response.data:
            raise Exception("Failed to create user")
        
        return self._to_entity(response.data[0])
    
    async def get(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        response = self.client.table(self.table).select("*").eq("id", user_id).single().execute()
        
        if not response.data:
            return None
        
        return self._to_entity(response.data)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        try:
            response = self.client.table(self.table).select("*").eq("email", email).single().execute()
            
            if not response.data:
                return None
            
            return self._to_entity(response.data)
        except Exception:
            return None
    
    async def update(self, user_id: str, **kwargs) -> Optional[User]:
        """Update user."""
        response = self.client.table(self.table).update(kwargs).eq("id", user_id).execute()
        
        if not response.data:
            return None
        
        return self._to_entity(response.data[0])
    
    async def delete(self, user_id: str) -> bool:
        """Delete user."""
        try:
            self.client.table(self.table).delete().eq("id", user_id).execute()
            return True
        except Exception:
            return False
    
    def _to_entity(self, data: dict) -> User:
        """Convert database row to entity."""
        return User(
            id=UUID(data["id"]),
            email=data["email"],
            brand_name=data.get("brand_name"),
            website=data.get("website"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
