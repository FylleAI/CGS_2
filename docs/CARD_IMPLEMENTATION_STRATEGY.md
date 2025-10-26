# 🎴 Card System - Strategia di Implementazione Semplificata

**Data**: 2025-10-25  
**Status**: 📋 Planning  
**Obiettivo**: Implementare card system in forma semplificata ma architetturalmente corretta

---

## 📊 Analisi Stato Attuale

### ✅ **Cosa Abbiamo GIÀ**

#### 1. **Database Schema Completo**
```sql
-- ✅ ESISTE: company_contexts table
CREATE TABLE company_contexts (
    context_id UUID PRIMARY KEY,
    company_name TEXT NOT NULL,
    company_snapshot JSONB NOT NULL,  -- CompanySnapshot completo
    version INTEGER,
    is_active BOOLEAN,
    usage_count INTEGER,
    source_session_id UUID
);

-- ❌ NON ESISTE: context_cards table
-- Documentato in DATABASE_SCHEMA_ADAPTIVE_CARDS.sql ma NON creato
```

**Status**: 
- ✅ `company_contexts` → **IMPLEMENTATO e FUNZIONANTE**
- ❌ `context_cards` → **SOLO DOCUMENTATO, NON IMPLEMENTATO**

#### 2. **Backend Models & Repository**
```python
# ✅ ESISTE: CompanySnapshot model
class CompanySnapshot(BaseModel):
    company: CompanyInfo
    audience: AudienceInfo
    voice: VoiceInfo
    insights: InsightsInfo
    clarifying_questions: List[ClarifyingQuestion]

# ✅ ESISTE: CompanyContextRepository
class CompanyContextRepository:
    async def save_context(snapshot, company_name, website, session_id)
    async def get_active_context(company_name)
    async def search_contexts(query, limit)
```

**Status**: ✅ **COMPLETAMENTE IMPLEMENTATO**

#### 3. **Frontend Card Components**
```tsx
// ✅ ESISTONO: 4 card components specializzate
- CompanySnapshotCardV2.tsx      // Visualizza company info
- AudienceIntelligenceCard.tsx   // Visualizza audience
- VoiceDNACard.tsx                // Visualizza brand voice
- StrategicInsightsCard.tsx      // Visualizza insights

// ✅ ESISTE: Base component
- FylleCard.tsx                   // Base card con styling
```

**Status**: ✅ **IMPLEMENTATO** (ma legge da `CompanySnapshot`, non da `context_cards`)

#### 4. **Workflow & Content Generation**
```python
# ✅ ESISTE: Workflow system completo
- Dynamic workflow execution
- Task orchestration
- Agent execution
- Content storage in content_generations table
```

**Status**: ✅ **IMPLEMENTATO**

---

## 🎯 Gap Analysis: Cosa Manca

### ❌ **1. Context Cards Table**
- Schema documentato ma **NON creato** in Supabase
- Nessuna migration eseguita
- Nessun repository per CRUD operations

### ❌ **2. Card Creation Logic**
- Nessun codice che crea card da `CompanySnapshot`
- Nessun mapping `CompanySnapshot` → `context_cards`
- Nessuna logica di sync tra `company_contexts` e `context_cards`

### ❌ **3. Card API Endpoints**
- Nessun endpoint per GET/POST/PATCH cards
- Frontend non può leggere/scrivere cards
- Nessuna integrazione con onboarding flow

### ❌ **4. Card-Workflow Integration**
- Workflow non legge da cards
- Workflow non aggiorna cards con performance
- Nessun tracking di quali card vengono usate

---

## 🚀 Strategia: Versione Semplificata ma Corretta

### **Principio Guida**

> **"Start simple, but architecturally sound"**
> 
> Implementiamo il minimo necessario per avere card funzionanti, ma con architettura che permette evoluzione futura senza refactoring.

---

## 📋 Piano di Implementazione (3 Fasi)

### **FASE 1: Foundation (1 settimana) - 13 SP**

**Obiettivo**: Creare infrastruttura base per card persistence

