# 📊 ANALISI COMPLETA: Flusso Payload Onboarding → CGS

**Data**: 2025-10-16  
**Scopo**: Comprendere come i dati fluiscono dall'Onboarding a CGS, dove vengono salvati in Supabase, e come vengono passati agli agenti.

---

## 🎯 PANORAMICA DEL FLUSSO

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         ONBOARDING FLOW                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  Step 1: START                                                           │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │ POST /api/v1/onboarding/start                                │       │
│  │ Body: { brand_name, website, goal, user_email }             │       │
│  └──────────────────────────────────────────────────────────────┘       │
│                           ↓                                              │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │ Perplexity Research → Raw company data                      │       │
│  │ Gemini Synthesis → CompanySnapshot + Questions              │       │
│  └──────────────────────────────────────────────────────────────┘       │
│                           ↓                                              │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │ SUPABASE SAVE #1                                             │       │
│  │ Table: onboarding_sessions                                   │       │
│  │ Fields:                                                      │       │
│  │   - session_id, trace_id, brand_name, goal                  │       │
│  │   - state = "awaiting_user"                                 │       │
│  │   - snapshot = CompanySnapshot (JSONB) ← IMPORTANTE!        │       │
│  └──────────────────────────────────────────────────────────────┘       │
│                           ↓                                              │
│  Step 2: ANSWERS                                                         │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │ POST /api/v1/onboarding/{session_id}/answers                │       │
│  │ Body: { answers: { "q1": "...", "q2": "..." } }            │       │
│  └──────────────────────────────────────────────────────────────┘       │
│                           ↓                                              │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │ CollectAnswersUseCase                                        │       │
│  │ - Valida risposte (tipo, required, enum options)            │       │
│  │ - Aggiunge a snapshot.clarifying_answers                    │       │
│  │ - Verifica completezza                                      │       │
│  └──────────────────────────────────────────────────────────────┘       │
│                           ↓                                              │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │ PayloadBuilder.build_payload()                               │       │
│  │ - Estrae dati da snapshot + answers                         │       │
│  │ - Crea LinkedInPostInput o NewsletterInput                  │       │
│  │ - Costruisce CgsPayload completo                            │       │
│  └──────────────────────────────────────────────────────────────┘       │
│                           ↓                                              │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │ SUPABASE SAVE #2                                             │       │
│  │ Table: onboarding_sessions                                   │       │
│  │ Fields:                                                      │       │
│  │   - state = "executing"                                     │       │
│  │   - snapshot.clarifying_answers = { "q1": "...", ... }      │       │
│  │   - cgs_payload = CgsPayload (JSONB) ← IMPORTANTE!          │       │
│  └──────────────────────────────────────────────────────────────┘       │
│                           ↓                                              │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │ CgsAdapter.execute_workflow()                                │       │
│  │ - Converte CgsPayload → CGS API Request                     │       │
│  │ - POST http://localhost:8000/api/v1/content/generate        │       │
│  └──────────────────────────────────────────────────────────────┘       │
│                           ↓                                              │
└─────────────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                            CGS FLOW                                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │ POST /api/v1/content/generate                                │       │
│  │ Body: {                                                      │       │
│  │   workflow_type: "enhanced_article",                        │       │
│  │   client_profile: "onboarding",                             │       │
│  │   provider: "gemini",                                       │       │
│  │   model: "gemini-2.5-pro",                                  │       │
│  │   topic: "...",                                             │       │
│  │   target_audience: "...",                                   │       │
│  │   ... (altri parametri da LinkedInPostInput)               │       │
│  │ }                                                            │       │
│  └──────────────────────────────────────────────────────────────┘       │
│                           ↓                                              │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │ CGS Workflow Orchestrator                                    │       │
│  │ - Carica client_profile "onboarding" da Supabase            │       │
│  │ - Carica agenti da data/profiles/onboarding/agents/         │       │
│  │ - Passa parametri agli agenti                               │       │
│  └──────────────────────────────────────────────────────────────┘       │
│                           ↓                                              │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │ AGENTI RICEVONO:                                             │       │
│  │ - topic (da PayloadBuilder._extract_topic)                  │       │
│  │ - target_audience (da snapshot.audience.primary)            │       │
│  │ - tone (da snapshot.voice.tone)                             │       │
│  │ - context (da PayloadBuilder._build_context)                │       │
│  │ - custom_instructions (da PayloadBuilder)                   │       │
│  │ - target_word_count (da answers o default)                  │       │
│  └──────────────────────────────────────────────────────────────┘       │
│                           ↓                                              │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │ Esecuzione Workflow (3+ minuti)                              │       │
│  │ - Ricerca Perplexity (sonar-pro)                            │       │
│  │ - Generazione contenuto (Gemini Pro 2.5)                    │       │
│  │ - Validazione e formattazione                               │       │
│  └──────────────────────────────────────────────────────────────┘       │
│                           ↓                                              │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │ CGS Response                                                 │       │
│  │ {                                                            │       │
│  │   success: true,                                            │       │
│  │   run_id: "uuid",                                           │       │
│  │   title: "...",                                             │       │
│  │   body: "...",                                              │       │
│  │   word_count: 1038,                                         │       │
│  │   total_cost: 0.0234,                                       │       │
│  │   ...                                                        │       │
│  │ }                                                            │       │
│  └──────────────────────────────────────────────────────────────┘       │
│                           ↓                                              │
└─────────────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                      ONBOARDING COMPLETION                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │ CgsAdapter._convert_to_result_envelope()                     │       │
│  │ - Converte CGS Response → ResultEnvelope                    │       │
│  │ - Estrae content, workflow_metrics, etc.                    │       │
│  └──────────────────────────────────────────────────────────────┘       │
│                           ↓                                              │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │ SUPABASE SAVE #3                                             │       │
│  │ Table: onboarding_sessions                                   │       │
│  │ Fields:                                                      │       │
│  │   - state = "done"                                          │       │
│  │   - cgs_run_id = "uuid"                                     │       │
│  │   - cgs_response = ResultEnvelope (JSONB) ← IMPORTANTE!     │       │
│  │   - delivery_status = "sent"                                │       │
│  └──────────────────────────────────────────────────────────────┘       │
│                           ↓                                              │
│  ✅ COMPLETATO                                                           │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📦 STRUTTURA DATI: CompanySnapshot

