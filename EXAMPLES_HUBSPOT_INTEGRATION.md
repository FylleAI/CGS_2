# 📚 HubSpot Integration - Practical Examples

## 🎯 Overview

This document provides practical code examples for implementing HubSpot native publishing integration.

**⚠️ IMPORTANT**: These are reference examples for planning purposes. Do NOT implement yet.

---

## 1️⃣ HubSpot Adapter Implementation

### Example 1.1: HubSpotAdapter Base Class (Python)

```python
# onboarding/infrastructure/adapters/hubspot_adapter.py

import httpx
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)


class HubSpotRateLimiter:
    """Rate limiter for HubSpot API (100 req/10s, 10k/day)."""
    
    def __init__(self, requests_per_10s: int = 100, requests_per_day: int = 10000):
        self.requests_per_10s = requests_per_10s
        self.requests_per_day = requests_per_day
        self.short_term_requests = []
        self.daily_requests = 0
        self.daily_reset_at = datetime.utcnow() + timedelta(days=1)
    
    async def acquire(self):
        """Wait if rate limit would be exceeded."""
        now = datetime.utcnow()
        
        # Reset daily counter
        if now >= self.daily_reset_at:
            self.daily_requests = 0
            self.daily_reset_at = now + timedelta(days=1)
        
        # Check daily limit
        if self.daily_requests >= self.requests_per_day:
            wait_seconds = (self.daily_reset_at - now).total_seconds()
            logger.warning(f"Daily rate limit reached. Waiting {wait_seconds}s")
            await asyncio.sleep(wait_seconds)
        
        # Clean old short-term requests (older than 10s)
        cutoff = now - timedelta(seconds=10)
        self.short_term_requests = [
            req_time for req_time in self.short_term_requests 
            if req_time > cutoff
        ]
        
        # Check short-term limit
        if len(self.short_term_requests) >= self.requests_per_10s:
            wait_seconds = 10 - (now - self.short_term_requests[0]).total_seconds()
            logger.info(f"Short-term rate limit. Waiting {wait_seconds}s")
            await asyncio.sleep(wait_seconds)
        
        # Record this request
        self.short_term_requests.append(now)
        self.daily_requests += 1


class HubSpotAdapter:
    """Adapter for HubSpot API integration."""
    
    def __init__(
        self,
        access_token: str,
        portal_id: str,
        base_url: str = "https://api.hubapi.com",
        timeout: int = 30,
    ):
        self.access_token = access_token
        self.portal_id = portal_id
        self.base_url = base_url
        self.timeout = timeout
        self.rate_limiter = HubSpotRateLimiter()
    
    def _build_headers(self) -> Dict[str, str]:
        """Build request headers with authentication."""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        max_retries: int = 5,
    ) -> Dict[str, Any]:
        """Make HTTP request with rate limiting and retry logic."""
        
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(max_retries):
            try:
                # Wait for rate limiter
                await self.rate_limiter.acquire()
                
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.request(
                        method=method,
                        url=url,
                        json=data,
                        params=params,
                        headers=self._build_headers(),
                    )
                    
                    # Handle rate limiting
                    if response.status_code == 429:
                        retry_after = int(response.headers.get("Retry-After", 10))
                        logger.warning(f"Rate limited. Retrying after {retry_after}s")
                        await asyncio.sleep(retry_after)
                        continue
                    
                    # Handle server errors with exponential backoff
                    if response.status_code >= 500:
                        wait_time = 2 ** attempt  # Exponential backoff
                        logger.warning(
                            f"Server error {response.status_code}. "
                            f"Retry {attempt + 1}/{max_retries} after {wait_time}s"
                        )
                        await asyncio.sleep(wait_time)
                        continue
                    
                    # Raise for other errors
                    response.raise_for_status()
                    
                    return response.json()
            
            except httpx.HTTPStatusError as e:
                if e.response.status_code < 500:
                    # Don't retry client errors (except 429 handled above)
                    logger.error(f"HubSpot API error: {e.response.status_code} - {e.response.text}")
                    raise
                # Retry server errors
                if attempt == max_retries - 1:
                    raise
            
            except Exception as e:
                logger.error(f"Request failed: {str(e)}")
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)
        
        raise Exception(f"Max retries ({max_retries}) exceeded")
    
    async def publish_blog_post(
        self,
        title: str,
        body_html: str,
        blog_author_id: str,
        content_group_id: str,
        meta_description: Optional[str] = None,
        featured_image: Optional[str] = None,
        tag_ids: Optional[list] = None,
        state: str = "PUBLISHED",
        publish_date: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Publish blog post to HubSpot.
        
        Args:
            title: Blog post title
            body_html: HTML content
            blog_author_id: HubSpot author ID
            content_group_id: HubSpot blog ID
            meta_description: SEO meta description
            featured_image: Featured image URL
            tag_ids: List of HubSpot tag IDs
            state: DRAFT or PUBLISHED
            publish_date: Unix timestamp (milliseconds)
        
        Returns:
            HubSpot blog post object with id and url
        """
        logger.info(f"Publishing blog post: {title}")
        
        payload = {
            "name": title,
            "post_body": body_html,
            "blog_author_id": blog_author_id,
            "content_group_id": content_group_id,
            "state": state,
        }
        
        # Optional fields
        if meta_description:
            payload["meta_description"] = meta_description
        if featured_image:
            payload["featured_image"] = featured_image
        if tag_ids:
            payload["tag_ids"] = tag_ids
        if publish_date:
            payload["publish_date"] = publish_date
        
        result = await self._make_request(
            method="POST",
            endpoint="/content/api/v2/blog-posts",
            data=payload,
        )
        
        logger.info(f"Blog post published: id={result.get('id')}, url={result.get('url')}")
        
        return result
    
    async def publish_social_post(
        self,
        channel_guid: str,
        message: str,
        link_url: Optional[str] = None,
        photo_url: Optional[str] = None,
        trigger_at: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Publish social media post via HubSpot.
        
        Args:
            channel_guid: HubSpot social channel GUID
            message: Post message/text
            link_url: Optional link to include
            photo_url: Optional photo URL
            trigger_at: Unix timestamp (milliseconds) for scheduling
        
        Returns:
            HubSpot broadcast object
        """
        logger.info(f"Publishing social post to channel: {channel_guid}")
        
        payload = {
            "channelGuid": channel_guid,
            "message": message,
        }
        
        if link_url:
            payload["linkUrl"] = link_url
        if photo_url:
            payload["photoUrl"] = photo_url
        if trigger_at:
            payload["triggerAt"] = trigger_at
        
        result = await self._make_request(
            method="POST",
            endpoint="/social/v1/broadcasts",
            data=payload,
        )
        
        logger.info(f"Social post published: broadcast_id={result.get('broadcastGuid')}")
        
        return result
    
    async def get_blog_post_analytics(
        self,
        blog_post_id: str,
    ) -> Dict[str, Any]:
        """
        Get analytics for a blog post.
        
        Args:
            blog_post_id: HubSpot blog post ID
        
        Returns:
            Analytics data (views, CTR, etc.)
        """
        logger.info(f"Fetching analytics for blog post: {blog_post_id}")
        
        result = await self._make_request(
            method="GET",
            endpoint=f"/content/api/v2/blog-posts/{blog_post_id}/analytics",
        )
        
        return result
```

