# Fylle API Clients

Auto-generated Python clients for Fylle microservices APIs.

## 📦 Available Clients

| Client | Version | API | Contract |
|--------|---------|-----|----------|
| **fylle-cards-client** | 1.0.0 | Cards API v1 | `contracts/cards-api-v1.yaml` |
| **fylle-workflow-client** | 1.0.0 | Workflow API v1 | `contracts/workflow-api-v1.yaml` |

## 🚀 Quick Start

### Cards Client

```bash
pip install fylle-cards-client==1.0.0
```

```python
from fylle_cards_client import CardsClient, CardType

client = CardsClient(
    base_url="http://localhost:8002",
    tenant_id="your-tenant-id"
)

card = client.create_card(
    card_type=CardType.COMPANY,
    title="Acme Corp",
    content={"name": "Acme Corp"},
    created_by="onboarding-service"
)
```

### Workflow Client

```bash
pip install fylle-workflow-client==1.0.0
```

```python
from fylle_workflow_client import WorkflowClient, WorkflowType
from uuid import UUID

client = WorkflowClient(
    base_url="http://localhost:8001",
    tenant_id="your-tenant-id"
)

response = client.execute_workflow(
    workflow_type=WorkflowType.PREMIUM_NEWSLETTER,
    card_ids=[UUID("card-id-1"), UUID("card-id-2")],
    parameters={"topic": "AI trends"}
)
```

## ✨ Features

All clients include:

✅ **Type-safe**: Full Pydantic v2 models  
✅ **Retry logic**: Automatic retry with exponential backoff (429, 5xx)  
✅ **Timeouts**: Configurable connect/read timeouts  
✅ **Header propagation**: X-Tenant-ID, X-Trace-ID, X-Session-ID  
✅ **Idempotency**: Support for Idempotency-Key header  
✅ **Error handling**: Typed exceptions with error details  
✅ **Context managers**: Automatic resource cleanup  

## 🔧 Development

### Install for Development

```bash
# Cards client
cd clients/python/fylle-cards-client
pip install -e ".[dev]"

# Workflow client
cd clients/python/fylle-workflow-client
pip install -e ".[dev]"
```

### Run Smoke Tests

```bash
# Install both clients
cd clients/python/fylle-cards-client && pip install -e .
cd ../fylle-workflow-client && pip install -e .

# Run smoke tests
cd ../..
python3 smoke_test.py
```

## 🔄 Regeneration

Clients are manually crafted based on OpenAPI contracts.

**When to regenerate**:
- Contract changes (new endpoints, models, parameters)
- API version bump (v1.1, v2.0)
- Bug fixes or improvements

**How to regenerate**:
1. Update OpenAPI contract in `contracts/`
2. Validate contract: `./contracts/validate.sh`
3. Update client models and methods manually
4. Update version in `pyproject.toml`
5. Run smoke tests
6. Build and publish

## 📋 Policy: Zero Manual Clients

**IMPORTANT**: Direct use of `httpx` or `requests` to call Fylle APIs is **prohibited** when an SDK exists.

### ✅ Correct

```python
from fylle_cards_client import CardsClient

client = CardsClient(base_url="...", tenant_id="...")
card = client.create_card(...)
```

### ❌ Incorrect

```python
import httpx

# PROHIBITED: Manual HTTP calls when SDK exists
response = httpx.post(
    "http://localhost:8002/api/v1/cards",
    json={...},
    headers={"X-Tenant-ID": "..."}
)
```

### Enforcement

- **Code review**: PRs using manual HTTP calls will be rejected
- **Linting**: Automated check for direct `httpx`/`requests` usage
- **Documentation**: All examples use SDKs

### Exceptions

Manual HTTP calls are allowed ONLY when:
1. SDK doesn't exist yet (new API)
2. Debugging/testing SDK itself
3. Explicitly approved by engineering lead

## 📚 Documentation

- [Cards Client README](python/fylle-cards-client/README.md)
- [Workflow Client README](python/fylle-workflow-client/README.md)
- [API Contracts](../contracts/README.md)

## 🔐 Security

- **X-Tenant-ID**: Required on all requests (enforced by clients)
- **Timeouts**: Prevent hanging requests
- **Retry logic**: Safe retries with exponential backoff
- **Error handling**: Never expose sensitive data in errors

## 📊 Versioning

Client versions match API versions:
- `fylle-cards-client==1.0.0` → Cards API v1.0
- `fylle-workflow-client==1.0.0` → Workflow API v1.0

**Compatibility**:
- Minor version bumps (1.0 → 1.1): Backward compatible
- Major version bumps (1.0 → 2.0): Breaking changes

## 🐛 Troubleshooting

### Import Error

```python
ModuleNotFoundError: No module named 'fylle_cards_client'
```

**Solution**: Install the client
```bash
pip install fylle-cards-client==1.0.0
```

### Timeout Error

```python
httpx.TimeoutException: Read timeout
```

**Solution**: Increase timeout
```python
client = CardsClient(
    base_url="...",
    tenant_id="...",
    timeout_read=2.0  # Increase from default 0.8s
)
```

### API Error

```python
CardsAPIError: Cards API error 401: Unauthorized - X-Tenant-ID header required
```

**Solution**: Provide tenant_id
```python
client = CardsClient(
    base_url="...",
    tenant_id="your-tenant-id"  # Required!
)
```

## 📄 License

Proprietary - Fylle AI © 2025

## 🤝 Support

For issues or questions, contact: engineering@fylle.ai

