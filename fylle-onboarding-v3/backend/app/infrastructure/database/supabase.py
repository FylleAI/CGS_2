"""
Supabase Client for Fylle Onboarding v3
"""

from functools import lru_cache

from supabase import create_client, Client

from app.config.settings import get_settings


@lru_cache()
def get_supabase_client() -> Client:
    """Get cached Supabase client instance."""
    settings = get_settings()
    return create_client(
        settings.supabase_url,
        settings.supabase_service_role_key,  # Use service role for backend
    )


class SupabaseClient:
    """Wrapper for Supabase client with helper methods."""
    
    def __init__(self, client: Client):
        self.client = client
    
    def table(self, name: str):
        """Get a table reference."""
        return self.client.table(name)
    
    async def execute_rpc(self, function_name: str, params: dict = None):
        """Execute a stored procedure."""
        return self.client.rpc(function_name, params or {}).execute()
