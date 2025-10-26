"""Manage workflows use case."""

import logging
from typing import List, Optional
from uuid import UUID

from ...domain.entities.workflow import Workflow, WorkflowType
from ...domain.repositories.workflow_repository import WorkflowRepository
from ..dto.workflow_config import WorkflowConfigRequest, WorkflowConfigResponse

logger = logging.getLogger(__name__)


class ManageWorkflowsUseCase:
    """
    Use case for managing workflows.

    This use case handles workflow creation, updating, deletion,
    and listing operations.
    """

    def __init__(self, workflow_repository: WorkflowRepository):
        self.workflow_repository = workflow_repository

    async def create_workflow(
        self, request: WorkflowConfigRequest
    ) -> WorkflowConfigResponse:
        """Create a new workflow."""
        try:
            workflow = Workflow(
                name=request.name,
                description=request.description,
                workflow_type=WorkflowType(request.workflow_type),
                client_profile=request.client_profile,
                target_audience=request.target_audience,
                context=request.context,
            )

            saved_workflow = await self.workflow_repository.save(workflow)

            return WorkflowConfigResponse(
                workflow_id=saved_workflow.id,
                name=saved_workflow.name,
                workflow_type=saved_workflow.workflow_type.value,
                description=saved_workflow.description,
                status=saved_workflow.status.value,
                tasks_count=len(saved_workflow.tasks),
                success=True,
            )

        except Exception as e:
            logger.error(f"Failed to create workflow: {str(e)}")
            return WorkflowConfigResponse(
                workflow_id=UUID("00000000-0000-0000-0000-000000000000"),
                name=request.name,
                workflow_type=request.workflow_type,
                description=request.description,
                status="failed",
                tasks_count=0,
                success=False,
                error_message=str(e),
            )

    async def get_workflow(self, workflow_id: UUID) -> Optional[Workflow]:
        """Get a workflow by ID."""
        return await self.workflow_repository.get_by_id(workflow_id)

    async def list_workflows(self, limit: int = 10, offset: int = 0) -> List[Workflow]:
        """List workflows with pagination."""
        all_workflows = await self.workflow_repository.get_all()
        return all_workflows[offset : offset + limit]

    async def delete_workflow(self, workflow_id: UUID) -> bool:
        """Delete a workflow."""
        return await self.workflow_repository.delete(workflow_id)
