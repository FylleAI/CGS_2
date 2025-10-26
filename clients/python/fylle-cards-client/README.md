# Fylle Cards API Client

**Version**: 1.0.0

Python client for Fylle Cards API v1.

Auto-generated from OpenAPI spec: `contracts/cards-api-v1.yaml`

## Installation

```bash
pip install fylle-cards-client==1.0.0
```

## Quick Start

```python
from fylle_cards_client import CardsClient, CardType
from uuid import UUID

# Create client
client = CardsClient(
    base_url="http://localhost:8002",
    tenant_id="123e4567-e89b-12d3-a456-426614174000"
)

# Create a single card
card = client.create_card(
    card_type=CardType.COMPANY,
    title="Acme Corp",
    content={
        "name": "Acme Corp",
        "domain": "acme.com",
        "industry": "SaaS"
    },
    created_by="onboarding-service"
)

print(f"Created card: {card.card_id}")
```

## Features

✅ **Type-safe**: Full Pydantic models for all requests and responses  
✅ **Retry logic**: Automatic retry with exponential backoff (429, 5xx)  
✅ **Timeouts**: Configurable connect (200ms) and read (800ms) timeouts  
✅ **Header propagation**: Automatic X-Tenant-ID, X-Trace-ID, X-Session-ID  
✅ **Idempotency**: Support for Idempotency-Key header on mutate endpoints  
✅ **Error handling**: Typed exceptions with error details  

## Usage Examples

### Create Cards from CompanySnapshot (Batch)

```python
from uuid import UUID

# Create multiple cards from onboarding snapshot (idempotent)
response = client.create_cards_batch(
    company_snapshot={
        "company": {
            "name": "Acme Corp",
            "domain": "acme.com",
            "industry": "SaaS"
        },
        "audience": {
            "primary": "Tech executives"
        },
        "voice": {
            "tone": "Professional"
        },
        "insights": {
            "key_differentiators": ["AI-powered"]
        }
    },
    source_session_id=UUID("456e7890-e89b-12d3-a456-426614174001"),
    created_by="onboarding-service",
    idempotency_key="session-456e7890"  # Safe retries
)

print(f"Created {response.created_count} cards")
for card in response.cards:
    print(f"  - {card.card_type}: {card.title}")
```

### Retrieve Cards for Workflow

```python
from uuid import UUID

# Retrieve cards by IDs (best-effort)
cards_response = client.retrieve_cards(
    card_ids=[
        UUID("789e0123-e89b-12d3-a456-426614174002"),
        UUID("789e0123-e89b-12d3-a456-426614174003"),
        UUID("789e0123-e89b-12d3-a456-426614174004"),
    ]
)

print(f"Retrieved {len(cards_response.cards)} cards")
# Note: If some IDs are missing, API returns available cards
# Check response headers for X-Partial-Result: true
```

### List Cards with Filtering

```python
# List all active company cards
cards_response = client.list_cards(
    card_type=CardType.COMPANY,
    is_active=True,
    page=1,
    page_size=20
)

print(f"Total: {cards_response.total} cards")
for card in cards_response.cards:
    print(f"  - {card.title} (usage: {card.usage_count})")
```

### Track Card Usage

```python
from uuid import UUID

# Track when a card is used in a workflow
client.track_usage(
    card_id=UUID("789e0123-e89b-12d3-a456-426614174002"),
    workflow_id=UUID("abc12345-e89b-12d3-a456-426614174003"),
    workflow_type="premium_newsletter",
    metadata={
        "agent_name": "content_generator",
        "context_position": 1
    }
)
```

### Context Manager

```python
# Use context manager for automatic cleanup
with CardsClient(
    base_url="http://localhost:8002",
    tenant_id="123e4567-e89b-12d3-a456-426614174000"
) as client:
    card = client.get_card(UUID("789e0123-e89b-12d3-a456-426614174002"))
    print(card.title)
# Client automatically closed
```

## Configuration

### Timeouts

```python
client = CardsClient(
    base_url="http://localhost:8002",
    tenant_id="123e4567-e89b-12d3-a456-426614174000",
    timeout_connect=0.2,  # 200ms connect timeout
    timeout_read=0.8,     # 800ms read timeout (for /retrieve)
)
```

### Distributed Tracing

```python
client = CardsClient(
    base_url="http://localhost:8002",
    tenant_id="123e4567-e89b-12d3-a456-426614174000",
    trace_id="trace-abc123",      # Propagated to all requests
    session_id="session-xyz789"   # Propagated to all requests
)
```

## Error Handling

```python
from fylle_cards_client import CardsClient, CardsAPIError

client = CardsClient(
    base_url="http://localhost:8002",
    tenant_id="123e4567-e89b-12d3-a456-426614174000"
)

try:
    card = client.get_card(UUID("non-existent-id"))
except CardsAPIError as e:
    print(f"Error {e.status_code}: {e.error.error}")
    print(f"Detail: {e.error.detail}")
    print(f"Request ID: {e.error.request_id}")
```

## Retry Logic

The client automatically retries on:
- **429 Too Many Requests**: Rate limit exceeded
- **5xx Server Errors**: Temporary server issues
- **Timeout**: Connection or read timeout

**Retry strategy**:
- Max attempts: 3
- Wait: Exponential backoff with jitter (0.1s to 2s)
- Only on safe operations (idempotent)

## Models

All models are Pydantic v2 models with full validation:

- `ContextCard` - Card model
- `CardType` - Enum (company, audience, voice, insight)
- `CreateCardRequest` - Create single card request
- `CreateCardsBatchRequest` - Batch creation request
- `CardBatchResponse` - Batch creation response
- `CardListResponse` - List/retrieve response
- `RetrieveCardsRequest` - Retrieve by IDs request
- `TrackUsageRequest` - Usage tracking request
- `ErrorResponse` - Error response

## API Version

This client is compatible with **Cards API v1.0.0**.

Contract: `contracts/cards-api-v1.yaml`

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy fylle_cards_client

# Linting
ruff check fylle_cards_client
```

## License

Proprietary - Fylle AI © 2025

## Support

For issues or questions, contact: engineering@fylle.ai

