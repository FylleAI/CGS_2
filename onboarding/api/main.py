"""FastAPI application for onboarding service."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from onboarding.config.settings import get_onboarding_settings
from onboarding.api.endpoints import router as onboarding_router
from onboarding.api.models import HealthCheckResponse
from onboarding.api.dependencies import get_cgs_adapter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""
    # Startup
    settings = get_onboarding_settings()
    logger.info(f"Starting {settings.service_name} v{settings.service_version}")
    
    # Validate services
    services = settings.validate_required_services()
    for service, configured in services.items():
        status_icon = "✅" if configured else "⚠️"
        logger.info(f"  {status_icon} {service.capitalize()}: {'configured' if configured else 'not configured'}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down onboarding service")


# Create FastAPI app
app = FastAPI(
    title="Onboarding Service",
    description="Automated client onboarding with AI-powered research and content generation",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware - configurable via environment
_settings = get_onboarding_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=_settings.cors_origins,
    allow_credentials=_settings.cors_allow_credentials,
    allow_methods=_settings.cors_allow_methods,
    allow_headers=_settings.cors_allow_headers,
)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": str(exc),
        },
    )


# Health check endpoint
@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint."""
    settings = get_onboarding_settings()
    services = settings.validate_required_services()
    
    # Check CGS health
    cgs_healthy = False
    try:
        cgs = get_cgs_adapter()
        cgs_healthy = await cgs.health_check()
    except Exception as e:
        logger.warning(f"CGS health check failed: {str(e)}")
    
    return HealthCheckResponse(
        status="healthy",
        version=settings.service_version,
        services=services,
        cgs_healthy=cgs_healthy,
    )


@app.get("/")
async def root():
    """Root endpoint."""
    settings = get_onboarding_settings()
    return {
        "service": settings.service_name,
        "version": settings.service_version,
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }


# Include routers
app.include_router(onboarding_router)


# Run with: uvicorn onboarding.api.main:app --reload --port 8001
if __name__ == "__main__":
    import uvicorn
    
    settings = get_onboarding_settings()
    uvicorn.run(
        "onboarding.api.main:app",
        host=settings.onboarding_api_host,
        port=settings.onboarding_api_port,
        reload=True,
        log_level=settings.log_level.lower(),
    )

