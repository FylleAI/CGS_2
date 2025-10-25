# 🏗️ Architettura Card Service - Visione Completa

**Data**: 2025-10-25  
**Scope**: Card Service come centro di verità  
**Versione**: 1.0 MVP

---

## 🎯 DECISIONE ARCHITETTURALE CRITICA

### Domanda: Creare una terza entità "Card Service"?

**RISPOSTA: SÌ, ma come modulo dentro CGS Core, non microservizio separato**

#### Perché?
1. **Evita complessità**: Microservizio = deployment, versioning, comunicazione asincrona
2. **Condivide database**: Supabase è già condiviso tra Onboarding e CGS
3. **Logica coesa**: Card è parte della strategia di generazione contenuti
4. **Scalabilità futura**: Può diventare microservizio dopo MVP

#### Struttura
```
CGS Core Engine
├── card_service/          # NUOVO modulo
│   ├── domain/
│   ├── application/
│   ├── infrastructure/
│   └── api/
├── workflow_engine/       # Esiste
├── agent_orchestration/   # Esiste
└── content_generation/    # Esiste
```

---

## 🔄 FLUSSO DATI COMPLETO

### Step 1: Onboarding crea snapshot
```
User Input → Onboarding Microservice → CompanySnapshot
```

### Step 2: Onboarding crea card atomiche
```
CompanySnapshot → Card Service (create_cards_from_snapshot)
                    ↓
                4 Card Atomiche:
                - ProductCard
                - PersonaCard
                - CampaignCard
                - TopicCard
```

### Step 3: Card Service salva in DB
```
Card Service → Supabase (context_cards table)
                ↓
            Multi-tenant isolation (RLS)
```

### Step 4: CGS legge card come RAG
```
CGS Workflow → Card Service (get_cards_for_context)
                ↓
            Agents usano card come knowledge base
                ↓
            Generazione contenuti
```

### Step 5: Feedback loop
```
Generated Content → Metrics → Card Service (update_card_metrics)
                                ↓
                            Card evolve con performance
```

---

## 📊 ENTITÀ E RELAZIONI

### BaseCard (Padre)
```python
class BaseCard(BaseModel):
    id: UUID
    tenant_id: UUID
    card_type: CardType  # Enum
    title: str
    content: Dict[str, Any]  # JSONB
    metrics: Dict[str, Any]  # JSONB
    version: int
    is_active: bool
    created_by: UUID
    updated_by: UUID
    created_at: datetime
    updated_at: datetime
    relationships: List[CardRelationship]
```

### ProductCard
```python
class ProductCard(BaseCard):
    content: ProductContent
    
class ProductContent(BaseModel):
    value_proposition: str
    features: List[str]
    differentiators: List[str]
    use_cases: List[str]
    target_market: str
```

### PersonaCard
```python
class PersonaCard(BaseCard):
    content: PersonaContent
    
class PersonaContent(BaseModel):
    icp_profile: str
    pain_points: List[str]
    goals: List[str]
    preferred_language: str
    communication_channels: List[str]
```

### CampaignCard
```python
class CampaignCard(BaseCard):
    content: CampaignContent
    
class CampaignContent(BaseModel):
    objective: str
    key_messages: List[str]
    tone: str
    target_personas: List[str]
    assets_produced: List[str]
```

### TopicCard
```python
class TopicCard(BaseCard):
    content: TopicContent
    
class TopicContent(BaseModel):
    keywords: List[str]
    angles: List[str]
    related_content: List[str]
    trend_status: str
    frequency: str
```

---

## 🔗 RELAZIONI TRA CARD

### Grafo di Relazioni
```
ProductCard ←→ PersonaCard
    ↓              ↓
    └─→ CampaignCard ←─┘
         ↓
    TopicCard
```

### Tipi di Relazioni
```
- 'links_to': Collegamento generico
- 'targets': Campaign targets Persona
- 'features': Product features Topic
- 'derives_from': Card derivata da altra
- 'supports': Card supporta altra
```

### Tabella card_relationships
```sql
source_card_id → target_card_id
relationship_type: 'links_to' | 'targets' | 'features' | 'derives_from' | 'supports'
strength: 0.0 - 1.0 (confidence)
```

---

## 🏛️ LAYER ARCHITECTURE

### Domain Layer
```python
# core/card_service/domain/
├── card_entity.py          # BaseCard, ProductCard, etc.
├── card_types.py           # Enums, constants
├── card_relationship.py    # CardRelationship entity
└── card_value_objects.py   # Value objects (ProductContent, etc.)
```

### Application Layer
```python
# core/card_service/application/
├── create_card_use_case.py
├── update_card_use_case.py
├── get_card_use_case.py
├── list_cards_use_case.py
├── link_cards_use_case.py
├── create_cards_from_snapshot_use_case.py  # KEY
└── get_cards_for_context_use_case.py       # KEY
```

### Infrastructure Layer
```python
# core/card_service/infrastructure/
├── card_repository.py
├── card_relationship_repository.py
├── card_mapper.py
└── migrations/
    └── 005_create_card_tables.sql
```

