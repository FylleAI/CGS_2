# 📋 PIANO OTTIMIZZAZIONE: Payload Arricchito + RAG Integration

**Data**: 2025-10-16  
**Obiettivo**: Arricchire il payload passato a CGS e creare un sistema RAG per riutilizzare i rich context aziendali

---

## 🎯 OBIETTIVI

### 1. **Passare Rich Context a CGS**
- Inviare `company_snapshot` completo agli agenti CGS
- Inviare `clarifying_answers` complete
- Permettere agli agenti di accedere a tutti i dati raccolti

### 2. **Salvare Rich Context in Supabase per RAG**
- Creare tabella dedicata `company_contexts` per memorizzare i context arricchiti
- Naming chiaro con nome azienda per riconoscibilità
- Struttura ottimizzata per retrieval (RAG)
- Versionamento dei context

### 3. **Utilizzare Context come RAG**
- Quando un'azienda torna, recuperare il context esistente
- Evitare di rifare ricerca Perplexity se context recente
- Permettere aggiornamento context se necessario
- Usare context in future generazioni di contenuto

---

## 📊 ARCHITETTURA PROPOSTA

### Nuova Tabella: `company_contexts`

```sql
CREATE TABLE IF NOT EXISTS company_contexts (
    -- Identificatori
    context_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_name TEXT NOT NULL,  -- Nome normalizzato (lowercase, no spaces)
    company_display_name TEXT NOT NULL,  -- Nome originale per display
    website TEXT,
    
    -- Versioning
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_active BOOLEAN NOT NULL DEFAULT true,
    
    -- Rich Context (JSONB)
    company_snapshot JSONB NOT NULL,  -- CompanySnapshot completo
    
    -- Metadata per RAG
    industry TEXT,  -- Estratto da snapshot.company.industry
    primary_audience TEXT,  -- Estratto da snapshot.audience.primary
    key_offerings TEXT[],  -- Array per ricerca
    tags TEXT[],  -- Tag per categorizzazione
    
    -- Usage tracking
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMPTZ,
    
    -- Source tracking
    source_session_id UUID,  -- Prima sessione che ha creato il context
    
    -- Indexes
    CONSTRAINT unique_company_version UNIQUE (company_name, version)
);

-- Indexes per performance
CREATE INDEX idx_company_contexts_name ON company_contexts(company_name) WHERE is_active = true;
CREATE INDEX idx_company_contexts_industry ON company_contexts(industry) WHERE is_active = true;
CREATE INDEX idx_company_contexts_updated ON company_contexts(updated_at DESC);
CREATE INDEX idx_company_contexts_tags ON company_contexts USING GIN(tags);

-- Full-text search su company info
CREATE INDEX idx_company_contexts_fts ON company_contexts USING GIN(
    to_tsvector('english', 
        company_display_name || ' ' || 
        COALESCE(industry, '') || ' ' || 
        COALESCE(primary_audience, '')
    )
);
```

### Modifiche a `onboarding_sessions`

```sql
-- Aggiungere riferimento al context
ALTER TABLE onboarding_sessions 
ADD COLUMN company_context_id UUID REFERENCES company_contexts(context_id);

-- Index
CREATE INDEX idx_onboarding_sessions_context ON onboarding_sessions(company_context_id);
```

---

## 🔄 FLUSSO OTTIMIZZATO