#### Task 1.1: Database Migration (3 SP)
```sql
-- Creare migration semplificata
CREATE TABLE context_cards (
    -- Identity
    card_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,  -- Per multi-tenant futuro
    
    -- Card Type
    card_type TEXT NOT NULL CHECK (card_type IN (
        'company', 'audience', 'voice', 'insight'
    )),
    
    -- Metadata
    title TEXT NOT NULL,
    description TEXT,
    
    -- Content (JSONB - flessibile)
    content JSONB NOT NULL,
    
    -- Versioning (semplificato)
    version INTEGER NOT NULL DEFAULT 1,
    is_active BOOLEAN NOT NULL DEFAULT true,
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by TEXT NOT NULL,
    
    -- Source Tracking
    source_session_id UUID,
    source_context_id UUID REFERENCES company_contexts(context_id),
    
    -- Usage (semplificato)
    usage_count INTEGER DEFAULT 0
);

-- Indexes essenziali
CREATE INDEX idx_cards_tenant ON context_cards(tenant_id);
CREATE INDEX idx_cards_type ON context_cards(card_type);
CREATE INDEX idx_cards_active ON context_cards(is_active) WHERE is_active = true;
CREATE INDEX idx_cards_source_context ON context_cards(source_context_id);
```

**Cosa NON includiamo (per ora)**:
- ❌ card_relationships table
- ❌ card_feedback table
- ❌ card_performance_events table
- ❌ Materialized views
- ❌ Complex triggers

**Rationale**: Iniziamo con tabella singola, aggiungeremo relazioni quando necessario.

---

#### Task 1.2: Backend Models (3 SP)
```python
# onboarding/domain/card_models.py

from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel, Field

class CardType(str, Enum):
    """Tipi di card supportati (versione semplificata)."""
    COMPANY = "company"
    AUDIENCE = "audience"
    VOICE = "voice"
    INSIGHT = "insight"

class ContextCard(BaseModel):
    """
    Context Card - versione semplificata.
    
    Rappresenta un'unità atomica di conoscenza aziendale.
    """
    card_id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID  # Per multi-tenant
    card_type: CardType
    title: str
    description: Optional[str] = None
    content: Dict[str, Any]  # JSONB flessibile
    version: int = 1
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str  # 'user:{id}', 'agent:{name}', 'system:onboarding'
    source_session_id: Optional[UUID] = None
    source_context_id: Optional[UUID] = None
    usage_count: int = 0
```

---

#### Task 1.3: Card Repository (4 SP)
```python
# onboarding/infrastructure/repositories/card_repository.py

class CardRepository:
    """Repository per CRUD operations su context_cards."""
    
    TABLE_NAME = "context_cards"
    
    def __init__(self, supabase_client: Client):
        self.client = supabase_client
    
    async def create_card(self, card: ContextCard) -> ContextCard:
        """Crea nuova card."""
        data = {
            "card_id": str(card.card_id),
            "tenant_id": str(card.tenant_id),
            "card_type": card.card_type.value,
            "title": card.title,
            "description": card.description,
            "content": card.content,
            "version": card.version,
            "is_active": card.is_active,
            "created_by": card.created_by,
            "source_session_id": str(card.source_session_id) if card.source_session_id else None,
            "source_context_id": str(card.source_context_id) if card.source_context_id else None,
        }
        
        result = self.client.table(self.TABLE_NAME).insert(data).execute()
        return card
    
    async def get_card(self, card_id: UUID, tenant_id: UUID) -> Optional[ContextCard]:
        """Get card by ID (con tenant isolation)."""
        result = (
            self.client.table(self.TABLE_NAME)
            .select("*")
            .eq("card_id", str(card_id))
            .eq("tenant_id", str(tenant_id))
            .execute()
        )
        
        if not result.data:
            return None
        
        return self._dict_to_card(result.data[0])
    
    async def list_cards(
        self, 
        tenant_id: UUID, 
        card_type: Optional[CardType] = None,
        limit: int = 50
    ) -> List[ContextCard]:
        """List cards per tenant (con filtro opzionale per tipo)."""
        query = (
            self.client.table(self.TABLE_NAME)
            .select("*")
            .eq("tenant_id", str(tenant_id))
            .eq("is_active", True)
        )
        
        if card_type:
            query = query.eq("card_type", card_type.value)
        
        result = query.order("created_at", desc=True).limit(limit).execute()
        
        return [self._dict_to_card(row) for row in result.data]
    
    async def update_card(self, card: ContextCard) -> ContextCard:
        """Update card esistente."""
        data = {
            "title": card.title,
            "description": card.description,
            "content": card.content,
            "updated_at": datetime.utcnow().isoformat(),
        }
        
        self.client.table(self.TABLE_NAME).update(data).eq(
            "card_id", str(card.card_id)
        ).eq("tenant_id", str(card.tenant_id)).execute()
        
        return card
    
    def _dict_to_card(self, data: Dict[str, Any]) -> ContextCard:
        """Convert DB row to ContextCard."""
        return ContextCard(
            card_id=UUID(data["card_id"]),
            tenant_id=UUID(data["tenant_id"]),
            card_type=CardType(data["card_type"]),
            title=data["title"],
            description=data.get("description"),
            content=data["content"],
            version=data["version"],
            is_active=data["is_active"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            created_by=data["created_by"],
            source_session_id=UUID(data["source_session_id"]) if data.get("source_session_id") else None,
            source_context_id=UUID(data["source_context_id"]) if data.get("source_context_id") else None,
            usage_count=data.get("usage_count", 0),
        )
```

