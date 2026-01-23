"""
Auth Routes for Fylle Onboarding v3
User registration and authentication endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr

from app.api.dependencies import get_user_repository
from app.infrastructure.repositories import UserRepository
from app.domain.entities import UserResponse


router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    """Request to register a new user."""
    email: EmailStr
    brand_name: str = None
    website: str = None


class RegisterResponse(BaseModel):
    """Response after registration."""
    user_id: str
    email: str
    message: str


@router.post("/register", response_model=RegisterResponse)
async def register_user(
    request: RegisterRequest,
    user_repo: UserRepository = Depends(get_user_repository),
):
    """
    Register a new user by email.
    
    If user already exists, returns existing user ID.
    """
    # Check if user exists
    existing = await user_repo.get_by_email(request.email)
    if existing:
        return RegisterResponse(
            user_id=str(existing.id),
            email=existing.email,
            message="Utente già esistente",
        )
    
    # Create new user
    try:
        user = await user_repo.create(
            email=request.email,
            brand_name=request.brand_name,
            website=request.website,
        )
        
        return RegisterResponse(
            user_id=str(user.id),
            email=user.email,
            message="Utente registrato con successo",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore durante la registrazione: {str(e)}",
        )


@router.get("/user/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    user_repo: UserRepository = Depends(get_user_repository),
):
    """Get user by ID."""
    user = await user_repo.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utente non trovato",
        )
    
    return UserResponse.from_entity(user)
