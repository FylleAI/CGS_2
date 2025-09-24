import pytest

from core.infrastructure.logging.cost_calculator import CostCalculator, TokenUsage


@pytest.fixture()
def calculator():
    return CostCalculator()


def test_openai_gpt4o_cost_breakdown(calculator):
    usage = TokenUsage(prompt_tokens=1000, completion_tokens=1000)

    breakdown = calculator.calculate_cost("openai", "gpt-4o", usage)

    assert breakdown.prompt_cost == pytest.approx(0.0025)
    assert breakdown.completion_cost == pytest.approx(0.01)
    assert breakdown.total_cost == pytest.approx(0.0125)


def test_reasoning_tokens_are_included(calculator):
    usage = TokenUsage(
        prompt_tokens=500,
        completion_tokens=250,
        reasoning_tokens=500,
    )

    breakdown = calculator.calculate_cost("openai", "o1-mini", usage)

    assert breakdown.prompt_cost == pytest.approx(0.0015)
    assert breakdown.completion_cost == pytest.approx(0.003)
    assert breakdown.reasoning_cost == pytest.approx(0.006)
    assert breakdown.total_cost == pytest.approx(0.0105)


def test_cached_tokens_implicit_from_usage(calculator):
    usage = TokenUsage(
        prompt_tokens=1000,
        completion_tokens=0,
        cached_tokens=2000,
    )

    breakdown = calculator.calculate_cost(
        "anthropic", "claude-3-5-haiku-20241022", usage
    )

    assert breakdown.prompt_cost == pytest.approx(0.00080)
    assert breakdown.cache_cost == pytest.approx(0.00016)
    assert breakdown.total_cost == pytest.approx(0.00096)


def test_cached_tokens_explicit_override(calculator):
    usage = TokenUsage(prompt_tokens=0, completion_tokens=0, cached_tokens=0)

    breakdown = calculator.calculate_cost(
        "anthropic", "claude-3-5-haiku-20241022", usage, cached_tokens=1000
    )

    assert breakdown.cache_cost == pytest.approx(0.00008)
    assert breakdown.total_cost == pytest.approx(0.00008)


def test_unknown_provider_falls_back_to_average(calculator):
    usage = TokenUsage(prompt_tokens=500, completion_tokens=500)

    breakdown = calculator.calculate_cost("unknown", "model", usage)

    assert breakdown.prompt_cost == pytest.approx(0.001)
    assert breakdown.completion_cost == pytest.approx(0.003)
    assert breakdown.total_cost == pytest.approx(0.004)


def test_cache_write_cost_is_accounted(calculator):
    usage = TokenUsage(cache_write_tokens=1000)

    breakdown = calculator.calculate_cost(
        "anthropic", "claude-3-5-haiku-20241022", usage
    )

    # Write-only cost should be billed using cache_write rate (0.0010 per 1k tokens)
    assert breakdown.cache_cost == pytest.approx(0.0010)
    assert breakdown.total_cost == pytest.approx(0.0010)


def test_cache_read_and_write_combined(calculator):
    usage = TokenUsage(cache_read_tokens=2000, cache_write_tokens=1000)

    breakdown = calculator.calculate_cost(
        "anthropic", "claude-3-7-sonnet-20250219", usage
    )

    expected_cache_cost = (2000 / 1000) * 0.00030 + (1000 / 1000) * 0.00375
    assert breakdown.cache_cost == pytest.approx(expected_cache_cost)
    assert breakdown.total_cost == pytest.approx(expected_cache_cost)


def test_token_usage_total_includes_cache_reads():
    usage = TokenUsage(cache_read_tokens=1500)

    assert usage.total_tokens == 1500


def test_model_alias_resolution(calculator):
    usage = TokenUsage(prompt_tokens=1000)

    breakdown = calculator.calculate_cost(
        "anthropic", "claude-3-7-sonnet-20250219-latest", usage
    )

    assert breakdown.prompt_cost == pytest.approx(0.003)