### Scenario 1: Nuova Azienda (Prima Volta)

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. User Input                                                    │
│    POST /api/v1/onboarding/start                                │
│    { brand_name: "Peterlegwood", website: "...", goal: "..." } │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. Check Existing Context                                       │
│    company_name = normalize("Peterlegwood") → "peterlegwood"   │
│    SELECT * FROM company_contexts                               │
│    WHERE company_name = 'peterlegwood' AND is_active = true    │
│    ORDER BY version DESC LIMIT 1                                │
│                                                                  │
│    Result: NOT FOUND ❌                                         │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. Create New Context                                           │
│    - Perplexity Research                                        │
│    - Gemini Synthesis → CompanySnapshot                         │
│    - Save to onboarding_sessions.snapshot                       │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. User Answers Questions                                       │
│    POST /api/v1/onboarding/{session_id}/answers                │
│    { answers: { q1: "...", q2: "...", q3: "..." } }           │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 5. Save Rich Context to company_contexts                        │
│    INSERT INTO company_contexts (                               │
│      company_name: "peterlegwood",                              │
│      company_display_name: "Peterlegwood",                      │
│      website: "https://peterlegwood.com",                       │
│      version: 1,                                                │
│      company_snapshot: { /* CompanySnapshot completo */ },      │
│      industry: "Therapeutic Footwear",                          │
│      primary_audience: "People with posture issues",            │
│      key_offerings: ["Orthopedic shoes", "Posture therapy"],    │
│      tags: ["healthcare", "footwear", "therapy"],               │
│      source_session_id: "e7704904-..."                          │
│    )                                                             │
│    RETURNING context_id                                         │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 6. Update Session with Context Reference                        │
│    UPDATE onboarding_sessions                                   │
│    SET company_context_id = 'context-uuid'                      │
│    WHERE session_id = 'session-uuid'                            │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 7. Build Enhanced Payload                                       │
│    CgsPayload = {                                               │
│      company_snapshot: { /* completo */ },                      │
│      clarifying_answers: { /* complete */ },                    │
│      input: { /* parametri estratti */ },                       │
│      metadata: { /* provider, language */ }                     │
│    }                                                             │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 8. Send to CGS (ENHANCED)                                       │
│    POST http://localhost:8000/api/v1/content/generate          │
│    {                                                             │
│      workflow_type: "enhanced_article",                         │
│      client_profile: "onboarding",                              │
│      provider: "gemini",                                        │
│      model: "gemini-2.5-pro",                                   │
│                                                                  │
│      // Parametri estratti (come prima)                         │
│      topic: "...",                                              │
│      target_audience: "...",                                    │
│      tone: "...",                                               │
│                                                                  │
│      // NUOVO: Rich context completo                            │
│      company_snapshot: { /* CompanySnapshot completo */ },      │
│      clarifying_answers: { /* Risposte complete */ }            │
│    }                                                             │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 9. CGS Agents Use Rich Data                                     │
│    - Researcher: Usa company.differentiators per focus          │
│    - Writer: Usa voice.style_guidelines per tone                │
│    - Editor: Usa insights.key_messages per messaging            │
└─────────────────────────────────────────────────────────────────┘
```

### Scenario 2: Azienda Esistente (Ritorno)

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. User Input                                                    │
│    POST /api/v1/onboarding/start                                │
│    { brand_name: "Peterlegwood", website: "...", goal: "..." } │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. Check Existing Context                                       │
│    company_name = normalize("Peterlegwood") → "peterlegwood"   │
│    SELECT * FROM company_contexts                               │
│    WHERE company_name = 'peterlegwood' AND is_active = true    │
│    ORDER BY version DESC LIMIT 1                                │
│                                                                  │
│    Result: FOUND ✅                                             │
│    {                                                             │
│      context_id: "abc-123",                                     │
│      version: 2,                                                │
│      company_snapshot: { /* dati esistenti */ },                │
│      updated_at: "2025-10-10T10:00:00Z"  (6 giorni fa)         │
│    }                                                             │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. Decide: Reuse or Refresh?                                    │
│                                                                  │
│    IF updated_at < 30 days ago:                                 │
│      → REUSE existing context ✅                                │
│      → Skip Perplexity research (save time & cost)              │
│      → Load snapshot from company_contexts                      │
│                                                                  │
│    ELSE:                                                         │
│      → REFRESH context 🔄                                       │
│      → Run Perplexity + Gemini                                  │
│      → Create new version (version = 3)                         │
│      → Mark old version as is_active = false                    │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. Load Existing Snapshot                                       │
│    session.snapshot = context.company_snapshot                  │
│    session.company_context_id = context.context_id              │
│    session.state = AWAITING_USER                                │
│                                                                  │
│    UPDATE company_contexts                                      │
│    SET usage_count = usage_count + 1,                           │
│        last_used_at = NOW()                                     │
│    WHERE context_id = 'abc-123'                                 │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 5. Return Questions to User                                     │
│    (Stesse domande dal snapshot esistente)                      │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 6. User Answers → CGS Execution                                 │
│    (Come Scenario 1, ma senza ricerca iniziale)                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ IMPLEMENTAZIONE

### Task 1: Creare Tabella `company_contexts`

**File**: `onboarding/infrastructure/database/supabase_schema_contexts.sql`

```sql
-- Schema completo come sopra
-- + Migration script per aggiungere company_context_id a onboarding_sessions
```

**Azioni**:
1. Creare file SQL con schema
2. Eseguire migration su Supabase
3. Verificare indexes creati

---

### Task 2: Creare Repository per `company_contexts`

**File**: `onboarding/infrastructure/repositories/company_context_repository.py`

```python
from typing import Optional, List
from uuid import UUID
from datetime import datetime, timedelta
from onboarding.domain.models import CompanySnapshot

