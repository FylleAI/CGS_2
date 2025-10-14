# Onboarding Service

Servizio esterno per l'onboarding automatizzato dei clienti tramite ricerca, sintesi e generazione di contenuti.

## 🎯 Panoramica

Il servizio di onboarding orchestra un flusso completo:

1. **Research** → Ricerca informazioni aziendali via Perplexity
2. **Synthesis** → Sintetizza snapshot aziendale via Gemini
3. **Questions** → Genera domande di chiarimento
4. **Answers** → Raccoglie risposte dall'utente
5. **Payload** → Costruisce payload per CGS
6. **Execute** → Esegue workflow CGS
7. **Deliver** → Invia contenuto via Brevo
8. **Persist** → Salva su Supabase

## 📁 Struttura

```
onboarding/
├── config/                    # Configurazione
│   └── settings.py           # Settings con Pydantic
├── domain/                    # Domain layer
│   ├── models.py             # Entità e value objects
│   └── cgs_contracts.py      # Contratti CGS (payload/response)
├── infrastructure/            # Infrastructure layer
│   └── adapters/             # Adapter esterni
│       ├── perplexity_adapter.py   # Research via Perplexity
│       ├── gemini_adapter.py       # Synthesis via Gemini
│       └── cgs_adapter.py          # Invocazione CGS
├── examples/                  # Esempi di utilizzo
│   ├── example_usage.py      # Flow completo
│   └── test_components.py    # Test componenti
├── .env.example              # Template configurazione
└── README.md                 # Questa documentazione
```

## 🚀 Quick Start

### 1. Configurazione

Copia il file di esempio e configura le API keys:

```bash
cd onboarding
cp .env.example .env
# Modifica .env con le tue credenziali
```

Configurazione minima richiesta:
- `PERPLEXITY_API_KEY` - Per la ricerca aziendale
- `GEMINI_API_KEY` o Vertex AI credentials - Per la sintesi
- `CGS_API_URL` - URL del backend CGS

### 2. Test Componenti

Testa i singoli componenti:

```bash
python -m onboarding.examples.test_components
```

Output:
```
🔧 Testing Settings Configuration
   ✅ Perplexity: Configured
   ✅ Gemini: Configured
   ✅ CGS: Configured

📦 Testing Domain Models
   ✓ Session created
   ✓ Snapshot created
   ✓ Payload built

🏥 Testing CGS Health Check
   ✅ CGS is healthy!
```

### 3. Esempio Completo

Esegui il flow completo di onboarding:

```bash
python -m onboarding.examples.example_usage
```

Questo esempio:
1. Crea una sessione di onboarding
2. Ricerca "Fylle AI" con Perplexity
3. Sintetizza snapshot con Gemini
4. Genera 3 domande di chiarimento
5. Simula risposte utente
6. Costruisce payload CGS
7. Salva artifacts in `data/onboarding/examples/`

## 📚 Utilizzo Programmatico

### Esempio Base

```python
import asyncio
from onboarding.config.settings import get_onboarding_settings
from onboarding.infrastructure.adapters.perplexity_adapter import PerplexityAdapter
from onboarding.infrastructure.adapters.gemini_adapter import GeminiSynthesisAdapter
from onboarding.domain.models import OnboardingSession, OnboardingGoal

async def onboard_client():
    # 1. Inizializza settings
    settings = get_onboarding_settings()
    
    # 2. Crea sessione
    session = OnboardingSession(
        brand_name="Acme Corp",
        website="https://acme.com",
        goal=OnboardingGoal.LINKEDIN_POST,
        user_email="client@acme.com",
    )
    
    # 3. Research con Perplexity
    perplexity = PerplexityAdapter(settings)
    research = await perplexity.research_company(
        brand_name=session.brand_name,
        website=session.website,
    )
    
    # 4. Synthesis con Gemini
    gemini = GeminiSynthesisAdapter(settings)
    snapshot = await gemini.synthesize_snapshot(
        brand_name=session.brand_name,
        research_result=research,
        trace_id=session.trace_id,
    )
    
    # 5. Mostra domande
    for q in snapshot.clarifying_questions:
        print(f"{q.question} ({q.expected_response_type})")
    
    # 6. Aggiungi risposte
    snapshot.add_answer("q1", "AI automation")
    snapshot.add_answer("q2", "medium (400-600 words)")
    snapshot.add_answer("q3", True)
    
    # 7. Verifica completezza
    if snapshot.is_complete():
        print("✅ Snapshot completo!")
        session.snapshot = snapshot
    
    return session

# Esegui
session = asyncio.run(onboard_client())
```

### Costruzione Payload CGS

