"""Data Transfer Objects for application layer."""

from .content_request import ContentGenerationRequest, ContentGenerationResponse
from .workflow_config import WorkflowConfigRequest, WorkflowConfigResponse
from .generation_result import GenerationResult, TaskResult

__all__ = [
    "ContentGenerationRequest",
    "ContentGenerationResponse",
    "WorkflowConfigRequest",
    "WorkflowConfigResponse",
    "GenerationResult",
    "TaskResult",
]
