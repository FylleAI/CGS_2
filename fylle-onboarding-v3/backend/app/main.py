"""
Fylle Onboarding v3 - Main FastAPI Application
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import get_settings
from app.api.routes import (
    auth_router,
    onboarding_router,
    cards_router,
    packs_router,
    briefs_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    settings = get_settings()
    print(f"🚀 Fylle Onboarding v3 starting on {settings.api_host}:{settings.api_port}")
    print(f"📊 Debug mode: {settings.debug}")
    print(f"🔌 Default LLM: {settings.default_llm_provider}")
    
    yield
    
    # Shutdown
    print("👋 Fylle Onboarding v3 shutting down")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title="Fylle Onboarding v3",
        description="Modular onboarding microservice for content generation",
        version="3.0.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(onboarding_router, prefix="/api/v1")
    app.include_router(cards_router, prefix="/api/v1")
    app.include_router(packs_router, prefix="/api/v1")
    app.include_router(briefs_router, prefix="/api/v1")
    
    # Health check
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "service": "fylle-onboarding-v3",
            "version": "3.0.0",
        }
    
    @app.get("/")
    async def root():
        return {
            "service": "Fylle Onboarding v3",
            "version": "3.0.0",
            "docs": "/docs" if settings.debug else "disabled",
        }
    
    return app


# Create application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
