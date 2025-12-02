"""
Cards application module.

Exports card builders and pipeline for the onboarding flow.
"""

from .builders import (
    build_product_card,
    build_target_cards,
    build_brand_voice_card,
    build_competitor_cards,
    build_topic_cards,
    build_campaigns_card,
    build_performance_card,
)

from .pipeline import (
    run_onboarding_pipeline,
    convert_snapshot_to_raw_input,
    run_pipeline_from_snapshot,
)

__all__ = [
    # Builders
    "build_product_card",
    "build_target_cards",
    "build_brand_voice_card",
    "build_competitor_cards",
    "build_topic_cards",
    "build_campaigns_card",
    "build_performance_card",
    # Pipeline
    "run_onboarding_pipeline",
    "convert_snapshot_to_raw_input",
    "run_pipeline_from_snapshot",
]

