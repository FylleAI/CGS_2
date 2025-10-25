# 🎯 Piano di Azione: Card System V1 (Prime 4 Card)

**Data**: 2025-10-25  
**Scope**: MVP delle prime 4 card atomiche  
**Timeline**: 2-3 settimane  
**Effort**: ~40 story points

---

## 📊 VISIONE ARCHITETTURALE

### Stato Attuale
```
Frontend Onboarding → Onboarding Microservice → CGS Core Engine
                           ↓
                    CompanySnapshot (monolitico)
                           ↓
                    Card UI (read-only)
```

### Stato Target (V1)
```
Frontend Onboarding ←→ Card Service (NEW) ←→ Database
                           ↓
                    Atomic Cards (Product, Persona, Campaign, Topic)
                           ↓
                    CGS Core Engine (usa card come RAG)
```

---

## 🏗️ ARCHITETTURA PROPOSTA

### 3 Entità Principali

#### 1. **CGS Core Engine** (Esiste)
- Orchestrazione workflow
- Generazione contenuti
- Gestione agenti

#### 2. **Onboarding Microservice** (Esiste)
- Research company
- Synthesize snapshot
- Collect user input
- Build CGS payload

#### 3. **Card Service** (NUOVO - Centro di Verità)
- CRUD card atomiche
- RAG centralizzato
- Versioning + feedback
- Multi-tenant support

### Flusso Dati
```
Onboarding → Crea Card (Product, Persona, Campaign, Topic)
                ↓
            Card Service (Database)
                ↓
            CGS Core Engine (legge card come RAG)
                ↓
            Generazione Contenuti
```

---

## 📋 LE 4 CARD INIZIALI

### 1. **Card Prodotto/Servizio**
```typescript
{
  card_type: 'product',
  title: string,
  content: {
    value_proposition: string,
    features: string[],
    differentiators: string[],
    use_cases: string[],
    target_market: string
  },
  metrics: {
    conversion_rate?: number,
    avg_deal_size?: number
  },
  relationships: {
    personas: string[],  // Link a Persona cards
    campaigns: string[]  // Link a Campaign cards
  }
}
```

### 2. **Card Persona/Target**
```typescript
{
  card_type: 'persona',
  title: string,
  content: {
    icp_profile: string,
    pain_points: string[],
    goals: string[],
    preferred_language: string,
    communication_channels: string[],
    demographics?: object,
    psychographics?: object
  },
  metrics: {
    engagement_rate?: number
  },
  relationships: {
    products: string[],
    campaigns: string[]
  }
}
```

### 3. **Card Campagna/Progetto**
```typescript
{
  card_type: 'campaign',
  title: string,
  content: {
    objective: string,
    key_messages: string[],
    tone: string,
    target_personas: string[],
    assets_produced: string[],
    results?: string,
    learnings?: string
  },
  metrics: {
    reach?: number,
    conversions?: number,
    roi?: number
  },
  relationships: {
    personas: string[],
    products: string[]
  }
}
```

### 4. **Card Tema/Topic**
```typescript
{
  card_type: 'topic',
  title: string,
  content: {
    keywords: string[],
    angles: string[],
    related_content: string[],
    trend_status: 'emerging' | 'stable' | 'declining',
    frequency: string,
    audience_interest: string
  },
  metrics: {
    search_volume?: number,
    trend_score?: number
  },
  relationships: {
    campaigns: string[],
    products: string[]
  }
}
```

---

## 🗄️ SCHEMA DATABASE (Fase 1)

### Tabella: `context_cards`
```sql
CREATE TABLE context_cards (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  card_type VARCHAR(50) NOT NULL,  -- product, persona, campaign, topic
  title VARCHAR(500) NOT NULL,
  content JSONB NOT NULL,           -- Flexible per tipo
  metrics JSONB DEFAULT '{}',
  version INT DEFAULT 1,
  is_active BOOLEAN DEFAULT true,
  created_by UUID,
  updated_by UUID,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT valid_card_type CHECK (card_type IN ('product', 'persona', 'campaign', 'topic'))
);

CREATE INDEX idx_cards_tenant_type ON context_cards(tenant_id, card_type);
CREATE INDEX idx_cards_active ON context_cards(is_active);
```

### Tabella: `card_relationships`
```sql
CREATE TABLE card_relationships (
  id UUID PRIMARY KEY,
  source_card_id UUID REFERENCES context_cards(id),
  target_card_id UUID REFERENCES context_cards(id),
  relationship_type VARCHAR(50),  -- 'links_to', 'derives_from', 'supports'
  strength FLOAT DEFAULT 1.0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT no_self_reference CHECK (source_card_id != target_card_id)
);

CREATE INDEX idx_relationships_source ON card_relationships(source_card_id);
CREATE INDEX idx_relationships_target ON card_relationships(target_card_id);
```

---

## 🔌 API ENDPOINTS (Fase 1)

### Card CRUD
```
POST   /api/v1/cards                    -- Create card
GET    /api/v1/cards                    -- List cards (con filtri)
GET    /api/v1/cards/{id}               -- Get card detail
PATCH  /api/v1/cards/{id}               -- Update card
DELETE /api/v1/cards/{id}               -- Soft delete

POST   /api/v1/cards/{id}/relationships -- Link cards
GET    /api/v1/cards/{id}/relationships -- Get card relationships
```