**Dove viene creato**: `GeminiSynthesisAdapter.synthesize_snapshot()`  
**Dove viene salvato**: Supabase `onboarding_sessions.snapshot` (JSONB)  
**Dove viene usato**: `PayloadBuilder` per estrarre parametri

### Schema CompanySnapshot (v1.0)

```json
{
  "version": "1.0",
  "snapshot_id": "uuid",
  "generated_at": "2025-10-16T12:00:00Z",
  "trace_id": "trace-123",
  
  "company": {
    "name": "Fylle AI",
    "website": "https://fylle.ai",
    "industry": "AI/SaaS",
    "description": "AI-powered content generation platform",
    "key_offerings": ["Content automation", "Multi-agent workflows"],
    "differentiators": ["Clean architecture", "Multi-provider support"],
    "evidence": [
      {
        "claim": "Enterprise-grade platform",
        "source": "https://fylle.ai/about",
        "confidence": 0.9
      }
    ]
  },
  
  "audience": {
    "primary": "Marketing teams and content creators",
    "pain_points": ["Time-consuming content creation", "Consistency issues"],
    "demographics": "B2B SaaS companies"
  },
  
  "voice": {
    "tone": "professional",
    "style_guidelines": ["Clear and concise", "Data-driven"],
    "forbidden_phrases": ["Revolutionary", "Game-changer"]
  },
  
  "insights": {
    "positioning": "Enterprise-grade AI content platform",
    "key_messages": ["Automate content at scale", "Maintain brand voice"],
    "recent_news": ["Launched Gemini integration"],
    "content_opportunities": ["AI automation trends", "Content ROI"]
  },
  
  "clarifying_questions": [
    {
      "id": "q1",
      "question": "What specific topic should we focus on?",
      "reason": "To tailor content to your current priorities",
      "expected_response_type": "string",
      "required": true
    },
    {
      "id": "q2",
      "question": "What length do you prefer?",
      "reason": "To match your audience's reading habits",
      "expected_response_type": "enum",
      "options": ["Short (200-300 words)", "Medium (400-600 words)", "Long (800+ words)"],
      "required": true
    },
    {
      "id": "q3",
      "question": "Should we include statistics?",
      "reason": "To add credibility and data-driven insights",
      "expected_response_type": "boolean",
      "required": false,
      "default_value": true
    }
  ],
  
  "clarifying_answers": {
    "q1": "AI automation benefits for marketing teams",
    "q2": "Medium (400-600 words)",
    "q3": true
  }
}
```

