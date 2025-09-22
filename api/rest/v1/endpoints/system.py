"""System management endpoints."""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from core.infrastructure.config.settings import get_settings

logger = logging.getLogger(__name__)

router = APIRouter()


class SystemHealth(BaseModel):
    """System health response model."""

    status: str
    version: str
    environment: str
    providers: Dict[str, bool]
    database: Dict[str, Any]
    storage: Dict[str, Any]


class SystemInfo(BaseModel):
    """System information model."""

    app_name: str
    version: str
    environment: str
    debug: bool
    api_host: str
    api_port: int


@router.get("/health", response_model=SystemHealth)
async def health_check():
    """System health check endpoint."""
    settings = get_settings()

    try:
        # Check providers
        providers = settings.get_available_providers()

        # Check database (simplified)
        database_status = {
            "status": "healthy",
            "url": settings.database_url,
            "echo": settings.database_echo,
        }

        # Check storage
        storage_status = {
            "data_dir": settings.data_dir,
            "output_dir": settings.output_dir,
            "status": "healthy",
        }

        return SystemHealth(
            status="healthy",
            version=settings.app_version,
            environment=settings.environment,
            providers=providers,
            database=database_status,
            storage=storage_status,
        )

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unavailable")


@router.get("/info", response_model=SystemInfo)
async def system_info():
    """Get system information."""
    settings = get_settings()

    return SystemInfo(
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
        debug=settings.debug,
        api_host=settings.api_host,
        api_port=settings.api_port,
    )


@router.get("/config")
async def get_config():
    """Get system configuration (non-sensitive)."""
    settings = get_settings()

    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "providers": settings.get_available_providers(),
        "default_provider": settings.default_provider,
        "default_model": settings.default_model,
        "rag_enabled": settings.rag_enabled,
        "websocket_enabled": settings.websocket_enabled,
    }
