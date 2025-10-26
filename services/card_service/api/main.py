"""
Card Service API - FastAPI Application
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.card_service.api.card_routes import router as card_router
from services.card_service.api.integration_routes import router as integration_router

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Card Service API",
    description="Microservice for managing cards and relationships",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(card_router)
app.include_router(integration_router)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "card-service",
        "version": "1.0.0",
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Card Service API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8001,
        reload=True,
    )

