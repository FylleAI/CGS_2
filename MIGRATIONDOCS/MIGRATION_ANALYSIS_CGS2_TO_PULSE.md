# 🔄 Analisi Migrazione: CGS_2 → Fylle Core Pulse

## 📋 Executive Summary

Questo documento identifica cosa **MANTENERE** (CORE Fylle) e cosa **SOSTITUIRE** (Infrastruttura) nella migrazione da CGS_2 a Fylle Core Pulse.

---

## ✅ CORE FYLLE - DA MANTENERE E MIGRARE

### 1. 🤖 **Agent System** (CORE)

**Cosa mantenere:**
- `core/domain/entities/agent.py` - Agent entity con system prompts
- `core/infrastructure/agents/` - Specialist agents:
  - `copywriter_agent.py`
  - `research_specialist_agent.py`
  - `rag_specialist_agent.py`
  - `compliance_specialist_agent.py`
- Agent configurations e system prompt templates
- Agent executor logic

**Perché è CORE:**
- Differenziatore chiave di Fylle
- Multi-agent orchestration è il valore unico
- System prompts sono IP proprietario

**Migrazione:**
- Portare in `fylle-core-pulse/app/agents/`
- Issue: FYL-14 (Portare Agent System)

---

### 2. 📝 **Workflow Engine** (CORE)

**Cosa mantenere:**
- `core/domain/entities/workflow.py` - Workflow entity
- `core/infrastructure/workflows/` - Workflow handlers:
  - `onboarding_content_handler.py` (Company Snapshot!)
  - `linkedin_post_handler.py`
  - `blog_article_handler.py`
  - `analytics_dashboard_handler.py`
- `core/infrastructure/workflows/registry.py` - Workflow registry pattern
- `core/infrastructure/workflows/templates/` - YAML workflow templates
- Task orchestration logic

**Perché è CORE:**
- Template-based workflow è feature chiave
- Configurabilità per clienti
- Workflow registry pattern è architettura solida

**Migrazione:**
- Portare in `fylle-core-pulse/app/workflows/`
- Issue: FYL-12 (Portare Workflow Engine)

---

### 3. 🎨 **Prompt Builder System** (CORE)

**Cosa mantenere:**
- `core/infrastructure/orchestration/prompt_builder.py` - Jinja2 prompt builder
- `core/infrastructure/prompts/` - Prompt templates:
  - System prompts per agents
  - Task prompts per workflows
  - Dynamic context injection
- Prompt versioning logic

**Perché è CORE:**
- Prompt engineering è IP proprietario
- Template system è riutilizzabile
- Versioning è necessario per A/B testing

**Migrazione:**
- Portare in `fylle-core-pulse/app/prompts/`
- Integrare con Agent System

---

### 4. 🔧 **Tool System** (CORE)

**Cosa mantenere:**
- `core/infrastructure/tools/rag_tool.py` - RAG semantic search
- `core/infrastructure/tools/perplexity_tool.py` - Web research
- `core/infrastructure/tools/serper_tool.py` - Google search
- `core/infrastructure/tools/image_generation_tool.py` - DALL-E integration
- Tool registry pattern
- Tool result handling

**Perché è CORE:**
- Tool orchestration è feature chiave
- RAG è differenziatore
- Tool registry è architettura solida

**Migrazione:**
- Portare in `fylle-core-pulse/app/tools/`
- Issue: FYL-13 (Portare RAG Tool)

---

### 5. 🏢 **Onboarding System** (CORE)

**Cosa mantenere:**
- `onboarding/domain/models.py` - CompanySnapshot, OnboardingSession
- `onboarding/application/use_cases/` - Tutti i use cases:
  - `create_session.py`
  - `research_company.py`
  - `synthesize_snapshot.py`
  - `collect_answers.py`
  - `execute_onboarding.py`
- `onboarding/application/builders/payload_builder.py` - Payload builder
- `onboarding/infrastructure/adapters/` - Adapters:
  - `perplexity_adapter.py`
  - `gemini_adapter.py`
  - `brevo_adapter.py`
  - `cgs_adapter.py`

