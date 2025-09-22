"""Workflow handler for Reopla enhanced article with hero image generation."""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict

from ..base.workflow_base import WorkflowHandler
from ..registry import register_workflow

logger = logging.getLogger(__name__)


@register_workflow("reopla_enhanced_article_with_image")
class ReoplaEnhancedArticleWithImageHandler(WorkflowHandler):
    """Coordinate Reopla-specific article creation and image strategy."""

    def validate_inputs(self, context: Dict[str, Any]) -> None:
        super().validate_inputs(context)

        topic = context.get("topic", "").strip()
        if len(topic) < 5:
            raise ValueError(
                "Topic must contain at least 5 characters for meaningful generation"
            )

        target_word_count = context.get("target_word_count")
        if target_word_count:
            try:
                count = int(target_word_count)
            except (TypeError, ValueError) as exc:
                raise ValueError("target_word_count must be a valid integer") from exc
            if count < 400:
                raise ValueError(
                    "target_word_count must be at least 400 words for Reopla articles"
                )
            if count > 2000:
                raise ValueError(
                    "target_word_count must not exceed 2000 words for this workflow"
                )

        logger.info("✅ Reopla workflow input validation passed")

    def prepare_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        context = super().prepare_context(context)

        context.setdefault("client_name", "reopla")
        context.setdefault("client_profile", context["client_name"])
        context.setdefault("target_audience", "real_estate_professionals_and_investors")
        context.setdefault("tone", "professional_approachable")
        context.setdefault("target_word_count", 900)
        context.setdefault("include_statistics", True)
        context.setdefault("include_case_studies", False)
        context.setdefault("image_style", "professional")
        context.setdefault("image_provider", "openai")
        context.setdefault("image_focus", "modern urban real estate innovation")
        context.setdefault("brand_colors", ["#2E5BBA", "#8BC34A", "#FF9800"])

        context["workflow_stage"] = "preparation"
        context["workflow_type"] = "reopla_enhanced_article_with_image"

        logger.debug(
            "📋 Reopla context prepared: %s",
            {
                k: context[k]
                for k in [
                    "client_name",
                    "target_audience",
                    "tone",
                    "target_word_count",
                    "image_style",
                    "image_provider",
                ]
            },
        )
        return context

    def post_process_task(
        self, task_id: str, task_output: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        context = super().post_process_task(task_id, task_output, context)

        if task_id == "task1_reopla_brief":
            context["reopla_brief_ready"] = True
            context["workflow_stage"] = "research"
            logger.info("🧭 Reopla brief completed and ready for research")
        elif task_id == "task2_reopla_research":
            context["reopla_research_ready"] = True
            context["workflow_stage"] = "drafting"
            context["research_characters"] = len(task_output or "")
            logger.info(
                "🔍 Research dossier prepared (%s characters)",
                context["research_characters"],
            )
        elif task_id == "task3_reopla_draft":
            context["reopla_draft_ready"] = True
            context["workflow_stage"] = "compliance_review"
            context["draft_word_count"] = len(task_output.split()) if task_output else 0
            logger.info("📝 Draft created with %s words", context["draft_word_count"])
        elif task_id == "task4_reopla_compliance":
            context["reopla_compliance_reviewed"] = True
            context["workflow_stage"] = "image_strategy"
            logger.info("🛡️ Compliance review completed for Reopla article")
        elif task_id == "task5_reopla_image":
            context["reopla_image_strategy"] = task_output
            context["workflow_stage"] = "completed"
            payload = self._extract_json_payload(task_output)
            if payload:
                context["reopla_image_payload"] = payload
                logger.info("🎨 Captured structured image payload for Reopla workflow")
            else:
                logger.warning(
                    "⚠️ Unable to parse JSON payload from image specialist output"
                )
        return context

    def post_process_workflow(self, context: Dict[str, Any]) -> Dict[str, Any]:
        final_content = context.get("task4_reopla_compliance_output") or context.get(
            "task3_reopla_draft_output", ""
        )
        context["final_output"] = final_content
        context["workflow_completed"] = True

        summary = {
            "topic": context.get("topic"),
            "target_word_count": context.get("target_word_count"),
            "draft_word_count": context.get("draft_word_count"),
            "include_statistics": context.get("include_statistics"),
            "image_provider": context.get("image_provider"),
            "image_payload_available": bool(context.get("reopla_image_payload")),
        }
        context["workflow_summary"] = summary

        logger.info("🎉 Reopla enhanced article with image workflow complete")
        logger.debug("📊 Workflow summary: %s", summary)

        return super().post_process_workflow(context)

    @staticmethod
    def _extract_json_payload(output: str) -> Dict[str, Any] | None:
        if not output:
            return None

        try:
            json_candidate = re.search(r"\{.*\}", output, re.DOTALL)
            if not json_candidate:
                return None
            return json.loads(json_candidate.group(0))
        except json.JSONDecodeError as exc:
            logger.debug("JSON parsing failed for image payload: %s", exc)
            return None
