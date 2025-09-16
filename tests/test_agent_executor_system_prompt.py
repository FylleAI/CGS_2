"""Tests covering AgentExecutor system prompt fallbacks."""

from core.domain.entities.agent import Agent, AgentRole
from core.domain.value_objects.provider_config import ProviderConfig
from core.infrastructure.config.settings import Settings
from core.infrastructure.orchestration.agent_executor import AgentExecutor


def create_agent() -> Agent:
    return Agent(
        name="legacy_agent",
        role=AgentRole.RESEARCHER,
        system_message="Legacy persona",
        backstory="Legacy backstory",
        goal="Legacy goal",
    )


def test_system_prompt_builder_disabled_uses_legacy_message():
    settings = Settings(secret_key="test-key", use_system_prompt_builder_v2=False)
    executor = AgentExecutor(
        agent_repository=None,
        llm_provider=None,
        provider_config=ProviderConfig(),
        settings=settings,
    )

    agent = create_agent()
    context = {"client_profile": "default"}

    legacy_message = executor._prepare_system_message(agent, context)
    system_message, report = executor._build_system_message(agent, context)

    assert system_message == legacy_message
    assert report == {}
