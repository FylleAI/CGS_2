# 🎯 LE TUE AREE: Riepilogo e Checklist Operativa

## 📚 Documenti Creati

Ho creato **7 documenti completi** per guidarti:

1. **AGENTIC_BACKEND_STRUCTURE.md** - Struttura e responsabilità backend agentic
2. **ONBOARDING_MICROSERVICE_STRUCTURE.md** - Struttura e responsabilità onboarding
3. **FRONTEND_ELASTIC_STRUCTURE.md** - Struttura e responsabilità frontend elastico
4. **COMPLETE_FLOW_DIAGRAM.md** - Flusso end-to-end completo
5. **MIGRATION_ANALYSIS_CGS2_TO_PULSE.md** - Analisi migrazione strategica
6. **DETAILED_FILE_INVENTORY.md** - Inventario file per file
7. **ARCHITECTURE_COMPARISON.md** - Confronto architetture

---

## 🎯 LE TUE 3 AREE DI COMPETENZA

```
┌─────────────────────────────────────────────────────────────────┐
│                    1. AGENTIC BACKEND                            │
├─────────────────────────────────────────────────────────────────┤
│  ✅ Workflow Engine (orchestrazione task)                        │
│  ✅ Agent System (esecuzione task con LLM)                       │
│  ✅ Prompt Builder (Jinja2 templates)                            │
│  ✅ Tool System (RAG, Perplexity, Serper)                        │
│  ✅ Tenant-aware configurations                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                 2. ONBOARDING MICROSERVICE                       │
├─────────────────────────────────────────────────────────────────┤
│  ✅ Research company (Perplexity)                                │
│  ✅ Synthesize snapshot (Gemini)                                 │
│  ✅ Payload Builder (CGS integration)                            │
│  ✅ CGS Adapter (HTTP client)                                    │
│  ✅ Use Cases (business logic)                                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      3. FRONTEND                                 │
├─────────────────────────────────────────────────────────────────┤
│  ✅ Wizard UI (6 steps)                                          │
│  ✅ Renderer Registry (metadata-driven)                          │
│  ✅ Content Cards (CompanySnapshot, Analytics, etc.)             │
│  ✅ API Client (HTTP client)                                     │
│  ✅ Hooks (useOnboarding)                                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔑 CONCETTI CHIAVE DA RICORDARE

### **1. Tenant-Aware Agent System**

**Concetto:** Ogni agent ha 2 livelli di configurazione:
- **Base (Generic):** Usato da tutti i tenant
- **Tenant-Specific (Override):** Personalizzato per cliente

**Implementazione:**
```python
# AgentExecutor carica:
base_agent = agent_registry.get("copywriter")  # Generic
tenant_config = db.fetch_tenant_config(tenant_id, "copywriter")  # Specific

# Merge: tenant OVERRIDE base
agent = merge_configs(base_agent, tenant_config)

# Risultato: stesso workflow, agent personalizzato!
```

**Database:**
```sql
CREATE TABLE tenant_agent_configs (
    tenant_id UUID,
    agent_id VARCHAR(50),
    custom_system_prompt TEXT,
    model_config JSONB,
    tools JSONB
);
```

---

### **2. Metadata-Driven Rendering**

**Concetto:** Backend decide COSA mostrare (display_type), Frontend decide COME mostrarlo (rendering).

**Flow:**
```
CGS Backend                    Frontend
───────────                    ────────
Generate content               Receive response
     ↓                              ↓
Add metadata:                  Extract display_type
{                                   ↓
  "display_type":              RendererRegistry.get(display_type)
    "company_snapshot"              ↓
}                              Renderer.render(data)
                                    ↓
                               CompanySnapshotCard
```

**Vantaggi:**
- ✅ Facile aggiungere nuovi content types
- ✅ Rendering consistente in tutti i frontend
- ✅ Separation of concerns (data vs rendering)

---

### **3. Renderer Registry Pattern**

**Concetto:** Pattern di design per mapping display_type → Renderer component.

**Implementazione:**
```typescript
class RendererRegistry {
  private renderers = new Map<string, Renderer>();
  
