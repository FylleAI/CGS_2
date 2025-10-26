# Fylle Workflow API Client

**Version**: 1.0.0

Python client for Fylle Workflow API v1.

Auto-generated from OpenAPI spec: `contracts/workflow-api-v1.yaml`

## Installation

```bash
pip install fylle-workflow-client==1.0.0
```

## Quick Start

```python
from fylle_workflow_client import WorkflowClient, WorkflowType
from uuid import UUID

# Create client
client = WorkflowClient(
    base_url="http://localhost:8001",
    tenant_id="123e4567-e89b-12d3-a456-426614174000"
)

# Execute workflow with card_ids (PREFERRED)
response = client.execute_workflow(
    workflow_type=WorkflowType.PREMIUM_NEWSLETTER,
    card_ids=[
        UUID("789e0123-e89b-12d3-a456-426614174002"),
        UUID("789e0123-e89b-12d3-a456-426614174003"),
    ],
    parameters={
        "topic": "AI trends in 2025",
        "tone": "professional",
        "length": "medium"
    }
)

print(f"Workflow ID: {response.workflow_id}")
print(f"Status: {response.status}")
print(f"Output: {response.output}")
```

## Features

✅ **Type-safe**: Full Pydantic models for all requests and responses  
✅ **Retry logic**: Automatic retry with exponential backoff (429, 5xx)  
✅ **Timeouts**: Configurable connect (200ms) and read (5s) timeouts  
✅ **Header propagation**: Automatic X-Tenant-ID, X-Trace-ID, X-Session-ID  
✅ **Deprecation warnings**: Detects deprecated `context` parameter usage  
✅ **Error handling**: Typed exceptions with error details  

## Migration from `context` to `card_ids`

### ❌ Old Way (Deprecated)

```python
# DEPRECATED: Using context dict
response = client.execute_workflow(
    workflow_type=WorkflowType.PREMIUM_NEWSLETTER,
    context={
        "company": {"name": "Acme Corp"},
        "audience": {"primary": "Tech executives"},
        "voice": {"tone": "Professional"}
    },
    parameters={"topic": "AI trends"}
)
# Response includes deprecation warning headers
```

### ✅ New Way (Preferred)

```python
# PREFERRED: Using card_ids
response = client.execute_workflow(
    workflow_type=WorkflowType.PREMIUM_NEWSLETTER,
    card_ids=[
        UUID("789e0123-e89b-12d3-a456-426614174002"),  # company card
        UUID("789e0123-e89b-12d3-a456-426614174003"),  # audience card
        UUID("789e0123-e89b-12d3-a456-426614174004"),  # voice card
    ],
    parameters={"topic": "AI trends"}
)
```

## Usage Examples

### Execute Workflow

```python
from fylle_workflow_client import WorkflowClient, WorkflowType
from uuid import UUID

with WorkflowClient(
    base_url="http://localhost:8001",
    tenant_id="123e4567-e89b-12d3-a456-426614174000",
    trace_id="trace-abc123"
) as client:
    response = client.execute_workflow(
        workflow_type=WorkflowType.PREMIUM_NEWSLETTER,
        card_ids=[
            UUID("789e0123-e89b-12d3-a456-426614174002"),
        ],
        parameters={
            "topic": "AI trends in 2025",
            "tone": "professional",
            "length": "medium"
        }
    )
    
    print(f"Workflow ID: {response.workflow_id}")
    print(f"Status: {response.status}")
    
    if response.metrics:
        print(f"Execution time: {response.metrics.execution_time_ms}ms")
        print(f"Cards used: {response.metrics.cards_used}")
        print(f"Cache hit rate: {response.metrics.cache_hit_rate}")
```

### Check Workflow Status

```python
from uuid import UUID

# Get workflow status
status = client.get_workflow_status(
    workflow_id=UUID("abc12345-e89b-12d3-a456-426614174003")
)

print(f"Status: {status.status}")
if status.status == "completed":
    print(f"Output: {status.output}")
```

## Error Handling

```python
from fylle_workflow_client import WorkflowClient, WorkflowAPIError

try:
    response = client.execute_workflow(
        workflow_type=WorkflowType.PREMIUM_NEWSLETTER,
        card_ids=[],  # Invalid: empty list
        parameters={}
    )
except WorkflowAPIError as e:
    print(f"Error {e.status_code}: {e.error.error}")
    print(f"Detail: {e.error.detail}")
```

## API Version

This client is compatible with **Workflow API v1.0.0**.

Contract: `contracts/workflow-api-v1.yaml`

## Deprecation Timeline

- **v1.0** (current): Both `card_ids` and `context` supported
- **v1.5** (2026-01-26): `context` marked deprecated with warning headers
- **v2.0** (2026-04-26): `context` removed (6 months notice)

## License

Proprietary - Fylle AI © 2025

## Support

For issues or questions, contact: engineering@fylle.ai