---

#### Task 1.4: Card Creation Service (3 SP)
```python
# onboarding/application/services/card_creation_service.py

class CardCreationService:
    """
    Service per creare cards da CompanySnapshot.
    
    Converte CompanySnapshot in 4 card atomiche.
    """
    
    def __init__(self, card_repository: CardRepository):
        self.card_repository = card_repository
    
    async def create_cards_from_snapshot(
        self,
        snapshot: CompanySnapshot,
        tenant_id: UUID,
        session_id: UUID,
        context_id: Optional[UUID] = None
    ) -> List[ContextCard]:
        """
        Crea 4 card da CompanySnapshot.
        
        Returns:
            List di 4 ContextCard (company, audience, voice, insight)
        """
        cards = []
        
        # 1. Company Card
        company_card = ContextCard(
            tenant_id=tenant_id,
            card_type=CardType.COMPANY,
            title=snapshot.company.name,
            description=snapshot.company.industry,
            content={
                "name": snapshot.company.name,
                "industry": snapshot.company.industry,
                "description": snapshot.company.description,
                "key_offerings": snapshot.company.key_offerings,
                "differentiators": snapshot.company.differentiators,
                "website": snapshot.company.website,
            },
            created_by="system:onboarding",
            source_session_id=session_id,
            source_context_id=context_id,
        )
        cards.append(await self.card_repository.create_card(company_card))
        
        # 2. Audience Card
        audience_card = ContextCard(
            tenant_id=tenant_id,
            card_type=CardType.AUDIENCE,
            title=f"{snapshot.company.name} - Target Audience",
            description=snapshot.audience.primary,
            content={
                "primary": snapshot.audience.primary,
                "pain_points": snapshot.audience.pain_points,
                "desired_outcomes": snapshot.audience.desired_outcomes,
            },
            created_by="system:onboarding",
            source_session_id=session_id,
            source_context_id=context_id,
        )
        cards.append(await self.card_repository.create_card(audience_card))
        
        # 3. Voice Card
        voice_card = ContextCard(
            tenant_id=tenant_id,
            card_type=CardType.VOICE,
            title=f"{snapshot.company.name} - Brand Voice",
            description=snapshot.voice.tone,
            content={
                "tone": snapshot.voice.tone,
                "style_guidelines": snapshot.voice.style_guidelines,
            },
            created_by="system:onboarding",
            source_session_id=session_id,
            source_context_id=context_id,
        )
        cards.append(await self.card_repository.create_card(voice_card))
        
        # 4. Insight Card
        insight_card = ContextCard(
            tenant_id=tenant_id,
            card_type=CardType.INSIGHT,
            title=f"{snapshot.company.name} - Strategic Insights",
            description=snapshot.insights.positioning,
            content={
                "positioning": snapshot.insights.positioning,
                "key_messages": snapshot.insights.key_messages,
                "recent_news": snapshot.insights.recent_news,
                "competitors": snapshot.insights.competitors,
            },
            created_by="system:onboarding",
            source_session_id=session_id,
            source_context_id=context_id,
        )
        cards.append(await self.card_repository.create_card(insight_card))
        
        logger.info(f"✅ Created {len(cards)} cards from snapshot for tenant {tenant_id}")
        return cards
```

---

### **FASE 2: Integration (1 settimana) - 13 SP**

**Obiettivo**: Integrare card creation nel flusso onboarding esistente

