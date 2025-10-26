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

from core.infrastructure.tools.context_card_tool import ContextCardTool
from core.infrastructure.workflows.registry import WorkflowRegistry
from core.infrastructure.metrics.prometheus import WorkflowMetrics
from fylle_cards_client import CardsClient

logger = logging.getLogger(__name__)

router = APIRouter()

# Global instances (initialized on startup)
_workflow_registry: Optional[WorkflowRegistry] = None
_cards_api_url: Optional[str] = None


def init_workflow_v1(workflow_registry: WorkflowRegistry, cards_api_url: str):
    """Initialize workflow v1 dependencies."""
    global _workflow_registry, _cards_api_url
    _workflow_registry = workflow_registry
    _cards_api_url = cards_api_url
    logger.info(f"✅ Workflow v1 initialized with registry and Cards API URL: {cards_api_url}")


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

        # Prepare context for workflow execution
        workflow_context = dict(request.parameters) if request.parameters else {}
        workflow_context["workflow_id"] = str(workflow_id)
        workflow_context["tenant_id"] = x_tenant_id
        workflow_context["trace_id"] = x_trace_id
        workflow_context["session_id"] = x_session_id

        cache_hit_rate = 0.0
        cards_used = 0
        partial_result = False

        # Path 1: card_ids (preferred)
        if request.card_ids:
            logger.info(
                f"📇 Using card-based context (preferred path)",
                extra={
                    "workflow_id": str(workflow_id),
                    "card_count": len(request.card_ids),
                },
            )

            # Initialize Cards client for this request
            if not _cards_api_url:
                raise HTTPException(
                    status_code=500,
                    detail="Cards API URL not initialized",
                )

            # Create CardsClient with tenant_id for this request
            cards_client = CardsClient(
                base_url=_cards_api_url,
                tenant_id=x_tenant_id,
                trace_id=x_trace_id,
                session_id=x_session_id,
            )

            context_tool = ContextCardTool(
                cards_client=cards_client,
            )

            try:
                # Retrieve cards and format context
                card_context = await context_tool.retrieve_cards(
                    tenant_id=x_tenant_id,
                    card_ids=request.card_ids,
                    workflow_id=workflow_id,
                    workflow_type=request.workflow_type.value,
                    trace_id=x_trace_id,
                )

                # Merge card context into workflow context
                workflow_context.update(card_context)

                # Get metrics
                cache_hit_rate = context_tool.get_cache_hit_rate()
                cards_used = len(request.card_ids)

                # Check for partial results
                retrieved_count = sum(len(v) for v in card_context.values() if isinstance(v, list))
                if retrieved_count < len(request.card_ids):
                    partial_result = True
                    missing_count = len(request.card_ids) - retrieved_count

                    logger.warning(
                        f"⚠️ Partial card retrieval",
                        extra={
                            "workflow_id": str(workflow_id),
                            "requested": len(request.card_ids),
                            "retrieved": retrieved_count,
                            "missing": missing_count,
                            "trace_id": x_trace_id,
                        },
                    )

                    # Add header to indicate partial result
                    response.headers["X-Partial-Result"] = (
                        f"Retrieved {retrieved_count}/{len(request.card_ids)} cards"
                    )

                logger.info(
                    f"✅ Cards retrieved successfully",
                    extra={
                        "workflow_id": str(workflow_id),
                        "cards_retrieved": retrieved_count,
                        "cache_hit_rate": cache_hit_rate,
                    },
                )

            except Exception as e:
                logger.error(
                    f"❌ Card retrieval failed completely",
                    extra={
                        "workflow_id": str(workflow_id),
                        "error": str(e),
                        "trace_id": x_trace_id,
                        "request_id": request_id,
                    },
                    exc_info=True,
                )

                # Record failure metric
                from core.infrastructure.metrics.prometheus import WorkflowMetrics as PrometheusMetrics
                PrometheusMetrics.record_retrieve_failure(
                    workflow_type=request.workflow_type.value,
                    error_type=type(e).__name__,
                )

                # Safety net: return 502 with trace_id
                raise HTTPException(
                    status_code=502,
                    detail={
                        "error": "Card retrieval failed",
                        "message": str(e),
                        "trace_id": x_trace_id,
                        "request_id": request_id,
                    },
                )

        # Path 2: legacy context (deprecated)
        else:
            logger.info(
                f"📦 Using legacy context (deprecated path)",
                extra={
                    "workflow_id": str(workflow_id),
                },
            )
            workflow_context.update(getattr(request, "context", {}))

        # Execute workflow
        if not _workflow_registry:
            raise HTTPException(
                status_code=500,
                detail="Workflow registry not initialized",
            )

        try:
            handler = _workflow_registry.get_handler(request.workflow_type.value)
            result = await handler.execute(workflow_context)

            execution_time_ms = int((time.time() - start_time) * 1000)

            # Extract output from result
            output = result if isinstance(result, dict) else {"result": str(result)}

            # Build metrics
            metrics = WorkflowMetrics(
                execution_time_ms=execution_time_ms,
                cards_used=cards_used,
                cache_hit_rate=cache_hit_rate if cards_used > 0 else None,
                tokens_used=output.get("tokens_used"),  # If available from workflow
            )

            # Record Prometheus metrics
            from core.infrastructure.metrics.prometheus import WorkflowMetrics as PrometheusMetrics
            PrometheusMetrics.record_workflow_execution(
                workflow_type=request.workflow_type.value,
                duration_ms=execution_time_ms,
                status="completed",
                using_card_ids=bool(request.card_ids),
                partial_result=partial_result,
            )

            logger.info(
                f"✅ Workflow execution completed",
                extra={
                    "workflow_id": str(workflow_id),
                    "execution_time_ms": execution_time_ms,
                    "status": "completed",
                    "request_id": request_id,
                    "cache_hit_rate": cache_hit_rate,
                    "partial_result": partial_result,
                },
            )

            return WorkflowExecuteResponse(
                workflow_id=workflow_id,
                status="completed",
                output=output,
                metrics=metrics,
            )

        except ValueError as e:
            # Workflow type not found
            logger.error(
                f"❌ Workflow type not found: {request.workflow_type.value}",
                extra={
                    "workflow_id": str(workflow_id),
                    "error": str(e),
                    "request_id": request_id,
                },
            )
            raise HTTPException(
                status_code=404,
                detail=f"Workflow type not found: {request.workflow_type.value}",
            )

        except Exception as e:
            logger.error(
                f"❌ Workflow execution failed",
                extra={
                    "workflow_id": str(workflow_id),
                    "error": str(e),
                    "trace_id": x_trace_id,
                    "request_id": request_id,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=500,
                detail=f"Workflow execution failed: {str(e)}",
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