### API Layer
```python
# core/card_service/api/
├── card_routes.py
├── card_schemas.py
└── card_dependencies.py
```

---

## 🔌 INTEGRAZIONE PUNTI CHIAVE

### 1. Onboarding → Card Service
```python
# onboarding/application/use_cases/execute_onboarding.py
from core.card_service.application import CreateCardsFromSnapshotUseCase

async def execute(self, session_id: str):
    # ... existing code ...
    
    # Create atomic cards from snapshot
    create_cards_uc = CreateCardsFromSnapshotUseCase(
        card_repository=self.card_repository
    )
    
    cards = await create_cards_uc.execute(
        snapshot=session.company_snapshot,
        tenant_id=session.tenant_id,
        created_by=session.user_id
    )
    
    # Store card IDs in session
    session.card_ids = [c.id for c in cards]
    await self.repository.save_session(session)
```

### 2. CGS → Card Service (RAG)
```python
# core/infrastructure/workflows/handlers/content_generation_handler.py
from core.card_service.application import GetCardsForContextUseCase

async def execute(self, context: Dict[str, Any]):
    # Get cards for context
    get_cards_uc = GetCardsForContextUseCase(
        card_repository=self.card_repository
    )
    
    cards = await get_cards_uc.execute(
        tenant_id=context['tenant_id'],
        card_types=['product', 'persona', 'campaign', 'topic'],
        limit=10
    )
    
    # Use cards as RAG context
    rag_context = self._build_rag_context(cards)
    
    # Pass to agents
    result = await self.agent_orchestrator.execute(
        agents=context['agents'],
        context=rag_context
    )
```

### 3. Frontend → Card Service
```typescript
// onboarding-frontend/src/services/cardApi.ts
export const cardApi = {
  createCard: (card: CreateCardRequest) =>
    api.post('/api/v1/cards', card),
  
  updateCard: (id: string, updates: Partial<Card>) =>
    api.patch(`/api/v1/cards/${id}`, updates),
  
  getCard: (id: string) =>
    api.get(`/api/v1/cards/${id}`),
  
  listCards: (filters: CardFilters) =>
    api.get('/api/v1/cards', { params: filters }),
  
  linkCards: (sourceId: string, targetId: string, type: string) =>
    api.post(`/api/v1/cards/${sourceId}/relationships`, {
      target_card_id: targetId,
      relationship_type: type
    })
};
```

---

## 🗄️ DATABASE SCHEMA

### context_cards
```sql
id UUID PRIMARY KEY
tenant_id UUID NOT NULL
card_type VARCHAR(50) NOT NULL
title VARCHAR(500) NOT NULL
content JSONB NOT NULL
metrics JSONB DEFAULT '{}'
version INT DEFAULT 1
is_active BOOLEAN DEFAULT true
created_by UUID
updated_by UUID
created_at TIMESTAMPTZ DEFAULT NOW()
updated_at TIMESTAMPTZ DEFAULT NOW()

INDEXES:
- (tenant_id, card_type)
- (is_active)
- (created_at DESC)
```

### card_relationships
```sql
id UUID PRIMARY KEY
source_card_id UUID REFERENCES context_cards(id)
target_card_id UUID REFERENCES context_cards(id)
relationship_type VARCHAR(50)
strength FLOAT DEFAULT 1.0
created_at TIMESTAMPTZ DEFAULT NOW()

INDEXES:
- (source_card_id)
- (target_card_id)
- (relationship_type)
```

---

## 🔐 MULTI-TENANCY

### Row-Level Security (RLS)
```sql
ALTER TABLE context_cards ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can only see their tenant's cards"
ON context_cards
FOR SELECT
USING (tenant_id = auth.uid());

CREATE POLICY "Users can only modify their tenant's cards"
ON context_cards
FOR UPDATE
USING (tenant_id = auth.uid());
```

### Validazione Backend
```python
# Ogni operazione verifica tenant_id
async def get_card(self, card_id: UUID, tenant_id: UUID):
    card = await self.repository.get(card_id)
    if card.tenant_id != tenant_id:
        raise PermissionError("Access denied")
    return card
```

---

## 📈 EVOLUZIONE FUTURA

### Phase 2: Feedback System
- Card feedback table
- Performance metrics tracking
- Automated card evolution

### Phase 3: Agent Integration
- Agents scrivono su card
- Versioning + audit trail
- Conflict resolution

### Phase 4: Advanced RAG
- Semantic search su card
- Vector embeddings
- Similarity matching

---

## ✅ CHECKLIST IMPLEMENTAZIONE

- [ ] Database schema creato
- [ ] Pydantic models definiti
- [ ] Repository implementato
- [ ] Use cases implementati
- [ ] API endpoints creati
- [ ] Integrazione Onboarding
- [ ] Integrazione CGS
- [ ] Frontend UI
- [ ] Tests (unit + integration)
- [ ] Documentation


