# 🚀 Piano d'Azione: Migrazione CGS_2 → Fylle Core Pulse

## 📋 Executive Summary

**Obiettivo:** Migrare il CORE di Fylle (workflow, agents, prompts, onboarding) da CGS_2 a Fylle Core Pulse, sostituendo l'infrastruttura con una production-ready.

**Timeline:** 8 settimane (2 mesi)

**Effort:** ~320 ore (2 developer full-time)

---

## 🎯 Fasi di Migrazione

### **PHASE 1: Infrastructure Setup** ✅ (Settimana 1-2) - IN CORSO

**Obiettivo:** Setup infrastruttura production-ready

**Tasks Completati:**
- ✅ FYL-35: Error Handling Framework (Exception hierarchy, RFC 7807)
- ✅ FYL-74: Exception Hierarchy con Error Codes
- ✅ FYL-75: Request ID Tracing
- ✅ FYL-76: Retry Logic con Exponential Backoff
- ✅ FYL-77: Circuit Breaker Pattern
- ✅ FYL-82: API Key Authentication (schema + functions)

**Tasks Rimanenti:**
- [ ] FYL-7: Database Migration (Supabase → Neon PostgreSQL)
- [ ] FYL-6: JWT Authentication (Clerk.com integration)
- [ ] FYL-33: Tenant Context & Multi-tenancy
- [ ] FYL-39: Request ID Middleware (integration)
- [ ] FYL-40: Health Check System
- [ ] FYL-36: Audit Logging System
- [ ] FYL-34: Configuration Management

**Deliverables:**
- [ ] Neon database setup con pgvector
- [ ] API Key authentication funzionante
- [ ] JWT authentication funzionante
- [ ] Tenant context middleware
- [ ] Health checks endpoints
- [ ] Audit logging system

**Estimate:** 40 ore rimanenti

---

### **PHASE 2: Core Domain Migration** (Settimana 3-4)

**Obiettivo:** Migrare domain entities, workflow engine, agent system

#### **Week 3: Domain Layer**

**Tasks:**
- [ ] FYL-47: Integrare Domain Layer da CGS_2
  - [ ] Portare `core/domain/entities/` (Agent, Workflow, Document, Content, CostEvent)
  - [ ] Portare `core/domain/value_objects/` (Provider, ModelConfig, ToolResult)
  - [ ] Adattare per Pydantic V2
  - [ ] Test entities

**Deliverables:**
- [ ] `app/domain/entities/` completo
- [ ] `app/domain/value_objects/` completo
- [ ] Test suite passed

**Estimate:** 20 ore

#### **Week 4: Infrastructure Layer**

**Tasks:**
- [ ] FYL-48: Integrare Infrastructure Layer da CGS_2
  - [ ] Portare LLM adapters (OpenAI, Anthropic, Gemini, DeepSeek)
  - [ ] Portare LLMProviderFactory
  - [ ] Adattare per asyncpg + Neon
  - [ ] Test adapters

- [ ] FYL-12: Portare Workflow Engine
  - [ ] Portare workflow registry pattern
  - [ ] Portare workflow handlers (onboarding, linkedin, blog, analytics)
  - [ ] Portare YAML workflow templates
  - [ ] Test workflow execution

- [ ] FYL-14: Portare Agent System
  - [ ] Portare agent entity
  - [ ] Portare specialist agents (copywriter, research, rag, compliance)
  - [ ] Portare agent executor
  - [ ] Test agent execution

**Deliverables:**
- [ ] `app/llm/adapters/` completo (4 providers)
- [ ] `app/workflows/` completo (registry + handlers + templates)
- [ ] `app/agents/` completo (4 specialist agents)
- [ ] Test suite passed

**Estimate:** 60 ore

---

### **PHASE 3: Tools & Prompts Migration** (Settimana 5)

**Obiettivo:** Migrare tool system e prompt builder

**Tasks:**
- [ ] FYL-13: Portare RAG Tool
  - [ ] Portare `rag_tool.py`
  - [ ] Implementare embedding generation
  - [ ] Implementare semantic search (pgvector)
  - [ ] Setup S3 storage per documenti
  - [ ] Test RAG search

- [ ] Portare Altri Tools
  - [ ] Portare `perplexity_tool.py`
  - [ ] Portare `serper_tool.py`
  - [ ] Portare `image_generation_tool.py`
  - [ ] Test tool execution