---

## 🔄 STEP 2: Come le Risposte Predispongono il Payload

### 2.1 Raccolta Risposte (`CollectAnswersUseCase`)

**File**: `onboarding/application/use_cases/collect_answers.py`

```python
async def execute(self, session: OnboardingSession, answers: Dict[str, Any]):
    # 1. Valida stato
    if session.state != SessionState.AWAITING_USER:
        raise ValueError(f"Invalid state: {session.state}")
    
    # 2. Per ogni risposta
    for question_id, answer in answers.items():
        # Trova la domanda nel snapshot
        question = next(
            (q for q in session.snapshot.clarifying_questions if q.id == question_id),
            None
        )
        
        # Valida tipo risposta
        self._validate_answer(question, answer)
        
        # Aggiungi a snapshot.clarifying_answers
        session.snapshot.add_answer(question_id, answer)
    
    # 3. Verifica completezza
    if not session.snapshot.is_complete():
        raise ValueError(f"Missing required answers")
    
    # 4. Aggiorna stato
    session.update_state(SessionState.PAYLOAD_READY)
    
    # 5. Salva in Supabase
    await self.repository.save_session(session)
```

**Validazioni**:
- `string`: Deve essere str
- `number`: Deve essere int o float
- `boolean`: Deve essere bool
- `enum`: Deve essere in `question.options`

---

### 2.2 Costruzione Payload (`PayloadBuilder`)

**File**: `onboarding/application/builders/payload_builder.py`

#### Metodi di Estrazione Intelligente

```python
def _extract_topic(self, snapshot: CompanySnapshot) -> str:
    """Estrae topic dalle risposte o inferisce da company info."""
    # 1. Cerca nelle risposte domande con "topic" o "focus"
    for q_id, answer in snapshot.clarifying_answers.items():
        question = next((q for q in snapshot.clarifying_questions if q.id == q_id), None)
        if question and "topic" in question.question.lower():
            return str(answer)  # ← RISPOSTA UTENTE
    
    # 2. Fallback: inferisci da company.key_offerings
    if snapshot.company.key_offerings:
        return f"{snapshot.company.key_offerings[0]} for {snapshot.audience.primary}"
    
    # 3. Ultimo fallback: company description
    return snapshot.company.description[:100]
```

```python
def _extract_word_count(self, snapshot: CompanySnapshot, default: int) -> int:
    """Estrae word count dalle risposte."""
    for q_id, answer in snapshot.clarifying_answers.items():
        question = next((q for q in snapshot.clarifying_questions if q.id == q_id), None)
        if question and "length" in question.question.lower():
            answer_str = str(answer).lower()
            
            # Parsing intelligente
            if "short" in answer_str:
                return 250
            elif "medium" in answer_str:
                return 500
            elif "long" in answer_str:
                return 1000
            
            # Estrai numero dalla stringa
            import re
            numbers = re.findall(r'\d+', answer_str)
            if numbers:
                return int(numbers[0])
    
    return default  # Fallback
```

