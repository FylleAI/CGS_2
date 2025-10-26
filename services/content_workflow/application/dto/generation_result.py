"""Generation result DTOs."""

from dataclasses import dataclass
from typing import Dict, Optional, Any
from uuid import UUID


@dataclass
class TaskResult:
    """Result of a single task execution."""

    task_id: UUID
    name: str
    output: str
    success: bool
    execution_time_seconds: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self) -> None:
        """Initialize default values."""
        if self.metadata is None:
            self.metadata = {}


@dataclass
class GenerationResult:
    """Complete generation result."""

    workflow_id: UUID
    final_output: str
    task_results: list[TaskResult]
    total_execution_time_seconds: float
    success: bool
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self) -> None:
        """Initialize default values."""
        if self.metadata is None:
            self.metadata = {}

    def get_successful_tasks(self) -> list[TaskResult]:
        """Get list of successful task results."""
        return [task for task in self.task_results if task.success]

    def get_failed_tasks(self) -> list[TaskResult]:
        """Get list of failed task results."""
        return [task for task in self.task_results if not task.success]
