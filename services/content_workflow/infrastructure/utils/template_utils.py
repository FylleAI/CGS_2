"""
Template utilities for variable substitution in task descriptions.
"""

from typing import Dict, Any, Optional
import re
import logging

logger = logging.getLogger(__name__)


class TemplateSubstitution:
    """Utility class for template variable substitution."""

    @staticmethod
    def substitute_template(text: str, variables: Dict[str, Any]) -> str:
        """
        Substitute template variables in text.

        Replaces patterns like {{variable_name}} with actual values.

        Args:
            text: Text containing template variables
            variables: Dictionary of variable names and values

        Returns:
            Text with variables substituted
        """
        if not text or not variables:
            return text

        result = text

        # Find all template variables in the format {{variable_name}}
        pattern = r"\{\{([^}]+)\}\}"
        matches = re.findall(pattern, text)

        for match in matches:
            variable_name = match.strip()

            # Get the value from variables dict
            value = variables.get(variable_name, "")

            # Convert to string and handle None values
            if value is None:
                value = ""
            elif not isinstance(value, str):
                value = str(value)

            # Replace the template variable with the actual value
            template_var = f"{{{{{variable_name}}}}}"
            result = result.replace(template_var, value)

            logger.debug(f"Substituted {{{{ {variable_name} }}}} with: {value}")

        return result

    @staticmethod
    def extract_template_variables(text: str) -> list[str]:
        """
        Extract all template variable names from text.

        Args:
            text: Text containing template variables

        Returns:
            List of variable names found in the text
        """
        pattern = r"\{\{([^}]+)\}\}"
        matches = re.findall(pattern, text)
        return [match.strip() for match in matches]

    @staticmethod
    def validate_template_variables(
        text: str, available_variables: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate that all template variables in text have corresponding values.

        Args:
            text: Text containing template variables
            available_variables: Dictionary of available variables

        Returns:
            Dictionary with validation results:
            - 'valid': bool - whether all variables are available
            - 'missing': list - list of missing variable names
            - 'found': list - list of found variable names
        """
        template_vars = TemplateSubstitution.extract_template_variables(text)
        missing_vars = []
        found_vars = []

        for var_name in template_vars:
            if var_name in available_variables:
                found_vars.append(var_name)
            else:
                missing_vars.append(var_name)

        return {
            "valid": len(missing_vars) == 0,
            "missing": missing_vars,
            "found": found_vars,
            "total_variables": len(template_vars),
        }


def build_template_variables(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build template variables dictionary from context.

    Args:
        context: Context dictionary containing workflow execution data

    Returns:
        Dictionary of template variables ready for substitution
    """
    variables = {}

    # Direct context variables
    direct_vars = [
        "topic",
        "client_name",
        "context",
        "workflow_type",
        "target_audience",
        "workflow_id",
        "workflow_name",
    ]

    for var in direct_vars:
        if var in context:
            variables[var] = context[var]

    # Extract from generation_params if available
    generation_params = context.get("generation_params", {})
    if isinstance(generation_params, dict):
        param_vars = [
            "target",
            "tone",
            "target_word_count",
            "include_statistics",
            "include_examples",
            "include_sources",
            "custom_instructions",
        ]

        for var in param_vars:
            if var in generation_params:
                variables[var] = generation_params[var]

    # Handle special mappings
    if "target" in variables and "target_audience" not in variables:
        variables["target_audience"] = variables["target"]

    # Ensure all variables are strings for template substitution
    for key, value in variables.items():
        if value is None:
            variables[key] = ""
        elif isinstance(value, bool):
            variables[key] = "true" if value else "false"
        elif not isinstance(value, str):
            variables[key] = str(value)

    logger.debug(f"Built template variables: {list(variables.keys())}")
    return variables


def substitute_task_description(description: str, context: Dict[str, Any]) -> str:
    """
    Substitute template variables in task description using context.

    Args:
        description: Task description with template variables
        context: Context dictionary from workflow execution

    Returns:
        Task description with variables substituted
    """
    if not description:
        return description

    # Build template variables from context
    variables = build_template_variables(context)

    # Validate template variables
    validation = TemplateSubstitution.validate_template_variables(
        description, variables
    )

    if not validation["valid"]:
        logger.warning(f"Missing template variables: {validation['missing']}")
        logger.debug(f"Available variables: {list(variables.keys())}")

    # Substitute variables
    result = TemplateSubstitution.substitute_template(description, variables)

    logger.info(
        f"Template substitution completed. Variables used: {validation['found']}"
    )

    return result


# Convenience function for backward compatibility
def substitute_template(text: str, variables: Dict[str, Any]) -> str:
    """
    Convenience function for template substitution.

    Args:
        text: Text containing template variables
        variables: Dictionary of variable names and values

    Returns:
        Text with variables substituted
    """
    return TemplateSubstitution.substitute_template(text, variables)
