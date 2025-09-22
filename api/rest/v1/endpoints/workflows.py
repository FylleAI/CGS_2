"""Workflow management endpoints."""

import logging
from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from core.infrastructure.workflows import execute_dynamic_workflow, list_available_workflows

logger = logging.getLogger(__name__)

router = APIRouter()


class WorkflowListItem(BaseModel):
    """Workflow list item model."""
    id: str
    name: str
    workflow_type: str
    status: str
    created_at: str
    client_profile: Optional[str] = None


class WorkflowDetail(BaseModel):
    """Detailed workflow model."""
    id: str
    name: str
    description: str
    workflow_type: str
    status: str
    tasks: List[dict] = []
    created_at: str
    client_profile: Optional[str] = None


class WorkflowExecutionRequest(BaseModel):
    """Workflow execution request model."""
    workflow_id: str
    parameters: Dict[str, Any] = {}


class WorkflowExecutionResponse(BaseModel):
    """Workflow execution response model."""
    workflow_id: str
    status: str
    outputs: Dict[str, Any] = {}
    execution_time: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None


@router.get("/", response_model=List[WorkflowListItem])
async def list_workflows(
    limit: int = 10,
    offset: int = 0,
    workflow_type: Optional[str] = None,
    status: Optional[str] = None
):
    """List available workflows."""
    try:
        available_workflows = list_available_workflows()
        workflow_list = []

        for workflow_id, workflow_handler_name in available_workflows.items():
            workflow_list.append(WorkflowListItem(
                id=workflow_id,
                name=workflow_id.replace('_', ' ').title(),
                workflow_type=workflow_id,
                status="available",
                created_at="2025-01-01T00:00:00Z",
                client_profile=None
            ))

        return workflow_list[:limit]
    except Exception as e:
        logger.error(f"Error listing workflows: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{workflow_id}", response_model=WorkflowDetail)
async def get_workflow(workflow_id: UUID):
    """Get workflow details."""
    # TODO: Implement workflow retrieval
    raise HTTPException(status_code=404, detail="Workflow not found")


@router.post("/", response_model=WorkflowDetail)
async def create_workflow(workflow_data: dict):
    """Create a new workflow."""
    # TODO: Implement workflow creation
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.put("/{workflow_id}", response_model=WorkflowDetail)
async def update_workflow(workflow_id: UUID, workflow_data: dict):
    """Update an existing workflow."""
    # TODO: Implement workflow update
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.delete("/{workflow_id}")
async def delete_workflow(workflow_id: UUID):
    """Delete a workflow."""
    # TODO: Implement workflow deletion
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.post("/execute", response_model=WorkflowExecutionResponse)
async def execute_workflow(request: WorkflowExecutionRequest):
    """Execute a workflow with given parameters."""
    try:
        logger.info(f"🚀 Executing workflow: {request.workflow_id}")
        logger.debug(f"📊 Parameters: {request.parameters}")

        # Check if workflow exists
        available_workflows = list_available_workflows()
        if request.workflow_id not in available_workflows:
            raise HTTPException(
                status_code=404,
                detail=f"Workflow '{request.workflow_id}' not found. Available: {list(available_workflows.keys())}"
            )

        # Execute the workflow
        import time
        start_time = time.time()

        result = await execute_dynamic_workflow(request.workflow_id, request.parameters)

        execution_time = time.time() - start_time

        logger.info(f"✅ Workflow execution completed in {execution_time:.3f}s")

        return WorkflowExecutionResponse(
            workflow_id=request.workflow_id,
            status="completed",
            outputs=result,
            execution_time=execution_time,
            success=True
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Workflow execution failed: {str(e)}")
        return WorkflowExecutionResponse(
            workflow_id=request.workflow_id,
            status="failed",
            outputs={},
            success=False,
            error_message=str(e)
        )
