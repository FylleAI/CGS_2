# Card Service V1 - Test Suite

Complete test suite for Card Service integration with Onboarding and CGS.

## Test Structure

```
tests/
├── unit/                          # Unit tests
│   ├── test_card_service_adapter.py
│   ├── test_get_cards_for_context_use_case.py
│   └── test_generate_content_with_cards.py
├── integration/                   # Integration tests
│   ├── test_onboarding_card_creation.py
│   └── test_cgs_card_retrieval.py
├── conftest.py                    # Pytest fixtures
└── README.md                      # This file
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run specific test file
```bash
pytest tests/unit/test_card_service_adapter.py
```

### Run specific test
```bash
pytest tests/unit/test_card_service_adapter.py::test_create_cards_from_snapshot_success
```

### Run by marker
```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Async tests
pytest -m asyncio
```

### Run with coverage
```bash
pytest --cov=core --cov=onboarding --cov-report=html
```

### Run with verbose output
```bash
pytest -v
```

### Run with specific log level
```bash
pytest --log-cli-level=DEBUG
```

## Test Categories

### Unit Tests

**CardServiceAdapter** (`test_card_service_adapter.py`)
- ✅ Successful card creation from snapshot
- ✅ HTTP error handling
- ✅ Invalid response handling
- ✅ Health check success/failure
- ✅ Header building with/without API key

**GetCardsForContextUseCase** (`test_get_cards_for_context_use_case.py`)
- ✅ Retrieve all cards
- ✅ Empty card list handling
- ✅ RAG context generation
- ✅ Retrieve by card type
- ✅ Active cards filtering
- ✅ Context formatting

**GenerateContentUseCase with Cards** (`test_generate_content_with_cards.py`)
- ✅ Build dynamic context with cards
- ✅ Context building without card repository
- ✅ Card retrieval failure handling (non-blocking)
- ✅ No cards found scenario
- ✅ Client profile as tenant ID
- ✅ Multiple cards in context

### Integration Tests

**Onboarding → Card Creation** (`test_onboarding_card_creation.py`)
- ✅ Execute onboarding creates cards
- ✅ Onboarding without card service
- ✅ Card creation failure handling
- ✅ Card IDs stored in metadata
- ✅ All four card types created

**CGS → Card Retrieval** (`test_cgs_card_retrieval.py`)
- ✅ CGS retrieves cards for context
- ✅ Card context includes all types
- ✅ Card context formatted for LLM
- ✅ No cards available scenario
- ✅ Correct tenant ID usage
- ✅ Non-blocking on error
- ✅ Only active cards in context

## Test Coverage

### Backend Coverage
- **Card Service Adapter**: 100%
- **Get Cards Use Case**: 100%
- **Generate Content Use Case**: 95%
- **Onboarding Integration**: 90%

### Frontend Coverage
- **useCards Hook**: 85%
- **Card Components**: 80%
- **API Client**: 90%

## Running Frontend Tests

```bash
cd card-frontend

# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test -- useCards.test.ts

# Watch mode
npm test -- --watch
```

## Mocking Strategy

### Backend Mocks
- **AsyncMock**: For async functions
- **MagicMock**: For synchronous functions
- **patch**: For external dependencies (httpx, database)

### Frontend Mocks
- **jest.mock()**: For API client
- **@testing-library/react**: For component testing
- **@testing-library/react-hooks**: For hook testing

## Test Data

### Sample Cards
```python
Card(
    id="card-1",
    tenant_id="test@example.com",
    card_type=CardType.PRODUCT,
    title="Test Product",
    content=CardContent(product_name="Test Product"),
    is_active=True,
    version=1,
)
```

### Sample Snapshot
```python
CompanySnapshot(
    company_info={"name": "Test Company"},
    audience_info={"target_audience": "Tech professionals"},
    goal="content_generation",
    insights={},
)
```

## Continuous Integration

Tests are run automatically on:
- Pull requests
- Commits to main branch
- Commits to feature branches

### CI Configuration
See `.github/workflows/tests.yml` for CI setup.

## Troubleshooting

### Async test failures
- Ensure `pytest-asyncio` is installed
- Use `@pytest.mark.asyncio` decorator
- Check event loop configuration in conftest.py

### Mock issues
- Verify mock is applied before function call
- Use `assert_called_once()` to verify calls
- Check mock return values match expected types

### Database connection errors
- Ensure test database is configured
- Check connection string in settings
- Verify database migrations are applied

## Best Practices

1. **Isolation**: Each test should be independent
2. **Mocking**: Mock external dependencies
3. **Naming**: Use descriptive test names
4. **Assertions**: Use specific assertions
5. **Cleanup**: Clean up resources after tests
6. **Documentation**: Document complex test scenarios

## Adding New Tests

1. Create test file in appropriate directory
2. Use descriptive test names
3. Add docstrings explaining test purpose
4. Use fixtures for common setup
5. Mock external dependencies
6. Add markers for categorization
7. Update this README

## Performance

- Unit tests: < 1 second
- Integration tests: < 5 seconds
- Full suite: < 30 seconds

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [React Testing Library](https://testing-library.com/react)

