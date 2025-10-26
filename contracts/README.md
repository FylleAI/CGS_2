# Fylle API Contracts

**Version**: 1.0.0

OpenAPI 3.1 specifications for Fylle microservices.

## 📋 Contracts

| API | File | Description | Port |
|-----|------|-------------|------|
| **Cards** | `cards-api-v1.yaml` | Context cards management | 8002 |
| **Workflow** | `workflow-api-v1.yaml` | Content generation workflows | 8001 |
| **Onboarding** | `onboarding-api-v1.yaml` | User onboarding and card creation | 8001 |

## 🎯 Contract-First Approach

These contracts are the **single source of truth** for API design.

**Workflow**:
1. ✅ Define OpenAPI contract (this folder)
2. ✅ Validate contract (`openapi-spec-validator`)
3. ✅ Generate client libraries (`openapi-python-client`)
4. ✅ Implement API following contract
5. ✅ Run contract tests (`schemathesis`)
6. ✅ Deploy

## 🔒 Locked Components

**DO NOT modify** without cross-team approval and migration plan:

- **Enums**: `CardType`, `WorkflowType` (from `fylle-shared`)
- **Security schemes**: `X-Tenant-ID`, `X-Trace-ID`, `Idempotency-Key`
- **Error envelope**: `{ error, detail, request_id }`

## 📝 v1.0 Surface

### Cards API

**Included in v1.0**:
- ✅ `POST /api/v1/cards` - Create single card
- ✅ `POST /api/v1/cards/batch` - Batch creation (idempotent)
- ✅ `GET /api/v1/cards` - List with filtering
- ✅ `GET /api/v1/cards/{card_id}` - Get by ID
- ✅ `POST /api/v1/cards/retrieve` - Retrieve for workflow
- ✅ `POST /api/v1/cards/{card_id}/usage` - Track usage

**NOT in v1.0** (deferred to v1.1):
- ❌ Card relationships
- ❌ Semantic search
- ❌ Performance tracking

### Workflow API

**Included in v1.0**:
- ✅ `POST /api/v1/workflow/execute` - Execute workflow
  - **Preferred**: `card_ids` parameter
  - **Deprecated**: `context` parameter (warning headers)
- ✅ `GET /api/v1/workflow/{workflow_id}` - Get status

### Onboarding API

**Included in v1.0**:
- ✅ `POST /api/v1/onboarding/sessions` - Create session
- ✅ `GET /api/v1/onboarding/sessions/{session_id}` - Get session
- ✅ `POST /api/v1/onboarding/sessions/{session_id}/answers` - Submit answers
  - Creates cards in Cards API
  - Returns `card_ids` in response

## 🔐 Security

### Required Headers

All APIs require:
- `X-Tenant-ID`: Tenant ID for multi-tenant isolation (required)
- `X-Trace-ID`: Distributed tracing ID (optional, auto-generated)

Mutate endpoints also accept:
- `Idempotency-Key`: For safe retries (optional)

### Security Schemes

```yaml
securitySchemes:
  TenantHeader:
    type: apiKey
    in: header
    name: X-Tenant-ID
```

### Rate Limiting

- **Cards API**: 100 req/min per tenant on mutate endpoints
- **Workflow API**: TBD
- **Onboarding API**: TBD

## 📊 Golden Examples

Each contract includes **golden examples** for critical endpoints:

### Cards API
- `POST /cards/batch` - Create cards from CompanySnapshot
- `POST /cards/retrieve` - Retrieve cards for workflow

### Workflow API
- `POST /workflow/execute` - Execute with `card_ids` (preferred)
- `POST /workflow/execute` - Execute with `context` (deprecated)

### Onboarding API
- `POST /sessions/{id}/answers` - Submit answers and create cards

## ✅ Validation

### Validate Contracts

```bash
# Install validator
pip install openapi-spec-validator

# Validate all contracts
python3 -m openapi_spec_validator contracts/cards-api-v1.yaml
python3 -m openapi_spec_validator contracts/workflow-api-v1.yaml
python3 -m openapi_spec_validator contracts/onboarding-api-v1.yaml

# Or use the validation script
./contracts/validate.sh
```

### Contract Testing

```bash
# Install schemathesis
pip install schemathesis

# Run contract tests against running API
schemathesis run \
  --base-url http://localhost:8002 \
  contracts/cards-api-v1.yaml \
  --checks all \
  --hypothesis-max-examples=100
```

## 🚀 Generate Clients

```bash
# Install generator
pip install openapi-python-client

# Generate Cards client
openapi-python-client generate \
  --path contracts/cards-api-v1.yaml \
  --output-path clients/python/fylle-cards-client \
  --meta setup

# Generate Workflow client
openapi-python-client generate \
  --path contracts/workflow-api-v1.yaml \
  --output-path clients/python/fylle-workflow-client \
  --meta setup
```

## 📖 View Documentation

### Swagger UI

```bash
# Install swagger-ui-watcher
npm install -g swagger-ui-watcher

# View Cards API
swagger-ui-watcher contracts/cards-api-v1.yaml

# View Workflow API
swagger-ui-watcher contracts/workflow-api-v1.yaml
```

### Redoc

```bash
# Install redoc-cli
npm install -g redoc-cli

# Generate HTML
redoc-cli bundle contracts/cards-api-v1.yaml -o docs/cards-api.html
```

## 🔄 Versioning

### URL-Based Versioning

All APIs use URL-based versioning: `/api/v1/`, `/api/v2/`

### Version Lifecycle

- **v1.0** (current): Initial release
- **v1.5** (2026-01-26): Deprecation warnings for `context` parameter
- **v2.0** (2026-04-26): Remove `context` parameter (6 months notice)

### Deprecation Policy

1. **Announce** (v1.5): Add deprecation notice in docs and response headers
2. **Warning** (v1.5): Include `X-API-Deprecation-Warning` header
3. **Final Notice** (v1.8): Log warnings, send emails to API consumers
4. **Removal** (v2.0): Remove deprecated feature (6 months after announcement)

## 🚨 Breaking Changes

**Breaking changes** require:
1. Cross-team approval
2. Migration guide
3. 6 months deprecation notice
4. New major version (v2.0)

**Examples of breaking changes**:
- Removing endpoint
- Removing required field
- Changing field type
- Changing enum values

## 📚 Additional Resources

- [OpenAPI 3.1 Specification](https://spec.openapis.org/oas/v3.1.0)
- [Fylle Shared Package](../shared/README.md)
- [API Migration Guide](https://docs.fylle.ai/migration/context-to-cards)

## 🤝 Contributing

1. Modify contract in this folder
2. Validate with `openapi-spec-validator`
3. Update golden examples
4. Regenerate clients
5. Update implementation
6. Run contract tests
7. Create PR

## 📄 License

Proprietary - Fylle AI © 2025

