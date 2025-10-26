# 🏗️ Analisi Architetturale: Separazione Microservizi CGS → Workflow + Cards

**Data**: 2025-10-26  
**Obiettivo**: Analizzare codebase attuale e progettare architettura a 3 microservizi

---

## 🎯 VISIONE STRATEGICA

### **Stato Attuale (Monolitico)**
```
┌─────────────────────────────────────────────────────────────┐
│                    CGS MONOLITH                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Onboarding  │  │   Workflow   │  │   Context    │      │
│  │  (Separato)  │  │   Engine     │  │   (Misto)    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### **Stato Target (Microservizi)**
```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  ONBOARDING  │─────▶│    CARDS     │◀─────│   WORKFLOW   │
│  Microservice│      │  Microservice│      │  Microservice│
│              │      │              │      │              │
│  • Research  │      │  • Storage   │      │  • Execution │
│  • Synthesis │      │  • Retrieval │      │  • Agents    │
│  • Questions │      │  • Evolution │      │  • Tools     │
│  • Delivery  │      │  • Tracking  │      │  • Templates │
└──────────────┘      └──────────────┘      └──────────────┘
       │                     ▲                      │
       │                     │                      │
       └─────────────────────┴──────────────────────┘
              "Cards = Single Source of Truth"
```

---

## 📊 ANALISI CODEBASE ATTUALE

### **1. ONBOARDING Microservice** ✅ **GIÀ SEPARATO**

**Location**: `onboarding/`  
**Status**: ✅ Microservizio indipendente (porta 8001)  
**Responsabilità**:
- Research company via Perplexity
- Synthesize CompanySnapshot via Gemini
- Generate clarifying questions
- Collect user answers
- Build CGS payload
- Execute CGS workflow (via adapter)
- Deliver content via Brevo
- Persist sessions to Supabase

**Architettura**:
```
onboarding/
├── api/                    # FastAPI endpoints
│   ├── main.py            # App entry point (porta 8001)
│   ├── endpoints.py       # POST /start, POST /answers
│   └── dependencies.py    # DI container
├── application/
│   ├── use_cases/         # Business logic
│   │   ├── create_session.py
│   │   ├── research_company.py
│   │   ├── synthesize_snapshot.py
│   │   └── execute_onboarding.py
│   └── builders/
│       └── payload_builder.py  # Build CGS payload
├── domain/
│   ├── models.py          # CompanySnapshot, OnboardingSession
│   └── cgs_contracts.py   # CGS API contracts
└── infrastructure/
    ├── adapters/
    │   ├── perplexity_adapter.py
    │   ├── gemini_adapter.py
    │   ├── cgs_adapter.py      # ⚠️ Chiama CGS via HTTP
    │   └── brevo_adapter.py
    └── repositories/
        ├── supabase_repository.py
        └── company_context_repository.py
```

**Dipendenze Esterne**:
- ✅ Perplexity API (research)
- ✅ Gemini API (synthesis)
- ⚠️ **CGS Core** (via HTTP adapter) → **DA SOSTITUIRE CON CARDS**
- ✅ Brevo API (email delivery)
- ✅ Supabase (persistence)

**Problemi Attuali**:
1. ❌ Crea `CompanySnapshot` ma NON crea cards atomiche
2. ❌ Chiama CGS direttamente invece di passare per Cards
3. ❌ `CompanyContextRepository` salva in `company_contexts` ma non in `context_cards`

---

### **2. CGS CORE (Workflow Engine)** ⚠️ **DA SEPARARE**

**Location**: `core/`  
**Status**: ⚠️ Monolite da separare in "Workflow Microservice"  
**Responsabilità**:
- Execute workflows (newsletter, article, LinkedIn post)
- Orchestrate tasks with dependencies
- Execute agents with LLM providers
- Provide tools (RAG, Perplexity, Web Search)
- Track execution metrics
- Store generated content

**Architettura**:
```
core/
├── application/
│   └── use_cases/
│       └── generate_content.py  # Main entry point
├── domain/
│   └── entities/
│       ├── workflow.py
│       ├── task.py
│       ├── agent.py
│       └── content.py
├── infrastructure/
│   ├── orchestration/
│   │   ├── task_orchestrator.py    # Execute tasks
│   │   └── agent_executor.py       # Execute agents
│   ├── workflows/
│   │   ├── registry.py             # Workflow registry
│   │   ├── base/
│   │   │   └── workflow_base.py    # Base handler
│   │   ├── handlers/               # Workflow implementations
│   │   │   ├── premium_newsletter_handler.py
│   │   │   ├── siebert_newsletter_html_handler.py
│   │   │   └── onboarding_content_handler.py
│   │   └── templates/              # JSON workflow definitions
│   │       ├── premium_newsletter.json
│   │       └── siebert_newsletter_html.json
│   ├── tools/
│   │   ├── rag_tool.py
│   │   ├── perplexity_research_tool.py
│   │   └── web_search_tool.py
│   └── repositories/
│       └── file_content_repository.py
└── prompts/                        # Agent prompts
```

**Dipendenze Esterne**:
- ✅ OpenAI API (GPT-4, embeddings)
- ✅ Gemini API (synthesis)
- ✅ Perplexity API (research tool)
- ✅ Serper API (web search)
- ✅ ChromaDB (RAG/embeddings)
- ⚠️ **Knowledge Base** (file-based) → **DA SOSTITUIRE CON CARDS**

**Problemi Attuali**:
1. ❌ Usa file-based knowledge base invece di Cards API
2. ❌ Non traccia quali cards vengono usate
3. ❌ Non aggiorna cards con performance metrics
4. ❌ Context è passato come dict generico, non come cards strutturate

---

### **3. CARDS System** ❌ **NON ESISTE (Solo Documentato)**

**Location**: Nessuna (da creare)  
**Status**: ❌ Solo schema SQL documentato, nessun microservizio  
**Responsabilità** (Target):
- Store atomic knowledge units (cards)
- Provide CRUD API for cards
- Track card usage by workflows
- Evolve cards based on performance
- Provide search/retrieval API
- Manage card relationships
- Track transparency (sources, confidence)

**Schema Documentato** (DATABASE_SCHEMA_ADAPTIVE_CARDS.sql):
```sql
-- 8 tipi di card
CREATE TABLE context_cards (
    card_id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    card_type TEXT CHECK (card_type IN (
        'product', 'persona', 'campaign', 'topic',
        'brand_voice', 'competitor', 'performance', 'insight'
    )),
    title TEXT NOT NULL,
    content JSONB NOT NULL,  -- Flessibile per tipo
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    metrics JSONB DEFAULT '{}',
    confidence_score FLOAT,
    usage_count INTEGER DEFAULT 0,
    source_session_id UUID,
    source_workflow_id UUID,
    ...
);
```

**Cosa Manca**:
1. ❌ Nessun microservizio Cards
2. ❌ Nessuna API REST per cards
3. ❌ Nessun repository implementato
4. ❌ Nessuna logica di creazione cards da CompanySnapshot
5. ❌ Nessuna integrazione con Workflow

---

## 🔍 ANALISI FLUSSI ATTUALI

### **Flusso 1: Onboarding → CGS (Attuale)**

```
┌──────────────┐
│  ONBOARDING  │
└──────┬───────┘
       │ 1. Research (Perplexity)
       ▼
┌──────────────────┐
│ CompanySnapshot  │ (In-memory)
└──────┬───────────┘
       │ 2. Save to company_contexts (Supabase)
       ▼
┌──────────────────┐
│ company_contexts │ (Table)
└──────┬───────────┘
       │ 3. Build CGS Payload
       ▼
┌──────────────────────────────────┐
│ CgsPayloadOnboardingContent      │
│  • company_snapshot (JSONB)      │
│  • clarifying_answers (dict)     │
│  • input (OnboardingContentInput)│
└──────┬───────────────────────────┘
       │ 4. HTTP POST to CGS
       ▼
┌──────────────┐
│   CGS CORE   │
└──────┬───────┘
       │ 5. Execute Workflow
       │    • Agents read from context dict
       │    • RAG tool reads from file KB
       ▼
┌──────────────────┐
│ Generated Content│
└──────────────────┘
```

**Problemi**:
- ❌ `CompanySnapshot` è un blob JSONB, non cards atomiche
- ❌ CGS riceve tutto il snapshot, non sa quali parti usare
- ❌ Nessun tracking di quali dati vengono usati
- ❌ Nessun feedback loop per migliorare snapshot

---

### **Flusso 2: Workflow Execution (Attuale)**

```
┌──────────────────────────────────┐
│ POST /api/v1/content/generate    │
│  • workflow_type                 │
│  • client_profile                │
│  • topic                          │
│  • context (dict generico)       │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ GenerateContentUseCase           │
└──────┬───────────────────────────┘
       │ 1. Get workflow handler
       ▼
┌──────────────────────────────────┐
│ WorkflowHandler.execute()        │
│  • create_workflow()             │
│  • execute_tasks()               │
└──────┬───────────────────────────┘
       │ 2. For each task
       ▼
┌──────────────────────────────────┐
│ TaskOrchestrator.execute_task()  │
└──────┬───────────────────────────┘
       │ 3. Get agent
       ▼
┌──────────────────────────────────┐
│ AgentExecutor.execute_agent()    │
│  • Build system prompt           │
│  • Prepare context (dict)        │
│  • Call LLM                      │
│  • Execute tools if needed       │
└──────┬───────────────────────────┘
       │ 4. Tools access
       ▼
┌──────────────────────────────────┐
│ RAGTool.execute()                │
│  • Reads from file KB            │
│  • ChromaDB embeddings           │
└──────────────────────────────────┘
```

**Problemi**:
- ❌ Context è dict generico, non strutturato
- ❌ RAG tool legge da file, non da Cards API
- ❌ Nessun tracking di quali knowledge viene usata
- ❌ Nessun modo per agent di richiedere cards specifiche

---

## 🎯 ARCHITETTURA TARGET

### **Separazione Microservizi**

```
┌─────────────────────────────────────────────────────────────┐
│                    FYLLE PLATFORM                            │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  ONBOARDING  │    │    CARDS     │    │   WORKFLOW   │
│ Microservice │    │ Microservice │    │ Microservice │
│  Port: 8001  │    │  Port: 8002  │    │  Port: 8000  │
└──────────────┘    └──────────────┘    └──────────────┘
```

---

### **1. ONBOARDING Microservice** (Modificato)

**Responsabilità**:
- ✅ Research company (Perplexity)
- ✅ Synthesize snapshot (Gemini)
- ✅ Generate questions
- ✅ Collect answers
- ⭐ **NEW**: Create cards from snapshot → **CARDS API**
- ⭐ **NEW**: Trigger workflow with card IDs → **WORKFLOW API**
- ✅ Deliver content (Brevo)

**Flusso Modificato**:
```
1. Research → CompanySnapshot (in-memory)
2. POST /cards/batch → Create 4 cards (company, audience, voice, insight)
3. Save session with card_ids
4. POST /workflow/execute with card_ids (not full snapshot)
5. Deliver content
```

**API Changes**:
```python
# OLD (attuale)
cgs_payload = {
    "company_snapshot": snapshot.model_dump(),  # Tutto il blob
    "clarifying_answers": {...}
}
await cgs_adapter.execute_workflow(cgs_payload)

