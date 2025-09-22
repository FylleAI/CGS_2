"""Serper web search adapter."""

from __future__ import annotations

import os
import time
import logging
from typing import Optional, Dict, Any

import requests

logger = logging.getLogger(__name__)


class WebSearchTool:
    """Thin wrapper around the Serper search API."""

    def __init__(self, api_key: Optional[str] = None, timeout: int = 30) -> None:
        self.api_key = api_key or os.getenv("SERPER_API_KEY")
        self.base_url = "https://google.serper.dev/search"
        self.timeout = timeout

    async def search(
        self, query: str, opts: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Perform a web search and return the raw payload.

        Args:
            query: Search query string.
            opts: Optional dictionary merged into request payload (e.g. num, gl).

        Returns:
            Dict with provider metadata and raw Serper response.

        Raises:
            ValueError: if API key is missing.
            Exception: for HTTP errors.
        """

        if not self.api_key:
            raise ValueError("SERPER_API_KEY not configured")

        payload: Dict[str, Any] = {"q": query}
        if opts:
            payload.update(opts)

        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json",
        }

        start = time.time()
        response = requests.post(
            self.base_url, headers=headers, json=payload, timeout=self.timeout
        )
        data = response.json()
        if response.status_code != 200:
            raise Exception(f"API error {response.status_code}: {data}")

        duration_ms = (time.time() - start) * 1000
        logger.debug("Serper search completed in %sms", duration_ms)
        return {"provider": "serper", "duration_ms": duration_ms, "data": data}