```python
def _extract_boolean_answer(self, snapshot: CompanySnapshot, keyword: str, default: bool) -> bool:
    """Estrae risposta booleana da domande contenenti keyword."""
    for q_id, answer in snapshot.clarifying_answers.items():
        question = next((q for q in snapshot.clarifying_questions if q.id == q_id), None)
        if question and keyword in question.question.lower():
            if isinstance(answer, bool):
                return answer
            # Parsing string
            answer_str = str(answer).lower()
            return answer_str in {"yes", "true", "si", "sì", "1"}
    
    return default
```

---

## 📋 ESEMPIO COMPLETO: LinkedIn Post

### Input Utente (Step 1)
```json
{
  "brand_name": "Peterlegwood",
  "website": "https://peterlegwood.com",
  "goal": "linkedin_post",
  "user_email": "davide@fylle.ai"
}
```

### CompanySnapshot Generato (Step 1)
```json
{
  "company": {
    "name": "Peterlegwood",
    "industry": "Therapeutic Footwear",
    "description": "Specialized therapeutic shoes for posture correction",
    "key_offerings": ["Orthopedic shoes", "Posture therapy", "Custom insoles"],
    "differentiators": ["Medical-grade materials", "Certified therapists"]
  },
  "audience": {
    "primary": "People with posture issues and back pain"
  },
  "voice": {
    "tone": "professional"
  },
  "clarifying_questions": [
    {
      "id": "q1",
      "question": "What specific aspect should we focus on?",
      "expected_response_type": "enum",
      "options": [
        "Posture correction benefits",
        "Product features",
        "Customer testimonials"
      ],
      "required": true
    },
    {
      "id": "q2",
      "question": "What's the main message?",
      "expected_response_type": "string",
      "required": true
    },
    {
      "id": "q3",
      "question": "Target audience?",
      "expected_response_type": "string",
      "required": true
    }
  ]
}
```

### Risposte Utente (Step 2)
```json
{
  "answers": {
    "q1": "Posture correction benefits",
    "q2": "How therapeutic shoes improve your daily life",
    "q3": "Office workers with back pain"
  }
}
```

### CgsPayload Costruito (Step 2)
```json
{
  "version": "1.0",
  "session_id": "e7704904-b69b-4356-b929-3446027a214f",
  "workflow": "enhanced_article",
  "goal": "linkedin_post",
  "trace_id": "trace-123",

  "company_snapshot": { /* CompanySnapshot completo */ },

  "clarifying_answers": {
    "q1": "Posture correction benefits",
    "q2": "How therapeutic shoes improve your daily life",
    "q3": "Office workers with back pain"
  },

  "input": {
    "topic": "How therapeutic shoes improve your daily life",
    "client_name": "Peterlegwood",
    "client_profile": "onboarding",
    "target_audience": "Office workers with back pain",
    "tone": "professional",
    "context": "Specialized therapeutic shoes for posture correction | Key offerings: Orthopedic shoes, Posture therapy, Custom insoles",
    "key_points": ["Medical-grade materials", "Certified therapists"],
    "hashtags": ["TherapeuticFootwear", "OrthopedicShoes", "PostureTherapy"],
    "target_word_count": 300,
    "include_statistics": true,
    "include_examples": true,
    "include_sources": true,
    "custom_instructions": null,
    "post_format": "thought_leadership"
  },

  "metadata": {
    "source": "onboarding_adapter",
    "dry_run": false,
    "requested_provider": "gemini",
    "language": "it"
  }
}
```

