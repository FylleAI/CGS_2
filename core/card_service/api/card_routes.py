"""
Card Service API - FastAPI Routes
"""

from typing import List, Optional, Union
from uuid import UUID
import hashlib

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.card_service.api.card_schemas import (
    CardResponseSchema,
    CreateCardRequestSchema,
    CreateRelationshipRequestSchema,
    RelationshipResponseSchema,
    UpdateCardRequestSchema,
)
from core.card_service.application.create_card_use_case import CreateCardUseCase
from core.card_service.application.get_card_use_case import GetCardUseCase
from core.card_service.application.link_cards_use_case import LinkCardsUseCase
from core.card_service.application.list_cards_use_case import ListCardsUseCase
from core.card_service.application.update_card_use_case import UpdateCardUseCase
from core.card_service.domain.card_entity import CreateCardRequest, UpdateCardRequest
from core.card_service.infrastructure.card_relationship_repository import (
    CardRelationshipRepository,
)
from core.card_service.infrastructure.card_repository import CardRepository

# Create router
router = APIRouter(prefix="/api/v1/cards", tags=["cards"])


# Dependency to get database session
async def get_db_session() -> AsyncSession:
    """Get database session - implement based on your setup"""
    # This should be injected from your main app
    pass


def normalize_tenant_id(tenant_id: str) -> str:
    """
    Normalize tenant_id to handle both email and UUID formats.

    - If it's a valid UUID, return as-is
    - If it's an email or string, convert to deterministic UUID v5
    - If it's 'admin', return as-is for super admin mode
    """
    if not tenant_id or tenant_id.strip() == '':
        raise ValueError("tenant_id cannot be empty")

    tenant_id = tenant_id.strip()

    # Allow 'admin' for super admin mode
    if tenant_id.lower() == 'admin':
        return tenant_id

    # Check if it's already a valid UUID
    try:
        UUID(tenant_id)
        return tenant_id
    except ValueError:
        pass

    # Convert email or string to deterministic UUID v5
    # Using a namespace UUID for Fylle
    FYLLE_NAMESPACE = UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')
    return str(UUID(hashlib.md5(f"fylle:{tenant_id}".encode()).hexdigest()))


# ============================================================================
# Card CRUD Endpoints
# ============================================================================