---

### Example 1.2: Markdown to HTML Conversion

```python
# onboarding/infrastructure/converters/markdown_to_html.py

import markdown
from markdown.extensions import fenced_code, tables, nl2br, sane_lists
import bleach
from typing import Optional


class MarkdownToHtmlConverter:
    """Convert Markdown to HubSpot-compatible HTML."""
    
    # Allowed HTML tags (for sanitization)
    ALLOWED_TAGS = [
        'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'blockquote', 'code', 'pre', 'hr', 'div', 'span',
        'ul', 'ol', 'li', 'dl', 'dt', 'dd',
        'table', 'thead', 'tbody', 'tr', 'th', 'td',
        'a', 'img',
    ]
    
    ALLOWED_ATTRIBUTES = {
        '*': ['class', 'id'],
        'a': ['href', 'title', 'target', 'rel'],
        'img': ['src', 'alt', 'title', 'width', 'height'],
        'code': ['class'],  # For syntax highlighting
    }
    
    def __init__(self):
        self.md = markdown.Markdown(
            extensions=[
                'fenced_code',
                'tables',
                'nl2br',
                'sane_lists',
                'codehilite',
            ],
            extension_configs={
                'codehilite': {
                    'css_class': 'highlight',
                    'linenums': False,
                }
            }
        )
    
    def convert(self, markdown_text: str, sanitize: bool = True) -> str:
        """
        Convert Markdown to HTML.
        
        Args:
            markdown_text: Markdown source
            sanitize: Whether to sanitize HTML (recommended)
        
        Returns:
            HTML string
        """
        # Convert Markdown to HTML
        html = self.md.convert(markdown_text)
        
        # Sanitize HTML to prevent XSS
        if sanitize:
            html = bleach.clean(
                html,
                tags=self.ALLOWED_TAGS,
                attributes=self.ALLOWED_ATTRIBUTES,
                strip=True,
            )
        
        # Reset markdown instance for next conversion
        self.md.reset()
        
        return html
    
    def extract_meta_description(
        self,
        markdown_text: str,
        max_length: int = 160,
    ) -> str:
        """
        Extract meta description from first paragraph.
        
        Args:
            markdown_text: Markdown source
            max_length: Max characters (default 160 for SEO)
        
        Returns:
            Meta description string
        """
        # Convert to HTML
        html = self.convert(markdown_text, sanitize=True)
        
        # Extract text from first paragraph
        import re
        match = re.search(r'<p>(.*?)</p>', html, re.DOTALL)
        if not match:
            return ""
        
        text = match.group(1)
        
        # Strip HTML tags
        text = bleach.clean(text, tags=[], strip=True)
        
        # Truncate to max_length
        if len(text) > max_length:
            text = text[:max_length - 3] + "..."
        
        return text
    
    def extract_featured_image(self, markdown_text: str) -> Optional[str]:
        """
        Extract first image URL from Markdown.
        
        Args:
            markdown_text: Markdown source
        
        Returns:
            Image URL or None
        """
        import re
        
        # Match Markdown image syntax: ![alt](url)
        match = re.search(r'!\[.*?\]\((.*?)\)', markdown_text)
        if match:
            return match.group(1)
        
        # Match HTML img tag
        match = re.search(r'<img[^>]+src="([^"]+)"', markdown_text)
        if match:
            return match.group(1)
        
        return None
```

