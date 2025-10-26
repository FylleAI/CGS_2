"""Client profile value object."""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional


@dataclass(frozen=True)
class ClientProfile:
    """
    Immutable client profile configuration.

    This value object encapsulates all client-specific information
    needed for content generation, including brand voice, style guidelines,
    and target audience information.
    """

    name: str
    display_name: str = ""
    description: str = ""
    brand_voice: str = ""
    style_guidelines: str = ""
    target_audience: str = ""
    industry: str = ""
    company_background: str = ""
    key_messages: List[str] = None
    terminology: Dict[str, str] = None
    content_preferences: Dict[str, Any] = None
    rag_enabled: bool = True
    knowledge_base_path: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self) -> None:
        """Initialize default values for mutable fields."""
        if self.key_messages is None:
            object.__setattr__(self, "key_messages", [])

        if self.terminology is None:
            object.__setattr__(self, "terminology", {})

        if self.content_preferences is None:
            object.__setattr__(self, "content_preferences", {})

        if self.metadata is None:
            object.__setattr__(self, "metadata", {})

        if not self.display_name:
            object.__setattr__(self, "display_name", self.name.title())

        if self.rag_enabled and not self.knowledge_base_path:
            object.__setattr__(
                self, "knowledge_base_path", f"data/knowledge_base/{self.name}"
            )

    def get_brand_context(self) -> str:
        """Get comprehensive brand context for content generation."""
        context_parts = []

        if self.brand_voice:
            context_parts.append(f"Brand Voice: {self.brand_voice}")

        if self.company_background:
            context_parts.append(f"Company Background: {self.company_background}")

        if self.target_audience:
            context_parts.append(f"Target Audience: {self.target_audience}")

        if self.industry:
            context_parts.append(f"Industry: {self.industry}")

        if self.key_messages:
            context_parts.append(f"Key Messages: {', '.join(self.key_messages)}")

        if self.style_guidelines:
            context_parts.append(f"Style Guidelines: {self.style_guidelines}")

        return "\n\n".join(context_parts)

    def get_terminology_context(self) -> str:
        """Get terminology context for consistent language use."""
        if not self.terminology:
            return ""

        terms = [
            f"- {term}: {definition}" for term, definition in self.terminology.items()
        ]
        return f"Terminology to use:\n" + "\n".join(terms)

    def get_content_preferences(self, content_type: str = None) -> Dict[str, Any]:
        """Get content preferences, optionally filtered by content type."""
        if not content_type:
            return self.content_preferences

        # Get general preferences and content-type specific ones
        general_prefs = {
            k: v
            for k, v in self.content_preferences.items()
            if not k.startswith(f"{content_type}_")
        }

        specific_prefs = {
            k.replace(f"{content_type}_", ""): v
            for k, v in self.content_preferences.items()
            if k.startswith(f"{content_type}_")
        }

        # Merge with specific preferences taking priority
        return {**general_prefs, **specific_prefs}

    def has_rag_knowledge(self) -> bool:
        """Check if client has RAG knowledge base available."""
        return self.rag_enabled and self.knowledge_base_path is not None

    def with_rag_enabled(self, enabled: bool) -> "ClientProfile":
        """Create a new profile with RAG enabled/disabled."""
        return ClientProfile(
            name=self.name,
            display_name=self.display_name,
            description=self.description,
            brand_voice=self.brand_voice,
            style_guidelines=self.style_guidelines,
            target_audience=self.target_audience,
            industry=self.industry,
            company_background=self.company_background,
            key_messages=self.key_messages,
            terminology=self.terminology,
            content_preferences=self.content_preferences,
            rag_enabled=enabled,
            knowledge_base_path=self.knowledge_base_path,
            metadata=self.metadata,
        )

    def with_knowledge_base_path(self, path: str) -> "ClientProfile":
        """Create a new profile with different knowledge base path."""
        return ClientProfile(
            name=self.name,
            display_name=self.display_name,
            description=self.description,
            brand_voice=self.brand_voice,
            style_guidelines=self.style_guidelines,
            target_audience=self.target_audience,
            industry=self.industry,
            company_background=self.company_background,
            key_messages=self.key_messages,
            terminology=self.terminology,
            content_preferences=self.content_preferences,
            rag_enabled=self.rag_enabled,
            knowledge_base_path=path,
            metadata=self.metadata,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "brand_voice": self.brand_voice,
            "style_guidelines": self.style_guidelines,
            "target_audience": self.target_audience,
            "industry": self.industry,
            "company_background": self.company_background,
            "key_messages": self.key_messages,
            "terminology": self.terminology,
            "content_preferences": self.content_preferences,
            "rag_enabled": self.rag_enabled,
            "knowledge_base_path": self.knowledge_base_path,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ClientProfile":
        """Create from dictionary representation."""
        return cls(
            name=data["name"],
            display_name=data.get("display_name", ""),
            description=data.get("description", ""),
            brand_voice=data.get("brand_voice", ""),
            style_guidelines=data.get("style_guidelines", ""),
            target_audience=data.get("target_audience", ""),
            industry=data.get("industry", ""),
            company_background=data.get("company_background", ""),
            key_messages=data.get("key_messages", []),
            terminology=data.get("terminology", {}),
            content_preferences=data.get("content_preferences", {}),
            rag_enabled=data.get("rag_enabled", True),
            knowledge_base_path=data.get("knowledge_base_path"),
            metadata=data.get("metadata", {}),
        )

    @classmethod
    def create_default(cls, name: str) -> "ClientProfile":
        """Create a default client profile."""
        return cls(
            name=name,
            description=f"Default profile for {name}",
            target_audience="General audience",
            rag_enabled=False,
        )

    @classmethod
    def create_siebert_profile(cls) -> "ClientProfile":
        """Create Siebert Financial client profile."""
        return cls(
            name="siebert",
            display_name="Siebert Financial",
            description="Financial services company focused on empowering individual investors",
            brand_voice="Professional yet accessible, empowering, educational, trustworthy",
            style_guidelines="Use clear, jargon-free language. Focus on education and empowerment. Maintain professional tone while being approachable.",
            target_audience="Gen Z and young professionals interested in financial literacy and investing",
            industry="Financial Services",
            company_background="Founded by Muriel Siebert, the first woman to own a seat on the New York Stock Exchange. Family-owned business focused on democratizing finance.",
            key_messages=[
                "Financial empowerment for everyone",
                "Breaking down barriers in finance",
                "Education-first approach to investing",
                "Family values in financial services",
            ],
            terminology={
                "investing": "building wealth through strategic asset allocation",
                "financial planning": "creating a roadmap for financial success",
                "portfolio": "collection of investments designed to meet your goals",
            },
            content_preferences={
                "tone": "educational and empowering",
                "length": "800-1200 words for articles",
                "newsletter_length": "600-800 words",
                "include_statistics": True,
                "include_actionable_tips": True,
            },
            rag_enabled=True,
            knowledge_base_path="data/knowledge_base/siebert",
        )
