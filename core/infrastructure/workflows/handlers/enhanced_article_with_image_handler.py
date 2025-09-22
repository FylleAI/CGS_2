"""Enhanced Article with Image workflow handler."""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, Optional

from .enhanced_article_handler import EnhancedArticleHandler
from ..registry import register_workflow

logger = logging.getLogger(__name__)


@register_workflow('enhanced_article_with_image')
class EnhancedArticleWithImageHandler(EnhancedArticleHandler):
    """Extend enhanced article workflow with contextual image generation."""

    _SUPPORTED_PROVIDERS = {'openai', 'gemini'}
    _VALID_STYLES = {'professional', 'creative', 'minimalist', 'abstract', 'realistic'}

    def validate_inputs(self, context: Dict[str, Any]) -> None:
        super().validate_inputs(context)

        provider = (context.get('image_provider') or 'openai').lower()
        if provider not in self._SUPPORTED_PROVIDERS:
            raise ValueError("Image provider must be 'openai' or 'gemini'")

        style = (context.get('image_style') or 'professional').lower()
        if style not in self._VALID_STYLES:
            raise ValueError(f"Image style must be one of: {sorted(self._VALID_STYLES)}")

        logger.info("✅ Enhanced article with image inputs validated")

    def prepare_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        context = super().prepare_context(context)

        context.setdefault('image_style', 'professional')
        context.setdefault('image_provider', 'openai')
        context.setdefault('image_size', '1024x1024')
        context.setdefault('image_quality', 'standard')
        context['requires_image_generation'] = True
        context['content_type'] = 'enhanced_article_with_image'

        logger.info(
            "🖼️ Image generation context prepared with provider=%s style=%s",
            context.get('image_provider'),
            context.get('image_style')
        )
        return context

    def post_process_task(
        self,
        task_id: str,
        task_output: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        context = super().post_process_task(task_id, task_output, context)

        if task_id == 'task5_image_generation':
            raw_payload = self._extract_tool_payload(task_output)
            image_data: Optional[Dict[str, Any]] = None

            if raw_payload:
                try:
                    image_data = json.loads(raw_payload)
                    context['generated_image'] = image_data
                    context['image_metadata'] = {
                        'provider': image_data.get('provider'),
                        'model': image_data.get('model'),
                        'success': image_data.get('success', False)
                    }
                    context['image_generated'] = image_data.get('success', False)
                    logger.info("🖼️ Image generation result captured (provider=%s)", image_data.get('provider'))
                except json.JSONDecodeError:
                    logger.warning("⚠️ Unable to parse image generation output as JSON")
                    context['image_generation_failed'] = True
            else:
                logger.warning("⚠️ Image generation output is empty")
                context['image_generation_failed'] = True

        return context

    def post_process_workflow(self, context: Dict[str, Any]) -> Dict[str, Any]:
        context = super().post_process_workflow(context)

        image_output = context.get('generated_image')
        if not image_output:
            raw_output = context.get('task5_image_generation_output')
            payload = self._extract_tool_payload(raw_output) if raw_output else None
            if payload:
                try:
                    image_output = json.loads(payload)
                    context['generated_image'] = image_output
                except json.JSONDecodeError:
                    logger.debug("Image payload present but not valid JSON")

        if image_output:
            metadata = context.setdefault('image_metadata', {})
            metadata.setdefault('provider', image_output.get('provider'))
            metadata.setdefault('success', image_output.get('success'))
            context['image_generated'] = image_output.get('success', False)
            logger.info("🖼️ Final image metadata stored for workflow")

        summary = context.get('workflow_summary') or {}
        summary['includes_image'] = bool(image_output)
        summary['image_provider'] = context.get('image_metadata', {}).get('provider')
        context['workflow_summary'] = summary

        return context

    @staticmethod
    def _extract_tool_payload(output: str | None) -> str | None:
        if not output:
            return None

        match = re.search(r"\[image_generation_tool RESULT\](.*?)\[/image_generation_tool RESULT\]", output, re.DOTALL)
        if match:
            return match.group(1).strip()

        return output.strip() if output.strip() else None
