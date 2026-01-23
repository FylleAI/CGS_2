"""
Packs Routes for Fylle Onboarding v3
Pack listing and management endpoints.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_pack_repository
from app.infrastructure.repositories import PackRepository
from app.domain.entities import PackResponse


router = APIRouter(prefix="/packs", tags=["packs"])


@router.get("", response_model=List[PackResponse])
async def get_all_packs(
    pack_repo: PackRepository = Depends(get_pack_repository),
):
    """Get all available packs."""
    packs = await pack_repo.get_all(active_only=True)
    return [PackResponse.from_entity(p) for p in packs]


@router.get("/{pack_id}", response_model=PackResponse)
async def get_pack(
    pack_id: str,
    pack_repo: PackRepository = Depends(get_pack_repository),
):
    """Get a specific pack by ID."""
    pack = await pack_repo.get(pack_id)
    
    if not pack:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pack non trovato",
        )
    
    return PackResponse.from_entity(pack)


@router.get("/name/{pack_name}", response_model=PackResponse)
async def get_pack_by_name(
    pack_name: str,
    pack_repo: PackRepository = Depends(get_pack_repository),
):
    """Get a pack by name."""
    pack = await pack_repo.get_by_name(pack_name)
    
    if not pack:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pack non trovato",
        )
    
    return PackResponse.from_entity(pack)