#### Task 2.1: Integrate in Onboarding Flow (5 SP)
```python
# onboarding/application/use_cases/execute_onboarding.py

class ExecuteOnboardingUseCase:
    """Modified to create cards after snapshot synthesis."""
    
    def __init__(
        self,
        # ... existing dependencies
        card_creation_service: CardCreationService,  # NEW
    ):
        # ... existing init
        self.card_creation_service = card_creation_service
    
    async def execute(self, session: OnboardingSession, answers: Dict[str, Any]):
        # ... existing code (research, synthesis, CGS call)
        
        # ⭐ NEW: Create cards from snapshot
        if session.snapshot and session.company_context_id:
            # Assume tenant_id from session metadata or default
            tenant_id = UUID(session.metadata.get("tenant_id", "00000000-0000-0000-0000-000000000000"))
            
            cards = await self.card_creation_service.create_cards_from_snapshot(
                snapshot=session.snapshot,
                tenant_id=tenant_id,
                session_id=session.session_id,
                context_id=session.company_context_id
            )
            
            # Store card IDs in session metadata
            session.metadata["card_ids"] = [str(card.card_id) for card in cards]
            await self.repository.save_session(session)
            
            logger.info(f"✅ Created {len(cards)} cards for session {session.session_id}")
        
        # ... rest of existing code
```

---

#### Task 2.2: Card API Endpoints (5 SP)
```python
# onboarding/api/card_endpoints.py

router = APIRouter(prefix="/cards", tags=["cards"])

@router.get("/{card_id}")
async def get_card(
    card_id: UUID,
    tenant_id: UUID = Header(..., alias="X-Tenant-ID"),
    card_repo: CardRepository = Depends(get_card_repository)
):
    """Get card by ID."""
    card = await card_repo.get_card(card_id, tenant_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return card

@router.get("/")
async def list_cards(
    tenant_id: UUID = Header(..., alias="X-Tenant-ID"),
    card_type: Optional[CardType] = Query(None),
    limit: int = Query(50, le=100),
    card_repo: CardRepository = Depends(get_card_repository)
):
    """List cards for tenant."""
    cards = await card_repo.list_cards(tenant_id, card_type, limit)
    return {"cards": cards, "count": len(cards)}

@router.patch("/{card_id}")
async def update_card(
    card_id: UUID,
    updates: Dict[str, Any],
    tenant_id: UUID = Header(..., alias="X-Tenant-ID"),
    card_repo: CardRepository = Depends(get_card_repository)
):
    """Update card content."""
    card = await card_repo.get_card(card_id, tenant_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    
    # Update fields
    if "title" in updates:
        card.title = updates["title"]
    if "description" in updates:
        card.description = updates["description"]
    if "content" in updates:
        card.content.update(updates["content"])
    
    card.updated_at = datetime.utcnow()
    
    updated_card = await card_repo.update_card(card)
    return updated_card
```

---

#### Task 2.3: Frontend Integration (3 SP)
```tsx
// onboarding-frontend/src/services/api/cardApi.ts

export const cardApi = {
  /**
   * Get card by ID
   */
  getCard: async (cardId: string, tenantId: string): Promise<ContextCard> => {
    const response = await onboardingApiClient.get<ContextCard>(
      `/cards/${cardId}`,
      { headers: { 'X-Tenant-ID': tenantId } }
    );
    return response.data;
  },

  /**
   * List cards for tenant
   */
  listCards: async (
    tenantId: string,
    cardType?: string,
    limit: number = 50
  ): Promise<{ cards: ContextCard[]; count: number }> => {
    const response = await onboardingApiClient.get('/cards', {
      params: { card_type: cardType, limit },
      headers: { 'X-Tenant-ID': tenantId }
    });
    return response.data;
  },

  /**
   * Update card
   */
  updateCard: async (
    cardId: string,
    tenantId: string,
    updates: Partial<ContextCard>
  ): Promise<ContextCard> => {
    const response = await onboardingApiClient.patch(
      `/cards/${cardId}`,
      updates,
      { headers: { 'X-Tenant-ID': tenantId } }
    );
    return response.data;
  },
};
```

---

### **FASE 3: Enhancement (1 settimana) - 8 SP**

**Obiettivo**: Aggiungere features essenziali per usabilità

#### Task 3.1: Card Edit UI (3 SP)
```tsx
// Aggiungere edit mode alle card esistenti
// Modificare CompanySnapshotCardV2 per permettere editing inline
```

#### Task 3.2: Card Usage Tracking (3 SP)
```python
# Aggiungere tracking quando workflow usa una card
# Incrementare usage_count quando card viene letta
```

#### Task 3.3: Testing & Documentation (2 SP)
```python
# Unit tests per CardRepository
# Integration tests per card creation flow
# API documentation
```

---

## 📊 Riepilogo Effort

