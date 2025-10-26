"""Utility for estimating tool execution costs.

This module centralises the logic required to compute the monetary cost of
non-LLM tool invocations. While LLM usage costs are derived from token
information, tool calls often expose heterogeneous metadata (per-call pricing,
usage counters, etc.). The :class:`ToolCostCalculator` consolidates those data
points and also supports explicit overrides via environment variables using the
``TOOL_COST_<TOOL_NAME>`` convention.

The calculator intentionally favours transparency:

* Any explicit ``cost_usd`` value attached to a tool response is honoured.
* Per-call pricing can be supplied either through tool metadata or execution
  metadata (``cost_per_call_usd``).
* Unit-based pricing is supported (``unit_cost_usd`` * ``units``).
* Environment overrides provide an escape hatch when providers do not return
  cost data natively.

The outcome is a consistent cost signal for workflow analytics and billing
reports.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional

logger = logging.getLogger(__name__)


def _normalise_key(value: str) -> str:
    """Normalise tool identifiers for lookup consistency."""

    return value.lower().replace("/", "_").replace(" ", "_").replace("-", "_")


@dataclass
class ToolCostDetails:
    """Structured representation of a tool cost calculation."""

    cost_usd: float = 0.0
    units: float = 1.0
    source: str = "unknown"


class ToolCostCalculator:
    """Derive monetary costs for tool calls using flexible heuristics."""

    ENV_PREFIX = "TOOL_COST_"

    def __init__(self) -> None:
        self._overrides = self._load_overrides()

    @staticmethod
    def _safe_float(value: Any) -> Optional[float]:
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _load_overrides(self) -> Dict[str, float]:
        overrides: Dict[str, float] = {}
        for key, value in os.environ.items():
            if not key.startswith(self.ENV_PREFIX):
                continue

            normalised = _normalise_key(key[len(self.ENV_PREFIX) :])
            parsed = self._safe_float(value)
            if parsed is None:
                logger.warning(
                    "Ignoring invalid tool cost override %s=%s", key, value
                )
                continue
            overrides[normalised] = parsed
        return overrides

    def refresh_overrides(self) -> None:
        """Re-read override configuration from the environment."""

        self._overrides = self._load_overrides()

    def _lookup_override(self, candidates: Iterable[str]) -> Optional[float]:
        for candidate in candidates:
            normalised = _normalise_key(candidate)
            if normalised in self._overrides:
                return self._overrides[normalised]
        return None

    def calculate_cost(
        self,
        tool_name: str,
        tool_metadata: Optional[Dict[str, Any]] = None,
        execution_metadata: Optional[Dict[str, Any]] = None,
    ) -> ToolCostDetails:
        """Compute the monetary cost of a tool execution.

        Parameters
        ----------
        tool_name:
            Canonical name of the tool.
        tool_metadata:
            Static metadata registered with the tool (e.g. provider, default
            pricing).
        execution_metadata:
            Dynamic metadata returned by a specific tool execution.
        """

        tool_metadata = tool_metadata or {}
        execution_metadata = execution_metadata or {}

        # 1. Explicit cost in execution metadata wins.
        for key in ("cost_usd", "total_cost", "price_usd"):
            value = execution_metadata.get(key)
            parsed = self._safe_float(value)
            if parsed is not None:
                return ToolCostDetails(cost_usd=max(parsed, 0.0), source="execution")

        # 2. Unit-based pricing (cost_per_call_usd / unit_cost_usd).
        usage_tokens = execution_metadata.get("usage_tokens")
        per_1k = execution_metadata.get("cost_per_1k_tokens_usd") or tool_metadata.get(
            "cost_per_1k_tokens_usd"
        )
        parsed_usage = self._safe_float(usage_tokens)
        parsed_per_1k = self._safe_float(per_1k)
        if parsed_usage is not None and parsed_per_1k is not None:
            token_cost = max((parsed_usage / 1000.0) * parsed_per_1k, 0.0)
            return ToolCostDetails(
                cost_usd=token_cost,
                units=parsed_usage,
                source="usage",
            )

        unit_cost = execution_metadata.get("unit_cost_usd")
        if unit_cost is None:
            unit_cost = execution_metadata.get("cost_per_call_usd")
        if unit_cost is None:
            unit_cost = tool_metadata.get("unit_cost_usd")
        if unit_cost is None:
            unit_cost = tool_metadata.get("cost_per_call_usd")

        units = (
            execution_metadata.get("units")
            or execution_metadata.get("call_count")
            or execution_metadata.get("calls")
            or execution_metadata.get("requests")
            or 1
        )

        parsed_unit_cost = self._safe_float(unit_cost)
        parsed_units = self._safe_float(units)
        if parsed_unit_cost is not None and parsed_units is not None:
            total = max(parsed_unit_cost * parsed_units, 0.0)
            source = (
                "execution"
                if unit_cost in execution_metadata.values()
                else "metadata"
            )
            return ToolCostDetails(cost_usd=total, units=parsed_units, source=source)

        # 3. Environment overrides using a set of lookup keys.
        override_candidates = [tool_name]
        provider = tool_metadata.get("provider") or execution_metadata.get(
            "provider"
        )
        if provider:
            override_candidates.append(provider)
            override_candidates.append(f"{provider}_{tool_name}")
        if "cost_override_key" in tool_metadata:
            override_candidates.append(tool_metadata["cost_override_key"])

        override = self._lookup_override(override_candidates)
        if override is not None:
            parsed_units = parsed_units if parsed_units is not None else 1.0
            return ToolCostDetails(
                cost_usd=max(override * parsed_units, 0.0),
                units=parsed_units,
                source="environment",
            )

        # 4. Fallback to zero cost when nothing else is available.
        return ToolCostDetails(cost_usd=0.0, units=parsed_units or 1.0, source="none")


# Singleton-style helper consistent with other logging utilities.
tool_cost_calculator = ToolCostCalculator()

