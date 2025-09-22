"""Content entity - represents generated content."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
from enum import Enum
from datetime import datetime


class ContentType(Enum):
    """Types of generated content."""

    ARTICLE = "article"
    NEWSLETTER = "newsletter"
    BLOG_POST = "blog_post"
    SOCIAL_MEDIA = "social_media"
    EMAIL = "email"
    REPORT = "report"
    SUMMARY = "summary"
    OTHER = "other"


class ContentStatus(Enum):
    """Content lifecycle status."""

    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ContentFormat(Enum):
    """Content output formats."""

    MARKDOWN = "markdown"
    HTML = "html"
    PLAIN_TEXT = "plain_text"
    JSON = "json"


@dataclass
class ContentMetrics:
    """Metrics for content analysis."""

    word_count: int = 0
    character_count: int = 0
    reading_time_minutes: float = 0.0
    readability_score: Optional[float] = None
    sentiment_score: Optional[float] = None

    def calculate_reading_time(self, words_per_minute: int = 200) -> None:
        """Calculate reading time based on word count."""
        if self.word_count > 0:
            self.reading_time_minutes = self.word_count / words_per_minute


@dataclass
class Content:
    """
    Content entity representing generated content.

    This entity encapsulates all information about a piece of generated content,
    including its metadata, metrics, and lifecycle information.
    """

    id: UUID = field(default_factory=uuid4)
    title: str = ""
    body: str = ""
    content_type: ContentType = ContentType.ARTICLE
    content_format: ContentFormat = ContentFormat.MARKDOWN
    status: ContentStatus = ContentStatus.DRAFT
    workflow_id: Optional[UUID] = None
    client_profile: Optional[str] = None
    target_audience: str = ""
    topic: str = ""
    tags: List[str] = field(default_factory=list)
    metrics: ContentMetrics = field(default_factory=ContentMetrics)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = None
    version: int = 1

    def __post_init__(self) -> None:
        """Calculate metrics after initialization."""
        self.update_metrics()

    def update_content(
        self, title: Optional[str] = None, body: Optional[str] = None
    ) -> None:
        """Update content and recalculate metrics."""
        if title is not None:
            self.title = title
        if body is not None:
            self.body = body

        self.updated_at = datetime.utcnow()
        self.version += 1
        self.update_metrics()

    def update_metrics(self) -> None:
        """Update content metrics based on current content."""
        # Calculate word and character counts
        words = self.body.split() if self.body else []
        self.metrics.word_count = len(words)
        self.metrics.character_count = len(self.body)
        self.metrics.calculate_reading_time()

    def add_tag(self, tag: str) -> None:
        """Add a tag to the content."""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.utcnow()

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the content."""
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.utcnow()

    def change_status(self, new_status: ContentStatus) -> None:
        """Change content status with validation."""
        valid_transitions = {
            ContentStatus.DRAFT: [ContentStatus.REVIEW, ContentStatus.ARCHIVED],
            ContentStatus.REVIEW: [
                ContentStatus.DRAFT,
                ContentStatus.APPROVED,
                ContentStatus.ARCHIVED,
            ],
            ContentStatus.APPROVED: [
                ContentStatus.PUBLISHED,
                ContentStatus.REVIEW,
                ContentStatus.ARCHIVED,
            ],
            ContentStatus.PUBLISHED: [ContentStatus.ARCHIVED],
            ContentStatus.ARCHIVED: [ContentStatus.DRAFT],
        }

        if new_status not in valid_transitions.get(self.status, []):
            raise ValueError(
                f"Invalid status transition from {self.status} to {new_status}"
            )

        self.status = new_status
        self.updated_at = datetime.utcnow()

        if new_status == ContentStatus.PUBLISHED:
            self.published_at = datetime.utcnow()

    def get_excerpt(self, max_length: int = 200) -> str:
        """Get a short excerpt of the content."""
        if len(self.body) <= max_length:
            return self.body

        # Try to break at a sentence boundary
        excerpt = self.body[:max_length]
        last_sentence_end = max(
            excerpt.rfind("."), excerpt.rfind("!"), excerpt.rfind("?")
        )

        if last_sentence_end > max_length * 0.7:  # If we found a good break point
            # Check if there's more content after this sentence
            sentence_end_pos = last_sentence_end + 1
            if sentence_end_pos < len(self.body):
                return excerpt[:sentence_end_pos] + "..."
            else:
                return excerpt[:sentence_end_pos]
        else:
            # Break at word boundary
            last_space = excerpt.rfind(" ")
            if last_space > 0:
                return excerpt[:last_space] + "..."
            else:
                return excerpt + "..."

    def convert_format(self, target_format: ContentFormat) -> str:
        """Convert content to different format (basic implementation)."""
        if self.content_format == target_format:
            return self.body

        # Basic format conversions
        if self.content_format == ContentFormat.MARKDOWN:
            if target_format == ContentFormat.PLAIN_TEXT:
                # Simple markdown to text conversion
                import re

                text = re.sub(r"[#*`_\[\]()]", "", self.body)
                text = re.sub(r"\n+", "\n", text)
                return text.strip()
            elif target_format == ContentFormat.HTML:
                # Would need a proper markdown parser in real implementation
                return f"<html><body>{self.body}</body></html>"

        return self.body  # Fallback to original content

    def to_dict(self) -> Dict[str, Any]:
        """Convert content to dictionary representation."""
        return {
            "id": str(self.id),
            "title": self.title,
            "body": self.body,
            "content_type": self.content_type.value,
            "content_format": self.content_format.value,
            "status": self.status.value,
            "workflow_id": str(self.workflow_id) if self.workflow_id else None,
            "client_profile": self.client_profile,
            "target_audience": self.target_audience,
            "topic": self.topic,
            "tags": self.tags,
            "metrics": {
                "word_count": self.metrics.word_count,
                "character_count": self.metrics.character_count,
                "reading_time_minutes": self.metrics.reading_time_minutes,
                "readability_score": self.metrics.readability_score,
                "sentiment_score": self.metrics.sentiment_score,
            },
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "published_at": (
                self.published_at.isoformat() if self.published_at else None
            ),
            "version": self.version,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Content":
        """Create content from dictionary representation."""
        content = cls(
            id=UUID(data["id"]) if "id" in data else uuid4(),
            title=data.get("title", ""),
            body=data.get("body", ""),
            content_type=ContentType(data.get("content_type", "article")),
            content_format=ContentFormat(data.get("content_format", "markdown")),
            status=ContentStatus(data.get("status", "draft")),
            workflow_id=UUID(data["workflow_id"]) if data.get("workflow_id") else None,
            client_profile=data.get("client_profile"),
            target_audience=data.get("target_audience", ""),
            topic=data.get("topic", ""),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
            created_at=(
                datetime.fromisoformat(data["created_at"])
                if "created_at" in data
                else datetime.utcnow()
            ),
            updated_at=(
                datetime.fromisoformat(data["updated_at"])
                if "updated_at" in data
                else datetime.utcnow()
            ),
            published_at=(
                datetime.fromisoformat(data["published_at"])
                if data.get("published_at")
                else None
            ),
            version=data.get("version", 1),
        )

        # Set metrics if present
        if "metrics" in data:
            metrics_data = data["metrics"]
            content.metrics = ContentMetrics(
                word_count=metrics_data.get("word_count", 0),
                character_count=metrics_data.get("character_count", 0),
                reading_time_minutes=metrics_data.get("reading_time_minutes", 0.0),
                readability_score=metrics_data.get("readability_score"),
                sentiment_score=metrics_data.get("sentiment_score"),
            )

        return content
