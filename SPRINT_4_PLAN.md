# SPRINT 4: INTEGRATION + HARDENING + CARD CENTER

**Status**: 📋 **PLANNED**  
**Estimated Duration**: 3-4 days  
**Dependencies**: Sprint 3 (Cards API) ✅ COMPLETE

---

## 🎯 SPRINT OBJECTIVE

Integrate Cards API with Onboarding and Workflow, add security hardening, and build minimal Card Center UI.

---

## 📋 SPRINT BREAKDOWN

### **Day 1: Onboarding Integration** (2-3 hours)

**Objective**: Onboarding API creates cards via Cards API

**Tasks**:
1. ✅ Update Onboarding API to call Cards API `/batch` endpoint
2. ✅ Store `card_ids` in onboarding session
3. ✅ Handle idempotency (use session ID as idempotency key)
4. ✅ Error handling (retry logic, fallback)
5. ✅ Integration tests (Onboarding → Cards)
6. ✅ Update OpenAPI contract

**Deliverables**:
- Modified `onboarding/api/v1/endpoints/complete.py`
- Cards API client integration
- 5 integration tests
- Updated OpenAPI spec

**Success Criteria**:
- Onboarding creates 4 cards (company, audience, voice, insight)
- `card_ids` stored in session
- Idempotency works (retry doesn't create duplicates)
- All tests passing

---

### **Day 2: Workflow Integration** (2-3 hours)

**Objective**: Workflow API retrieves cards and tracks usage

**Tasks**:
1. ✅ Update `ContextCardTool` to call Cards API `/retrieve` endpoint
2. ✅ Track usage via Cards API `/usage` endpoint
3. ✅ Cache cards in memory (TTL: 5 minutes)
4. ✅ Handle missing cards gracefully
5. ✅ Integration tests (Workflow → Cards)
6. ✅ Update OpenAPI contract

**Deliverables**:
- Modified `workflow/tools/context_card_tool.py`
- Cards API client integration
- In-memory cache (TTL: 5 minutes)
- 5 integration tests
- Updated OpenAPI spec

**Success Criteria**:
- Workflow retrieves cards by IDs
- Usage tracked for each card
- Cache reduces API calls
- All tests passing

---

### **Day 3: Security Hardening** (2-3 hours)

**Objective**: Add CORS, rate limiting, and authentication

**Tasks**:
1. ✅ CORS configuration (allow production domain)
2. ✅ Rate limiting (Redis-based, per-tenant)
3. ✅ API key authentication (service-to-service)
4. ✅ JWT authentication (user-facing)
5. ✅ Security headers (HSTS, CSP, X-Frame-Options)
6. ✅ Input validation (Pydantic models)
7. ✅ Security tests (OWASP Top 10)

**Deliverables**:
- CORS middleware
- Rate limiting middleware (Redis)
- Authentication middleware (API key + JWT)
- Security headers middleware
- 10 security tests
- Security documentation

**Success Criteria**:
- CORS allows only production domain
- Rate limiting blocks excessive requests
- Authentication required for all endpoints
- Security headers present in responses
- All security tests passing

---

### **Day 4: Card Center UI** (3-4 hours)

**Objective**: Build minimal UI to view and manage cards

**Tasks**:
1. ✅ Card list view (table with filters)
2. ✅ Card detail view (show content, usage stats)
3. ✅ Usage analytics (chart: usage over time)
4. ✅ Card search (by type, content)
5. ✅ Card soft delete (deactivate)
6. ✅ Responsive design (mobile-friendly)
7. ✅ Integration with Cards API

**Deliverables**:
- React components (CardList, CardDetail, UsageChart)
- API integration (fetch cards, usage stats)
- Responsive UI (Tailwind CSS)
- 5 UI tests (Playwright)

**Success Criteria**:
- Users can view all cards
- Users can see usage stats
- Users can search/filter cards
- Users can soft-delete cards
- UI is responsive (mobile + desktop)

---

## 🎯 DEFINITION OF DONE (DoD)

### **Sprint-Level DoD**

| Criteria | Target | Notes |
|----------|--------|-------|
| Onboarding integration | ✅ | Creates cards via Cards API |
| Workflow integration | ✅ | Retrieves cards + tracks usage |
| CORS configured | ✅ | Production domain only |
| Rate limiting | ✅ | Redis-based, per-tenant |
| Authentication | ✅ | API key + JWT |
| Security headers | ✅ | HSTS, CSP, X-Frame-Options |
| Card Center UI | ✅ | List, detail, usage analytics |
| All tests passing | ✅ | 25+ tests (integration + security + UI) |
| Documentation | ✅ | Security guide, UI guide |
| Performance | ✅ | p95 latency still meets SLOs |

---

## 📊 ESTIMATED METRICS

| Metric | Estimated Value |
|--------|-----------------|
| **Files Created** | 20 |
| **Files Modified** | 15 |
| **Lines of Code** | ~3,000 |
| **Endpoints** | 6 (no new endpoints) |
| **Tests** | 25 (10 integration + 10 security + 5 UI) |
| **UI Components** | 5 (CardList, CardDetail, UsageChart, SearchBar, FilterPanel) |
| **Documentation Files** | 3 (Security, UI, Integration) |
| **Git Commits** | 12 |

---

## 🏗️ ARCHITECTURE CHANGES

### **Before Sprint 4**

```
┌─────────────┐
│ Onboarding  │
│     API     │
└─────────────┘

┌─────────────┐
│  Workflow   │
│     API     │
└─────────────┘

┌─────────────┐
│   Cards     │
│     API     │
└─────────────┘
```

### **After Sprint 4**

```
┌─────────────┐
│ Onboarding  │ ──────► Cards API (create cards)
│     API     │
└─────────────┘

┌─────────────┐
│  Workflow   │ ──────► Cards API (retrieve + usage)
│     API     │
└─────────────┘

┌─────────────┐
│   Cards     │ ◄────── Card Center UI (view + manage)
│     API     │
└─────────────┘
```

---

## 🎓 KEY FEATURES

### **1. Onboarding Integration**
- Onboarding creates 4 cards after collecting user data
- Cards stored in Cards API (not in Onboarding DB)
- `card_ids` returned to client for future use

### **2. Workflow Integration**
- Workflow retrieves cards by IDs
- Cards used as context for content generation
- Usage tracked for analytics

### **3. Security Hardening**
- CORS prevents unauthorized domains
- Rate limiting prevents abuse
- Authentication ensures only authorized clients
- Security headers protect against common attacks

### **4. Card Center UI**
- Users can view all their cards
- Users can see usage analytics
- Users can search/filter cards
- Users can soft-delete cards

---

## 🚀 USAGE EXAMPLES

### **1. Onboarding Creates Cards**

```python
# onboarding/api/v1/endpoints/complete.py

from fylle_cards_client import CardsClient

cards_client = CardsClient(base_url="http://cards-api:8002")

# Create cards
response = await cards_client.batch_create(
    tenant_id=session.tenant_id,
    idempotency_key=f"onboarding-{session.session_id}",
    cards=[
        {"card_type": "company", "content": company_data},
        {"card_type": "audience", "content": audience_data},
        {"card_type": "voice", "content": voice_data},
        {"card_type": "insight", "content": insight_data},
    ]
)

# Store card IDs
session.card_ids = [card["card_id"] for card in response["cards"]]
```

### **2. Workflow Retrieves Cards**

```python
# workflow/tools/context_card_tool.py

from fylle_cards_client import CardsClient

cards_client = CardsClient(base_url="http://cards-api:8002")

# Retrieve cards
cards = await cards_client.retrieve(
    tenant_id=tenant_id,
    card_ids=card_ids
)

# Track usage
for card in cards:
    await cards_client.track_usage(
        tenant_id=tenant_id,
        card_id=card["card_id"],
        workflow_id=workflow_id,
        workflow_type="premium_newsletter"
    )
```

### **3. Card Center UI**

```typescript
// card-center/src/components/CardList.tsx

import { useCards } from '../hooks/useCards';

export function CardList() {
  const { cards, loading, error } = useCards();
  
  if (loading) return <Spinner />;
  if (error) return <Error message={error} />;
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {cards.map(card => (
        <CardItem key={card.card_id} card={card} />
      ))}
    </div>
  );
}
```

---

## 🧪 TEST PLAN

### **Integration Tests** (10 tests)

**Onboarding → Cards** (5 tests):
1. Create cards successfully
2. Idempotency works (retry doesn't duplicate)
3. Handle Cards API errors gracefully
4. Store card IDs in session
5. Validate card content

**Workflow → Cards** (5 tests):
1. Retrieve cards successfully
2. Track usage successfully
3. Handle missing cards gracefully
4. Cache reduces API calls
5. Deduplication prevents duplicate usage events

### **Security Tests** (10 tests)

1. CORS blocks unauthorized domains
2. Rate limiting blocks excessive requests
3. Authentication required for all endpoints
4. Invalid API keys rejected
5. Expired JWT tokens rejected
6. SQL injection prevented
7. XSS prevented
8. CSRF prevented
9. Security headers present
10. Input validation works

### **UI Tests** (5 tests)

1. Card list renders correctly
2. Card detail shows usage stats
3. Search filters cards
4. Soft delete deactivates card
5. Responsive design works on mobile

---

## 📚 DOCUMENTATION

| Document | Status | Location |
|----------|--------|----------|
| Sprint 4 Plan | ✅ | SPRINT_4_PLAN.md |
| Security Guide | ⏳ | docs/SECURITY.md |
| UI Guide | ⏳ | card-center/README.md |
| Integration Guide | ⏳ | docs/INTEGRATION.md |

---

## 🎯 NEXT STEPS AFTER SPRINT 4

### **Sprint 5: Advanced Features** (Future)

1. **Card Versioning**: Track changes to cards over time
2. **Card Templates**: Pre-defined card templates for common use cases
3. **Card Sharing**: Share cards between tenants (with permissions)
4. **Card Export**: Export cards to JSON, CSV, PDF
5. **Card Import**: Import cards from external sources
6. **Advanced Analytics**: Usage trends, popular cards, etc.
7. **Webhooks**: Notify external systems when cards are created/updated
8. **GraphQL API**: Alternative to REST API

---

## ✅ SIGN-OFF

**Sprint 4 Status**: 📋 **PLANNED**

**Ready to start**: After Sprint 3 deployment + benchmarking

**Estimated Start Date**: 2025-10-28  
**Estimated End Date**: 2025-10-31

**Blockers**: None

---

**Status**: Ready for Sprint 3 Deployment + Benchmarking 🚀

