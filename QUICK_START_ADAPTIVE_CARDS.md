# 🚀 Quick Start: Adaptive Knowledge Base

## 📋 TL;DR

**Obiettivo**: Trasformare le card da read-only a sistema evoluto dove utenti, agent e automazioni creano/modificano card atomiche multi-tenant.

**Timeline MVP**: 4-5 settimane  
**Timeline Production**: 7-8 settimane  
**Total Effort**: ~155 story points

---

## 🎯 Cosa Stiamo Costruendo

### Prima (Stato Attuale)
```
User → Onboarding → CompanySnapshot (monolitico) → Card UI (read-only)
```

### Dopo (Visione Target)
```
User ←→ Interactive Cards ←→ Database
  ↓                              ↑
Agent ←→ ContextCardTool ←→ Database
  ↓                              ↑
Automation ←→ Evolution Worker ←→ Database
```

---

## 🏗️ Architettura in 3 Livelli

### 1. **Database Layer** (Week 1-2)
```sql
context_cards              -- Atomic knowledge units
card_relationships         -- Links between cards
card_feedback             -- User/agent feedback
card_performance_events   -- Performance tracking
```

### 2. **API Layer** (Week 2-3)
```
POST   /api/v1/cards                    -- Create card
GET    /api/v1/cards                    -- List cards
PATCH  /api/v1/cards/{id}               -- Update card
DELETE /api/v1/cards/{id}               -- Delete card
POST   /api/v1/cards/{id}/relationships -- Link cards
POST   /api/v1/cards/{id}/feedback      -- Submit feedback
```

### 3. **UI Layer** (Week 4-5)
```tsx
<InteractiveCard
  card={card}
  editable={true}
  onUpdate={handleUpdate}
  onFeedback={handleFeedback}
/>
```

---

## 📦 5 Fasi di Sviluppo

### Phase 1: Foundation (Weeks 1-3) - 38 points
**Goal**: Database + API pronti

**Key Deliverables**:
- ✅ 4 nuove tabelle create
- ✅ Multi-tenancy implementato
- ✅ CRUD API funzionante
- ✅ Migration da CompanySnapshot a card granulari

**Critical Path**:
```
Schema Design → Migration → Repository → API
```

---

### Phase 2: Interactive Cards (Weeks 4-5) - 31 points
**Goal**: UI interattiva

**Key Deliverables**:
- ✅ Card editing UI
- ✅ Feedback system
- ✅ Real-time updates
- ✅ Optimistic UI

**Critical Path**:
```
InteractiveCard → CardEditors → State Management → WebSocket
```

---

### Phase 3: Agent Integration (Weeks 6-7) - 31 points
**Goal**: Agents scrivono su card

**Key Deliverables**:
- ✅ ContextCardTool per agents
- ✅ Workflow integration
- ✅ Insight generation
- ✅ Relationship tracking

**Critical Path**:
```
ContextCardTool → Agent Integration → Workflow Updates
```

---

### Phase 4: Auto-Evolution (Weeks 8-10) - 31 points
**Goal**: Card si aggiornano automaticamente

**Key Deliverables**:
- ✅ Performance tracking
- ✅ Feedback automation
- ✅ Quality scoring
- ✅ Auto-update triggers

**Critical Path**:
```
Performance Tracking → Feedback Worker → Quality Score → Auto-Updates
```

---

### Phase 5: Advanced Features (Weeks 11-12) - 24 points
**Goal**: Features avanzate

**Key Deliverables**:
- ✅ Analytics dashboard
- ✅ Card recommendations
- ✅ Template system
- ✅ Bulk operations

---

## 🎯 MVP Scope (Fai Questo Prima!)

**Timeline**: 4-5 settimane  
**Effort**: 69 points  

### Must-Have Features:
1. **Multi-tenant card database** ✅
2. **CRUD API** ✅
3. **Interactive editing UI** ✅
4. **Feedback system** ✅
5. **Real-time updates** ✅

### Success Criteria:
- [ ] User può creare una card in <30 secondi
- [ ] User può editare una card in <3 click
- [ ] Save success rate >95%
- [ ] Multi-tenant isolation funziona
- [ ] Real-time updates <500ms

---

## 🚀 Come Iniziare

### Step 1: Setup Database (Week 1)
```bash
# 1. Crea migration script
cd onboarding/infrastructure/database/migrations
touch 004_create_adaptive_cards.sql

# 2. Definisci schema (vedi LINEAR_ROADMAP per dettagli)
# 3. Testa migration su dev
python scripts/run_migration_004.py --env dev

# 4. Verifica tabelle create
psql -h localhost -U postgres -d fylle_dev -c "\dt context_*"
```

### Step 2: Implement Repository (Week 2)
```bash
# 1. Crea repository
touch onboarding/infrastructure/repositories/context_card_repository.py

# 2. Implementa CRUD methods
# 3. Scrivi unit tests
pytest onboarding/tests/repositories/test_context_card_repository.py -v

# 4. Coverage check
pytest --cov=onboarding/infrastructure/repositories --cov-report=html
```

### Step 3: Build API (Week 2-3)
```bash
# 1. Crea endpoints
touch onboarding/api/endpoints/cards.py

# 2. Definisci request/response models
touch onboarding/api/models/card_models.py

# 3. Testa endpoints
pytest onboarding/tests/api/test_cards_endpoints.py -v

# 4. Verifica OpenAPI docs
open http://localhost:8000/docs
```

### Step 4: Build UI (Week 4-5)
```bash
# 1. Crea componenti
cd onboarding-frontend/src/components/cards
touch InteractiveCard.tsx
touch CardEditor.tsx

# 2. Crea store
cd ../../store
touch cardsStore.ts

# 3. Testa componenti
npm test -- InteractiveCard.test.tsx

# 4. Verifica in browser
npm run dev
```