  constructor() {
    this.register('company_snapshot', new CompanySnapshotRenderer());
    this.register('analytics_dashboard', new AnalyticsRenderer());
    this.register('content', new GenericContentRenderer());  // Fallback
  }
  
  render(displayType: string, data: any): JSX.Element {
    const renderer = this.get(displayType) || this.get('content');
    return renderer.render(data);
  }
}
```

**Uso:**
```typescript
// Step6Results.tsx
const displayType = session.cgs_response?.content?.metadata?.display_type;
return RendererRegistry.render(displayType, session.cgs_response);
```

---

### **4. Onboarding come Microservice Isolato**

**Concetto:** Onboarding è un PONTE tra Frontend e CGS.

**Responsabilità:**
```
Frontend → Onboarding → CGS
           ↓
    1. Research (Perplexity)
    2. Synthesize (Gemini)
    3. Build payload
    4. Call CGS
    5. Return structured response
```

**NON fa:**
- ❌ NON esegue workflow (lo fa CGS)
- ❌ NON genera content (lo fa CGS)
- ❌ NON rendering (lo fa Frontend)

---

## ✅ CHECKLIST OPERATIVA

### **AREA 1: Agentic Backend**

#### **Workflow Engine**
- [ ] Portare workflow handlers da CGS_2
  - [ ] `onboarding_content_handler.py` (🔥 CRITICO)
  - [ ] `linkedin_post_handler.py`
  - [ ] `blog_article_handler.py`
  - [ ] `analytics_dashboard_handler.py`
- [ ] Portare YAML workflow templates
- [ ] Portare workflow registry pattern
- [ ] Portare workflow orchestrator
- [ ] Test workflow execution

#### **Agent System**
- [ ] Portare agent entity
- [ ] Portare specialist agents
  - [ ] `copywriter_agent.py`
  - [ ] `research_agent.py`
  - [ ] `rag_agent.py`
  - [ ] `compliance_agent.py`
- [ ] Implementare AgentExecutor (tenant-aware)
  - [ ] Load base agent
  - [ ] Load tenant config from database
  - [ ] Merge configs (tenant OVERRIDE base)
  - [ ] Execute with LLM
- [ ] Test agent execution (generic)
- [ ] Test agent execution (tenant-specific)

#### **Prompt Builder**
- [ ] Portare `prompt_builder.py` (Jinja2)
- [ ] Portare tutti i prompt templates (`*.md`)
- [ ] Test prompt rendering
- [ ] Test variabili dinamiche

#### **Tool System**
- [ ] Portare `rag_tool.py` (🔥 CRITICO)
- [ ] Portare `perplexity_tool.py`
- [ ] Portare `serper_tool.py`
- [ ] Portare `image_generation_tool.py`
- [ ] Test tool execution

#### **LLM Adapters**
- [ ] Portare `openai_adapter.py`
- [ ] Portare `anthropic_adapter.py`
- [ ] Portare `gemini_adapter.py`
- [ ] Portare `deepseek_adapter.py`
- [ ] Portare `llm_provider_factory.py`
- [ ] Test LLM calls

---

### **AREA 2: Onboarding Microservice**

#### **Domain Layer**
- [ ] Portare `models.py` (CompanySnapshot, OnboardingSession)
- [ ] Portare `contracts.py` (CGS integration contracts)
- [ ] Portare `content_types.py`
- [ ] Test domain models

#### **Use Cases**
- [ ] Portare `create_session.py`
- [ ] Portare `research_company.py` (Perplexity)
- [ ] Portare `synthesize_snapshot.py` (Gemini)
- [ ] Portare `collect_answers.py`
- [ ] Portare `execute_onboarding.py` (🔥 CRITICO)
- [ ] Test use cases

#### **Adapters**
- [ ] Portare `perplexity_adapter.py`
- [ ] Portare `gemini_adapter.py`
- [ ] Portare `brevo_adapter.py`
- [ ] Implementare `cgs_adapter.py` (🔥 CRITICO)
  - [ ] HTTP client
  - [ ] Tenant-ID header
  - [ ] Error handling
  - [ ] Timeout handling (5 min)
- [ ] Test adapters

#### **Payload Builder**
- [ ] Portare `payload_builder.py` (🔥 CRITICO)
- [ ] Implementare goal-specific builders
  - [ ] `_build_company_snapshot_payload()`
  - [ ] `_build_linkedin_post_payload()`
  - [ ] `_build_blog_article_payload()`
  - [ ] `_build_analytics_dashboard_payload()`
- [ ] Test payload generation

#### **API Endpoints**
- [ ] Implementare `POST /api/v1/onboarding/start`
- [ ] Implementare `POST /api/v1/onboarding/{id}/answers`
- [ ] Implementare `GET /api/v1/onboarding/{id}`
- [ ] Test API endpoints

---

### **AREA 3: Frontend**

#### **Wizard Steps**
- [ ] Portare `Step1Input.tsx`
- [ ] Portare `Step2SnapshotReview.tsx`
- [ ] Portare `Step3Questions.tsx`
- [ ] Portare `Step4Execution.tsx`
- [ ] Portare `Step6Results.tsx` (🔥 CRITICO)
- [ ] Test wizard flow

#### **Renderer Registry**
- [ ] Implementare `RendererRegistry.ts` (🔥 CRITICO)
- [ ] Implementare `CompanySnapshotRenderer.tsx`
- [ ] Implementare `AnalyticsRenderer.tsx`
- [ ] Implementare `LinkedInPostRenderer.tsx`
- [ ] Implementare `BlogArticleRenderer.tsx`
- [ ] Implementare `GenericContentRenderer.tsx` (fallback)
- [ ] Test renderer registry

#### **Content Cards**
- [ ] Portare `CompanySnapshotCard.tsx` (🔥 CRITICO)
- [ ] Portare `AnalyticsDashboardCard.tsx`
- [ ] Implementare `LinkedInPostCard.tsx`
- [ ] Implementare `BlogArticleCard.tsx`
- [ ] Implementare `GenericContentCard.tsx`
- [ ] Test cards rendering

#### **Hooks & Store**
- [ ] Portare `useOnboarding.ts` (🔥 CRITICO)
  - [ ] `startOnboarding()`
  - [ ] `submitAnswers()`
  - [ ] Fetch session details dopo submit
- [ ] Portare `onboardingStore.ts`
- [ ] Test hooks

#### **API Client**
- [ ] Implementare `onboardingApi.ts`
  - [ ] `startOnboarding()`
  - [ ] `submitAnswers()`
  - [ ] `getSessionDetails()` (🔥 CRITICO)
- [ ] Adattare `client.ts` per tenant-ID
- [ ] Test API client

---

## 🎯 PRIORITÀ DI LAVORO

### **P0 - BLOCKER (Settimana 1-2)**
1. ✅ **Infrastruttura setup** (fatto da altri)
2. **AgentExecutor tenant-aware** (🔥 CRITICO)
3. **OnboardingContentHandler** (🔥 CRITICO)
4. **CGSAdapter** (🔥 CRITICO)
5. **RendererRegistry** (🔥 CRITICO)

### **P1 - HIGH (Settimana 3-4)**
1. **Workflow handlers** (tutti)
2. **Prompt Builder** + templates
3. **RAG Tool**
4. **Payload Builder** (goal-specific)
5. **CompanySnapshotCard**

### **P2 - MEDIUM (Settimana 5-6)**
1. **Altri specialist agents**
2. **Altri tools** (Perplexity, Serper)
3. **Altri renderers** (Analytics, LinkedIn, Blog)
4. **Altri cards**
5. **Test end-to-end**

---

## 🔄 WORKFLOW TIPICO DI LAVORO

### **Quando aggiungi un nuovo workflow:**

1. **Backend (CGS):**
   - [ ] Crea YAML template (`workflows/templates/new_workflow.yaml`)
   - [ ] Crea handler (`workflows/handlers/new_workflow_handler.py`)
   - [ ] Registra workflow (`@register_workflow("new_workflow")`)
   - [ ] Test workflow execution

2. **Onboarding:**
   - [ ] Aggiungi goal enum (`OnboardingGoal.NEW_WORKFLOW`)
   - [ ] Aggiungi payload builder (`_build_new_workflow_payload()`)
   - [ ] Test payload generation

3. **Frontend:**
   - [ ] Aggiungi goal option (`GOAL_OPTIONS`)
   - [ ] Aggiungi renderer (`NewWorkflowRenderer.tsx`)
   - [ ] Aggiungi card (`NewWorkflowCard.tsx`)
   - [ ] Registra renderer (`RendererRegistry.register()`)
   - [ ] Test rendering

---

### **Quando aggiungi un nuovo agent:**

1. **Backend (CGS):**
   - [ ] Crea specialist agent (`agents/specialists/new_agent.py`)
   - [ ] Definisci system prompt generico
   - [ ] Registra agent (`agent_registry.register()`)
   - [ ] Test agent execution (generic)

2. **Per personalizzazioni tenant:**
   - [ ] Inserisci record in `tenant_agent_configs` (via API admin)
   - [ ] Test agent execution (tenant-specific)

---

### **Quando aggiungi un nuovo renderer:**

1. **Frontend:**
   - [ ] Crea card component (`components/cards/NewCard.tsx`)
   - [ ] Crea renderer (`renderers/NewRenderer.tsx`)
   - [ ] Registra renderer (`RendererRegistry.register()`)
   - [ ] Test rendering

2. **Backend (CGS):**
   - [ ] Aggiungi `display_type: "new_type"` in metadata
   - [ ] Test end-to-end

---

## 🚨 ERRORI COMUNI DA EVITARE

### **1. NON hardcodare tenant-specific logic**

❌ **SBAGLIATO:**
```python
if tenant_id == "acme-corp":
    system_prompt = "You are ACME's copywriter..."