### CGS API Request (Conversione)
```json
{
  "workflow_type": "enhanced_article",
  "client_profile": "onboarding",
  "provider": "gemini",
  "model": "gemini-2.5-pro",

  "topic": "How therapeutic shoes improve your daily life",
  "client_name": "Peterlegwood",
  "target_audience": "Office workers with back pain",
  "tone": "professional",
  "target_word_count": 300,
  "include_statistics": true,
  "include_examples": true,
  "include_sources": true,
  "context": "Specialized therapeutic shoes for posture correction | ...",
  "custom_instructions": null
}
```

**NOTA IMPORTANTE**: Il payload completo (`company_snapshot` e `clarifying_answers`) **NON viene inviato a CGS**. Solo i parametri estratti da `LinkedInPostInput` vengono passati.

---

## 💾 DOVE VEDERE I DATI IN SUPABASE

### Tabella: `onboarding_sessions`

**Schema**:
```sql
CREATE TABLE onboarding_sessions (
    -- Identificatori
    session_id UUID PRIMARY KEY,
    trace_id TEXT NOT NULL,

    -- Input
    brand_name TEXT NOT NULL,
    website TEXT,
    goal TEXT NOT NULL,  -- 'linkedin_post', 'newsletter', etc.
    user_email TEXT,

    -- Stato
    state TEXT NOT NULL,  -- 'created', 'awaiting_user', 'executing', 'done', etc.
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Artifacts (JSONB) ← IMPORTANTE!
    snapshot JSONB,           -- CompanySnapshot completo
    cgs_payload JSONB,        -- CgsPayload completo
    cgs_run_id UUID,          -- ID del run CGS
    cgs_response JSONB,       -- ResultEnvelope completo

    -- Delivery
    delivery_status TEXT,
    delivery_message_id TEXT,
    delivery_timestamp TIMESTAMPTZ,

    -- Error handling
    error_message TEXT,

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb
);
```

### Query Utili

#### 1. Vedere CompanySnapshot di una sessione
```sql
SELECT
    session_id,
    brand_name,
    state,
    snapshot -> 'company' ->> 'name' AS company_name,
    snapshot -> 'company' ->> 'description' AS description,
    snapshot -> 'clarifying_questions' AS questions,
    snapshot -> 'clarifying_answers' AS answers
FROM onboarding_sessions
WHERE session_id = 'e7704904-b69b-4356-b929-3446027a214f';
```

#### 2. Vedere le risposte dell'utente
```sql
SELECT
    session_id,
    brand_name,
    snapshot -> 'clarifying_answers' AS user_answers,
    jsonb_pretty(snapshot -> 'clarifying_answers') AS formatted_answers
FROM onboarding_sessions
WHERE state IN ('payload_ready', 'executing', 'done');
```

#### 3. Vedere il payload inviato a CGS
```sql
SELECT
    session_id,
    brand_name,
    cgs_payload -> 'input' ->> 'topic' AS topic,
    cgs_payload -> 'input' ->> 'target_audience' AS audience,
    cgs_payload -> 'input' ->> 'tone' AS tone,
    cgs_payload -> 'input' -> 'target_word_count' AS word_count,
    cgs_payload -> 'metadata' ->> 'requested_provider' AS provider
FROM onboarding_sessions
WHERE cgs_payload IS NOT NULL;
```

#### 4. Vedere la risposta di CGS
```sql
SELECT
    session_id,
    brand_name,
    cgs_response ->> 'status' AS status,
    cgs_response -> 'content' ->> 'title' AS content_title,
    cgs_response -> 'content' -> 'word_count' AS word_count,
    cgs_response -> 'workflow_metrics' ->> 'total_cost' AS cost,
    cgs_response -> 'workflow_metrics' ->> 'duration_seconds' AS duration
FROM onboarding_sessions
WHERE cgs_response IS NOT NULL;
```

