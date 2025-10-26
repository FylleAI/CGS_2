"""
Fylle Shared Workflow Models

Domain models for workflow requests and results.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from fylle_shared.enums import WorkflowType


class WorkflowRequest(BaseModel):
    """
    Workflow Request - Request to execute a workflow.

    v1: Uses card_ids to reference context cards.
    Legacy 'context' dict is deprecated and will be removed in v2.0.
    """
    workflow_type: WorkflowType
    card_ids: Optional[List[UUID]] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)

    # DEPRECATED: Will be removed in v2.0 (6 months notice)
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        deprecated=True,
        description="DEPRECATED: Use card_ids instead. Will be removed in v2.0.",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "workflow_type": "premium_newsletter",
                "card_ids": [
                    "123e4567-e89b-12d3-a456-426614174000",
                    "456e7890-e89b-12d3-a456-426614174001",
                    "789e0123-e89b-12d3-a456-426614174002"
                ],
                "parameters": {
                    "topic": "AI trends in 2025",
                    "tone": "professional",
                    "length": "medium"
                }
            }
        }


class WorkflowResult(BaseModel):
    """
    Workflow Result - Result of workflow execution.
    
    Contains output, status, and metrics.
    """
    workflow_id: UUID
    status: str  # completed | failed | running
    output: Dict[str, Any]
    metrics: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "workflow_id": "abc12345-e89b-12d3-a456-426614174003",
                "status": "completed",
                "output": {
                    "content": "Generated newsletter content...",
                    "title": "AI Trends in 2025",
                    "metadata": {
                        "word_count": 850,
                        "reading_time_minutes": 4
                    }
                },
                "metrics": {
                    "execution_time_ms": 2500,
                    "cards_used": 3,
                    "llm_calls": 2,
                    "tokens_used": 1200
                }
            }
        }