```python
from onboarding.domain.cgs_contracts import (
    CgsPayloadLinkedInPost,
    LinkedInPostInput,
)

# Costruisci input da snapshot
linkedin_input = LinkedInPostInput(
    topic="AI-powered content automation",
    client_name=snapshot.company.name,
    target_audience=snapshot.audience.primary,
    tone=snapshot.voice.tone,
    context=snapshot.company.description,
    key_points=snapshot.company.differentiators[:3],
    target_word_count=300,
)

# Crea payload
payload = CgsPayloadLinkedInPost(
    session_id=session.session_id,
    trace_id=session.trace_id,
    company_snapshot=snapshot,
    clarifying_answers=snapshot.clarifying_answers,
    input=linkedin_input,
)

# Esegui workflow CGS
from onboarding.infrastructure.adapters.cgs_adapter import CgsAdapter

cgs = CgsAdapter(settings)
result = await cgs.execute_workflow(payload)

if result.is_successful():
    print(f"✅ Content generato: {result.content.title}")
    print(f"📊 Costo: ${result.workflow_metrics.total_cost}")
```

## 🔧 Componenti Principali

### Settings (`config/settings.py`)

Gestione configurazione con Pydantic:

```python
from onboarding.config.settings import get_onboarding_settings

settings = get_onboarding_settings()

# Validazione servizi
services = settings.validate_required_services()
# {'perplexity': True, 'gemini': True, 'cgs': True, ...}

# Helper methods
workflow_type = settings.get_workflow_type("linkedin_post")
# → "enhanced_article"
```

### Domain Models (`domain/models.py`)

Entità core:

- **`CompanySnapshot`** - Snapshot aziendale v1.0
- **`OnboardingSession`** - Sessione con state machine
- **`ClarifyingQuestion`** - Domanda di chiarimento
- **`OnboardingGoal`** - Enum: linkedin_post, newsletter, article

### CGS Contracts (`domain/cgs_contracts.py`)

Contratti versionati:

- **`CgsPayloadLinkedInPost`** - Payload per enhanced_article
- **`CgsPayloadNewsletter`** - Payload per premium_newsletter
- **`ResultEnvelope`** - Wrapper risposta CGS

### Adapters (`infrastructure/adapters/`)

#### PerplexityAdapter

```python
adapter = PerplexityAdapter(settings)
result = await adapter.research_company(
    brand_name="Acme Corp",
    website="https://acme.com",
)
# → {'raw_content': '...', 'cost_usd': 0.05, ...}
```

#### GeminiSynthesisAdapter

```python
adapter = GeminiSynthesisAdapter(settings)
snapshot = await adapter.synthesize_snapshot(
    brand_name="Acme Corp",
    research_result=research,
)
# → CompanySnapshot con domande
```

#### CgsAdapter

```python
adapter = CgsAdapter(settings)
result = await adapter.execute_workflow(payload)
# → ResultEnvelope con content e metrics
```

## 📊 Contratti e Schema

### CompanySnapshot v1.0

```json
{
  "version": "1.0",
  "snapshot_id": "uuid",
  "company": {
    "name": "string",
    "description": "string",
    "key_offerings": ["..."],
    "differentiators": ["..."]
  },
  "audience": {
    "primary": "string",
    "pain_points": ["..."]
  },
  "voice": {
    "tone": "professional|conversational|...",
    "style_guidelines": ["..."]
  },
  "clarifying_questions": [
    {
      "id": "q1",
      "question": "string",
      "expected_response_type": "string|enum|boolean|number",
      "options": ["..."] // per enum
    }
  ]
}
```

### CgsPayload v1.0

```json
{
  "version": "1.0",
  "session_id": "uuid",
  "workflow": "enhanced_article",
  "goal": "linkedin_post",
  "company_snapshot": { /* CompanySnapshot */ },
  "clarifying_answers": {
    "q1": "answer1",
    "q2": "answer2"
  },
  "input": {
    "topic": "string",
    "target_audience": "string",
    "tone": "string",
    "target_word_count": 300
  }
}
```

## 🔄 State Machine

```
created → researching → synthesizing → awaiting_user → 
payload_ready → executing → delivering → done|failed
```

Transizioni:

```python
session.update_state(SessionState.RESEARCHING)
session.update_state(SessionState.SYNTHESIZING)
session.update_state(SessionState.AWAITING_USER)
# ... user provides answers ...
session.update_state(SessionState.PAYLOAD_READY)
session.update_state(SessionState.EXECUTING)
session.update_state(SessionState.DONE)
```

## 🎨 Architettura

Il servizio segue **Clean Architecture**:

- **Domain Layer** - Entità, value objects, logica business pura
- **Infrastructure Layer** - Adapter per servizi esterni (Perplexity, Gemini, CGS)
- **Configuration** - Settings con Pydantic, nessun hardcoding

