# 🔄 FLUSSO COMPLETO: Frontend → Onboarding → CGS → Rendering

## 📊 Diagramma di Flusso End-to-End

```
┌─────────────────────────────────────────────────────────────────┐
│                    1. FRONTEND (React)                           │
│                    User Input Phase                              │
├─────────────────────────────────────────────────────────────────┤
│  Step1Input.tsx                                                  │
│  ├── User enters:                                                │
│  │   ├── Brand name: "ACME Corp"                                │
│  │   ├── Website: "https://acme.com"                            │
│  │   ├── Goal: "Company Snapshot"                               │
│  │   └── Email: "user@acme.com"                                 │
│  │                                                               │
│  └── onClick "Start" →                                           │
│      POST /api/v1/onboarding/start                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              2. ONBOARDING MICROSERVICE                          │
│              Research & Synthesis Phase                          │
├─────────────────────────────────────────────────────────────────┤
│  CreateSessionUseCase                                            │
│  ├── Crea sessione in database                                  │
│  └── session_id: "uuid-123"                                     │
│                                                                  │
│  ResearchCompanyUseCase                                          │
│  ├── Call Perplexity API                                        │
│  ├── Query: "Research ACME Corp (https://acme.com)..."          │
│  └── Returns: raw research data                                 │
│                                                                  │
│  SynthesizeSnapshotUseCase                                       │
│  ├── Call Gemini API                                            │
│  ├── Prompt: "Extract structured snapshot from research..."     │
│  └── Returns: CompanySnapshot {                                 │
│      company: { name, website, industry, description },         │
│      voice_tone: { tone, style, language_complexity },          │
│      target_audience: { demographics, pain_points, goals },     │
│      positioning: { uvp, differentiators },                     │
│      recent_news: [...]                                         │
│  }                                                               │
│                                                                  │
│  Response to Frontend:                                           │
│  {                                                               │
│    "session_id": "uuid-123",                                    │
│    "company_snapshot": { ... }                                  │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    3. FRONTEND (React)                           │
│                    Snapshot Review Phase                         │
├─────────────────────────────────────────────────────────────────┤
│  Step2SnapshotReview.tsx                                         │
│  ├── Display CompanySnapshot                                     │
│  ├── User reviews and confirms                                  │
│  └── onClick "Continue" → Step3Questions.tsx                    │
│                                                                  │
│  Step3Questions.tsx                                              │
│  ├── Display goal-specific questions                            │
│  ├── User answers:                                              │
│  │   ├── "What's your main message?" → "AI automation"         │
│  │   ├── "Target audience?" → "Tech leaders"                   │
│  │   └── "Additional context?" → "Focus on ROI"                │
│  │                                                               │
│  └── onClick "Submit" →                                          │
│      POST /api/v1/onboarding/{session_id}/answers               │
│      {                                                           │
│        "answers": {                                             │
│          "main_message": "AI automation",                       │
│          "target_audience": "Tech leaders",                     │
│          "additional_context": "Focus on ROI"                   │
│        }                                                         │
│      }                                                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              4. ONBOARDING MICROSERVICE                          │
│              Execution Phase                                     │
├─────────────────────────────────────────────────────────────────┤
│  CollectAnswersUseCase                                           │
│  ├── Salva answers in database                                  │
│  └── session.state = "ANSWERS_COLLECTED"                        │
│                                                                  │
│  ExecuteOnboardingUseCase                                        │
│  ├── PayloadBuilder.build()                                     │
│  │   ├── Merge snapshot + answers                              │
│  │   └── Returns CGS payload: {                                │
│  │       "brand": {                                             │
│  │         "name": "ACME Corp",                                 │
│  │         "website": "https://acme.com",                       │
│  │         "industry": "Technology",                            │
│  │         "description": "..."                                 │
│  │       },                                                     │
│  │       "voice_tone": {                                        │
│  │         "tone": "professional",                              │
│  │         "style": "data-driven",                              │
│  │         "language_complexity": "technical"                   │
│  │       },                                                     │
│  │       "target_audience": {                                   │
│  │         "demographics": "Tech leaders",                      │
│  │         "pain_points": [...],                                │
│  │         "goals": [...]                                       │
│  │       },                                                     │
│  │       "goal": "company_snapshot",                            │
│  │       "additional_context": "Focus on ROI"                   │
│  │   }                                                          │
│  │                                                               │
│  └── CGSAdapter.execute_workflow()                              │
│      POST http://cgs-backend/api/v1/workflows/execute           │
│      Headers: { "X-Tenant-ID": "acme-corp-uuid" }               │
│      Body: {                                                     │
│        "workflow_id": "onboarding_content",                     │
│        "input_data": { ... }  ← CGS payload                     │
│      }                                                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    5. CGS BACKEND                                │
│                    Workflow Execution Phase                      │
├─────────────────────────────────────────────────────────────────┤
│  WorkflowOrchestrator.execute("onboarding_content")             │
│  ├── Load workflow template (YAML)                              │
│  ├── Extract tenant_id from headers                             │
│  └── Call OnboardingContentHandler.execute()                    │
│                                                                  │
│  OnboardingContentHandler.execute()                             │
│  ├── Task 1: Research                                           │
│  │   ├── agent_id: "research_specialist"                       │
│  │   ├── prompt_template: "research/company_research.md"       │
│  │   └── AgentExecutor.execute_task() →                        │
│  │       ├── Load base agent (generic)                         │
│  │       ├── Load tenant config (if exists)                    │
│  │       ├── Merge configs (tenant OVERRIDE base)              │
│  │       ├── PromptBuilder.build(template, variables)          │
│  │       ├── LLM call (OpenAI/Anthropic/Gemini)                │
│  │       └── Returns: TaskResult                               │
│  │                                                               │
│  ├── Task 2: Synthesis                                          │
│  │   ├── agent_id: "copywriter"                                │
│  │   ├── prompt_template: "copywriter/company_snapshot.md"     │
│  │   └── AgentExecutor.execute_task() →                        │
│  │       ├── Load base copywriter agent                        │
│  │       ├── Load ACME Corp tenant config:                     │
│  │       │   {                                                  │
│  │       │     "custom_system_prompt": "You are ACME's...",    │
│  │       │     "model_config": {                               │
│  │       │       "provider": "anthropic",                      │
│  │       │       "model": "claude-3-opus"                      │
│  │       │     }                                                │
│  │       │   }                                                  │
│  │       ├── Merge: tenant OVERRIDE base                       │
│  │       ├── PromptBuilder.build() with ACME's prompt          │
│  │       ├── LLM call (Claude 3 Opus)                          │
│  │       └── Returns: TaskResult                               │
│  │                                                               │
│  ├── Task 3: Compliance Review                                  │
│  │   ├── agent_id: "compliance_specialist"                     │
│  │   └── AgentExecutor.execute_task() → ...                    │
│  │                                                               │
│  └── Format Output:                                             │
│      {                                                           │
│        "version": "1.0",                                        │
│        "session_id": "cgs-run-uuid",                            │
│        "workflow": "onboarding_content",                        │
│        "status": "completed",                                   │
│        "content": {                                             │
│          "content_id": "content-uuid",                          │
│          "title": "Company Snapshot: ACME Corp",                │
│          "body": "...",                                         │
│          "format": "markdown",                                  │
│          "word_count": 1500,                                    │
│          "metadata": {                                          │
│            "display_type": "company_snapshot",  ← CHIAVE!       │
│            "company_snapshot": {                                │
│              "company": { ... },                                │
│              "voice_tone": { ... },                             │
│              "target_audience": { ... },                        │
│              "positioning": { ... },                            │
│              "recent_news": [ ... ]                             │
│            }                                                     │
│          }                                                       │
│        }                                                         │
│      }                                                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              6. ONBOARDING MICROSERVICE                          │
│              Response Handling Phase                             │
├─────────────────────────────────────────────────────────────────┤
│  ExecuteOnboardingUseCase (continued)                            │
│  ├── Receive CGS response                                       │
│  ├── Update session:                                            │
│  │   ├── session.cgs_run_id = "cgs-run-uuid"                   │
│  │   ├── session.cgs_response = { ... }  ← Full response       │
│  │   └── session.state = "COMPLETED"                           │
│  │                                                               │
│  └── Return to Frontend:                                        │
│      {                                                           │
│        "session_id": "uuid-123",                                │
│        "cgs_run_id": "cgs-run-uuid",                            │
│        "content_title": "Company Snapshot: ACME Corp",          │
│        "content_preview": "...",                                │
│        "word_count": 1500,                                      │
│        "display_type": "company_snapshot"                       │
│      }                                                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    7. FRONTEND (React)                           │
│                    Fetch Full Details Phase                      │
├─────────────────────────────────────────────────────────────────┤
│  useOnboarding.submitAnswers() (continued)                       │
│  ├── Receive summary response                                   │
│  │                                                               │
│  └── Fetch full session details:                                │
│      GET /api/v1/onboarding/{session_id}                        │
│      Returns: {                                                  │
│        "session_id": "uuid-123",                                │
│        "state": "COMPLETED",                                    │
│        "company_snapshot": { ... },                             │
│        "cgs_response": {  ← FULL CGS RESPONSE                   │
│          "content": {                                            │
│            "metadata": {                                         │
│              "display_type": "company_snapshot",                │
│              "company_snapshot": { ... }                        │
│            }                                                     │
│          }                                                       │
│        },                                                        │
│        "created_at": "...",                                     │
│        "updated_at": "..."                                      │
│      }                                                           │
│                                                                  │
│  Update session state:                                           │
│  setSession({                                                    │
│    ...session,                                                   │
│    cgs_response: sessionDetails.cgs_response  ← CHIAVE!         │
│  })                                                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    8. FRONTEND (React)                           │
│                    Rendering Phase                               │
├─────────────────────────────────────────────────────────────────┤
│  Step6Results.tsx                                                │
│  ├── Extract display_type:                                      │
│  │   const displayType =                                        │
│  │     session.cgs_response?.content?.metadata?.display_type    │
│  │     || 'content';                                            │
│  │   // displayType = "company_snapshot"                       │
│  │                                                               │
│  ├── Console logs:                                              │
│  │   🎨 Rendering with display_type: company_snapshot           │
│  │   📦 CGS Response: { ... }                                   │
│  │   📦 Content metadata: { display_type: "company_snapshot" } │
│  │                                                               │
│  └── Render using RendererRegistry:                             │
│      RendererRegistry.render(displayType, session.cgs_response) │
│      ↓                                                           │
│      RendererRegistry.get("company_snapshot")                   │
│      ↓                                                           │
│      CompanySnapshotRenderer.render(data)                       │
│      ↓                                                           │
│      <CompanySnapshotCard snapshot={...} />                     │
│      ├── Company Info section                                   │
│      ├── Voice & Tone section                                   │
│      ├── Target Audience section                                │
│      ├── Positioning section                                    │
│      └── Recent News section                                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 PUNTI CHIAVE DEL FLUSSO

### **1. Separazione Responsabilità**

| Componente | Responsabilità |
|------------|----------------|
| **Frontend** | UI, Form validation, Rendering (metadata-driven) |
| **Onboarding** | Research, Synthesis, Payload building, CGS orchestration |
| **CGS** | Workflow execution, Agent orchestration, Content generation |

### **2. Tenant-Awareness**

```
Frontend → Onboarding → CGS
           ↓            ↓
      tenant_id    tenant_id
      (middleware) (header)
                      ↓
                  AgentExecutor
                      ↓
                  Load tenant config
                      ↓
                  Merge with base agent
                      ↓
                  Personalized content