@router.post("", response_model=CardResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_card(
    tenant_id: str = Query(..., description="Tenant ID (email or UUID)"),
    request: CreateCardRequestSchema = None,
    session: AsyncSession = Depends(get_db_session),
) -> CardResponseSchema:
    """
    Create a new card.

    If a card of the same type already exists for the tenant, it will be soft-deleted.

    tenant_id can be:
    - Email address (e.g., user@example.com)
    - UUID (e.g., 550e8400-e29b-41d4-a716-446655440000)
    - 'admin' for super admin mode
    """

    try:
        # Normalize tenant_id
        normalized_tenant_id = normalize_tenant_id(tenant_id)

        use_case = CreateCardUseCase(session)

        card_request = CreateCardRequest(
            card_type=request.card_type,
            title=request.title,
            content=request.content,
            metrics=request.metrics,
            notes=request.notes,
        )

        card = await use_case.execute(normalized_tenant_id, card_request)
        
        return CardResponseSchema(
            id=card.id,
            tenant_id=card.tenant_id,
            card_type=card.card_type,
            title=card.title,
            content=card.content,
            metrics=card.metrics,
            notes=card.notes,
            version=card.version,
            is_active=card.is_active,
            created_by=card.created_by,
            updated_by=card.updated_by,
            created_at=card.created_at,
            updated_at=card.updated_at,
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("", response_model=List[CardResponseSchema])
async def list_cards(
    tenant_id: str = Query(..., description="Tenant ID (email or UUID)"),
    card_type: Optional[str] = Query(None, description="Filter by card type"),
    session: AsyncSession = Depends(get_db_session),
) -> List[CardResponseSchema]:
    """
    List all cards for a tenant, optionally filtered by type.

    tenant_id can be:
    - Email address (e.g., user@example.com)
    - UUID (e.g., 550e8400-e29b-41d4-a716-446655440000)
    - 'admin' for super admin mode (returns all cards)
    """

    try:
        # Normalize tenant_id
        normalized_tenant_id = normalize_tenant_id(tenant_id)

        use_case = ListCardsUseCase(session)
        cards = await use_case.execute(normalized_tenant_id, card_type)
        
        return [
            CardResponseSchema(
                id=card.id,
                tenant_id=card.tenant_id,
                card_type=card.card_type,
                title=card.title,
                content=card.content,
                metrics=card.metrics,
                notes=card.notes,
                version=card.version,
                is_active=card.is_active,
                created_by=card.created_by,
                updated_by=card.updated_by,
                created_at=card.created_at,
                updated_at=card.updated_at,
                relationships=[],
            )
            for card in cards
        ]
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{card_id}", response_model=CardResponseSchema)
async def get_card(
    card_id: UUID,
    tenant_id: str = Query(..., description="Tenant ID (email or UUID)"),
    session: AsyncSession = Depends(get_db_session),
) -> CardResponseSchema:
    """
    Get a specific card by ID with all its relationships.

    tenant_id can be:
    - Email address (e.g., user@example.com)
    - UUID (e.g., 550e8400-e29b-41d4-a716-446655440000)
    - 'admin' for super admin mode
    """

    try:
        # Normalize tenant_id
        normalized_tenant_id = normalize_tenant_id(tenant_id)

        use_case = GetCardUseCase(session)
        card = await use_case.execute(card_id, normalized_tenant_id)
        
        if not card:
            raise HTTPException(status_code=404, detail="Card not found")
        
        return CardResponseSchema(
            id=card.id,
            tenant_id=card.tenant_id,
            card_type=card.card_type,
            title=card.title,
            content=card.content,
            metrics=card.metrics,
            notes=card.notes,
            version=card.version,
            is_active=card.is_active,
            created_by=card.created_by,
            updated_by=card.updated_by,
            created_at=card.created_at,
            updated_at=card.updated_at,
            relationships=card.relationships,
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.patch("/{card_id}", response_model=CardResponseSchema)
async def update_card(
    card_id: UUID,
    tenant_id: str = Query(..., description="Tenant ID (email or UUID)"),
    request: UpdateCardRequestSchema = None,
    session: AsyncSession = Depends(get_db_session),
) -> CardResponseSchema:
    """
    Update a card. Only provided fields will be updated.

    tenant_id can be:
    - Email address (e.g., user@example.com)
    - UUID (e.g., 550e8400-e29b-41d4-a716-446655440000)
    - 'admin' for super admin mode
    """

    try:
        # Normalize tenant_id
        normalized_tenant_id = normalize_tenant_id(tenant_id)

        use_case = UpdateCardUseCase(session)

        card_request = UpdateCardRequest(
            title=request.title,
            content=request.content,
            metrics=request.metrics,
            notes=request.notes,
        )

        card = await use_case.execute(card_id, normalized_tenant_id, card_request)
        
        if not card:
            raise HTTPException(status_code=404, detail="Card not found")
        
        return CardResponseSchema(
            id=card.id,
            tenant_id=card.tenant_id,
            card_type=card.card_type,
            title=card.title,
            content=card.content,
            metrics=card.metrics,
            notes=card.notes,
            version=card.version,
            is_active=card.is_active,
            created_by=card.created_by,
            updated_by=card.updated_by,
            created_at=card.created_at,
            updated_at=card.updated_at,
            relationships=card.relationships,
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_card(
    card_id: UUID,
    tenant_id: str = Query(..., description="Tenant ID (email or UUID)"),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    """
    Soft delete a card.

    tenant_id can be:
    - Email address (e.g., user@example.com)
    - UUID (e.g., 550e8400-e29b-41d4-a716-446655440000)
    - 'admin' for super admin mode
    """

    try:
        # Normalize tenant_id
        normalized_tenant_id = normalize_tenant_id(tenant_id)

        repository = CardRepository(session)
        success = await repository.soft_delete(card_id, normalized_tenant_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Card not found")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================================
# Card Relationship Endpoints
# ============================================================================


@router.post(
    "/{source_card_id}/relationships",
    response_model=RelationshipResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_relationship(
    source_card_id: UUID,
    tenant_id: UUID = Query(..., description="Tenant ID"),
    request: CreateRelationshipRequestSchema = None,
    session: AsyncSession = Depends(get_db_session),
) -> RelationshipResponseSchema:
    """
    Create a relationship between two cards.
    """
    
    try:
        use_case = LinkCardsUseCase(session)
        
        relationship = await use_case.execute(
            source_card_id=source_card_id,
            target_card_id=request.target_card_id,
            tenant_id=tenant_id,
            relationship_type=request.relationship_type,
            strength=request.strength,
        )
        
        if not relationship:
            raise HTTPException(status_code=400, detail="Failed to create relationship")
        
        return RelationshipResponseSchema(
            id=relationship.id,
            source_card_id=relationship.source_card_id,
            target_card_id=relationship.target_card_id,
            relationship_type=relationship.relationship_type,
            strength=relationship.strength,
            created_at=relationship.created_at,
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{card_id}/relationships", response_model=List[RelationshipResponseSchema])
async def get_relationships(
    card_id: UUID,
    tenant_id: UUID = Query(..., description="Tenant ID"),
    session: AsyncSession = Depends(get_db_session),
) -> List[RelationshipResponseSchema]:
    """
    Get all relationships for a card.
    """
    
    try:
        # Verify card exists and belongs to tenant
        card_repo = CardRepository(session)
        card = await card_repo.get_by_id(card_id, tenant_id)
        
        if not card:
            raise HTTPException(status_code=404, detail="Card not found")
        
        # Get relationships
        rel_repo = CardRelationshipRepository(session)
        relationships = await rel_repo.get_by_source_card(card_id)
        
        return [
            RelationshipResponseSchema(
                id=rel.id,
                source_card_id=rel.source_card_id,
                target_card_id=rel.target_card_id,
                relationship_type=rel.relationship_type,
                strength=rel.strength,
                created_at=rel.created_at,
            )
            for rel in relationships
        ]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete(
    "/{source_card_id}/relationships/{target_card_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_relationship(
    source_card_id: UUID,
    target_card_id: UUID,
    tenant_id: UUID = Query(..., description="Tenant ID"),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    """
    Delete a relationship between two cards.
    """
    
    try:
        # Verify cards exist and belong to tenant
        card_repo = CardRepository(session)
        source = await card_repo.get_by_id(source_card_id, tenant_id)
        target = await card_repo.get_by_id(target_card_id, tenant_id)
        
        if not source or not target:
            raise HTTPException(status_code=404, detail="One or both cards not found")
        
        # Delete relationship
        rel_repo = CardRelationshipRepository(session)
        success = await rel_repo.delete_by_cards(source_card_id, target_card_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Relationship not found")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

