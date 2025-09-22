"""Thin Perplexity adapter exposing a simple search function."""

from __future__ import annotations

import os
import time
import logging
from typing import Optional, Dict, Any

import aiohttp

logger = logging.getLogger(__name__)


class PerplexityResearchTool:
    """Minimal wrapper around the Perplexity chat-completions API.

    This adapter performs no business logic. It simply forwards a query to
    Perplexity and returns the raw response along with basic metadata.
    Agents are responsible for any domain filtering, timeframe logic,
    or policy enforcement.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = 30,
    ) -> None:
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.model = model or "sonar-pro"
        self.timeout = timeout

    async def search(
        self, query: str, opts: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a Perplexity search.

        Args:
            query: Free-form search query.
            opts: Optional dictionary merged into the request payload.

        Returns:
            Dict containing provider metadata and raw API response. The shape is::

                {
                    "provider": "perplexity",
                    "model_used": str,
                    "duration_ms": int,
                    "data": {...raw Perplexity response...}
                }

        Raises:
            ValueError: If API key is missing.
            Exception: For HTTP errors returned by the API.
        """

        if not self.api_key:
            raise ValueError("Perplexity API key not configured")

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": "user", "content": query}],
        }
        if opts:
            payload.update(opts)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        start = time.time()
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.base_url,
                json=payload,
                headers=headers,
                timeout=self.timeout,
                ssl=False,
            ) as resp:
                data = await resp.json()
                if resp.status != 200:
                    raise Exception(f"API error {resp.status}: {data}")

        duration_ms = int((time.time() - start) * 1000)
        logger.debug("Perplexity search completed in %sms", duration_ms)
        return {
            "provider": "perplexity",
            "model_used": data.get("model", self.model),
            "duration_ms": duration_ms,
            "data": data,
        }