```

✅ **CORRETTO:**
```python
tenant_config = await db.fetch_tenant_config(tenant_id, agent_id)
agent = merge_configs(base_agent, tenant_config)
```

---

### **2. NON dimenticare di passare tenant_id**

❌ **SBAGLIATO:**
```python
async def execute_workflow(workflow_id: str, input_data: dict):
    # Manca tenant_id!
```

✅ **CORRETTO:**
```python
async def execute_workflow(workflow_id: str, input_data: dict, tenant_id: str):
    # tenant_id passato ovunque
```

---

### **3. NON modificare Step6Results per ogni nuovo renderer**

❌ **SBAGLIATO:**
```typescript
if (displayType === 'company_snapshot') {
  return <CompanySnapshotCard />;
} else if (displayType === 'analytics') {
  return <AnalyticsCard />;
}
// ... 10 if/else
```

✅ **CORRETTO:**
```typescript
return RendererRegistry.render(displayType, data);
// Aggiungere nuovo renderer = registrare in RendererRegistry
```

---

### **4. NON dimenticare fallback renderer**

❌ **SBAGLIATO:**
```typescript
const renderer = this.renderers.get(displayType);
return renderer.render(data);  // Crash se displayType sconosciuto!
```

✅ **CORRETTO:**
```typescript
const renderer = this.renderers.get(displayType) || this.renderers.get('content');
return renderer.render(data);  // Fallback a GenericContentRenderer
```

---

## 📊 METRICHE DI SUCCESSO

### **Funzionalità:**
- [ ] Tutti i workflow CGS_2 funzionanti
- [ ] Onboarding flow completo funzionante
- [ ] Frontend rendering corretto (tutti i display_type)
- [ ] Tenant-specific agents funzionanti

### **Qualità:**
- [ ] Test coverage > 80%
- [ ] Zero duplicazione codice
- [ ] Separation of concerns rispettata
- [ ] Dependency Rule rispettata

### **Elasticità:**
- [ ] Aggiungere nuovo workflow < 2 ore
- [ ] Aggiungere nuovo renderer < 1 ora
- [ ] Aggiungere nuovo agent < 1 ora
- [ ] Secondo frontend funzionante con stesso RendererRegistry

---

## 🎯 NEXT STEPS IMMEDIATI

1. **Verifica CompanySnapshotCard rendering** (test in corso)
2. **Inizia migrazione AgentExecutor** (tenant-aware)
3. **Inizia migrazione OnboardingContentHandler**
4. **Implementa RendererRegistry**
5. **Test end-to-end** (frontend → onboarding → CGS → rendering)

---

**Hai tutto quello che ti serve per iniziare! Buon lavoro! 🚀**

