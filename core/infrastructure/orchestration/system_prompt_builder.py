"""System prompt builder with layered template support and budgeting."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from ...domain.entities.agent import Agent
from ..config.settings import Settings, get_settings
from .token_utils import SimpleTokenizer

logger = logging.getLogger(__name__)


SECTION_ORDER = [
    "persona",
    "goal",
    "tool_rules",
    "brand_voice",
    "compliance_rules",
    "run_context_notice",
]


DEFAULT_SECTION_BUDGETS = {
    "persona": 400,
    "goal": 80,
    "tool_rules": 260,
    "brand_voice": 160,
    "compliance_rules": 180,
    "run_context_notice": 160,
}


@dataclass
class SectionContribution:
    """Data structure for section-level overrides."""

    text: str
    replace: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemPromptBuilderConfig:
    """Configuration object accepted by :class:`SystemPromptBuilder`."""

    version: Optional[str] = None
    section_budgets: Optional[Dict[str, int]] = None
    tools: Optional[List[Dict[str, Any]]] = None
    runtime_overrides: Optional[Dict[str, Any]] = None


class SystemPromptBuilder:
    """Builder responsible for composing system prompts from layered sources."""

    def __init__(
        self,
        settings: Optional[Settings] = None,
        tokenizer: Optional[SimpleTokenizer] = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.tokenizer = tokenizer or SimpleTokenizer()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def build(
        self,
        agent: Agent,
        context: Dict[str, Any],
        config: Optional[SystemPromptBuilderConfig] = None,
    ) -> Tuple[str, Dict[str, Any]]:
        """Build the system message for ``agent`` within ``context``."""

        config = config or SystemPromptBuilderConfig()
        version = config.version or self.settings.system_prompt_version or "v1"

        section_budgets = {**DEFAULT_SECTION_BUDGETS}
        if config.section_budgets:
            section_budgets.update(config.section_budgets)

        profile = self._resolve_profile(context)
        workflow = self._resolve_workflow(context)
        task = self._resolve_task(context)

        logger.debug(
            "Building system prompt v%s (profile=%s, workflow=%s, task=%s)",
            version,
            profile,
            workflow,
            task,
        )

        layers: List[Dict[str, SectionContribution]] = []

        # Global layer -------------------------------------------------
        layers.append(
            self._load_template_sections(
                base_dir=self._core_prompt_dir(version),
                relative_path=Path("global.yaml"),
                context=context,
            )
        )

        # Profile layer ------------------------------------------------
        if profile:
            layers.append(
                self._load_template_sections(
                    base_dir=self._profile_prompt_dir(profile, version),
                    relative_path=Path("profile.yaml"),
                    context=context,
                )
            )

        # Workflow layer -----------------------------------------------
        if workflow:
            layers.append(
                self._load_template_sections(
                    base_dir=self._core_prompt_dir(version),
                    relative_path=Path("workflows") / f"{workflow}.yaml",
                    context=context,
                )
            )
            if profile:
                layers.append(
                    self._load_template_sections(
                        base_dir=self._profile_prompt_dir(profile, version),
                        relative_path=Path("workflows") / f"{workflow}.yaml",
                        context=context,
                    )
                )

        # Agent layer --------------------------------------------------
        layers.append(
            self._load_template_sections(
                base_dir=self._core_prompt_dir(version),
                relative_path=Path("agents") / f"{agent.name}.yaml",
                context=context,
            )
        )
        if profile:
            layers.append(
                self._load_template_sections(
                    base_dir=self._profile_prompt_dir(profile, version),
                    relative_path=Path("agents") / f"{agent.name}.yaml",
                    context=context,
                )
            )
        layers.append(self._build_agent_layer(agent, config.tools or []))

        # Task layer ---------------------------------------------------
        if workflow and task:
            layers.append(
                self._load_template_sections(
                    base_dir=self._core_prompt_dir(version),
                    relative_path=Path("tasks") / workflow / f"{task}.yaml",
                    context=context,
                )
            )
            if profile:
                layers.append(
                    self._load_template_sections(
                        base_dir=self._profile_prompt_dir(profile, version),
                        relative_path=Path("tasks") / workflow / f"{task}.yaml",
                        context=context,
                    )
                )

        # Runtime layer ------------------------------------------------
        layers.append(
            self._build_runtime_layer(context, config.runtime_overrides)
        )

        assembled_sections: Dict[str, List[str]] = {section: [] for section in SECTION_ORDER}
        section_sources: Dict[str, List[Dict[str, Any]]] = {section: [] for section in SECTION_ORDER}

        for layer in layers:
            for section, contribution in layer.items():
                if not contribution or not contribution.text:
                    continue
                section = section.lower()
                if section not in assembled_sections:
                    assembled_sections[section] = []
                    section_sources[section] = []
                if contribution.replace:
                    assembled_sections[section] = [contribution.text]
                    section_sources[section] = [contribution.metadata]
                else:
                    assembled_sections[section].append(contribution.text)
                    section_sources[section].append(contribution.metadata)

        budget_report = {
            "version": version,
            "sections": {},
            "total_tokens": 0,
        }

        final_sections: List[str] = []
        for section in SECTION_ORDER:
            parts = [segment.strip() for segment in assembled_sections.get(section, []) if segment.strip()]
            if not parts:
                continue
            raw_text = "\n\n".join(parts).strip()
            truncated_text = raw_text
            truncated = False
            token_budget = section_budgets.get(section)
            raw_tokens = self.tokenizer.count_tokens(raw_text)
            if token_budget and raw_tokens > token_budget:
                truncated_text = self.tokenizer.truncate(raw_text, token_budget)
                truncated = True
            final_sections.append(truncated_text)
            budget_report["sections"][section] = {
                "tokens": self.tokenizer.count_tokens(truncated_text),
                "budget": token_budget,
                "truncated": truncated,
                "sources": section_sources.get(section, []),
            }
            budget_report["total_tokens"] += budget_report["sections"][section]["tokens"]

        system_message = "\n\n".join(final_sections).strip()
        budget_report["system_message_length"] = len(system_message)

        return system_message, budget_report

    # ------------------------------------------------------------------
    # Layer helpers
    # ------------------------------------------------------------------
    def _build_agent_layer(
        self,
        agent: Agent,
        tools: List[Dict[str, Any]],
    ) -> Dict[str, SectionContribution]:
        sections: Dict[str, SectionContribution] = {}

        persona_parts: List[str] = []
        if agent.system_message:
            persona_parts.append(agent.system_message.strip())
        if agent.backstory:
            persona_parts.append(agent.backstory.strip())
        if persona_parts:
            sections["persona"] = SectionContribution(
                text="\n\n".join(persona_parts),
                metadata={"source": "agent"},
            )

        if agent.goal:
            sections["goal"] = SectionContribution(
                text=f"Primary goal: {agent.goal.strip()}",
                metadata={"source": "agent"},
            )

        brand_voice = agent.metadata.get("brand_voice") if isinstance(agent.metadata, dict) else None
        if brand_voice:
            sections["brand_voice"] = SectionContribution(
                text=f"Brand voice guidance: {brand_voice}",
                metadata={"source": "agent.metadata"},
            )

        tool_rules = self._build_tool_rules(tools)
        if tool_rules:
            sections["tool_rules"] = SectionContribution(
                text=tool_rules,
                metadata={"source": "agent.tools"},
            )

        return sections

    def _build_runtime_layer(
        self,
        context: Dict[str, Any],
        runtime_overrides: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, SectionContribution]:
        sections: Dict[str, SectionContribution] = {}

        lines: List[str] = []
        client_profile = context.get("client_profile") or context.get("client_name")
        if client_profile:
            lines.append(f"Client profile: {client_profile}")
        target_audience = context.get("target_audience")
        if target_audience:
            lines.append(f"Target audience: {target_audience}")
        tone = context.get("tone")
        if tone:
            lines.append(f"Preferred tone: {tone}")
        if context.get("workflow_template"):
            lines.append(f"Workflow template: {context['workflow_template']}")
        if context.get("task_name"):
            lines.append(f"Current task: {context['task_name']}")
        if context.get("custom_instructions"):
            lines.append(f"Custom instructions: {context['custom_instructions']}")

        if lines:
            sections["run_context_notice"] = SectionContribution(
                text="Runtime context:\n- " + "\n- ".join(lines),
                metadata={"source": "runtime"},
            )

        if runtime_overrides:
            for section, value in runtime_overrides.items():
                if not value:
                    continue
                sections[section] = SectionContribution(
                    text=str(value),
                    metadata={"source": "runtime_override"},
                    replace=True,
                )

        compliance = context.get("compliance_requirements")
        if compliance and "compliance_rules" not in sections:
            sections["compliance_rules"] = SectionContribution(
                text=str(compliance),
                metadata={"source": "runtime"},
            )

        return sections

    # ------------------------------------------------------------------
    # Utility helpers
    # ------------------------------------------------------------------
    def _build_tool_rules(self, tools: List[Dict[str, Any]]) -> str:
        if not tools:
            return ""

        lines: List[str] = ["You have access to the following tools:"]
        for tool in tools:
            name = tool.get("name")
            description = tool.get("description", "").strip()
            if name and description:
                lines.append(f"- {name}: {description}")
            elif name:
                lines.append(f"- {name}")

        try:
            from ..tools.tool_names import ToolNames

            lines.extend(
                [
                    "",
                    "When invoking tools, use the exact syntax:",
                    f"[{ToolNames.RAG_GET_CLIENT_CONTENT}] client_name [/{ToolNames.RAG_GET_CLIENT_CONTENT}]",
                    f"[{ToolNames.RAG_GET_CLIENT_CONTENT}] client_name, document_name [/{ToolNames.RAG_GET_CLIENT_CONTENT}]",
                    f"[{ToolNames.RAG_SEARCH_CONTENT}] client_name, search_query [/{ToolNames.RAG_SEARCH_CONTENT}]",
                    f"[{ToolNames.RAG_SEARCH_CONTENT}] search_query [/{ToolNames.RAG_SEARCH_CONTENT}] (defaults to 'siebert' if client is omitted)",
                    f"[{ToolNames.WEB_SEARCH_SERPER}] your search query [/{ToolNames.WEB_SEARCH_SERPER}]",
                    f"[{ToolNames.WEB_SEARCH_PERPLEXITY}] your search query [/{ToolNames.WEB_SEARCH_PERPLEXITY}]",
                    "",
                    "Critical rules:",
                    "- Use the exact tool names listed above",
                    "- Provide concrete queries for rag_search_content",
                    "- Separate parameters with commas for multi-argument tools",
                    "- Do not use placeholders like 'TOOL_NAME'",
                ]
            )
        except Exception:  # pragma: no cover - defensive, ToolNames always available in runtime
            lines.append(
                "Ensure tool calls use the canonical name and are wrapped in [TOOL] ... [/TOOL] blocks."
            )

        return "\n".join(lines)

    def _load_template_sections(
        self,
        base_dir: Path,
        relative_path: Path,
        context: Dict[str, Any],
    ) -> Dict[str, SectionContribution]:
        if not base_dir:
            return {}
        path = base_dir / relative_path
        if not path.exists():
            return {}

        try:
            with open(path, "r", encoding="utf-8") as fp:
                data = yaml.safe_load(fp) or {}
        except FileNotFoundError:
            return {}
        except Exception as exc:
            logger.warning("Failed to load system prompt template %s: %s", path, exc)
            return {}

        sections: Dict[str, SectionContribution] = {}
        raw_sections = data.get("sections", {})
        for section, value in raw_sections.items():
            text = ""
            replace = False
            if isinstance(value, dict):
                text = value.get("text") or value.get("content") or ""
                replace = bool(value.get("replace"))
            else:
                text = str(value)

            rendered = self._render_template(text, context).strip()
            if rendered:
                sections[section.lower()] = SectionContribution(
                    text=rendered,
                    replace=replace,
                    metadata={"source": str(path)},
                )

        return sections

    def _render_template(self, template_text: str, context: Dict[str, Any]) -> str:
        if not template_text:
            return ""

        try:
            from jinja2 import Template  # type: ignore

            return Template(template_text).render(**context)
        except Exception:
            # As a safe fallback simply return the raw template text; system prompts
            # primarily use literals so this is acceptable.
            return template_text

    def _core_prompt_dir(self, version: str) -> Path:
        return Path(__file__).resolve().parent.parent.parent / "prompts" / "system" / version

    def _profile_prompt_dir(self, profile: str, version: str) -> Path:
        base = Path(self.settings.profiles_dir) / profile / "prompts" / "system" / version
        return base

    def _resolve_profile(self, context: Dict[str, Any]) -> Optional[str]:
        return context.get("client_profile") or context.get("client_name")

    def _resolve_workflow(self, context: Dict[str, Any]) -> Optional[str]:
        return context.get("workflow_type") or context.get("workflow_template")

    def _resolve_task(self, context: Dict[str, Any]) -> Optional[str]:
        return context.get("task_id") or context.get("task_name")
