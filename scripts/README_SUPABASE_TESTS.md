# 🧪 Supabase SQL Test Suite

## Overview

This directory contains SQL test scripts for validating Cards API database operations directly in Supabase SQL Editor.

**Why SQL tests?**
- ✅ No network/DNS issues
- ✅ Direct database validation
- ✅ Fast execution (< 5 seconds)
- ✅ Easy to run in CI/CD
- ✅ Documents expected behavior

---

## 📁 Files

| File | Purpose | Run Time |
|------|---------|----------|
| `test_cards_api_supabase.sql` | Complete test suite (7 tests) | ~5 sec |

---

## 🚀 How to Run

### **Option 1: Supabase SQL Editor (Recommended)**

1. Open your Supabase project
2. Go to **SQL Editor**
3. Click **New Query**
4. Copy/paste the entire content of `test_cards_api_supabase.sql`
5. Click **Run** (or press `Cmd+Enter` / `Ctrl+Enter`)

**Expected Output**: All tests pass with ✅ messages

---

### **Option 2: psql CLI**

```bash
# Set environment variables
export SUPABASE_DB_URL="postgresql://postgres:PASSWORD@db.PROJECT.supabase.co:5432/postgres"

# Run tests
psql $SUPABASE_DB_URL -f scripts/test_cards_api_supabase.sql
```

---

## 🧪 Test Coverage

### **Test 1: Batch Card Creation**
**Simulates**: `POST /api/v1/cards/batch`

**What it tests**:
- ✅ Insert 4 cards (company, audience, voice, insight)
- ✅ Content stored as JSONB
- ✅ Content hash computed correctly
- ✅ Tenant isolation via RLS

**Expected Result**: 4 cards created with correct types

---

### **Test 2: Idempotency Store - INSERT**
**Simulates**: First API call with `Idempotency-Key`

**What it tests**:
- ✅ Insert idempotency entry
- ✅ Response payload stored as JSONB
- ✅ 24h TTL set correctly
- ✅ `was_inserted = true` (cache MISS)

**Expected Result**: New entry created, cache status = MISS

---

### **Test 3: Idempotency Store - UPDATE**
**Simulates**: Replay with same `Idempotency-Key`

**What it tests**:
- ✅ ON CONFLICT triggers UPDATE
- ✅ `updated_at` timestamp changes
- ✅ `was_inserted = false` (cache HIT)
- ✅ No duplicate entries created

**Expected Result**: Existing entry updated, cache status = HIT

---

### **Test 4: Card Retrieval**
**Simulates**: `POST /api/v1/cards/retrieve`

**What it tests**:
- ✅ Retrieve cards by tenant
- ✅ Only active cards returned
- ✅ Correct ordering (company → audience → voice → insight)

**Expected Result**: All 4 cards retrieved in correct order

---

### **Test 5: RLS Tenant Isolation**
**Simulates**: Multi-tenant security

**What it tests**:
- ✅ Tenant A cannot see Tenant B cards
- ✅ Tenant B cannot see Tenant A cards
- ✅ RLS policies enforced

**Expected Result**: `tenant_a_cards_visible_to_tenant_b = 0`

---

### **Test 6: Content Deduplication**
**Simulates**: Duplicate card prevention

**What it tests**:
- ✅ UNIQUE constraint on (tenant_id, card_type, content_hash)
- ✅ Duplicate insert fails with `unique_violation`

**Expected Result**: Duplicate card prevented

---

### **Test 7: Usage Tracking**
**Simulates**: `POST /api/v1/cards/{id}/usage`

**What it tests**:
- ✅ Insert usage entry
- ✅ Track workflow type
- ✅ Timestamp recorded

**Expected Result**: Usage entry created

---

## 📊 Expected Output