**Perché è CORE:**
- Onboarding flow è feature unica
- CompanySnapshot è IP proprietario
- Research + Synthesis è differenziatore

**Migrazione:**
- Portare in `fylle-core-pulse/app/onboarding/`
- Adattare per nuovo database schema

---

### 6. 🎨 **Frontend Components** (CORE)

**Cosa mantenere:**
- `onboarding-frontend/src/components/` - Tutti i componenti:
  - `steps/` - Wizard steps
  - `cards/` - CompanySnapshotCard, AnalyticsDashboardCard
  - `wizard/` - Wizard container
- `onboarding-frontend/src/renderers/` - Renderer registry pattern:
  - `RendererRegistry.ts`
  - `CompanySnapshotRenderer.tsx`
  - `AnalyticsRenderer.tsx`
- `onboarding-frontend/src/hooks/` - Custom hooks
- `onboarding-frontend/src/store/` - State management

**Perché è CORE:**
- UI/UX è differenziatore
- Renderer registry è architettura solida
- Metadata-driven rendering è innovativo

**Migrazione:**
- Portare in nuovo frontend Fylle
- Integrare con Clerk.com authentication

---

## ❌ INFRASTRUTTURA - DA SOSTITUIRE

### 1. 🗄️ **Database Layer** (SOSTITUIRE)

**Cosa sostituire:**
- `core/infrastructure/database/supabase_client.py` → **Neon PostgreSQL + asyncpg**
- Supabase Storage → **AWS S3**
- Supabase RPC calls → **Direct SQL queries**

**Perché sostituire:**
- Vendor lock-in Supabase
- Performance: Neon + pgvector HNSW è più veloce
- Controllo completo su database

**Nuova implementazione:**
- `fylle-core-pulse/app/core/database.py` - DatabaseManager con asyncpg
- Issue: FYL-7 (Database Migration)

---

### 2. 🔐 **Authentication** (SOSTITUIRE)

**Cosa sostituire:**
- Nessun sistema di autenticazione in CGS_2 → **API Key + JWT**

**Perché sostituire:**
- CGS_2 non ha autenticazione (BLOCKER CRITICO)
- Serve multi-tenancy con tenant isolation

**Nuova implementazione:**
- API Key authentication per client esterni (machine-to-machine)
- JWT authentication per frontend users (Clerk.com)
- Issue: FYL-5 (API Key), FYL-6 (JWT), FYL-82 (API Key implementation)

---

### 3. 🏗️ **Application Server** (SOSTITUIRE)

**Cosa sostituire:**
- `core/api/main.py` → **Nuovo FastAPI app con middleware stack**
- Basic error handling → **RFC 7807 Problem Details**
- No request tracing → **Request ID tracing**
- No health checks → **Health check system**

**Perché sostituire:**
- Serve production-ready infrastructure
- Monitoring, observability, debugging

**Nuova implementazione:**
- `fylle-core-pulse/app/main.py` - FastAPI app con:
  - Exception handler middleware (FYL-35)
  - Request ID middleware (FYL-39)
  - Health checks (FYL-40)
  - Audit logging (FYL-36)

---

### 4. 📊 **Monitoring & Observability** (AGGIUNGERE)

**Cosa manca in CGS_2:**
- No structured logging
- No metrics (Prometheus)
- No tracing (OpenTelemetry)
- No audit logging

**Nuova implementazione:**
- Structured logging con request_id
- Audit logging system (FYL-36)
- Health checks (FYL-40)
- Request ID tracing (FYL-39)

---

### 5. ⚙️ **Configuration Management** (AGGIUNGERE)

**Cosa manca in CGS_2:**
- No tenant-specific configuration
- No encrypted secrets storage
- No hierarchical config (global → tenant overrides)

**Nuova implementazione:**
- Configuration management per tenant (FYL-34)
- Encrypted API keys storage
- Tenant limits e settings

---

### 6. 🔄 **Background Jobs** (AGGIUNGERE)

