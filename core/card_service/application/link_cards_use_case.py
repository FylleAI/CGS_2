"""
Card Service Application - Link Cards Use Case
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from core.card_service.domain.card_entity import CardRelationship
from core.card_service.domain.card_types import RelationshipType
from core.card_service.infrastructure.card_relationship_repository import (
    CardRelationshipRepository,
)
from core.card_service.infrastructure.card_repository import CardRepository


class LinkCardsUseCase:
    """Use case for linking cards together"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.card_repository = CardRepository(session)
        self.relationship_repository = CardRelationshipRepository(session)

    async def execute(
        self,
        source_card_id: UUID,
        target_card_id: UUID,
        tenant_id: UUID,
        relationship_type: RelationshipType,
        strength: float = 1.0,
    ) -> Optional[CardRelationship]:
        """
        Create a relationship between two cards.
        
        Args:
            source_card_id: Source card ID
            target_card_id: Target card ID
            tenant_id: Tenant identifier (for security)
            relationship_type: Type of relationship
            strength: Strength of relationship (0.0 to 1.0)
            
        Returns:
            Created CardRelationship, or None if cards not found
        """
        
        # Validate cards exist and belong to tenant
        source_card = await self.card_repository.get_by_id(source_card_id, tenant_id)
        target_card = await self.card_repository.get_by_id(target_card_id, tenant_id)
        
        if not source_card or not target_card:
            raise ValueError("One or both cards not found or don't belong to tenant")
        
        # Validate no self-reference
        if source_card_id == target_card_id:
            raise ValueError("Cannot create self-referencing relationship")
        
        # Check if relationship already exists
        existing = await self.relationship_repository.get_by_cards(
            source_card_id, target_card_id
        )
        
        if existing:
            # Update existing relationship
            return await self.relationship_repository.update(
                existing.id,
                relationship_type=relationship_type,
                strength=strength,
            )
        
        # Create new relationship
        return await self.relationship_repository.create(
            source_card_id=source_card_id,
            target_card_id=target_card_id,
            relationship_type=relationship_type,
            strength=strength,
        )

    async def link_multiple(
        self,
        tenant_id: UUID,
        links: List[tuple],  # [(source_id, target_id, relationship_type, strength), ...]
    ) -> List[CardRelationship]:
        """
        Create multiple relationships at once.
        
        Args:
            tenant_id: Tenant identifier
            links: List of tuples (source_id, target_id, relationship_type, strength)
            
        Returns:
            List of created CardRelationship objects
        """
        
        relationships = []
        for source_id, target_id, rel_type, strength in links:
            rel = await self.execute(
                source_card_id=source_id,
                target_card_id=target_id,
                tenant_id=tenant_id,
                relationship_type=rel_type,
                strength=strength,
            )
            if rel:
                relationships.append(rel)
        
        return relationships

