# E2E Tests - Cards API

End-to-end tests for the complete Onboarding → Cards → Workflow flow.

## Overview

These tests validate the complete integration between:
- **Onboarding API**: Creates cards via batch endpoint
- **Cards API**: Stores, retrieves, and tracks card usage
- **Workflow API**: Consumes cards and tracks usage

## Test Flow

```
┌─────────────┐
│ Onboarding  │
│   Service   │
└──────┬──────┘
       │
       │ POST /api/v1/cards/batch
       │ (Create 4 cards)
       ▼
┌─────────────┐
│  Cards API  │
│  (Database) │
└──────┬──────┘
       │
       │ POST /api/v1/cards/retrieve
       │ (Get cards by IDs)
       ▼
┌─────────────┐
│  Workflow   │
│   Service   │
└──────┬──────┘
       │
       │ POST /api/v1/cards/{id}/usage
       │ (Track usage)
       ▼
┌─────────────┐
│  Cards API  │
│  (Metrics)  │
└─────────────┘
```

## Prerequisites

### 1. Cards API Running

```bash
# Start Cards API
./scripts/start_cards_api.sh

# Or manually
uvicorn cards.api.main:app --port 8002
```

### 2. Environment Variables

```bash
export SUPABASE_DATABASE_URL="postgresql://user:pass@host:port/db"
export CARDS_API_URL="http://localhost:8002"  # Optional, defaults to localhost:8002
```

### 3. Database Setup

Ensure the database schema is created:

```bash
# Run migration script in Supabase SQL Editor
# See: scripts/test_cards_api_supabase.sql
```

## Running Tests

### Run All E2E Tests

```bash
pytest tests/e2e/ -v -m e2e
```

### Run Specific Test

```bash
pytest tests/e2e/test_onboarding_cards_workflow.py::test_onboarding_cards_workflow_e2e -v
```

### Run with Output

```bash
pytest tests/e2e/ -v -s -m e2e
```

## Test Coverage

### `test_onboarding_cards_workflow.py`

**Test**: `test_onboarding_cards_workflow_e2e`

**Steps**:
1. ✅ **Onboarding**: Create 4 cards (company, audience, voice, insight)
2. ✅ **Workflow**: Retrieve cards by IDs
3. ✅ **Workflow**: Track usage for each card
4. ✅ **Verify**: Usage count incremented
5. ✅ **Verify**: Metrics exposed on `/metrics`
6. ✅ **Verify**: Idempotency replay (cache HIT)

**Assertions**:
- 201 response for batch create
- 4 cards created
- Idempotency cache MISS on first request
- 200 response for retrieve
- All 4 cards retrieved
- Partial result = false
- 200 response for usage tracking
- Usage count >= 1 for all cards
- Event recorded = true
- Metrics exposed (4 key metrics)
- Idempotency cache HIT on replay

## Expected Output

```
================================================================================
STEP 1: ONBOARDING - Create Cards
================================================================================
✅ Created 4 cards
  - 550e8400-e29b-41d4-a716-446655440001: company
  - 550e8400-e29b-41d4-a716-446655440002: audience
  - 550e8400-e29b-41d4-a716-446655440003: voice
  - 550e8400-e29b-41d4-a716-446655440004: insight
  - Idempotency Cache: MISS

================================================================================
STEP 2: WORKFLOW - Retrieve Cards
================================================================================
✅ Retrieved 4 cards
  - 550e8400-e29b-41d4-a716-446655440001: company
  - 550e8400-e29b-41d4-a716-446655440002: audience
  - 550e8400-e29b-41d4-a716-446655440003: voice
  - 550e8400-e29b-41d4-a716-446655440004: insight
  - Partial Result: false

================================================================================
STEP 3: WORKFLOW - Track Usage
================================================================================
  - 550e8400-e29b-41d4-a716-446655440001: usage_count=1, event_recorded=true
  - 550e8400-e29b-41d4-a716-446655440002: usage_count=1, event_recorded=true
  - 550e8400-e29b-41d4-a716-446655440003: usage_count=1, event_recorded=true
  - 550e8400-e29b-41d4-a716-446655440004: usage_count=1, event_recorded=true
✅ Usage tracked for all cards

================================================================================
STEP 4: VERIFY - Usage Count Incremented
================================================================================
  - 550e8400-e29b-41d4-a716-446655440001: usage_count=1
  - 550e8400-e29b-41d4-a716-446655440002: usage_count=1
  - 550e8400-e29b-41d4-a716-446655440003: usage_count=1
  - 550e8400-e29b-41d4-a716-446655440004: usage_count=1
✅ All cards have usage_count >= 1

================================================================================
STEP 5: VERIFY - Metrics Exposed
================================================================================
✅ Metrics exposed:
  - cards_api_requests_total
  - cards_api_request_duration_seconds
  - card_usage_events_total
  - cards_usage_write_duration_ms

================================================================================
STEP 6: VERIFY - Idempotency Replay
================================================================================
  - Idempotency Cache: HIT
✅ Idempotency replay successful (cache HIT)

================================================================================
E2E TEST SUMMARY
================================================================================
✅ STEP 1: Onboarding created 4 cards
✅ STEP 2: Workflow retrieved 4 cards
✅ STEP 3: Workflow tracked usage for 4 cards
✅ STEP 4: Usage count incremented for all cards
✅ STEP 5: Metrics exposed on /metrics
✅ STEP 6: Idempotency replay successful
================================================================================
🎉 E2E TEST PASSED!
================================================================================
```

## Troubleshooting

### Test Fails: Connection Refused

**Problem**: Cards API not running

**Solution**:
```bash
./scripts/start_cards_api.sh
```

### Test Fails: Database Connection Error

**Problem**: `SUPABASE_DATABASE_URL` not set or invalid

**Solution**:
```bash
export SUPABASE_DATABASE_URL="postgresql://user:pass@host:port/db"
```

### Test Fails: Cards Not Found

**Problem**: Database schema not created

**Solution**: Run migration script in Supabase SQL Editor

### Test Fails: Idempotency Cache Always MISS

**Problem**: `idempotency_store` table not created or RLS blocking access

**Solution**: Check RLS policies and table existence

## CI/CD Integration

### GitHub Actions Example

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  e2e:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:17
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Start Cards API
        run: |
          uvicorn cards.api.main:app --port 8002 &
          sleep 5
        env:
          SUPABASE_DATABASE_URL: ${{ secrets.SUPABASE_DATABASE_URL }}
      
      - name: Run E2E Tests
        run: |
          pytest tests/e2e/ -v -m e2e
        env:
          CARDS_API_URL: http://localhost:8002
```

## Performance Benchmarks

Expected performance (p95):
- **Batch Create**: ≤ 100ms
- **Retrieve**: ≤ 50ms
- **Usage Tracking**: ≤ 25ms

Run benchmarks:
```bash
pytest tests/e2e/ -v --benchmark-only
```

## Next Steps

1. Add more E2E scenarios (error cases, edge cases)
2. Add performance benchmarking
3. Add load testing
4. Add chaos testing (network failures, database failures)
5. Add multi-tenant isolation tests

