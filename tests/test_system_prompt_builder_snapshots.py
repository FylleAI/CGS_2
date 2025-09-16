"""Snapshot tests for the layered system prompt builder."""

from pathlib import Path
from typing import Dict

import yaml

from core.domain.entities.agent import Agent
from core.infrastructure.config.settings import Settings
from core.infrastructure.orchestration.system_prompt_builder import (
    SystemPromptBuilder,
    SystemPromptBuilderConfig,
)


FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures" / "system_prompts"
TEST_SETTINGS = Settings(secret_key="snapshot-test")


def load_agent(profile: str, agent_name: str) -> Agent:
    agent_path = Path(TEST_SETTINGS.profiles_dir) / profile / "agents" / f"{agent_name}.yaml"
    with open(agent_path, "r", encoding="utf-8") as fh:
        data: Dict[str, any] = yaml.safe_load(fh) or {}
    data.setdefault("name", agent_name)
    data.setdefault("role", data.get("role", "researcher"))
    agent = Agent.from_dict(data)
    agent.metadata["client_profile"] = profile
    return agent


def build_context(workflow: str, task_id: str, task_name: str, profile: str) -> Dict[str, str]:
    return {
        "client_profile": profile,
        "workflow_type": workflow,
        "workflow_template": workflow,
        "task_id": task_id,
        "task_name": task_name,
        "target_audience": "Gen Z investors",
        "tone": "confident",
        "custom_instructions": "Highlight actionable insights and cite approved sources.",
        "compliance_requirements": "Use only verified statements and provide disclosures when necessary.",
    }


SNAPSHOTS = [
    (
        "enhanced_article",
        "task1_brief",
        "Brief Creation",
        "rag_specialist",
        "enhanced_article_task1_brief.txt",
    ),
    (
        "enhanced_article",
        "task2_research",
        "Web Research & Brief Enhancement",
        "research_specialist",
        "enhanced_article_task2_research.txt",
    ),
    (
        "enhanced_article",
        "task4_compliance_review",
        "FINRA/SEC Compliance Review & Validation",
        "compliance_specialist",
        "enhanced_article_task4_compliance_review.txt",
    ),
    (
        "premium_newsletter",
        "task3_newsletter_creation",
        "Precision Newsletter Creation",
        "copywriter",
        "premium_newsletter_task3_newsletter_creation.txt",
    ),
]


def test_system_prompt_builder_snapshots():
    builder = SystemPromptBuilder(settings=TEST_SETTINGS)

    for workflow, task_id, task_name, agent_name, fixture_name in SNAPSHOTS:
        agent = load_agent("siebert", agent_name)
        context = build_context(workflow, task_id, task_name, "siebert")
        system_prompt, _ = builder.build(agent, context, SystemPromptBuilderConfig())
        expected_path = FIXTURES_DIR / fixture_name
        assert expected_path.exists(), f"Missing snapshot fixture: {expected_path}"
        expected = expected_path.read_text(encoding="utf-8").strip()
        assert system_prompt.strip() == expected
