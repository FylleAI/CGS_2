"""
Data models for Fylle Workflow API.

Auto-generated from OpenAPI spec: contracts/workflow-api-v1.yaml
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class WorkflowType(str, Enum):
    """Workflow type enum (LOCKED - from fylle-shared)."""

    PREMIUM_NEWSLETTER = "premium_newsletter"
    ONBOARDING_CONTENT = "onboarding_content"


class WorkflowExecuteRequest(BaseModel):
    """Request to execute a workflow."""

    workflow_type: WorkflowType
    card_ids: Optional[List[UUID]] = Field(
        default=None,
        description="Card IDs for context (PREFERRED in v1.0)"
    )
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        deprecated=True,
        description="DEPRECATED: Legacy context dict. Use card_ids instead."
    )
    parameters: Dict[str, Any] = Field(default_factory=dict)


class WorkflowMetrics(BaseModel):
    """Workflow execution metrics."""

    execution_time_ms: Optional[int] = None
    cards_used: Optional[int] = None
    llm_calls: Optional[int] = None
    tokens_used: Optional[int] = None
    cache_hit_rate: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class WorkflowExecuteResponse(BaseModel):
    """Response from workflow execution."""

    workflow_id: UUID
    status: str  # running, completed, failed
    output: Dict[str, Any]
    metrics: Optional[WorkflowMetrics] = None


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str
    detail: Optional[str] = None
    request_id: Optional[str] = None

