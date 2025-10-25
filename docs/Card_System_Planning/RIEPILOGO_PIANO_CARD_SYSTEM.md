# 📋 RIEPILOGO ESECUTIVO - Piano Card System V1

**Data**: 2025-10-25  
**Scope**: MVP delle prime 4 card atomiche  
**Timeline**: 3 settimane  
**Effort**: ~40 story points

---

## 🎯 DECISIONE ARCHITETTURALE CRITICA

### ✅ RISPOSTA: Card Service come modulo dentro CGS Core

**NON** come microservizio separato perché:
1. ✅ Evita complessità di deployment
2. ✅ Condivide database (Supabase)
3. ✅ Logica coesa con generazione contenuti
4. ✅ Scalabilità futura garantita

**Struttura**:
```
CGS Core Engine
├── card_service/          # NUOVO modulo
├── workflow_engine/       # Esiste
├── agent_orchestration/   # Esiste
└── content_generation/    # Esiste
```

---

## 📊 LE 4 CARD INIZIALI

### 1. **ProductCard** - Value Proposition
```
value_proposition, features, differentiators, use_cases, target_market
```

### 2. **PersonaCard** - ICP Profile
```
icp_profile, pain_points, goals, preferred_language, communication_channels
```

### 3. **CampaignCard** - Campaign Strategy
```
objective, key_messages, tone, target_personas, assets_produced
```

### 4. **TopicCard** - Content Topics
```
keywords, angles, related_content, trend_status, frequency
```

---

## 🔄 FLUSSO DATI COMPLETO

```
1. User Input
   ↓
2. Onboarding Microservice
   ├─ Research (Perplexity)
   ├─ Synthesize (Gemini)
   └─ Create CompanySnapshot
   ↓
3. Card Service (NUOVO)
   ├─ Convert Snapshot → 4 Cards
   ├─ Save to Database
   └─ Link Cards
   ↓
4. CGS Core Engine
   ├─ Read Cards as RAG
   ├─ Execute Workflow
   └─ Generate Content
   ↓
5. Frontend
   └─ Display Results
```

---

## 🏗️ ARCHITETTURA LAYERS

### Domain Layer
```
card_entity.py          # BaseCard, ProductCard, PersonaCard, etc.
card_types.py           # Enums, constants
card_relationship.py    # CardRelationship entity
```

### Application Layer
```
create_card_use_case.py
update_card_use_case.py
get_card_use_case.py
list_cards_use_case.py
create_cards_from_snapshot_use_case.py  # KEY
get_cards_for_context_use_case.py       # KEY
```

### Infrastructure Layer
```
card_repository.py
card_relationship_repository.py
migrations/005_create_card_tables.sql
```

### API Layer
```
card_routes.py
relationship_routes.py
card_schemas.py
```

---

## 🗄️ DATABASE SCHEMA

### context_cards
```sql
id, tenant_id, card_type, title, content (JSONB), metrics (JSONB),
version, is_active, created_by, updated_by, created_at, updated_at
```

### card_relationships
```sql
id, source_card_id, target_card_id, relationship_type, strength, created_at
```

---

## 🔌 INTEGRAZIONI CHIAVE

### 1. Onboarding → Card Service
```python
# Dopo snapshot, crea 4 card atomiche
cards = await create_cards_from_snapshot(snapshot, tenant_id)
```

### 2. Card Service → CGS
```python
# CGS legge card come RAG context
cards = await get_cards_for_context(tenant_id, card_types)
```

### 3. Frontend → Card Service
```typescript
// CRUD operations via API
cardApi.createCard(card)
cardApi.updateCard(id, updates)
cardApi.linkCards(sourceId, targetId, type)
```

---

## 📅 TIMELINE SETTIMANALE

### Settimana 1: Foundation
- [ ] Database schema
- [ ] Pydantic models
- [ ] Repository
- [ ] Use cases

### Settimana 2: API + Integration
- [ ] API endpoints
- [ ] Onboarding integration
- [ ] Tests
- [ ] Documentation

### Settimana 3: Frontend + CGS
- [ ] Frontend types
- [ ] Card editors
- [ ] CGS integration
- [ ] E2E testing

---

## ✅ DELIVERABLES

### Week 1
```
✅ Migration SQL (context_cards, card_relationships)
✅ Pydantic models (4 card types)
✅ Repository (CRUD)
✅ Use cases (5 use cases)
```

### Week 2
```
✅ API endpoints (CRUD + relationships)
✅ Onboarding integration
✅ Unit + integration tests
✅ API documentation
```

### Week 3
```
✅ TypeScript types
✅ Card editors (4 specialized)
✅ CGS integration
✅ E2E tests
✅ Production ready
```

---

## 📊 METRICHE DI SUCCESSO

- [ ] 4 card types creati e funzionanti
- [ ] CRUD API 100% operativo
- [ ] Relationships linking funziona
- [ ] Multi-tenant isolation verificato
- [ ] Integrazione Onboarding → Card → CGS
- [ ] Test coverage >80%
- [ ] Performance <500ms per query
- [ ] Zero breaking changes

---

## 🔐 MULTI-TENANCY

### Row-Level Security (RLS)
```sql
-- Users can only see their tenant's cards
ALTER TABLE context_cards ENABLE ROW LEVEL SECURITY;
CREATE POLICY "tenant_isolation" ON context_cards
  USING (tenant_id = auth.uid());
```

### Backend Validation
```python
# Ogni operazione verifica tenant_id
if card.tenant_id != current_tenant_id:
    raise PermissionError("Access denied")
```

---

## 🚀 PROSSIMI STEP

### Oggi (2025-10-25)
- [ ] Review architettura con team
- [ ] Approvazione piano
- [ ] Assegnazione task

### Domani (2025-10-26)
- [ ] Creare branch feature
- [ ] Setup cartelle
- [ ] Iniziare migration SQL

### Settimana 1
- [ ] Completare foundation
- [ ] Daily standup
- [ ] Mid-week review

### Settimana 2
- [ ] API endpoints
- [ ] Integration testing
- [ ] Friday demo

### Settimana 3
- [ ] Frontend UI
- [ ] E2E testing
- [ ] Production deployment

---

## 📚 DOCUMENTI CORRELATI

1. **PIANO_CARD_SYSTEM_V1.md** - Piano dettagliato
2. **ARCHITETTURA_CARD_SERVICE.md** - Architettura completa
3. **CARD_MODELS_DEFINITION.md** - Modelli Pydantic + TypeScript
4. **PIANO_IMPLEMENTAZIONE_SETTIMANALE.md** - Timeline settimanale

---

## 🎯 VISIONE FUTURA (Post-MVP)

### Phase 2: Feedback System
- Card feedback table
- Performance metrics tracking
- Automated card evolution

### Phase 3: Agent Integration
- Agents scrivono su card
- Versioning + audit trail
- Conflict resolution

### Phase 4: Advanced RAG
- Semantic search
- Vector embeddings
- Similarity matching

---

## ✨ CONCLUSIONE

**Card Service V1** è il primo passo verso un **centro di verità centralizzato** per la conoscenza aziendale.

Trasforma il sistema da:
```
Monolitico (CompanySnapshot) → Atomico (4 Card Types)
Read-only → Interactive
Statico → Evolutivo
```

**Timeline**: 3 settimane  
**Effort**: ~40 story points  
**Impact**: Alto (RAG centralizzato, scalabilità futura)