| Fase | Duration | Story Points | Deliverables |
|------|----------|--------------|--------------|
| **Fase 1: Foundation** | 1 settimana | 13 SP | DB migration, Models, Repository, Service |
| **Fase 2: Integration** | 1 settimana | 13 SP | Onboarding integration, API, Frontend |
| **Fase 3: Enhancement** | 1 settimana | 8 SP | Edit UI, Usage tracking, Tests |
| **TOTALE** | **3 settimane** | **34 SP** | **Card system funzionante** |

---

## ✅ Cosa Otteniamo

### **Versione Semplificata**
1. ✅ 4 tipi di card (company, audience, voice, insight)
2. ✅ Persistence in Supabase con JSONB flessibile
3. ✅ Auto-creation da onboarding flow
4. ✅ API CRUD completa
5. ✅ Frontend integration con card esistenti
6. ✅ Multi-tenant ready
7. ✅ Versioning base

### **Cosa NON Includiamo (per ora)**
- ❌ Card relationships
- ❌ Card feedback system
- ❌ Performance events tracking
- ❌ Advanced analytics
- ❌ Transparency features (field-level references)
- ❌ Agent usage tracking

---

## 🎯 Architettura Corretta

### **Perché è "Architetturalmente Corretta"?**

1. ✅ **Separation of Concerns**: Card models separati da CompanySnapshot
2. ✅ **Repository Pattern**: CardRepository per data access
3. ✅ **Service Layer**: CardCreationService per business logic
4. ✅ **Multi-tenant**: tenant_id in schema
5. ✅ **Versioning**: version field per evoluzione
6. ✅ **JSONB Flexibility**: content field permette evoluzione senza migration
7. ✅ **Source Tracking**: source_context_id linka a company_contexts
8. ✅ **API-first**: REST endpoints per frontend/mobile

### **Perché è "Semplificata"?**

1. ✅ **Single Table**: Solo `context_cards`, no relationships/feedback/events
2. ✅ **4 Card Types**: Solo essenziali, no product/campaign/competitor
3. ✅ **No Triggers**: Sync manuale invece di automatic
4. ✅ **No Materialized Views**: Query dirette invece di pre-computed
5. ✅ **No Advanced Features**: No transparency, no agent tracking

---

## 🚀 Next Steps

### **Immediate (Questa Settimana)**
1. ✅ Review questo documento con team
2. ✅ Approve architettura semplificata
3. ✅ Create Linear tickets per Fase 1
4. ✅ Setup development branch

### **Fase 1 (Prossima Settimana)**
1. ✅ Create DB migration
2. ✅ Implement models & repository
3. ✅ Implement card creation service
4. ✅ Unit tests

### **Fase 2 (Settimana 2)**
1. ✅ Integrate in onboarding flow
2. ✅ Create API endpoints
3. ✅ Frontend integration

### **Fase 3 (Settimana 3)**
1. ✅ Edit UI
2. ✅ Usage tracking
3. ✅ Testing & docs

---

## 💾 Gestione Memoria e Persistenza con Supabase

### **Architettura Memoria: Hybrid Approach**

```
┌─────────────────────────────────────────────────────────────┐
│                    MEMORY LAYERS                             │
└─────────────────────────────────────────────────────────────┘

Layer 1: VOLATILE (Runtime)
├── Agent Execution Context (in-memory durante workflow)
├── Task Outputs (temporanei)
└── LLM Responses (cached per session)

Layer 2: SESSION (Supabase - Short-term)
├── onboarding_sessions table
│   ├── snapshot JSONB (CompanySnapshot completo)
│   ├── cgs_payload JSONB
│   └── cgs_response JSONB
└── Lifetime: 30 giorni, poi archived

Layer 3: CONTEXT (Supabase - Medium-term)
├── company_contexts table
│   ├── company_snapshot JSONB (versioned)
│   ├── usage_count (tracking riuso)
│   └── is_active (solo 1 versione attiva)
└── Lifetime: Finché company esiste, versioning

Layer 4: CARDS (Supabase - Long-term)
├── context_cards table
│   ├── content JSONB (atomic knowledge)
│   ├── version (evolutionary)
│   └── usage_count (performance tracking)
└── Lifetime: Permanente, evolve nel tempo

Layer 5: CONTENT (Supabase - Permanent)
├── content_generations table
│   ├── Generated content
│   ├── Performance metrics
│   └── Source tracking (workflow_id, card_ids)
└── Lifetime: Permanente (business asset)
```

