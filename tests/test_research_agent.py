import pytest

from core.infrastructure.config.settings import Settings
from core.infrastructure.repositories.yaml_agent_repository import YamlAgentRepository
from core.infrastructure.orchestration.agent_executor import AgentExecutor
from core.infrastructure.tools.tool_names import ToolNames
from core.domain.value_objects.provider_config import ProviderConfig
from core.application.interfaces.llm_provider_interface import (
    LLMProviderInterface,
    LLMResponse,
    LLMStreamChunk,
)


class DummyProvider(LLMProviderInterface):
    async def generate_content(self, prompt, config, system_message=None):
        return LLMResponse(
            content=f"[{ToolNames.WEB_SEARCH_PERPLEXITY}]test query[/{ToolNames.WEB_SEARCH_PERPLEXITY}]"
        )

    async def generate_content_detailed(self, prompt, config, system_message=None):  # pragma: no cover - unused
        return LLMResponse(content="")

    async def generate_content_stream(self, prompt, config, system_message=None):  # pragma: no cover - unused
        yield LLMStreamChunk(content="", is_final=True)

    async def chat_completion(self, messages, config):  # pragma: no cover - unused
        return LLMResponse(content="")

    async def validate_config(self, config):  # pragma: no cover - unused
        return True

    async def get_available_models(self, config):  # pragma: no cover - unused
        return []

    async def estimate_tokens(self, text, model):  # pragma: no cover - unused
        return len(text)

    async def check_health(self, config):  # pragma: no cover - unused
        return {"status": "ok"}


@pytest.mark.asyncio
async def test_research_agent_triggers_perplexity():
    repo = YamlAgentRepository()
    agent = await repo.get_by_name("research_agent")
    assert agent is not None
    assert "last 7 days" in agent.system_message
    assert "blog.siebert.com" in agent.system_message

    provider = DummyProvider()
    executor = AgentExecutor(
        repo,
        provider,
        ProviderConfig(),
        settings=Settings(secret_key="test-key"),
    )

    calls = {}

    async def fake_search(query: str, opts=None):
        calls["query"] = query
        return {"provider": "perplexity", "model_used": "mock", "duration_ms": 0, "data": {"citations": []}}

    executor.register_tools({
        ToolNames.WEB_SEARCH_PERPLEXITY: {"function": fake_search, "description": "mock"}
    })

    result = await executor.execute_agent(agent, "do research", context={"client_profile": "siebert"})
    assert "citations" in result
    assert calls["query"] == "test query"

