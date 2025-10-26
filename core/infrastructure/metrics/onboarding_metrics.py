"""Prometheus metrics for Onboarding API.

Tracks:
- Cards created
- Batch creation latency
- Session creation
- Errors

Note: All metrics are registered in the workflow_registry to ensure
they are exposed at the /metrics endpoint.
"""

from prometheus_client import Counter, Histogram

# Import the workflow registry to register onboarding metrics
from core.infrastructure.metrics.prometheus import workflow_registry

# Cards creation metrics
onboarding_cards_created_total = Counter(
    "onboarding_cards_created_total",
    "Total number of cards created from onboarding sessions",
    ["tenant_id", "card_type"],
    registry=workflow_registry,
)

onboarding_batch_duration_ms = Histogram(
    "onboarding_batch_duration_ms",
    "Duration of card batch creation in milliseconds",
    ["tenant_id"],
    buckets=[100, 250, 500, 1000, 2500, 5000, 10000],
    registry=workflow_registry,
)

# Session metrics
onboarding_sessions_total = Counter(
    "onboarding_sessions_total",
    "Total number of onboarding sessions created",
    ["tenant_id"],
    registry=workflow_registry,
)

onboarding_sessions_completed_total = Counter(
    "onboarding_sessions_completed_total",
    "Total number of onboarding sessions completed",
    ["tenant_id", "status"],
    registry=workflow_registry,
)

# Error metrics
onboarding_errors_total = Counter(
    "onboarding_errors_total",
    "Total number of onboarding errors",
    ["tenant_id", "error_type"],
    registry=workflow_registry,
)

