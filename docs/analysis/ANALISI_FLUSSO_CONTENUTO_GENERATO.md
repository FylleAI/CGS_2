# 📊 ANALISI FLUSSO CONTENUTO GENERATO

**Data**: 2025-10-16  
**Autore**: AI Assistant  
**Scopo**: Tracciare il flusso completo da onboarding a contenuto generato e capire dove viene salvato

---

## 🔍 FLUSSO END-TO-END COMPLETO

### **1. START ONBOARDING** (`POST /api/v1/onboarding/start`)

**Input**:
```json
{
  "brand_name": "reopla",
  "website": null,
  "goal": "linkedin_post",
  "user_email": "davide@fylle.ai"
}
```

**Processo**:
1. ✅ Crea `OnboardingSession` con `session_id` univoco
2. ✅ Salva in Supabase tabella `onboarding_sessions` (stato: `created`)
3. ✅ Ricerca company con Perplexity (o RAG cache)
4. ✅ Sintetizza `CompanySnapshot` con Gemini
5. ✅ Genera 3 domande di chiarimento
6. ✅ Salva RAG context in tabella `company_contexts`
7. ✅ Aggiorna sessione con `snapshot` (stato: `ready`)

**Output**:
```json
{
  "session_id": "d0675491-02de-4126-ac02-cd52be6d3581",
  "state": "ready",
  "snapshot": { ... },
  "clarifying_questions": [ ... ]
}
```

---

### **2. SUBMIT ANSWERS** (`POST /api/v1/onboarding/{session_id}/answers`)

**Input**:
```json
{
  "answers": {
    "q1": "lombardy",
    "q2": "Sales volume",
    "q3": "Intermediate (some technical details)"
  }
}
```

**Processo**:

#### **Step 1: Collect Answers**
- ✅ Valida risposte
- ✅ Aggiorna `snapshot.clarifying_answers`
- ✅ Salva in Supabase

#### **Step 2: Build CGS Payload**
- ✅ `PayloadBuilder.build_payload()` crea `CgsPayloadOnboardingContent` (v2.0)
- ✅ Mappa `goal` → `content_type` (linkedin_post)
- ✅ Estrae `content_config` dalle risposte:
  ```python
  {
    "word_count": 300,
    "tone": "conversational",
    "include_emoji": True,
    "include_hashtags": True,
    "include_cta": True,
    "max_hashtags": 5
  }
  ```
- ✅ Costruisce `OnboardingContentInput`:
  ```python
  {
    "content_type": "linkedin_post",
    "topic": "lombardy",  # da q1
    "client_name": "reopla",
    "target_audience": "Real estate agencies and brokers",
    "tone": "authoritative",
    "context": "...",
    "content_config": { ... }
  }
  ```
- ✅ Salva `cgs_payload` in sessione

#### **Step 3: Execute CGS Workflow**
- ✅ `CgsAdapter.execute_workflow()` chiama CGS backend
- ✅ Endpoint: `POST http://localhost:8000/api/v1/content/generate`
- ✅ Request body:
  ```json
  {
    "workflow_type": "onboarding_content_generator",
    "client_profile": "onboarding",
    "topic": "lombardy",
    "client_name": "reopla",
    "target_audience": "Real estate agencies and brokers",
    "tone": "authoritative",
    "context": "...",
    "custom_instructions": "...",
    "context": {
      "company_snapshot": { ... },
      "clarifying_answers": { ... },
      "content_type": "linkedin_post",
      "content_config": { ... }
    }
  }
  ```

