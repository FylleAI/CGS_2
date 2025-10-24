# 📁 Inventario Dettagliato File: CGS_2 → Fylle Core Pulse

## 🎯 Legenda

- ✅ **CORE** - Da mantenere e migrare
- ❌ **INFRA** - Da sostituire con Fylle Core Pulse
- 🔄 **ADAPT** - Da adattare per nuova architettura
- 📝 **DOC** - Documentazione (opzionale)

---

## 📦 CORE - Domain Layer

### `core/domain/entities/`

| File | Status | Descrizione | Migrazione |
|------|--------|-------------|------------|
| `agent.py` | ✅ CORE | Agent entity con system prompts | `app/agents/entities/agent.py` |
| `workflow.py` | ✅ CORE | Workflow entity e configuration | `app/workflows/entities/workflow.py` |
| `document.py` | ✅ CORE | Document entity per RAG | `app/knowledge/entities/document.py` |
| `content.py` | ✅ CORE | Content entity (generated content) | `app/content/entities/content.py` |
| `cost_event.py` | ✅ CORE | Cost tracking entity | `app/analytics/entities/cost_event.py` |

### `core/domain/value_objects/`

| File | Status | Descrizione | Migrazione |
|------|--------|-------------|------------|
| `provider.py` | ✅ CORE | LLM provider enum | `app/llm/value_objects/provider.py` |
| `model_config.py` | ✅ CORE | Model configuration | `app/llm/value_objects/model_config.py` |
| `tool_result.py` | ✅ CORE | Tool execution result | `app/tools/value_objects/tool_result.py` |

---

## 🏗️ CORE - Application Layer

### `core/application/use_cases/`

| File | Status | Descrizione | Migrazione |
|------|--------|-------------|------------|
| `generate_content.py` | ✅ CORE | Main content generation use case | `app/workflows/use_cases/generate_content.py` |
| `execute_workflow.py` | ✅ CORE | Workflow execution orchestration | `app/workflows/use_cases/execute_workflow.py` |

### `core/application/dto/`

| File | Status | Descrizione | Migrazione |
|------|--------|-------------|------------|
| `workflow_request.py` | ✅ CORE | Workflow request DTO | `app/workflows/dto/workflow_request.py` |
| `workflow_response.py` | ✅ CORE | Workflow response DTO | `app/workflows/dto/workflow_response.py` |

---

## 🔧 CORE - Infrastructure Layer

### `core/infrastructure/workflows/`

| File | Status | Descrizione | Migrazione |
|------|--------|-------------|------------|
| `registry.py` | ✅ CORE | Workflow registry pattern | `app/workflows/registry.py` |
| `base_handler.py` | ✅ CORE | Base workflow handler | `app/workflows/handlers/base_handler.py` |

### `core/infrastructure/workflows/handlers/`

| File | Status | Descrizione | Migrazione |
|------|--------|-------------|------------|
| `onboarding_content_handler.py` | ✅ CORE | **CRITICO** - Company Snapshot handler | `app/workflows/handlers/onboarding_handler.py` |
| `linkedin_post_handler.py` | ✅ CORE | LinkedIn post workflow | `app/workflows/handlers/linkedin_handler.py` |
| `blog_article_handler.py` | ✅ CORE | Blog article workflow | `app/workflows/handlers/blog_handler.py` |
| `analytics_dashboard_handler.py` | ✅ CORE | Analytics dashboard workflow | `app/workflows/handlers/analytics_handler.py` |

### `core/infrastructure/workflows/templates/`

| File | Status | Descrizione | Migrazione |
|------|--------|-------------|------------|
| `*.yaml` | ✅ CORE | Workflow templates (YAML) | `app/workflows/templates/*.yaml` |

### `core/infrastructure/orchestration/`

| File | Status | Descrizione | Migrazione |
|------|--------|-------------|------------|
| `prompt_builder.py` | ✅ CORE | **CRITICO** - Jinja2 prompt builder | `app/prompts/prompt_builder.py` |
| `workflow_orchestrator.py` | ✅ CORE | Workflow orchestration logic | `app/workflows/orchestrator.py` |

### `core/infrastructure/tools/`

| File | Status | Descrizione | Migrazione |
|------|--------|-------------|------------|
| `rag_tool.py` | ✅ CORE | **CRITICO** - RAG semantic search | `app/tools/rag_tool.py` |
| `perplexity_tool.py` | ✅ CORE | Perplexity web research | `app/tools/perplexity_tool.py` |
| `serper_tool.py` | ✅ CORE | Google search via Serper | `app/tools/serper_tool.py` |
| `image_generation_tool.py` | ✅ CORE | DALL-E image generation | `app/tools/image_generation_tool.py` |

