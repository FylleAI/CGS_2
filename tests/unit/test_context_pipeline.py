"""Unit tests for the context compaction pipeline."""

from core.infrastructure.config.settings import Settings
from core.infrastructure.orchestration import context_pipeline
from core.infrastructure.orchestration.context_pipeline import ContextPipeline


def sample_context() -> dict:
    return {
        "task1_brief_output": "Line A\nLine A\nLine B",
        "task2_research_output": "Line B\nLine C",
        "topic": "Inflation outlook 2025",
        "target_audience": "Gen Z investors",
        "tone": "confident",
        "sources": ["https://example.com/a", "https://example.com/b"],
        "duplicate_sources": ["https://example.com/a"],
    }


def test_pipeline_dedupe_and_normalize():
    pipeline = ContextPipeline(settings=Settings(secret_key="test-key"))
    result = pipeline.build(sample_context())

    kb_summary = result["kb_summary"]
    assert kb_summary.count("Line A") == 1
    assert "Line C" in kb_summary

    runtime_context = result["runtime_context"]
    assert "Topic" in runtime_context
    assert "Tone" in runtime_context

    citations = result["citations"]
    assert citations[0] == "https://example.com/a"
    assert len(citations) <= 5


def test_pipeline_hard_cap(monkeypatch):
    monkeypatch.setitem(context_pipeline.SECTION_BUDGETS, "kb_summary", 2)
    pipeline = ContextPipeline(settings=Settings(secret_key="test-key"))
    result = pipeline.build(sample_context())

    notes = result["notes"]
    assert notes["drop_ratios"]["kb_summary"] > 0
    assert result["kb_summary"].endswith("…")
