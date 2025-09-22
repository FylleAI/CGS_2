"""File-based content repository implementation."""

import json
import logging
from typing import List, Optional
from uuid import UUID
from pathlib import Path
from datetime import datetime

from ...domain.entities.content import Content, ContentType, ContentStatus
from ...domain.repositories.content_repository import ContentRepository

logger = logging.getLogger(__name__)


class FileContentRepository(ContentRepository):
    """
    File-based implementation of ContentRepository.

    This implementation stores content as JSON files in the filesystem,
    providing a simple persistence mechanism without requiring a database.
    """

    def __init__(self, base_path: str = "data/output"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

        # Create subdirectories for organization
        (self.base_path / "content").mkdir(exist_ok=True)
        (self.base_path / "metadata").mkdir(exist_ok=True)

    def _get_content_file_path(self, content_id: UUID) -> Path:
        """Get file path for content body."""
        return self.base_path / "content" / f"{content_id}.md"

    def _get_metadata_file_path(self, content_id: UUID) -> Path:
        """Get file path for content metadata."""
        return self.base_path / "metadata" / f"{content_id}.json"

    async def save(self, content: Content) -> Content:
        """Save content to files."""
        try:
            # Save content body
            content_file = self._get_content_file_path(content.id)
            with open(content_file, "w", encoding="utf-8") as f:
                f.write(content.body)

            # Save metadata
            metadata_file = self._get_metadata_file_path(content.id)
            metadata = content.to_dict()
            metadata.pop("body", None)  # Don't duplicate body in metadata

            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved content {content.id} to {content_file}")
            return content

        except Exception as e:
            logger.error(f"Failed to save content {content.id}: {str(e)}")
            raise

    async def get_by_id(self, content_id: UUID) -> Optional[Content]:
        """Get content by ID."""
        try:
            metadata_file = self._get_metadata_file_path(content_id)
            content_file = self._get_content_file_path(content_id)

            if not metadata_file.exists() or not content_file.exists():
                return None

            # Load metadata
            with open(metadata_file, "r", encoding="utf-8") as f:
                metadata = json.load(f)

            # Load content body
            with open(content_file, "r", encoding="utf-8") as f:
                body = f.read()

            metadata["body"] = body
            return Content.from_dict(metadata)

        except Exception as e:
            logger.error(f"Failed to load content {content_id}: {str(e)}")
            return None

    async def get_by_title(self, title: str) -> Optional[Content]:
        """Get content by title."""
        all_content = await self.get_all()
        for content in all_content:
            if content.title == title:
                return content
        return None

    async def get_by_workflow_id(self, workflow_id: UUID) -> List[Content]:
        """Get content by workflow ID."""
        all_content = await self.get_all()
        return [c for c in all_content if c.workflow_id == workflow_id]

    async def get_by_type(self, content_type: ContentType) -> List[Content]:
        """Get content by type."""
        all_content = await self.get_all()
        return [c for c in all_content if c.content_type == content_type]

    async def get_by_status(self, status: ContentStatus) -> List[Content]:
        """Get content by status."""
        all_content = await self.get_all()
        return [c for c in all_content if c.status == status]

    async def get_by_client_profile(self, profile_name: str) -> List[Content]:
        """Get content by client profile."""
        all_content = await self.get_all()
        return [c for c in all_content if c.client_profile == profile_name]

    async def get_by_topic(self, topic: str) -> List[Content]:
        """Get content by topic."""
        all_content = await self.get_all()
        return [c for c in all_content if topic.lower() in c.topic.lower()]

    async def get_by_tags(self, tags: List[str]) -> List[Content]:
        """Get content by tags."""
        all_content = await self.get_all()
        result = []
        for content in all_content:
            if any(tag in content.tags for tag in tags):
                result.append(content)
        return result

    async def get_all(self) -> List[Content]:
        """Get all content."""
        content_list = []
        metadata_dir = self.base_path / "metadata"

        for metadata_file in metadata_dir.glob("*.json"):
            try:
                content_id = UUID(metadata_file.stem)
                content = await self.get_by_id(content_id)
                if content:
                    content_list.append(content)
            except (ValueError, Exception) as e:
                logger.warning(f"Failed to load content from {metadata_file}: {str(e)}")

        return content_list

    async def get_recent(self, limit: int = 10) -> List[Content]:
        """Get recent content."""
        all_content = await self.get_all()
        sorted_content = sorted(all_content, key=lambda x: x.created_at, reverse=True)
        return sorted_content[:limit]

    async def get_published(self) -> List[Content]:
        """Get published content."""
        return await self.get_by_status(ContentStatus.PUBLISHED)

    async def get_drafts(self) -> List[Content]:
        """Get draft content."""
        return await self.get_by_status(ContentStatus.DRAFT)

    async def update(self, content: Content) -> Content:
        """Update content."""
        if not await self.exists(content.id):
            raise ValueError(f"Content {content.id} does not exist")

        content.updated_at = datetime.utcnow()
        content.version += 1
        return await self.save(content)

    async def delete(self, content_id: UUID) -> bool:
        """Delete content."""
        try:
            content_file = self._get_content_file_path(content_id)
            metadata_file = self._get_metadata_file_path(content_id)

            deleted = False
            if content_file.exists():
                content_file.unlink()
                deleted = True

            if metadata_file.exists():
                metadata_file.unlink()
                deleted = True

            if deleted:
                logger.info(f"Deleted content {content_id}")

            return deleted

        except Exception as e:
            logger.error(f"Failed to delete content {content_id}: {str(e)}")
            return False

    async def exists(self, content_id: UUID) -> bool:
        """Check if content exists."""
        metadata_file = self._get_metadata_file_path(content_id)
        content_file = self._get_content_file_path(content_id)
        return metadata_file.exists() and content_file.exists()

    async def search(self, query: str) -> List[Content]:
        """Search content."""
        all_content = await self.get_all()
        query_lower = query.lower()

        results = []
        for content in all_content:
            if (
                query_lower in content.title.lower()
                or query_lower in content.body.lower()
                or any(query_lower in tag.lower() for tag in content.tags)
            ):
                results.append(content)

        return results

    async def get_content_metrics(self, content_id: UUID) -> Optional[dict]:
        """Get content metrics."""
        content = await self.get_by_id(content_id)
        if not content:
            return None

        return {
            "word_count": content.metrics.word_count,
            "character_count": content.metrics.character_count,
            "reading_time_minutes": content.metrics.reading_time_minutes,
            "readability_score": content.metrics.readability_score,
            "sentiment_score": content.metrics.sentiment_score,
        }

    async def get_content_history(self, content_id: UUID) -> List[Content]:
        """Get content version history."""
        # For file-based implementation, we only have current version
        content = await self.get_by_id(content_id)
        return [content] if content else []

    async def archive_content(self, content_id: UUID) -> bool:
        """Archive content."""
        content = await self.get_by_id(content_id)
        if not content:
            return False

        content.change_status(ContentStatus.ARCHIVED)
        await self.update(content)
        return True