# NEW (target)
card_ids = await cards_client.create_cards_from_snapshot(
    snapshot=snapshot,
    tenant_id=tenant_id
)
workflow_result = await workflow_client.execute(
    workflow_type="onboarding_content",
    card_ids=card_ids,  # Solo IDs, non dati
    parameters={...}
)
```

---

### **2. CARDS Microservice** (Nuovo)

**Port**: 8002  
**Database**: Supabase (`context_cards` table)  
**Responsabilità**:
- Store & retrieve cards
- Track card usage
- Evolve cards based on feedback
- Provide search API
- Manage relationships
- Track transparency

**API Endpoints**:
```python
# CRUD
POST   /api/v1/cards                    # Create card
POST   /api/v1/cards/batch              # Create multiple cards
GET    /api/v1/cards/{card_id}          # Get card
GET    /api/v1/cards                    # List cards (filter by type, tenant)
PATCH  /api/v1/cards/{card_id}          # Update card
DELETE /api/v1/cards/{card_id}          # Soft delete

# Search & Retrieval
GET    /api/v1/cards/search             # Search cards (full-text, semantic)
POST   /api/v1/cards/retrieve           # Retrieve cards for workflow

# Usage Tracking
POST   /api/v1/cards/{card_id}/usage    # Increment usage
GET    /api/v1/cards/{card_id}/usage    # Get usage stats

# Relationships
POST   /api/v1/cards/{card_id}/relationships  # Link cards
GET    /api/v1/cards/{card_id}/relationships  # Get related cards

# Transparency
GET    /api/v1/cards/{card_id}/sources  # Get sources & confidence
POST   /api/v1/cards/{card_id}/feedback # Submit feedback
```

**Architettura**:
```
cards/
├── api/
│   ├── main.py                 # FastAPI app (porta 8002)
│   ├── endpoints/
│   │   ├── cards.py           # CRUD endpoints
│   │   ├── search.py          # Search & retrieval
│   │   ├── usage.py           # Usage tracking
│   │   └── relationships.py   # Card relationships
│   └── dependencies.py
├── application/
│   ├── use_cases/
│   │   ├── create_card.py
│   │   ├── retrieve_cards_for_workflow.py
│   │   ├── track_usage.py
│   │   └── evolve_card.py
│   └── services/
│       ├── card_creation_service.py
│       └── card_evolution_service.py
├── domain/
│   └── models/
│       ├── card.py            # ContextCard model
│       ├── card_type.py       # CardType enum
│       └── card_relationship.py
└── infrastructure/
    ├── repositories/
    │   ├── card_repository.py
    │   └── card_usage_repository.py
    └── search/
        ├── semantic_search.py  # Embeddings-based
        └── full_text_search.py # PostgreSQL FTS
```

---

### **3. WORKFLOW Microservice** (Refactored da CGS Core)

**Port**: 8000  
**Responsabilità**:
- Execute workflows
- Orchestrate tasks
- Execute agents
- Provide tools
- ⭐ **NEW**: Retrieve context from **CARDS API** (not file KB)
- ⭐ **NEW**: Track which cards are used
- ⭐ **NEW**: Update card metrics with performance

**API Changes**:
```python
# OLD (attuale)
POST /api/v1/content/generate
{
    "workflow_type": "premium_newsletter",
    "client_profile": "Siebert",
    "topic": "AI trends",
    "context": {...}  # Dict generico
}

# NEW (target)
POST /api/v1/workflow/execute
{
    "workflow_type": "premium_newsletter",
    "card_ids": [
        "uuid-company-card",
        "uuid-voice-card",
        "uuid-audience-card"
    ],
    "parameters": {
        "topic": "AI trends",
        "custom_instructions": "..."
    }
}
```

**Modifiche Interne**:
```python
# OLD: RAGTool reads from file KB
class RAGTool:
    def execute(self, query: str) -> str:
        # Read from data/knowledge_base/*.md
        docs = load_from_files()
        return search(docs, query)

# NEW: ContextCardTool reads from Cards API
class ContextCardTool:
    def __init__(self, cards_client: CardsClient):
        self.cards_client = cards_client
    
    async def execute(self, query: str, card_ids: List[UUID]) -> str:
        # Retrieve cards from Cards API
        cards = await self.cards_client.retrieve_cards(
            card_ids=card_ids,
            query=query
        )
        
        # Track usage
        for card in cards:
            await self.cards_client.track_usage(card.card_id)
        
        return format_cards_for_agent(cards)
```

---

## 📋 PIANO DI MIGRAZIONE

### **Fase 0: API Contracts & Versioning Strategy** (1 settimana) ⭐ **RAFFINATO**

**Obiettivo**: Definire contratti API condivisi, shared package, client auto-generati, contract tests come gate CI

---

#### **0.1: Shared Package con Enum e Mapping Bloccati** (1.5 giorni) 🔒

**Obiettivo**: Pacchetto unico `fylle-shared` per evitare duplicazioni tra repos

**Tasks**:
1. Create `shared/` package come **Python package installabile**
2. **Blocca enum e mapping** in `shared/enums.py`:
   ```python
   class CardType(str, Enum):
       COMPANY = "company"
       AUDIENCE = "audience"
       VOICE = "voice"
       INSIGHT = "insight"
       # v1.1: PRODUCT, PERSONA, CAMPAIGN, TOPIC

   # Mapping atomico: CompanySnapshot → Cards
   SNAPSHOT_TO_CARD_MAPPING = {
       "company": CardType.COMPANY,
       "audience": CardType.AUDIENCE,
       "voice": CardType.VOICE,
       "insights": CardType.INSIGHT
   }
   ```
3. Implement `shared/models/card.py` (ContextCard, CardUsageEvent)
4. Implement `shared/models/workflow.py` (WorkflowRequest, WorkflowResult)
5. Implement `shared/models/common.py` (Pagination, ErrorResponse, IdempotencyKey)
6. **Package as `fylle-shared==0.1.0`** con `setup.py` e `pyproject.toml`
7. Publish to **private PyPI** o **Git submodule** (decisione team)

**Deliverables**:
- ✅ `shared/` package installabile via `pip install fylle-shared`
- ✅ Enum e mapping bloccati (single source of truth)
- ✅ Versioning semantico (0.1.0, 0.2.0, etc.)
- ✅ README con usage examples

**Struttura**:
```
shared/
├── fylle_shared/
│   ├── __init__.py
│   ├── enums.py              # CardType, WorkflowType (BLOCCATI)
│   ├── mappings.py           # SNAPSHOT_TO_CARD_MAPPING (BLOCCATO)
│   ├── models/
│   │   ├── card.py           # ContextCard, CardUsageEvent
│   │   ├── workflow.py       # WorkflowRequest, WorkflowResult
│   │   └── common.py         # Pagination, ErrorResponse, IdempotencyKey
│   └── utils/
│       ├── hashing.py        # Deterministic hash per dedup
│       └── tracing.py        # Trace ID propagation helpers
├── setup.py
├── pyproject.toml
└── README.md
```

---

#### **0.2: OpenAPI Specs con Golden Examples** (2 giorni) 📋

**Obiettivo**: Contratti completi con esempi "golden" per ogni endpoint critico

**Tasks**:
1. Define `contracts/cards-api-v1.yaml` con **golden examples**:
   - `POST /cards/batch` - Request/Response completi
   - `POST /cards/retrieve` - Request/Response completi
   - `POST /cards/{card_id}/usage` - Request/Response completi
2. Define `contracts/workflow-api-v1.yaml` con **golden examples**:
   - `POST /workflow/execute` - Request/Response completi (con card_ids)
   - `POST /workflow/execute` (legacy) - Deprecato ma documentato
3. Define `contracts/onboarding-api-v1.yaml` con **golden examples**:
   - `POST /onboarding/{session_id}/answers` - Response con card_ids
4. **Taglia superficie v1**: NO relationships, NO semantic search (v1.1)
5. Include **security schemes**: `X-Tenant-ID`, `X-Trace-ID`, `Idempotency-Key`

**Deliverables**:
- ✅ 3 OpenAPI specs con golden examples
- ✅ Validati con `openapi-spec-validator`
- ✅ Swagger UI generata per ogni spec

**Golden Example (Cards API)**:
```yaml
# contracts/cards-api-v1.yaml
paths:
  /cards/batch:
    post:
      summary: Create multiple cards from CompanySnapshot
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateCardsBatchRequest'
            examples:
              onboarding_snapshot:
                summary: Cards from onboarding session
                value:
                  tenant_id: "123e4567-e89b-12d3-a456-426614174000"
                  company_snapshot:
                    company:
                      name: "Acme Corp"
                      industry: "SaaS"
                      description: "Cloud CRM platform"
                    audience:
                      primary: "Tech executives"
                      pain_points: ["Manual processes", "Data silos"]
                    voice:
                      tone: "Professional, approachable"
                      style_guidelines: ["Active voice", "Short sentences"]
                    insights:
                      key_differentiators: ["AI-powered", "Easy integration"]
                  source_session_id: "456e7890-e89b-12d3-a456-426614174001"
                  created_by: "onboarding-service"
                  idempotency_key: "onboarding-456e7890-batch"
      responses:
        '201':
          content:
            application/json:
              examples:
                success:
                  value:
                    cards:
                      - card_id: "789e0123-e89b-12d3-a456-426614174002"
                        card_type: "company"
                        title: "Acme Corp"
                        content: {...}
                      - card_id: "789e0123-e89b-12d3-a456-426614174003"
                        card_type: "audience"
                        title: "Tech Executives"
                        content: {...}
                      - card_id: "789e0123-e89b-12d3-a456-426614174004"
                        card_type: "voice"
                        title: "Brand Voice"
                        content: {...}
                      - card_id: "789e0123-e89b-12d3-a456-426614174005"
                        card_type: "insight"
                        title: "Key Differentiators"
                        content: {...}
                    created_count: 4
                    idempotency_key: "onboarding-456e7890-batch"
