"""Generation parameters value object."""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum

from ..entities.content import ContentType, ContentFormat


class GenerationMode(Enum):
    """Content generation modes."""

    STANDARD = "standard"
    CREATIVE = "creative"
    ANALYTICAL = "analytical"
    CONVERSATIONAL = "conversational"


@dataclass(frozen=True)
class GenerationParams:
    """
    Immutable parameters for content generation.

    This value object encapsulates all parameters that control
    how content is generated, including style, format, and constraints.
    """

    topic: str
    content_type: ContentType = ContentType.ARTICLE
    content_format: ContentFormat = ContentFormat.MARKDOWN
    generation_mode: GenerationMode = GenerationMode.STANDARD
    target_word_count: Optional[int] = None
    max_word_count: Optional[int] = None
    min_word_count: Optional[int] = None
    include_sources: bool = True
    include_statistics: bool = False
    include_examples: bool = True
    tone: str = "professional"
    style: str = "informative"
    target_audience: str = "general"
    language: str = "en"
    seo_keywords: list[str] = None
    custom_instructions: str = ""
    metadata: Dict[str, Any] = None

    # Enhanced Article specific parameters
    target: Optional[str] = None
    context: Optional[str] = None
    image_style: str = "professional"
    image_provider: str = "openai"

    # Newsletter Premium specific parameters
    newsletter_topic: Optional[str] = None
    edition_number: Optional[int] = None
    featured_sections: Optional[list] = None

    def __post_init__(self) -> None:
        """Initialize default values and validate parameters."""
        if self.seo_keywords is None:
            object.__setattr__(self, "seo_keywords", [])

        if self.metadata is None:
            object.__setattr__(self, "metadata", {})

        if self.featured_sections is None:
            object.__setattr__(self, "featured_sections", [])

        # Set default word counts based on content type
        if self.target_word_count is None:
            object.__setattr__(
                self, "target_word_count", self._get_default_word_count()
            )

        # Validate word count constraints
        if self.min_word_count and self.max_word_count:
            if self.min_word_count > self.max_word_count:
                raise ValueError(
                    "Minimum word count cannot be greater than maximum word count"
                )

        if self.target_word_count:
            if self.min_word_count and self.target_word_count < self.min_word_count:
                raise ValueError(
                    "Target word count cannot be less than minimum word count"
                )
            if self.max_word_count and self.target_word_count > self.max_word_count:
                raise ValueError(
                    "Target word count cannot be greater than maximum word count"
                )

    def _get_default_word_count(self) -> int:
        """Get default word count based on content type."""
        defaults = {
            ContentType.ARTICLE: 800,
            ContentType.NEWSLETTER: 600,
            ContentType.BLOG_POST: 1000,
            ContentType.SOCIAL_MEDIA: 100,
            ContentType.EMAIL: 300,
            ContentType.REPORT: 1500,
            ContentType.SUMMARY: 200,
            ContentType.OTHER: 500,
        }
        return defaults.get(self.content_type, 500)

    def get_word_count_range(self) -> tuple[Optional[int], Optional[int]]:
        """Get the word count range (min, max)."""
        return (self.min_word_count, self.max_word_count)

    def is_within_word_count_limits(self, word_count: int) -> bool:
        """Check if a word count is within the specified limits."""
        if self.min_word_count and word_count < self.min_word_count:
            return False
        if self.max_word_count and word_count > self.max_word_count:
            return False
        return True

    def get_generation_context(self) -> str:
        """Get formatted context for content generation."""
        context_parts = [
            f"Topic: {self.topic}",
            f"Content Type: {self.content_type.value}",
            f"Target Audience: {self.target_audience}",
            f"Tone: {self.tone}",
            f"Style: {self.style}",
            f"Generation Mode: {self.generation_mode.value}",
        ]

        if self.target_word_count:
            context_parts.append(f"Target Word Count: {self.target_word_count}")

        if self.seo_keywords:
            context_parts.append(f"SEO Keywords: {', '.join(self.seo_keywords)}")

        if self.custom_instructions:
            context_parts.append(f"Custom Instructions: {self.custom_instructions}")

        return "\n".join(context_parts)

    def get_content_requirements(self) -> str:
        """Get formatted content requirements."""
        requirements = []

        if self.include_sources:
            requirements.append("Include credible sources and references")

        if self.include_statistics:
            requirements.append("Include relevant statistics and data")

        if self.include_examples:
            requirements.append("Include practical examples and case studies")

        word_count_req = []
        if self.target_word_count:
            word_count_req.append(f"target {self.target_word_count} words")
        if self.min_word_count:
            word_count_req.append(f"minimum {self.min_word_count} words")
        if self.max_word_count:
            word_count_req.append(f"maximum {self.max_word_count} words")

        if word_count_req:
            requirements.append(f"Word count: {', '.join(word_count_req)}")

        return "\n".join(f"- {req}" for req in requirements)

    def with_topic(self, topic: str) -> "GenerationParams":
        """Create new params with different topic."""
        return GenerationParams(
            topic=topic,
            content_type=self.content_type,
            content_format=self.content_format,
            generation_mode=self.generation_mode,
            target_word_count=self.target_word_count,
            max_word_count=self.max_word_count,
            min_word_count=self.min_word_count,
            include_sources=self.include_sources,
            include_statistics=self.include_statistics,
            include_examples=self.include_examples,
            tone=self.tone,
            style=self.style,
            target_audience=self.target_audience,
            language=self.language,
            seo_keywords=self.seo_keywords,
            custom_instructions=self.custom_instructions,
            metadata=self.metadata,
        )

    def with_content_type(self, content_type: ContentType) -> "GenerationParams":
        """Create new params with different content type."""
        return GenerationParams(
            topic=self.topic,
            content_type=content_type,
            content_format=self.content_format,
            generation_mode=self.generation_mode,
            target_word_count=None,  # Will be recalculated
            max_word_count=self.max_word_count,
            min_word_count=self.min_word_count,
            include_sources=self.include_sources,
            include_statistics=self.include_statistics,
            include_examples=self.include_examples,
            tone=self.tone,
            style=self.style,
            target_audience=self.target_audience,
            language=self.language,
            seo_keywords=self.seo_keywords,
            custom_instructions=self.custom_instructions,
            metadata=self.metadata,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "topic": self.topic,
            "content_type": self.content_type.value,
            "content_format": self.content_format.value,
            "generation_mode": self.generation_mode.value,
            "target_word_count": self.target_word_count,
            "max_word_count": self.max_word_count,
            "min_word_count": self.min_word_count,
            "include_sources": self.include_sources,
            "include_statistics": self.include_statistics,
            "include_examples": self.include_examples,
            "tone": self.tone,
            "style": self.style,
            "target_audience": self.target_audience,
            "language": self.language,
            "seo_keywords": self.seo_keywords,
            "custom_instructions": self.custom_instructions,
            "metadata": self.metadata,
            "target": self.target,
            "context": self.context,
            "image_style": self.image_style,
            "image_provider": self.image_provider,
            "newsletter_topic": self.newsletter_topic,
            "edition_number": self.edition_number,
            "featured_sections": self.featured_sections,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GenerationParams":
        """Create from dictionary representation."""
        return cls(
            topic=data["topic"],
            content_type=ContentType(data.get("content_type", "article")),
            content_format=ContentFormat(data.get("content_format", "markdown")),
            generation_mode=GenerationMode(data.get("generation_mode", "standard")),
            target_word_count=data.get("target_word_count"),
            max_word_count=data.get("max_word_count"),
            min_word_count=data.get("min_word_count"),
            include_sources=data.get("include_sources", True),
            include_statistics=data.get("include_statistics", False),
            include_examples=data.get("include_examples", True),
            tone=data.get("tone", "professional"),
            style=data.get("style", "informative"),
            target_audience=data.get("target_audience", "general"),
            language=data.get("language", "en"),
            seo_keywords=data.get("seo_keywords", []),
            custom_instructions=data.get("custom_instructions", ""),
            metadata=data.get("metadata", {}),
            target=data.get("target"),
            context=data.get("context"),
            image_style=data.get("image_style", "professional"),
            image_provider=data.get("image_provider", "openai"),
            newsletter_topic=data.get("newsletter_topic"),
            edition_number=data.get("edition_number"),
            featured_sections=data.get("featured_sections"),
        )
