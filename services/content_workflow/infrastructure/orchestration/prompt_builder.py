"""Centralized prompt builder for composing agent prompts with template rendering.

- Uses Jinja2 if available to support expressions (e.g., arithmetic, indexing)
- Falls back to simple variable substitution otherwise
"""

from typing import Any, Dict
import logging

from ..utils.template_utils import substitute_task_description

logger = logging.getLogger(__name__)


def build(agent: Any, prompt_template: str, context: Dict[str, Any]) -> str:
    """Build final prompt for an agent using a template and context.

    Args:
        agent: Agent instance (currently unused, reserved for future customization)
        prompt_template: Raw prompt template (markdown) with placeholders
        context: Execution context providing variables and overrides

    Returns:
        Final prompt string ready for agent execution
    """
    if not prompt_template:
        return ""

    # Try rendering with Jinja2 first (supports arithmetic, indexing, control flow)
    prompt = None
    try:
        from jinja2 import Template  # type: ignore

        template = Template(prompt_template)
        prompt = template.render(**context)
        logger.debug("Prompt rendered with Jinja2 template engine")
    except Exception as e:
        # Either jinja2 is not installed or rendering failed; fall back gracefully
        logger.warning(
            f"Jinja2 unavailable or rendering error ('{e}'). Falling back to simple substitution"
        )
        prompt = substitute_task_description(prompt_template, context)

    # Client specific overrides (disclaimers, extra instructions)
    client_overrides = context.get("client_overrides") or {}
    extra_instructions = client_overrides.get(
        "additional_instructions"
    ) or client_overrides.get("disclaimer")
    if extra_instructions:
        prompt += f"\n\n{extra_instructions}"

    return prompt
