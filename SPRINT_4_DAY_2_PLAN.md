# 🚀 SPRINT 4 DAY 2: WORKFLOW INTEGRATION & USAGE TRACKING

**Date**: 2025-10-28 (Planned)  
**Status**: ⏳ **READY TO START**  
**Estimated Duration**: 4-6 hours

---

## 🎯 OBJECTIVES

Integrate card_ids from Onboarding into Workflow execution and verify end-to-end usage tracking.

**Key Goals**:
1. ✅ Workflow consumes card_ids from Onboarding
2. ✅ Usage tracking works end-to-end
3. ✅ Staging deployment verified
4. ✅ Benchmark p95 ≤ 2.5s confirmed

---

## 📋 TASKS

### **TASK 1: Workflow Integration** (2-3 hours)

**Objective**: Update Workflow API to consume card_ids from Onboarding

**Subtasks**:
1. ⏳ Modify Workflow execution to accept `card_ids` parameter
2. ⏳ Fetch cards from Cards API using `card_ids`
3. ⏳ Use cards as context for content generation
4. ⏳ Add error handling for missing/partial cards
5. ⏳ Add metrics for card usage in workflow

**Files to Modify**:
- `api/rest/v1/endpoints/workflow_v1.py`
- `workflow/application/use_cases/execute_workflow.py`
- `workflow/domain/services/context_builder.py` (if exists)

**Expected Outcome**:
```python
# Workflow execution with card_ids
POST /api/v1/workflows/execute
{
  "workflow_type": "linkedin_post",
  "card_ids": ["id1", "id2", "id3", "id4"],  # From Onboarding
  "additional_context": "..."
}

# Workflow fetches cards from Cards API
# Uses cards as context for generation
# Returns generated content
```

---

### **TASK 2: Usage Tracking End-to-End** (1-2 hours)

**Objective**: Verify usage tracking works from Onboarding → Cards → Workflow

**Subtasks**:
1. ⏳ Add usage tracking when cards are fetched by Workflow
2. ⏳ Verify usage metrics in Prometheus
3. ⏳ Create E2E test for full flow
4. ⏳ Verify usage data in database (if applicable)

**Metrics to Track**:
- `cards_api_usage_total{tenant_id, card_type, source="workflow"}`
- `workflow_cards_fetched_total{tenant_id, workflow_type}`
- `workflow_execution_duration_seconds{tenant_id, workflow_type}`

**Expected Flow**:
```
1. Onboarding creates 4 cards
   → cards_api_requests_total{endpoint="/batch"} +1
   
2. Workflow fetches 4 cards
   → cards_api_requests_total{endpoint="/retrieve"} +1
   → cards_api_usage_total{source="workflow"} +4
   
3. Workflow executes with cards
   → workflow_cards_fetched_total +4
   → workflow_execution_duration_seconds recorded
```

---

### **TASK 3: Staging Deployment** (1 hour)

**Objective**: Deploy to staging and verify functionality

**Subtasks**:
1. ⏳ Run `./scripts/deploy_staging.sh`
2. ⏳ Verify all services healthy in staging
3. ⏳ Run E2E test in staging
4. ⏳ Verify metrics in staging Prometheus

**Staging URLs** (example):
- Workflow API: `https://staging-workflow.fylle.ai`
- Onboarding API: `https://staging-onboarding.fylle.ai`
- Cards API: `https://staging-cards.fylle.ai`
- Prometheus: `https://staging-prometheus.fylle.ai`

**Verification**:
```bash
# Health checks
curl https://staging-workflow.fylle.ai/health
curl https://staging-onboarding.fylle.ai/health
curl https://staging-cards.fylle.ai/health

# E2E test
python3 test_complete_e2e.py --env staging

# Metrics
curl https://staging-prometheus.fylle.ai/api/v1/query?query=onboarding_cards_created_total
```

---

### **TASK 4: Benchmark p95** (30 min)

**Objective**: Verify p95 latency ≤ 2.5s in staging

**Subtasks**:
1. ⏳ Run load test with 100 requests
2. ⏳ Measure p95 latency
3. ⏳ Generate benchmark report
4. ⏳ Verify p95 ≤ 2.5s

**Load Test Script**:
```bash
# Run 100 requests with 10 concurrent users
./scripts/load_test_onboarding.sh \
  --requests 100 \
  --concurrency 10 \
  --env staging
```

**Expected Results**:
```
Requests: 100
Concurrency: 10
Duration: ~10s

Latency:
  p50: < 500ms
  p95: < 2.5s  ✅
  p99: < 5s

Success Rate: 100%
Cards Created: 400/400 (100%)
```

---

### **TASK 5: Card Center v1 Scope Update** (30 min)

**Objective**: Update Card Center v1 scope for Sprint 4 Day 4

**Subtasks**:
1. ⏳ Review current Card Center scope
2. ⏳ Add new features based on Day 1-2 learnings
3. ⏳ Update timeline and priorities
4. ⏳ Document dependencies