#### 5. Vedere tutto il flusso di una sessione
```sql
SELECT
    session_id,
    brand_name,
    goal,
    state,
    created_at,
    updated_at,

    -- Snapshot
    snapshot -> 'company' ->> 'name' AS company,
    jsonb_array_length(snapshot -> 'clarifying_questions') AS num_questions,

    -- Payload
    cgs_payload -> 'input' ->> 'topic' AS topic,
    cgs_payload -> 'metadata' ->> 'requested_provider' AS provider,

    -- Response
    cgs_response ->> 'status' AS cgs_status,
    cgs_response -> 'content' ->> 'title' AS content_title,

    -- Delivery
    delivery_status
FROM onboarding_sessions
WHERE session_id = 'YOUR_SESSION_ID';
```

---

## 🤖 COME GLI AGENTI RICEVONO LE INFORMAZIONI IN CGS

### Flusso in CGS (Ipotetico)

**Endpoint**: `POST /api/v1/content/generate`

```python
@router.post("/api/v1/content/generate")
async def generate_content(request: ContentGenerationRequestModel):
    # 1. Estrai parametri dalla request
    workflow_type = request.workflow_type  # "enhanced_article"
    client_profile = request.client_profile  # "onboarding"
    provider = request.provider  # "gemini"
    model = request.model  # "gemini-2.5-pro"

    # 2. Carica client profile da Supabase
    profile = await load_client_profile(client_profile)
    # → SELECT * FROM clients WHERE name = 'onboarding'

    # 3. Carica agenti da file YAML
    agents = await load_agents_for_profile(client_profile, workflow_type)
    # → Legge da data/profiles/onboarding/agents/*.yaml
    # → Filtra per workflow_type e is_active = true

    # 4. Costruisci context per agenti
    context = {
        "topic": request.topic,
        "client_name": request.client_name,
        "target_audience": request.target_audience,
        "tone": request.tone,
        "context": request.context,
        "custom_instructions": request.custom_instructions,
        "target_word_count": request.target_word_count,
        "include_statistics": request.include_statistics,
        "include_examples": request.include_examples,
        "include_sources": request.include_sources,
    }

    # 5. Esegui workflow
    result = await workflow_orchestrator.execute(
        workflow_type=workflow_type,
        agents=agents,
        context=context,
        provider=provider,
        model=model,
    )

    return result
```

### Agenti Onboarding

**File**: `data/profiles/onboarding/agents/researcher.yaml`

```yaml
name: researcher
role: Research Specialist
is_active: true
workflows:
  - enhanced_article
  - premium_newsletter

system_prompt: |
  You are a research specialist for {client_name}.

  Your task is to research the topic: "{topic}"
  Target audience: {target_audience}
  Tone: {tone}

  {context}

  {custom_instructions}

  Find credible sources and statistics to support the content.

tools:
  - perplexity_search

provider_override: null  # Usa Perplexity per ricerca (sonar-pro)
```

**File**: `data/profiles/onboarding/agents/writer.yaml`

```yaml
name: writer
role: Content Writer
is_active: true
workflows:
  - enhanced_article
  - premium_newsletter

system_prompt: |
  You are a professional content writer for {client_name}.

  Write about: "{topic}"
  Target audience: {target_audience}
  Tone: {tone}
  Target word count: {target_word_count}

  Context: {context}

  {% if include_statistics %}
  Include relevant statistics and data to support your points.
  {% endif %}

  {% if include_examples %}
  Include concrete examples and case studies.
  {% endif %}

  {% if include_sources %}
  Cite credible sources for all claims.
  {% endif %}

  {% if custom_instructions %}
  Additional instructions: {custom_instructions}
  {% endif %}

tools:
  - llm_generate

provider_override: gemini  # Usa Gemini per generazione
model_override: gemini-2.5-pro
```

### Interpolazione Parametri

CGS usa **Jinja2** per interpolare i parametri nei system prompts:

