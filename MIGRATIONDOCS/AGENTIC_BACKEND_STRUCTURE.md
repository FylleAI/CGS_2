# 🤖 AGENTIC BACKEND - Struttura e Responsabilità

## 📂 File Structure (Solo Tua Area)

```
fylle-core-pulse/
└── app/
    ├── workflows/                          # ✅ TUA AREA
    │   ├── entities/
    │   │   └── workflow.py                 # Workflow entity (domain)
    │   │
    │   ├── handlers/                       # 🔥 CORE - Workflow handlers
    │   │   ├── base_handler.py             # Base class per tutti i workflow
    │   │   ├── onboarding_content_handler.py  # Handler onboarding
    │   │   ├── linkedin_post_handler.py    # Handler LinkedIn
    │   │   ├── blog_article_handler.py     # Handler Blog
    │   │   └── analytics_dashboard_handler.py  # Handler Analytics
    │   │
    │   ├── templates/                      # 🔥 CORE - YAML workflow templates
    │   │   ├── onboarding_content.yaml
    │   │   ├── linkedin_post.yaml
    │   │   ├── blog_article.yaml
    │   │   └── analytics_dashboard.yaml
    │   │
    │   ├── registry.py                     # Workflow registry pattern
    │   └── orchestrator.py                 # Workflow orchestrator
    │
    ├── agents/                             # ✅ TUA AREA
    │   ├── entities/
    │   │   └── agent.py                    # Agent entity (domain)
    │   │
    │   ├── specialists/                    # 🔥 CORE - Pre-configured agents
    │   │   ├── copywriter_agent.py         # Generic copywriter
    │   │   ├── research_agent.py           # Generic research
    │   │   ├── rag_agent.py                # Generic RAG
    │   │   └── compliance_agent.py         # Generic compliance
    │   │
    │   ├── executor.py                     # 🔥 CORE - Agent executor (tenant-aware)
    │   └── registry.py                     # Agent registry
    │
    ├── tasks/                              # ✅ TUA AREA
    │   ├── entities/
    │   │   └── task.py                     # Task entity (domain)
    │   ├── executor.py                     # Task executor (usa Agent)
    │   └── result.py                       # TaskResult value object
    │
    ├── prompts/                            # ✅ TUA AREA - IP PROPRIETARIO
    │   ├── prompt_builder.py               # 🔥 CORE - Jinja2 prompt builder
    │   └── templates/                      # 🔥 CORE - Prompt templates
    │       ├── copywriter/
    │       │   ├── linkedin_post.md
    │       │   ├── blog_article.md
    │       │   └── company_snapshot.md
    │       ├── research/
    │       │   ├── company_research.md
    │       │   └── market_research.md
    │       ├── rag/
    │       │   └── semantic_search.md
    │       └── compliance/
    │           └── content_review.md
    │
    ├── tools/                              # ✅ TUA AREA
    │   ├── rag_tool.py                     # 🔥 CORE - RAG semantic search
    │   ├── perplexity_tool.py              # Perplexity research
    │   ├── serper_tool.py                  # Google search
    │   └── image_generation_tool.py        # DALL-E image generation
    │
    └── llm/                                # ✅ TUA AREA
        ├── adapters/                       # 🔥 CORE - LLM adapters
        │   ├── openai_adapter.py
        │   ├── anthropic_adapter.py
        │   ├── gemini_adapter.py
        │   └── deepseek_adapter.py
        └── factories/
            └── llm_provider_factory.py     # Factory pattern
```

---

## 🎯 RESPONSABILITÀ CHIAVE

### **1. Workflow Engine**

**Cosa fa:**
- Definisce la sequenza di task per ogni tipo di content
- Orchestrazione esecuzione task
- Validazione input/output
- Formattazione risultato finale