#### **Step 4: CGS Processing**
- ✅ CGS riceve richiesta
- ✅ `OnboardingContentHandler.execute()` viene chiamato
- ✅ Routing interno: `content_type="linkedin_post"` → `_generate_linkedin_post()`
- ✅ Genera prompt ottimizzato per LinkedIn Post
- ✅ Chiama LLM (Gemini)
- ✅ Genera contenuto (200-400 parole, emoji, hashtags, CTA)
- ✅ Salva in CGS database (`content_generations` table)
- ✅ Ritorna `ResultEnvelope`:
  ```json
  {
    "status": "completed",
    "run_id": "accaff99-b914-4c88-9546-4a07188af5a3",
    "content": {
      "title": "...",
      "body": "...",
      "word_count": 300,
      "format": "linkedin_post"
    },
    "workflow_metrics": {
      "total_duration_seconds": 65.2,
      "total_cost_usd": 0.0012
    }
  }
  ```

#### **Step 5: Save Response**
- ✅ Onboarding salva `cgs_response` in sessione
- ✅ Aggiorna `cgs_run_id`
- ✅ Stato: `executing` → `done`
- ✅ Salva in Supabase

#### **Step 6: Email Delivery (Optional)**
- ⚠️ Skipped (Brevo not configured)

**Output**:
```json
{
  "session_id": "d0675491-02de-4126-ac02-cd52be6d3581",
  "state": "done",
  "message": "Onboarding completed successfully!",
  "content_title": "...",
  "content_preview": "...",
  "word_count": 300,
  "workflow_metrics": { ... }
}
```

---

## 💾 DOVE VIENE SALVATO IL CONTENUTO?

### **1. Supabase - Tabella `onboarding_sessions`**

**Schema**:
```sql
CREATE TABLE onboarding_sessions (
    session_id UUID PRIMARY KEY,
    trace_id TEXT NOT NULL,
    brand_name TEXT NOT NULL,
    website TEXT,
    goal TEXT NOT NULL,
    user_email TEXT,
    state TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    
    -- Artifacts
    snapshot JSONB,              -- CompanySnapshot completo
    cgs_payload JSONB,           -- CgsPayloadOnboardingContent
    cgs_run_id UUID,             -- ID del run CGS
    cgs_response JSONB,          -- ⭐ CONTENUTO GENERATO QUI!
    
    -- Delivery
    delivery_status TEXT,
    delivery_message_id TEXT,
    delivery_timestamp TIMESTAMPTZ,
    
    -- Error handling
    error_message TEXT,
    metadata JSONB
);
```

**Campo `cgs_response`** contiene:
```json
{
  "version": "1.0",
  "session_id": "...",
  "workflow": "onboarding_content_generator",
  "status": "completed",
  "cgs_run_id": "accaff99-b914-4c88-9546-4a07188af5a3",
  "content": {
    "title": "Lombardy Real Estate Market: Sales Volume Insights",
    "body": "🏡 The Lombardy real estate market is experiencing...",
    "word_count": 300,
    "format": "linkedin_post",
    "metadata": {
      "has_emoji": true,
      "has_hashtags": true,
      "has_cta": true
    }
  },
  "workflow_metrics": {
    "total_duration_seconds": 65.2,
    "total_cost_usd": 0.0012,
    "tasks_completed": 1
  }
}
```

**Come accedere**:
```bash
# Via API
curl http://localhost:8001/api/v1/onboarding/{session_id}

# Via Supabase Dashboard
https://iimymnlepgilbuoxnkqa.supabase.co
→ Table Editor → onboarding_sessions
→ Filtra per session_id
→ Colonna cgs_response (JSONB)
```

---

### **2. Supabase - Tabella `content_generations` (CGS)**

**Schema**:
```sql
CREATE TABLE content_generations (
    id UUID PRIMARY KEY,
    client_id UUID,
    workflow_id UUID,
    run_id UUID,                 -- ⭐ Corrisponde a cgs_run_id
    title VARCHAR(500),
    content TEXT,                -- ⭐ CONTENUTO COMPLETO QUI!
    content_type VARCHAR(50),
    content_format VARCHAR(50),
    topic TEXT,
    context TEXT,
    target_audience TEXT,
    parameters JSONB,
    word_count INTEGER,
    generation_time_seconds NUMERIC,
    cost_usd NUMERIC,
    status VARCHAR(50),
    metadata JSONB,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
);
```