**Principi**:
- ✅ Nessuna modifica alla codebase CGS esistente
- ✅ Riuso adapter esistenti (PerplexityResearchTool, GeminiAdapter)
- ✅ Contratti versionati (v1.0)
- ✅ Configurazione esterna (.env)
- ✅ Modularità e testabilità

## 📝 Note

- Il servizio è **standalone** e non modifica CGS
- Riusa infrastruttura CGS esistente (tools, adapters)
- Supporta retry con exponential backoff
- Validazione JSON schema per contratti
- Cost tracking integrato

## 🚀 Installazione

### 1. Installa dipendenze

```bash
cd onboarding
pip install -r requirements.txt
```

### 2. Configura Supabase

Esegui lo schema SQL in Supabase:

```bash
# Copia il contenuto di infrastructure/database/supabase_schema.sql
# ed eseguilo nel SQL Editor di Supabase
```

### 3. Configura variabili d'ambiente

```bash
cp .env.example .env
# Modifica .env con le tue credenziali
```

### 4. Avvia il servizio

```bash
# Opzione 1: Uvicorn diretto
uvicorn onboarding.api.main:app --reload --port 8001

# Opzione 2: Python module
python -m onboarding.api.main
```

Il servizio sarà disponibile su `http://localhost:8001`

- **API Docs**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health

## 📡 API Endpoints

### POST `/api/v1/onboarding/start`

Avvia il processo di onboarding.

**Request:**
```json
{
  "brand_name": "Acme Corp",
  "website": "https://acme.com",
  "goal": "linkedin_post",
  "user_email": "user@acme.com",
  "additional_context": "Focus on AI automation"
}
```

**Response:**
```json
{
  "session_id": "uuid",
  "trace_id": "trace-id",
  "state": "awaiting_user",
  "snapshot_summary": {
    "company_name": "Acme Corp",
    "industry": "Technology",
    "description": "...",
    "target_audience": "Business professionals",
    "tone": "professional",
    "questions_count": 3
  },
  "clarifying_questions": [
    {
      "id": "q1",
      "question": "What specific aspect should we focus on?",
      "reason": "To tailor content to priorities",
      "expected_response_type": "string",
      "required": true
    }
  ],
  "message": "Onboarding started. Please answer the questions.",
  "next_action": "POST /api/v1/onboarding/{session_id}/answers"
}
```

### POST `/api/v1/onboarding/{session_id}/answers`

Invia risposte e esegui workflow.

**Request:**
```json
{
  "answers": {
    "q1": "AI automation benefits",
    "q2": "medium (400-600 words)",
    "q3": true
  }
}
```

**Response:**
```json
{
  "session_id": "uuid",
  "state": "done",
  "content_title": "AI Automation: Transforming Modern Business",
  "content_preview": "In today's fast-paced business...",
  "word_count": 523,
  "delivery_status": "sent",
  "message": "Onboarding completed successfully!",
  "workflow_metrics": {
    "total_cost": 0.15,
    "total_tokens": 2500,
    "duration_seconds": 45.2
  }
}
```

### GET `/api/v1/onboarding/{session_id}/status`

Ottieni stato sessione.

**Response:**
```json
{
  "session_id": "uuid",
  "trace_id": "trace-id",
  "brand_name": "Acme Corp",
  "goal": "linkedin_post",
  "state": "done",
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-01-15T10:05:00Z",
  "has_snapshot": true,
  "snapshot_complete": true,
  "cgs_run_id": "uuid",
  "delivery_status": "sent"
}
```

### GET `/api/v1/onboarding/{session_id}`

Ottieni dettagli completi sessione (include snapshot completo).

## 🧪 Testing

### Test Componenti

```bash
python -m onboarding.examples.test_components
```

### Test Flow Completo

```bash
python -m onboarding.examples.example_usage
```

### Test API (con curl)

```bash
# Start onboarding
curl -X POST http://localhost:8001/api/v1/onboarding/start \
  -H "Content-Type: application/json" \
  -d '{
    "brand_name": "Test Company",
    "website": "https://test.com",
    "goal": "linkedin_post",
    "user_email": "test@test.com"
  }'

# Submit answers (usa session_id dalla risposta precedente)
curl -X POST http://localhost:8001/api/v1/onboarding/{session_id}/answers \
  -H "Content-Type: application/json" \
  -d '{
    "answers": {
      "q1": "AI automation",
      "q2": "medium (400-600 words)",
      "q3": true
    }
  }'

# Check status
curl http://localhost:8001/api/v1/onboarding/{session_id}/status
```

Vedi `IMPLEMENTATION_STATUS.md` per dettagli implementazione completa.