**Potential Updates**:
- Card versioning (v1, v2, ...)
- Card templates
- Card validation rules
- Card lifecycle management
- Card search/filter
- Card analytics dashboard

---

## 📊 DEFINITION OF DONE

| Requirement | Target | Verification |
|-------------|--------|--------------|
| Workflow consumes card_ids | ✅ Implemented | E2E test passes |
| Usage tracking end-to-end | ✅ Working | Metrics visible in Prometheus |
| Staging deployment | ✅ Deployed | All services healthy |
| Benchmark p95 ≤ 2.5s | ✅ Verified | Load test report |
| Card Center v1 scope | ✅ Updated | Document created |

---

## 🧪 TESTS TO CREATE

### **Test 1: Workflow Integration E2E**
```python
# test_workflow_integration_e2e.py

1. Create Onboarding session
2. Submit answers → Get card_ids
3. Execute Workflow with card_ids
4. Verify content generated
5. Verify cards were used as context
6. Verify usage metrics updated
```

### **Test 2: Usage Tracking**
```python
# test_usage_tracking.py

1. Create cards via Onboarding
2. Fetch cards via Workflow
3. Verify usage metrics:
   - cards_api_usage_total +4
   - workflow_cards_fetched_total +4
4. Verify usage data in database
```

### **Test 3: Staging E2E**
```bash
# test_staging_e2e.sh

1. Deploy to staging
2. Run health checks
3. Run E2E test
4. Verify metrics
5. Run load test
6. Generate report
```

---

## 📈 SUCCESS METRICS

| Metric | Target | Measurement |
|--------|--------|-------------|
| Workflow integration | 100% | E2E test pass rate |
| Usage tracking accuracy | 100% | Metrics match actual usage |
| Staging uptime | 99.9% | Health check success rate |
| p95 latency | ≤ 2.5s | Load test results |
| Card usage rate | 100% | All workflows use cards |

---

## 🔧 TECHNICAL DETAILS

### **Workflow API Changes**

**Before** (Sprint 4 Day 1):
```python
POST /api/v1/workflows/execute
{
  "workflow_type": "linkedin_post",
  "context": {
    "company": "...",
    "audience": "...",
    "voice": "...",
    "insight": "..."
  }
}
```

**After** (Sprint 4 Day 2):
```python
POST /api/v1/workflows/execute
{
  "workflow_type": "linkedin_post",
  "card_ids": ["id1", "id2", "id3", "id4"],  # NEW!
  "additional_context": "..."  # Optional
}

# Workflow fetches cards from Cards API
# Builds context from cards
# Executes workflow with card-based context
```

### **Cards API Usage**

```python
# Workflow fetches cards
GET /api/v1/cards/retrieve
{
  "card_ids": ["id1", "id2", "id3", "id4"]
}

# Response
{
  "cards": [
    {"card_id": "id1", "card_type": "company", "content": {...}},
    {"card_id": "id2", "card_type": "audience", "content": {...}},
    {"card_id": "id3", "card_type": "voice", "content": {...}},
    {"card_id": "id4", "card_type": "insight", "content": {...}}
  ],
  "partial_result": false
}

# Workflow builds context
context = {
  "company": cards[0].content,
  "audience": cards[1].content,
  "voice": cards[2].content,
  "insight": cards[3].content
}
```

---

## 🚀 NEXT STEPS AFTER DAY 2

### **Sprint 4 Day 3**: Error Handling & Resilience
- Retry logic for Cards API failures
- Fallback to cached cards
- Partial card handling
- Circuit breaker implementation

### **Sprint 4 Day 4**: Card Center v1
- Card versioning
- Card templates
- Card validation
- Card lifecycle management

### **Sprint 4 Day 5**: Production Readiness
- Security audit
- Performance optimization
- Documentation finalization
- Deployment automation

---

## 📝 NOTES

### **Dependencies**
- ✅ Sprint 4 Day 1 complete
- ✅ Cards API running
- ✅ Onboarding API running
- ⏳ Staging environment ready

### **Risks**
- ⚠️ Staging environment availability
- ⚠️ Load test infrastructure
- ⚠️ Network latency in staging

### **Assumptions**
- Cards API is stable and performant
- Onboarding API creates cards reliably
- Workflow API can be modified without breaking changes

---

## 🎯 SUMMARY

Sprint 4 Day 2 focuses on **closing the loop** between Onboarding, Cards, and Workflow:

1. ✅ Workflow consumes card_ids from Onboarding
2. ✅ Usage tracking works end-to-end
3. ✅ Staging deployment verified
4. ✅ Performance benchmarks met

**Estimated Duration**: 4-6 hours  
**Complexity**: Medium  
**Priority**: High

---

**Plan Created**: 2025-10-27  
**Author**: Augment Agent  
**Sprint**: Sprint 4 Day 2  
**Status**: ⏳ READY TO START

