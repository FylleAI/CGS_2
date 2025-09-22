"""Content generation request and response DTOs."""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from uuid import UUID

from ...domain.entities.content import ContentType, ContentFormat
from ...domain.value_objects.generation_params import GenerationParams
from ...domain.value_objects.provider_config import ProviderConfig


@dataclass
class ContentGenerationRequest:
    """
    Request DTO for content generation.

    This DTO encapsulates all information needed to generate content,
    serving as the input to the content generation use case.
    """

    topic: str
    content_type: ContentType = ContentType.ARTICLE
    content_format: ContentFormat = ContentFormat.MARKDOWN
    client_profile: Optional[str] = None
    workflow_type: Optional[str] = None
    provider_config: Optional[ProviderConfig] = None
    generation_params: Optional[GenerationParams] = None
    custom_instructions: str = ""
    context: Dict[str, Any] = None

    def __post_init__(self) -> None:
        """Initialize default values."""
        if self.context is None:
            self.context = {}

        if self.generation_params is None:
            self.generation_params = GenerationParams(
                topic=self.topic,
                content_type=self.content_type,
                content_format=self.content_format,
                custom_instructions=self.custom_instructions,
            )

        if self.provider_config is None:
            self.provider_config = ProviderConfig()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "topic": self.topic,
            "content_type": self.content_type.value,
            "content_format": self.content_format.value,
            "client_profile": self.client_profile,
            "workflow_type": self.workflow_type,
            "provider_config": (
                self.provider_config.to_dict() if self.provider_config else None
            ),
            "generation_params": (
                self.generation_params.to_dict() if self.generation_params else None
            ),
            "custom_instructions": self.custom_instructions,
            "context": self.context,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ContentGenerationRequest":
        """Create from dictionary representation."""
        return cls(
            topic=data["topic"],
            content_type=ContentType(data.get("content_type", "article")),
            content_format=ContentFormat(data.get("content_format", "markdown")),
            client_profile=data.get("client_profile"),
            workflow_type=data.get("workflow_type"),
            provider_config=(
                ProviderConfig.from_dict(data["provider_config"])
                if data.get("provider_config")
                else None
            ),
            generation_params=(
                GenerationParams.from_dict(data["generation_params"])
                if data.get("generation_params")
                else None
            ),
            custom_instructions=data.get("custom_instructions", ""),
            context=data.get("context", {}),
        )


@dataclass
class WorkflowMetrics:
    """Workflow execution metrics."""

    total_cost: float = 0.0
    total_tokens: int = 0
    duration_seconds: float = 0.0
    agents_used: int = 0
    success_rate: float = 1.0
    tasks_completed: int = 0
    tasks_failed: int = 0
    tool_calls: int = 0
    llm_calls: int = 0


@dataclass
class ContentGenerationResponse:
    """
    Response DTO for content generation.

    This DTO encapsulates the result of content generation,
    including the generated content and metadata about the process.
    """

    content_id: UUID
    title: str
    body: str
    content_type: ContentType
    content_format: ContentFormat
    workflow_id: Optional[UUID] = None
    generation_time_seconds: Optional[float] = None
    word_count: int = 0
    character_count: int = 0
    reading_time_minutes: float = 0.0
    tasks_completed: int = 0
    total_tasks: int = 0
    success: bool = True
    error_message: Optional[str] = None
    warnings: List[str] = None
    metadata: Dict[str, Any] = None
    workflow_metrics: Optional[WorkflowMetrics] = None
    generated_image: Optional[Dict[str, Any]] = None
    image_metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        """Initialize default values."""
        if self.warnings is None:
            self.warnings = []

        if self.metadata is None:
            self.metadata = {}

    def get_progress_percentage(self) -> float:
        """Get completion progress as percentage."""
        if self.total_tasks == 0:
            return 100.0 if self.success else 0.0
        return (self.tasks_completed / self.total_tasks) * 100.0

    def is_completed(self) -> bool:
        """Check if generation is completed."""
        return self.tasks_completed == self.total_tasks and self.success

    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return len(self.warnings) > 0

    def add_warning(self, warning: str) -> None:
        """Add a warning message."""
        if warning not in self.warnings:
            self.warnings.append(warning)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "content_id": str(self.content_id),
            "title": self.title,
            "body": self.body,
            "content_type": self.content_type.value,
            "content_format": self.content_format.value,
            "workflow_id": str(self.workflow_id) if self.workflow_id else None,
            "generation_time_seconds": self.generation_time_seconds,
            "word_count": self.word_count,
            "character_count": self.character_count,
            "reading_time_minutes": self.reading_time_minutes,
            "tasks_completed": self.tasks_completed,
            "total_tasks": self.total_tasks,
            "success": self.success,
            "error_message": self.error_message,
            "warnings": self.warnings,
            "metadata": self.metadata,
            "generated_image": self.generated_image,
            "image_metadata": self.image_metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ContentGenerationResponse":
        """Create from dictionary representation."""
        return cls(
            content_id=UUID(data["content_id"]),
            title=data["title"],
            body=data["body"],
            content_type=ContentType(data["content_type"]),
            content_format=ContentFormat(data["content_format"]),
            workflow_id=UUID(data["workflow_id"]) if data.get("workflow_id") else None,
            generation_time_seconds=data.get("generation_time_seconds"),
            word_count=data.get("word_count", 0),
            character_count=data.get("character_count", 0),
            reading_time_minutes=data.get("reading_time_minutes", 0.0),
            tasks_completed=data.get("tasks_completed", 0),
            total_tasks=data.get("total_tasks", 0),
            success=data.get("success", True),
            error_message=data.get("error_message"),
            warnings=data.get("warnings", []),
            metadata=data.get("metadata", {}),
            generated_image=data.get("generated_image"),
            image_metadata=data.get("image_metadata"),
        )
