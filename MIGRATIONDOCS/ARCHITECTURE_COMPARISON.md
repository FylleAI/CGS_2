# 🏗️ Confronto Architetture: CGS_2 vs Fylle Core Pulse

## 📊 Architettura Attuale (CGS_2)

```
┌─────────────────────────────────────────────────────────────────┐
│                         CGS_2 ARCHITECTURE                       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                          FRONTEND LAYER                          │
├─────────────────────────────────────────────────────────────────┤
│  onboarding-frontend/                                            │
│  ├── components/                                                 │
│  │   ├── steps/          (Wizard steps)                         │
│  │   ├── cards/          (CompanySnapshotCard, AnalyticsCard)   │
│  │   └── wizard/         (Wizard container)                     │
│  ├── renderers/          ✅ CORE - Renderer Registry Pattern    │
│  ├── hooks/              (useOnboarding)                        │
│  └── store/              (Zustand state management)             │
└─────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────┐
│                           API LAYER                              │
├─────────────────────────────────────────────────────────────────┤
│  core/api/                                                       │
│  ├── main.py             ❌ INFRA - Basic FastAPI               │
│  └── endpoints.py        🔄 ADAPT - API endpoints               │
│                                                                  │
│  onboarding/api/                                                 │
│  ├── main.py             ❌ INFRA - Basic FastAPI               │
│  ├── endpoints.py        ✅ CORE - Onboarding endpoints         │
│  └── models.py           ✅ CORE - Request/Response models      │
└─────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────┐
│                       APPLICATION LAYER                          │
├─────────────────────────────────────────────────────────────────┤
│  core/application/                                               │
│  ├── use_cases/                                                  │
│  │   ├── generate_content.py    ✅ CORE                         │
│  │   └── execute_workflow.py    ✅ CORE                         │
│  └── dto/                        ✅ CORE                         │
│                                                                  │
│  onboarding/application/                                         │
│  ├── use_cases/                  ✅ CORE - Tutti i use cases    │
│  │   ├── create_session.py                                      │
│  │   ├── research_company.py    (Perplexity)                    │
│  │   ├── synthesize_snapshot.py (Gemini)                        │
│  │   ├── collect_answers.py                                     │
│  │   └── execute_onboarding.py                                  │
│  └── builders/                   ✅ CORE                         │
│      └── payload_builder.py     (CGS payload builder)           │
└─────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────┐
│                         DOMAIN LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│  core/domain/                                                    │
│  ├── entities/               ✅ CORE                             │
│  │   ├── agent.py           (Agent with system prompts)         │
│  │   ├── workflow.py        (Workflow definition)               │
│  │   ├── document.py        (RAG documents)                     │
│  │   ├── content.py         (Generated content)                 │
│  │   └── cost_event.py      (Cost tracking)                     │
│  └── value_objects/          ✅ CORE                             │
│      ├── provider.py         (LLM provider enum)                │
│      ├── model_config.py     (Model configuration)              │
│      └── tool_result.py      (Tool execution result)            │
│                                                                  │
│  onboarding/domain/                                              │
│  ├── models.py               ✅ CORE - CompanySnapshot          │
│  ├── cgs_contracts.py        ✅ CORE - CGS contracts            │
│  └── content_types.py        ✅ CORE - Content types            │
└─────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────┐
│                      INFRASTRUCTURE LAYER                        │
├─────────────────────────────────────────────────────────────────┤
│  core/infrastructure/                                            │
│  ├── workflows/              ✅ CORE                             │
│  │   ├── registry.py        (Workflow registry pattern)         │
│  │   ├── handlers/          (Workflow handlers)                 │
│  │   │   ├── onboarding_content_handler.py  🔥 CRITICO         │
│  │   │   ├── linkedin_post_handler.py                           │
│  │   │   ├── blog_article_handler.py                            │
│  │   │   └── analytics_dashboard_handler.py                     │
│  │   └── templates/         (YAML workflow templates)           │
│  ├── orchestration/          ✅ CORE                             │
│  │   ├── prompt_builder.py  🔥 CRITICO - Jinja2 prompts        │
│  │   └── workflow_orchestrator.py                               │
│  ├── tools/                  ✅ CORE                             │
│  │   ├── rag_tool.py         🔥 CRITICO - RAG semantic search  │
│  │   ├── perplexity_tool.py                                     │
│  │   ├── serper_tool.py                                         │
│  │   └── image_generation_tool.py                               │
│  ├── external_services/      ✅ CORE - LLM Adapters             │
│  │   ├── openai_adapter.py                                      │
│  │   ├── anthropic_adapter.py                                   │
│  │   ├── gemini_adapter.py                                      │
│  │   └── deepseek_adapter.py                                    │
│  ├── factories/              ✅ CORE                             │
│  │   └── llm_provider_factory.py                                │
│  ├── database/               ❌ INFRA - Supabase                │
│  │   └── supabase_client.py (DA SOSTITUIRE)                     │
│  └── config/                 🔄 ADAPT                            │
│      └── settings.py                                             │
│                                                                  │
│  onboarding/infrastructure/                                      │
│  ├── adapters/               ✅ CORE                             │
│  │   ├── perplexity_adapter.py                                  │
│  │   ├── gemini_adapter.py                                      │
│  │   ├── brevo_adapter.py                                       │
│  │   └── cgs_adapter.py                                         │
│  └── repositories/           🔄 ADAPT                            │
│      └── supabase_repository.py (DA ADATTARE)                   │
│                                                                  │
│  core/prompts/               ✅ CORE - IP Proprietario          │
│  └── *.md                    (Prompt templates)                 │
└─────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────┐
│                        DATABASE LAYER                            │
├─────────────────────────────────────────────────────────────────┤
│  Supabase PostgreSQL         ❌ INFRA - DA SOSTITUIRE           │
│  ├── pgvector                (Semantic search)                   │
│  ├── RLS policies            (Row-level security)                │
│  └── Storage                 (File storage)                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Architettura Target (Fylle Core Pulse)

```
┌─────────────────────────────────────────────────────────────────┐
│                   FYLLE CORE PULSE ARCHITECTURE                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                          FRONTEND LAYER                          │
├─────────────────────────────────────────────────────────────────┤
│  ✅ MANTENERE da CGS_2:                                          │
│  ├── components/steps/       (Wizard steps)                     │
│  ├── components/cards/       (CompanySnapshotCard, Analytics)   │
│  ├── renderers/              (Renderer Registry Pattern)        │
│  ├── hooks/useOnboarding     (Onboarding hook)                  │
│  └── store/                  (Zustand state)                    │
│                                                                  │
│  🆕 AGGIUNGERE:                                                  │
│  └── Authentication          (Clerk.com integration)            │
└─────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────┐
│                      API GATEWAY LAYER                           │
├─────────────────────────────────────────────────────────────────┤
│  app/main.py                 🆕 Production-Ready FastAPI        │
│  ├── Middleware Stack:                                          │
│  │   ├── ExceptionHandlerMiddleware    (FYL-35)                │
│  │   ├── RequestIDMiddleware           (FYL-39)                │
│  │   ├── AuthMiddleware                (API Key + JWT)         │
│  │   ├── TenantContextMiddleware       (FYL-33)                │
│  │   └── AuditLoggingMiddleware        (FYL-36)                │
│  ├── Health Checks:          (FYL-40)                           │
│  │   ├── /health                                                │
│  │   ├── /health/ready                                          │
│  │   └── /health/live                                           │
│  └── API Versioning:         /api/v1/                           │
└─────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────┐
│                         API ENDPOINTS                            │
├─────────────────────────────────────────────────────────────────┤
│  app/api/v1/                                                     │
│  ├── workflows.py            ✅ Da CGS_2                         │
│  ├── onboarding.py           ✅ Da CGS_2                         │
│  ├── agents.py               🆕 Agent management                │
│  ├── knowledge.py            🆕 RAG/Knowledge base              │
│  ├── admin/                  🆕 Admin endpoints                 │
│  │   ├── api_keys.py         (FYL-82)                           │
│  │   ├── tenants.py          (FYL-44)                           │
│  │   └── users.py            (FYL-45)                           │
│  └── auth/                   🆕 Authentication                  │
│      ├── login.py            (FYL-6)                            │
│      └── refresh.py                                             │
└─────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────┐
│                       APPLICATION LAYER                          │
├─────────────────────────────────────────────────────────────────┤
│  app/workflows/              ✅ Da CGS_2                         │
│  ├── use_cases/                                                  │
│  │   ├── generate_content.py                                    │
│  │   └── execute_workflow.py                                    │
│  ├── handlers/                                                   │
│  │   ├── onboarding_handler.py    🔥 CRITICO                   │
│  │   ├── linkedin_handler.py                                    │
│  │   ├── blog_handler.py                                        │
│  │   └── analytics_handler.py                                   │
│  └── templates/              (YAML workflows)                   │
│                                                                  │
│  app/onboarding/             ✅ Da CGS_2                         │
│  ├── use_cases/              (Tutti i use cases)                │
│  ├── builders/               (Payload builder)                  │
│  └── adapters/               (Perplexity, Gemini, Brevo, CGS)   │
│                                                                  │
│  app/agents/                 ✅ Da CGS_2                         │
│  ├── entities/agent.py                                          │
│  └── executor.py                                                │
│                                                                  │
│  app/tools/                  ✅ Da CGS_2                         │
│  ├── rag_tool.py             🔥 CRITICO                         │
│  ├── perplexity_tool.py                                         │
│  ├── serper_tool.py                                             │
│  └── image_generation_tool.py                                   │
└─────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────┐
│                         DOMAIN LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│  ✅ MANTENERE TUTTO da CGS_2:                                    │
│  ├── entities/               (Agent, Workflow, Document, etc.)  │
│  ├── value_objects/          (Provider, ModelConfig, etc.)      │
│  └── onboarding/models.py    (CompanySnapshot)                  │
└─────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────┐
│                      INFRASTRUCTURE LAYER                        │
├─────────────────────────────────────────────────────────────────┤
│  app/llm/                    ✅ Da CGS_2                         │
│  ├── adapters/               (OpenAI, Anthropic, Gemini, etc.)  │
│  └── factories/              (Provider factory)                 │
│                                                                  │
│  app/prompts/                ✅ Da CGS_2 - IP Proprietario      │
│  ├── prompt_builder.py       🔥 CRITICO - Jinja2               │
│  └── templates/*.md          (Prompt templates)                 │
│                                                                  │
│  app/core/                   🆕 Nuova Infrastruttura            │
│  ├── database.py             (DatabaseManager + asyncpg)        │
│  ├── config.py               (Pydantic Settings)                │
│  ├── security.py             (API Key + JWT)                    │
│  ├── tenant_context.py       (Multi-tenancy)                    │
│  └── audit_logger.py         (Audit logging)                    │
│                                                                  │
│  app/exceptions.py           🆕 Exception Hierarchy (FYL-35)    │
│  app/utils/                  🆕 Utilities                       │
│  ├── retry.py                (Retry logic - FYL-76)             │
│  └── circuit_breaker.py      (Circuit breaker - FYL-77)         │
└─────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────┐
│                        DATABASE LAYER                            │
├─────────────────────────────────────────────────────────────────┤
│  Neon PostgreSQL             🆕 Production Database             │
│  ├── pgvector + HNSW         (Faster semantic search)           │
│  ├── Connection pooling      (asyncpg)                          │
│  ├── Row-Level Security      (Multi-tenant isolation)           │
│  └── Database branches       (main, staging, dev)               │
│                                                                  │
│  AWS S3                      🆕 File Storage                    │
│  └── Document storage        (Replace Supabase Storage)         │
│                                                                  │
│  Redis                       🆕 Caching & Jobs                  │
│  ├── Config caching                                             │
│  ├── Rate limiting                                              │
│  └── Job queue (Celery)                                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 Confronto Componenti

| Componente | CGS_2 | Fylle Core Pulse | Azione |
|------------|-------|------------------|--------|
| **Frontend** | React + Vite | React + Vite | ✅ MANTENERE |
| **Renderer Registry** | ✅ Presente | ✅ Mantenere | ✅ MANTENERE |
| **API Framework** | FastAPI (basic) | FastAPI (production) | 🔄 UPGRADE |
| **Authentication** | ❌ Nessuno | API Key + JWT | 🆕 AGGIUNGERE |
| **Multi-tenancy** | ❌ Nessuno | Tenant Context | 🆕 AGGIUNGERE |
| **Database** | Supabase | Neon PostgreSQL | 🔄 MIGRARE |
| **Storage** | Supabase Storage | AWS S3 | 🔄 MIGRARE |
| **Workflow Engine** | ✅ Template-based | ✅ Mantenere | ✅ MANTENERE |
| **Agent System** | ✅ Multi-agent | ✅ Mantenere | ✅ MANTENERE |
| **Prompt Builder** | ✅ Jinja2 | ✅ Mantenere | ✅ MANTENERE |
| **RAG Tool** | ✅ pgvector | ✅ Mantenere | ✅ MANTENERE |
| **LLM Adapters** | ✅ 4 providers | ✅ Mantenere | ✅ MANTENERE |
| **Onboarding** | ✅ Completo | ✅ Mantenere | ✅ MANTENERE |
| **Error Handling** | ❌ Basic | RFC 7807 | 🆕 AGGIUNGERE |
| **Logging** | ❌ Basic | Structured + Audit | 🆕 AGGIUNGERE |
| **Health Checks** | ❌ Nessuno | ✅ Completo | 🆕 AGGIUNGERE |
| **Background Jobs** | ❌ Nessuno | Celery + Redis | 🆕 AGGIUNGERE |
| **Monitoring** | ❌ Nessuno | Prometheus + Grafana | 🆕 AGGIUNGERE |

---

## 🎯 Conclusione

### **CORE Fylle (60% del codice):**
- ✅ Workflow Engine + Handlers
- ✅ Agent System
- ✅ Prompt Builder + Templates
- ✅ Tool System (RAG, Perplexity, etc.)
- ✅ LLM Adapters (4 providers)
- ✅ Onboarding System completo
- ✅ Frontend completo (Renderer Registry)

### **Infrastruttura (40% del codice):**
- 🔄 Database (Supabase → Neon)
- 🔄 Storage (Supabase → S3)
- 🆕 Authentication (API Key + JWT)
- 🆕 Multi-tenancy (Tenant Context)
- 🆕 Error Handling (RFC 7807)
- 🆕 Monitoring (Logging, Health, Audit)
- 🆕 Background Jobs (Celery)

**La migrazione è FATTIBILE e STRATEGICA: manteniamo il CORE di Fylle e sostituiamo solo l'infrastruttura con una production-ready.**


