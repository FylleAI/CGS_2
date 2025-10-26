"""
Fylle Cards API Client v1.0.0

Auto-generated Python client for Fylle Cards API.
Based on OpenAPI spec: contracts/cards-api-v1.yaml

Usage:
    from fylle_cards_client import CardsClient, ContextCard, CardType
    
    client = CardsClient(
        base_url="http://localhost:8002",
        tenant_id="123e4567-e89b-12d3-a456-426614174000"
    )
    
    # Create a card
    card = client.create_card(
        card_type=CardType.COMPANY,
        title="Acme Corp",
        content={"name": "Acme Corp", "industry": "SaaS"},
        created_by="onboarding-service"
    )
    
    # Retrieve cards for workflow
    cards = client.retrieve_cards(
        card_ids=["789e0123-e89b-12d3-a456-426614174002"]
    )
"""

from fylle_cards_client.client import CardsClient
from fylle_cards_client.models import (
    CardBatchResponse,
    CardListResponse,
    CardType,
    ContextCard,
    CreateCardRequest,
    CreateCardsBatchRequest,
    RetrieveCardsRequest,
    TrackUsageRequest,
)

__version__ = "1.0.0"
__all__ = [
    "CardsClient",
    "ContextCard",
    "CardType",
    "CreateCardRequest",
    "CreateCardsBatchRequest",
    "CardBatchResponse",
    "CardListResponse",
    "RetrieveCardsRequest",
    "TrackUsageRequest",
]

