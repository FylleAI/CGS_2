"""FastAPI application main module."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.infrastructure.config.settings import get_settings
from .v1.endpoints import content, workflows, agents, system, knowledge_base
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

    # Validate configuration
    if not settings.has_any_provider():
        logger.warning("No AI providers configured. Some features may not work.")

    # Initialize services here if needed
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
    app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
    app.include_router(system.router, prefix="/api/v1/system", tags=["system"])
    app.include_router(knowledge_base.router, prefix="/api/v1", tags=["knowledge-base"])
    app.include_router(logging_endpoints.router, tags=["logging"])

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
