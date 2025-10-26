"""FastAPI application main module."""

import logging
import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Make .env values visible to os.environ (tools read env directly)
load_dotenv(dotenv_path=Path(".env"), override=False)

from core.infrastructure.config.settings import get_settings
from .v1.endpoints import content, workflows, agents, system, knowledge_base, workflow_v1, metrics, onboarding_v1
from .endpoints import logging as logging_endpoints
from .middleware import LoggingMiddleware
from .exceptions import setup_exception_handlers

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting CGSRef API...")
    settings = get_settings()

    # Ensure Google ADC env vars for Vertex AI are set from Settings
    try:
        if settings.google_application_credentials and not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            cred_path = Path(settings.google_application_credentials).expanduser().resolve()
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(cred_path)
            logger.info("GOOGLE_APPLICATION_CREDENTIALS set from settings")

        if settings.gcp_project_id and not os.getenv("GOOGLE_CLOUD_PROJECT"):
            os.environ["GOOGLE_CLOUD_PROJECT"] = settings.gcp_project_id
        if settings.gcp_location and not os.getenv("GOOGLE_CLOUD_REGION"):
            os.environ["GOOGLE_CLOUD_REGION"] = settings.gcp_location
    except Exception as e:
        logger.warning(f"Failed to set Google ADC env vars: {e}")

    # Validate configuration
    if not settings.has_any_provider():
        logger.warning("No AI providers configured. Some features may not work.")

    # Initialize workflow registry and Cards API URL
    try:
        from core.infrastructure.workflows.registry import workflow_registry

        # Get Cards API URL from environment
        cards_api_url = os.getenv("CARDS_API_URL", "http://localhost:8002/api/v1")
        logger.info(f"✅ Cards API URL configured: {cards_api_url}")

        # Initialize workflow v1 endpoint with dependencies
        workflow_v1.init_workflow_v1(workflow_registry, cards_api_url)
        logger.info("✅ Workflow v1 endpoint initialized")

        # Initialize onboarding v1 endpoint with dependencies
        onboarding_v1.init_onboarding_v1(cards_api_url)
        logger.info("✅ Onboarding v1 endpoint initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize v1 endpoints: {e}", exc_info=True)
        # Continue startup - endpoints will return 500 if not initialized

    yield

    # Shutdown
    logger.info("Shutting down CGSRef API...")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()

    if not settings.debug:
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    app = FastAPI(
        title="CGSRef API",
        description="Clean Content Generation System - REST API",
        version="1.0.0",
        docs_url="/docs" if not settings.is_production() else None,
        redoc_url="/redoc" if not settings.is_production() else None,
        lifespan=lifespan,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add custom middleware
    app.add_middleware(LoggingMiddleware)

    # Setup exception handlers
    setup_exception_handlers(app)

    # Include routers
    app.include_router(content.router, prefix="/api/v1/content", tags=["content"])
    app.include_router(workflows.router, prefix="/api/v1/workflows", tags=["workflows"])
    app.include_router(workflow_v1.router, prefix="/api/v1/workflow", tags=["workflow-v1"])
    app.include_router(onboarding_v1.router, prefix="/api/v1/onboarding", tags=["onboarding-v1"])
    app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
    app.include_router(system.router, prefix="/api/v1/system", tags=["system"])
    app.include_router(knowledge_base.router, prefix="/api/v1", tags=["knowledge-base"])
    app.include_router(logging_endpoints.router, tags=["logging"])
    app.include_router(metrics.router, tags=["metrics"])

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "service": "cgsref-api", "version": "1.0.0"}

    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "message": "CGSRef API",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/health",
        }

    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload and settings.is_development(),
        log_level=settings.log_level.lower(),
    )
