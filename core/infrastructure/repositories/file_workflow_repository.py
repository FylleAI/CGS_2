"""File-based workflow repository implementation."""

import json
import logging
from typing import List, Optional
from uuid import UUID, uuid4
from pathlib import Path

from ...domain.entities.workflow import Workflow, WorkflowType, WorkflowStatus
from ...domain.repositories.workflow_repository import WorkflowRepository

logger = logging.getLogger(__name__)


class FileWorkflowRepository(WorkflowRepository):
    """
    File-based implementation of WorkflowRepository.

    This implementation stores workflows as JSON files in the filesystem.
    """

    def __init__(self, base_path: str = "data/workflows"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (self.base_path / "templates").mkdir(exist_ok=True)
        (self.base_path / "instances").mkdir(exist_ok=True)

    def _get_workflow_file_path(
        self, workflow_id: UUID, is_template: bool = False
    ) -> Path:
        """Get file path for workflow."""
        subdir = "templates" if is_template else "instances"
        return self.base_path / subdir / f"{workflow_id}.json"

    async def save(self, workflow: Workflow) -> Workflow:
        """Save a workflow."""
        try:
            is_template = workflow.status == WorkflowStatus.DRAFT
            file_path = self._get_workflow_file_path(workflow.id, is_template)

            # Convert workflow to dict
            data = workflow.to_dict()

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved workflow {workflow.id} to {file_path}")
            return workflow

        except Exception as e:
            logger.error(f"Failed to save workflow {workflow.id}: {str(e)}")
            raise

    async def get_by_id(self, workflow_id: UUID) -> Optional[Workflow]:
        """Get a workflow by ID."""
        # Check both templates and instances
        for is_template in [False, True]:
            file_path = self._get_workflow_file_path(workflow_id, is_template)
            if file_path.exists():
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    return Workflow.from_dict(data)
                except Exception as e:
                    logger.error(f"Failed to load workflow {workflow_id}: {str(e)}")

        return None

    async def get_by_name(self, name: str) -> Optional[Workflow]:
        """Get a workflow by name."""
        all_workflows = await self.get_all()
        for workflow in all_workflows:
            if workflow.name == name:
                return workflow
        return None

    async def get_by_type(self, workflow_type: WorkflowType) -> List[Workflow]:
        """Get all workflows of a specific type."""
        all_workflows = await self.get_all()
        return [w for w in all_workflows if w.workflow_type == workflow_type]

    async def get_by_status(self, status: WorkflowStatus) -> List[Workflow]:
        """Get all workflows with a specific status."""
        all_workflows = await self.get_all()
        return [w for w in all_workflows if w.status == status]

    async def get_all(self) -> List[Workflow]:
        """Get all workflows."""
        workflows = []

        # Load from both templates and instances
        for subdir in ["templates", "instances"]:
            workflow_dir = self.base_path / subdir
            if workflow_dir.exists():
                for workflow_file in workflow_dir.glob("*.json"):
                    try:
                        with open(workflow_file, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        workflow = Workflow.from_dict(data)
                        workflows.append(workflow)
                    except Exception as e:
                        logger.warning(
                            f"Failed to load workflow from {workflow_file}: {str(e)}"
                        )

        return workflows

    async def get_templates(self) -> List[Workflow]:
        """Get workflow templates."""
        templates = []
        templates_dir = self.base_path / "templates"

        if templates_dir.exists():
            for template_file in templates_dir.glob("*.json"):
                try:
                    with open(template_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    workflow = Workflow.from_dict(data)
                    templates.append(workflow)
                except Exception as e:
                    logger.warning(
                        f"Failed to load template from {template_file}: {str(e)}"
                    )

        return templates

    async def update(self, workflow: Workflow) -> Workflow:
        """Update an existing workflow."""
        if not await self.exists(workflow.id):
            raise ValueError(f"Workflow {workflow.id} does not exist")

        return await self.save(workflow)

    async def delete(self, workflow_id: UUID) -> bool:
        """Delete a workflow."""
        try:
            deleted = False

            # Check both templates and instances
            for is_template in [False, True]:
                file_path = self._get_workflow_file_path(workflow_id, is_template)
                if file_path.exists():
                    file_path.unlink()
                    deleted = True
                    logger.info(f"Deleted workflow {workflow_id} from {file_path}")

            return deleted

        except Exception as e:
            logger.error(f"Failed to delete workflow {workflow_id}: {str(e)}")
            return False

    async def exists(self, workflow_id: UUID) -> bool:
        """Check if a workflow exists."""
        for is_template in [False, True]:
            file_path = self._get_workflow_file_path(workflow_id, is_template)
            if file_path.exists():
                return True
        return False

    async def get_by_client_profile(self, profile_name: str) -> List[Workflow]:
        """Get workflows configured for a specific client profile."""
        all_workflows = await self.get_all()
        return [w for w in all_workflows if w.client_profile == profile_name]

    async def get_running_workflows(self) -> List[Workflow]:
        """Get all currently running workflows."""
        return await self.get_by_status(WorkflowStatus.RUNNING)

    async def get_recent_workflows(self, limit: int = 10) -> List[Workflow]:
        """Get recently created or executed workflows."""
        all_workflows = await self.get_all()
        sorted_workflows = sorted(
            all_workflows, key=lambda x: x.created_at, reverse=True
        )
        return sorted_workflows[:limit]

    async def search(self, query: str) -> List[Workflow]:
        """Search workflows by name, description, or type."""
        all_workflows = await self.get_all()
        query_lower = query.lower()

        results = []
        for workflow in all_workflows:
            if (
                query_lower in workflow.name.lower()
                or query_lower in workflow.description.lower()
                or query_lower in workflow.workflow_type.value.lower()
            ):
                results.append(workflow)

        return results

    async def clone_workflow(self, workflow_id: UUID, new_name: str) -> Workflow:
        """Clone an existing workflow with a new name."""
        original = await self.get_by_id(workflow_id)
        if not original:
            raise ValueError(f"Workflow {workflow_id} not found")

        # Create new workflow with new ID and name
        cloned = Workflow(
            id=uuid4(),
            name=new_name,
            description=f"Cloned from {original.name}",
            workflow_type=original.workflow_type,
            tasks=original.tasks.copy(),
            agent_ids=original.agent_ids.copy(),
            client_profile=original.client_profile,
            target_audience=original.target_audience,
            context=original.context.copy(),
            metadata=original.metadata.copy(),
        )

        return await self.save(cloned)
