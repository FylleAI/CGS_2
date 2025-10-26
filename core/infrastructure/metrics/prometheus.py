"""
Prometheus metrics for Workflow API.

Exposes metrics for cache performance, card retrieval, and usage tracking.
"""

import logging
from prometheus_client import Counter, Gauge, Histogram, CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST

logger = logging.getLogger(__name__)

# Create a custom registry for workflow metrics
workflow_registry = CollectorRegistry()

# Cache metrics
workflow_cache_hit_total = Counter(
    "workflow_cache_hit_total",
    "Total number of cache hits",
    ["card_type"],
    registry=workflow_registry,
)

workflow_cache_miss_total = Counter(
    "workflow_cache_miss_total",
    "Total number of cache misses",
    ["card_type"],
    registry=workflow_registry,
)

workflow_cache_hit_rate = Gauge(
    "workflow_cache_hit_rate",
    "Current cache hit rate (0.0-1.0)",
    registry=workflow_registry,
)

# Card retrieval metrics
workflow_retrieve_duration_ms = Histogram(
    "workflow_retrieve_duration_ms",
    "Duration of card retrieval in milliseconds",
    buckets=[10, 25, 50, 100, 200, 500, 1000, 2000, 5000],
    registry=workflow_registry,
)

cards_retrieve_p95_ms = Histogram(
    "cards_retrieve_p95_ms",
    "p95 latency for /cards/retrieve in milliseconds",
    buckets=[10, 25, 50, 100, 200, 500, 1000, 2000, 5000],
    registry=workflow_registry,
)

# Usage tracking metrics
card_usage_events_total = Counter(
    "card_usage_events_total",
    "Total number of card usage events sent",
    ["card_type", "workflow_type"],
    registry=workflow_registry,
)

card_usage_events_failed = Counter(
    "card_usage_events_failed",
    "Total number of failed card usage events",
    ["card_type", "workflow_type"],
    registry=workflow_registry,
)

# Workflow execution metrics
workflow_card_only_total = Counter(
    "workflow_card_only_total",
    "Total workflows using card_ids (preferred path)",
    ["workflow_type"],
    registry=workflow_registry,
)

workflow_legacy_context_total = Counter(
    "workflow_legacy_context_total",
    "Total workflows using legacy context (deprecated)",
    ["workflow_type"],
    registry=workflow_registry,
)

workflow_card_only_percentage = Gauge(
    "workflow_card_only_percentage",
    "Percentage of workflows using card_ids (0.0-100.0)",
    registry=workflow_registry,
)

workflow_execution_duration_ms = Histogram(
    "workflow_execution_duration_ms",
    "Total workflow execution duration in milliseconds",
    ["workflow_type", "status"],
    buckets=[100, 250, 500, 1000, 2000, 5000, 10000, 30000, 60000],
    registry=workflow_registry,
)

# Partial result metrics
workflow_partial_result_total = Counter(
    "workflow_partial_result_total",
    "Total workflows with partial card retrieval",
    ["workflow_type"],
    registry=workflow_registry,
)

workflow_retrieve_failure_total = Counter(
    "workflow_retrieve_failure_total",
    "Total card retrieval failures",
    ["workflow_type", "error_type"],
    registry=workflow_registry,
)


class WorkflowMetrics:
    """Helper class for recording workflow metrics."""
    
    @staticmethod
    def record_cache_hit(card_type: str):
        """Record a cache hit."""
        workflow_cache_hit_total.labels(card_type=card_type).inc()
    
    @staticmethod
    def record_cache_miss(card_type: str):
        """Record a cache miss."""
        workflow_cache_miss_total.labels(card_type=card_type).inc()
    
    @staticmethod
    def update_cache_hit_rate(hit_rate: float):
        """Update the current cache hit rate."""
        workflow_cache_hit_rate.set(hit_rate)
    
    @staticmethod
    def record_retrieve_duration(duration_ms: float):
        """Record card retrieval duration."""
        workflow_retrieve_duration_ms.observe(duration_ms)
        cards_retrieve_p95_ms.observe(duration_ms)
    
    @staticmethod
    def record_usage_event(card_type: str, workflow_type: str, success: bool = True):
        """Record a card usage event."""
        if success:
            card_usage_events_total.labels(
                card_type=card_type,
                workflow_type=workflow_type,
            ).inc()
        else:
            card_usage_events_failed.labels(
                card_type=card_type,
                workflow_type=workflow_type,
            ).inc()
    
    @staticmethod
    def record_workflow_execution(
        workflow_type: str,
        duration_ms: float,
        status: str,
        using_card_ids: bool,
        partial_result: bool = False,
    ):
        """Record workflow execution metrics."""
        # Record execution duration
        workflow_execution_duration_ms.labels(
            workflow_type=workflow_type,
            status=status,
        ).observe(duration_ms)
        
        # Record path used (card_ids vs legacy context)
        if using_card_ids:
            workflow_card_only_total.labels(workflow_type=workflow_type).inc()
        else:
            workflow_legacy_context_total.labels(workflow_type=workflow_type).inc()
        
        # Record partial result
        if partial_result:
            workflow_partial_result_total.labels(workflow_type=workflow_type).inc()
        
        # Update card_only percentage
        WorkflowMetrics._update_card_only_percentage()
    
    @staticmethod
    def record_retrieve_failure(workflow_type: str, error_type: str):
        """Record a card retrieval failure."""
        workflow_retrieve_failure_total.labels(
            workflow_type=workflow_type,
            error_type=error_type,
        ).inc()
    
    @staticmethod
    def _update_card_only_percentage():
        """Update the percentage of workflows using card_ids."""
        try:
            # Get total counts from counters
            card_only_count = sum(
                workflow_card_only_total.labels(workflow_type=wt)._value.get()
                for wt in ["premium_newsletter", "onboarding_content"]
            )
            legacy_count = sum(
                workflow_legacy_context_total.labels(workflow_type=wt)._value.get()
                for wt in ["premium_newsletter", "onboarding_content"]
            )
            
            total = card_only_count + legacy_count
            if total > 0:
                percentage = (card_only_count / total) * 100
                workflow_card_only_percentage.set(percentage)
        except Exception as e:
            logger.warning(f"Failed to update card_only_percentage: {e}")


def get_metrics() -> bytes:
    """
    Get Prometheus metrics in text format.
    
    Returns:
        Metrics in Prometheus text format
    """
    return generate_latest(workflow_registry)


def get_metrics_content_type() -> str:
    """
    Get the content type for Prometheus metrics.
    
    Returns:
        Content type string
    """
    return CONTENT_TYPE_LATEST

