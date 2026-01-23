"""
Prompt Loader for Fylle Onboarding v3
Handles loading prompts from YAML files and Supabase.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml


class YAMLPromptLoader:
    """Loads prompts from YAML files."""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    def load_file(self, relative_path: str) -> Dict[str, Any]:
        """Load a YAML file and return its contents."""
        if relative_path in self._cache:
            return self._cache[relative_path]
        
        full_path = self.base_dir / relative_path
        if not full_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {full_path}")
        
        with open(full_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        self._cache[relative_path] = data
        return data
    
    def get_prompt(self, file_path: str, prompt_key: str) -> Optional[str]:
        """
        Get a specific prompt from a YAML file.
        
        Args:
            file_path: Path to YAML file (relative to base_dir)
            prompt_key: Dot-separated key to the prompt
            
        Returns:
            Prompt template string or None
        """
        try:
            data = self.load_file(file_path)
        except FileNotFoundError:
            return None
        
        # Navigate to the prompt
        current = data
        for key in prompt_key.split('.'):
            if isinstance(current, dict):
                current = current.get(key)
            else:
                return None
        
        if isinstance(current, str):
            return current
        elif isinstance(current, dict) and 'template' in current:
            return current['template']
        
        return None
    
    def list_prompts(self, file_path: str) -> List[str]:
        """List all prompt keys in a YAML file."""
        try:
            data = self.load_file(file_path)
        except FileNotFoundError:
            return []
        
        prompts = data.get('prompts', {})
        return self._extract_keys(prompts)
    
    def _extract_keys(self, data: Any, prefix: str = '') -> List[str]:
        """Recursively extract all keys from nested dict."""
        keys = []
        if isinstance(data, dict):
            for key, value in data.items():
                full_key = f"{prefix}.{key}" if prefix else key
                if isinstance(value, str):
                    keys.append(full_key)
                elif isinstance(value, dict):
                    if 'template' in value:
                        keys.append(full_key)
                    else:
                        keys.extend(self._extract_keys(value, full_key))
        return keys
    
    def reload(self, file_path: Optional[str] = None):
        """Clear cache and reload files."""
        if file_path:
            self._cache.pop(file_path, None)
        else:
            self._cache.clear()


class SupabasePromptRepository:
    """Repository for prompts stored in Supabase."""
    
    def __init__(self, supabase_client):
        self.client = supabase_client
        self.table = 'prompts'
    
    async def get_prompt(self, key: str) -> Optional[Dict[str, Any]]:
        """Get a prompt by key."""
        try:
            response = self.client.table(self.table).select('*').eq('key', key).eq('is_active', True).single().execute()
            return response.data
        except Exception:
            return None
    
    async def get_all_prompts(self) -> List[Dict[str, Any]]:
        """Get all active prompts."""
        try:
            response = self.client.table(self.table).select('*').eq('is_active', True).execute()
            return response.data or []
        except Exception:
            return []
    
    async def create_prompt(
        self,
        key: str,
        template: str,
        description: Optional[str] = None,
        variables: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Create a new prompt."""
        data = {
            'key': key,
            'template': template,
            'description': description,
            'variables': variables or [],
            'is_active': True,
            'version': 1,
        }
        response = self.client.table(self.table).insert(data).execute()
        return response.data[0]
    
    async def update_prompt(
        self,
        key: str,
        template: str,
        increment_version: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """Update an existing prompt."""
        existing = await self.get_prompt(key)
        if not existing:
            return None
        
        data = {'template': template}
        if increment_version:
            data['version'] = existing.get('version', 0) + 1
        
        response = self.client.table(self.table).update(data).eq('key', key).execute()
        return response.data[0] if response.data else None
    
    async def deactivate_prompt(self, key: str) -> bool:
        """Deactivate a prompt (soft delete)."""
        try:
            self.client.table(self.table).update({'is_active': False}).eq('key', key).execute()
            return True
        except Exception:
            return False