```python
from jinja2 import Template

# System prompt template dall'agent YAML
template_str = agent.system_prompt

# Context costruito dalla request
context = {
    "client_name": "Peterlegwood",
    "topic": "How therapeutic shoes improve your daily life",
    "target_audience": "Office workers with back pain",
    "tone": "professional",
    "context": "Specialized therapeutic shoes for posture correction | ...",
    "target_word_count": 300,
    "include_statistics": True,
    "include_examples": True,
    "include_sources": True,
    "custom_instructions": None,
}

# Render del template
template = Template(template_str)
rendered_prompt = template.render(**context)

# Risultato per writer agent:
"""
You are a professional content writer for Peterlegwood.

Write about: "How therapeutic shoes improve your daily life"
Target audience: Office workers with back pain
Tone: professional
Target word count: 300

Context: Specialized therapeutic shoes for posture correction | ...

Include relevant statistics and data to support your points.

Include concrete examples and case studies.

Cite credible sources for all claims.
"""
```

---

## 🔍 PUNTI CHIAVE PER OTTIMIZZAZIONE

### 1. **Snapshot NON viene passato a CGS**

**Situazione Attuale**:
- `CgsPayload` contiene `company_snapshot` completo (JSONB ~5-10KB)
- `CgsAdapter._convert_to_cgs_request()` **NON invia** il snapshot a CGS
- Solo i parametri estratti (`topic`, `tone`, `context`, etc.) vengono inviati

**Implicazioni**:
- ✅ **Pro**: Request CGS leggera (~1KB invece di ~10KB)
- ❌ **Contro**: CGS non ha accesso a dati ricchi come:
  - `company.differentiators`
  - `audience.pain_points`
  - `voice.style_guidelines`
  - `insights.key_messages`
  - `evidence` con fonti

**Opportunità di Ottimizzazione**:
1. **Passare snapshot completo a CGS** → Agenti possono usare dati più ricchi
2. **Creare `context` più dettagliato** → Includere più info da snapshot
3. **Aggiungere parametri custom** → Es. `key_messages`, `pain_points`, etc.

---

### 2. **Clarifying Answers NON vengono passate a CGS**

**Situazione Attuale**:
- `CgsPayload` contiene `clarifying_answers` (Dict)
- `CgsAdapter._convert_to_cgs_request()` **NON invia** le risposte a CGS
- Solo i valori estratti vengono passati (es. `topic` da q2)

**Implicazioni**:
- ❌ **Contro**: Perdita di contesto delle risposte originali
- ❌ **Contro**: Agenti non possono vedere tutte le preferenze utente

**Opportunità di Ottimizzazione**:
1. **Passare `clarifying_answers` come parametro** → Agenti vedono tutte le risposte
2. **Creare `user_preferences` object** → Aggregare risposte in formato strutturato
3. **Includere in `custom_instructions`** → Formattare risposte come istruzioni

---

### 3. **Estrazione Parametri è "Lossy"**

**Situazione Attuale**:
- `PayloadBuilder` estrae parametri con logica di fallback
- Se una domanda non matcha keyword (es. "topic", "length"), viene ignorata
- Informazioni utente possono essere perse

**Esempio**:
```python
# Domanda: "What style do you prefer?"
# Risposta: "Conversational and friendly"
# → NON viene estratta perché nessun metodo cerca "style"
# → Viene usato default: tone = "professional"
```

**Opportunità di Ottimizzazione**:
1. **Mapping esplicito domanda → parametro** → Configurabile via metadata
2. **Passare tutte le risposte** → Lasciare agli agenti decidere cosa usare
3. **Validazione pre-generazione** → Verificare che tutte le risposte siano usate

---

### 4. **Context è Limitato**

**Situazione Attuale**:
```python
def _build_context(self, snapshot: CompanySnapshot) -> str:
    parts = [snapshot.company.description]

    if snapshot.company.key_offerings:
        parts.append(f"Key offerings: {', '.join(snapshot.company.key_offerings[:3])}")

    if snapshot.insights.positioning:
        parts.append(f"Positioning: {snapshot.insights.positioning}")

    return " | ".join(parts)
```

