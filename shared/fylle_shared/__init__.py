"""
Fylle Shared Package

Shared enums, models and utilities for Fylle microservices.
Version: 0.1.0
"""

from fylle_shared.enums import CardType, WorkflowType
from fylle_shared.mappings import SNAPSHOT_TO_CARD_MAPPING
from fylle_shared.models.card import ContextCard, CardUsageEvent
from fylle_shared.models.workflow import WorkflowRequest, WorkflowResult
from fylle_shared.models.common import Pagination, ErrorResponse, IdempotencyKey
from fylle_shared.utils.hashing import generate_content_hash, generate_idempotency_key
from fylle_shared.utils.tracing import get_trace_id, TRACE_HEADER
from fylle_shared.utils.headers import (
    TENANT_HEADER,
    TRACE_HEADER as TRACE_HEADER_NAME,
    SESSION_HEADER,
    IDEMPOTENCY_HEADER,
    propagate_headers,
)

__version__ = "0.1.0"

__all__ = [
    # Enums
    "CardType",
    "WorkflowType",
    # Mappings
    "SNAPSHOT_TO_CARD_MAPPING",
    # Models - Card
    "ContextCard",
    "CardUsageEvent",
    # Models - Workflow
    "WorkflowRequest",
    "WorkflowResult",
    # Models - Common
    "Pagination",
    "ErrorResponse",
    "IdempotencyKey",
    # Utils - Hashing
    "generate_content_hash",
    "generate_idempotency_key",
    # Utils - Tracing
    "get_trace_id",
    "TRACE_HEADER",
    # Utils - Headers
    "TENANT_HEADER",
    "TRACE_HEADER_NAME",
    "SESSION_HEADER",
    "IDEMPOTENCY_HEADER",
    "propagate_headers",
]

