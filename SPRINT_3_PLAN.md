# 🚀 SPRINT 3 - CARDS API (Real Implementation)

**Sprint**: Sprint 3 - Cards API  
**Goal**: Replace mock Cards API with real PostgreSQL-backed implementation  
**Estimated Time**: 3-4 hours  
**Status**: 🟡 PLANNING

---

## 📋 Overview

Sprint 3 focuses on implementing the **real Cards API** with PostgreSQL storage, replacing the current mock implementation. This will make Cards the "center of truth" for context management.

### Current State
- ✅ Mock Cards API working (in-memory storage)
- ✅ OpenAPI contract defined (`contracts/cards-api-v1.yaml`)
- ✅ Auto-generated client (`fylle-cards-client==1.0.0`)
- ✅ Onboarding API using `/cards/batch` endpoint
- ✅ Workflow API using `/cards/retrieve` endpoint

### Target State
- 🎯 PostgreSQL database with cards table
- 🎯 Real `/cards/batch` endpoint with persistent storage
- 🎯 Persistent idempotency storage
- 🎯 Row-Level Security (RLS) for multi-tenancy
- 🎯 Card CRUD endpoints
- 🎯 Integration tests with real database

---

## 📅 Day-by-Day Plan

### **Day 1: Database Schema + Basic CRUD** (1.5 hours)

**Goal**: Set up PostgreSQL database and implement basic card storage

**Tasks**:
1. Create database schema (cards table, idempotency table)
2. Implement Row-Level Security (RLS) policies
3. Create database connection pool
4. Implement basic CRUD operations (create, get, list)
5. Unit tests for database layer

**Files to Create**:
- `cards/infrastructure/database/schema.sql` - Database schema
- `cards/infrastructure/database/connection.py` - Connection pool
- `cards/infrastructure/repositories/card_repository.py` - Repository pattern
- `tests/unit/test_card_repository.py` - Unit tests

**Files to Modify**:
- `.env` - Add DATABASE_URL
- `requirements.txt` - Add asyncpg, sqlalchemy

**Deliverables**:
- ✅ PostgreSQL schema with RLS
- ✅ Card repository with CRUD operations
- ✅ Unit tests passing

---

### **Day 2: Batch Creation + Idempotency** (1 hour)

**Goal**: Implement `/cards/batch` endpoint with persistent idempotency

**Tasks**:
1. Implement batch card creation endpoint
2. Persistent idempotency storage (idempotency table)
3. Transaction support for atomic batch creation
4. Error handling and rollback
5. Integration tests

**Files to Create**:
- `cards/api/v1/endpoints/cards_v1.py` - FastAPI endpoints
- `cards/api/v1/models/cards.py` - Pydantic models
- `cards/infrastructure/repositories/idempotency_repository.py` - Idempotency storage
- `tests/integration/test_cards_batch.py` - Integration tests

**Files to Modify**:
- `cards/infrastructure/repositories/card_repository.py` - Add batch creation

**Deliverables**:
- ✅ POST /api/v1/cards/batch working
- ✅ Persistent idempotency storage
- ✅ Atomic transactions
- ✅ Integration tests passing

---

### **Day 3: Retrieval + Usage Tracking** (0.5 hours)

**Goal**: Implement card retrieval and usage tracking endpoints

**Tasks**:
1. Implement `/cards/retrieve` endpoint (batch retrieval)
2. Implement `/cards/{id}/usage` endpoint
3. Usage tracking with deduplication
4. Partial result handling
5. Integration tests

**Files to Create**:
- `cards/infrastructure/repositories/usage_repository.py` - Usage tracking
- `tests/integration/test_cards_retrieve.py` - Integration tests

**Files to Modify**:
- `cards/api/v1/endpoints/cards_v1.py` - Add retrieve and usage endpoints

**Deliverables**:
- ✅ POST /api/v1/cards/retrieve working
- ✅ POST /api/v1/cards/{id}/usage working
- ✅ Usage tracking with dedup
- ✅ Integration tests passing

---

### **Day 4: E2E Testing + Deployment** (1 hour)

**Goal**: End-to-end testing and deployment preparation

