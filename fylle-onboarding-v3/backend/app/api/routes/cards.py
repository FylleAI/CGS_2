"""
Cards Routes for Fylle Onboarding v3
Card CRUD endpoints.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from app.api.dependencies import get_card_repository
from app.infrastructure.repositories import CardRepository
from app.domain.entities import CardResponse, CardsSnapshot


router = APIRouter(prefix="/cards", tags=["cards"])


class UpdateCardRequest(BaseModel):
    """Request to update a card."""
    title: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


@router.get("", response_model=CardsSnapshot)
async def get_user_cards(
    user_id: str = Query(..., description="User ID"),
    card_type: Optional[str] = Query(None, description="Filter by card type"),
    card_repo: CardRepository = Depends(get_card_repository),
):
    """Get all cards for a user."""
    cards = await card_repo.get_by_user(user_id, card_type)
    
    return CardsSnapshot.from_cards(user_id, cards)


@router.get("/{card_id}", response_model=CardResponse)
async def get_card(
    card_id: str,
    card_repo: CardRepository = Depends(get_card_repository),
):
    """Get a specific card by ID."""
    card = await card_repo.get(card_id)
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card non trovata",
        )
    
    return CardResponse.from_entity(card)


@router.put("/{card_id}", response_model=CardResponse)
async def update_card(
    card_id: str,
    request: UpdateCardRequest,
    card_repo: CardRepository = Depends(get_card_repository),
):
    """Update a card."""
    card = await card_repo.update(
        card_id=card_id,
        title=request.title,
        data=request.data,
    )
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card non trovata",
        )
    
    return CardResponse.from_entity(card)


@router.delete("/{card_id}")
async def delete_card(
    card_id: str,
    card_repo: CardRepository = Depends(get_card_repository),
):
    """Delete a card."""
    success = await card_repo.delete(card_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card non trovata",
        )
    
    return {"message": "Card eliminata con successo"}