```

---

#### **0.3: Auto-Generated Clients (NO Manual)** (1 giorno) 🤖

**Obiettivo**: Client generati da OpenAPI, usati ovunque, zero client manuali

**Tasks**:
1. Generate `fylle-cards-client` from `cards-api-v1.yaml`:
   ```bash
   openapi-python-client generate \
     --path contracts/cards-api-v1.yaml \
     --output-path clients/python/fylle-cards-client \
     --meta setup
   ```
2. Generate `fylle-workflow-client` from `workflow-api-v1.yaml`
3. **Package clients** con versioning (1.0.0 = API v1)
4. **Enforce usage**: Onboarding MUST use `fylle-cards-client`, Workflow MUST use `fylle-cards-client`
5. Add **retry logic** e **timeout** nei client generati (custom templates)
6. Add **tracing headers** propagation (X-Trace-ID, X-Session-ID)

**Deliverables**:
- ✅ `fylle-cards-client==1.0.0` installabile
- ✅ `fylle-workflow-client==1.0.0` installabile
- ✅ Zero client manuali (policy enforced in code review)
- ✅ Client include retry, timeout, tracing

**Usage Example**:
```python
# onboarding/application/use_cases/execute_onboarding.py

from fylle_cards_client import Client as CardsClient
from fylle_cards_client.models import CreateCardsBatchRequest
from fylle_shared.enums import CardType
from fylle_shared.utils.hashing import generate_idempotency_key

# Initialize client (auto-generated)
cards_client = CardsClient(
    base_url=settings.CARDS_API_URL,
    timeout=10.0,
    headers={"X-Tenant-ID": str(tenant_id)}
)

# Create cards (idempotent)
request = CreateCardsBatchRequest(
    tenant_id=tenant_id,
    company_snapshot=snapshot.model_dump(),
    source_session_id=session_id,
    created_by="onboarding-service",
    idempotency_key=generate_idempotency_key(session_id, "batch")
)

response = await cards_client.cards.create_cards_batch(request)
card_ids = [card.card_id for card in response.cards]
```

---

#### **0.4: Contract Tests as CI Gate** (1 giorno) 🚦

**Obiettivo**: Contract tests obbligatori per merge, validano implementazione vs contratto

**Tasks**:
1. Setup `schemathesis` per ogni API
2. Create `tests/contract/test_cards_api.py`:
   ```python
   import schemathesis

   schema = schemathesis.from_uri("http://localhost:8002/openapi.json")

   @schema.parametrize()
   def test_cards_api_contract(case):
       response = case.call()
       case.validate_response(response)
   ```
3. **CI Pipeline**: Contract tests run on every PR
4. **Merge gate**: PR cannot merge if contract tests fail
5. **Golden examples validation**: Test against golden examples in OpenAPI spec

**Deliverables**:
- ✅ Contract tests per Cards, Workflow, Onboarding
- ✅ CI pipeline con merge gate
- ✅ Golden examples tested automaticamente

**CI Pipeline**:
```yaml
# .github/workflows/contract-tests.yml
name: Contract Tests (Merge Gate)

on:
  pull_request:
    paths:
      - 'cards/**'
      - 'contracts/cards-api-v1.yaml'

jobs:
  contract-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Start Cards API
        run: docker-compose up -d cards

      - name: Wait for API
        run: ./scripts/wait-for-api.sh http://localhost:8002/health

      - name: Run Contract Tests
        run: |
          pip install schemathesis
          schemathesis run \
            --base-url http://localhost:8002 \
            contracts/cards-api-v1.yaml \
            --checks all \
            --hypothesis-max-examples=100 \
            --exitfirst  # Fail fast

      - name: Validate Golden Examples
        run: |
          pytest tests/contract/test_golden_examples.py -v

      # ❌ Se fallisce, PR non può essere merged
```

---

#### **0.5: Idempotency & Deduplication** (0.5 giorni) 🔐

**Obiettivo**: Hash deterministico + Idempotency-Key per retry sicuri

**Tasks**:
1. Implement `fylle_shared.utils.hashing.generate_content_hash()`:
   ```python
   def generate_content_hash(payload: dict) -> str:
       """Deterministic hash per dedup."""
       normalized = json.dumps(payload, sort_keys=True)
       return hashlib.sha256(normalized.encode()).hexdigest()
   ```
2. Implement `fylle_shared.utils.hashing.generate_idempotency_key()`:
   ```python
   def generate_idempotency_key(session_id: UUID, operation: str) -> str:
       """Generate idempotency key for retry safety."""
       return f"{operation}-{session_id}"
   ```
3. **Cards API**: Check `idempotency_key` in `/cards/batch`, return existing if duplicate
4. **Onboarding**: Always send `Idempotency-Key` header on mutate requests

**Deliverables**:
- ✅ Hashing utils in `fylle-shared`
- ✅ Idempotency logic in Cards API
- ✅ Onboarding usa Idempotency-Key

---

#### **0.6: Multi-Tenant Security & Rate Limiting** (0.5 giorni) 🔒

**Obiettivo**: X-Tenant-ID obbligatorio, RLS enforcement, rate limit per tenant

**Tasks**:
1. **Require `X-Tenant-ID` header** in all APIs (FastAPI dependency)
2. **Propagate tenant** to DB connection for RLS:
   ```python
   async with db.begin():
       await db.execute(text(f"SET app.current_tenant_id = '{tenant_id}'"))
   ```
3. **Rate limit** per tenant su mutate endpoints (100 req/min):
   ```python
   from slowapi import Limiter

   limiter = Limiter(key_func=lambda: request.headers.get("X-Tenant-ID"))

   @app.post("/cards/batch")
   @limiter.limit("100/minute")
   async def create_cards_batch(...):
       ...
   ```
4. **Log abuse** con trace_id quando rate limit hit

**Deliverables**:
- ✅ X-Tenant-ID required in all APIs
- ✅ RLS enforced via SET app.current_tenant_id
- ✅ Rate limit 100 req/min per tenant
- ✅ Abuse logging con trace_id

---

#### **0.7: Observability Minimo Vitale** (0.5 giorni) 📊

**Obiettivo**: Trace ID propagation, metriche chiave, logging strutturato

**Tasks**:
1. **Propagate headers**: `X-Trace-ID`, `X-Session-ID` attraverso tutti i microservizi
2. **Metriche chiave** (Prometheus):
   - `cards_retrieve_p95_ms` - p95 latency /cards/retrieve
   - `workflow_cache_hit_rate` - Cache hit rate in Workflow
   - `card_usage_events_total` - Counter per (card_id, workflow_type)
   - `workflow_card_only_percentage` - % workflow che usano solo card_ids
3. **Logging strutturato** (JSON):
   ```python
   logger.info(
       "cards_retrieved",
       extra={
           "trace_id": trace_id,
           "tenant_id": tenant_id,
           "card_ids": card_ids,
           "duration_ms": duration
       }
   )
   ```

**Deliverables**:
- ✅ Trace ID propagation helpers in `fylle-shared`
- ✅ 4 metriche chiave in Prometheus
- ✅ Logging strutturato JSON

---

### **Deliverables Finali Fase 0**:

| # | Deliverable | Status |
|---|-------------|--------|
| 1 | `fylle-shared==0.1.0` package (enum, mapping, models, utils) | ✅ |
| 2 | `contracts/cards-api-v1.yaml` con golden examples | ✅ |
| 3 | `contracts/workflow-api-v1.yaml` con golden examples | ✅ |
| 4 | `contracts/onboarding-api-v1.yaml` con golden examples | ✅ |
| 5 | `fylle-cards-client==1.0.0` auto-generated | ✅ |
| 6 | `fylle-workflow-client==1.0.0` auto-generated | ✅ |
| 7 | Contract tests con CI merge gate | ✅ |
| 8 | Idempotency & dedup logic | ✅ |
| 9 | Multi-tenant security & rate limiting | ✅ |
| 10 | Observability (tracing, metrics, logging) | ✅ |

**Esempio OpenAPI Spec (Cards API)**:
```yaml
# contracts/cards-api-v1.yaml
openapi: 3.1.0
info:
  title: Fylle Cards API
  version: 1.0.0
  description: Context Cards microservice API
  contact:
    name: Fylle Engineering
    email: engineering@fylle.ai

servers:
  - url: http://localhost:8002/api/v1
    description: Local development
  - url: https://cards.fylle.ai/api/v1
    description: Production

paths:
  /cards:
    post:
      operationId: createCard
      summary: Create a new context card
      tags: [Cards]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateCardRequest'
      responses:
        '201':
          description: Card created successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ContextCard'
        '400':
          $ref: '#/components/responses/BadRequest'
        '401':
          $ref: '#/components/responses/Unauthorized'

    get:
      operationId: listCards
      summary: List cards with filtering
      tags: [Cards]
      parameters:
        - name: tenant_id
          in: query
          required: true
          schema:
            type: string
            format: uuid
        - name: card_type
          in: query
          schema:
            $ref: '#/components/schemas/CardType'
        - name: is_active
          in: query
          schema:
            type: boolean
            default: true
        - name: page
          in: query
          schema:
            type: integer
            minimum: 1
            default: 1
        - name: page_size
          in: query
          schema:
            type: integer
            minimum: 1
            maximum: 100
            default: 20
      responses:
        '200':
          description: List of cards
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CardListResponse'

  /cards/{card_id}:
    get:
      operationId: getCard
      summary: Get card by ID
      tags: [Cards]
      parameters:
        - name: card_id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: Card details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ContextCard'
        '404':
          $ref: '#/components/responses/NotFound'

  /cards/batch:
    post:
      operationId: createCardsBatch
      summary: Create multiple cards from CompanySnapshot
      tags: [Cards]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateCardsBatchRequest'
      responses:
        '201':
          description: Cards created successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CardBatchResponse'

  /cards/retrieve:
    post:
      operationId: retrieveCards
      summary: Retrieve cards for workflow execution
      tags: [Cards]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/RetrieveCardsRequest'
      responses:
        '200':
          description: Retrieved cards
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CardListResponse'

