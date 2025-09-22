"""Image generation tool supporting multiple providers."""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, Optional

from ..config.settings import Settings
from ..external_services.openai_adapter import OpenAIAdapter
from ..external_services.gemini_adapter import GeminiAdapter
from ...domain.value_objects.provider_config import ProviderConfig, LLMProvider

logger = logging.getLogger(__name__)


class ImageGenerationTool:
    """High-level helper that orchestrates image generation across providers."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings
        self._openai_api_key = (
            settings.openai_api_key if settings else os.getenv("OPENAI_API_KEY")
        )
        self._gemini_api_key = (
            settings.gemini_api_key if settings else os.getenv("GEMINI_API_KEY")
        )
        self._openai_adapter: Optional[OpenAIAdapter] = None
        self._gemini_adapter: Optional[GeminiAdapter] = None

    def _get_openai_adapter(self) -> OpenAIAdapter:
        if self._openai_adapter is None:
            self._openai_adapter = OpenAIAdapter(self._openai_api_key)
        return self._openai_adapter

    def _get_gemini_adapter(self) -> GeminiAdapter:
        if self._gemini_adapter is None:
            self._gemini_adapter = GeminiAdapter(self._gemini_api_key)
        return self._gemini_adapter

    async def generate_image(
        self,
        prompt: str,
        provider: str = "openai",
        style: str = "professional",
        size: str = "1024x1024",
        quality: str = "standard",
    ) -> Dict[str, Any]:
        """Generate an image using the requested provider."""

        provider_normalized = (provider or "openai").lower()
        logger.info(
            "🖼️ Generating image with provider=%s style=%s size=%s",
            provider_normalized,
            style,
            size,
        )

        try:
            if provider_normalized == "openai":
                return await self._generate_with_openai(prompt, style, size, quality)
            if provider_normalized == "gemini":
                return await self._generate_with_gemini(prompt, style, size)

            raise ValueError(f"Unsupported image provider: {provider}")
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.error("❌ Image generation failed: %s", exc)
            return {
                "success": False,
                "error": str(exc),
                "provider": provider_normalized,
            }

    async def _generate_with_openai(
        self,
        prompt: str,
        style: str,
        size: str,
        quality: str,
    ) -> Dict[str, Any]:
        adapter = self._get_openai_adapter()
        config = ProviderConfig(
            provider=LLMProvider.OPENAI,
            model="dall-e-3",
            api_key=self._openai_api_key,
            additional_params={
                "size": size,
                "quality": quality,
                "style": "vivid" if style == "creative" else "natural",
            },
        )

        result = await adapter.generate_image(prompt, config)
        return {
            "success": True,
            "provider": "openai",
            "model": "dall-e-3",
            "image_url": result.get("url"),
            "image_data": result.get("b64_json"),
            "revised_prompt": result.get("revised_prompt"),
            "prompt": prompt,
            "style": style,
            "size": size,
            "quality": quality,
        }

    async def _generate_with_gemini(
        self,
        prompt: str,
        style: str,
        size: str,
    ) -> Dict[str, Any]:
        adapter = self._get_gemini_adapter()
        config = ProviderConfig(
            provider=LLMProvider.GEMINI,
            model="gemini-pro-vision",
            api_key=self._gemini_api_key,
            additional_params={
                "size": size,
                "style": style,
            },
        )

        result = await adapter.generate_image(prompt, config)
        return {
            "success": True,
            "provider": "gemini",
            "model": "gemini-pro-vision",
            "image_url": result.get("url"),
            "image_data": result.get("data"),
            "prompt": prompt,
            "style": style,
            "size": size,
        }


async def image_generation_tool(
    article_content: str,
    image_style: str = "professional",
    image_provider: str = "openai",
) -> str:
    """Agent-facing wrapper that builds an image prompt from article content."""

    tool = ImageGenerationTool()

    excerpt = (article_content or "").strip()
    if len(excerpt) > 500:
        excerpt = excerpt[:500] + "..."

    prompt = (
        "Create an illustrative, brand-safe image that captures the main ideas of this compliance-approved "
        f"article. Style should be {image_style}.\n\nArticle summary:\n{excerpt}"
    )

    result = await tool.generate_image(
        prompt=prompt,
        provider=image_provider,
        style=image_style,
    )

    payload = {
        "prompt": prompt,
        **result,
    }

    return json.dumps(payload, indent=2)
