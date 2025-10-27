#!/usr/bin/env python3
"""
⚠️ DEPRECATED: Mock Cards API server for testing workflow integration.

**STATUS**: DEPRECATED - Use real Cards API instead (cards/api/main.py)

**DEPRECATION NOTICE**:
- This mock is deprecated as of Sprint 3 Day 2 (2025-10-27)
- Use the real Cards API: ./scripts/start_cards_api.sh
- Real API provides: database persistence, idempotency, RLS, metrics
- This mock will be removed in Sprint 4

**Migration Guide**:
1. Start real Cards API: ./scripts/start_cards_api.sh
2. Update tests to use real API (port 8002)
3. Create cards via POST /api/v1/cards/batch
4. Retrieve cards via POST /api/v1/cards/retrieve

Provides a simple HTTP server that responds to card retrieval requests
with mock card data (IN-MEMORY ONLY - NOT PERSISTENT).
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List
from uuid import uuid4

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Mock Cards API", version="1.0.0")


# Models
class RetrieveCardsRequest(BaseModel):
    """Request to retrieve multiple cards by ID."""

    card_ids: List[str] = Field(..., description="List of card IDs to retrieve")


class CreateCardRequest(BaseModel):
    """Request to create a single card."""

    tenant_id: str
    card_type: str
    title: str
    description: str = ""
    content: Dict[str, Any]
    tags: List[str] = Field(default_factory=list)
    source_session_id: str = None
    created_by: str = "onboarding-api"


class ContextCard(BaseModel):
    """Context card response."""

    card_id: str  # Changed from 'id' to 'card_id' to match client expectations
    tenant_id: str
    card_type: str
    title: str
    description: str
    content: Dict[str, Any]
    tags: List[str] = Field(default_factory=list)
    is_active: bool = True
    created_at: str
    updated_at: str
    created_by: str


class RetrieveCardsResponse(BaseModel):
    """Response for card retrieval."""

    cards: List[ContextCard]
    total: int
    retrieved: int
    missing_ids: List[str] = Field(default_factory=list)


# Mock card database (using valid UUIDs)
MOCK_CARDS: Dict[str, ContextCard] = {}

# Idempotency storage: {idempotency_key: response_payload}
IDEMPOTENCY_STORE: Dict[str, Dict[str, Any]] = {}

# Initialize with mock cards
_INITIAL_MOCK_CARDS: Dict[str, ContextCard] = {
    "550e8400-e29b-41d4-a716-446655440001": ContextCard(
        card_id="550e8400-e29b-41d4-a716-446655440001",
        tenant_id="123e4567-e89b-12d3-a456-426614174000",
        card_type="company",
        title="Fylle AI",
        description="AI-powered content generation platform",
        content={
            "name": "Fylle AI",
            "domain": "fylle.ai",
            "industry": "Artificial Intelligence",
            "description": "Fylle AI is a cutting-edge content generation platform that leverages advanced AI to create high-quality, personalized content for businesses.",
            "founded": "2023",
            "size": "11-50 employees",
            "headquarters": "San Francisco, CA",
        },
        tags=["AI", "Content Generation", "SaaS"],
        is_active=True,
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat(),
        created_by="onboarding-service",
    ),
    "550e8400-e29b-41d4-a716-446655440002": ContextCard(
        card_id="550e8400-e29b-41d4-a716-446655440002",
        tenant_id="123e4567-e89b-12d3-a456-426614174000",
        card_type="audience",
        title="Tech Decision Makers",
        description="C-level executives and VPs in technology companies",
        content={
            "name": "Tech Decision Makers",
            "description": "C-level executives, VPs, and senior directors at technology companies who make strategic decisions about AI adoption and content strategy.",
            "demographics": {
                "age_range": "35-55",
                "job_titles": ["CTO", "VP Engineering", "Head of Product", "CMO"],
                "industries": ["SaaS", "Enterprise Software", "AI/ML"],
            },
            "pain_points": [
                "Need to stay ahead of AI trends",
                "Pressure to adopt AI while managing risks",
                "Balancing innovation with operational efficiency",
            ],
            "goals": [
                "Drive digital transformation",
                "Improve operational efficiency",
                "Maintain competitive advantage",
            ],
        },
        tags=["B2B", "Enterprise", "Decision Makers"],
        is_active=True,
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat(),
        created_by="onboarding-service",
    ),
    "550e8400-e29b-41d4-a716-446655440003": ContextCard(
        card_id="550e8400-e29b-41d4-a716-446655440003",
        tenant_id="123e4567-e89b-12d3-a456-426614174000",
        card_type="voice",
        title="Professional & Insightful",
        description="Authoritative yet accessible tone for tech executives",
        content={
            "name": "Professional & Insightful",
            "tone": "Professional, authoritative, yet accessible",
            "style": "Data-driven insights with clear actionable recommendations",
            "vocabulary": "Industry-specific terminology balanced with clarity",
            "sentence_structure": "Mix of concise statements and detailed explanations",
            "guidelines": [
                "Use data and statistics to support claims",
                "Provide actionable insights, not just information",
                "Balance technical depth with accessibility",
                "Cite credible sources (TechCrunch, VentureBeat, etc.)",
                "Focus on business impact, not just technology",
            ],
            "examples": [
                "According to TechCrunch, AI adoption has increased 42% YoY...",
                "Tech executives should prioritize...",
                "The data shows a clear trend toward...",
            ],
        },
        tags=["Professional", "B2B", "Executive"],
        is_active=True,
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat(),
        created_by="onboarding-service",
    ),
    "550e8400-e29b-41d4-a716-446655440004": ContextCard(
        card_id="550e8400-e29b-41d4-a716-446655440004",
        tenant_id="123e4567-e89b-12d3-a456-426614174000",
        card_type="insight",
        title="AI Market Trends Q4 2024",
        description="Latest insights on AI adoption and market dynamics",
        content={
            "title": "AI Market Trends Q4 2024",
            "summary": "AI adoption accelerating across industries with focus on practical applications and ROI",
            "key_insights": [
                "Enterprise AI spending up 67% YoY",
                "Focus shifting from experimentation to production deployment",
                "Ethical AI and governance becoming critical priorities",
                "AI-powered automation driving 30% efficiency gains",
            ],
            "sources": [
                "TechCrunch AI Report Q4 2024",
                "Gartner AI Adoption Survey 2024",
                "McKinsey AI Index 2024",
            ],
            "relevance": "Directly applicable to tech executives planning AI strategy",
        },
        tags=["AI", "Market Trends", "2024"],
        is_active=True,
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat(),
        created_by="analytics-service",
    ),
}

# Copy initial mocks to MOCK_CARDS
MOCK_CARDS.update(_INITIAL_MOCK_CARDS)


# Batch creation models
class CreateCardsBatchRequest(BaseModel):
    """Request to create multiple cards from CompanySnapshot."""

    tenant_id: str
    company_snapshot: Dict[str, Any]
    source_session_id: str
    created_by: str = "onboarding-api"


class CardBatchResponse(BaseModel):
    """Response from batch card creation."""

    cards: List[ContextCard]
    created_count: int


@app.post("/api/v1/cards/batch", response_model=CardBatchResponse, status_code=201)
async def create_cards_batch(
    request: CreateCardsBatchRequest,
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
    x_trace_id: str = Header(None, alias="X-Trace-ID"),
    idempotency_key: str = Header(None, alias="Idempotency-Key"),
) -> CardBatchResponse:
    """
    Create multiple cards from CompanySnapshot (idempotent).

    If Idempotency-Key is provided and matches a previous request,
    returns the same cards without creating duplicates.
    """
    logger.info(f"📦 Batch card creation request (idempotency_key={idempotency_key})")

    # Check idempotency
    if idempotency_key and idempotency_key in IDEMPOTENCY_STORE:
        logger.info(f"♻️  Idempotent replay detected - returning cached response")
        cached = IDEMPOTENCY_STORE[idempotency_key]
        return CardBatchResponse(**cached)

    # Extract snapshot sections
    snapshot = request.company_snapshot
    company = snapshot.get("company", {})
    audience = snapshot.get("audience", {})
    voice = snapshot.get("voice", {})
    insights = snapshot.get("insights", {})

    # Create 4 atomic cards
    cards = []

    # 1. Company Card
    company_card = ContextCard(
        card_id=str(uuid4()),
        tenant_id=request.tenant_id,
        card_type="company",
        title=company.get("name", "Company Profile"),
        description=company.get("description", ""),
        content=company,
        tags=["company", "profile"],
        is_active=True,
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat(),
        created_by=request.created_by,
    )
    MOCK_CARDS[company_card.card_id] = company_card
    cards.append(company_card)
    logger.info(f"✅ Created company card: {company_card.card_id}")

    # 2. Audience Card
    audience_card = ContextCard(
        card_id=str(uuid4()),
        tenant_id=request.tenant_id,
        card_type="audience",
        title=audience.get("primary", "Target Audience"),
        description=f"Primary audience: {audience.get('primary', 'N/A')}",
        content=audience,
        tags=["audience", "targeting"],
        is_active=True,
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat(),
        created_by=request.created_by,
    )
    MOCK_CARDS[audience_card.card_id] = audience_card
    cards.append(audience_card)
    logger.info(f"✅ Created audience card: {audience_card.card_id}")

    # 3. Voice Card
    voice_card = ContextCard(
        card_id=str(uuid4()),
        tenant_id=request.tenant_id,
        card_type="voice",
        title=f"Brand Voice: {voice.get('tone', 'Professional')}",
        description=f"Tone: {voice.get('tone', 'N/A')}",
        content=voice,
        tags=["voice", "tone", "style"],
        is_active=True,
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat(),
        created_by=request.created_by,
    )
    MOCK_CARDS[voice_card.card_id] = voice_card
    cards.append(voice_card)
    logger.info(f"✅ Created voice card: {voice_card.card_id}")

    # 4. Insight Card
    insight_card = ContextCard(
        card_id=str(uuid4()),
        tenant_id=request.tenant_id,
        card_type="insight",
        title="Market Insights",
        description="Key market insights and positioning",
        content=insights,
        tags=["insights", "market", "positioning"],
        is_active=True,
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat(),
        created_by=request.created_by,
    )
    MOCK_CARDS[insight_card.card_id] = insight_card
    cards.append(insight_card)
    logger.info(f"✅ Created insight card: {insight_card.card_id}")

    # Build response
    response = CardBatchResponse(
        cards=cards,
        created_count=len(cards),
    )

    # Store for idempotency
    if idempotency_key:
        IDEMPOTENCY_STORE[idempotency_key] = response.model_dump()
        logger.info(f"💾 Stored response for idempotency key: {idempotency_key}")

    logger.info(f"🎉 Batch creation complete: {len(cards)} cards created")
    return response


@app.post("/api/v1/cards/retrieve", response_model=RetrieveCardsResponse)
async def retrieve_cards(
    request: RetrieveCardsRequest,
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
    x_trace_id: str = Header(None, alias="X-Trace-ID"),
) -> RetrieveCardsResponse:
    """
    Retrieve multiple cards by ID.
    
    Mock implementation that returns predefined cards.
    """
    logger.info(
        f"📥 Card retrieval request: {len(request.card_ids)} cards",
        extra={
            "tenant_id": x_tenant_id,
            "trace_id": x_trace_id,
            "card_ids": request.card_ids,
        },
    )

    retrieved_cards: List[ContextCard] = []
    missing_ids: List[str] = []

    for card_id in request.card_ids:
        if card_id in MOCK_CARDS:
            card = MOCK_CARDS[card_id]
            # Verify tenant_id matches
            if card.tenant_id == x_tenant_id:
                retrieved_cards.append(card)
                logger.info(f"✅ Retrieved card: {card_id} ({card.card_type})")
            else:
                logger.warning(f"⚠️ Tenant mismatch for card: {card_id}")
                missing_ids.append(card_id)
        else:
            logger.warning(f"❌ Card not found: {card_id}")
            missing_ids.append(card_id)

    response = RetrieveCardsResponse(
        cards=retrieved_cards,
        total=len(request.card_ids),
        retrieved=len(retrieved_cards),
        missing_ids=missing_ids,
    )

    logger.info(
        f"📤 Card retrieval response: {response.retrieved}/{response.total} cards",
        extra={
            "tenant_id": x_tenant_id,
            "trace_id": x_trace_id,
            "retrieved": response.retrieved,
            "missing": len(response.missing_ids),
        },
    )

    return response


@app.post("/api/v1/cards")
async def create_card(
    request: CreateCardRequest,
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
    x_trace_id: str = Header(None, alias="X-Trace-ID"),
):
    """Create a single card (mock implementation)."""
    logger.info(
        f"📝 Card creation request: {request.card_type}",
        extra={
            "tenant_id": x_tenant_id,
            "trace_id": x_trace_id,
            "card_type": request.card_type,
            "title": request.title,
        },
    )

    # Generate card ID
    card_id = str(uuid4())

    # Create card
    card = ContextCard(
        card_id=card_id,
        tenant_id=request.tenant_id,
        card_type=request.card_type,
        title=request.title,
        description=request.description,
        content=request.content,
        tags=request.tags,
        is_active=True,
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat(),
        created_by=request.created_by,
    )

    # Store in mock database
    MOCK_CARDS[card_id] = card

    logger.info(
        f"✅ Card created: {card_id} ({request.card_type})",
        extra={
            "tenant_id": x_tenant_id,
            "trace_id": x_trace_id,
            "card_id": card_id,
        },
    )

    return card.model_dump()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "mock-cards-api",
        "version": "1.0.0",
        "cards_available": len(MOCK_CARDS),
    }


if __name__ == "__main__":
    import uvicorn

    logger.warning("=" * 80)
    logger.warning("⚠️  DEPRECATION WARNING: Mock Cards API")
    logger.warning("=" * 80)
    logger.warning("This mock is DEPRECATED as of Sprint 3 Day 2 (2025-10-27)")
    logger.warning("")
    logger.warning("Please use the REAL Cards API instead:")
    logger.warning("  Start: ./scripts/start_cards_api.sh")
    logger.warning("  Port: 8002")
    logger.warning("  Features: Database persistence, idempotency, RLS, metrics")
    logger.warning("")
    logger.warning("This mock will be REMOVED in Sprint 4")
    logger.warning("=" * 80)
    logger.warning("")

    logger.info("🚀 Starting Mock Cards API server (DEPRECATED)...")
    logger.info(f"📦 Mock cards available: {len(MOCK_CARDS)}")
    for card_id, card in MOCK_CARDS.items():
        logger.info(f"  - {card_id}: {card.card_type} - {card.title}")

    uvicorn.run(app, host="0.0.0.0", port=8002, log_level="info")