**Cosa manca in CGS_2:**
- No async job processing
- Workflow execution è sincrono (timeout 30s)

**Nuova implementazione:**
- Background job system (Celery + Redis) (FYL-37)
- Job status tracking
- Retry logic per jobs

---

## 📦 PIANO DI MIGRAZIONE

### **Phase 1: Infrastructure Setup** (Week 1-2)
- ✅ Database migration (Supabase → Neon) - FYL-7
- ✅ API Key authentication - FYL-5, FYL-82
- ✅ JWT authentication - FYL-6
- ✅ Error handling framework - FYL-35
- ✅ Request ID tracing - FYL-39
- ✅ Health checks - FYL-40

### **Phase 2: Core Domain Migration** (Week 3-4)
- [ ] Domain entities - FYL-47
- [ ] Infrastructure adapters - FYL-48
- [ ] Workflow engine - FYL-12
- [ ] Agent system - FYL-14
- [ ] RAG tool - FYL-13

### **Phase 3: Onboarding Migration** (Week 5-6)
- [ ] Onboarding domain models
- [ ] Onboarding use cases
- [ ] Onboarding adapters
- [ ] Frontend components
- [ ] Renderer registry

### **Phase 4: Testing & Deployment** (Week 7-8)
- [ ] Integration tests
- [ ] End-to-end tests
- [ ] Performance testing
- [ ] Production deployment

---

## 🎯 DECISIONI CHIAVE

### ✅ MANTENERE (CORE Fylle):
1. **Agent System** - Multi-agent orchestration
2. **Workflow Engine** - Template-based workflows
3. **Prompt Builder** - Jinja2 prompt templates
4. **Tool System** - RAG, Perplexity, Serper, Image Gen
5. **Onboarding System** - CompanySnapshot, Research, Synthesis
6. **Frontend Components** - Renderer registry, Cards, Wizard

### ❌ SOSTITUIRE (Infrastruttura):
1. **Database** - Supabase → Neon PostgreSQL + asyncpg
2. **Storage** - Supabase Storage → AWS S3
3. **Authentication** - Nessuno → API Key + JWT (Clerk.com)
4. **Application Server** - Basic FastAPI → Production-ready con middleware
5. **Monitoring** - Nessuno → Structured logging + Audit + Health checks
6. **Configuration** - Nessuno → Tenant-specific config management
7. **Background Jobs** - Nessuno → Celery + Redis

---

## 📊 METRICHE DI SUCCESSO

### **Code Reuse:**
- **CORE (da mantenere):** ~60% del codice CGS_2
- **INFRASTRUTTURA (da sostituire):** ~40% del codice CGS_2

### **Effort Estimate:**
- **Infrastructure Setup:** 2 settimane
- **Core Migration:** 2 settimane
- **Onboarding Migration:** 2 settimane
- **Testing & Deployment:** 2 settimane
- **TOTALE:** 8 settimane (2 mesi)

---

## 🚀 NEXT STEPS

1. **Completare Phase 1** (Infrastructure) - In corso
2. **Iniziare Phase 2** (Core Domain Migration) - FYL-47, FYL-48
3. **Pianificare Phase 3** (Onboarding Migration)
4. **Setup CI/CD pipeline**
5. **Setup staging environment**

---

## 🔑 RACCOMANDAZIONI STRATEGICHE

### 1. **Priorità Assoluta: Onboarding System**

Il sistema di onboarding è il **differenziatore chiave** di Fylle:
- CompanySnapshot è IP proprietario
- Research + Synthesis è unico nel mercato
- Frontend con renderer registry è innovativo

**Azione:** Migrare onboarding PRIMA di altri workflow.

### 2. **Mantenere Prompt Templates**

I prompt templates in `core/prompts/*.md` sono **IP proprietario**:
- Prompt engineering è il valore aggiunto
- Template Jinja2 sono riutilizzabili
- Versioning è necessario per A/B testing

**Azione:** Portare TUTTI i prompt templates senza modifiche.

