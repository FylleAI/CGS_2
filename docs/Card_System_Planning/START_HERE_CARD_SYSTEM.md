# 🚀 START HERE - Card System V1 Planning

**Data**: 2025-10-25  
**Status**: ✅ Piano Completo  
**Prossimo Step**: Review con team

---

## 🎯 COSA STIAMO COSTRUENDO?

Un **Card Service** che centralizza la conoscenza aziendale in 4 card atomiche:

```
ProductCard (Value Proposition)
PersonaCard (ICP Profile)
CampaignCard (Campaign Strategy)
TopicCard (Content Topics)
```

---

## ❓ DOMANDA CRITICA: Microservizio o Modulo?

### ✅ RISPOSTA: Modulo dentro CGS Core

**Perché?**
- ✅ Evita complessità di deployment
- ✅ Condivide database (Supabase)
- ✅ Logica coesa
- ✅ Scalabilità futura

**Struttura**:
```
CGS Core Engine
├── card_service/          # NUOVO
├── workflow_engine/
├── agent_orchestration/
└── content_generation/
```

---

## 🔄 FLUSSO DATI

```
Onboarding
  ↓
Create CompanySnapshot
  ↓
Card Service (NUOVO)
  ├─ ProductCard
  ├─ PersonaCard
  ├─ CampaignCard
  └─ TopicCard
  ↓
CGS Core Engine
  ├─ Read Cards as RAG
  ├─ Execute Workflow
  └─ Generate Content
  ↓
Frontend
  └─ Display Results
```

---

## 📊 LE 4 CARD

### 1. ProductCard
```
value_proposition, features, differentiators, use_cases, target_market
```

### 2. PersonaCard
```
icp_profile, pain_points, goals, preferred_language, communication_channels
```

### 3. CampaignCard
```
objective, key_messages, tone, target_personas, assets_produced
```

### 4. TopicCard
```
keywords, angles, related_content, trend_status, frequency
```

---

## 📅 TIMELINE: 3 SETTIMANE

### Settimana 1: Foundation
```
✅ Database schema (context_cards, card_relationships)
✅ Pydantic models (4 card types)
✅ Repository (CRUD)
✅ Use cases (5 use cases)
```

### Settimana 2: API + Integration
```
✅ API endpoints (CRUD + relationships)
✅ Onboarding integration
✅ Tests (unit + integration)
✅ Documentation
```

### Settimana 3: Frontend + CGS
```
✅ TypeScript types
✅ Card editors (4 specialized)
✅ CGS integration
✅ E2E tests
```

---

## 📁 STRUTTURA CARTELLE

### Backend
```
core/card_service/
├── domain/
│   ├── card_entity.py
│   ├── card_types.py
│   └── card_relationship.py
├── application/
│   ├── create_card_use_case.py
│   ├── update_card_use_case.py
│   ├── get_card_use_case.py
│   ├── list_cards_use_case.py
│   ├── link_cards_use_case.py
│   ├── create_cards_from_snapshot_use_case.py
│   └── get_cards_for_context_use_case.py
├── infrastructure/
│   ├── card_repository.py
│   ├── card_relationship_repository.py
│   └── migrations/005_create_card_tables.sql
└── api/
    ├── card_routes.py
    ├── relationship_routes.py
    └── card_schemas.py
```

### Frontend
```
onboarding-frontend/src/
├── components/cards/
│   ├── CardEditor.tsx
│   ├── ProductCardEditor.tsx
│   ├── PersonaCardEditor.tsx
│   ├── CampaignCardEditor.tsx
│   └── TopicCardEditor.tsx
├── hooks/
│   ├── useCard.ts
│   └── useCardRelationships.ts
├── services/
│   └── cardApi.ts
└── types/
    └── card.ts
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
// CRUD operations
cardApi.createCard(card)
cardApi.updateCard(id, updates)
cardApi.linkCards(sourceId, targetId, type)
```

---

## 🗄️ DATABASE

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

## 📚 DOCUMENTI DISPONIBILI

1. **RIEPILOGO_PIANO_CARD_SYSTEM.md** ⭐ Leggi prima
2. **PIANO_CARD_SYSTEM_V1.md** - Piano dettagliato
3. **ARCHITETTURA_CARD_SERVICE.md** - Architettura completa
4. **CARD_MODELS_DEFINITION.md** - Modelli Pydantic + TypeScript
5. **PIANO_IMPLEMENTAZIONE_SETTIMANALE.md** - Timeline settimanale

---

## ✅ CHECKLIST PROSSIMI STEP

### Oggi (2025-10-25)
- [ ] Leggere START_HERE_CARD_SYSTEM.md (questo file)
- [ ] Leggere RIEPILOGO_PIANO_CARD_SYSTEM.md
- [ ] Review architettura con team

### Domani (2025-10-26)
- [ ] Approvazione piano
- [ ] Assegnazione task
- [ ] Creare branch feature

### Settimana 1
- [ ] Implementare foundation
- [ ] Daily standup
- [ ] Mid-week review

---

## 🎯 METRICHE DI SUCCESSO

- [ ] 4 card types creati e funzionanti
- [ ] CRUD API 100% operativo
- [ ] Relationships linking funziona
- [ ] Multi-tenant isolation verificato
- [ ] Integrazione Onboarding → Card → CGS
- [ ] Test coverage >80%
- [ ] Performance <500ms per query

---

## 🚀 VISIONE FUTURA

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

## 💡 KEY INSIGHTS

1. **Card Service è il centro di verità** per la conoscenza aziendale
2. **Modulo, non microservizio** per evitare complessità
3. **4 card atomiche** sono il MVP perfetto
4. **RAG centralizzato** migliora qualità generazione contenuti
5. **Multi-tenant** da day 1 per scalabilità

---

## 📞 DOMANDE?

Consulta i documenti correlati o contatta il team.

**Prossimo meeting**: Review architettura con team


