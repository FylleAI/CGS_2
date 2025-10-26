# Fylle Shared Package

**Version**: 0.1.0

Shared enums, models, and utilities for Fylle microservices.

## 🎯 Purpose

This package provides a **single source of truth** for:
- **Enums**: CardType, WorkflowType (LOCKED - do not modify without migration plan)
- **Mappings**: CompanySnapshot → CardType mapping
- **Models**: ContextCard, WorkflowRequest, etc. (Pydantic models)
- **Utils**: Hashing, tracing, header propagation

## 📦 Installation

### From Local Source

```bash
cd shared/
pip install -e .
```

### From Built Package

```bash
cd shared/
python -m build
pip install dist/fylle_shared-0.1.0-py3-none-any.whl
```

### Development Installation

```bash
cd shared/
pip install -e ".[dev]"
```

## 🚀 Usage Examples

### Enums

```python
from fylle_shared import CardType, WorkflowType

# Use card types
card_type = CardType.COMPANY
print(card_type.value)  # "company"

# Validate card type
if card_type in [CardType.COMPANY, CardType.AUDIENCE]:
    print("Valid card type")

# Workflow types
workflow = WorkflowType.PREMIUM_NEWSLETTER
```

### Mappings

```python
from fylle_shared import SNAPSHOT_TO_CARD_MAPPING, CardType

# Map snapshot field to card type
snapshot_field = "company"
card_type = SNAPSHOT_TO_CARD_MAPPING[snapshot_field]
print(card_type)  # CardType.COMPANY
```

### Models

```python
from datetime import datetime
from uuid import uuid4
from fylle_shared import ContextCard, CardType

# Create a context card
card = ContextCard(
    card_id=uuid4(),
    tenant_id=uuid4(),
    card_type=CardType.COMPANY,
    title="Acme Corp",
    description="Cloud CRM platform",
    content={
        "name": "Acme Corp",
        "industry": "SaaS",
        "description": "Cloud CRM for tech companies"
    },
    tags=["SaaS", "CRM"],
    created_at=datetime.now(),
    updated_at=datetime.now(),
    created_by="onboarding-service"
)

# Serialize to JSON
card_json = card.model_dump_json()

# Deserialize from JSON
card_loaded = ContextCard.model_validate_json(card_json)
```

### Hashing Utils

```python
from fylle_shared import generate_content_hash, generate_idempotency_key

# Generate deterministic hash for deduplication
content = {"name": "Acme Corp", "industry": "SaaS"}
hash_value = generate_content_hash(content, type_hint="company")
print(hash_value)  # "a1b2c3d4..."

# Generate idempotency key for safe retries
session_id = "123e4567-e89b-12d3-a456-426614174000"
idem_key = generate_idempotency_key(session_id, "batch")
print(idem_key)  # "batch-123e4567-e89b-12d3-a456-426614174000"
```

### Tracing Utils

```python
from fylle_shared import get_trace_id, TRACE_HEADER

# Extract or generate trace ID
headers = {"X-Trace-ID": "trace-123"}
trace_id = get_trace_id(headers)
print(trace_id)  # "trace-123"

# Generate new trace ID if not present
trace_id = get_trace_id()
print(trace_id)  # "a1b2c3d4-..." (UUID)
```

### Header Propagation

```python
from fylle_shared import propagate_headers

# Propagate important headers to downstream services
incoming_headers = {
    "X-Tenant-ID": "tenant-123",
    "X-Trace-ID": "trace-456",
    "X-Session-ID": "session-789",
    "Content-Type": "application/json",
    "Authorization": "Bearer token"
}

# Extract only headers to propagate
outgoing_headers = propagate_headers(incoming_headers)
print(outgoing_headers)
# {
#     "X-Tenant-ID": "tenant-123",
#     "X-Trace-ID": "trace-456",
#     "X-Session-ID": "session-789"
# }

# Use in downstream HTTP call
import httpx
response = await httpx.post(
    "http://cards-api/cards/retrieve",
    headers=outgoing_headers,
    json={"card_ids": [...]}
)
```

## 🧪 Testing

```bash
# Run tests
cd shared/
pytest

# Run tests with coverage
pytest --cov=fylle_shared --cov-report=html

# Run specific test file
pytest tests/test_enums.py -v
```

## 📋 Package Structure

```
shared/
├── fylle_shared/
│   ├── __init__.py           # Package exports
│   ├── enums.py              # CardType, WorkflowType (LOCKED)
│   ├── mappings.py           # SNAPSHOT_TO_CARD_MAPPING (LOCKED)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── card.py           # ContextCard, CardUsageEvent
│   │   ├── workflow.py       # WorkflowRequest, WorkflowResult
│   │   └── common.py         # Pagination, ErrorResponse, IdempotencyKey
│   └── utils/
│       ├── __init__.py
│       ├── hashing.py        # generate_content_hash, generate_idempotency_key
│       ├── tracing.py        # get_trace_id
│       └── headers.py        # propagate_headers
├── tests/
│   ├── test_enums.py
│   ├── test_hashing.py
│   ├── test_tracing.py
│   └── test_headers.py
├── pyproject.toml
├── setup.cfg
└── README.md
```

## 🔒 LOCKED Components

**WARNING**: The following components are LOCKED and should NOT be modified without:
1. Cross-team approval
2. Migration plan
3. Deprecation notice (6 months for breaking changes)

### Locked Enums
- `CardType` (v1.0: company, audience, voice, insight)
- `WorkflowType`

### Locked Mappings
- `SNAPSHOT_TO_CARD_MAPPING`

## 📝 Versioning

This package follows **Semantic Versioning**:
- **Major** (1.0.0): Breaking changes to enums, models, or APIs
- **Minor** (0.1.0): Backward-compatible additions
- **Patch** (0.1.1): Bug fixes, no API changes

## 🚨 Important Notes

### v1.0 vs v1.1

**v1.0** (current):
- Only 4 card types: COMPANY, AUDIENCE, VOICE, INSIGHT
- Do NOT use v1.1 types (PRODUCT, PERSONA, CAMPAIGN, TOPIC)

**v1.1** (future):
- Will add 4 more card types
- Requires migration plan

### Pitfalls to Avoid

1. **Do NOT duplicate enums** in other services - always import from `fylle-shared`
2. **Do NOT modify LOCKED components** without approval
3. **Do NOT use v1.1 types** in v1.0 implementations
4. **Do NOT create manual API clients** - use auto-generated clients from OpenAPI specs

## 🤝 Contributing

1. All changes require tests
2. Run `pytest` before committing
3. Update version in `pyproject.toml` following semver
4. Update this README if adding new exports

## 📄 License

Proprietary - Fylle AI © 2025