---

## 2️⃣ Use Case Implementation

### Example 2.1: PublishToHubSpotUseCase

```python
# onboarding/application/use_cases/publish_to_hubspot.py

from uuid import UUID
from typing import Optional
from datetime import datetime
import logging

from onboarding.domain.hubspot_models import (
    ContentPublication,
    PublicationStatus,
    HubSpotPlatform,
    PublicationMetadata,
)
from onboarding.infrastructure.adapters.hubspot_adapter import HubSpotAdapter
from onboarding.infrastructure.converters.markdown_to_html import MarkdownToHtmlConverter
from onboarding.infrastructure.repositories.hubspot_credential_repository import (
    HubSpotCredentialRepository,
)
from onboarding.infrastructure.repositories.content_publication_repository import (
    ContentPublicationRepository,
)
from core.infrastructure.repositories.file_content_repository import FileContentRepository

logger = logging.getLogger(__name__)


class PublishToHubSpotUseCase:
    """Use case for publishing content to HubSpot."""
    
    def __init__(
        self,
        content_repository: FileContentRepository,
        credential_repository: HubSpotCredentialRepository,
        publication_repository: ContentPublicationRepository,
        markdown_converter: MarkdownToHtmlConverter,
    ):
        self.content_repo = content_repository
        self.credential_repo = credential_repository
        self.publication_repo = publication_repository
        self.markdown_converter = markdown_converter
    
    async def execute(
        self,
        content_id: UUID,
        tenant_id: UUID,
        platform: HubSpotPlatform,
        metadata: PublicationMetadata,
        schedule_at: Optional[datetime] = None,
    ) -> ContentPublication:
        """
        Publish content to HubSpot.
        
        Args:
            content_id: Content to publish
            tenant_id: Tenant ID
            platform: HubSpot platform (blog, social, email)
            metadata: Publication metadata (SEO, images, etc.)
            schedule_at: Optional scheduled publication time
        
        Returns:
            ContentPublication record
        
        Raises:
            ValueError: If content not found or credentials missing
            Exception: If publication fails
        """
        logger.info(f"Publishing content {content_id} to {platform.value}")
        
        # 1. Get content
        content = await self.content_repo.get_by_id(content_id)
        if not content:
            raise ValueError(f"Content {content_id} not found")
        
        # 2. Get HubSpot credentials for tenant
        credential = await self.credential_repo.get_by_tenant(tenant_id)
        if not credential or not credential.is_active:
            raise ValueError(f"No active HubSpot credentials for tenant {tenant_id}")
        
        # 3. Create publication record
        publication = ContentPublication(
            publication_id=UUID(),
            content_id=content_id,
            tenant_id=tenant_id,
            platform=platform,
            credential_id=credential.credential_id,
            status=PublicationStatus.SCHEDULED if schedule_at else PublicationStatus.PENDING,
            scheduled_at=schedule_at,
            metadata={},
        )
        
        publication = await self.publication_repo.create(publication)
        
        # 4. If scheduled, return early
        if schedule_at:
            logger.info(f"Publication scheduled for {schedule_at}")
            return publication
        
        # 5. Publish immediately
        try:
            await self._publish_now(content, credential, publication, metadata)
            return publication
        
        except Exception as e:
            logger.error(f"Publication failed: {str(e)}")
            await self.publication_repo.update_status(
                publication.publication_id,
                PublicationStatus.FAILED,
                error_message=str(e),
            )
            raise
    
    async def _publish_now(
        self,
        content,
        credential,
        publication: ContentPublication,
        metadata: PublicationMetadata,
    ):
        """Publish content immediately."""
        
        # Update status to PUBLISHING
        await self.publication_repo.update_status(
            publication.publication_id,
            PublicationStatus.PUBLISHING,
        )
        
        # Initialize HubSpot adapter
        adapter = HubSpotAdapter(
            access_token=credential.access_token,
            portal_id=credential.portal_id,
        )
        
        # Publish based on platform
        if publication.platform == HubSpotPlatform.BLOG:
            result = await self._publish_blog_post(adapter, content, metadata)
        elif publication.platform == HubSpotPlatform.SOCIAL_LINKEDIN:
            result = await self._publish_social_post(adapter, content, metadata)
        else:
            raise ValueError(f"Unsupported platform: {publication.platform}")
        
        # Update publication with HubSpot IDs
        await self.publication_repo.update_status(
            publication.publication_id,
            PublicationStatus.PUBLISHED,
            platform_content_id=result.get("id") or result.get("broadcastGuid"),
            platform_url=result.get("url"),
            published_at=datetime.utcnow(),
        )
        
        logger.info(f"Publication successful: {result.get('url')}")
    
    async def _publish_blog_post(
        self,
        adapter: HubSpotAdapter,
        content,
        metadata: PublicationMetadata,
    ) -> dict:
        """Publish blog post."""
        
        # Convert Markdown to HTML
        body_html = self.markdown_converter.convert(content.body)
        
        # Extract meta description if not provided
        meta_description = metadata.meta_description
        if not meta_description:
            meta_description = self.markdown_converter.extract_meta_description(content.body)
        
        # Publish to HubSpot
        result = await adapter.publish_blog_post(
            title=content.title,
            body_html=body_html,
            blog_author_id=metadata.author_id,
            content_group_id=metadata.blog_id,
            meta_description=meta_description,
            featured_image=metadata.featured_image_url,
            tag_ids=metadata.tags,
            state="PUBLISHED",
        )
        
        return result
    
    async def _publish_social_post(
        self,
        adapter: HubSpotAdapter,
        content,
        metadata: PublicationMetadata,
    ) -> dict:
        """Publish social media post."""
        
        # Use social_message if provided, otherwise use content body
        message = metadata.social_message or content.body
        
        # Truncate to LinkedIn limit (3000 chars)
        if len(message) > 3000:
            message = message[:2997] + "..."
        
        result = await adapter.publish_social_post(
            channel_guid=metadata.social_channel_guid,
            message=message,
            link_url=metadata.social_link_url,
            photo_url=metadata.social_photo_url,
        )
        
        return result
```

