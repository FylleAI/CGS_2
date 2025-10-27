"""
Cards API - FastAPI Application.

Provides card management endpoints with multi-tenant isolation,
idempotency, and performance monitoring.
"""

import logging
import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

from .v1.endpoints import cards_router, init_cards_endpoints
from ..infrastructure.database.connection import DatabaseConnection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    "cards_api_requests_total",
    "Total number of requests",
    ["method", "endpoint", "status"],
)

REQUEST_DURATION = Histogram(
    "cards_api_request_duration_seconds",
    "Request duration in seconds",
    ["method", "endpoint"],
)

CARD_OPERATIONS = Counter(
    "cards_api_operations_total",
    "Total number of card operations",
    ["operation", "status"],
)

# Global database connection
db_connection: DatabaseConnection = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown.
    
    Handles database connection initialization and cleanup.
    """
    global db_connection
    
    # Startup
    logger.info("🚀 Starting Cards API...")
    
    # Initialize database connection
    database_url = os.getenv("SUPABASE_DATABASE_URL")
    if not database_url:
        logger.error("❌ SUPABASE_DATABASE_URL not set")
        raise RuntimeError("SUPABASE_DATABASE_URL environment variable is required")
    
    # Remove asyncpg+ prefix if present
    if database_url.startswith("postgresql+asyncpg://"):
        database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    
    logger.info(f"📍 Connecting to database: {database_url.split('@')[1]}")
    
    db_connection = DatabaseConnection(database_url, min_size=5, max_size=20)
    await db_connection.connect()
    
    logger.info("✅ Database connection established")
    
    # Initialize endpoints with database
    init_cards_endpoints(db_connection)
    
    logger.info("✅ Cards API started successfully")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Cards API...")
    
    if db_connection:
        await db_connection.disconnect()
        logger.info("✅ Database connection closed")
    
    logger.info("✅ Cards API shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Cards API",
    description="Card management API with multi-tenant isolation and idempotency",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware for request tracking and metrics
@app.middleware("http")
async def track_requests(request: Request, call_next):
    """Track request metrics and duration."""
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Extract endpoint path (remove query params)
    endpoint = request.url.path
    method = request.method
    status = response.status_code
    
    # Update metrics
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
    REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
    
    # Add custom headers
    response.headers["X-Request-Duration-Ms"] = str(int(duration * 1000))
    
    return response


# Health check endpoints
@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns 200 if the service is running.
    """
    return {
        "status": "healthy",
        "service": "cards-api",
        "version": "1.0.0",
    }


@app.get("/ready")
async def readiness_check():
    """
    Readiness check endpoint.
    
    Returns 200 if the service is ready to accept requests.
    Checks database connectivity.
    """
    global db_connection
    
    if not db_connection or not db_connection._pool:
        return Response(
            content='{"status": "not_ready", "reason": "database_not_connected"}',
            status_code=503,
            media_type="application/json",
        )
    
    try:
        # Test database connection
        async with db_connection.acquire() as conn:
            await conn.fetchval("SELECT 1")
        
        return {
            "status": "ready",
            "service": "cards-api",
            "database": "connected",
        }
    except Exception as e:
        logger.error(f"❌ Readiness check failed: {e}")
        return Response(
            content=f'{{"status": "not_ready", "reason": "database_error", "error": "{str(e)}"}}',
            status_code=503,
            media_type="application/json",
        )


@app.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint.
    
    Returns metrics in Prometheus format.
    """
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


# Include routers
app.include_router(
    cards_router,
    prefix="/api/v1/cards",
    tags=["cards"],
)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "cards-api",
        "version": "1.0.0",
        "description": "Card management API with multi-tenant isolation",
        "endpoints": {
            "health": "/health",
            "ready": "/ready",
            "metrics": "/metrics",
            "batch_create": "POST /api/v1/cards/batch",
            "retrieve": "POST /api/v1/cards/retrieve",
        },
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "cards.api.main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info",
    )

