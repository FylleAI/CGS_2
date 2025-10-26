"""Workflow entity - represents a content generation workflow."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
from enum import Enum
from datetime import datetime

from .task import Task, TaskStatus


class WorkflowStatus(Enum):
    """Workflow execution status."""

    DRAFT = "draft"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowType(Enum):
    """Types of workflows."""

    BASIC = "basic"
    SIEBERT_NEWSLETTER = "siebert_newsletter"
    SIEBERT_ARTICLE = "siebert_article"
    ENHANCED_ARTICLE = "enhanced_article"
    ENHANCED_ARTICLE_WITH_IMAGE = "enhanced_article_with_image"
    SUMMARY_RAG = "summary_rag"
    CUSTOM = "custom"


@dataclass
class WorkflowResult:
    """Result of a workflow execution."""

    final_output: str = ""
    task_outputs: Dict[UUID, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time: Optional[float] = None
    error_message: Optional[str] = None

    def is_successful(self) -> bool:
        """Check if workflow execution was successful."""
        return self.error_message is None


@dataclass
class Workflow:
    """
    Workflow entity representing a content generation workflow.

    A workflow orchestrates multiple tasks and agents to generate content
    following a specific process and sequence.
    """

    id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""
    workflow_type: WorkflowType = WorkflowType.BASIC
    tasks: List[Task] = field(default_factory=list)
    agent_ids: List[UUID] = field(default_factory=list)
    client_profile: Optional[str] = None
    target_audience: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    status: WorkflowStatus = WorkflowStatus.DRAFT
    result: Optional[WorkflowResult] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate workflow after initialization."""
        if not self.name:
            self.name = f"{self.workflow_type.value}_workflow"

    def add_task(self, task: Task) -> None:
        """Add a task to the workflow."""
        if task.id not in [t.id for t in self.tasks]:
            self.tasks.append(task)

            # Add agent to workflow if not already present
            if task.agent_id and task.agent_id not in self.agent_ids:
                self.agent_ids.append(task.agent_id)

    def remove_task(self, task_id: UUID) -> None:
        """Remove a task from the workflow."""
        self.tasks = [t for t in self.tasks if t.id != task_id]

        # Remove dependencies on this task
        for task in self.tasks:
            task.remove_dependency(task_id)

    def get_task_by_id(self, task_id: UUID) -> Optional[Task]:
        """Get a task by its ID."""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def get_ready_tasks(self) -> List[Task]:
        """Get tasks that are ready to be executed."""
        completed_task_ids = [
            t.id for t in self.tasks if t.status == TaskStatus.COMPLETED
        ]

        return [task for task in self.tasks if task.can_start(completed_task_ids)]

    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Get tasks by their status."""
        return [task for task in self.tasks if task.status == status]

    def can_start(self) -> bool:
        """Check if workflow can start execution."""
        if self.status != WorkflowStatus.READY:
            return False

        if not self.tasks:
            return False

        # Check if there's at least one task that can start
        return len(self.get_ready_tasks()) > 0

    def start(self) -> None:
        """Start workflow execution."""
        if not self.can_start():
            raise ValueError(f"Cannot start workflow in status: {self.status}")

        self.status = WorkflowStatus.RUNNING
        self.started_at = datetime.utcnow()

    def complete(self, result: WorkflowResult) -> None:
        """Complete workflow execution."""
        if self.status != WorkflowStatus.RUNNING:
            raise ValueError(f"Cannot complete workflow in status: {self.status}")

        self.status = WorkflowStatus.COMPLETED
        self.result = result
        self.completed_at = datetime.utcnow()

    def fail(self, error_message: str) -> None:
        """Mark workflow as failed."""
        if self.status not in [WorkflowStatus.RUNNING, WorkflowStatus.READY]:
            raise ValueError(f"Cannot fail workflow in status: {self.status}")

        self.status = WorkflowStatus.FAILED
        self.result = WorkflowResult(error_message=error_message)
        self.completed_at = datetime.utcnow()

    def cancel(self) -> None:
        """Cancel workflow execution."""
        if self.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED]:
            raise ValueError(f"Cannot cancel workflow in status: {self.status}")

        self.status = WorkflowStatus.CANCELLED
        self.completed_at = datetime.utcnow()

        # Cancel all pending and running tasks
        for task in self.tasks:
            if task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
                task.cancel()

    def is_completed(self) -> bool:
        """Check if all tasks in workflow are completed."""
        if not self.tasks:
            return False

        return all(task.status == TaskStatus.COMPLETED for task in self.tasks)

    def get_progress(self) -> float:
        """Get workflow completion progress (0.0 to 1.0)."""
        if not self.tasks:
            return 0.0

        completed_tasks = len(self.get_tasks_by_status(TaskStatus.COMPLETED))
        return completed_tasks / len(self.tasks)

    def get_execution_time(self) -> Optional[float]:
        """Get workflow execution time in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    def validate(self) -> List[str]:
        """Validate workflow configuration and return list of errors."""
        errors = []

        if not self.tasks:
            errors.append("Workflow must have at least one task")

        # Check for circular dependencies
        if self._has_circular_dependencies():
            errors.append("Workflow has circular task dependencies")

        # Check if all agent IDs are valid
        task_agent_ids = {t.agent_id for t in self.tasks if t.agent_id}
        missing_agents = task_agent_ids - set(self.agent_ids)
        if missing_agents:
            errors.append(f"Missing agents: {missing_agents}")

        return errors

    def _has_circular_dependencies(self) -> bool:
        """Check for circular dependencies in tasks."""
        # Simple cycle detection using DFS
        visited = set()
        rec_stack = set()

        def has_cycle(task_id: UUID) -> bool:
            visited.add(task_id)
            rec_stack.add(task_id)

            task = self.get_task_by_id(task_id)
            if task:
                for dep_id in task.dependencies:
                    if dep_id not in visited:
                        if has_cycle(dep_id):
                            return True
                    elif dep_id in rec_stack:
                        return True

            rec_stack.remove(task_id)
            return False

        for task in self.tasks:
            if task.id not in visited:
                if has_cycle(task.id):
                    return True

        return False

    def mark_ready(self) -> None:
        """Mark workflow as ready for execution after validation."""
        errors = self.validate()
        if errors:
            raise ValueError(f"Workflow validation failed: {errors}")

        self.status = WorkflowStatus.READY

    def to_dict(self) -> Dict[str, Any]:
        """Convert workflow to dictionary representation."""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "workflow_type": self.workflow_type.value,
            "tasks": [task.to_dict() for task in self.tasks],
            "agent_ids": [str(agent_id) for agent_id in self.agent_ids],
            "client_profile": self.client_profile,
            "target_audience": self.target_audience,
            "context": self.context,
            "status": self.status.value,
            "result": (
                {
                    "final_output": self.result.final_output,
                    "task_outputs": {
                        str(k): v for k, v in self.result.task_outputs.items()
                    },
                    "metadata": self.result.metadata,
                    "execution_time": self.result.execution_time,
                    "error_message": self.result.error_message,
                }
                if self.result
                else None
            ),
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Workflow":
        """Create workflow from dictionary representation."""
        from datetime import datetime
        from uuid import UUID

        workflow = cls(
            id=UUID(data["id"]) if "id" in data else uuid4(),
            name=data.get("name", ""),
            description=data.get("description", ""),
            workflow_type=WorkflowType(data.get("workflow_type", "basic")),
            agent_ids=[UUID(agent_id) for agent_id in data.get("agent_ids", [])],
            client_profile=data.get("client_profile"),
            target_audience=data.get("target_audience", ""),
            context=data.get("context", {}),
            status=WorkflowStatus(data.get("status", "draft")),
            created_at=(
                datetime.fromisoformat(data["created_at"])
                if "created_at" in data
                else datetime.utcnow()
            ),
            started_at=(
                datetime.fromisoformat(data["started_at"])
                if data.get("started_at")
                else None
            ),
            completed_at=(
                datetime.fromisoformat(data["completed_at"])
                if data.get("completed_at")
                else None
            ),
            metadata=data.get("metadata", {}),
        )

        # Add tasks
        for task_data in data.get("tasks", []):
            from .task import Task

            task = Task.from_dict(task_data)
            workflow.add_task(task)

        # Set result if present
        if data.get("result"):
            result_data = data["result"]
            workflow.result = WorkflowResult(
                final_output=result_data.get("final_output", ""),
                task_outputs={
                    UUID(k): v for k, v in result_data.get("task_outputs", {}).items()
                },
                metadata=result_data.get("metadata", {}),
                execution_time=result_data.get("execution_time"),
                error_message=result_data.get("error_message"),
            )

        return workflow
