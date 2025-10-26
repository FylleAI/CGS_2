"""Enhanced cost calculation system for accurate token usage and cost tracking."""

import logging
import re
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class ModelTier(Enum):
    """Model pricing tiers."""

    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    REASONING = "reasoning"


@dataclass
class TokenUsage:
    """Detailed token usage information."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cached_tokens: int = 0  # For providers that support caching
    reasoning_tokens: int = 0  # For reasoning models like o1
    cache_write_tokens: int = 0  # Tokens billed for cache creation (Anthropic, Gemini)
    cache_read_tokens: int = 0  # Tokens billed when reading from cache

    def __post_init__(self):
        if self.cache_read_tokens == 0 and self.cached_tokens:
            self.cache_read_tokens = self.cached_tokens
        elif self.cached_tokens == 0 and self.cache_read_tokens:
            self.cached_tokens = self.cache_read_tokens

        if self.total_tokens == 0:
            base_total = self.prompt_tokens + self.completion_tokens
            if self.reasoning_tokens:
                base_total += self.reasoning_tokens
            if self.cache_read_tokens:
                base_total += self.cache_read_tokens
            self.total_tokens = base_total


@dataclass
class CostBreakdown:
    """Detailed cost breakdown."""

    prompt_cost: float = 0.0
    completion_cost: float = 0.0
    reasoning_cost: float = 0.0
    cache_cost: float = 0.0
    total_cost: float = 0.0
    currency: str = "USD"

    def __post_init__(self):
        if self.total_cost == 0.0:
            self.total_cost = (
                self.prompt_cost
                + self.completion_cost
                + self.reasoning_cost
                + self.cache_cost
            )


class CostCalculator:
    """
    Enhanced cost calculator with accurate pricing for all supported providers.

    This calculator uses real-time pricing information and handles different
    model tiers, token types, and provider-specific features.
    """

    def __init__(self):
        self.pricing_data = self._load_pricing_data()
        logger.info("💰 Cost calculator initialized with current pricing data")

    def _load_pricing_data(self) -> Dict[str, Dict[str, Any]]:
        """Load current pricing data for all providers and models."""
        return {
            "openai": {
                # GPT-4o models
                "gpt-4o": {
                    "tier": ModelTier.PREMIUM,
                    "prompt_cost_per_1k": 0.0025,
                    "completion_cost_per_1k": 0.01,
                    "supports_caching": False,
                },
                "gpt-4o-mini": {
                    "tier": ModelTier.STANDARD,
                    "prompt_cost_per_1k": 0.00015,
                    "completion_cost_per_1k": 0.0006,
                    "supports_caching": False,
                },
                # GPT-4 models
                "gpt-4": {
                    "tier": ModelTier.PREMIUM,
                    "prompt_cost_per_1k": 0.03,
                    "completion_cost_per_1k": 0.06,
                    "supports_caching": False,
                },
                "gpt-4-32k": {
                    "tier": ModelTier.PREMIUM,
                    "prompt_cost_per_1k": 0.06,
                    "completion_cost_per_1k": 0.12,
                    "supports_caching": False,
                },
                "gpt-4-turbo": {
                    "tier": ModelTier.PREMIUM,
                    "prompt_cost_per_1k": 0.01,
                    "completion_cost_per_1k": 0.03,
                    "supports_caching": False,
                },
                # GPT-3.5 models
                "gpt-3.5-turbo": {
                    "tier": ModelTier.BASIC,
                    "prompt_cost_per_1k": 0.0015,
                    "completion_cost_per_1k": 0.0020,
                    "supports_caching": False,
                },
                # o1 reasoning models
                "o1": {
                    "tier": ModelTier.REASONING,
                    "prompt_cost_per_1k": 0.015,
                    "completion_cost_per_1k": 0.06,
                    "reasoning_cost_per_1k": 0.06,
                    "supports_caching": False,
                },
                "o1-mini": {
                    "tier": ModelTier.REASONING,
                    "prompt_cost_per_1k": 0.003,
                    "completion_cost_per_1k": 0.012,
                    "reasoning_cost_per_1k": 0.012,
                    "supports_caching": False,
                },
                "o1-pro": {
                    "tier": ModelTier.REASONING,
                    "prompt_cost_per_1k": 0.06,
                    "completion_cost_per_1k": 0.24,
                    "reasoning_cost_per_1k": 0.24,
                    "supports_caching": False,
                },
                "o3-mini": {
                    "tier": ModelTier.REASONING,
                    "prompt_cost_per_1k": 0.003,
                    "completion_cost_per_1k": 0.012,
                    "reasoning_cost_per_1k": 0.012,
                    "supports_caching": False,
                },
            },
            "anthropic": {
                # Claude 3.5 models
                "claude-3-5-haiku-20241022": {
                    "tier": ModelTier.BASIC,
                    "prompt_cost_per_1k": 0.00080,
                    "completion_cost_per_1k": 0.0040,
                    "supports_caching": True,
                    "cache_write_cost_per_1k": 0.0010,
                    "cache_read_cost_per_1k": 0.00008,
                },
                "claude-3-5-haiku-latest": {
                    "tier": ModelTier.BASIC,
                    "prompt_cost_per_1k": 0.00080,
                    "completion_cost_per_1k": 0.0040,
                    "supports_caching": True,
                    "cache_write_cost_per_1k": 0.0010,
                    "cache_read_cost_per_1k": 0.00008,
                },
                "claude-3-7-sonnet-20250219": {
                    "tier": ModelTier.PREMIUM,
                    "prompt_cost_per_1k": 0.003,
                    "completion_cost_per_1k": 0.015,
                    "supports_caching": True,
                    "cache_write_cost_per_1k": 0.00375,
                    "cache_read_cost_per_1k": 0.00030,
                },
                "claude-3-7-sonnet-latest": {
                    "tier": ModelTier.PREMIUM,
                    "prompt_cost_per_1k": 0.003,
                    "completion_cost_per_1k": 0.015,
                    "supports_caching": True,
                    "cache_write_cost_per_1k": 0.00375,
                    "cache_read_cost_per_1k": 0.00030,
                },
                # Claude 4 models (future pricing estimates)
                "claude-sonnet-4-20250514": {
                    "tier": ModelTier.PREMIUM,
                    "prompt_cost_per_1k": 0.005,
                    "completion_cost_per_1k": 0.025,
                    "supports_caching": True,
                    "cache_write_cost_per_1k": 0.0125,
                    "cache_read_cost_per_1k": 0.0005,
                },
                "claude-opus-4-20250514": {
                    "tier": ModelTier.PREMIUM,
                    "prompt_cost_per_1k": 0.015,
                    "completion_cost_per_1k": 0.075,
                    "supports_caching": True,
                    "cache_write_cost_per_1k": 0.0375,
                    "cache_read_cost_per_1k": 0.0015,
                },
                "claude-4.1-opus": {
                    "tier": ModelTier.PREMIUM,
                    "prompt_cost_per_1k": 0.015,
                    "completion_cost_per_1k": 0.075,
                    "supports_caching": True,
                    "cache_write_cost_per_1k": 0.01875,
                    "cache_read_cost_per_1k": 0.00150,
                },
            },
            "deepseek": {
                "deepseek-chat": {
                    "tier": ModelTier.BASIC,
                    "prompt_cost_per_1k": 0.00027,
                    "completion_cost_per_1k": 0.00110,
                    "supports_caching": False,
                },
                "deepseek-coder": {
                    "tier": ModelTier.BASIC,
                    "prompt_cost_per_1k": 0.00014,
                    "completion_cost_per_1k": 0.00028,
                    "supports_caching": False,
                },
                "deepseek-reasoner": {
                    "tier": ModelTier.BASIC,
                    "prompt_cost_per_1k": 0.00055,
                    "completion_cost_per_1k": 0.00219,
                    "supports_caching": False,
                },
            },
            "gemini": {
                # Gemini 2.5 Pro - Prompt <= 128k tokens
                "gemini-2.5-pro": {
                    "tier": ModelTier.PREMIUM,
                    "prompt_cost_per_1k": 0.00125,
                    "completion_cost_per_1k": 0.010,
                    "supports_caching": True,
                },
                # Gemini 2.5 Pro - Prompt > 128k tokens (higher pricing tier)
                "gemini-2.5-pro-large": {
                    "tier": ModelTier.PREMIUM,
                    "prompt_cost_per_1k": 0.00250,
                    "completion_cost_per_1k": 0.015,
                    "supports_caching": True,
                },
                # Gemini 2.5 Flash - Prompt <= 128k tokens
                "gemini-2.5-flash": {
                    "tier": ModelTier.STANDARD,
                    "prompt_cost_per_1k": 0.00030,
                    "completion_cost_per_1k": 0.00250,
                    "supports_caching": True,
                },
                # Gemini 2.0 Flash (similar pricing to 2.5 Flash)
                "gemini-2.0-flash": {
                    "tier": ModelTier.STANDARD,
                    "prompt_cost_per_1k": 0.000125,
                    "completion_cost_per_1k": 0.0005,
                    "supports_caching": True,
                    "cache_write_cost_per_1k": 0.00003125,
                    "cache_read_cost_per_1k": 0.00003125,
                },
                # Legacy models (keeping for backward compatibility)
                "gemini-1.5-pro": {
                    "tier": ModelTier.PREMIUM,
                    "prompt_cost_per_1k": 0.00125,
                    "completion_cost_per_1k": 0.005,
                    "supports_caching": True,
                    "cache_write_cost_per_1k": 0.0003125,
                    "cache_read_cost_per_1k": 0.0003125,
                },
                "gemini-1.5-flash": {
                    "tier": ModelTier.STANDARD,
                    "prompt_cost_per_1k": 0.000075,
                    "completion_cost_per_1k": 0.00030,
                    "supports_caching": True,
                    "cache_write_cost_per_1k": 0.00001875,
                    "cache_read_cost_per_1k": 0.0000375,
                    "cache_storage_cost_per_hour": 1.00,
                },
                "gemini-1.5-flash-large": {
                    "tier": ModelTier.STANDARD,
                    "prompt_cost_per_1k": 0.00015,
                    "completion_cost_per_1k": 0.00060,
                    "supports_caching": True,
                    "cache_write_cost_per_1k": 0.00001875,
                    "cache_read_cost_per_1k": 0.0000375,
                    "cache_storage_cost_per_hour": 1.00,
                },
            },
        }

    def calculate_cost(
        self,
        provider: str,
        model: str,
        token_usage: TokenUsage,
        cached_tokens: Optional[int] = None,
    ) -> CostBreakdown:
        """
        Calculate accurate cost based on real token usage.

        Args:
            provider: LLM provider name
            model: Model name
            token_usage: Actual token usage from API response
            cached_tokens: Number of cached tokens (for supported providers).
                When ``None`` the calculator falls back to the value exposed by
                ``token_usage.cached_tokens``.

        Returns:
            Detailed cost breakdown
        """
        provider_lower = provider.lower()

        if provider_lower not in self.pricing_data:
            logger.warning(f"⚠️ Unknown provider: {provider}, using default pricing")
            return self._calculate_default_cost(token_usage)

        provider_data = self.pricing_data[provider_lower]

        model_data = self._resolve_model_pricing(provider_lower, model)
        if model_data is None:
            logger.warning(
                f"⚠️ Unknown model: {model} for provider {provider}, using default pricing"
            )
            return self._calculate_default_cost(token_usage)

        # Calculate base costs
        prompt_cost = (token_usage.prompt_tokens / 1000) * model_data[
            "prompt_cost_per_1k"
        ]
        completion_cost = (token_usage.completion_tokens / 1000) * model_data[
            "completion_cost_per_1k"
        ]

        # Calculate reasoning cost for o1 models
        reasoning_cost = 0.0
        if "reasoning_cost_per_1k" in model_data and token_usage.reasoning_tokens > 0:
            reasoning_cost = (token_usage.reasoning_tokens / 1000) * model_data[
                "reasoning_cost_per_1k"
            ]

        # Determine cached token usage (explicit argument takes precedence)
        cached_token_count = (
            token_usage.cache_read_tokens
            if cached_tokens is None
            else cached_tokens
        )

        # Calculate cache costs for supported providers
        cache_cost = 0.0
        if model_data.get("supports_caching", False):
            if cached_token_count > 0:
                cache_read_cost = (cached_token_count / 1000) * model_data.get(
                    "cache_read_cost_per_1k", 0
                )
                cache_cost += cache_read_cost

            if token_usage.cache_write_tokens > 0:
                cache_write_rate = model_data.get("cache_write_cost_per_1k", 0)
                cache_cost += (
                    token_usage.cache_write_tokens / 1000
                ) * cache_write_rate

        cost_breakdown = CostBreakdown(
            prompt_cost=prompt_cost,
            completion_cost=completion_cost,
            reasoning_cost=reasoning_cost,
            cache_cost=cache_cost,
        )

        logger.debug(
            f"💰 Cost calculated for {provider}/{model}: "
            f"${cost_breakdown.total_cost:.6f} "
            f"({token_usage.total_tokens} tokens)"
        )

        return cost_breakdown

    def _resolve_model_pricing(
        self, provider: str, model: str
    ) -> Optional[Dict[str, Any]]:
        """Resolve pricing data for a model, handling aliases and version suffixes."""

        provider_models = self.pricing_data.get(provider, {})
        if not provider_models:
            return None

        if model in provider_models:
            return provider_models[model]

        normalized = self._normalize_model_name(model)
        if normalized in provider_models:
            return provider_models[normalized]

        # Attempt prefix/suffix based matching for future model variants
        for known_model, pricing in provider_models.items():
            if normalized.startswith(known_model) or known_model.startswith(normalized):
                return pricing

        return None

    @staticmethod
    def _normalize_model_name(model: str) -> str:
        """Normalize a model name by lowering case and stripping version suffixes."""

        name = model.strip().lower()
        name = name.replace(":", "-")
        # Remove common marketing suffixes
        for suffix in ("-latest", "-preview", "-beta", "-alpha", "-test"):
            if name.endswith(suffix):
                name = name[: -len(suffix)]

        # Drop date/version suffixes like -20250219 or -v1
        name = re.sub(r"-(\d{4,8}|v\d+)$", "", name)
        return name

    def _calculate_default_cost(self, token_usage: TokenUsage) -> CostBreakdown:
        """Fallback cost calculation for unknown providers/models."""
        # Use average pricing as fallback
        avg_prompt_cost = (token_usage.prompt_tokens / 1000) * 0.002
        avg_completion_cost = (token_usage.completion_tokens / 1000) * 0.006

        return CostBreakdown(
            prompt_cost=avg_prompt_cost, completion_cost=avg_completion_cost
        )

    def get_model_info(self, provider: str, model: str) -> Dict[str, Any]:
        """Get model information including tier and pricing."""
        provider_lower = provider.lower()

        if provider_lower not in self.pricing_data:
            return {"tier": ModelTier.BASIC, "supports_caching": False}

        provider_data = self.pricing_data[provider_lower]

        if model not in provider_data:
            return {"tier": ModelTier.BASIC, "supports_caching": False}

        return provider_data[model]


# Global cost calculator instance
cost_calculator = CostCalculator()
