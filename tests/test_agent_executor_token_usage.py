import types

import pytest

from core.infrastructure.orchestration.agent_executor import AgentExecutor


@pytest.fixture
def executor():
    return AgentExecutor.__new__(AgentExecutor)


def test_extract_token_usage_handles_dict_with_cache_fields(executor):
    response = types.SimpleNamespace(
        content="ok",
        usage={
            "input_tokens": 100,
            "output_tokens": 50,
            "cache_creation_input_tokens": 25,
            "cache_read_input_tokens": 75,
        },
    )

    usage = executor._extract_token_usage(response)

    assert usage.prompt_tokens == 100
    assert usage.completion_tokens == 50
    assert usage.cache_write_tokens == 25
    assert usage.cache_read_tokens == 75
    assert usage.cached_tokens == 75
    assert usage.total_tokens == 225  # prompt + completion + cache read


def test_extract_token_usage_handles_object_usage(executor):
    usage_obj = types.SimpleNamespace(
        prompt_tokens=80,
        completion_tokens=40,
        reasoning_tokens=20,
        cache_read_tokens=60,
        cache_write_tokens=10,
    )
    response = types.SimpleNamespace(content="ok", usage=usage_obj)

    usage = executor._extract_token_usage(response)

    assert usage.prompt_tokens == 80
    assert usage.completion_tokens == 40
    assert usage.reasoning_tokens == 20
    assert usage.cache_read_tokens == 60
    assert usage.cache_write_tokens == 10
    assert usage.total_tokens == 200
