"""Content types and configurations for onboarding content generation."""

from enum import Enum
from typing import Any, Dict
from pydantic import BaseModel, Field


class ContentType(str, Enum):
    """Supported content types for onboarding content generation."""
    
    LINKEDIN_POST = "linkedin_post"
    LINKEDIN_ARTICLE = "linkedin_article"
    NEWSLETTER = "newsletter"
    BLOG_POST = "blog_post"


class ContentConfig(BaseModel):
    """Base configuration for content generation."""
    
    word_count: int = Field(..., description="Target word count")
    tone: str = Field(default="professional", description="Content tone")
    
    class Config:
        extra = "allow"  # Allow additional fields


class LinkedInPostConfig(ContentConfig):
    """Configuration for LinkedIn post generation."""
    
    word_count: int = Field(default=300, ge=200, le=400)
    include_emoji: bool = Field(default=True, description="Include strategic emojis")
    include_hashtags: bool = Field(default=True, description="Include relevant hashtags")
    include_cta: bool = Field(default=True, description="Include call-to-action")
    max_hashtags: int = Field(default=5, ge=3, le=7)
    tone: str = Field(default="conversational", description="Conversational and engaging")


class LinkedInArticleConfig(ContentConfig):
    """Configuration for LinkedIn article generation."""
    
    word_count: int = Field(default=1200, ge=800, le=1500)
    include_headings: bool = Field(default=True, description="Include H2/H3 headings")
    include_statistics: bool = Field(default=True, description="Include data and statistics")
    include_examples: bool = Field(default=True, description="Include concrete examples")
    include_sources: bool = Field(default=True, description="Include source citations")
    tone: str = Field(default="thought_leadership", description="Professional thought leadership")


class NewsletterConfig(ContentConfig):
    """Configuration for newsletter generation."""
    
    word_count: int = Field(default=1200, ge=1000, le=1500)
    num_sections: int = Field(default=4, ge=3, le=6, description="Number of sections")
    include_links: bool = Field(default=True, description="Include external links")
    include_cta: bool = Field(default=True, description="Include call-to-action")
    format: str = Field(default="multi_section", description="Newsletter format")
    tone: str = Field(default="informative", description="Informative and curated")


class BlogPostConfig(ContentConfig):
    """Configuration for blog post generation."""
    
    word_count: int = Field(default=1500, ge=1200, le=2000)
    seo_optimized: bool = Field(default=True, description="SEO optimization")
    include_headings: bool = Field(default=True, description="Include H2/H3 structure")
    include_faq: bool = Field(default=True, description="Include FAQ section")
    include_meta_description: bool = Field(default=True, description="Generate meta description")
    tone: str = Field(default="informative", description="Informative and comprehensive")


def get_default_config(content_type: ContentType) -> ContentConfig:
    """Get default configuration for a content type."""
    
    config_map = {
        ContentType.LINKEDIN_POST: LinkedInPostConfig(),
        ContentType.LINKEDIN_ARTICLE: LinkedInArticleConfig(),
        ContentType.NEWSLETTER: NewsletterConfig(),
        ContentType.BLOG_POST: BlogPostConfig(),
    }
    
    return config_map.get(content_type, ContentConfig(word_count=800))


def build_content_config(
    content_type: ContentType,
    custom_params: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    Build content configuration dictionary for a content type.
    
    Args:
        content_type: Type of content to generate
        custom_params: Optional custom parameters to override defaults
    
    Returns:
        Dictionary with content configuration
    """
    
    # Get default config
    default_config = get_default_config(content_type)
    
    # Convert to dict
    config_dict = default_config.model_dump()
    
    # Override with custom params if provided
    if custom_params:
        config_dict.update(custom_params)
    
    return config_dict

