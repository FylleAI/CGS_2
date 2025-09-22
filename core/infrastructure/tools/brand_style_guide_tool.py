"""Brand style helper tool for client-specific visual guidance."""

from __future__ import annotations

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class BrandStyleGuideTool:
    """Expose lightweight brand metadata to creative agents."""

    def __init__(self) -> None:
        self._guides: Dict[str, Dict[str, Any]] = {
            "reopla": {
                "client": "Reopla",
                "palette": ["#2E5BBA", "#8BC34A", "#FF9800", "#0F1B33"],
                "typography": {
                    "heading": "Geometric sans-serif, bold, high contrast",
                    "body": "Humanist sans-serif, clear and approachable",
                },
                "image_keywords": [
                    "modern architecture",
                    "collaborative workspaces",
                    "proptech dashboards",
                    "sustainable urban living",
                    "sunlit interiors",
                ],
                "lighting_preferences": "natural daylight or warm twilight with balanced contrast",
                "composition": "clean lines, wide-angle establishing shots, inclusive teams in motion",
                "tone": "confident, progressive, welcoming",
            }
        }

    async def get_style(self, client_name: str) -> Dict[str, Any]:
        """Return brand guidance for the requested client.

        Args:
            client_name: Name or identifier of the client profile.

        Returns:
            Dictionary containing palette, typography, and imagery guidance.
        """
        normalized = (client_name or "").strip().lower()
        logger.info("🎨 BrandStyleGuideTool.get_style requested for client=%s", normalized or "<unknown>")

        guide = self._guides.get(normalized)
        if guide:
            return guide

        logger.warning("⚠️ No brand style guide configured for client '%s'", client_name)
        return {
            "client": client_name or "unknown",
            "palette": [],
            "typography": {},
            "image_keywords": [],
            "tone": "neutral",
            "notes": "No client-specific style guide available."
        }
