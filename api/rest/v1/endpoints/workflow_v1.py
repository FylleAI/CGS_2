"""
Workflow API v1 - Card-based context execution.

Implements POST /api/v1/workflow/execute following OpenAPI contract.
Supports card_ids (preferred) and context (deprecated).
"""

import logging
import time
import uuid
from typing import Dict, Any, List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Header, Response
from pydantic import BaseModel, Field

from fylle_shared.enums import WorkflowType
from fylle_shared.models.workflow import WorkflowRequest

logger = logging.getLogger(__name__)

router = APIRouter()


# Response Models (matching OpenAPI contract)


class WorkflowMetrics(BaseModel):
    """Workflow execution metrics."""
    
    execution_time_ms: int
    cards_used: int
    cache_hit_rate: Optional[float] = None
    tokens_used: Optional[int] = None


class WorkflowExecuteResponse(BaseModel):
    """Workflow execution response."""
    
    workflow_id: UUID
    status: str  # running, completed, failed
    output: Dict[str, Any]
    metrics: Optional[WorkflowMetrics] = None


class ErrorResponse(BaseModel):
    """Error response."""
    
    error: str
    detail: str
    request_id: str


# Endpoint


@router.post("/execute", response_model=WorkflowExecuteResponse)
async def execute_workflow_v1(
    request: WorkflowRequest,
    response: Response,
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
    x_trace_id: Optional[str] = Header(None, alias="X-Trace-ID"),
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID"),
) -> WorkflowExecuteResponse:
    """
    Execute a workflow with card-based context.
    
    **Preferred**: Use `card_ids` to reference context cards.
    **Deprecated**: `context` dict is deprecated and will be removed in v2.0.
    
    Args:
        request: Workflow execution request
        x_tenant_id: Tenant ID (required)
        x_trace_id: Trace ID for distributed tracing (optional)
        x_session_id: Session ID for tracking (optional)
    
    Returns:
        Workflow execution response with status and output
    
    Raises:
        400: Bad request - missing required fields
        401: Unauthorized - missing or invalid X-Tenant-ID
        404: Workflow type not found
        500: Internal server error
    """
    workflow_id = uuid.uuid4()
    request_id = f"req-{uuid.uuid4().hex[:12]}"
    
    logger.info(
        f"🚀 Workflow execution request",
        extra={
            "workflow_id": str(workflow_id),
            "workflow_type": request.workflow_type.value,
            "tenant_id": x_tenant_id,
            "trace_id": x_trace_id,
            "session_id": x_session_id,
            "request_id": request_id,
            "has_card_ids": bool(request.card_ids),
            "has_context": bool(getattr(request, "context", None)),
        },
    )
    
    try:
        # Validate request
        if not request.card_ids and not getattr(request, "context", None):
            raise HTTPException(
                status_code=400,
                detail="Either card_ids or context (deprecated) must be provided",
            )
        
        # Check for deprecated context usage
        using_legacy_context = False
        if getattr(request, "context", None) and not request.card_ids:
            using_legacy_context = True
            logger.warning(
                f"⚠️ DEPRECATED: Workflow using legacy 'context' parameter",
                extra={
                    "workflow_id": str(workflow_id),
                    "tenant_id": x_tenant_id,
                    "request_id": request_id,
                },
            )
            
            # Add deprecation headers
            response.headers["X-API-Deprecation-Warning"] = (
                "context parameter is deprecated, use card_ids instead"
            )
            response.headers["X-API-Migration-Guide"] = (
                "https://docs.fylle.ai/migration/context-to-cards"
            )
        
        # Start execution
        start_time = time.time()
        
        # TODO: Implement actual workflow execution with ContextCardTool
        # For now, return a placeholder response
        
        execution_time_ms = int((time.time() - start_time) * 1000)
        
        # Placeholder metrics
        metrics = WorkflowMetrics(
            execution_time_ms=execution_time_ms,
            cards_used=len(request.card_ids) if request.card_ids else 0,
            cache_hit_rate=0.0,
            tokens_used=0,
        )
        
        logger.info(
            f"✅ Workflow execution completed",
            extra={
                "workflow_id": str(workflow_id),
                "execution_time_ms": execution_time_ms,
                "status": "completed",
                "request_id": request_id,
            },
        )
        
        return WorkflowExecuteResponse(
            workflow_id=workflow_id,
            status="completed",
            output={"message": "Workflow execution placeholder - implementation in progress"},
            metrics=metrics,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"❌ Workflow execution failed: {str(e)}",
            extra={
                "workflow_id": str(workflow_id),
                "error": str(e),
                "request_id": request_id,
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Workflow execution failed: {str(e)}",
        )


@router.get("/{workflow_id}", response_model=WorkflowExecuteResponse)
async def get_workflow_status_v1(
    workflow_id: UUID,
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
) -> WorkflowExecuteResponse:
    """
    Get workflow execution status.
    
    Args:
        workflow_id: Workflow ID
        x_tenant_id: Tenant ID (required)
    
    Returns:
        Workflow execution status
    
    Raises:
        404: Workflow not found
    """
    # TODO: Implement workflow status retrieval
    raise HTTPException(
        status_code=501,
        detail="Workflow status retrieval not implemented yet",
    )

