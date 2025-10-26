# Contributing to Fylle CGS

Thank you for contributing to Fylle CGS! This document outlines our development practices and policies.

## 🚨 Critical Policies

### Policy: Zero Manual Clients

**RULE**: Direct use of `httpx` or `requests` to call Fylle APIs is **PROHIBITED** when an SDK exists.

#### ✅ Correct

```python
from fylle_cards_client import CardsClient

client = CardsClient(base_url="...", tenant_id="...")
card = client.create_card(card_type=CardType.COMPANY, ...)
```

#### ❌ Incorrect - Will be REJECTED in code review

```python
import httpx

# PROHIBITED: Manual HTTP calls when SDK exists
response = httpx.post(
    "http://localhost:8002/api/v1/cards",
    json={...},
    headers={"X-Tenant-ID": "..."}
)
```

#### Rationale

1. **Type safety**: SDKs provide Pydantic models with validation
2. **Consistency**: All services use the same patterns
3. **Retry logic**: Automatic retry with exponential backoff
4. **Header propagation**: X-Tenant-ID, X-Trace-ID automatically included
5. **Error handling**: Typed exceptions with error details
6. **Maintainability**: Contract changes update SDK, not scattered HTTP calls

#### Exceptions

Manual HTTP calls are allowed ONLY when:
1. **SDK doesn't exist yet** (new API being developed)
2. **Debugging/testing SDK itself**
3. **Explicitly approved** by engineering lead with documented reason

#### Enforcement

- **Code review**: PRs using manual HTTP calls will be rejected
- **Linting**: Automated check (see below)
- **Documentation**: All examples use SDKs

## 🔍 Linting for Manual HTTP Calls

We use a custom lint check to detect manual HTTP calls:

```bash
# Check for prohibited patterns
./scripts/lint-no-manual-clients.sh
```

This script checks for:
- `httpx.post(` with Fylle API URLs
- `httpx.get(` with Fylle API URLs
- `requests.post(` with Fylle API URLs
- `requests.get(` with Fylle API URLs

**Allowed exceptions**:
- Files in `clients/` directory (SDK implementation)
- Files in `tests/` directory with `# lint:allow-manual-http` comment
- Files with explicit `# lint:allow-manual-http` comment

## 📋 Development Workflow

### 1. Contract-First Development

All API changes start with the OpenAPI contract:

```bash
# 1. Update contract
vim contracts/cards-api-v1.yaml

# 2. Validate contract
./contracts/validate.sh

# 3. Update SDK (if needed)
cd clients/python/fylle-cards-client
# Update models.py and client.py

# 4. Run smoke tests
cd ../../..
python3 clients/smoke_test.py

# 5. Implement API following contract
# 6. Run contract tests
schemathesis run --base-url http://localhost:8002 contracts/cards-api-v1.yaml
```

### 2. Branch Naming

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation only
- `refactor/` - Code refactoring
- `test/` - Test improvements

Examples:
- `feature/phase-0-api-contracts`
- `fix/cards-api-timeout`
- `docs/update-readme`

### 3. Commit Messages

Follow Conventional Commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `refactor`: Code refactoring
- `test`: Tests
- `chore`: Maintenance

**Examples**:
```
feat(cards-api): Add batch card creation endpoint

- Implement POST /cards/batch
- Add idempotency support with Idempotency-Key header
- Add deduplication with content hash
- Update OpenAPI contract

Closes #123
```

```
fix(workflow-client): Fix timeout configuration

- Set all 4 timeout parameters (connect, read, write, pool)
- Fixes httpx.Timeout validation error

Fixes #456
```

### 4. Pull Requests

**Before creating PR**:
1. ✅ All tests pass
2. ✅ Contracts validated
3. ✅ Smoke tests pass
4. ✅ No manual HTTP calls (unless exception)
5. ✅ Documentation updated

**PR Template**:
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] New feature
- [ ] Bug fix
- [ ] Breaking change
- [ ] Documentation update

## Checklist
- [ ] Contracts validated (`./contracts/validate.sh`)
- [ ] Smoke tests pass (`python3 clients/smoke_test.py`)
- [ ] No manual HTTP calls (or exception documented)
- [ ] Documentation updated
- [ ] Tests added/updated

## Related Issues
Closes #123
```

## 🧪 Testing

### Run All Tests

```bash
# Shared package tests
cd shared && pytest

# Smoke tests for clients
python3 clients/smoke_test.py

# Contract validation
./contracts/validate.sh

# Service tests (when implemented)
cd services/cards && pytest
cd services/workflow && pytest
```

### Writing Tests

- **Unit tests**: Test individual functions/classes
- **Integration tests**: Test API endpoints
- **Contract tests**: Validate against OpenAPI spec
- **Smoke tests**: Verify basic functionality

## 📚 Documentation

### Update Documentation When

- Adding new API endpoint → Update OpenAPI contract
- Adding new SDK method → Update client README
- Changing behavior → Update relevant docs
- Adding new feature → Update main README

### Documentation Structure

```
docs/
├── architecture/          # Architecture docs
├── contracts/            # OpenAPI specs
├── clients/              # SDK documentation
└── guides/               # How-to guides
```

## 🔐 Security

### Never Commit

- API keys or secrets
- Tenant IDs (use placeholders)
- Personal data
- `.env` files (use `.env.example`)

### Security Headers

Always include:
- `X-Tenant-ID`: Required on all requests
- `X-Trace-ID`: For distributed tracing
- `Idempotency-Key`: On mutate endpoints

## 🚀 Deployment

### Before Deploying

1. ✅ All tests pass in CI
2. ✅ Code reviewed and approved
3. ✅ Documentation updated
4. ✅ Breaking changes documented
5. ✅ Migration plan (if needed)

### Deployment Process

1. Merge PR to `main`
2. CI runs all tests
3. Tag release (e.g., `v1.0.0`)
4. Deploy to staging
5. Run smoke tests on staging
6. Deploy to production
7. Monitor metrics

## 📊 Code Quality

### Linting

```bash
# Python
ruff check .
ruff format .

# Type checking
mypy .
```

### Code Style

- **Python**: Follow PEP 8
- **Line length**: 120 characters
- **Imports**: Sorted with `isort`
- **Type hints**: Required for all functions

## 🤝 Getting Help

- **Questions**: Ask in #engineering Slack channel
- **Bugs**: Create GitHub issue
- **Feature requests**: Create GitHub issue with `enhancement` label
- **Urgent**: Contact engineering lead

## 📄 License

Proprietary - Fylle AI © 2025

---

**Thank you for contributing!** 🎉