**Cosa NON fa:**
- ❌ NON esegue i task (lo fanno gli Agent)
- ❌ NON chiama LLM direttamente
- ❌ NON gestisce tenant context (lo fa l'infrastruttura)

**File chiave:**
- `workflows/handlers/onboarding_content_handler.py`
- `workflows/templates/onboarding_content.yaml`
- `workflows/orchestrator.py`

---

### **2. Agent System (TENANT-AWARE)**

**Cosa fa:**
- Esegue task usando LLM
- Applica system prompt (generico o tenant-specific)
- Usa tools (RAG, Perplexity, etc.)
- Gestisce personalizzazioni per tenant

**Cosa NON fa:**
- ❌ NON decide la sequenza di task (lo fa il Workflow)
- ❌ NON gestisce autenticazione (lo fa l'infrastruttura)

**File chiave:**
- `agents/executor.py` (🔥 CRITICO - tenant-aware)
- `agents/specialists/copywriter_agent.py`

---

### **3. Prompt Builder**

**Cosa fa:**
- Rendering prompt templates con Jinja2
- Injection variabili dinamiche (brand, audience, tone)
- Gestione prompt personalizzati per tenant

**Cosa NON fa:**
- ❌ NON chiama LLM (lo fa l'Agent)
- ❌ NON gestisce business logic

**File chiave:**
- `prompts/prompt_builder.py`
- `prompts/templates/*.md`

---

### **4. Tool System**

**Cosa fa:**
- RAG semantic search (pgvector)
- Web research (Perplexity, Serper)
- Image generation (DALL-E)

**Cosa NON fa:**
- ❌ NON gestisce business logic
- ❌ NON decide quando usare i tool (lo fa l'Agent)

**File chiave:**
- `tools/rag_tool.py` (🔥 CRITICO)
- `tools/perplexity_tool.py`

---

## 🔑 TENANT-AWARE AGENT SYSTEM

### **Concetto:**

Ogni agent ha **2 livelli di configurazione:**

1. **Base Configuration (Generic)** - Usato da tutti i tenant
2. **Tenant Configuration (Override)** - Personalizzato per tenant specifico

### **Database Schema (Gestito da Infrastruttura):**

```sql
-- Tabella gestita da infrastruttura
CREATE TABLE tenant_agent_configs (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    agent_id VARCHAR(50) NOT NULL,
    custom_system_prompt TEXT,
    model_config JSONB,
    tools JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(tenant_id, agent_id)
);
```

### **Agent Executor (TUA RESPONSABILITÀ):**

```python
# app/agents/executor.py

from app.core.tenant_context import get_current_tenant_id  # ← Fornito da infrastruttura
from app.core.database import DatabaseManager  # ← Fornito da infrastruttura

class AgentExecutor:
    def __init__(
        self,
        agent_registry: AgentRegistry,
        llm_factory: LLMProviderFactory,
        db_manager: DatabaseManager  # ← Injected da infrastruttura
    ):
        self.agent_registry = agent_registry
        self.llm_factory = llm_factory
        self.db_manager = db_manager
    
    async def execute_task(
        self,
        agent_id: str,
        task: Task,
        context: dict
    ) -> TaskResult:
        """
        Esegue un task con agent tenant-aware.
        
        Il tenant_id viene estratto dal context (fornito da middleware).
        """
        # 1. Estrai tenant_id dal context (fornito da middleware)
        tenant_id = context.get("tenant_id")
        if not tenant_id:
            raise ValueError("tenant_id missing in context")
        
        # 2. Carica agent base (generico)
        base_agent = self.agent_registry.get(agent_id)
        
        # 3. Carica personalizzazioni tenant (se esistono)
        tenant_config = await self._load_tenant_config(tenant_id, agent_id)
        
        # 4. Merge: tenant config OVERRIDE base config
        agent = self._merge_configs(base_agent, tenant_config)
        
        # 5. Build prompt usando PromptBuilder
        prompt = await self._build_prompt(agent, task, context)
        
        # 6. Esegui con LLM
        llm = self.llm_factory.create(agent.model_config.provider)
        result = await llm.generate(
            prompt=prompt,
            model=agent.model_config.model,
            temperature=agent.model_config.temperature,
            tools=agent.tools
        )
        
        return TaskResult(
            task_id=task.task_id,
            output=result.content,
            metadata={
                "agent_id": agent_id,
                "tenant_id": tenant_id,
                "model": agent.model_config.model,
                "tokens": result.usage.total_tokens
            }
        )
    
    async def _load_tenant_config(
        self,
        tenant_id: str,
        agent_id: str
    ) -> Optional[dict]:
        """
        Carica configurazione tenant-specific da database.
        
        Questa query viene eseguita dal DatabaseManager (fornito da infrastruttura).
        """
        query = """
            SELECT custom_system_prompt, model_config, tools
            FROM tenant_agent_configs
            WHERE tenant_id = $1 AND agent_id = $2
        """
        
        result = await self.db_manager.fetch_one(query, tenant_id, agent_id)
        
        if not result:
            return None
        
        return {
            "custom_system_prompt": result["custom_system_prompt"],
            "model_config": result["model_config"],
            "tools": result["tools"]
        }
    
    def _merge_configs(
        self,
        base_agent: Agent,
        tenant_config: Optional[dict]
    ) -> Agent:
        """
        Merge base agent config con tenant config.
        
        Tenant config OVERRIDE base config.
        """
        if not tenant_config:
            return base_agent
        
        # Clone base agent
        agent = base_agent.model_copy(deep=True)
        
        # Override con tenant config
        if tenant_config.get("custom_system_prompt"):
            agent.system_prompt = tenant_config["custom_system_prompt"]
        
        if tenant_config.get("model_config"):
            agent.model_config = ModelConfig(**tenant_config["model_config"])
        
        if tenant_config.get("tools"):
            agent.tools = tenant_config["tools"]
        
        return agent
    
    async def _build_prompt(
        self,
        agent: Agent,
        task: Task,
        context: dict
    ) -> str:
        """
        Build prompt usando PromptBuilder.
        """
        from app.prompts.prompt_builder import PromptBuilder
        
        prompt_builder = PromptBuilder()
        
        return await prompt_builder.build(
            template_name=task.prompt_template,
            variables={
                "system_prompt": agent.system_prompt,
                "task_description": task.description,
                **context  # Brand, audience, tone, etc.
            }
        )
```

---

## 🧪 TASK GENERICI vs TENANT-SPECIFIC

### **Concetto:**

- **Task Generici:** Usati per testing e workflow standard
- **Task Tenant-Specific:** Personalizzati per contenuti specifici del cliente

### **Esempio: LinkedIn Post**

#### **Task Generico (Testing/Default):**

```yaml
# workflows/templates/linkedin_post.yaml

workflow_id: "linkedin_post"
tasks:
  - task_id: "task1_research"
    agent_id: "research_specialist"
    prompt_template: "research/company_research.md"
    description: "Research company and industry trends"
    
  - task_id: "task2_write"
    agent_id: "copywriter"  # ← Agent generico
    prompt_template: "copywriter/linkedin_post.md"  # ← Prompt generico
    description: "Write engaging LinkedIn post"
    
  - task_id: "task3_review"
    agent_id: "compliance_specialist"
    prompt_template: "compliance/content_review.md"
    description: "Review content for compliance"
```

**Agent generico:**
```python
# agents/specialists/copywriter_agent.py

COPYWRITER_AGENT = Agent(
    agent_id="copywriter",
    name="Copywriter Specialist",
    system_prompt="""
    You are an expert copywriter specialized in creating engaging content.
    You follow brand voice guidelines and target audience preferences.
    """,
    model_config=ModelConfig(
        provider="openai",
        model="gpt-4-turbo",
        temperature=0.7
    ),
    tools=["rag_tool"]
)
```

#### **Task Tenant-Specific (Cliente ACME Corp):**

**Database record:**
```sql
INSERT INTO tenant_agent_configs (tenant_id, agent_id, custom_system_prompt, model_config)
VALUES (
    'acme-corp-uuid',
    'copywriter',
    'You are ACME Corp''s copywriter. ACME''s voice is: professional, data-driven, technical. Always mention ROI and metrics. Never use emojis or casual language.',
    '{"provider": "anthropic", "model": "claude-3-opus", "temperature": 0.5}'
);
```

**Quando ACME Corp esegue il workflow:**
1. Workflow usa lo stesso YAML template (generico)
2. AgentExecutor carica agent generico
3. AgentExecutor carica tenant config da database
4. AgentExecutor fa MERGE (tenant OVERRIDE base)
5. Risultato: stesso workflow, agent personalizzato!

---

## 🎯 COME RAGIONARE

### **Quando aggiungi un nuovo workflow:**

1. **Crea YAML template generico** (`workflows/templates/`)
2. **Definisci task generici** (agent_id, prompt_template)
3. **Crea handler** (`workflows/handlers/`)
4. **Registra workflow** (`@register_workflow("workflow_name")`)

### **Quando aggiungi un nuovo agent:**

1. **Crea agent generico** (`agents/specialists/`)
2. **Definisci system prompt generico**
3. **Registra agent** (`agent_registry.register()`)
4. **Per personalizzazioni:** Inserisci record in `tenant_agent_configs` (via API admin)

### **Quando aggiungi un nuovo prompt:**

1. **Crea template Jinja2** (`prompts/templates/`)
2. **Usa variabili dinamiche** (`{{ brand_name }}`, `{{ tone }}`)
3. **Testa con PromptBuilder**

### **Quando aggiungi un nuovo tool:**

1. **Crea tool class** (`tools/`)
2. **Implementa `execute()` method**
3. **Registra tool** (disponibile per agent)

---

## ✅ CHECKLIST: Agentic Backend

Quando lavori su questa area, assicurati:

- [ ] **Workflow è generico** (non hardcoded per tenant)
- [ ] **Agent è tenant-aware** (usa `AgentExecutor`)
- [ ] **Prompt è template-based** (Jinja2, non hardcoded)
- [ ] **Tool è riutilizzabile** (non business logic)
- [ ] **Context include tenant_id** (fornito da middleware)
- [ ] **Database queries usano DatabaseManager** (fornito da infrastruttura)
- [ ] **Non gestisci autenticazione** (fornita da middleware)

---

## 📦 DIPENDENZE DA INFRASTRUTTURA

**Cosa ti fornisce l'infrastruttura:**

```python
# app/core/tenant_context.py (fornito da infrastruttura)
def get_current_tenant_id() -> str:
    """Estrae tenant_id dal context (middleware)."""
    ...

# app/core/database.py (fornito da infrastruttura)
class DatabaseManager:
    async def fetch_one(self, query: str, *args) -> dict:
        """Esegue query e ritorna un record."""
        ...
    
    async def fetch_many(self, query: str, *args) -> list[dict]:
        """Esegue query e ritorna lista di record."""
        ...
    
    async def execute(self, query: str, *args) -> None:
        """Esegue query senza ritorno."""
        ...
```

**Come usi queste dipendenze:**

```python
# app/agents/executor.py

class AgentExecutor:
    def __init__(self, db_manager: DatabaseManager):  # ← Dependency injection
        self.db_manager = db_manager
    
    async def execute_task(self, agent_id: str, task: Task, context: dict):
        tenant_id = context.get("tenant_id")  # ← Fornito da middleware
        
        # Usa DatabaseManager per query
        tenant_config = await self.db_manager.fetch_one(
            "SELECT * FROM tenant_agent_configs WHERE tenant_id = $1 AND agent_id = $2",
            tenant_id,
            agent_id
        )
        ...
```

**Dependency injection setup (fatto da infrastruttura):**

```python
# app/main.py (gestito da infrastruttura)

from app.core.database import DatabaseManager
from app.agents.executor import AgentExecutor

# Setup
db_manager = DatabaseManager(config.database_url)
agent_executor = AgentExecutor(db_manager=db_manager)  # ← Injection

# Disponibile per API endpoints
app.state.agent_executor = agent_executor
```

---

**Questa è la TUA area! Ora passiamo all'Onboarding Microservice?** 🚀