```

### **3. Metadata-Driven Rendering**

```
CGS generates:                Frontend renders:
display_type: "company_snapshot" → CompanySnapshotCard
display_type: "analytics_dashboard" → AnalyticsDashboardCard
display_type: "linkedin_post" → LinkedInPostCard
display_type: "unknown" → GenericContentCard (fallback)
```

---

## 🔄 FLUSSO ALTERNATIVO: Secondo Frontend

```
┌─────────────────────────────────────────────────────────────────┐
│              CONTENT VIEWER FRONTEND (Secondo Frontend)          │
├─────────────────────────────────────────────────────────────────┤
│  User opens: /content/{content_id}                              │
│  ↓                                                               │
│  ContentViewer.tsx                                               │
│  ├── Fetch content:                                             │
│  │   GET /api/v1/content/{content_id}                           │
│  │   Returns: {                                                  │
│  │     "content_id": "...",                                     │
│  │     "title": "...",                                          │
│  │     "body": "...",                                           │
│  │     "metadata": {                                            │
│  │       "display_type": "company_snapshot",                   │
│  │       "company_snapshot": { ... }                           │
│  │     }                                                         │
│  │   }                                                           │
│  │                                                               │
│  ├── Extract display_type:                                      │
│  │   const displayType = content.metadata?.display_type         │
│  │                                                               │
│  └── Render using SAME RendererRegistry:                        │
│      RendererRegistry.render(displayType, content)              │
│      ↓                                                           │
│      CompanySnapshotRenderer.render(content)                    │
│      ↓                                                           │
│      <CompanySnapshotCard snapshot={...} />                     │
└─────────────────────────────────────────────────────────────────┘
```

**Vantaggi:**
- ✅ **Riusa renderer:** Stesso RendererRegistry
- ✅ **Riusa cards:** Stesso CompanySnapshotCard
- ✅ **Consistente:** Stesso look & feel
- ✅ **Elastico:** Qualsiasi content type funziona

---

## 📊 SUMMARY: Aree di Tua Competenza

### **✅ TUA RESPONSABILITÀ:**

1. **Agentic Backend (CGS)**
   - Workflow Engine (handlers + templates)
   - Agent System (executor + specialists)
   - Prompt Builder (Jinja2 templates)
   - Tool System (RAG, Perplexity, Serper)
   - Tenant-aware agent configuration

2. **Onboarding Microservice**
   - Research (Perplexity)
   - Synthesis (Gemini)
   - Payload Builder (CGS integration)
   - CGS Adapter (HTTP client)
   - Use Cases (business logic)

3. **Frontend (Onboarding + Content Viewer)**
   - Wizard UI (6 steps)
   - Renderer Registry (metadata-driven)
   - Content Cards (CompanySnapshot, Analytics, etc.)
   - API Client (HTTP client)
   - Hooks (useOnboarding)

### **❌ NON TUA RESPONSABILITÀ (Infrastruttura):**

- Database setup (Neon PostgreSQL)
- Authentication (API Key + JWT)
- Multi-tenancy middleware
- Health checks, Monitoring, Logging
- Deployment, CI/CD

---

## 🎯 NEXT STEPS

1. **Verifica CompanySnapshotCard rendering** (test in corso)
2. **Inizia migrazione Agentic Backend** (workflow + agents)
3. **Inizia migrazione Onboarding** (use cases + adapters)
4. **Setup Renderer Registry** (pattern di design)
5. **Test end-to-end** (frontend → onboarding → CGS → rendering)

---

**Hai una visione completa ora! Vuoi che approfondiamo qualche area specifica?** 🚀