### Request/Response
```typescript
// POST /api/v1/cards
{
  card_type: 'product',
  title: 'Enterprise CRM',
  content: { ... },
  metrics: { ... }
}

// Response
{
  id: 'uuid',
  card_type: 'product',
  title: 'Enterprise CRM',
  content: { ... },
  version: 1,
  created_at: '2025-10-25T...',
  relationships: []
}
```

---

## 📁 STRUTTURA CARTELLE (Backend)

```
core/
├── card_service/                    # NUOVO
│   ├── domain/
│   │   ├── card_entity.py          # BaseCard, ProductCard, PersonaCard, etc.
│   │   ├── card_types.py           # Enums e costanti
│   │   └── card_relationship.py    # CardRelationship entity
│   │
│   ├── application/
│   │   ├── create_card_use_case.py
│   │   ├── update_card_use_case.py
│   │   ├── get_card_use_case.py
│   │   ├── list_cards_use_case.py
│   │   └── link_cards_use_case.py
│   │
│   ├── infrastructure/
│   │   ├── card_repository.py      # CRUD operations
│   │   ├── card_relationship_repo.py
│   │   └── migrations/
│   │       └── 005_create_card_tables.sql
│   │
│   └── api/
│       ├── card_routes.py          # FastAPI routes
│       └── card_schemas.py         # Pydantic models
```

---

## 📁 STRUTTURA CARTELLE (Frontend)

```
onboarding-frontend/src/
├── components/cards/
│   ├── CardEditor.tsx              # Editor generico
│   ├── ProductCardEditor.tsx       # Specifico per Product
│   ├── PersonaCardEditor.tsx       # Specifico per Persona
│   ├── CampaignCardEditor.tsx      # Specifico per Campaign
│   ├── TopicCardEditor.tsx         # Specifico per Topic
│   └── CardRelationshipUI.tsx      # Linking UI
│
├── hooks/
│   ├── useCard.ts                  # CRUD hook
│   ├── useCardRelationships.ts     # Relationship hook
│   └── useCardValidation.ts        # Validation hook
│
├── services/
│   └── cardApi.ts                  # API client
│
└── types/
    └── card.ts                     # TypeScript types
```

---

## 🚀 FASE 1: FOUNDATION (Settimana 1-2)

### Week 1: Database + Domain
- [ ] Creare migration SQL (context_cards, card_relationships)
- [ ] Definire Pydantic models (BaseCard, ProductCard, PersonaCard, CampaignCard, TopicCard)
- [ ] Definire TypeScript types (stesso)
- [ ] Creare CardRepository (CRUD base)

### Week 2: API + Integration
- [ ] Implementare API endpoints (POST, GET, PATCH, DELETE)
- [ ] Integrare con Onboarding (crea card dopo snapshot)
- [ ] Implementare CardRelationshipRepository
- [ ] Aggiungere validazione (Pydantic + Zod)

---

## 🎨 FASE 2: FRONTEND (Settimana 3)

### Week 3: UI Interattiva
- [ ] Creare CardEditor generico
- [ ] Creare editor specifici per ogni tipo
- [ ] Implementare linking UI
- [ ] Aggiungere validazione client-side

---

## ✅ CHECKLIST MVP

### Database
- [ ] Migration SQL creata
- [ ] Tabelle create in Supabase
- [ ] Indici creati
- [ ] RLS policies configurate

### Backend
- [ ] Pydantic models definiti
- [ ] Repository implementato
- [ ] API endpoints funzionanti
- [ ] Validazione server-side
- [ ] Integrazione con Onboarding

### Frontend
- [ ] TypeScript types definiti
- [ ] CardEditor component
- [ ] API client (cardApi.ts)
- [ ] Validazione client-side
- [ ] UI interattiva

### Testing
- [ ] Unit tests (repository)
- [ ] Integration tests (API)
- [ ] E2E tests (UI)

---

## 🔗 INTEGRAZIONE CON ONBOARDING

### Flusso
```
1. Onboarding completa snapshot
2. Crea 4 card atomiche:
   - ProductCard (da company info)
   - PersonaCard (da audience info)
   - CampaignCard (da goal)
   - TopicCard (da insights)
3. Salva card in Card Service
4. Passa card IDs a CGS
5. CGS usa card come RAG
```

### Codice
```python
# onboarding/application/use_cases/execute_onboarding.py
async def execute(self, session_id: str):
    # ... existing code ...
    
    # NEW: Create atomic cards
    cards = await self.card_service.create_cards_from_snapshot(
        snapshot=session.company_snapshot,
        tenant_id=session.tenant_id
    )
    
    # Link cards
    await self.card_service.link_cards(cards)
    
    # Pass to CGS
    cgs_payload = self.payload_builder.build(
        goal=session.goal,
        snapshot=session.company_snapshot,
        card_ids=[c.id for c in cards]  # NEW
    )
```

---

## 📊 METRICHE DI SUCCESSO

- [ ] 4 card types creati e funzionanti
- [ ] CRUD API 100% operativo
- [ ] Relationships linking funziona
- [ ] Multi-tenant isolation verificato
- [ ] Integrazione Onboarding → Card Service → CGS
- [ ] Test coverage >80%

---

## 🎯 PROSSIMI STEP

1. **Oggi**: Review architettura con team
2. **Domani**: Creare migration SQL
3. **Settimana 1**: Implementare backend
4. **Settimana 2**: Implementare frontend
5. **Settimana 3**: Testing + refinement


