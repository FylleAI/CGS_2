"""Workflow configuration DTOs."""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from uuid import UUID


@dataclass
class WorkflowConfigRequest:
    """Request DTO for workflow configuration."""

    name: str
    workflow_type: str
    description: str = ""
    client_profile: Optional[str] = None
    target_audience: str = ""
    tasks: List[Dict[str, Any]] = None
    context: Dict[str, Any] = None

    def __post_init__(self) -> None:
        """Initialize default values."""
        if self.tasks is None:
            self.tasks = []
        if self.context is None:
            self.context = {}


@dataclass
class WorkflowConfigResponse:
    """Response DTO for workflow configuration."""

    workflow_id: UUID
    name: str
    workflow_type: str
    description: str
    status: str
    tasks_count: int
    success: bool = True
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self) -> None:
        """Initialize default values."""
        if self.metadata is None:
            self.metadata = {}