components:
  schemas:
    CardType:
      type: string
      enum:
        - company
        - audience
        - voice
        - insight
        - product
        - persona
        - campaign
        - topic
      description: Type of context card

    ContextCard:
      type: object
      required:
        - card_id
        - tenant_id
        - card_type
        - title
        - content
        - version
        - is_active
        - created_at
        - updated_at
      properties:
        card_id:
          type: string
          format: uuid
        tenant_id:
          type: string
          format: uuid
        card_type:
          $ref: '#/components/schemas/CardType'
        title:
          type: string
          minLength: 1
          maxLength: 200
        description:
          type: string
          maxLength: 1000
        content:
          type: object
          description: Flexible JSONB content specific to card type
        tags:
          type: array
          items:
            type: string
        version:
          type: integer
          minimum: 1
        is_active:
          type: boolean
        confidence_score:
          type: number
          format: float
          minimum: 0.0
          maximum: 1.0
        quality_score:
          type: number
          format: float
          minimum: 0.0
          maximum: 1.0
        usage_count:
          type: integer
          minimum: 0
        last_used_at:
          type: string
          format: date-time
          nullable: true
        source_session_id:
          type: string
          format: uuid
          nullable: true
        source_workflow_id:
          type: string
          format: uuid
          nullable: true
        created_at:
          type: string
          format: date-time
        updated_at:
          type: string
          format: date-time
        created_by:
          type: string

    CreateCardRequest:
      type: object
      required:
        - tenant_id
        - card_type
        - title
        - content
        - created_by
      properties:
        tenant_id:
          type: string
          format: uuid
        card_type:
          $ref: '#/components/schemas/CardType'
        title:
          type: string
        description:
          type: string
        content:
          type: object
        tags:
          type: array
          items:
            type: string
        confidence_score:
          type: number
          format: float
        source_session_id:
          type: string
          format: uuid
        created_by:
          type: string

    CreateCardsBatchRequest:
      type: object
      required:
        - tenant_id
        - company_snapshot
        - source_session_id
        - created_by
      properties:
        tenant_id:
          type: string
          format: uuid
        company_snapshot:
          type: object
          description: CompanySnapshot from onboarding
        source_session_id:
          type: string
          format: uuid
        created_by:
          type: string

    RetrieveCardsRequest:
      type: object
      required:
        - tenant_id
        - card_ids
      properties:
        tenant_id:
          type: string
          format: uuid
        card_ids:
          type: array
          items:
            type: string
            format: uuid
          minItems: 1
        query:
          type: string
          description: Optional semantic search query

    CardListResponse:
      type: object
      required:
        - cards
        - total
        - page
        - page_size
      properties:
        cards:
          type: array
          items:
            $ref: '#/components/schemas/ContextCard'
        total:
          type: integer
        page:
          type: integer
        page_size:
          type: integer

    CardBatchResponse:
      type: object
      required:
        - cards
        - created_count
      properties:
        cards:
          type: array
          items:
            $ref: '#/components/schemas/ContextCard'
        created_count:
          type: integer

  responses:
    BadRequest:
      description: Bad request
      content:
        application/json:
          schema:
            type: object
            properties:
              error:
                type: string
              detail:
                type: string

    Unauthorized:
      description: Unauthorized
      content:
        application/json:
          schema:
            type: object
            properties:
              error:
                type: string

    NotFound:
      description: Resource not found
      content:
        application/json:
          schema:
            type: object
            properties:
              error:
                type: string

  securitySchemes:
    TenantHeader:
      type: apiKey
      in: header
      name: X-Tenant-ID
      description: Tenant ID for multi-tenancy isolation

security:
  - TenantHeader: []
```

---

### **Fase 1: Create Cards Microservice (Superficie Ridotta)** (2 settimane) 🎯

**Obiettivo**: Cards v1 con superficie minima - NO relationships, NO semantic search (→ v1.1)

---

#### **1.1: Setup FastAPI App + Database** (2 giorni)

**Tasks**:
1. Setup FastAPI app (porta 8002) con `fylle-shared` dependency
2. Create database migration per `context_cards` table:
   ```sql
   CREATE TABLE context_cards (
       card_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       tenant_id UUID NOT NULL,
       card_type TEXT NOT NULL CHECK (card_type IN ('company', 'audience', 'voice', 'insight')),
       title TEXT NOT NULL,
       description TEXT,
       content JSONB NOT NULL,
       tags TEXT[] DEFAULT '{}',
       version INTEGER DEFAULT 1,
       is_active BOOLEAN DEFAULT true,
       confidence_score FLOAT DEFAULT 0.8,
       usage_count INTEGER DEFAULT 0,
       last_used_at TIMESTAMPTZ,
       source_session_id UUID,
       created_at TIMESTAMPTZ DEFAULT NOW(),
       updated_at TIMESTAMPTZ DEFAULT NOW(),
       created_by TEXT NOT NULL,

       -- Deduplication
       content_hash TEXT NOT NULL,
       idempotency_key TEXT,

       UNIQUE(tenant_id, idempotency_key)
   );

   -- Indexes per performance
   CREATE INDEX idx_cards_tenant ON context_cards(tenant_id);
   CREATE INDEX idx_cards_type ON context_cards(card_type);
   CREATE INDEX idx_cards_active ON context_cards(is_active) WHERE is_active = true;
   CREATE INDEX idx_cards_tenant_type_active ON context_cards(tenant_id, card_type, is_active);  -- Covering index
   CREATE INDEX idx_cards_content_gin ON context_cards USING GIN (content);
   CREATE INDEX idx_cards_tags_gin ON context_cards USING GIN (tags);
   CREATE INDEX idx_cards_content_hash ON context_cards(content_hash);

   -- RLS
   ALTER TABLE context_cards ENABLE ROW LEVEL SECURITY;
   CREATE POLICY tenant_isolation ON context_cards
       USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
   ```
3. Create `card_usage_events` table:
   ```sql
   CREATE TABLE card_usage_events (
       event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       card_id UUID NOT NULL REFERENCES context_cards(card_id),
       tenant_id UUID NOT NULL,
       workflow_id UUID,
       workflow_type TEXT,
       used_at TIMESTAMPTZ DEFAULT NOW(),
       trace_id TEXT,
       session_id TEXT
   );

   CREATE INDEX idx_usage_card ON card_usage_events(card_id);
   CREATE INDEX idx_usage_tenant ON card_usage_events(tenant_id);
   CREATE INDEX idx_usage_workflow_type ON card_usage_events(workflow_type);
   CREATE INDEX idx_usage_time ON card_usage_events(used_at DESC);
   ```
4. Setup multi-tenant middleware (X-Tenant-ID required)
5. Setup rate limiting (100 req/min per tenant)

**Deliverables**:
- ✅ FastAPI app running on port 8002
- ✅ Database migrations applied
- ✅ Multi-tenant middleware active
- ✅ Rate limiting configured

---

#### **1.2: Implement CardRepository** (2 giorni)

**Tasks**:
1. Implement `CardRepository` con metodi:
   ```python
   class CardRepository:
       async def create(self, card: ContextCard) -> ContextCard
       async def create_batch(self, cards: List[ContextCard], idempotency_key: str) -> List[ContextCard]
       async def find_by_id(self, card_id: UUID, tenant_id: UUID) -> Optional[ContextCard]
       async def find_by_ids(self, card_ids: List[UUID], tenant_id: UUID) -> List[ContextCard]
       async def list_cards(
           self,
           tenant_id: UUID,
           card_type: Optional[CardType] = None,
           is_active: bool = True,
           page: int = 1,
           page_size: int = 20
       ) -> Tuple[List[ContextCard], int]
       async def increment_usage(self, card_id: UUID, tenant_id: UUID) -> None
   ```
2. **Idempotency logic** in `create_batch()`:
   ```python
   async def create_batch(self, cards: List[ContextCard], idempotency_key: str):
       # Check if already created
       existing = await self.find_by_idempotency_key(idempotency_key)
       if existing:
           return existing  # Return existing cards

       # Create new cards
       for card in cards:
           card.content_hash = generate_content_hash(card.content)

       # Insert with idempotency_key
       ...
   ```
3. **Deduplication** by content_hash (optional check)
4. **RLS enforcement**: Set `app.current_tenant_id` before queries

**Deliverables**:
- ✅ CardRepository implemented
- ✅ Idempotency logic working
- ✅ Deduplication by content_hash
- ✅ RLS enforced

---

#### **1.3: Implement API Endpoints (v1 - Superficie Ridotta)** (3 giorni)

**Obiettivo**: Solo retrieve by IDs, list filtrata, usage tracking. NO relationships, NO semantic search.

**Endpoints v1**:
```python
# cards/api/endpoints.py

from fylle_shared.models.card import ContextCard, CardType
from fylle_shared.models.common import Pagination, ErrorResponse

@app.post("/api/v1/cards", status_code=201)
async def create_card(
    request: CreateCardRequest,
    tenant_id: UUID = Depends(get_tenant_id),
    trace_id: str = Depends(get_trace_id)
) -> ContextCard:
    """Create single card."""
    ...

@app.post("/api/v1/cards/batch", status_code=201)
async def create_cards_batch(
    request: CreateCardsBatchRequest,
    tenant_id: UUID = Depends(get_tenant_id),
    trace_id: str = Depends(get_trace_id)
) -> CardBatchResponse:
    """
    Create cards from CompanySnapshot (idempotent).

    Uses idempotency_key for safe retries.
    Returns existing cards if idempotency_key already processed.
    """
    # Check idempotency
    if request.idempotency_key:
        existing = await card_repo.find_by_idempotency_key(
            request.idempotency_key,
            tenant_id
        )
        if existing:
            return CardBatchResponse(cards=existing, created_count=0)

    # Create cards from snapshot
    cards = await card_service.create_from_snapshot(
        snapshot=request.company_snapshot,
        tenant_id=tenant_id,
        source_session_id=request.source_session_id,
        created_by=request.created_by,
        idempotency_key=request.idempotency_key
    )

    return CardBatchResponse(cards=cards, created_count=len(cards))

@app.get("/api/v1/cards/{card_id}")
async def get_card(
    card_id: UUID,
    tenant_id: UUID = Depends(get_tenant_id)
) -> ContextCard:
    """Get card by ID."""
    ...

@app.get("/api/v1/cards")
async def list_cards(
    tenant_id: UUID = Depends(get_tenant_id),
    card_type: Optional[CardType] = None,
    is_active: bool = True,
    page: int = 1,
    page_size: int = 20
) -> CardListResponse:
    """List cards with filtering (NO semantic search in v1)."""
    ...

