"""Prometheus metrics for Onboarding API.

Tracks:
- Cards created
- Batch creation latency
- Session creation
- Errors
"""

from prometheus_client import Counter, Histogram

# Cards creation metrics
onboarding_cards_created_total = Counter(
    "onboarding_cards_created_total",
    "Total number of cards created from onboarding sessions",
    ["tenant_id", "card_type"],
)

onboarding_batch_duration_ms = Histogram(
    "onboarding_batch_duration_ms",
    "Duration of card batch creation in milliseconds",
    ["tenant_id"],
    buckets=[100, 250, 500, 1000, 2500, 5000, 10000],
)

# Session metrics
onboarding_sessions_total = Counter(
    "onboarding_sessions_total",
    "Total number of onboarding sessions created",
    ["tenant_id"],
)

onboarding_sessions_completed_total = Counter(
    "onboarding_sessions_completed_total",
    "Total number of onboarding sessions completed",
    ["tenant_id", "status"],
)

# Error metrics
onboarding_errors_total = Counter(
    "onboarding_errors_total",
    "Total number of onboarding errors",
    ["tenant_id", "error_type"],
)