---

### **Supabase Storage Strategy**

#### **1. JSONB vs Relational: Quando Usare Cosa**

```sql
-- ✅ USA JSONB per:
-- - Dati flessibili che evolvono (card content)
-- - Nested structures (CompanySnapshot)
-- - Schema-less data (metadata)

CREATE TABLE context_cards (
    content JSONB NOT NULL,  -- ✅ Flessibile, no migration
    metadata JSONB DEFAULT '{}'::jsonb  -- ✅ Extensible
);

-- ✅ USA RELATIONAL per:
-- - Dati strutturati stabili (IDs, timestamps)
-- - Foreign keys (relationships)
-- - Indexed fields (queries performanti)

CREATE TABLE context_cards (
    card_id UUID PRIMARY KEY,  -- ✅ Indexed, fast lookup
    tenant_id UUID NOT NULL,   -- ✅ RLS, multi-tenant
    card_type TEXT NOT NULL,   -- ✅ Indexed, filtering
    created_at TIMESTAMPTZ     -- ✅ Indexed, sorting
);
```

**Rationale**:
- **JSONB**: Flessibilità per evoluzione rapida senza migration
- **Relational**: Performance per query frequenti e relationships

---

#### **2. Row-Level Security (RLS) per Multi-Tenant**

```sql
-- Enable RLS on context_cards
ALTER TABLE context_cards ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their tenant's cards
CREATE POLICY tenant_isolation_policy ON context_cards
    FOR ALL
    USING (tenant_id = current_setting('app.current_tenant_id')::uuid);

-- Policy: Service role can see all (for admin/analytics)
CREATE POLICY service_role_policy ON context_cards
    FOR ALL
    TO service_role
    USING (true);
```

**Come Usare**:
```python
# Set tenant context before queries
await supabase.rpc('set_config', {
    'setting': 'app.current_tenant_id',
    'value': str(tenant_id),
    'is_local': True
})

# Ora tutte le query sono automaticamente filtrate per tenant
cards = await supabase.table('context_cards').select('*').execute()
# Returns only cards for current tenant
```

---

#### **3. Indexing Strategy per Performance**

```sql
-- ✅ CRITICAL INDEXES (create immediately)

-- 1. Primary lookups
CREATE INDEX idx_cards_tenant ON context_cards(tenant_id);
CREATE INDEX idx_cards_type ON context_cards(card_type);
CREATE INDEX idx_cards_active ON context_cards(is_active) WHERE is_active = true;

-- 2. Foreign keys
CREATE INDEX idx_cards_source_context ON context_cards(source_context_id);
CREATE INDEX idx_cards_source_session ON context_cards(source_session_id);

-- 3. Sorting/filtering
CREATE INDEX idx_cards_created_at ON context_cards(created_at DESC);
CREATE INDEX idx_cards_updated_at ON context_cards(updated_at DESC);

-- 4. JSONB queries (GIN index)
CREATE INDEX idx_cards_content_gin ON context_cards USING GIN (content);

-- ⚠️ OPTIONAL INDEXES (add if needed)

-- Composite index for common query pattern
CREATE INDEX idx_cards_tenant_type_active
    ON context_cards(tenant_id, card_type, is_active)
    WHERE is_active = true;

-- Full-text search on title
CREATE INDEX idx_cards_title_fts ON context_cards USING GIN (to_tsvector('english', title));
```

**Query Examples**:
```sql
-- Fast: Uses idx_cards_tenant_type_active
SELECT * FROM context_cards
WHERE tenant_id = '...'
  AND card_type = 'company'
  AND is_active = true;

-- Fast: Uses idx_cards_content_gin
SELECT * FROM context_cards
WHERE content @> '{"industry": "AI"}';

-- Fast: Uses idx_cards_title_fts
SELECT * FROM context_cards
WHERE to_tsvector('english', title) @@ to_tsquery('english', 'Fylle & AI');
```

---

#### **4. Versioning & Archiving Strategy**

```sql
-- Soft delete: Mark as inactive instead of DELETE
UPDATE context_cards
SET is_active = false, updated_at = NOW()
WHERE card_id = '...';

-- Create new version
INSERT INTO context_cards (
    tenant_id, card_type, title, content, version,
    parent_card_id, created_by
)
SELECT
    tenant_id, card_type, title, content, version + 1,
    card_id, 'system:versioning'
FROM context_cards
WHERE card_id = '...' AND is_active = true;

-- Mark old version as inactive
UPDATE context_cards
SET is_active = false
WHERE card_id = '...' AND version < (SELECT MAX(version) FROM context_cards WHERE ...);
```

