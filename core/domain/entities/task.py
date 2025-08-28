"""Task entity - represents a task in the content generation workflow."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
from enum import Enum
from datetime import datetime


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskType(Enum):
    """Task type categories."""
    RESEARCH = "research"
    WRITING = "writing"
    EDITING = "editing"
    ANALYSIS = "analysis"
    PLANNING = "planning"
    REVIEW = "review"


@dataclass
class TaskResult:
    """Result of a task execution."""
    output: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time: Optional[float] = None
    error_message: Optional[str] = None
    
    def is_successful(self) -> bool:
        """Check if task execution was successful."""
        return self.error_message is None


@dataclass
class Task:
    """
    Task entity representing a unit of work in the content generation workflow.
    
    A task is assigned to an agent and represents a specific piece of work
    that needs to be completed as part of a larger workflow.
    """
    
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""
    expected_output: str = ""
    task_type: TaskType = TaskType.RESEARCH
    agent_id: Optional[UUID] = None
    agent_name: Optional[str] = None  # Preferred explicit agent identifier from templates
    agent_role: Optional[Any] = None  # Will be AgentRole enum
    dependencies: List[UUID] = field(default_factory=list)
    tools_required: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[TaskResult] = None
    output: str = ""  # Direct output field
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Validate task after initialization."""
        if not self.name:
            self.name = f"task_{str(self.id)[:8]}"
    
    def can_start(self, completed_task_ids: List[UUID]) -> bool:
        """Check if task can start based on dependencies."""
        if self.status != TaskStatus.PENDING:
            return False
        
        # Check if all dependencies are completed
        for dep_id in self.dependencies:
            if dep_id not in completed_task_ids:
                return False
        
        return True
    
    def start(self) -> None:
        """Mark task as started."""
        if self.status != TaskStatus.PENDING:
            raise ValueError(f"Cannot start task in status: {self.status}")
        
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.utcnow()
    
    def complete(self, result: TaskResult) -> None:
        """Mark task as completed with result."""
        if self.status != TaskStatus.RUNNING:
            raise ValueError(f"Cannot complete task in status: {self.status}")
        
        self.status = TaskStatus.COMPLETED
        self.result = result
        self.completed_at = datetime.utcnow()
    
    def fail(self, error_message: str) -> None:
        """Mark task as failed with error message."""
        if self.status not in [TaskStatus.RUNNING, TaskStatus.PENDING]:
            raise ValueError(f"Cannot fail task in status: {self.status}")
        
        self.status = TaskStatus.FAILED
        self.result = TaskResult(error_message=error_message)
        self.completed_at = datetime.utcnow()
    
    def cancel(self) -> None:
        """Cancel the task."""
        if self.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            raise ValueError(f"Cannot cancel task in status: {self.status}")
        
        self.status = TaskStatus.CANCELLED
        self.completed_at = datetime.utcnow()
    
    def add_dependency(self, task_id: UUID) -> None:
        """Add a dependency to this task."""
        if task_id not in self.dependencies:
            self.dependencies.append(task_id)
    
    def remove_dependency(self, task_id: UUID) -> None:
        """Remove a dependency from this task."""
        if task_id in self.dependencies:
            self.dependencies.remove(task_id)
    
    def get_execution_time(self) -> Optional[float]:
        """Get task execution time in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary representation."""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "expected_output": self.expected_output,
            "agent_id": str(self.agent_id) if self.agent_id else None,
            "agent_name": self.agent_name,
            "dependencies": [str(dep) for dep in self.dependencies],
            "tools_required": self.tools_required,
            "context": self.context,
            "priority": self.priority.value,
            "status": self.status.value,
            "result": {
                "output": self.result.output,
                "metadata": self.result.metadata,
                "execution_time": self.result.execution_time,
                "error_message": self.result.error_message
            } if self.result else None,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Create task from dictionary representation."""
        task = cls(
            id=UUID(data["id"]) if "id" in data else uuid4(),
            name=data.get("name", ""),
            description=data.get("description", ""),
            expected_output=data.get("expected_output", ""),
            agent_id=UUID(data["agent_id"]) if data.get("agent_id") else None,
            agent_name=data.get("agent_name"),
            dependencies=[UUID(dep) for dep in data.get("dependencies", [])],
            tools_required=data.get("tools_required", []),
            context=data.get("context", {}),
            priority=TaskPriority(data.get("priority", "medium")),
            status=TaskStatus(data.get("status", "pending")),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.utcnow(),
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            metadata=data.get("metadata", {})
        )
        
        # Set result if present
        if data.get("result"):
            result_data = data["result"]
            task.result = TaskResult(
                output=result_data.get("output", ""),
                metadata=result_data.get("metadata", {}),
                execution_time=result_data.get("execution_time"),
                error_message=result_data.get("error_message")
            )
        
        return task
