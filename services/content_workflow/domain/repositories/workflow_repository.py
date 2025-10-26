"""Workflow repository interface."""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from ..entities.workflow import Workflow, WorkflowType, WorkflowStatus


class WorkflowRepository(ABC):
    """
    Abstract repository for workflow persistence.

    This interface defines the contract for workflow data access,
    allowing different implementations (file-based, database, etc.)
    """

    @abstractmethod
    async def save(self, workflow: Workflow) -> Workflow:
        """
        Save a workflow.

        Args:
            workflow: The workflow to save

        Returns:
            The saved workflow with any generated fields populated
        """
        pass

    @abstractmethod
    async def get_by_id(self, workflow_id: UUID) -> Optional[Workflow]:
        """
        Get a workflow by ID.

        Args:
            workflow_id: The workflow ID

        Returns:
            The workflow if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Workflow]:
        """
        Get a workflow by name.

        Args:
            name: The workflow name

        Returns:
            The workflow if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_type(self, workflow_type: WorkflowType) -> List[Workflow]:
        """
        Get all workflows of a specific type.

        Args:
            workflow_type: The workflow type

        Returns:
            List of workflows of the specified type
        """
        pass

    @abstractmethod
    async def get_by_status(self, status: WorkflowStatus) -> List[Workflow]:
        """
        Get all workflows with a specific status.

        Args:
            status: The workflow status

        Returns:
            List of workflows with the specified status
        """
        pass

    @abstractmethod
    async def get_all(self) -> List[Workflow]:
        """
        Get all workflows.

        Returns:
            List of all workflows
        """
        pass

    @abstractmethod
    async def get_templates(self) -> List[Workflow]:
        """
        Get workflow templates (workflows that can be used as starting points).

        Returns:
            List of workflow templates
        """
        pass

    @abstractmethod
    async def update(self, workflow: Workflow) -> Workflow:
        """
        Update an existing workflow.

        Args:
            workflow: The workflow to update

        Returns:
            The updated workflow

        Raises:
            ValueError: If workflow doesn't exist
        """
        pass

    @abstractmethod
    async def delete(self, workflow_id: UUID) -> bool:
        """
        Delete a workflow.

        Args:
            workflow_id: The workflow ID to delete

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    async def exists(self, workflow_id: UUID) -> bool:
        """
        Check if a workflow exists.

        Args:
            workflow_id: The workflow ID to check

        Returns:
            True if exists, False otherwise
        """
        pass

    @abstractmethod
    async def get_by_client_profile(self, profile_name: str) -> List[Workflow]:
        """
        Get workflows configured for a specific client profile.

        Args:
            profile_name: The client profile name

        Returns:
            List of workflows for the profile
        """
        pass

    @abstractmethod
    async def get_running_workflows(self) -> List[Workflow]:
        """
        Get all currently running workflows.

        Returns:
            List of running workflows
        """
        pass

    @abstractmethod
    async def get_recent_workflows(self, limit: int = 10) -> List[Workflow]:
        """
        Get recently created or executed workflows.

        Args:
            limit: Maximum number of workflows to return

        Returns:
            List of recent workflows
        """
        pass

    @abstractmethod
    async def search(self, query: str) -> List[Workflow]:
        """
        Search workflows by name, description, or type.

        Args:
            query: The search query

        Returns:
            List of matching workflows
        """
        pass

    @abstractmethod
    async def clone_workflow(self, workflow_id: UUID, new_name: str) -> Workflow:
        """
        Clone an existing workflow with a new name.

        Args:
            workflow_id: The workflow ID to clone
            new_name: Name for the cloned workflow

        Returns:
            The cloned workflow

        Raises:
            ValueError: If source workflow doesn't exist
        """
        pass
