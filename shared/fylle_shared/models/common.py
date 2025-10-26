"""
Fylle Shared Common Models

Common models used across microservices.
"""

from typing import Optional

from pydantic import BaseModel, Field


class Pagination(BaseModel):
    """
    Pagination metadata for list responses.
    """
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    total: int = Field(ge=0)

    class Config:
        json_schema_extra = {
            "example": {
                "page": 1,
                "page_size": 20,
                "total": 150
            }
        }


class ErrorResponse(BaseModel):
    """
    Standard error response format.
    """
    error: str
    detail: Optional[str] = None
    request_id: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "detail": "Invalid card_type: must be one of [company, audience, voice, insight]",
                "request_id": "req-abc123"
            }
        }


class IdempotencyKey(BaseModel):
    """
    Idempotency key for safe retries.
    """
    value: str = Field(min_length=1, max_length=255)

    class Config:
        json_schema_extra = {
            "example": {
                "value": "onboarding-123e4567-batch"
            }
        }