---

## 3️⃣ API Endpoints

### Example 3.1: FastAPI Endpoints

```python
# onboarding/api/endpoints.py (additions)

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from uuid import UUID
from typing import Optional, List
from datetime import datetime

from onboarding.domain.hubspot_models import HubSpotPlatform, PublicationStatus
from onboarding.application.use_cases.publish_to_hubspot import PublishToHubSpotUseCase

router = APIRouter(prefix="/api/v1", tags=["hubspot"])


class PublishToHubSpotRequest(BaseModel):
    """Request to publish content to HubSpot."""
    platform: HubSpotPlatform
    blog_id: Optional[str] = None
    author_id: Optional[str] = None
    meta_description: Optional[str] = None
    featured_image_url: Optional[str] = None
    tags: List[str] = []
    schedule_at: Optional[datetime] = None


class PublicationResponse(BaseModel):
    """Publication response."""
    publication_id: UUID
    content_id: UUID
    platform: str
    status: str
    platform_url: Optional[str]
    scheduled_at: Optional[datetime]
    published_at: Optional[datetime]


@router.post("/content/{content_id}/publish/hubspot", response_model=PublicationResponse)
async def publish_to_hubspot(
    content_id: UUID,
    request: PublishToHubSpotRequest,
    tenant_id: UUID = Depends(get_current_tenant),
    use_case: PublishToHubSpotUseCase = Depends(get_publish_use_case),
):
    """Publish content to HubSpot."""
    
    try:
        publication = await use_case.execute(
            content_id=content_id,
            tenant_id=tenant_id,
            platform=request.platform,
            metadata=PublicationMetadata(
                blog_id=request.blog_id,
                author_id=request.author_id,
                meta_description=request.meta_description,
                featured_image_url=request.featured_image_url,
                tags=request.tags,
            ),
            schedule_at=request.schedule_at,
        )
        
        return PublicationResponse(
            publication_id=publication.publication_id,
            content_id=publication.content_id,
            platform=publication.platform.value,
            status=publication.status.value,
            platform_url=publication.platform_url,
            scheduled_at=publication.scheduled_at,
            published_at=publication.published_at,
        )
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/publications/{publication_id}", response_model=PublicationResponse)
async def get_publication(
    publication_id: UUID,
    publication_repo = Depends(get_publication_repository),
):
    """Get publication status."""
    
    publication = await publication_repo.get_by_id(publication_id)
    if not publication:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publication not found")
    
    return PublicationResponse(
        publication_id=publication.publication_id,
        content_id=publication.content_id,
        platform=publication.platform.value,
        status=publication.status.value,
        platform_url=publication.platform_url,
        scheduled_at=publication.scheduled_at,
        published_at=publication.published_at,
    )


@router.post("/publications/{publication_id}/retry")
async def retry_publication(
    publication_id: UUID,
    use_case: PublishToHubSpotUseCase = Depends(get_publish_use_case),
):
    """Retry failed publication."""
    
    # Implementation here
    pass
```

---

**Last Updated**: 2025-10-25  
**Version**: 1.0  
**Status**: Reference Examples Only - Do Not Implement Yet

