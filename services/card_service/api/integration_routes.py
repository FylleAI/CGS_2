"""
Card Service API - Integration Routes
Routes for Onboarding and CGS Core Engine integration
"""

import logging
from typing import Dict, List, Optional
from uuid import UUID
import hashlib

from fastapi import APIRouter, Depends, HTTPException, Query, status

from services.card_service.api.card_schemas import CardResponseSchema
from services.card_service.application.create_cards_from_snapshot_use_case import (
    CreateCardsFromSnapshotUseCase,
)
from services.card_service.application.get_cards_for_context_use_case import (
    GetCardsForContextUseCase,
)
from services.card_service.infrastructure.supabase_card_repository import SupabaseCardRepository
from services.card_service.api.dependencies import get_card_repository

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/cards", tags=["cards-integration"])


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
# Onboarding Integration
# ============================================================================


@router.post(
    "/onboarding/create-from-snapshot",
    response_model=List[CardResponseSchema],
    status_code=status.HTTP_201_CREATED,
)
async def create_cards_from_snapshot(
    tenant_id: str = Query(..., description="Tenant ID (email or UUID)"),
    snapshot: dict = None,
    repo: SupabaseCardRepository = Depends(get_card_repository),
) -> List[CardResponseSchema]:
    """
    Create 4 atomic cards from CompanySnapshot.

    Called by Onboarding Microservice after completing the onboarding flow.

    tenant_id can be:
    - Email address (e.g., user@example.com)
    - UUID (e.g., 550e8400-e29b-41d4-a716-446655440000)
    - 'admin' for super admin mode

    Expected snapshot structure:
    {
        "company_info": {
            "company_name": str,
            "value_proposition": str,
            "features": [str],
            "differentiators": [str],
            "use_cases": [str],
            "target_market": str,
            "conversion_rate": float (optional),
            "avg_deal_size": float (optional)
        },
        "audience_info": {
            "persona_name": str,
            "icp_profile": str,
            "pain_points": [str],
            "goals": [str],
            "preferred_language": str,
            "communication_channels": [str],
            "demographics": dict (optional),
            "psychographics": dict (optional)
        },
        "goal": {
            "campaign_name": str,
            "objective": str,
            "key_messages": [str],
            "tone": str,
            "assets_produced": [str],
            "reach": float (optional),
            "conversions": float (optional),
            "roi": float (optional)
        },
        "insights": {
            "topic_name": str,
            "keywords": [str],
            "angles": [str],
            "related_content": [str],
            "trend_status": str,
            "frequency": str,
            "audience_interest": str,
            "search_volume": float (optional),
            "trend_score": float (optional)
        }
    }
    """

    try:
        # Normalize tenant_id
        normalized_tenant_id = normalize_tenant_id(tenant_id)
        logger.info(f"Creating cards from snapshot for tenant: {normalized_tenant_id}")

        use_case = CreateCardsFromSnapshotUseCase(repo)
        cards = await use_case.execute(normalized_tenant_id, snapshot)

        logger.info(f"✅ Created {len(cards)} cards for tenant: {normalized_tenant_id}")

        return [
            CardResponseSchema(
                id=card.id,
                tenant_id=card.tenant_id,
                card_type=card.card_type,
                title=card.title,
                content=card.content,
                metrics=card.metrics or {},
                notes=card.notes or "",
                version=card.version or 1,
                is_active=card.is_active if card.is_active is not None else True,
                created_by=card.created_by,
                updated_by=None,
                created_at=card.created_at,
                updated_at=card.updated_at,
            )
            for card in cards
        ]

    except ValueError as e:
        logger.error(f"ValueError: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Error creating cards: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ============================================================================
# CGS Core Engine Integration
# ============================================================================


@router.get("/context/all")
async def get_all_cards_for_context(
    tenant_id: str = Query(..., description="Tenant ID (email or UUID)"),
    repo: SupabaseCardRepository = Depends(get_card_repository),
) -> Dict[str, List[CardResponseSchema]]:
    """
    Get all cards for a tenant organized by type.

    Called by CGS Core Engine to retrieve cards as RAG context.

    tenant_id can be:
    - Email address (e.g., user@example.com)
    - UUID (e.g., 550e8400-e29b-41d4-a716-446655440000)
    - 'admin' for super admin mode

    Returns:
    {
        "product": [ProductCard, ...],
        "persona": [PersonaCard, ...],
        "campaign": [CampaignCard, ...],
        "topic": [TopicCard, ...]
    }
    """

    try:
        # Normalize tenant_id
        normalized_tenant_id = normalize_tenant_id(tenant_id)

        use_case = GetCardsForContextUseCase(repo)
        cards_dict = await use_case.execute(normalized_tenant_id)

        result = {}
        for card_type, cards in cards_dict.items():
            result[card_type] = [
                CardResponseSchema(
                    id=card.id,
                    tenant_id=card.tenant_id,
                    card_type=card.card_type,
                    title=card.title,
                    content=card.content,
                    metrics=card.metrics or {},
                    notes=card.notes or "",
                    version=card.version or 1,
                    is_active=card.is_active if card.is_active is not None else True,
                    created_by=card.created_by,
                    updated_by=None,
                    created_at=card.created_at,
                    updated_at=card.updated_at,
                    relationships=[],
                )
                for card in cards
            ]

        return result

    except Exception as e:
        logger.error(f"❌ Error getting cards for context: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/context/rag-text")
async def get_rag_context_text(
    tenant_id: str = Query(..., description="Tenant ID (email or UUID)"),
    repo: SupabaseCardRepository = Depends(get_card_repository),
) -> Dict[str, str]:
    """
    Get all cards formatted as RAG context text for LLM.

    Called by CGS Core Engine to get formatted context for content generation.

    tenant_id can be:
    - Email address (e.g., user@example.com)
    - UUID (e.g., 550e8400-e29b-41d4-a716-446655440000)
    - 'admin' for super admin mode

    Returns:
    {
        "context": "Formatted text with all card information"
    }
    """

    try:
        # Normalize tenant_id
        normalized_tenant_id = normalize_tenant_id(tenant_id)

        use_case = GetCardsForContextUseCase(repo)
        context_text = await use_case.get_as_rag_context(normalized_tenant_id)

        return {"context": context_text}

    except Exception as e:
        logger.error(f"❌ Error getting RAG context: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/context/by-type")
async def get_cards_by_type(
    tenant_id: str = Query(..., description="Tenant ID (email or UUID)"),
    card_types: Optional[List[str]] = Query(
        None, description="Card types to retrieve (product, persona, campaign, topic)"
    ),
    repo: SupabaseCardRepository = Depends(get_card_repository),
) -> Dict[str, List[CardResponseSchema]]:
    """
    Get cards for specific types.

    Called by CGS Core Engine to retrieve specific card types.

    tenant_id can be:
    - Email address (e.g., user@example.com)
    - UUID (e.g., 550e8400-e29b-41d4-a716-446655440000)
    - 'admin' for super admin mode
    """

    try:
        # Normalize tenant_id
        normalized_tenant_id = normalize_tenant_id(tenant_id)

        use_case = GetCardsForContextUseCase(repo)
        cards_dict = await use_case.execute(normalized_tenant_id, card_types)

        result = {}
        for card_type, cards in cards_dict.items():
            result[card_type] = [
                CardResponseSchema(
                    id=card.id,
                    tenant_id=card.tenant_id,
                    card_type=card.card_type,
                    title=card.title,
                    content=card.content,
                    metrics=card.metrics or {},
                    notes=card.notes or "",
                    version=card.version or 1,
                    is_active=card.is_active if card.is_active is not None else True,
                    created_by=card.created_by,
                    updated_by=None,
                    created_at=card.created_at,
                    updated_at=card.updated_at,
                    relationships=[],
                )
                for card in cards
            ]

        return result

    except ValueError as e:
        logger.error(f"ValueError: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Error getting cards by type: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