**Tasks**:
1. E2E tests: Onboarding → Cards → Workflow
2. Performance testing (p95 latency, throughput)
3. Database migrations setup
4. Docker Compose for local development
5. Documentation

**Files to Create**:
- `tests/e2e/test_full_flow.py` - E2E tests
- `cards/infrastructure/database/migrations/` - Migration scripts
- `docker-compose.yml` - Local development setup
- `SPRINT_3_COMPLETE.md` - Sprint summary

**Files to Modify**:
- `README.md` - Update with Cards API documentation

**Deliverables**:
- ✅ E2E tests passing
- ✅ Performance validated (p95 ≤ 100ms)
- ✅ Docker Compose working
- ✅ Documentation complete

---

## 🗄️ Database Schema

### **cards** table
```sql
CREATE TABLE cards (
    card_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    card_type VARCHAR(50) NOT NULL CHECK (card_type IN ('company', 'audience', 'voice', 'insight')),
    content JSONB NOT NULL,
    content_hash VARCHAR(64) NOT NULL,
    source_session_id UUID,
    created_by VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Indexes
    INDEX idx_cards_tenant_id (tenant_id),
    INDEX idx_cards_card_type (card_type),
    INDEX idx_cards_content_hash (content_hash),
    INDEX idx_cards_source_session (source_session_id),
    
    -- Unique constraint for deduplication
    UNIQUE (tenant_id, card_type, content_hash)
);

-- Row-Level Security
ALTER TABLE cards ENABLE ROW LEVEL SECURITY;

CREATE POLICY cards_tenant_isolation ON cards
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);
```

### **idempotency_store** table
```sql
CREATE TABLE idempotency_store (
    idempotency_key VARCHAR(255) PRIMARY KEY,
    tenant_id UUID NOT NULL,
    response_payload JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Index for cleanup
    INDEX idx_idempotency_expires_at (expires_at)
);

-- Row-Level Security
ALTER TABLE idempotency_store ENABLE ROW LEVEL SECURITY;

CREATE POLICY idempotency_tenant_isolation ON idempotency_store
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);
```

### **card_usage** table
```sql
CREATE TABLE card_usage (
    usage_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    card_id UUID NOT NULL REFERENCES cards(card_id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL,
    workflow_id UUID,
    workflow_type VARCHAR(100),
    used_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Indexes
    INDEX idx_usage_card_id (card_id),
    INDEX idx_usage_tenant_id (tenant_id),
    INDEX idx_usage_workflow_id (workflow_id),
    INDEX idx_usage_used_at (used_at)
);

-- Row-Level Security
ALTER TABLE card_usage ENABLE ROW LEVEL SECURITY;

CREATE POLICY usage_tenant_isolation ON card_usage
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);
```

---

## 🔧 Technology Stack

### Database
- **PostgreSQL 15+** - Main database
- **asyncpg** - Async PostgreSQL driver
- **SQLAlchemy 2.0** - ORM (optional, for migrations)

### API
- **FastAPI** - Already in use
- **Pydantic** - Already in use
- **uvicorn** - Already in use

### Testing
- **pytest** - Already in use
- **pytest-asyncio** - For async tests
- **pytest-postgresql** - For test database

---

## 📊 Success Criteria

### Performance
- ✅ POST /cards/batch: p95 ≤ 100ms (4 cards)
- ✅ POST /cards/retrieve: p95 ≤ 50ms (4 cards)
- ✅ POST /cards/{id}/usage: p95 ≤ 20ms

### Reliability
- ✅ Idempotency: 100% replay protection
- ✅ Transactions: Atomic batch creation
- ✅ RLS: Multi-tenant isolation verified

### Testing
- ✅ Unit tests: 100% coverage on repositories
- ✅ Integration tests: All endpoints tested
- ✅ E2E tests: Full flow working

---

## 🚀 Next Steps

**Immediate**:
1. Set up PostgreSQL database (local + Supabase)
2. Create database schema with RLS
3. Implement card repository

**Follow-up**:
1. Migrate Onboarding API to use real Cards API
2. Migrate Workflow API to use real Cards API
3. Deploy to production

---

**Sprint Created**: 2025-10-26  
**Estimated Completion**: 2025-10-27  
**Status**: 🟡 PLANNING

