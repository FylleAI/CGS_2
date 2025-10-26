# 🎯 Fase 0 - Refinements Summary

**Data**: 2025-10-26  
**Obiettivo**: Riepilogo revisioni applicate alla Fase 0 del piano di migrazione

---

## 📋 REVISIONI APPLICATE

### **1. Shared Package Unico (Enum & Mapping Bloccati)** 🔒

**Problema**: Rischio duplicazione enum e mapping tra repos  
**Soluzione**: Package `fylle-shared==0.1.0` installabile

**Contenuto**:
```python
# fylle_shared/enums.py
class CardType(str, Enum):
    COMPANY = "company"
    AUDIENCE = "audience"
    VOICE = "voice"
    INSIGHT = "insight"

# fylle_shared/mappings.py
SNAPSHOT_TO_CARD_MAPPING = {
    "company": CardType.COMPANY,
    "audience": CardType.AUDIENCE,
    "voice": CardType.VOICE,
    "insights": CardType.INSIGHT
}
```

**Benefici**:
- ✅ Single source of truth per enum
- ✅ Nessuna duplicazione tra microservizi
- ✅ Versioning semantico (0.1.0, 0.2.0)
- ✅ Installabile via pip o Git submodule

---

### **2. Client Auto-Generati (NO Manual)** 🤖

**Problema**: Client manuali portano a drift vs API contract  
**Soluzione**: Client 100% auto-generati da OpenAPI specs

**Tool**: `openapi-python-client`

```bash
openapi-python-client generate \
  --path contracts/cards-api-v1.yaml \
  --output-path clients/python/fylle-cards-client
```

**Policy Enforcement**:
- ✅ Zero client manuali (enforced in code review)
- ✅ Client include retry, timeout, tracing
- ✅ Versioning: `fylle-cards-client==1.0.0` = API v1

**Usage**:
```python
from fylle_cards_client import Client as CardsClient

cards_client = CardsClient(base_url="http://localhost:8002")
response = await cards_client.cards.create_cards_batch(request)
```

---

### **3. Contract Tests as CI Gate** 🚦

**Problema**: Implementazione può divergere da contratto  
**Soluzione**: Contract tests obbligatori per merge

**Tool**: `schemathesis`

```python
@schema.parametrize()
def test_api_contract(case):
    response = case.call()
    case.validate_response(response)  # Valida vs OpenAPI schema
```

**CI Pipeline**:
```yaml
# .github/workflows/contract-tests.yml
- name: Run Contract Tests
  run: |
    schemathesis run \
      --base-url http://localhost:8002 \
      contracts/cards-api-v1.yaml \
      --checks all \
      --exitfirst  # Fail fast
```

**Merge Gate**: ❌ PR cannot merge if contract tests fail

---

### **4. Golden Examples in Contracts** 📋

**Problema**: Spec astratti, difficili da capire  
**Soluzione**: Esempi "golden" completi per ogni endpoint critico

**Esempio**:
```yaml
# contracts/cards-api-v1.yaml
paths:
  /cards/batch:
    post:
      requestBody:
        content:
          application/json:
            examples:
              onboarding_snapshot:
                summary: Cards from onboarding session
                value:
                  tenant_id: "123e4567-..."
                  company_snapshot:
                    company: {...}
                    audience: {...}
                    voice: {...}
                    insights: {...}
                  idempotency_key: "onboarding-456e7890-batch"
      responses:
        '201':
          content:
            application/json:
              examples:
                success:
                  value:
                    cards: [...]
                    created_count: 4
```

**Benefici**:
- ✅ Spec più comprensibili
- ✅ Golden examples testati automaticamente
- ✅ Documentazione by example

---

### **5. Superficie Ridotta v1** 🎯

**Problema**: Troppa complessità in v1  
**Soluzione**: Taglia features non essenziali → v1.1

**Cards v1 (Incluso)**:
- ✅ `POST /cards` - Create card
- ✅ `POST /cards/batch` - Batch creation
- ✅ `GET /cards/{card_id}` - Get by ID
- ✅ `GET /cards` - List con filtering
- ✅ `POST /cards/retrieve` - Retrieve by IDs
- ✅ `POST /cards/{card_id}/usage` - Usage tracking

**Cards v1 (Escluso → v1.1)**:
- ❌ `POST /cards/{card_id}/relationships` - Card relationships
- ❌ `GET /cards/search` - Semantic search
- ❌ `POST /cards/{card_id}/performance` - Performance tracking

**Workflow v1**:
- ✅ Accept `card_ids` (preferred)
- ✅ Accept `context` (deprecated, backward compat)
- ❌ Remove `context` in v2.0 (6 months notice)

---

### **6. Idempotency & Deduplication** 🔐

**Problema**: Retry non sicuri, duplicati  
**Soluzione**: Hash deterministico + Idempotency-Key

**Hashing**:
```python
# fylle_shared/utils/hashing.py

def generate_content_hash(payload: dict) -> str:
    """Deterministic hash per dedup."""
    normalized = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(normalized.encode()).hexdigest()

def generate_idempotency_key(session_id: UUID, operation: str) -> str:
    """Generate idempotency key for retry safety."""
    return f"{operation}-{session_id}"
```

**Cards API**:
```python
@app.post("/api/v1/cards/batch")
async def create_cards_batch(request: CreateCardsBatchRequest):
    # Check idempotency
    if request.idempotency_key:
        existing = await card_repo.find_by_idempotency_key(
            request.idempotency_key, 
            tenant_id
        )
        if existing:
            return CardBatchResponse(cards=existing, created_count=0)
    
    # Create new cards
    ...
```

