"""
Card Service Infrastructure - Card Relationship Repository
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.card_service.domain.card_entity import CardRelationship
from core.card_service.domain.card_types import RelationshipType


class CardRelationshipRepository:
    """Repository for card relationship CRUD operations"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        source_card_id: UUID,
        target_card_id: UUID,
        relationship_type: RelationshipType,
        strength: float = 1.0,
    ) -> CardRelationship:
        """Create a new relationship"""

        query = text("""
            INSERT INTO card_relationships
            (source_card_id, target_card_id, relationship_type, strength)
            VALUES (:source_card_id, :target_card_id, :relationship_type, :strength)
            RETURNING *
        """)

        result = await self.session.execute(
            query,
            {
                "source_card_id": str(source_card_id),
                "target_card_id": str(target_card_id),
                "relationship_type": relationship_type.value,
                "strength": strength,
            },
        )
        await self.session.commit()

        return result.fetchone()

    async def get_by_id(self, relationship_id: UUID) -> Optional[CardRelationship]:
        """Get relationship by ID"""

        query = text("""
            SELECT * FROM card_relationships
            WHERE id = :relationship_id
        """)

        result = await self.session.execute(
            query,
            {"relationship_id": str(relationship_id)},
        )

        return result.fetchone()

    async def get_by_source_card(self, source_card_id: UUID) -> List[CardRelationship]:
        """Get all relationships from a source card"""

        query = text("""
            SELECT * FROM card_relationships
            WHERE source_card_id = :source_card_id
            ORDER BY created_at DESC
        """)

        result = await self.session.execute(
            query,
            {"source_card_id": str(source_card_id)},
        )

        return result.fetchall()

    async def get_by_target_card(self, target_card_id: UUID) -> List[CardRelationship]:
        """Get all relationships to a target card"""

        query = text("""
            SELECT * FROM card_relationships
            WHERE target_card_id = :target_card_id
            ORDER BY created_at DESC
        """)

        result = await self.session.execute(
            query,
            {"target_card_id": str(target_card_id)},
        )

        return result.fetchall()

    async def get_by_cards(
        self, source_card_id: UUID, target_card_id: UUID
    ) -> Optional[CardRelationship]:
        """Get relationship between two specific cards"""

        query = text("""
            SELECT * FROM card_relationships
            WHERE source_card_id = :source_card_id AND target_card_id = :target_card_id
            LIMIT 1
        """)

        result = await self.session.execute(
            query,
            {
                "source_card_id": str(source_card_id),
                "target_card_id": str(target_card_id),
            },
        )

        return result.fetchone()

    async def update(
        self,
        relationship_id: UUID,
        relationship_type: Optional[RelationshipType] = None,
        strength: Optional[float] = None,
    ) -> Optional[CardRelationship]:
        """Update relationship"""
        
        updates = []
        params = {"relationship_id": str(relationship_id)}
        
        if relationship_type is not None:
            updates.append("relationship_type = :relationship_type")
            params["relationship_type"] = relationship_type.value
        
        if strength is not None:
            updates.append("strength = :strength")
            params["strength"] = strength
        
        if not updates:
            return await self.get_by_id(relationship_id)

        query = text(f"""
            UPDATE card_relationships
            SET {', '.join(updates)}
            WHERE id = :relationship_id
            RETURNING *
        """)

        result = await self.session.execute(query, params)
        await self.session.commit()

        return result.fetchone()

    async def delete(self, relationship_id: UUID) -> bool:
        """Delete relationship"""

        query = text("""
            DELETE FROM card_relationships
            WHERE id = :relationship_id
        """)

        result = await self.session.execute(
            query,
            {"relationship_id": str(relationship_id)},
        )
        await self.session.commit()

        return result.rowcount > 0

    async def delete_by_cards(
        self, source_card_id: UUID, target_card_id: UUID
    ) -> bool:
        """Delete relationship between two cards"""

        query = text("""
            DELETE FROM card_relationships
            WHERE source_card_id = :source_card_id AND target_card_id = :target_card_id
        """)

        result = await self.session.execute(
            query,
            {
                "source_card_id": str(source_card_id),
                "target_card_id": str(target_card_id),
            },
        )
        await self.session.commit()

        return result.rowcount > 0