@app.post("/api/v1/cards/retrieve")
async def retrieve_cards(
    request: RetrieveCardsRequest,
    tenant_id: UUID = Depends(get_tenant_id),
    trace_id: str = Depends(get_trace_id)
) -> CardListResponse:
    """
    Retrieve cards by IDs for workflow execution.

    v1: Simple retrieve by IDs (NO semantic search).
    v1.1: Add semantic search with query parameter.
    """
    cards = await card_repo.find_by_ids(request.card_ids, tenant_id)

    # Track retrieval
    await metrics.increment("cards_retrieve_total", {"tenant_id": tenant_id})

    return CardListResponse(cards=cards, total=len(cards))

@app.post("/api/v1/cards/{card_id}/usage")
async def track_usage(
    card_id: UUID,
    request: TrackUsageRequest,
    tenant_id: UUID = Depends(get_tenant_id),
    trace_id: str = Depends(get_trace_id)
) -> None:
    """Track card usage in workflow."""
    await card_repo.increment_usage(card_id, tenant_id)

    # Log usage event
    await usage_repo.create_event(
        card_id=card_id,
        tenant_id=tenant_id,
        workflow_id=request.workflow_id,
        workflow_type=request.workflow_type,
        trace_id=trace_id,
        session_id=request.session_id
    )

    # Metrics
    await metrics.increment(
        "card_usage_events_total",
        {"card_id": str(card_id), "workflow_type": request.workflow_type}
    )
```

**NOT in v1** (deferred to v1.1):
- ❌ `POST /cards/{card_id}/relationships` - Card relationships
- ❌ `GET /cards/search` - Semantic search
- ❌ `POST /cards/{card_id}/performance` - Performance tracking

**Deliverables**:
- ✅ 6 endpoints implemented (create, batch, get, list, retrieve, usage)
- ✅ Idempotency working in /batch
- ✅ Contract tests passing
- ✅ Swagger UI generated

---

#### **1.4: Implement CardCreationService** (2 giorni)

**Tasks**:
1. Implement `CardCreationService.create_from_snapshot()`:
   ```python
   from fylle_shared.mappings import SNAPSHOT_TO_CARD_MAPPING
   from fylle_shared.utils.hashing import generate_content_hash

   class CardCreationService:
       async def create_from_snapshot(
           self,
           snapshot: CompanySnapshot,
           tenant_id: UUID,
           source_session_id: UUID,
           created_by: str,
           idempotency_key: Optional[str] = None
       ) -> List[ContextCard]:
           """
           Create 4 atomic cards from CompanySnapshot.

           Uses SNAPSHOT_TO_CARD_MAPPING from fylle-shared.
           """
           cards = []

           # Company card
           if snapshot.company:
               cards.append(ContextCard(
                   tenant_id=tenant_id,
                   card_type=CardType.COMPANY,
                   title=snapshot.company.name,
                   description=snapshot.company.description,
                   content=snapshot.company.model_dump(),
                   tags=[snapshot.company.industry] if snapshot.company.industry else [],
                   source_session_id=source_session_id,
                   created_by=created_by
               ))

           # Audience card
           if snapshot.audience:
               cards.append(ContextCard(
                   tenant_id=tenant_id,
                   card_type=CardType.AUDIENCE,
                   title=f"{snapshot.company.name} - Target Audience",
                   content=snapshot.audience.model_dump(),
                   source_session_id=source_session_id,
                   created_by=created_by
               ))

           # Voice card
           if snapshot.voice:
               cards.append(ContextCard(
                   tenant_id=tenant_id,
                   card_type=CardType.VOICE,
                   title=f"{snapshot.company.name} - Brand Voice",
                   content=snapshot.voice.model_dump(),
                   source_session_id=source_session_id,
                   created_by=created_by
               ))

           # Insight card
           if snapshot.insights:
               cards.append(ContextCard(
                   tenant_id=tenant_id,
                   card_type=CardType.INSIGHT,
                   title=f"{snapshot.company.name} - Strategic Insights",
                   content=snapshot.insights.model_dump(),
                   source_session_id=source_session_id,
                   created_by=created_by
               ))

           # Create batch (idempotent)
           return await self.card_repo.create_batch(cards, idempotency_key)
   ```

**Deliverables**:
- ✅ CardCreationService implemented
- ✅ Uses SNAPSHOT_TO_CARD_MAPPING from fylle-shared
- ✅ Creates 4 atomic cards
- ✅ Idempotent batch creation

---

#### **1.5: Testing & Contract Validation** (3 giorni)

**Tasks**:
1. Unit tests per CardRepository (80% coverage)
2. Unit tests per CardCreationService
3. Integration tests per API endpoints
4. **Contract tests** (schemathesis):
   ```bash
   schemathesis run \
     --base-url http://localhost:8002 \
     contracts/cards-api-v1.yaml \
     --checks all
   ```
5. **Golden examples validation**:
   ```python
   def test_batch_creation_golden_example():
       # Load golden example from OpenAPI spec
       response = client.post("/api/v1/cards/batch", json=GOLDEN_EXAMPLE)
       assert response.status_code == 201
       assert len(response.json()["cards"]) == 4
   ```
6. Performance tests (p95 < 100ms for /retrieve)

**Deliverables**:
- ✅ Test coverage > 80%
- ✅ Contract tests passing
- ✅ Golden examples validated
- ✅ Performance tests passing (p95 < 100ms)

---

### **Deliverables Finali Fase 1**:

| # | Deliverable | Status |
|---|-------------|--------|
| 1 | Cards microservice running on port 8002 | ✅ |
| 2 | Database schema con indexes ottimizzati | ✅ |
| 3 | 6 API endpoints (NO relationships, NO semantic search) | ✅ |
| 4 | Idempotency & deduplication working | ✅ |
| 5 | Multi-tenant security (RLS) | ✅ |
| 6 | Rate limiting (100 req/min per tenant) | ✅ |
| 7 | Contract tests passing | ✅ |
| 8 | Test coverage > 80% | ✅ |
| 9 | Performance: p95 < 100ms for /retrieve | ✅ |
| 10 | Swagger UI con golden examples | ✅ |

---

### **Fase 2: Integrate Onboarding → Cards** (1 settimana)

**Obiettivo**: Onboarding crea cards invece di solo company_contexts

**Tasks**:
1. **Install `fylle-cards-client` package** in onboarding service
2. Configure CardsClient with base URL and auth
3. Modify ExecuteOnboardingUseCase to call Cards API `/cards/batch` endpoint
4. Store card_ids in session metadata (add `card_ids` field to OnboardingSession)
5. **Update Onboarding API contract** to include card_ids in response
6. **Run contract tests** to validate integration
7. Update tests (mock Cards API calls)
8. Deploy & verify

**Deliverables**:
- ✅ Onboarding creates 4 cards per session via Cards API
- ✅ card_ids stored in session
- ✅ Backward compatible (still saves company_contexts)
- ✅ **Contract tests passing for Onboarding API v1**
- ✅ **API changelog updated** with new fields

**API Contract Change**:
```yaml
# contracts/onboarding-api-v1.yaml (UPDATED)
paths:
  /onboarding/sessions/{session_id}:
    get:
      responses:
        '200':
          content:
            application/json:
              schema:
                type: object
                properties:
                  session_id:
                    type: string
                    format: uuid
                  card_ids:  # ⭐ NEW FIELD
                    type: array
                    items:
                      type: string
                      format: uuid
                    description: IDs of cards created from this session
                  # ... other fields
