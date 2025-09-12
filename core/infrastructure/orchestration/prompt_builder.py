"""Centralized prompt builder for composing agent prompts."""
from typing import Any, Dict

from ..utils.template_utils import substitute_task_description


def build(agent: Any, prompt_template: str, context: Dict[str, Any]) -> str:
    """Build final prompt for an agent using a template and context.

    Args:
        agent: Agent instance (unused but allows future customisation).
        prompt_template: Raw prompt template with placeholders.
        context: Execution context providing variables and overrides.

    Returns:
        Final prompt string ready for agent execution.
    """
    # Substitute context variables into template
    prompt = substitute_task_description(prompt_template, context)

    # Client specific overrides (disclaimers, extra instructions)
    client_overrides = context.get("client_overrides") or {}
    extra_instructions = client_overrides.get("additional_instructions") or client_overrides.get("disclaimer")
    if extra_instructions:
        prompt += f"\n\n{extra_instructions}"

    return prompt