---

## 📊 8 Tipologie di Card

### 1. ProductCard
```typescript
{
  card_type: 'product',
  content: {
    name: "Enterprise CRM",
    value_proposition: "...",
    features: [...],
    differentiators: [...],
    use_cases: [...]
  },
  metrics: {
    conversion_rate: 0.15,
    avg_deal_size: 50000
  }
}
```

### 2. PersonaCard
```typescript
{
  card_type: 'persona',
  content: {
    name: "Enterprise IT Director",
    demographics: {...},
    psychographics: {
      pain_points: [...],
      goals: [...],
      motivations: [...]
    },
    communication: {...}
  },
  metrics: {
    engagement_rate: 0.25
  }
}
```

### 3. CampaignCard
```typescript
{
  card_type: 'campaign',
  content: {
    name: "Q4 Product Launch",
    objective: "...",
    target_personas: ["persona_id_1"],
    key_messages: [...],
    assets: [...]
  },
  metrics: {
    reach: 10000,
    conversions: 150
  }
}
```

### 4. BrandVoiceCard
```typescript
{
  card_type: 'brand_voice',
  content: {
    tone: "Professional yet approachable",
    style_guidelines: [...],
    do_examples: [...],
    dont_examples: [...],
    forbidden_phrases: [...]
  }
}
```

### 5. TopicCard
```typescript
{
  card_type: 'topic',
  content: {
    name: "AI in Healthcare",
    keywords: [...],
    angles: [...],
    related_content: [...],
    trends: [...]
  }
}
```

### 6. CompetitorCard
```typescript
{
  card_type: 'competitor',
  content: {
    name: "Competitor X",
    positioning: "...",
    messaging: [...],
    strengths: [...],
    weaknesses: [...],
    opportunities: [...]
  }
}
```

### 7. PerformanceCard
```typescript
{
  card_type: 'performance',
  content: {
    scope: "content_type",
    scope_value: "linkedin_post",
    top_performers: [...],
    insights: [...],
    recommendations: [...]
  },
  metrics: {
    avg_ctr: 0.05,
    trend: "up"
  }
}
```

### 8. InsightCard
```typescript
{
  card_type: 'insight',
  content: {
    title: "Audience prefers video content",
    description: "...",
    evidence: [...],
    recommendations: [...],
    confidence: 0.85
  }
}
```

---

## 🔧 Tech Stack

### Backend
- **Framework**: FastAPI
- **Database**: Supabase (PostgreSQL)
- **ORM**: Supabase Python Client
- **Validation**: Pydantic
- **Background Jobs**: Celery + Redis
- **Testing**: pytest

### Frontend
- **Framework**: React 18 + TypeScript
- **State**: Zustand
- **Data Fetching**: TanStack Query
- **UI**: Tailwind CSS + MUI
- **Real-time**: WebSocket
- **Testing**: Vitest + React Testing Library

---

## 📈 Metriche di Successo

### Phase 1 (Foundation)
- [ ] Migration runs in <5 minutes
- [ ] API response time <200ms (p95)
- [ ] Test coverage >80%
- [ ] Zero breaking changes

### Phase 2 (Interactive)
- [ ] Card edit time <30 seconds
- [ ] Save success rate >95%
- [ ] Real-time update latency <500ms
- [ ] Mobile responsive (100% features)

### Phase 3 (Agents)
- [ ] Agents create cards automatically
- [ ] 90%+ workflows use card context
- [ ] Insight accuracy >80%
- [ ] Zero duplicate cards created

### Phase 4 (Evolution)
- [ ] Quality scores for 100% of cards
- [ ] Feedback processed <1 hour
- [ ] Auto-update accuracy >85%
- [ ] Performance tracking for all content

---

## 🚨 Rischi & Mitigazioni

| Rischio | Mitigazione |
|---------|-------------|
| **Migration fails** | Extensive testing, rollback plan, backup |
| **Performance issues** | Pagination, indexing, caching, lazy loading |
| **Concurrent edits** | Optimistic locking, conflict resolution UI |
| **Agent hallucinations** | Confidence thresholds, human review queue |
| **Low adoption** | Training, templates, excellent UX |

---

## 📚 Risorse Utili

### Documentation
- `LINEAR_ROADMAP_ADAPTIVE_KNOWLEDGE_BASE.md` - Full roadmap
- `LINEAR_IMPORT_TASKS.csv` - CSV for Linear import
- `CARD_SYSTEM_ARCHITECTURE.md` - Current card system
- `onboarding/README.md` - Onboarding backend docs

### Code Examples
- `onboarding/infrastructure/repositories/company_context_repository.py` - Repository pattern
- `onboarding-frontend/src/components/cards/FylleCard.tsx` - Card UI components
- `core/infrastructure/workflows/handlers/onboarding_content_handler.py` - Workflow integration

### Database
- `onboarding/infrastructure/database/migrations/003_create_company_contexts.sql` - Similar migration
- `onboarding/infrastructure/database/supabase_schema.sql` - Current schema

---

## 🎯 Next Steps

### This Week
1. [ ] Review roadmap with team
2. [ ] Import tasks to Linear
3. [ ] Assign Phase 1 tasks
4. [ ] Setup dev environment
5. [ ] Kickoff meeting

### Next Week
1. [ ] Complete database schema design
2. [ ] Create migration script
3. [ ] Start repository implementation
4. [ ] Begin API endpoint development

---

## 💬 Questions?

**Slack**: #adaptive-knowledge-base  
**Docs**: Notion workspace  
**Meetings**: Tuesdays 10am (sprint planning), Fridays 3pm (demo)

---

**Last Updated**: 2025-10-25  
**Version**: 1.0  
**Status**: Ready to Start 🚀