**Archiving Policy**:
```sql
-- Archive old sessions after 30 days
CREATE OR REPLACE FUNCTION archive_old_sessions()
RETURNS void AS $$
BEGIN
    UPDATE onboarding_sessions
    SET metadata = metadata || '{"archived": true}'::jsonb
    WHERE created_at < NOW() - INTERVAL '30 days'
      AND (metadata->>'archived')::boolean IS NOT TRUE;
END;
$$ LANGUAGE plpgsql;

-- Schedule with pg_cron (Supabase extension)
SELECT cron.schedule(
    'archive-old-sessions',
    '0 2 * * *',  -- Every day at 2 AM
    'SELECT archive_old_sessions();'
);
```

---

### **5. Backup & Recovery Strategy**

#### **Supabase Automatic Backups**
```yaml
# Supabase provides:
- Daily automatic backups (retained 7 days on Free, 30 days on Pro)
- Point-in-time recovery (Pro plan)
- Manual backups on demand

# Our strategy:
1. Rely on Supabase automatic backups for disaster recovery
2. Export critical data weekly to S3 for long-term retention
3. Test restore procedure monthly
```

#### **Manual Export Script**
```python
# scripts/backup_cards.py

async def export_cards_to_s3(tenant_id: UUID, s3_bucket: str):
    """Export all cards for tenant to S3."""

    # Get all active cards
    cards = await card_repo.list_cards(tenant_id, limit=10000)

    # Convert to JSON
    export_data = {
        "tenant_id": str(tenant_id),
        "exported_at": datetime.utcnow().isoformat(),
        "cards_count": len(cards),
        "cards": [card.model_dump(mode="json") for card in cards]
    }

    # Upload to S3
    filename = f"cards_backup_{tenant_id}_{datetime.utcnow().strftime('%Y%m%d')}.json"
    s3_client.put_object(
        Bucket=s3_bucket,
        Key=f"backups/cards/{filename}",
        Body=json.dumps(export_data, indent=2)
    )

    logger.info(f"✅ Exported {len(cards)} cards to S3: {filename}")
```

---

### **6. Query Optimization Patterns**

#### **Pattern 1: Batch Loading**
```python
# ❌ BAD: N+1 queries
for session_id in session_ids:
    session = await repo.get_session(session_id)
    cards = await card_repo.list_cards_by_session(session_id)

# ✅ GOOD: Batch query
sessions = await repo.get_sessions(session_ids)
all_cards = await card_repo.list_cards_by_sessions(session_ids)
cards_by_session = group_by(all_cards, 'source_session_id')
```

#### **Pattern 2: Projection (Select Only Needed Fields)**
```python
# ❌ BAD: Select all fields
cards = await supabase.table('context_cards').select('*').execute()

# ✅ GOOD: Select only needed fields
cards = await supabase.table('context_cards').select(
    'card_id, title, card_type, created_at'
).execute()
```

#### **Pattern 3: Pagination**
```python
# ✅ ALWAYS paginate large result sets
async def list_cards_paginated(
    tenant_id: UUID,
    page: int = 1,
    page_size: int = 50
) -> Dict[str, Any]:
    offset = (page - 1) * page_size

    # Get total count
    count_result = await supabase.table('context_cards').select(
        'card_id', count='exact'
    ).eq('tenant_id', str(tenant_id)).execute()

    total_count = count_result.count

    # Get page of results
    result = await supabase.table('context_cards').select('*').eq(
        'tenant_id', str(tenant_id)
    ).order('created_at', desc=True).range(
        offset, offset + page_size - 1
    ).execute()

    return {
        "cards": result.data,
        "page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": (total_count + page_size - 1) // page_size
    }
```

---

### **7. Caching Strategy**