```

---

### **Fase 3: Refactor Workflow → Cards (con Cache LRU)** (2 settimane) 🚀

**Obiettivo**: Workflow legge da Cards API con cache locale, tracking completo, backward compat

---

#### **3.1: Install Client & Setup Cache** (1 giorno)

**Tasks**:
1. **Install `fylle-cards-client==1.0.0`** in workflow service
2. **Setup LRU cache** per cards con TTL differenziato:
   ```python
   from cachetools import TTLCache
   from typing import Tuple

   class CardCache:
       def __init__(self):
           # Cache key: (tenant_id, card_id, version)
           # TTL differenziato per tipo
           self.cache = TTLCache(maxsize=1000, ttl=3600)  # Default 1h

           # TTL per tipo (in secondi)
           self.ttl_by_type = {
               CardType.VOICE: 7200,      # 2h (cambia raramente)
               CardType.TOPIC: 7200,      # 2h (cambia raramente)
               CardType.COMPANY: 3600,    # 1h (cambia moderatamente)
               CardType.AUDIENCE: 3600,   # 1h (cambia moderatamente)
               CardType.INSIGHT: 1800,    # 30min (cambia frequentemente)
               CardType.CAMPAIGN: 1800,   # 30min (cambia frequentemente)
           }

       def get(self, tenant_id: UUID, card_id: UUID, version: int) -> Optional[ContextCard]:
           key = (tenant_id, card_id, version)
           return self.cache.get(key)

       def set(self, card: ContextCard):
           key = (card.tenant_id, card.card_id, card.version)
           ttl = self.ttl_by_type.get(card.card_type, 3600)
           self.cache[key] = card

           # Metrics
           metrics.increment("workflow_cache_set", {"card_type": card.card_type})

       def invalidate(self, tenant_id: UUID, card_id: UUID):
           # Invalidate all versions
           keys_to_remove = [k for k in self.cache.keys() if k[0] == tenant_id and k[1] == card_id]
           for key in keys_to_remove:
               del self.cache[key]
   ```
3. Configure CardsClient with retry & timeout:
   ```python
   from fylle_cards_client import Client as CardsClient

   cards_client = CardsClient(
       base_url=settings.CARDS_API_URL,
       timeout=5.0,  # 5s timeout
       headers={"X-Tenant-ID": str(tenant_id)}
   )
   ```

**Deliverables**:
- ✅ `fylle-cards-client` installed
- ✅ LRU cache con TTL differenziato
- ✅ Cache metrics (set, hit, miss)

---

#### **3.2: Implement ContextCardTool (Replace RAGTool)** (2 giorni)

**Tasks**:
1. Implement `ContextCardTool` che usa Cards API + cache:
   ```python
   from fylle_cards_client import Client as CardsClient
   from fylle_shared.models.card import ContextCard

   class ContextCardTool:
       """
       Tool for agents to retrieve context from Cards API.

       Replaces RAGTool (file-based KB).
       Uses LRU cache with TTL differentiated by card type.
       """

       def __init__(
           self,
           cards_client: CardsClient,
           cache: CardCache,
           tenant_id: UUID,
           trace_id: str
       ):
           self.cards_client = cards_client
           self.cache = cache
           self.tenant_id = tenant_id
           self.trace_id = trace_id

       async def execute(
           self,
           card_ids: List[UUID],
           workflow_id: UUID,
           workflow_type: str
       ) -> str:
           """
           Retrieve cards for agent context.

           1. Check cache first
           2. Fetch missing from Cards API
           3. Track usage
           4. Format for agent
           """
           cards = []
           missing_ids = []

           # Check cache
           for card_id in card_ids:
               cached = self.cache.get(self.tenant_id, card_id, version=1)  # TODO: version tracking
               if cached:
                   cards.append(cached)
                   metrics.increment("workflow_cache_hit", {"card_type": cached.card_type})
               else:
                   missing_ids.append(card_id)
                   metrics.increment("workflow_cache_miss")

           # Fetch missing from API
           if missing_ids:
               response = await self.cards_client.cards.retrieve_cards(
                   RetrieveCardsRequest(
                       tenant_id=self.tenant_id,
                       card_ids=missing_ids
                   )
               )

               # Cache fetched cards
               for card in response.cards:
                   self.cache.set(card)
                   cards.append(card)

           # Track usage for all cards
           for card in cards:
               await self.cards_client.cards.track_usage(
                   card_id=card.card_id,
                   request=TrackUsageRequest(
                       workflow_id=workflow_id,
                       workflow_type=workflow_type,
                       session_id=self.trace_id
                   )
               )

           # Metrics
           cache_hit_rate = len(cards) - len(missing_ids) / len(card_ids) if card_ids else 0
           metrics.gauge("workflow_cache_hit_rate", cache_hit_rate)

           # Format for agent
           return self._format_cards_for_agent(cards)

       def _format_cards_for_agent(self, cards: List[ContextCard]) -> str:
           """Format cards into readable context for agent."""
           sections = []

           for card in cards:
               section = f"""
   ## {card.title} ({card.card_type})

   {self._format_card_content(card.card_type, card.content)}

   ---
   Confidence: {card.confidence_score:.2f}
   Last updated: {card.updated_at.strftime('%Y-%m-%d')}
   Usage: {card.usage_count} times
   """
               sections.append(section)

           return "\n\n".join(sections)
   ```

**Deliverables**:
- ✅ ContextCardTool implemented
- ✅ Cache-first retrieval
- ✅ Usage tracking per card
- ✅ Cache hit rate metrics

---

#### **3.3: Update Workflow API (Backward Compatible)** (2 giorni)

**Tasks**:
1. **Update Workflow API contract** to accept `card_ids`:
   ```yaml
   # contracts/workflow-api-v1.yaml
   paths:
     /workflow/execute:
       post:
         requestBody:
           content:
             application/json:
               schema:
                 type: object
                 properties:
                   workflow_type:
                     type: string
                   card_ids:  # ⭐ NEW (preferred)
                     type: array
                     items:
                       type: string
                       format: uuid
                   context:  # ⚠️ DEPRECATED (backward compat)
                     type: object
                     deprecated: true
                     description: |
                       DEPRECATED: Use card_ids instead.
                       Will be removed in v2.0 (2026-04-26).
                   parameters:
                     type: object
   ```
2. **Modify workflow handlers** to accept both `card_ids` (new) and `context` (legacy):
   ```python
   @app.post("/api/v1/workflow/execute")
   async def execute_workflow(
       request: WorkflowExecuteRequest,
       tenant_id: UUID = Depends(get_tenant_id),
       trace_id: str = Depends(get_trace_id)
   ):
       # Prefer card_ids (new way)
       if request.card_ids:
           # Retrieve cards from Cards API
           context_tool = ContextCardTool(
               cards_client=cards_client,
               cache=card_cache,
               tenant_id=tenant_id,
               trace_id=trace_id
           )
           context_str = await context_tool.execute(
               card_ids=request.card_ids,
               workflow_id=workflow_id,
               workflow_type=request.workflow_type
           )

           # Metrics: track card-only usage
           metrics.increment("workflow_card_only_total")

       # Fallback to legacy context (deprecated)
       elif request.context:
           logger.warning(
               "workflow_using_legacy_context",
               extra={
                   "trace_id": trace_id,
                   "workflow_type": request.workflow_type,
                   "deprecation_notice": "Use card_ids instead. context will be removed in v2.0"
               }
           )
           context_str = format_legacy_context(request.context)

           # Metrics: track legacy usage
           metrics.increment("workflow_legacy_context_total")

       else:
           raise HTTPException(400, "Either card_ids or context required")

       # Execute workflow
       result = await workflow_engine.execute(
           workflow_type=request.workflow_type,
           context=context_str,
           parameters=request.parameters
       )

       return result
   ```
3. **Add deprecation headers** for legacy usage:
   ```python
   if request.context:
       response.headers["X-API-Deprecation-Warning"] = "context parameter is deprecated, use card_ids"
       response.headers["X-API-Migration-Guide"] = "https://docs.fylle.ai/migration/context-to-cards"
   ```

**Deliverables**:
- ✅ Workflow API accepts card_ids (preferred)
- ✅ Backward compatible con context (deprecated)
- ✅ Deprecation warnings in headers
- ✅ Metrics per card-only vs legacy usage

---

#### **3.4: Migrate Existing KB to Cards** (2 giorni)

**Tasks**:
1. Create migration script `scripts/migrate_kb_to_cards.py`:
   ```python
   async def migrate_kb_to_cards():
       """
       One-time migration: file-based KB → Cards.

       Reads from data/knowledge_base/*.md
       Creates cards in Cards API
       """
       kb_files = Path("data/knowledge_base").glob("*.md")

       for file in kb_files:
           content = file.read_text()

           # Parse metadata from frontmatter
           metadata = parse_frontmatter(content)

           # Determine card type
           card_type = infer_card_type(metadata, content)

           # Create card
           card = await cards_client.cards.create_card(
               CreateCardRequest(
                   tenant_id=DEFAULT_TENANT_ID,
                   card_type=card_type,
                   title=metadata.get("title", file.stem),
                   content={"markdown": content, **metadata},
                   tags=metadata.get("tags", []),
                   created_by="migration-script"
               )
           )

           logger.info(f"Migrated {file.name} → card {card.card_id}")
   ```
2. Run migration script
3. Verify all KB content migrated
4. **Keep file KB for 1 release** (backward compat), then remove

**Deliverables**:
- ✅ Migration script executed
- ✅ All KB content in Cards
- ✅ File KB kept for 1 release (safety)

---

#### **3.5: Testing & Metrics** (3 giorni)

**Tasks**:
1. Integration tests con Cards API (mocked)
2. **Contract tests** for Workflow API v1
3. **Performance tests**:
   - p95 latency invariato o migliorato
   - Cache hit rate > 70% dopo warmup
4. **Metrics validation**:
   ```python
   # Prometheus metrics
   workflow_cache_hit_rate  # Gauge: cache hit rate
   workflow_cache_hit_total  # Counter: cache hits by card_type
   workflow_cache_miss_total  # Counter: cache misses
   workflow_card_only_total  # Counter: workflows using card_ids
   workflow_legacy_context_total  # Counter: workflows using context (deprecated)
   workflow_card_only_percentage  # Gauge: % workflows using card_ids
   cards_retrieve_p95_ms  # Histogram: p95 latency for /cards/retrieve
   card_usage_events_total  # Counter: usage events by (card_id, workflow_type)
   ```
5. Load testing (100 concurrent workflows)

**Deliverables**:
- ✅ Integration tests passing
- ✅ Contract tests passing
- ✅ Performance tests passing (p95 invariato)
- ✅ Cache hit rate > 70%
- ✅ 4 metriche chiave in Prometheus
- ✅ Load tests passing (100 concurrent)

---

### **Deliverables Finali Fase 3**:

| # | Deliverable | Status |
|---|-------------|--------|
| 1 | ContextCardTool implemented (replace RAGTool) | ✅ |
| 2 | LRU cache con TTL differenziato | ✅ |
| 3 | Workflow API accepts card_ids (preferred) | ✅ |
| 4 | Backward compatible con context (deprecated) | ✅ |
| 5 | KB migrated to Cards | ✅ |
| 6 | Cache hit rate > 70% | ✅ |
| 7 | 4 metriche chiave in Prometheus | ✅ |
| 8 | Contract tests passing | ✅ |
| 9 | Performance invariato (p95) | ✅ |
| 10 | Deprecation warnings active | ✅ |

**API Contract Change**:
```yaml
# contracts/workflow-api-v1.yaml (UPDATED)
paths:
  /workflow/execute:
    post:
      requestBody:
        content:
          application/json:
            schema:
              type: object
              required:
                - workflow_type
                - card_ids  # ⭐ NEW REQUIRED FIELD
              properties:
                workflow_type:
                  type: string
                card_ids:  # ⭐ NEW
                  type: array
                  items:
                    type: string
                    format: uuid
                  description: Context card IDs to use for execution
                parameters:
                  type: object
                  description: Workflow-specific parameters
```

**Migration Strategy**:
- ✅ Support both old (`context` dict) and new (`card_ids`) for 1 release cycle
- ✅ Deprecate `context` dict in API v1.1 (6 months notice)
- ✅ Remove `context` dict in API v2.0

---

### **Fase 4: Card Evolution & Analytics** (2 settimane)

**Obiettivo**: Cards evolvono basandosi su performance

**Tasks**:
1. Implement card performance tracking (track content generation success/failure)
2. Create card evolution logic (update confidence_score, quality_score)
3. **Extend Cards API contract** with performance endpoints
4. Add analytics dashboard (card usage, performance metrics)
5. Implement transparency features (sources, confidence display)
6. Add card relationships (link related cards)
7. **Update OpenAPI spec to v1.1** with new endpoints
8. **Run contract tests** for v1.1

**Deliverables**:
- ✅ Cards update based on content performance
- ✅ Analytics on card usage
- ✅ Transparency UI showing sources
- ✅ **Cards API v1.1 contract published**
- ✅ **Contract tests passing for v1.1**

**New API Endpoints (v1.1)**:
```yaml
# contracts/cards-api-v1.1.yaml (NEW VERSION)
paths:
  /cards/{card_id}/performance:
    post:
      operationId: trackCardPerformance
      summary: Track card performance in content generation
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                workflow_id:
                  type: string
                  format: uuid
                success:
                  type: boolean
                metrics:
                  type: object
      responses:
        '200':
          description: Performance tracked

  /cards/{card_id}/relationships:
    post:
      operationId: createCardRelationship
      summary: Link related cards
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                related_card_id:
                  type: string
                  format: uuid
                relationship_type:
                  type: string
                  enum: [derived_from, related_to, supersedes]