- [ ] Portare Prompt Builder
  - [ ] Portare `prompt_builder.py` (Jinja2)
  - [ ] Portare tutti i prompt templates (`core/prompts/*.md`)
  - [ ] Test prompt rendering

**Deliverables:**
- [ ] `app/tools/` completo (RAG, Perplexity, Serper, Image Gen)
- [ ] `app/prompts/` completo (builder + templates)
- [ ] S3 storage configurato
- [ ] Test suite passed

**Estimate:** 40 ore

---

### **PHASE 4: Onboarding Migration** (Settimana 6)

**Obiettivo:** Migrare sistema di onboarding completo

**Tasks:**
- [ ] Portare Onboarding Domain
  - [ ] Portare `onboarding/domain/models.py` (CompanySnapshot, OnboardingSession)
  - [ ] Portare `onboarding/domain/cgs_contracts.py`
  - [ ] Portare `onboarding/domain/content_types.py`

- [ ] Portare Onboarding Use Cases
  - [ ] Portare `create_session.py`
  - [ ] Portare `research_company.py` (Perplexity)
  - [ ] Portare `synthesize_snapshot.py` (Gemini)
  - [ ] Portare `collect_answers.py`
  - [ ] Portare `execute_onboarding.py`

- [ ] Portare Onboarding Adapters
  - [ ] Portare `perplexity_adapter.py`
  - [ ] Portare `gemini_adapter.py`
  - [ ] Portare `brevo_adapter.py`
  - [ ] Portare `cgs_adapter.py`

- [ ] Portare Payload Builder
  - [ ] Portare `payload_builder.py`
  - [ ] Test payload generation

- [ ] Adattare Repository
  - [ ] Adattare `supabase_repository.py` per asyncpg
  - [ ] Test CRUD operations

**Deliverables:**
- [ ] `app/onboarding/` completo (domain + use cases + adapters + builders)
- [ ] Repository adattato per Neon
- [ ] Test suite passed

**Estimate:** 40 ore

---

### **PHASE 5: Frontend Migration** (Settimana 7)

**Obiettivo:** Migrare frontend e integrare con nuovo backend

**Tasks:**
- [ ] Portare Frontend Components
  - [ ] Portare `components/steps/` (Wizard steps)
  - [ ] Portare `components/cards/` (CompanySnapshotCard, AnalyticsCard)
  - [ ] Portare `components/wizard/` (Wizard container)
  - [ ] Portare `components/common/`

- [ ] Portare Renderer Registry
  - [ ] Portare `renderers/RendererRegistry.ts`
  - [ ] Portare `renderers/CompanySnapshotRenderer.tsx`
  - [ ] Portare `renderers/AnalyticsRenderer.tsx`
  - [ ] Portare `renderers/ContentRenderer.tsx`

- [ ] Portare Hooks & Store
  - [ ] Portare `hooks/useOnboarding.ts`
  - [ ] Portare `store/onboardingStore.ts`

- [ ] Adattare API Client
  - [ ] Adattare `services/api/onboardingApi.ts` per nuovi endpoints
  - [ ] Adattare `services/api/client.ts` per API Key auth
  - [ ] Test API integration

- [ ] Integrare Clerk.com
  - [ ] Setup Clerk.com authentication
  - [ ] Integrare JWT in API client
  - [ ] Test authentication flow

**Deliverables:**
- [ ] Frontend completo migrato
- [ ] Renderer registry funzionante
- [ ] API client adattato
- [ ] Clerk.com integrato
- [ ] Test E2E passed

**Estimate:** 40 ore

---

### **PHASE 6: Testing & Deployment** (Settimana 8)

**Obiettivo:** Test completi e deployment production

**Tasks:**
- [ ] Integration Tests
  - [ ] Test workflow execution end-to-end
  - [ ] Test onboarding flow completo
  - [ ] Test multi-tenancy isolation
  - [ ] Test API Key authentication
  - [ ] Test JWT authentication

- [ ] Performance Testing
  - [ ] Benchmark API response times
  - [ ] Benchmark database query times
  - [ ] Benchmark workflow execution times
  - [ ] Load testing (100 concurrent users)

- [ ] Security Audit
  - [ ] Audit tenant isolation
  - [ ] Audit API Key security
  - [ ] Audit JWT security
  - [ ] Audit secrets encryption

- [ ] Documentation
  - [ ] API documentation (OpenAPI)
  - [ ] Developer guide
  - [ ] Deployment guide
  - [ ] Migration guide