### `core/infrastructure/factories/`

| File | Status | Descrizione | Migrazione |
|------|--------|-------------|------------|
| `llm_provider_factory.py` | ✅ CORE | LLM provider factory pattern | `app/llm/factories/provider_factory.py` |

### `core/infrastructure/external_services/`

| File | Status | Descrizione | Migrazione |
|------|--------|-------------|------------|
| `openai_adapter.py` | ✅ CORE | OpenAI API adapter | `app/llm/adapters/openai_adapter.py` |
| `anthropic_adapter.py` | ✅ CORE | Anthropic API adapter | `app/llm/adapters/anthropic_adapter.py` |
| `gemini_adapter.py` | ✅ CORE | Google Gemini adapter | `app/llm/adapters/gemini_adapter.py` |
| `deepseek_adapter.py` | ✅ CORE | DeepSeek adapter | `app/llm/adapters/deepseek_adapter.py` |

### `core/prompts/`

| File | Status | Descrizione | Migrazione |
|------|--------|-------------|------------|
| `*.md` | ✅ CORE | **CRITICO** - Prompt templates | `app/prompts/templates/*.md` |

---

## ❌ INFRA - Da Sostituire

### `core/infrastructure/database/`

| File | Status | Descrizione | Sostituzione |
|------|--------|-------------|--------------|
| `supabase_client.py` | ❌ INFRA | Supabase client | `app/core/database.py` (asyncpg) |

### `core/infrastructure/config/`

| File | Status | Descrizione | Sostituzione |
|------|--------|-------------|--------------|
| `settings.py` | 🔄 ADAPT | Settings (adattare) | `app/core/config.py` (Pydantic Settings) |

### `core/api/`

| File | Status | Descrizione | Sostituzione |
|------|--------|-------------|--------------|
| `main.py` | ❌ INFRA | Basic FastAPI app | `app/main.py` (Production-ready) |
| `endpoints.py` | 🔄 ADAPT | API endpoints (adattare) | `app/api/v1/workflows.py` |

---

## 🏢 ONBOARDING - Da Mantenere Completamente

### `onboarding/domain/`

| File | Status | Descrizione | Migrazione |
|------|--------|-------------|------------|
| `models.py` | ✅ CORE | **CRITICO** - CompanySnapshot, OnboardingSession | `app/onboarding/domain/models.py` |
| `cgs_contracts.py` | ✅ CORE | CGS integration contracts | `app/onboarding/domain/contracts.py` |
| `content_types.py` | ✅ CORE | Content type enums | `app/onboarding/domain/content_types.py` |

### `onboarding/application/use_cases/`

| File | Status | Descrizione | Migrazione |
|------|--------|-------------|------------|
| `create_session.py` | ✅ CORE | Create onboarding session | `app/onboarding/use_cases/create_session.py` |
| `research_company.py` | ✅ CORE | **CRITICO** - Perplexity research | `app/onboarding/use_cases/research_company.py` |
| `synthesize_snapshot.py` | ✅ CORE | **CRITICO** - Gemini synthesis | `app/onboarding/use_cases/synthesize_snapshot.py` |
| `collect_answers.py` | ✅ CORE | Collect clarifying answers | `app/onboarding/use_cases/collect_answers.py` |
| `execute_onboarding.py` | ✅ CORE | **CRITICO** - Execute full flow | `app/onboarding/use_cases/execute_onboarding.py` |

### `onboarding/application/builders/`

| File | Status | Descrizione | Migrazione |
|------|--------|-------------|------------|
| `payload_builder.py` | ✅ CORE | **CRITICO** - CGS payload builder | `app/onboarding/builders/payload_builder.py` |

### `onboarding/infrastructure/adapters/`

| File | Status | Descrizione | Migrazione |
|------|--------|-------------|------------|
| `perplexity_adapter.py` | ✅ CORE | Perplexity API adapter | `app/onboarding/adapters/perplexity_adapter.py` |
| `gemini_adapter.py` | ✅ CORE | Gemini API adapter | `app/onboarding/adapters/gemini_adapter.py` |
| `brevo_adapter.py` | ✅ CORE | Brevo email delivery | `app/onboarding/adapters/brevo_adapter.py` |
| `cgs_adapter.py` | ✅ CORE | CGS integration adapter | `app/onboarding/adapters/cgs_adapter.py` |