```

---

## 📊 METRICHE DI SUCCESSO

### **Separazione Microservizi**
- ✅ 3 microservizi indipendenti (Onboarding, Cards, Workflow)
- ✅ Ogni microservizio ha proprio database/schema
- ✅ Comunicazione via REST API (no shared DB)
- ✅ Deployable indipendentemente

### **Cards come Single Source of Truth**
- ✅ 100% dei workflow usano Cards API (no file KB)
- ✅ 100% delle sessioni onboarding creano cards
- ✅ Card usage tracked per ogni workflow run
- ✅ Cards evolvono basandosi su performance

### **Performance**
- ✅ Cards API response time < 100ms (p95)
- ✅ Workflow execution time invariato o migliorato
- ✅ Onboarding time invariato

### **Qualità**
- ✅ Test coverage > 80% per ogni microservizio
- ✅ API documentation completa (Swagger)
- ✅ Monitoring & logging per ogni servizio

---

## � API VERSIONING STRATEGY

### **Approccio: URL-based Versioning**

```
https://cards.fylle.ai/api/v1/cards
https://cards.fylle.ai/api/v2/cards
```

**Rationale**:
- ✅ Chiaro e esplicito
- ✅ Facile da cachare (CDN, proxy)
- ✅ Supporta multiple versioni in parallelo
- ✅ Standard de-facto per REST API

---

### **Versioning Rules**

#### **Major Version (v1 → v2)**
**Quando**: Breaking changes che richiedono modifiche client

**Esempi**:
- Rimozione di endpoint
- Rimozione di campi required
- Cambio tipo di dato (string → integer)
- Cambio semantica di endpoint

**Policy**:
- ✅ Supporto per 2 major versions in parallelo (v1 + v2)
- ✅ Deprecation notice: 6 mesi prima di rimuovere v1
- ✅ Migration guide pubblicata con v2

#### **Minor Version (v1.0 → v1.1)**
**Quando**: Backward-compatible additions

**Esempi**:
- Nuovi endpoint
- Nuovi campi opzionali
- Nuovi valori enum

**Policy**:
- ✅ Nessun breaking change
- ✅ Documentato in changelog
- ✅ Nessuna deprecation necessaria

#### **Patch Version (v1.0.0 → v1.0.1)**
**Quando**: Bug fixes, performance improvements

**Esempi**:
- Fix bug in validation
- Performance optimization
- Security patch

**Policy**:
- ✅ Nessun cambio API contract
- ✅ Documentato in changelog
- ✅ Deploy automatico

---

### **Deprecation Policy**

#### **Step 1: Announce (T+0)**
```yaml
# OpenAPI spec
paths:
  /cards/old-endpoint:
    get:
      deprecated: true
      description: |
        ⚠️ DEPRECATED: This endpoint will be removed in v2.0 (2026-04-26).
        Use /cards/new-endpoint instead.
        Migration guide: https://docs.fylle.ai/migration/v1-to-v2
```

**Actions**:
- ✅ Update OpenAPI spec with `deprecated: true`
- ✅ Add deprecation warning in response headers
- ✅ Publish migration guide
- ✅ Email notification to API consumers

#### **Step 2: Warning Period (T+3 months)**
```python
# API response headers
X-API-Deprecation-Warning: This endpoint is deprecated and will be removed on 2026-04-26
X-API-Migration-Guide: https://docs.fylle.ai/migration/v1-to-v2
```

**Actions**:
- ✅ Log usage of deprecated endpoints
- ✅ Send monthly reports to teams using deprecated endpoints
- ✅ Offer migration support

#### **Step 3: Final Notice (T+5 months)**
**Actions**:
- ✅ Final email notification (1 month before removal)
- ✅ Increase log level to WARNING for deprecated usage
- ✅ Update docs with removal date

#### **Step 4: Removal (T+6 months)**
**Actions**:
- ✅ Remove deprecated endpoint in new major version
- ✅ Return 410 Gone for old endpoint in v1
- ✅ Update changelog

---

### **API Changelog Structure**

```markdown
# Cards API Changelog

## [v1.1.0] - 2025-11-15

### Added
- `POST /cards/{card_id}/performance` - Track card performance metrics
- `POST /cards/{card_id}/relationships` - Create card relationships
- New field `quality_score` in ContextCard schema (optional)

### Changed
- `GET /cards` now supports `sort_by` parameter (default: `created_at`)

### Deprecated
- None

### Removed
- None

### Fixed
- Fixed pagination bug in `GET /cards` when `page_size > 100`

### Security
- Added rate limiting: 100 requests/minute per tenant

---

## [v1.0.0] - 2025-10-26

### Added
- Initial release
- `POST /cards` - Create card
- `GET /cards` - List cards
- `GET /cards/{card_id}` - Get card
- `POST /cards/batch` - Create cards from CompanySnapshot
- `POST /cards/retrieve` - Retrieve cards for workflow
```

---

### **Contract Testing Strategy**

#### **Tool: Schemathesis**

```python
# tests/contract/test_cards_api_contract.py

import schemathesis
from hypothesis import settings

# Load OpenAPI spec
schema = schemathesis.from_uri("http://localhost:8002/openapi.json")

@schema.parametrize()
@settings(max_examples=50)
def test_api_contract(case):
    """
    Test that Cards API implementation matches OpenAPI contract.

    Schemathesis will:
    - Generate test cases from OpenAPI spec
    - Send requests to API
    - Validate responses match schema
    - Check status codes
    - Validate headers
    """
    response = case.call()
    case.validate_response(response)
```

#### **CI Pipeline Integration**

```yaml
# .github/workflows/contract-tests.yml

name: Contract Tests

on:
  pull_request:
    paths:
      - 'cards/**'
      - 'contracts/cards-api-v1.yaml'

jobs:
  contract-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Start Cards API
        run: |
          cd cards
          docker-compose up -d
          sleep 10

      - name: Run Contract Tests
        run: |
          pip install schemathesis
          schemathesis run \
            --base-url http://localhost:8002 \
            contracts/cards-api-v1.yaml \
            --checks all \
            --hypothesis-max-examples=100

      - name: Validate OpenAPI Spec
        run: |
          pip install openapi-spec-validator
          openapi-spec-validator contracts/cards-api-v1.yaml
```

---

### **Client Library Generation**

#### **Tool: openapi-python-client**

```bash
# Generate Python client from OpenAPI spec
openapi-python-client generate \
  --path contracts/cards-api-v1.yaml \
  --output-path clients/python/fylle-cards-client

# Package structure
clients/python/fylle-cards-client/
├── fylle_cards_client/
│   ├── __init__.py
│   ├── client.py
│   ├── models/
│   │   ├── context_card.py
│   │   ├── card_type.py
│   │   └── create_card_request.py
│   └── api/
│       ├── cards.py
│       └── usage.py
├── setup.py
└── README.md
```

#### **Usage Example**

```python
# Install client
# pip install fylle-cards-client

from fylle_cards_client import Client
from fylle_cards_client.models import CreateCardRequest, CardType

# Initialize client
client = Client(base_url="http://localhost:8002")

# Create card
request = CreateCardRequest(
    tenant_id="uuid-tenant",
    card_type=CardType.COMPANY,
    title="Acme Corp",
    content={"industry": "SaaS", "description": "..."},
    created_by="onboarding-service"
)

card = client.cards.create_card(request)
print(f"Created card: {card.card_id}")

# Retrieve cards
cards = client.cards.retrieve_cards(
    tenant_id="uuid-tenant",
    card_ids=["uuid-1", "uuid-2"]
)
```

---

### **Shared Models Package**

```python
# shared/models/card.py

from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

class CardType(str, Enum):
    """Card type enumeration - shared across all services."""
    COMPANY = "company"
    AUDIENCE = "audience"
    VOICE = "voice"
    INSIGHT = "insight"
    PRODUCT = "product"
    PERSONA = "persona"
    CAMPAIGN = "campaign"
    TOPIC = "topic"

class ContextCard(BaseModel):
    """
    Context Card model - shared across all services.

    This model is generated from OpenAPI spec and used by:
    - Cards microservice (storage)
    - Workflow microservice (consumption)
    - Onboarding microservice (creation)
    """
    card_id: UUID
    tenant_id: UUID
    card_type: CardType
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    content: Dict[str, Any]
    tags: List[str] = Field(default_factory=list)
    version: int = Field(default=1, ge=1)
    is_active: bool = Field(default=True)
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    quality_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    usage_count: int = Field(default=0, ge=0)
    last_used_at: Optional[datetime] = None
    source_session_id: Optional[UUID] = None
    source_workflow_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    created_by: str

    class Config:
        json_schema_extra = {
            "example": {
                "card_id": "123e4567-e89b-12d3-a456-426614174000",
                "tenant_id": "123e4567-e89b-12d3-a456-426614174001",
                "card_type": "company",
                "title": "Acme Corp",
                "description": "Leading SaaS provider",
                "content": {
                    "industry": "SaaS",
                    "description": "Cloud-based solutions",
                    "key_offerings": ["CRM", "Analytics"]
                },
                "tags": ["saas", "b2b"],
                "version": 1,
                "is_active": True,
                "confidence_score": 0.85,
                "usage_count": 42,
                "created_at": "2025-10-26T10:00:00Z",
                "updated_at": "2025-10-26T10:00:00Z",
                "created_by": "onboarding-service"
            }
        }
```

---

## �🔧 DETTAGLI IMPLEMENTATIVI

### **Comunicazione tra Microservizi**

#### **Pattern: REST API (Sincrono)**

```python
# cards/infrastructure/clients/workflow_client.py
class WorkflowClient:
    """Client per chiamare Workflow microservice da Cards."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    async def notify_card_updated(self, card_id: UUID) -> None:
        """Notifica Workflow che una card è stata aggiornata."""
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{self.base_url}/api/v1/cards/webhook/updated",
                json={"card_id": str(card_id)}
            )

# workflow/infrastructure/clients/cards_client.py
class CardsClient:
    """Client per chiamare Cards microservice da Workflow."""

    def __init__(self, base_url: str = "http://localhost:8002"):
        self.base_url = base_url

    async def retrieve_cards(
        self,
        card_ids: List[UUID],
        tenant_id: UUID
    ) -> List[ContextCard]:
        """Retrieve cards for workflow execution."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/cards/retrieve",
                json={
                    "card_ids": [str(id) for id in card_ids],
                    "tenant_id": str(tenant_id)
                },
                headers={"X-Tenant-ID": str(tenant_id)}
            )
            response.raise_for_status()
            data = response.json()
            return [ContextCard(**card) for card in data["cards"]]

    async def track_usage(
        self,
        card_id: UUID,
        workflow_id: UUID,
        tenant_id: UUID
    ) -> None:
        """Track card usage in workflow."""
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{self.base_url}/api/v1/cards/{card_id}/usage",
                json={
                    "workflow_id": str(workflow_id),
                    "tenant_id": str(tenant_id)
                },
                headers={"X-Tenant-ID": str(tenant_id)}
            )
