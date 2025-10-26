"""
Metrics endpoint for Prometheus.

Exposes workflow, cache, and onboarding metrics in Prometheus format.
"""

import logging
from fastapi import APIRouter, Response

from core.infrastructure.metrics.prometheus import get_metrics, get_metrics_content_type

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/metrics")
async def prometheus_metrics():
    """
    Prometheus metrics endpoint.

    Returns metrics in Prometheus text format for scraping.

    Metrics exposed:

    **Workflow Metrics:**
    - workflow_cache_hit_total: Cache hits by card type
    - workflow_cache_miss_total: Cache misses by card type
    - workflow_cache_hit_rate: Current cache hit rate (0.0-1.0)
    - workflow_retrieve_duration_ms: Card retrieval duration histogram
    - cards_retrieve_p95_ms: p95 latency for card retrieval
    - card_usage_events_total: Usage events by card type and workflow type
    - card_usage_events_failed: Failed usage events
    - workflow_card_only_total: Workflows using card_ids
    - workflow_legacy_context_total: Workflows using legacy context
    - workflow_card_only_percentage: % workflows using card_ids
    - workflow_execution_duration_ms: Workflow execution duration
    - workflow_partial_result_total: Workflows with partial results
    - workflow_retrieve_failure_total: Card retrieval failures

    **Onboarding Metrics:**
    - onboarding_cards_created_total: Cards created by tenant and card type
    - onboarding_batch_duration_ms: Batch creation duration histogram
    - onboarding_sessions_total: Sessions created by tenant
    - onboarding_sessions_completed_total: Sessions completed by tenant and status
    - onboarding_errors_total: Errors by tenant and error type

    Returns:
        Prometheus metrics in text format
    """
    metrics_data = get_metrics()
    return Response(
        content=metrics_data,
        media_type=get_metrics_content_type(),
    )