**Database**:
```sql
CREATE TABLE context_cards (
    ...
    content_hash TEXT NOT NULL,
    idempotency_key TEXT,
    UNIQUE(tenant_id, idempotency_key)
);
```

---

### **7. Multi-Tenant Security** 🔒

**Problema**: Tenant isolation non garantita  
**Soluzione**: X-Tenant-ID obbligatorio + RLS + Rate limiting

**X-Tenant-ID Required**:
```python
async def get_tenant_id(request: Request) -> UUID:
    tenant_id = request.headers.get("X-Tenant-ID")
    if not tenant_id:
        raise HTTPException(401, "X-Tenant-ID header required")
    return UUID(tenant_id)
```

**RLS Enforcement**:
```python
async with db.begin():
    await db.execute(text(f"SET app.current_tenant_id = '{tenant_id}'"))
    # All queries now filtered by tenant_id via RLS
```

**Rate Limiting**:
```python
from slowapi import Limiter

limiter = Limiter(key_func=lambda: request.headers.get("X-Tenant-ID"))

@app.post("/cards/batch")
@limiter.limit("100/minute")  # Per tenant
async def create_cards_batch(...):
    ...
```

---

### **8. Cache LRU con TTL Differenziato** ⚡

**Problema**: Latenza chiamate API tra microservizi  
**Soluzione**: Cache locale in Workflow con TTL per tipo

**Implementation**:
```python
class CardCache:
    def __init__(self):
        self.cache = TTLCache(maxsize=1000, ttl=3600)
        
        # TTL differenziato per tipo
        self.ttl_by_type = {
            CardType.VOICE: 7200,      # 2h (cambia raramente)
            CardType.TOPIC: 7200,      # 2h
            CardType.COMPANY: 3600,    # 1h (cambia moderatamente)
            CardType.AUDIENCE: 3600,   # 1h
            CardType.INSIGHT: 1800,    # 30min (cambia frequentemente)
            CardType.CAMPAIGN: 1800,   # 30min
        }
```

**Benefici**:
- ✅ Riduce latenza (cache hit)
- ✅ Riduce carico su Cards API
- ✅ TTL ottimizzato per frequenza cambio

**Target**: Cache hit rate > 70% dopo warmup

---

### **9. Observability Minimo Vitale** 📊

**Problema**: Debugging difficile in ambiente distribuito  
**Soluzione**: Trace ID propagation + 4 metriche chiave

**Trace ID Propagation**:
```python
# fylle_shared/utils/tracing.py

def get_trace_id(request: Request) -> str:
    trace_id = request.headers.get("X-Trace-ID")
    if not trace_id:
        trace_id = str(uuid4())
    return trace_id

# Propagate to downstream services
headers = {
    "X-Trace-ID": trace_id,
    "X-Session-ID": session_id,
    "X-Tenant-ID": str(tenant_id)
}
```

**4 Metriche Chiave** (Prometheus):
```python
# 1. p95 latency Cards API
cards_retrieve_p95_ms = Histogram("cards_retrieve_duration_ms")

# 2. Cache hit rate Workflow
workflow_cache_hit_rate = Gauge("workflow_cache_hit_rate")

# 3. Card usage events
card_usage_events_total = Counter(
    "card_usage_events_total",
    ["card_id", "workflow_type"]
)

# 4. % workflow usando card_ids
workflow_card_only_percentage = Gauge("workflow_card_only_percentage")
```

**Logging Strutturato** (JSON):
```python
logger.info(
    "cards_retrieved",
    extra={
        "trace_id": trace_id,
        "tenant_id": tenant_id,
        "card_ids": card_ids,
        "duration_ms": duration,
        "cache_hit": cache_hit
    }
)
```

---

### **10. Performance Indexes** 🚀

**Problema**: Query lente su grandi dataset  
**Soluzione**: Covering index + GIN indexes

**Database Indexes**:
```sql
-- Covering index per query più frequente
CREATE INDEX idx_cards_tenant_type_active 
ON context_cards(tenant_id, card_type, is_active);

-- GIN indexes per JSONB e array
CREATE INDEX idx_cards_content_gin 
ON context_cards USING GIN (content);

CREATE INDEX idx_cards_tags_gin 
ON context_cards USING GIN (tags);

-- Index per deduplication
CREATE INDEX idx_cards_content_hash 
ON context_cards(content_hash);
```

**Target**: p95 < 100ms per `/cards/retrieve`

---

## ✅ CHECKLIST FASE 0

| # | Task | Status |
|---|------|--------|
| 1 | `fylle-shared==0.1.0` package creato | ⬜ |
| 2 | Enum e mapping bloccati in shared | ⬜ |
| 3 | OpenAPI specs con golden examples | ⬜ |
| 4 | Client auto-generati (cards, workflow) | ⬜ |
| 5 | Contract tests setup in CI | ⬜ |
| 6 | Idempotency & hashing utils | ⬜ |
| 7 | Multi-tenant security (RLS, rate limit) | ⬜ |
| 8 | Cache LRU con TTL differenziato | ⬜ |
| 9 | Trace ID propagation helpers | ⬜ |
| 10 | 4 metriche chiave definite | ⬜ |

---

## 🎯 SUCCESS CRITERIA

### **Fase 0 Completata Quando**:
- ✅ 3 OpenAPI specs validati
- ✅ 2 client auto-generati installabili
- ✅ Contract tests passing in CI
- ✅ Shared package pubblicato
- ✅ Idempotency logic testata
- ✅ Security policies documentate
- ✅ Cache strategy implementata
- ✅ Observability setup completo

---

**Next Step**: Iniziare implementazione Fase 0 (1 settimana)

