"""Prometheus metrics for Onboarding Service.

Sprint 4 Day 1: Cards API Integration Metrics

Tracks:
- Cards created from onboarding sessions
- Batch creation latency
- Session lifecycle
- Errors and partial creations
"""

from prometheus_client import Counter, Histogram, CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST

# Create a custom registry for onboarding metrics
onboarding_registry = CollectorRegistry()

# Cards creation metrics
onboarding_cards_created_total = Counter(
    "onboarding_cards_created_total",
    "Total number of cards created from onboarding sessions",
    ["tenant_id", "card_type"],
    registry=onboarding_registry,
)

onboarding_batch_duration_ms = Histogram(
    "onboarding_batch_duration_ms",
    "Duration of card batch creation in milliseconds",
    ["tenant_id"],
    buckets=[100, 250, 500, 1000, 2500, 5000, 10000],
    registry=onboarding_registry,
)

# Session metrics
onboarding_sessions_total = Counter(
    "onboarding_sessions_total",
    "Total number of onboarding sessions created",
    ["tenant_id"],
    registry=onboarding_registry,
)

onboarding_sessions_completed_total = Counter(
    "onboarding_sessions_completed_total",
    "Total number of onboarding sessions completed",
    ["tenant_id", "status"],
    registry=onboarding_registry,
)

# Error metrics
onboarding_errors_total = Counter(
    "onboarding_errors_total",
    "Total number of onboarding errors",
    ["tenant_id", "error_type"],
    registry=onboarding_registry,
)

# Partial creation metrics
onboarding_partial_creation_total = Counter(
    "onboarding_partial_creation_total",
    "Total number of partial card creations (< 4 cards)",
    ["tenant_id"],
    registry=onboarding_registry,
)


def get_metrics() -> bytes:
    """Get metrics in Prometheus format."""
    return generate_latest(onboarding_registry)


def get_metrics_content_type() -> str:
    """Get metrics content type."""
    return CONTENT_TYPE_LATEST

