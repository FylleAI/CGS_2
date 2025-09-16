"""Context compaction pipeline for workflow prompts."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ..config.settings import Settings, get_settings
from .token_utils import SimpleTokenizer

logger = logging.getLogger(__name__)


KB_PATTERNS = (
    "rag",
    "research",
    "analysis",
    "context",
    "brief",
    "summary",
    "content",
    "insight",
)

RUNTIME_FIELDS = (
    "topic",
    "target_audience",
    "target_word_count",
    "tone",
    "edition_number",
    "include_sources",
    "custom_instructions",
    "client_profile",
    "client_name",
)


SECTION_BUDGETS = {
    "kb_summary": 1200,
    "runtime_context": 400,
    "examples": 400,
}


@dataclass
class PipelineSection:
    """Container for intermediate pipeline data."""

    text: str
    tokens: int


class ContextPipeline:
    """Stage 1 context pipeline with dedupe/normalize/cap operations."""

    def __init__(
        self,
        settings: Optional[Settings] = None,
        tokenizer: Optional[SimpleTokenizer] = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.tokenizer = tokenizer or SimpleTokenizer()

    def build(self, enhanced_context: Dict[str, Any]) -> Dict[str, Any]:
        start = time.time()

        collected = self._collect(enhanced_context)
        deduped = {name: self._dedupe_text(text) for name, text in collected.items()}
        normalized = {name: self._normalize_text(text) for name, text in deduped.items()}
        capped = {
            name: self._apply_cap(name, text)
            for name, text in normalized.items()
        }

        citations = self._extract_citations(enhanced_context)

        duration_ms = (time.time() - start) * 1000
        drop_ratios = self._compute_drop_ratios(collected, capped)

        report = {
            "duration_ms": duration_ms,
            "drop_ratios": drop_ratios,
            "budgets": SECTION_BUDGETS,
            "total_tokens": sum(section.tokens for section in capped.values()),
        }

        logger.debug(
            "Context pipeline completed in %.2f ms (tokens=%s)",
            duration_ms,
            {name: section.tokens for name, section in capped.items()},
        )

        return {
            "kb_summary": capped["kb_summary"].text,
            "runtime_context": capped["runtime_context"].text,
            "examples": capped["examples"].text,
            "citations": citations,
            "notes": report,
        }

    # ------------------------------------------------------------------
    # Stage helpers
    # ------------------------------------------------------------------
    def _collect(self, context: Dict[str, Any]) -> Dict[str, str]:
        kb_chunks: List[str] = []
        runtime_lines: List[str] = []
        example_chunks: List[str] = []

        for key in sorted(context.keys()):
            value = context[key]
            if not value:
                continue
            if isinstance(value, (list, tuple)):
                str_value = "\n".join(str(item) for item in value if item)
            else:
                str_value = str(value)

            lowered_key = key.lower()

            if any(pattern in lowered_key for pattern in KB_PATTERNS):
                kb_chunks.append(f"[{key}]\n{str_value.strip()}")
                continue

            if lowered_key.endswith("_examples") or "example" in lowered_key:
                example_chunks.append(str_value.strip())
                continue

        for field in RUNTIME_FIELDS:
            if field in context and context[field]:
                runtime_lines.append(
                    f"{field.replace('_', ' ').title()}: {self._inline_value(context[field])}"
                )

        return {
            "kb_summary": "\n\n".join(chunk for chunk in kb_chunks if chunk).strip(),
            "runtime_context": "\n".join(f"- {line}" for line in runtime_lines if line).strip(),
            "examples": "\n\n".join(chunk for chunk in example_chunks if chunk).strip(),
        }

    def _dedupe_text(self, text: str) -> str:
        if not text:
            return ""
        seen = set()
        deduped_lines: List[str] = []
        for line in text.splitlines():
            key = line.strip()
            if key and key not in seen:
                deduped_lines.append(line)
                seen.add(key)
        return "\n".join(deduped_lines)

    def _normalize_text(self, text: str) -> str:
        if not text:
            return ""
        cleaned = [line.rstrip() for line in text.splitlines()]
        return "\n".join(line for line in cleaned if line.strip())

    def _apply_cap(self, name: str, text: str) -> PipelineSection:
        budget = SECTION_BUDGETS.get(name)
        tokens_before = self.tokenizer.count_tokens(text)
        if budget and tokens_before > budget:
            truncated = self.tokenizer.truncate(text, budget)
            tokens_after = self.tokenizer.count_tokens(truncated)
            return PipelineSection(truncated, tokens_after)
        return PipelineSection(text, tokens_before)

    def _compute_drop_ratios(
        self,
        collected: Dict[str, str],
        capped: Dict[str, PipelineSection],
    ) -> Dict[str, float]:
        ratios: Dict[str, float] = {}
        for name, original in collected.items():
            original_tokens = self.tokenizer.count_tokens(original)
            final_tokens = capped[name].tokens
            if original_tokens == 0:
                ratios[name] = 0.0
            else:
                ratios[name] = max(0.0, 1 - (final_tokens / original_tokens))
        return ratios

    def _extract_citations(self, context: Dict[str, Any]) -> List[str]:
        citations: List[str] = []
        for key in sorted(context.keys()):
            if "citation" in key.lower() or "source" in key.lower():
                value = context[key]
                if isinstance(value, list):
                    citations.extend(str(item) for item in value if item)
                elif value:
                    citations.append(str(value))
        # Limit to a manageable number while preserving order.
        unique: List[str] = []
        seen = set()
        for entry in citations:
            if entry not in seen:
                unique.append(entry)
                seen.add(entry)
            if len(unique) >= 5 and not self.settings.use_context_pipeline_summarize:
                break
        return unique

    def _inline_value(self, value: Any) -> str:
        if isinstance(value, (list, tuple)):
            return ", ".join(str(item) for item in value)
        return str(value)
