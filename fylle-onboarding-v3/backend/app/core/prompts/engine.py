"""
Prompt Engine for Fylle Onboarding v3
Resolves prompts from YAML defaults with Supabase dynamic overrides.
"""

from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from jinja2 import Environment, BaseLoader, TemplateNotFound


class PromptEngine:
    """
    Resolves and renders prompt templates.
    
    Priority order:
    1. Supabase prompt overrides (if active)
    2. YAML file defaults
    
    Supports Jinja2 templating for variable interpolation.
    """
    
    def __init__(
        self,
        yaml_prompts_dir: Path,
        supabase_repository: Optional[Any] = None,
    ):
        self.yaml_prompts_dir = yaml_prompts_dir
        self.supabase_repo = supabase_repository
        self._template_cache: Dict[str, str] = {}
        
        # Initialize Jinja2 environment
        self.jinja_env = Environment(
            loader=BaseLoader(),
            variable_start_string='{{',
            variable_end_string='}}',
            autoescape=False,
        )
    
    async def get_prompt(
        self,
        key: str,
        variables: Optional[Dict[str, Any]] = None,
        use_cache: bool = True,
    ) -> str:
        """
        Get and render a prompt template.
        
        Args:
            key: Prompt key (e.g., "brief.newsletter.questions")
            variables: Variables to interpolate into the template
            use_cache: Whether to use cached templates
            
        Returns:
            Rendered prompt string
        """
        variables = variables or {}
        
        # Try to get template from cache
        template_str = None
        if use_cache and key in self._template_cache:
            template_str = self._template_cache[key]
        
        if template_str is None:
            # 1. Check Supabase for override
            if self.supabase_repo:
                override = await self.supabase_repo.get_prompt(key)
                if override and override.get('is_active', True):
                    template_str = override.get('template', '')
            
            # 2. Fall back to YAML
            if not template_str:
                template_str = self._load_yaml_prompt(key)
            
            # Cache for future use
            if use_cache and template_str:
                self._template_cache[key] = template_str
        
        if not template_str:
            raise ValueError(f"Prompt not found: {key}")
        
        # Render with Jinja2
        return self._render(template_str, variables)
    
    def _load_yaml_prompt(self, key: str) -> Optional[str]:
        """
        Load a prompt from YAML file.
        
        Key format: "category.subcategory.name" maps to:
        yaml_prompts_dir/category/subcategory.yaml -> prompts.name
        
        Or simpler: "category.name" maps to:
        yaml_prompts_dir/category.yaml -> prompts.name
        """
        parts = key.split('.')
        
        if len(parts) < 2:
            return None
        
        # Try nested path first: category/subcategory.yaml
        if len(parts) >= 3:
            yaml_path = self.yaml_prompts_dir / parts[0] / f"{parts[1]}.yaml"
            prompt_name = '.'.join(parts[2:])
            
            if yaml_path.exists():
                return self._extract_from_yaml(yaml_path, prompt_name)
        
        # Try flat path: category.yaml
        yaml_path = self.yaml_prompts_dir / f"{parts[0]}.yaml"
        prompt_name = '.'.join(parts[1:])
        
        if yaml_path.exists():
            return self._extract_from_yaml(yaml_path, prompt_name)
        
        return None
    
    def _extract_from_yaml(self, yaml_path: Path, prompt_name: str) -> Optional[str]:
        """Extract a specific prompt from a YAML file."""
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Navigate to prompts section
            prompts = data.get('prompts', data)
            
            # Support nested keys like "questions.system"
            for part in prompt_name.split('.'):
                if isinstance(prompts, dict):
                    prompts = prompts.get(part)
                else:
                    return None
            
            if isinstance(prompts, str):
                return prompts
            elif isinstance(prompts, dict) and 'template' in prompts:
                return prompts['template']
            
            return None
        except Exception:
            return None
    
    def _render(self, template_str: str, variables: Dict[str, Any]) -> str:
        """Render a template string with variables."""
        try:
            template = self.jinja_env.from_string(template_str)
            return template.render(**variables)
        except Exception as e:
            # If rendering fails, return template with basic string replacement
            result = template_str
            for key, value in variables.items():
                result = result.replace(f"{{{{{key}}}}}", str(value))
            return result
    
    def clear_cache(self, key: Optional[str] = None):
        """Clear the template cache."""
        if key:
            self._template_cache.pop(key, None)
        else:
            self._template_cache.clear()
    
    def register_prompt(self, key: str, template: str):
        """Register a prompt template in memory (useful for testing)."""
        self._template_cache[key] = template


class PromptBuilder:
    """
    Helper class for building complex prompts.
    """
    
    def __init__(self):
        self._parts: list = []
    
    def add_section(self, title: str, content: str) -> 'PromptBuilder':
        """Add a titled section."""
        self._parts.append(f"## {title}\n\n{content}")
        return self
    
    def add_paragraph(self, text: str) -> 'PromptBuilder':
        """Add a paragraph."""
        self._parts.append(text)
        return self
    
    def add_list(self, items: list, ordered: bool = False) -> 'PromptBuilder':
        """Add a list of items."""
        if ordered:
            formatted = "\n".join(f"{i+1}. {item}" for i, item in enumerate(items))
        else:
            formatted = "\n".join(f"- {item}" for item in items)
        self._parts.append(formatted)
        return self
    
    def add_json_schema(self, schema: Dict[str, Any]) -> 'PromptBuilder':
        """Add a JSON schema as a code block."""
        import json
        self._parts.append(f"```json\n{json.dumps(schema, indent=2)}\n```")
        return self
    
    def add_context(self, context: Dict[str, Any]) -> 'PromptBuilder':
        """Add context data as a formatted section."""
        lines = []
        for key, value in context.items():
            if isinstance(value, list):
                lines.append(f"**{key}:**")
                for item in value:
                    lines.append(f"  - {item}")
            elif isinstance(value, dict):
                lines.append(f"**{key}:**")
                for k, v in value.items():
                    lines.append(f"  - {k}: {v}")
            else:
                lines.append(f"**{key}:** {value}")
        self._parts.append("\n".join(lines))
        return self
    
    def build(self) -> str:
        """Build the final prompt string."""
        return "\n\n".join(self._parts)