### `onboarding/infrastructure/repositories/`

| File | Status | Descrizione | Migrazione |
|------|--------|-------------|------------|
| `supabase_repository.py` | 🔄 ADAPT | Supabase repository | `app/onboarding/repositories/session_repository.py` (asyncpg) |

### `onboarding/api/`

| File | Status | Descrizione | Migrazione |
|------|--------|-------------|------------|
| `main.py` | ❌ INFRA | Basic FastAPI app | Integrare in `app/main.py` |
| `endpoints.py` | ✅ CORE | Onboarding endpoints | `app/api/v1/onboarding.py` |
| `models.py` | ✅ CORE | Request/Response models | `app/onboarding/schemas.py` |
| `dependencies.py` | 🔄 ADAPT | Dependency injection | Adattare per nuovo DI container |

---

## 🎨 FRONTEND - Da Mantenere Completamente

### `onboarding-frontend/src/components/`

| Directory | Status | Descrizione | Migrazione |
|-----------|--------|-------------|------------|
| `steps/` | ✅ CORE | **CRITICO** - Wizard steps | Mantenere |
| `cards/` | ✅ CORE | **CRITICO** - CompanySnapshotCard, AnalyticsCard | Mantenere |
| `wizard/` | ✅ CORE | Wizard container | Mantenere |
| `common/` | ✅ CORE | Common components | Mantenere |

### `onboarding-frontend/src/renderers/`

| File | Status | Descrizione | Migrazione |
|------|--------|-------------|------------|
| `RendererRegistry.ts` | ✅ CORE | **CRITICO** - Renderer registry pattern | Mantenere |
| `CompanySnapshotRenderer.tsx` | ✅ CORE | Company snapshot renderer | Mantenere |
| `AnalyticsRenderer.tsx` | ✅ CORE | Analytics renderer | Mantenere |
| `ContentRenderer.tsx` | ✅ CORE | Content renderer (fallback) | Mantenere |

### `onboarding-frontend/src/hooks/`

| File | Status | Descrizione | Migrazione |
|------|--------|-------------|------------|
| `useOnboarding.ts` | ✅ CORE | **CRITICO** - Onboarding hook | Mantenere |

### `onboarding-frontend/src/services/`

| File | Status | Descrizione | Migrazione |
|------|--------|-------------|------------|
| `api/onboardingApi.ts` | ✅ CORE | API client | Adattare per nuovi endpoints |
| `api/client.ts` | 🔄 ADAPT | HTTP client | Adattare per API Key auth |

### `onboarding-frontend/src/store/`

| File | Status | Descrizione | Migrazione |
|------|--------|-------------|------------|
| `onboardingStore.ts` | ✅ CORE | Zustand store | Mantenere |

---

## 📊 SUMMARY

### ✅ CORE Files (Da Mantenere): ~85 files
- Domain entities: 5 files
- Value objects: 3 files
- Use cases: 7 files
- Workflow handlers: 4 files
- Tools: 4 files
- LLM adapters: 4 files
- Onboarding: 15 files
- Frontend: 40+ files
- Prompts: 15+ files

### ❌ INFRA Files (Da Sostituire): ~10 files
- Database layer: 2 files
- API main: 2 files
- Config: 1 file
- Repository: 1 file

### 🔄 ADAPT Files (Da Adattare): ~5 files
- Settings: 1 file
- Dependencies: 1 file
- API client: 1 file
- Endpoints: 2 files

---

## 🎯 PRIORITÀ MIGRAZIONE

### **P0 - CRITICO (Settimana 1-2)**
1. `onboarding_content_handler.py` - Company Snapshot
2. `prompt_builder.py` - Prompt system
3. `rag_tool.py` - RAG tool
4. `CompanySnapshotCard.tsx` - Frontend card
5. `RendererRegistry.ts` - Renderer pattern

### **P1 - HIGH (Settimana 3-4)**
1. Workflow handlers (LinkedIn, Blog, Analytics)
2. LLM adapters (OpenAI, Anthropic, Gemini, DeepSeek)
3. Onboarding use cases (Research, Synthesis, Execute)
4. Frontend components (Steps, Wizard)

### **P2 - MEDIUM (Settimana 5-6)**
1. Tool system (Perplexity, Serper, Image Gen)
2. Workflow templates (YAML)
3. Prompt templates (MD)
4. Frontend hooks e store


