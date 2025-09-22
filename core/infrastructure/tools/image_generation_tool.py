"""Lightweight image generation helper for prompt-centric workflows."""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class ImageGenerationTool:
    """Utility that prepares deterministic image payloads for downstream services.

    The goal is to provide agents with a stable interface that mimics an
    image-generation API. Actual rendering can be handled by a separate
    service once prompts and parameters are approved.
    """

    def __init__(self, default_provider: str = "openai") -> None:
        self.default_provider = default_provider

    async def generate(
        self,
        prompt: str,
        *,
        provider: Optional[str] = None,
        style: Optional[str] = None,
        aspect_ratio: str = "16:9",
        negative_prompt: Optional[str] = None,
        brand_notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Return a structured payload describing the desired image.

        Args:
            prompt: Descriptive prompt to send to the image model.
            provider: Preferred provider ("openai", "gemini", etc.).
            style: Short label describing the visual style.
            aspect_ratio: Desired aspect ratio string (e.g. "16:9").
            negative_prompt: Optional negative prompt guidance.
            brand_notes: Additional brand alignment notes.

        Returns:
            Dictionary with prompt metadata and a deterministic placeholder URL.
        """
        selected_provider = (provider or self.default_provider).lower()
        style_label = style or "photoreal"
        negative = negative_prompt or ""

        logger.info(
            "🎨 ImageGenerationTool.generate called with provider=%s, style=%s",
            selected_provider,
            style_label,
        )

        timestamp = datetime.now(timezone.utc).isoformat()
        digest_source = f"{selected_provider}|{prompt}|{style_label}|{aspect_ratio}|{negative}".encode("utf-8")
        prompt_hash = hashlib.sha256(digest_source).hexdigest()[:16]
        placeholder_url = f"prompt://{selected_provider}/{prompt_hash}"

        payload: Dict[str, Any] = {
            "provider": selected_provider,
            "prompt": prompt,
            "style": style_label,
            "aspect_ratio": aspect_ratio,
            "negative_prompt": negative,
            "brand_notes": brand_notes or "",
            "generated_at": timestamp,
            "image_url": placeholder_url,
        }

        logger.debug("🎨 Image payload prepared: %s", payload)
        return payload
