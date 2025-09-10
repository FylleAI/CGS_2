"""Minimal Perplexity API wrapper.

This tool acts as a thin wrapper around the Perplexity
chat-completions endpoint. All higher level research
logic (domain selection, query strategies, etc.) should
live in agents. The tool simply forwards a query to the
API and returns the raw JSON response as a string.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


class PerplexityResearchTool:
    """Simple asynchronous wrapper for the Perplexity API."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None) -> None:
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.model = model or "sonar-pro"
        self.max_tokens = 1000
        self.temperature = 0.2
        logger.info(f"🔍 PerplexityResearchTool initialized (model={self.model})")

    async def search(self, query: str) -> str:
        """Execute a free-form search query using Perplexity.

        Args:
            query: Text query to send to the API.

        Returns:
            Raw JSON response from the API as a string.
        """
        if not self.api_key:
            raise Exception("Perplexity API key not configured")

        import aiohttp
        import ssl

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a helpful research assistant."},
                {"role": "user", "content": query},
            ],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        connector = aiohttp.TCPConnector(ssl=ssl_context)

        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post(self.base_url, json=payload, headers=headers, timeout=30) as response:
                result = await response.json()
                return json.dumps(result)