**Risultato**:
```
"Specialized therapeutic shoes for posture correction | Key offerings: Orthopedic shoes, Posture therapy, Custom insoles | Positioning: Medical-grade footwear"
```

**Opportunità di Ottimizzazione**:
1. **Includere più dati**:
   - `audience.pain_points`
   - `company.differentiators`
   - `voice.style_guidelines`
   - `insights.key_messages`
2. **Formattare come JSON** → Più strutturato per agenti
3. **Creare sezioni separate** → `brand_context`, `audience_context`, `voice_context`

---

## 📊 RIEPILOGO FLUSSO DATI

| **Dato** | **Dove viene creato** | **Dove viene salvato** | **Viene passato a CGS?** | **Come viene usato** |
|----------|----------------------|------------------------|--------------------------|----------------------|
| `brand_name` | User input | `onboarding_sessions.brand_name` | ✅ Sì | `client_name` parameter |
| `website` | User input | `onboarding_sessions.website` | ❌ No | Solo per ricerca Perplexity |
| `goal` | User input | `onboarding_sessions.goal` | ✅ Sì (come `workflow_type`) | Determina workflow |
| `CompanySnapshot` | Gemini synthesis | `onboarding_sessions.snapshot` (JSONB) | ❌ No | Estratto in parametri |
| `clarifying_questions` | Gemini synthesis | `snapshot.clarifying_questions` | ❌ No | Solo per UI frontend |
| `clarifying_answers` | User input (Step 2) | `snapshot.clarifying_answers` | ❌ No | Estratto in parametri |
| `topic` | Estratto da answers | `cgs_payload.input.topic` | ✅ Sì | Passato ad agenti |
| `target_audience` | Estratto da snapshot | `cgs_payload.input.target_audience` | ✅ Sì | Passato ad agenti |
| `tone` | Estratto da snapshot | `cgs_payload.input.tone` | ✅ Sì | Passato ad agenti |
| `context` | Costruito da snapshot | `cgs_payload.input.context` | ✅ Sì | Passato ad agenti |
| `custom_instructions` | Costruito da snapshot | `cgs_payload.input.custom_instructions` | ✅ Sì | Passato ad agenti |
| `CgsPayload` | PayloadBuilder | `onboarding_sessions.cgs_payload` (JSONB) | ❌ No (solo parametri) | Audit trail |
| `ResultEnvelope` | CGS response | `onboarding_sessions.cgs_response` (JSONB) | N/A | Contenuto generato |

---

## ✅ CONCLUSIONI

### Cosa Funziona Bene

1. ✅ **Separazione chiara** tra Onboarding e CGS
2. ✅ **Persistenza completa** in Supabase (snapshot, payload, response)
3. ✅ **Estrazione intelligente** con fallback
4. ✅ **Validazione robusta** delle risposte
5. ✅ **Audit trail completo** per debugging

### Aree di Miglioramento

1. ⚠️ **Snapshot non passato a CGS** → Perdita di dati ricchi
2. ⚠️ **Clarifying answers non passate** → Perdita di contesto utente
3. ⚠️ **Context limitato** → Solo 3 campi del snapshot
4. ⚠️ **Estrazione "lossy"** → Risposte possono essere ignorate
5. ⚠️ **Nessun feedback loop** → Agenti non possono chiedere chiarimenti

### Prossimi Passi Suggeriti

1. **Analizzare sessioni reali** → Vedere quali dati vengono persi
2. **Testare con snapshot completo** → Passare tutto a CGS e misurare qualità
3. **Ottimizzare context building** → Includere più dati rilevanti
4. **Aggiungere mapping esplicito** → Domande → Parametri CGS
5. **Implementare feedback loop** → Agenti possono richiedere info mancanti

---

**Fine Analisi** 🎉


