"""Unit tests for the layered system prompt builder."""

from core.domain.entities.agent import Agent, AgentRole
from core.infrastructure.config.settings import Settings
from core.infrastructure.orchestration.system_prompt_builder import (
    SystemPromptBuilder,
    SystemPromptBuilderConfig,
)


def create_agent() -> Agent:
    return Agent(
        name="unit_agent",
        role=AgentRole.RESEARCHER,
        system_message="word1 word2 word3 word4 word5 word6",
        backstory="Backstory text that should be removed when overridden.",
        goal="Deliver accurate summaries.",
    )


def create_context() -> dict:
    return {
        "client_profile": "default",
        "workflow_type": "enhanced_article",
        "workflow_template": "enhanced_article",
        "task_id": "task1_brief",
        "task_name": "Brief Creation",
    }


def test_runtime_override_precedence():
    settings = Settings(secret_key="test-key")
    builder = SystemPromptBuilder(settings=settings)
    agent = create_agent()
    context = create_context()

    config = SystemPromptBuilderConfig(
        runtime_overrides={"persona": "Runtime persona override."}
    )

    system_message, report = builder.build(agent, context, config)

    assert "Runtime persona override." in system_message
    assert "Backstory text" not in system_message
    assert report["sections"]["persona"]["truncated"] is False


def test_section_budget_truncation():
    settings = Settings(secret_key="test-key")
    builder = SystemPromptBuilder(settings=settings)
    agent = create_agent()
    context = create_context()

    config = SystemPromptBuilderConfig(section_budgets={"persona": 3})
    system_message, report = builder.build(agent, context, config)

    assert report["sections"]["persona"]["truncated"] is True
    assert "word4" not in system_message
