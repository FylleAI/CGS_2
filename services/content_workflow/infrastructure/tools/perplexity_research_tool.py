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
        cost_per_call_usd: Optional[float] = None,
        cost_per_1k_tokens_usd: Optional[float] = None,
    ) -> None:
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.model = model or "sonar-pro"
        self.timeout = timeout
        # Per-call fallback
        self.cost_per_call_usd, self.cost_source = self._resolve_cost(
            cost_per_call_usd,
            "PERPLEXITY_COST_PER_CALL_USD",
        )
        # Single blended per-1k rate fallback
        per_1k, token_source = self._resolve_cost(
            cost_per_1k_tokens_usd, "PERPLEXITY_COST_PER_1K_TOKENS"
        )
        self.cost_per_token_usd = per_1k / 1000.0 if per_1k else 0.0
        self.token_cost_source = token_source
        # Precise split rates (optional): Sonar and Sonar Pro
        sonar_in_1k, _ = self._resolve_cost(None, "PERPLEXITY_SONAR_COST_PER_1K_TOKENS_INPUT")
        sonar_out_1k, _ = self._resolve_cost(None, "PERPLEXITY_SONAR_COST_PER_1K_TOKENS_OUTPUT")
        sonar_pro_in_1k, _ = self._resolve_cost(None, "PERPLEXITY_SONAR_PRO_COST_PER_1K_TOKENS_INPUT")
        sonar_pro_out_1k, _ = self._resolve_cost(None, "PERPLEXITY_SONAR_PRO_COST_PER_1K_TOKENS_OUTPUT")
        self.sonar_in_per_token = (sonar_in_1k or 0.0) / 1000.0
        self.sonar_out_per_token = (sonar_out_1k or 0.0) / 1000.0
        self.sonar_pro_in_per_token = (sonar_pro_in_1k or 0.0) / 1000.0
        self.sonar_pro_out_per_token = (sonar_pro_out_1k or 0.0) / 1000.0
        # For reporting/debug purposes
        self.split_rates_enabled = any(
            [self.sonar_in_per_token, self.sonar_out_per_token, self.sonar_pro_in_per_token, self.sonar_pro_out_per_token]
        )

    @staticmethod
    def _resolve_cost(
        explicit_cost: Optional[float], env_var: str
    ) -> tuple[float, str]:
        if explicit_cost is not None:
            try:
                return float(explicit_cost), "explicit"
            except (TypeError, ValueError):  # pragma: no cover - defensive
                logger.warning(
                    "Invalid explicit cost supplied for Perplexity tool: %s",
                    explicit_cost,
                )
        env_value = os.getenv(env_var)
        if env_value:
            try:
                return float(env_value), f"env:{env_var}"
            except ValueError:  # pragma: no cover - defensive
                logger.warning(
                    "Invalid %s value for Perplexity tool cost: %s",
                    env_var,
                    env_value,
                )
        return 0.0, "default"

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
        usage = data.get("usage", {}) if isinstance(data, dict) else {}
        prompt_tokens = 0
        completion_tokens = 0
        total_tokens = 0
        if isinstance(usage, dict):
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens") or (prompt_tokens + completion_tokens)

        token_cost = None
        cost_source = self.cost_source

        # Prefer precise split rates when available and usage is present
        model_used = str(data.get("model", self.model)).lower()
        if self.split_rates_enabled and (prompt_tokens or completion_tokens):
            in_rate = out_rate = 0.0
            if "sonar-pro" in model_used:
                in_rate = self.sonar_pro_in_per_token
                out_rate = self.sonar_pro_out_per_token
            elif "sonar" in model_used:
                in_rate = self.sonar_in_per_token
                out_rate = self.sonar_out_per_token

            if in_rate or out_rate:
                token_cost = prompt_tokens * in_rate + completion_tokens * out_rate
                cost_source = "usage:split"

        # Fallback to single blended per-1k rate
        if token_cost is None and total_tokens and self.cost_per_token_usd:
            token_cost = total_tokens * self.cost_per_token_usd
            cost_source = "usage"

        cost_usd = token_cost if token_cost is not None else self.cost_per_call_usd

        return {
            "provider": "perplexity",
            "model_used": data.get("model", self.model),
            "duration_ms": duration_ms,
            "data": data,
            "usage_tokens": total_tokens,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "cost_usd": cost_usd,
            "cost_per_call_usd": self.cost_per_call_usd,
            "cost_per_1k_tokens_usd": self.cost_per_token_usd * 1000 if self.cost_per_token_usd else 0.0,
            "cost_source": cost_source,
            "token_cost_source": self.token_cost_source,
        }