```
NOTICE:  Tenant A: 123e4567-e89b-12d3-a456-426614174000
NOTICE:  Tenant B: 987e6543-e21b-12d3-a456-426614174999

NOTICE:  ============================================================================
NOTICE:  TEST 1: BATCH CARD CREATION
NOTICE:  ============================================================================
NOTICE:  ✅ TEST 1 PASSED: 4 cards created successfully

NOTICE:  ============================================================================
NOTICE:  TEST 2: IDEMPOTENCY STORE - INSERT (Cache MISS)
NOTICE:  ============================================================================
NOTICE:  ✅ TEST 2 PASSED: Idempotency entry created (Cache MISS)

NOTICE:  ============================================================================
NOTICE:  TEST 3: IDEMPOTENCY STORE - UPDATE (Cache HIT)
NOTICE:  ============================================================================
NOTICE:  ✅ TEST 3 PASSED: Idempotency replay detected (Cache HIT)

NOTICE:  ============================================================================
NOTICE:  TEST 4: CARD RETRIEVAL
NOTICE:  ============================================================================
NOTICE:  ✅ TEST 4 PASSED: Cards retrieved successfully

NOTICE:  ============================================================================
NOTICE:  TEST 5: RLS TENANT ISOLATION
NOTICE:  ============================================================================
NOTICE:  ✅ TEST 5 PASSED: RLS tenant isolation verified

NOTICE:  ============================================================================
NOTICE:  TEST 6: CONTENT DEDUPLICATION
NOTICE:  ============================================================================
NOTICE:  ✅ TEST 6 PASSED: Duplicate card prevented by unique constraint

NOTICE:  ============================================================================
NOTICE:  TEST 7: USAGE TRACKING
NOTICE:  ============================================================================
NOTICE:  ✅ TEST 7 PASSED: Usage tracked successfully

NOTICE:  ============================================================================
NOTICE:  TEST SUMMARY
NOTICE:  ============================================================================

 tenant_id                            | total_cards | unique_card_types
--------------------------------------+-------------+-------------------
 123e4567-e89b-12d3-a456-426614174000 |           4 |                 4
 987e6543-e21b-12d3-a456-426614174999 |           1 |                 1

 total_idempotency_entries | valid_entries | expired_entries
---------------------------+---------------+-----------------
                         1 |             1 |               0

 total_usage_entries | unique_cards_used | unique_workflows
---------------------+-------------------+------------------
                   1 |                 1 |                1

NOTICE:  ✅ ALL TESTS PASSED!
NOTICE:  
NOTICE:  Cards API database operations validated:
NOTICE:    ✅ Batch card creation
NOTICE:    ✅ Idempotency (INSERT + UPDATE)
NOTICE:    ✅ Card retrieval
NOTICE:    ✅ RLS tenant isolation
NOTICE:    ✅ Content deduplication
NOTICE:    ✅ Usage tracking
```

---

## 🔧 Troubleshooting

### **Error: column "updated_at" does not exist**

**Solution**: Run the migration to add the column:

```sql
ALTER TABLE idempotency_store
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();
```

---

### **Error: there is no unique or exclusion constraint**

**Solution**: Add the unique constraint:

```sql
ALTER TABLE idempotency_store
ADD CONSTRAINT idempotency_store_key_tenant_unique 
UNIQUE (idempotency_key, tenant_id);
```

---

### **Error: RLS policy violation**

**Solution**: Ensure RLS is enabled and policies exist:

```sql
-- Enable RLS
ALTER TABLE cards ENABLE ROW LEVEL SECURITY;
ALTER TABLE idempotency_store ENABLE ROW LEVEL SECURITY;
ALTER TABLE card_usage ENABLE ROW LEVEL SECURITY;

-- Check policies
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual
FROM pg_policies
WHERE tablename IN ('cards', 'idempotency_store', 'card_usage');
```

---

## 📝 Cleanup

To clean up test data after running:

```sql
-- Delete test cards
DELETE FROM cards WHERE created_by = 'test-suite';

-- Delete test idempotency entries
DELETE FROM idempotency_store WHERE idempotency_key LIKE 'onboarding-session-%';

-- Delete test usage entries
DELETE FROM card_usage WHERE used_by = 'workflow-api';
```

---

## 🎯 CI/CD Integration

### **GitHub Actions Example**

```yaml
name: Supabase Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install PostgreSQL client
        run: sudo apt-get install -y postgresql-client
      
      - name: Run Supabase tests
        env:
          SUPABASE_DB_URL: ${{ secrets.SUPABASE_DB_URL }}
        run: |
          psql $SUPABASE_DB_URL -f scripts/test_cards_api_supabase.sql
```

---

## 📚 Related Documentation

- [Sprint 3 Day 1 Progress](../SPRINT_3_DAY_1_PROGRESS.md) - Database schema setup
- [Sprint 3 Day 2 Complete](../SPRINT_3_DAY_2_COMPLETE.md) - API implementation
- [Cards API Contract](../contracts/cards-api-v1.yaml) - OpenAPI specification

---

## ✅ Acceptance Criteria

These tests validate the **Day 2 Definition of Done**:

- ✅ Idempotency 100% with DB storage
- ✅ Atomic transactions for batch operations
- ✅ RLS tenant isolation
- ✅ Content deduplication
- ✅ Usage tracking

---

**Last Updated**: 2025-10-27  
**Sprint**: 3 - Day 2  
**Status**: ✅ Complete