**Come accedere**:
```bash
# Via Supabase Dashboard
https://iimymnlepgilbuoxnkqa.supabase.co
→ Table Editor → content_generations
→ Filtra per run_id = "accaff99-b914-4c88-9546-4a07188af5a3"
→ Colonna content (TEXT)
```

---

## 🔗 RELAZIONE TRA LE TABELLE

```
onboarding_sessions.cgs_run_id
         ↓
         ↓ (FK relationship)
         ↓
content_generations.run_id
```

**Query per recuperare tutto**:
```sql
SELECT 
    os.session_id,
    os.brand_name,
    os.goal,
    os.state,
    os.cgs_run_id,
    cg.title AS content_title,
    cg.content AS content_body,
    cg.word_count,
    cg.cost_usd,
    cg.generation_time_seconds
FROM onboarding_sessions os
LEFT JOIN content_generations cg ON os.cgs_run_id = cg.run_id
WHERE os.session_id = 'd0675491-02de-4126-ac02-cd52be6d3581';
```

---

## 🎯 RIEPILOGO FINALE

### **Dove trovare il contenuto generato?**

1. **Via API Onboarding** (più semplice):
   ```bash
   GET http://localhost:8001/api/v1/onboarding/{session_id}
   ```
   → Campo `cgs_response.content.body`

2. **Via Supabase - Tabella `onboarding_sessions`**:
   - Colonna: `cgs_response` (JSONB)
   - Path: `cgs_response → content → body`

3. **Via Supabase - Tabella `content_generations`**:
   - Filtra per: `run_id = cgs_run_id`
   - Colonna: `content` (TEXT)

### **Flusso dati**:
```
User Input (onboarding)
    ↓
CompanySnapshot (Perplexity + Gemini)
    ↓
CgsPayloadOnboardingContent (PayloadBuilder)
    ↓
CGS Backend (OnboardingContentHandler)
    ↓
LLM Generation (Gemini)
    ↓
ResultEnvelope (CGS response)
    ↓
onboarding_sessions.cgs_response (Supabase) ⭐
    ↓
content_generations.content (Supabase) ⭐
```

---

## 📝 ESEMPIO SESSIONE COMPLETATA

**Session ID**: `d0675491-02de-4126-ac02-cd52be6d3581`  
**Company**: reopla  
**Goal**: linkedin_post  
**CGS Run ID**: `accaff99-b914-4c88-9546-4a07188af5a3`  
**Status**: ✅ done  

**Contenuto salvato in**:
- ✅ `onboarding_sessions.cgs_response`
- ✅ `content_generations.content` (run_id match)

**Accesso**:
```bash
# API
curl http://localhost:8001/api/v1/onboarding/d0675491-02de-4126-ac02-cd52be6d3581

# Supabase Dashboard
https://iimymnlepgilbuoxnkqa.supabase.co/project/iimymnlepgilbuoxnkqa/editor
```

---

## ✅ CONCLUSIONI

1. **Il contenuto generato è salvato in 2 posti**:
   - `onboarding_sessions.cgs_response` (JSONB) - Include metadata completo
   - `content_generations.content` (TEXT) - Solo il testo del contenuto

2. **Il link tra le tabelle è `cgs_run_id`**

3. **L'API `/api/v1/onboarding/{session_id}` ritorna tutto** ma attualmente non include `cgs_response` nella risposta (solo metadata)

4. **Per vedere il contenuto completo** serve:
   - Modificare l'endpoint per includere `cgs_response` nella risposta
   - Oppure accedere direttamente a Supabase

5. **Il nuovo workflow `onboarding_content_generator` funziona correttamente**:
   - ✅ Routing interno basato su `content_type`
   - ✅ Config dinamica per ogni tipo
   - ✅ Contenuto salvato correttamente