class CompanyContextRepository:
    """Repository for company contexts (RAG)."""
    
    def __init__(self, supabase_client):
        self.client = supabase_client
    
    async def find_by_company_name(
        self, 
        company_name: str,
        max_age_days: int = 30
    ) -> Optional[dict]:
        """Find active context for company (RAG retrieval)."""
        normalized_name = self._normalize_company_name(company_name)
        cutoff_date = datetime.utcnow() - timedelta(days=max_age_days)
        
        result = self.client.table("company_contexts") \
            .select("*") \
            .eq("company_name", normalized_name) \
            .eq("is_active", True) \
            .gte("updated_at", cutoff_date.isoformat()) \
            .order("version", desc=True) \
            .limit(1) \
            .execute()
        
        if result.data:
            return result.data[0]
        return None
    
    async def create_context(
        self,
        company_name: str,
        company_display_name: str,
        website: Optional[str],
        snapshot: CompanySnapshot,
        source_session_id: UUID,
    ) -> dict:
        """Create new company context."""
        normalized_name = self._normalize_company_name(company_name)
        
        # Check if context exists
        existing = await self.find_by_company_name(company_name, max_age_days=999999)
        version = (existing["version"] + 1) if existing else 1
        
        # Deactivate old versions
        if existing:
            self.client.table("company_contexts") \
                .update({"is_active": False}) \
                .eq("company_name", normalized_name) \
                .execute()
        
        # Extract metadata
        industry = snapshot.company.industry if snapshot.company else None
        primary_audience = snapshot.audience.primary if snapshot.audience else None
        key_offerings = snapshot.company.key_offerings[:5] if snapshot.company else []
        tags = self._generate_tags(snapshot)
        
        # Insert new context
        data = {
            "company_name": normalized_name,
            "company_display_name": company_display_name,
            "website": website,
            "version": version,
            "company_snapshot": snapshot.model_dump(mode="json"),
            "industry": industry,
            "primary_audience": primary_audience,
            "key_offerings": key_offerings,
            "tags": tags,
            "source_session_id": str(source_session_id),
            "usage_count": 0,
        }
        
        result = self.client.table("company_contexts").insert(data).execute()
        return result.data[0]
    
    async def increment_usage(self, context_id: UUID):
        """Increment usage counter."""
        self.client.table("company_contexts") \
            .update({
                "usage_count": "usage_count + 1",  # SQL expression
                "last_used_at": datetime.utcnow().isoformat()
            }) \
            .eq("context_id", str(context_id)) \
            .execute()
    
    def _normalize_company_name(self, name: str) -> str:
        """Normalize company name for matching."""
        return name.lower().strip().replace(" ", "").replace("-", "")
    
    def _generate_tags(self, snapshot: CompanySnapshot) -> List[str]:
        """Generate tags from snapshot for categorization."""
        tags = []
        
        if snapshot.company:
            if snapshot.company.industry:
                tags.append(snapshot.company.industry.lower())
        
        if snapshot.audience:
            if snapshot.audience.primary:
                # Extract keywords from audience
                words = snapshot.audience.primary.lower().split()
                tags.extend([w for w in words if len(w) > 4])
        
        # Deduplicate
        return list(set(tags))[:10]
```

---