### 3. **Workflow Registry Pattern**

Il pattern di workflow registry è **architettura solida**:
- Decorator-based registration
- Dynamic workflow loading
- Template-based configuration

**Azione:** Mantenere il pattern esattamente come è.

### 4. **Renderer Registry Pattern (Frontend)**

Il renderer registry è **innovazione chiave**:
- Metadata-driven rendering
- Separation of concerns (data extraction vs rendering)
- Facile aggiungere nuovi renderer

**Azione:** Mantenere il pattern e documentarlo come best practice.

### 5. **Multi-Provider LLM Support**

Il supporto multi-provider è **differenziatore**:
- OpenAI, Anthropic, Gemini, DeepSeek
- Factory pattern per provider switching
- Tenant-specific provider configuration

**Azione:** Portare tutti gli adapter senza modifiche.

### 6. **RAG Tool**

Il RAG tool è **feature core**:
- Semantic search con pgvector
- Document chunking strategies
- Tenant isolation

**Azione:** Migrare con priorità alta (P0).

---

## ⚠️ RISCHI E MITIGAZIONI

### Rischio 1: **Perdita di Funzionalità**

**Rischio:** Dimenticare di migrare componenti critici.

**Mitigazione:**
- Usare `DETAILED_FILE_INVENTORY.md` come checklist
- Test end-to-end dopo ogni migrazione
- Mantenere CGS_2 come reference durante migrazione

### Rischio 2: **Breaking Changes nel Frontend**

**Rischio:** Cambiare API contracts rompe il frontend.

**Mitigazione:**
- Mantenere API contracts identici (Request/Response models)
- Versioning API (`/api/v1/`)
- Test integration frontend-backend

### Rischio 3: **Performance Degradation**

**Rischio:** Nuova infrastruttura più lenta di Supabase.

**Mitigazione:**
- Benchmark performance prima e dopo migrazione
- Neon + pgvector HNSW è più veloce di Supabase
- Connection pooling con asyncpg

### Rischio 4: **Data Loss durante Database Migration**

**Rischio:** Perdere dati durante migrazione Supabase → Neon.

**Mitigazione:**
- Backup completo prima di migrazione
- Data integrity check post-migrazione
- Rollback plan

---

## 📈 METRICHE DI SUCCESSO POST-MIGRAZIONE

### **Performance:**
- [ ] API response time < 200ms (p95)
- [ ] Database query time < 50ms (p95)
- [ ] Workflow execution time < 30s (p95)

### **Reliability:**
- [ ] Uptime > 99.9%
- [ ] Error rate < 0.1%
- [ ] Zero data loss

### **Security:**
- [ ] API Key authentication funzionante
- [ ] Tenant isolation verificato
- [ ] Secrets encrypted at rest

### **Developer Experience:**
- [ ] Test coverage > 80%
- [ ] Documentation completa
- [ ] CI/CD pipeline funzionante

---

## 📚 DOCUMENTI DI RIFERIMENTO

1. **MIGRATION_ANALYSIS_CGS2_TO_PULSE.md** (questo documento)
2. **DETAILED_FILE_INVENTORY.md** - Inventario completo file
3. **fylle-core-pulse_dettagliato.md** - Issue Fylle Core Pulse
4. **CGS_2/** - Codebase di riferimento

---

## ✅ CHECKLIST FINALE

### **Prima di Iniziare Migrazione:**
- [ ] Backup completo CGS_2
- [ ] Setup Fylle Core Pulse repository
- [ ] Setup Neon database
- [ ] Setup AWS S3 bucket
- [ ] Setup staging environment

### **Durante Migrazione:**
- [ ] Seguire `DETAILED_FILE_INVENTORY.md` come checklist
- [ ] Test ogni componente dopo migrazione
- [ ] Documentare breaking changes
- [ ] Mantenere changelog

### **Dopo Migrazione:**
- [ ] Test end-to-end completo
- [ ] Performance benchmark
- [ ] Security audit
- [ ] Documentation review
- [ ] Production deployment plan