```python
# Use Redis for hot data caching

from redis import asyncio as aioredis
import json

class CachedCardRepository:
    """Card repository with Redis caching."""

    def __init__(self, card_repo: CardRepository, redis_client: aioredis.Redis):
        self.card_repo = card_repo
        self.redis = redis_client
        self.cache_ttl = 300  # 5 minutes

    async def get_card(self, card_id: UUID, tenant_id: UUID) -> Optional[ContextCard]:
        """Get card with caching."""

        # Try cache first
        cache_key = f"card:{tenant_id}:{card_id}"
        cached = await self.redis.get(cache_key)

        if cached:
            logger.debug(f"Cache HIT: {cache_key}")
            return ContextCard(**json.loads(cached))

        # Cache miss - fetch from DB
        logger.debug(f"Cache MISS: {cache_key}")
        card = await self.card_repo.get_card(card_id, tenant_id)

        if card:
            # Store in cache
            await self.redis.setex(
                cache_key,
                self.cache_ttl,
                card.model_dump_json()
            )

        return card

    async def invalidate_card(self, card_id: UUID, tenant_id: UUID):
        """Invalidate cache when card is updated."""
        cache_key = f"card:{tenant_id}:{card_id}"
        await self.redis.delete(cache_key)
        logger.debug(f"Cache INVALIDATED: {cache_key}")
```

**When to Cache**:
- ✅ Frequently accessed cards (company, voice)
- ✅ Read-heavy workloads
- ❌ Rapidly changing data
- ❌ Large result sets (cache only IDs)

---

## 🎯 Decision Matrix: Cosa Implementare Ora vs Dopo

| Feature | Implementa Ora | Implementa Dopo | Rationale |
|---------|----------------|-----------------|-----------|
| **context_cards table** | ✅ Fase 1 | - | Foundation necessaria |
| **CardRepository CRUD** | ✅ Fase 1 | - | Core functionality |
| **4 card types** | ✅ Fase 1 | +4 types in Fase 4 | Start simple |
| **JSONB content** | ✅ Fase 1 | - | Flexibility critical |
| **Multi-tenant (tenant_id)** | ✅ Fase 1 | - | Architectural requirement |
| **Versioning (version field)** | ✅ Fase 1 | Advanced versioning later | Basic versioning sufficient |
| **Source tracking** | ✅ Fase 1 | - | Traceability important |
| **Basic indexes** | ✅ Fase 1 | Advanced indexes later | Performance baseline |
| **RLS policies** | ⚠️ Fase 2 | - | Important but not blocking |
| **API endpoints** | ✅ Fase 2 | - | Frontend integration |
| **Card creation from snapshot** | ✅ Fase 2 | - | Core use case |
| **Edit UI** | ✅ Fase 3 | - | User value |
| **Usage tracking** | ✅ Fase 3 | Advanced analytics later | Basic tracking sufficient |
| **card_relationships** | ❌ | Fase 4+ | Not needed initially |
| **card_feedback** | ❌ | Fase 4+ | Nice to have |
| **card_performance_events** | ❌ | Fase 4+ | Advanced feature |
| **Materialized views** | ❌ | When performance needed | Premature optimization |
| **Transparency features** | ❌ | Separate project (6 weeks) | Major feature |
| **Agent usage tracking** | ❌ | Part of transparency | Separate project |
| **Redis caching** | ❌ | When scale requires | Not needed at start |

---

## ✅ Conclusioni e Raccomandazioni

### **Raccomandazione Finale**

> **Implementare Fase 1-3 (3 settimane, 34 SP) per avere card system funzionante e architetturalmente corretto.**

### **Perché Questo Approccio?**

1. ✅ **Minimal Viable Product**: 4 card types coprono 80% use cases
2. ✅ **Architecturally Sound**: JSONB + relational, multi-tenant, versioning
3. ✅ **Fast Time-to-Value**: 3 settimane vs 6+ settimane per full system
4. ✅ **Evolutionary**: Architettura permette aggiungere features senza refactoring
5. ✅ **Low Risk**: Riusa infrastruttura esistente (Supabase, CompanySnapshot)
6. ✅ **User Value**: Cards visibili e editabili da subito

### **Cosa Otteniamo Dopo 3 Settimane**

- ✅ Cards persistenti in Supabase
- ✅ Auto-creation da onboarding
- ✅ API CRUD completa
- ✅ Frontend integration
- ✅ Edit capability
- ✅ Usage tracking base
- ✅ Multi-tenant ready
- ✅ Versioning ready
- ✅ Foundation per transparency (future)

### **Next Evolution (Fase 4+)**

Dopo Fase 1-3, possiamo aggiungere:
- Card relationships (link tra cards)
- Advanced card types (product, campaign, competitor)
- Performance events tracking
- Transparency features (6 settimane separate)
- Advanced analytics
- Caching layer

---

**Prepared by**: Fylle AI Team
**Date**: 2025-10-25
**Status**: ✅ Ready for Review
**Decision Required**: Approve for Development
**Estimated Start**: Week of 2025-10-28