- [ ] Deployment
  - [ ] Setup staging environment
  - [ ] Deploy to staging
  - [ ] Smoke tests staging
  - [ ] Setup production environment
  - [ ] Deploy to production
  - [ ] Smoke tests production

**Deliverables:**
- [ ] Test coverage > 80%
- [ ] Performance benchmarks passed
- [ ] Security audit passed
- [ ] Documentation completa
- [ ] Production deployment successful

**Estimate:** 40 ore

---

## 📊 Timeline Gantt

```
Week 1-2: Infrastructure Setup ✅ (IN CORSO)
├── FYL-7: Database Migration
├── FYL-6: JWT Authentication
├── FYL-33: Tenant Context
├── FYL-39: Request ID Middleware
├── FYL-40: Health Checks
├── FYL-36: Audit Logging
└── FYL-34: Configuration Management

Week 3: Domain Layer
├── FYL-47: Domain Entities
└── FYL-47: Value Objects

Week 4: Infrastructure Layer
├── FYL-48: LLM Adapters
├── FYL-12: Workflow Engine
└── FYL-14: Agent System

Week 5: Tools & Prompts
├── FYL-13: RAG Tool
├── Tools: Perplexity, Serper, Image Gen
└── Prompt Builder + Templates

Week 6: Onboarding
├── Onboarding Domain
├── Onboarding Use Cases
├── Onboarding Adapters
└── Repository Adaptation

Week 7: Frontend
├── Components Migration
├── Renderer Registry
├── Hooks & Store
├── API Client Adaptation
└── Clerk.com Integration

Week 8: Testing & Deployment
├── Integration Tests
├── Performance Testing
├── Security Audit
├── Documentation
└── Production Deployment
```

---

## 🎯 Priorità Critiche

### **P0 - BLOCKER (Settimana 1-2)**
1. Database Migration (FYL-7)
2. API Key Authentication (FYL-82)
3. Tenant Context (FYL-33)

### **P1 - HIGH (Settimana 3-5)**
1. Workflow Engine (FYL-12)
2. Onboarding Handler (onboarding_content_handler.py)
3. Prompt Builder (prompt_builder.py)
4. RAG Tool (FYL-13)

### **P2 - MEDIUM (Settimana 6-7)**
1. Frontend Migration
2. Renderer Registry
3. Clerk.com Integration

---

## 📈 Metriche di Successo

### **Funzionalità:**
- [ ] Tutti i workflow CGS_2 funzionanti
- [ ] Onboarding flow completo funzionante
- [ ] Frontend rendering corretto (CompanySnapshotCard, AnalyticsCard)
- [ ] Multi-tenancy isolation verificato

### **Performance:**
- [ ] API response time < 200ms (p95)
- [ ] Database query time < 50ms (p95)
- [ ] Workflow execution time < 30s (p95)

### **Security:**
- [ ] API Key authentication funzionante
- [ ] JWT authentication funzionante
- [ ] Tenant isolation verificato
- [ ] Zero data leakage

### **Quality:**
- [ ] Test coverage > 80%
- [ ] Zero critical bugs
- [ ] Documentation completa

---

## ✅ Checklist Pre-Migrazione

- [ ] Backup completo CGS_2
- [ ] Setup Fylle Core Pulse repository
- [ ] Setup Neon database account
- [ ] Setup AWS S3 bucket
- [ ] Setup staging environment
- [ ] Setup CI/CD pipeline
- [ ] Team alignment su piano

---

## 🚨 Rischi e Mitigazioni

| Rischio | Probabilità | Impatto | Mitigazione |
|---------|-------------|---------|-------------|
| Perdita funzionalità | Media | Alto | Usare DETAILED_FILE_INVENTORY.md come checklist |
| Breaking changes frontend | Media | Alto | Mantenere API contracts identici |
| Performance degradation | Bassa | Medio | Benchmark prima e dopo migrazione |
| Data loss | Bassa | Critico | Backup completo + data integrity check |
| Timeline slippage | Media | Medio | Buffer 20% su ogni fase |

---

## 📞 Prossimi Passi Immediati

1. **Completare FYL-7** (Database Migration) - PRIORITÀ MASSIMA
2. **Completare FYL-33** (Tenant Context) - BLOCKER
3. **Iniziare FYL-47** (Domain Layer Migration)
4. **Setup staging environment**
5. **Creare migration checklist dettagliata**