```

---

### **Database Schema per Cards**

```sql
-- =============================================================================
-- CARDS MICROSERVICE DATABASE SCHEMA
-- =============================================================================

-- Main cards table (simplified from documented schema)
CREATE TABLE context_cards (
    -- Identity
    card_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,

    -- Type
    card_type TEXT NOT NULL CHECK (card_type IN (
        'company', 'audience', 'voice', 'insight',
        'product', 'persona', 'campaign', 'topic'
    )),

    -- Metadata
    title TEXT NOT NULL,
    description TEXT,
    tags TEXT[] DEFAULT '{}',

    -- Content (JSONB - flexible structure)
    content JSONB NOT NULL,

    -- Versioning
    version INTEGER NOT NULL DEFAULT 1,
    is_active BOOLEAN NOT NULL DEFAULT true,
    parent_card_id UUID REFERENCES context_cards(card_id),

    -- Lifecycle
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by TEXT NOT NULL,

    -- Quality
    confidence_score FLOAT DEFAULT 0.8,
    quality_score FLOAT,

    -- Usage
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMPTZ,

    -- Source tracking
    source_session_id UUID,
    source_workflow_id UUID,
    source_context_id UUID
);

-- Card usage tracking (for analytics)
CREATE TABLE card_usage_events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    card_id UUID NOT NULL REFERENCES context_cards(card_id),
    tenant_id UUID NOT NULL,

    -- Usage context
    workflow_id UUID,
    workflow_type TEXT,
    agent_name TEXT,

    -- Timing
    used_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Metadata
    metadata JSONB DEFAULT '{}'
);

-- Indexes for performance
CREATE INDEX idx_cards_tenant ON context_cards(tenant_id);
CREATE INDEX idx_cards_type ON context_cards(card_type);
CREATE INDEX idx_cards_active ON context_cards(is_active) WHERE is_active = true;
CREATE INDEX idx_cards_tenant_type ON context_cards(tenant_id, card_type);
CREATE INDEX idx_cards_content_gin ON context_cards USING GIN (content);
CREATE INDEX idx_cards_tags_gin ON context_cards USING GIN (tags);

CREATE INDEX idx_usage_card ON card_usage_events(card_id);
CREATE INDEX idx_usage_tenant ON card_usage_events(tenant_id);
CREATE INDEX idx_usage_workflow ON card_usage_events(workflow_id);
CREATE INDEX idx_usage_time ON card_usage_events(used_at DESC);

-- RLS for multi-tenancy
ALTER TABLE context_cards ENABLE ROW LEVEL SECURITY;
ALTER TABLE card_usage_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_cards ON context_cards
    USING (tenant_id = current_setting('app.current_tenant_id')::uuid);

CREATE POLICY tenant_isolation_usage ON card_usage_events
    USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

---

### **Workflow Context Transformation**

#### **OLD: Dict-based Context**
```python
# Workflow riceve context come dict generico
context = {
    "client_profile": "Siebert",
    "topic": "AI trends",
    "target_audience": "Tech executives",
    "tone": "Professional",
    "company_snapshot": {  # Blob JSONB
        "company": {...},
        "audience": {...},
        "voice": {...},
        "insights": {...}
    }
}

# Agent riceve tutto il blob
agent_prompt = f"""
You are writing for {context['client_profile']}.
Company info: {context['company_snapshot']}
Topic: {context['topic']}
"""
```

#### **NEW: Card-based Context**
```python
# Workflow riceve card IDs
workflow_request = {
    "workflow_type": "premium_newsletter",
    "card_ids": [
        "uuid-company-card",
        "uuid-voice-card",
        "uuid-audience-card"
    ],
    "parameters": {
        "topic": "AI trends",
        "custom_instructions": "..."
    }
}

# Workflow retrieves cards from Cards API
cards = await cards_client.retrieve_cards(
    card_ids=workflow_request["card_ids"],
    tenant_id=tenant_id
)

# Build structured context from cards
context = {
    "company": cards[0].content,  # Company card
    "voice": cards[1].content,    # Voice card
    "audience": cards[2].content, # Audience card
    "parameters": workflow_request["parameters"]
}

# Agent riceve context strutturato
agent_prompt = f"""
You are writing for {context['company']['name']}.
Brand voice: {context['voice']['tone']}
Target audience: {context['audience']['primary']}
Topic: {context['parameters']['topic']}
"""

# Track usage
for card in cards:
    await cards_client.track_usage(
        card_id=card.card_id,
        workflow_id=workflow_id,
        tenant_id=tenant_id
    )
```

---

### **Agent Tool: ContextCardTool**

```python
# workflow/infrastructure/tools/context_card_tool.py

from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel

class ContextCardTool:
    """
    Tool for agents to retrieve context from Cards microservice.

    Replaces RAGTool which read from file-based KB.
    """

    def __init__(self, cards_client: CardsClient):
        self.cards_client = cards_client

    async def execute(
        self,
        query: str,
        card_ids: Optional[List[UUID]] = None,
        card_types: Optional[List[str]] = None,
        tenant_id: UUID = None,
        workflow_id: UUID = None
    ) -> str:
        """
        Retrieve relevant cards for agent context.

        Args:
            query: Natural language query
            card_ids: Specific card IDs to retrieve (optional)
            card_types: Filter by card types (optional)
            tenant_id: Tenant ID for isolation
            workflow_id: Workflow ID for usage tracking

        Returns:
            Formatted context string for agent
        """
        # If specific card IDs provided, retrieve those
        if card_ids:
            cards = await self.cards_client.retrieve_cards(
                card_ids=card_ids,
                tenant_id=tenant_id
            )
        else:
            # Otherwise, search by query and types
            cards = await self.cards_client.search_cards(
                query=query,
                card_types=card_types,
                tenant_id=tenant_id,
                limit=5
            )

        # Track usage for each card
        if workflow_id:
            for card in cards:
                await self.cards_client.track_usage(
                    card_id=card.card_id,
                    workflow_id=workflow_id,
                    tenant_id=tenant_id
                )

        # Format cards for agent consumption
        return self._format_cards_for_agent(cards)

    def _format_cards_for_agent(self, cards: List[ContextCard]) -> str:
        """Format cards into readable context for agent."""
        sections = []

        for card in cards:
            section = f"""
## {card.title} ({card.card_type})

{card.description or ''}

{self._format_card_content(card.card_type, card.content)}

---
Confidence: {card.confidence_score:.2f}
Last updated: {card.updated_at.strftime('%Y-%m-%d')}
"""
            sections.append(section)

        return "\n\n".join(sections)

    def _format_card_content(self, card_type: str, content: dict) -> str:
        """Format card content based on type."""
        if card_type == "company":
            return f"""
**Industry**: {content.get('industry', 'N/A')}
**Description**: {content.get('description', 'N/A')}
**Key Offerings**: {', '.join(content.get('key_offerings', []))}
**Differentiators**: {', '.join(content.get('differentiators', []))}
"""
        elif card_type == "voice":
            return f"""
**Tone**: {content.get('tone', 'N/A')}
**Style Guidelines**: {', '.join(content.get('style_guidelines', []))}
"""
        elif card_type == "audience":
            return f"""
**Primary Audience**: {content.get('primary', 'N/A')}
**Pain Points**: {', '.join(content.get('pain_points', []))}
**Desired Outcomes**: {', '.join(content.get('desired_outcomes', []))}
"""
        else:
            # Generic formatting for other types
            return "\n".join([f"**{k}**: {v}" for k, v in content.items()])
```

---

## 🎯 VANTAGGI ARCHITETTURA MICROSERVIZI

### **1. Separation of Concerns**
- ✅ Onboarding: Ingresso utenti, research, questions
- ✅ Cards: Storage, retrieval, evolution del contesto
- ✅ Workflow: Execution, orchestration, content generation

### **2. Scalabilità Indipendente**
- ✅ Cards può scalare separatamente (read-heavy)
- ✅ Workflow può scalare per picchi di generazione
- ✅ Onboarding può scalare per onboarding massivi

### **3. Evoluzione Indipendente**
- ✅ Cards può evolvere schema senza impattare Workflow
- ✅ Workflow può aggiungere nuovi tipi senza impattare Cards
- ✅ Onboarding può cambiare research logic senza impattare altri

### **4. Testing & Deployment**
- ✅ Ogni microservizio testabile indipendentemente
- ✅ Deploy indipendente (no downtime completo)
- ✅ Rollback granulare

### **5. Ownership & Team Structure**
- ✅ Team Cards: Focus su data quality, search, evolution
- ✅ Team Workflow: Focus su execution, agents, tools
- ✅ Team Onboarding: Focus su UX, research, questions

---

## ⚠️ SFIDE & MITIGAZIONI

### **Sfida 1: Latenza di Rete**
**Problema**: Chiamate HTTP tra microservizi aggiungono latenza

**Mitigazione**:
- ✅ Caching locale in Workflow (Redis)
- ✅ Batch retrieval (retrieve multiple cards in 1 call)
- ✅ Async/non-blocking calls dove possibile

### **Sfida 2: Consistenza Dati**
**Problema**: Cards e Workflow possono essere out-of-sync

**Mitigazione**:
- ✅ Event-driven updates (webhook quando card cambia)
- ✅ Cache invalidation strategy
- ✅ Eventual consistency acceptable (non critical)

### **Sfida 3: Debugging Distribuito**
**Problema**: Tracciare errori attraverso microservizi

**Mitigazione**:
- ✅ Distributed tracing (trace_id propagato)
- ✅ Centralized logging (tutti i log in Supabase o CloudWatch)
- ✅ Correlation IDs in ogni request

### **Sfida 4: Deployment Complexity**
**Problema**: 3 microservizi da deployare e coordinare

**Mitigazione**:
- ✅ Docker Compose per local dev
- ✅ Kubernetes/ECS per production
- ✅ CI/CD pipeline per ogni microservizio
- ✅ Health checks e readiness probes

---

**Next Steps**: Vuoi che proceda con l'implementazione della Fase 1 (Cards Microservice)?

