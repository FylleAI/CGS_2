# 🤖 AGENTIC AI CORE - Documentazione Tecnica Completa

> **Versione:** 1.0  
> **Data:** 2025-01-22  
> **Audience:** Development Team  
> **Obiettivo:** Documentazione completa del core Agentic AI di Fylle - il nostro differenziante

---

## 📋 INDICE

1. [Panoramica Architetturale](#panoramica-architetturale)
2. [Workflow Engine](#workflow-engine)
3. [Agent System](#agent-system)
4. [Prompt Builder](#prompt-builder)
5. [Tool System](#tool-system)
6. [Tenant-Aware Architecture](#tenant-aware-architecture)
7. [Database Schema](#database-schema)
8. [Execution Flow](#execution-flow)
9. [File Rilevanti](#file-rilevanti)
10. [Best Practices](#best-practices)

---

## 1. PANORAMICA ARCHITETTURALE

### 1.1 Componenti Principali

```
┌─────────────────────────────────────────────────────────────────┐
│                    AGENTIC AI CORE                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐      ┌──────────────────┐                │
│  │ WORKFLOW ENGINE  │──────│  AGENT SYSTEM    │                │
│  │                  │      │                  │                │
│  │ • Orchestration  │      │ • Execution      │                │
│  │ • YAML Templates │      │ • Specialists    │                │
│  │ • Task Sequence  │      │ • LLM Calls      │                │
│  └──────────────────┘      └──────────────────┘                │
│           │                         │                            │
│           │                         │                            │
│           ▼                         ▼                            │
│  ┌──────────────────┐      ┌──────────────────┐                │
│  │ PROMPT BUILDER   │      │   TOOL SYSTEM    │                │
│  │                  │      │                  │                │
│  │ • Jinja2 Engine  │      │ • RAG            │                │
│  │ • Templates      │      │ • Perplexity     │                │
│  │ • Variables      │      │ • Serper         │                │
│  └──────────────────┘      └──────────────────┘                │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           TENANT-AWARE CONFIGURATION LAYER               │  │
│  │                                                           │  │
│  │  Base Config (Generic) + Tenant Config (Override)        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Principi Fondamentali

#### **A. Separation of Concerns**

| Componente | Responsabilità | NON Responsabile |
|------------|----------------|------------------|
| **Workflow Engine** | Orchestrare task sequence | Eseguire task (lo fa Agent) |
| **Agent System** | Eseguire task con LLM | Decidere task sequence (lo fa Workflow) |
| **Prompt Builder** | Generare prompt da template | Chiamare LLM (lo fa Agent) |
| **Tool System** | Fornire capabilities (RAG, search) | Decidere quando usarli (lo fa Agent) |

#### **B. Tenant-Aware by Design**

**OGNI componente DEVE essere tenant-aware:**

```python
# ✅ CORRETTO
async def execute_workflow(
    workflow_id: str,
    input_data: dict,
    tenant_id: str  # ← SEMPRE presente
) -> WorkflowResult:
    ...

# ❌ SBAGLIATO
async def execute_workflow(
    workflow_id: str,
    input_data: dict
) -> WorkflowResult:
    # Manca tenant_id!
    ...
```

#### **C. Generic + Tenant-Specific Pattern**

**Concetto chiave:** Ogni risorsa (workflow, agent, prompt) ha 2 livelli:

1. **Base (Generic):** Configurazione di default, usata da tutti i tenant
2. **Tenant-Specific (Override):** Configurazione personalizzata per un tenant specifico

**Merge logic:**
```python
final_config = merge(base_config, tenant_config)
# tenant_config OVERRIDE base_config
```

---

## 2. WORKFLOW ENGINE

### 2.1 Cos'è un Workflow?

Un **workflow** è una **sequenza di task** che producono un output specifico.

**Esempio:** Workflow "LinkedIn Post"
```
Task 1: Research company → Task 2: Generate post → Task 3: Compliance review → Output: LinkedIn post
```

### 2.2 Struttura YAML Workflow

#### **Template YAML (Generic)**

```yaml
# workflows/templates/linkedin_post.yaml

workflow_id: "linkedin_post"
name: "LinkedIn Post Generator"
description: "Generates a professional LinkedIn post based on company context"
version: "1.0"

# Input schema (cosa serve per eseguire il workflow)
input_schema:
  required:
    - brand_name
    - brand_description
    - target_audience
    - main_message
  optional:
    - tone
    - hashtags_count
    - cta

# Task sequence (eseguiti in ordine)
tasks:
  - task_id: "research"
    name: "Research Company Context"
    agent_id: "research_specialist"
    prompt_template: "research/company_context.md"
    input_mapping:
      company_name: "{{ brand_name }}"
      company_description: "{{ brand_description }}"
    tools:
      - "rag_tool"
      - "perplexity_tool"
    output_key: "research_data"
    
  - task_id: "generate_post"
    name: "Generate LinkedIn Post"
    agent_id: "copywriter"
    prompt_template: "copywriter/linkedin_post.md"
    input_mapping:
      company_name: "{{ brand_name }}"
      research_data: "{{ tasks.research.output }}"
      target_audience: "{{ target_audience }}"
      main_message: "{{ main_message }}"
      tone: "{{ tone | default('professional') }}"
    tools:
      - "rag_tool"
    output_key: "post_content"
    
  - task_id: "compliance_review"
    name: "Compliance Review"
    agent_id: "compliance_specialist"
    prompt_template: "compliance/review.md"
    input_mapping:
      content: "{{ tasks.generate_post.output }}"
      brand_name: "{{ brand_name }}"
    output_key: "compliance_result"

# Output format (come strutturare il risultato finale)
output_format:
  content_type: "linkedin_post"
  display_type: "linkedin_post"
  metadata:
    - "hashtags"
    - "cta"
    - "word_count"
    - "compliance_status"
```

### 2.3 Workflow Handler (Python)

#### **Base Handler Class**

```python
# app/workflows/handlers/base_handler.py

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from app.workflows.entities.workflow import Workflow, WorkflowResult, Task
from app.agents.executor import AgentExecutor
from app.infrastructure.prompt_builder import PromptBuilder

class BaseWorkflowHandler(ABC):
    """
    Base class per tutti i workflow handler.
    
    Responsabilità:
    - Orchestrare esecuzione task sequence
    - Gestire context tra task
    - Formattare output finale
    """
    
    def __init__(
        self,
        agent_executor: AgentExecutor,
        prompt_builder: PromptBuilder
    ):
        self.agent_executor = agent_executor
        self.prompt_builder = prompt_builder
    
    async def execute(
        self,
        workflow: Workflow,
        input_data: Dict[str, Any],
        tenant_id: str
    ) -> WorkflowResult:
        """
        Esegue il workflow.
        
        Args:
            workflow: Workflow entity (caricato da YAML)
            input_data: Input data fornito dall'utente
            tenant_id: Tenant ID (per tenant-aware execution)
        
        Returns:
            WorkflowResult con output finale
        """
        # 1. Validate input
        self._validate_input(workflow, input_data)
        
        # 2. Initialize context
        context = {
            "tenant_id": tenant_id,
            "input": input_data,
            "tasks": {}  # Store task outputs
        }
        
        # 3. Execute tasks in sequence
        for task in workflow.tasks:
            task_result = await self._execute_task(
                task=task,
                context=context,
                tenant_id=tenant_id
            )
            
            # Store task output in context
            context["tasks"][task.task_id] = {
                "output": task_result.output,
                "metadata": task_result.metadata
            }
        
        # 4. Format final output
        final_output = await self._format_output(
            workflow=workflow,
            context=context
        )
        
        return WorkflowResult(
            workflow_id=workflow.workflow_id,
            status="completed",
            output=final_output,
            metadata={
                "tenant_id": tenant_id,
                "tasks_executed": len(workflow.tasks)
            }
        )
    
    async def _execute_task(
        self,
        task: Task,
        context: Dict[str, Any],
        tenant_id: str
    ) -> Any:
        """
        Esegue un singolo task.
        
        Delega esecuzione all'AgentExecutor.
        """
        # 1. Resolve input variables usando Jinja2
        task_input = self._resolve_input_mapping(
            task.input_mapping,
            context
        )
        
        # 2. Esegui task con AgentExecutor
        task_result = await self.agent_executor.execute_task(
            agent_id=task.agent_id,
            task=task,
            context={
                **context,
                "task_input": task_input
            }
        )
        
        return task_result
    
    def _resolve_input_mapping(
        self,
        input_mapping: Dict[str, str],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Risolve variabili Jinja2 in input_mapping.
        
        Esempio:
            input_mapping = {
                "company_name": "{{ brand_name }}",
                "research_data": "{{ tasks.research.output }}"
            }
            
            context = {
                "input": {"brand_name": "ACME Corp"},
                "tasks": {"research": {"output": "..."}}
            }
            
            Returns:
            {
                "company_name": "ACME Corp",
                "research_data": "..."
            }
        """
        resolved = {}
        for key, template_str in input_mapping.items():
            resolved[key] = self.prompt_builder.render_string(
                template_str,
                context
            )
        return resolved
    
    @abstractmethod
    async def _format_output(
        self,
        workflow: Workflow,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Formatta output finale del workflow.
        
        Implementato da ogni workflow handler specifico.
        """
        pass
    
    def _validate_input(
        self,
        workflow: Workflow,
        input_data: Dict[str, Any]
    ):
        """Valida che input_data contenga tutti i campi required."""
        required_fields = workflow.input_schema.get("required", [])
        missing = [f for f in required_fields if f not in input_data]
        
        if missing:
            raise ValueError(
                f"Missing required fields: {', '.join(missing)}"
            )
```

#### **Specific Handler Example**

```python
# app/workflows/handlers/linkedin_post_handler.py

from app.workflows.handlers.base_handler import BaseWorkflowHandler

class LinkedInPostHandler(BaseWorkflowHandler):
    """
    Handler specifico per workflow LinkedIn Post.
    """
    
    async def _format_output(
        self,
        workflow: Workflow,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Formatta output per LinkedIn Post.
        
        Estrae:
        - Post content (da task generate_post)
        - Compliance status (da task compliance_review)
        - Metadata (hashtags, cta, word_count)
        """
        # Estrai output dai task
        post_content = context["tasks"]["generate_post"]["output"]
        compliance_result = context["tasks"]["compliance_review"]["output"]
        
        # Parse post content (assumiamo sia JSON)
        import json
        post_data = json.loads(post_content)
        
        # Formatta output finale
        return {
            "content_id": str(uuid.uuid4()),
            "title": f"LinkedIn Post: {context['input']['brand_name']}",
            "body": post_data["post_text"],
            "format": "markdown",
            "word_count": len(post_data["post_text"].split()),
            "metadata": {
                "display_type": "linkedin_post",
                "hashtags": post_data.get("hashtags", []),
                "cta": post_data.get("cta"),
                "compliance_status": compliance_result.get("status"),
                "compliance_notes": compliance_result.get("notes", [])
            }
        }
```

### 2.4 Workflow Registry Pattern

```python
# app/workflows/registry.py

from typing import Dict, Type
from app.workflows.handlers.base_handler import BaseWorkflowHandler

class WorkflowRegistry:
    """
    Registry pattern per workflow handlers.
    
    Permette di registrare e recuperare handler per workflow_id.
    """
    
    def __init__(self):
        self._handlers: Dict[str, Type[BaseWorkflowHandler]] = {}
    
    def register(
        self,
        workflow_id: str,
        handler_class: Type[BaseWorkflowHandler]
    ):
        """Registra un handler per un workflow_id."""
        self._handlers[workflow_id] = handler_class
    
    def get(self, workflow_id: str) -> Type[BaseWorkflowHandler]:
        """Recupera handler per workflow_id."""
        if workflow_id not in self._handlers:
            raise ValueError(f"No handler registered for workflow: {workflow_id}")
        return self._handlers[workflow_id]
    
    def list_workflows(self) -> List[str]:
        """Lista tutti i workflow_id registrati."""
        return list(self._handlers.keys())

# Global registry instance
workflow_registry = WorkflowRegistry()

# Decorator per registrazione
def register_workflow(workflow_id: str):
    """Decorator per registrare workflow handler."""
    def decorator(handler_class: Type[BaseWorkflowHandler]):
        workflow_registry.register(workflow_id, handler_class)
        return handler_class
    return decorator
```

**Uso:**

```python
# app/workflows/handlers/linkedin_post_handler.py

from app.workflows.registry import register_workflow

@register_workflow("linkedin_post")
class LinkedInPostHandler(BaseWorkflowHandler):
    ...
```

### 2.5 Workflow Orchestrator

```python
# app/workflows/orchestrator.py

from app.workflows.registry import workflow_registry
from app.workflows.loaders.yaml_loader import YAMLWorkflowLoader
from app.agents.executor import AgentExecutor
from app.infrastructure.prompt_builder import PromptBuilder

class WorkflowOrchestrator:
    """
    Orchestratore principale per esecuzione workflow.
    
    Responsabilità:
    - Caricare workflow YAML
    - Istanziare handler appropriato
    - Eseguire workflow
    - Gestire errori
    """
    
    def __init__(
        self,
        yaml_loader: YAMLWorkflowLoader,
        agent_executor: AgentExecutor,
        prompt_builder: PromptBuilder
    ):
        self.yaml_loader = yaml_loader
        self.agent_executor = agent_executor
        self.prompt_builder = prompt_builder
    
    async def execute(
        self,
        workflow_id: str,
        input_data: Dict[str, Any],
        tenant_id: str
    ) -> WorkflowResult:
        """
        Esegue un workflow.
        
        Args:
            workflow_id: ID del workflow da eseguire
            input_data: Input data fornito dall'utente
            tenant_id: Tenant ID
        
        Returns:
            WorkflowResult con output finale
        """
        # 1. Carica workflow YAML (generic)
        workflow = await self.yaml_loader.load(workflow_id)
        
        # 2. Carica tenant-specific workflow overrides (se esistono)
        workflow = await self._apply_tenant_overrides(
            workflow,
            tenant_id
        )
        
        # 3. Ottieni handler per questo workflow
        handler_class = workflow_registry.get(workflow_id)
        handler = handler_class(
            agent_executor=self.agent_executor,
            prompt_builder=self.prompt_builder
        )
        
        # 4. Esegui workflow
        result = await handler.execute(
            workflow=workflow,
            input_data=input_data,
            tenant_id=tenant_id
        )
        
        return result
    
    async def _apply_tenant_overrides(
        self,
        workflow: Workflow,
        tenant_id: str
    ) -> Workflow:
        """
        Applica override tenant-specific al workflow.
        
        Esempio override:
        - Modificare task sequence
        - Aggiungere task custom
        - Modificare prompt_template per un task
        """
        # Query database per tenant workflow overrides
        overrides = await self._fetch_tenant_workflow_overrides(
            workflow.workflow_id,
            tenant_id
        )
        
        if not overrides:
            return workflow  # No overrides, usa generic
        
        # Merge overrides (tenant OVERRIDE generic)
        return self._merge_workflow_configs(workflow, overrides)
    
    async def _fetch_tenant_workflow_overrides(
        self,
        workflow_id: str,
        tenant_id: str
    ) -> Optional[Dict]:
        """Fetch tenant workflow overrides from database."""
        # TODO: Implement database query
        pass
    
    def _merge_workflow_configs(
        self,
        base: Workflow,
        overrides: Dict
    ) -> Workflow:
        """Merge tenant overrides into base workflow."""
        # TODO: Implement merge logic
        pass
```

---

## 3. AGENT SYSTEM

### 3.1 Cos'è un Agent?

Un **agent** è uno **specialist** che esegue un task specifico usando un LLM.

**Caratteristiche:**
- Ha un **system prompt** (definisce personalità e capabilities)
- Ha un **goal** (obiettivo del task)
- Ha un **backstory** (contesto e expertise)
- Può usare **tools** (RAG, Perplexity, Serper)
- È **tenant-aware** (configurazione personalizzabile per tenant)

### 3.2 Agent Entity

```python
# app/agents/entities/agent.py

from dataclasses import dataclass
from typing import List, Optional, Dict, Any

@dataclass
class ModelConfig:
    """Configurazione LLM per agent."""
    provider: str  # "openai", "anthropic", "gemini", "deepseek"
    model: str  # "gpt-4", "claude-3-opus", "gemini-pro"
    temperature: float = 0.7
    max_tokens: int = 2000
    top_p: float = 1.0

@dataclass
class Agent:
    """
    Agent entity.
    
    Rappresenta uno specialist agent (copywriter, research, RAG, compliance).
    """
    agent_id: str
    name: str
    description: str
    system_prompt: str
    goal: str
    backstory: str
    model_config: ModelConfig
    tools: List[str]  # List of tool_id
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
```

### 3.3 Specialist Agents (Generic)

#### **Copywriter Agent**

```python
# app/agents/specialists/copywriter_agent.py

from app.agents.entities.agent import Agent, ModelConfig

COPYWRITER_AGENT = Agent(
    agent_id="copywriter",
    name="Copywriter Specialist",
    description="Expert in creating engaging, persuasive content",
    
    system_prompt="""You are an expert copywriter with 10+ years of experience.

Your expertise includes:
- Crafting compelling narratives
- Understanding target audience psychology
- Writing in various tones and styles
- SEO optimization
- Brand voice consistency

You always:
- Focus on clarity and impact
- Use data-driven insights
- Adapt to brand voice
- Follow best practices for the content type
""",
    
    goal="Create high-quality, engaging content that resonates with the target audience",
    
    backstory="""You've worked with Fortune 500 companies and startups alike,
crafting content that drives engagement and conversions. You understand the nuances
of different platforms (LinkedIn, blogs, emails) and adapt your writing accordingly.""",
    
    model_config=ModelConfig(
        provider="anthropic",
        model="claude-3-sonnet",
        temperature=0.7,
        max_tokens=2000
    ),
    
    tools=["rag_tool"],  # Can access RAG for brand context
    
    metadata={
        "category": "content_creation",
        "version": "1.0"
    }
)
```

#### **Research Specialist Agent**

```python
# app/agents/specialists/research_agent.py

RESEARCH_AGENT = Agent(
    agent_id="research_specialist",
    name="Research Specialist",
    description="Expert in gathering and analyzing information",
    
    system_prompt="""You are a research specialist with expertise in:
- Web research and fact-checking
- Competitive analysis
- Industry trends analysis
- Data synthesis

You always:
- Verify information from multiple sources
- Provide structured, actionable insights
- Cite sources when relevant
- Focus on recent, relevant data
""",
    
    goal="Gather comprehensive, accurate information to support content creation",
    
    backstory="""You've conducted research for major consulting firms and media
organizations. You excel at finding relevant information quickly and synthesizing
it into clear, actionable insights.""",
    
    model_config=ModelConfig(
        provider="openai",
        model="gpt-4-turbo",
        temperature=0.3,  # Lower temperature for factual research
        max_tokens=3000
    ),
    
    tools=["rag_tool", "perplexity_tool", "serper_tool"],
    
    metadata={
        "category": "research",
        "version": "1.0"
    }
)
```

#### **RAG Specialist Agent**

```python
# app/agents/specialists/rag_agent.py

RAG_AGENT = Agent(
    agent_id="rag_specialist",
    name="RAG Specialist",
    description="Expert in retrieving and using company knowledge",
    
    system_prompt="""You are a RAG (Retrieval-Augmented Generation) specialist.

Your role:
- Retrieve relevant information from company knowledge base
- Synthesize retrieved documents into coherent insights
- Ensure accuracy and relevance
- Provide context-aware responses

You always:
- Use semantic search to find relevant documents
- Cite which documents you're using
- Highlight gaps in knowledge base
- Provide confidence scores
""",
    
    goal="Retrieve and synthesize company knowledge to support content creation",
    
    backstory="""You specialize in knowledge management and information retrieval.
You understand how to query vector databases effectively and synthesize information
from multiple sources.""",
    
    model_config=ModelConfig(
        provider="openai",
        model="gpt-4-turbo",
        temperature=0.2,
        max_tokens=2000
    ),
    
    tools=["rag_tool"],
    
    metadata={
        "category": "knowledge_retrieval",
        "version": "1.0"
    }
)
```

#### **Compliance Specialist Agent**

```python
# app/agents/specialists/compliance_agent.py

COMPLIANCE_AGENT = Agent(
    agent_id="compliance_specialist",
    name="Compliance Specialist",
    description="Expert in content compliance and brand guidelines",
    
    system_prompt="""You are a compliance specialist focused on:
- Brand guidelines adherence
- Legal compliance (disclaimers, claims)
- Tone and voice consistency
- Factual accuracy

You always:
- Flag potential compliance issues
- Suggest corrections
- Provide clear reasoning
- Balance compliance with creativity
""",
    
    goal="Ensure content meets brand guidelines and compliance requirements",
    
    backstory="""You've worked in legal and brand management for major corporations.
You understand the balance between creative freedom and compliance requirements.""",
    
    model_config=ModelConfig(
        provider="anthropic",
        model="claude-3-sonnet",
        temperature=0.1,  # Very low temperature for compliance
        max_tokens=1500
    ),
    
    tools=["rag_tool"],  # Access brand guidelines from RAG
    
    metadata={
        "category": "compliance",
        "version": "1.0"
    }
)
```

### 3.4 Agent Registry

```python
# app/agents/registry.py

from typing import Dict
from app.agents.entities.agent import Agent
from app.agents.specialists.copywriter_agent import COPYWRITER_AGENT
from app.agents.specialists.research_agent import RESEARCH_AGENT
from app.agents.specialists.rag_agent import RAG_AGENT
from app.agents.specialists.compliance_agent import COMPLIANCE_AGENT

class AgentRegistry:
    """Registry per specialist agents."""
    
    def __init__(self):
        self._agents: Dict[str, Agent] = {}
        self._register_default_agents()
    
    def _register_default_agents(self):
        """Registra agent di default (generic)."""
        self.register(COPYWRITER_AGENT)
        self.register(RESEARCH_AGENT)
        self.register(RAG_AGENT)
        self.register(COMPLIANCE_AGENT)
    
    def register(self, agent: Agent):
        """Registra un agent."""
        self._agents[agent.agent_id] = agent
    
    def get(self, agent_id: str) -> Agent:
        """Recupera agent per agent_id."""
        if agent_id not in self._agents:
            raise ValueError(f"Agent not found: {agent_id}")
        return self._agents[agent_id]
    
    def list_agents(self) -> List[Agent]:
        """Lista tutti gli agent registrati."""
        return list(self._agents.values())

# Global registry instance
agent_registry = AgentRegistry()
```

### 3.5 Agent Executor (🔥 CRITICO - Tenant-Aware)

```python
# app/agents/executor.py

from app.agents.registry import agent_registry
from app.agents.entities.agent import Agent
from app.infrastructure.prompt_builder import PromptBuilder
from app.infrastructure.llm.factory import LLMProviderFactory
from app.infrastructure.tools.tool_manager import ToolManager
from app.infrastructure.database import DatabaseManager

class AgentExecutor:
    """
    Executor per agent tasks.
    
    🔥 RESPONSABILITÀ CHIAVE:
    - Caricare base agent (generic)
    - Caricare tenant-specific agent config (se esiste)
    - Merge configs (tenant OVERRIDE base)
    - Eseguire task con LLM
    - Gestire tool calls
    """
    
    def __init__(
        self,
        prompt_builder: PromptBuilder,
        llm_factory: LLMProviderFactory,
        tool_manager: ToolManager,
        db: DatabaseManager
    ):
        self.prompt_builder = prompt_builder
        self.llm_factory = llm_factory
        self.tool_manager = tool_manager
        self.db = db
    
    async def execute_task(
        self,
        agent_id: str,
        task: Task,
        context: Dict[str, Any]
    ) -> TaskResult:
        """
        Esegue un task usando un agent.
        
        🔥 TENANT-AWARE EXECUTION:
        1. Carica base agent (generic)
        2. Carica tenant config (se esiste)
        3. Merge (tenant OVERRIDE base)
        4. Build prompt
        5. Execute con LLM
        
        Args:
            agent_id: ID dell'agent da usare
            task: Task entity (da workflow)
            context: Context con tenant_id e task_input
        
        Returns:
            TaskResult con output del task
        """
        tenant_id = context.get("tenant_id")
        
        # 1. Carica base agent (generic)
        base_agent = agent_registry.get(agent_id)
        
        # 2. Carica tenant-specific config
        tenant_config = await self._load_tenant_agent_config(
            tenant_id=tenant_id,
            agent_id=agent_id
        )
        
        # 3. Merge configs (tenant OVERRIDE base)
        agent = self._merge_agent_configs(base_agent, tenant_config)
        
        # 4. Build prompt usando PromptBuilder
        prompt = await self._build_prompt(
            agent=agent,
            task=task,
            context=context
        )
        
        # 5. Initialize tools (se agent li usa)
        tools = await self._initialize_tools(
            agent=agent,
            tenant_id=tenant_id
        )
        
        # 6. Execute con LLM
        llm = self.llm_factory.create(
            provider=agent.model_config.provider
        )
        
        result = await llm.generate(
            prompt=prompt,
            model=agent.model_config.model,
            temperature=agent.model_config.temperature,
            max_tokens=agent.model_config.max_tokens,
            tools=tools  # LLM può chiamare tools se necessario
        )
        
        return TaskResult(
            task_id=task.task_id,
            agent_id=agent_id,
            output=result.content,
            metadata={
                "model_used": agent.model_config.model,
                "tokens_used": result.usage.total_tokens,
                "tools_called": result.tool_calls if result.tool_calls else []
            }
        )
    
    async def _load_tenant_agent_config(
        self,
        tenant_id: str,
        agent_id: str
    ) -> Optional[Dict]:
        """
        Carica tenant-specific agent config da database.
        
        Query: SELECT * FROM tenant_agent_configs
               WHERE tenant_id = ? AND agent_id = ?
        """
        query = """
            SELECT 
                custom_system_prompt,
                custom_goal,
                custom_backstory,
                model_config,
                tools
            FROM tenant_agent_configs
            WHERE tenant_id = $1 AND agent_id = $2
        """
        
        result = await self.db.fetch_one(query, tenant_id, agent_id)
        
        if not result:
            return None  # No tenant-specific config
        
        return {
            "system_prompt": result["custom_system_prompt"],
            "goal": result["custom_goal"],
            "backstory": result["custom_backstory"],
            "model_config": result["model_config"],  # JSONB
            "tools": result["tools"]  # JSONB array
        }
    
    def _merge_agent_configs(
        self,
        base_agent: Agent,
        tenant_config: Optional[Dict]
    ) -> Agent:
        """
        Merge tenant config into base agent.
        
        🔥 MERGE LOGIC:
        - Se tenant_config è None, usa base_agent
        - Se tenant_config esiste, tenant OVERRIDE base
        
        Esempio:
            base_agent.system_prompt = "You are a copywriter..."
            tenant_config.system_prompt = "You are ACME's copywriter..."
            
            Result: agent.system_prompt = "You are ACME's copywriter..."
        """
        if not tenant_config:
            return base_agent  # No override, usa generic
        
        # Create new Agent instance con overrides
        return Agent(
            agent_id=base_agent.agent_id,
            name=base_agent.name,
            description=base_agent.description,
            
            # Override system_prompt se tenant lo specifica
            system_prompt=tenant_config.get("system_prompt") or base_agent.system_prompt,
            
            # Override goal se tenant lo specifica
            goal=tenant_config.get("goal") or base_agent.goal,
            
            # Override backstory se tenant lo specifica
            backstory=tenant_config.get("backstory") or base_agent.backstory,
            
            # Override model_config se tenant lo specifica
            model_config=self._merge_model_config(
                base_agent.model_config,
                tenant_config.get("model_config")
            ),
            
            # Override tools se tenant lo specifica
            tools=tenant_config.get("tools") or base_agent.tools,
            
            metadata={
                **base_agent.metadata,
                "tenant_customized": True,
                "tenant_id": tenant_config.get("tenant_id")
            }
        )
    
    def _merge_model_config(
        self,
        base_config: ModelConfig,
        tenant_config: Optional[Dict]
    ) -> ModelConfig:
        """Merge model config."""
        if not tenant_config:
            return base_config
        
        return ModelConfig(
            provider=tenant_config.get("provider") or base_config.provider,
            model=tenant_config.get("model") or base_config.model,
            temperature=tenant_config.get("temperature") or base_config.temperature,
            max_tokens=tenant_config.get("max_tokens") or base_config.max_tokens,
            top_p=tenant_config.get("top_p") or base_config.top_p
        )
    
    async def _build_prompt(
        self,
        agent: Agent,
        task: Task,
        context: Dict[str, Any]
    ) -> str:
        """
        Build prompt usando PromptBuilder.
        
        Combina:
        - Agent system prompt
        - Task prompt template
        - Context variables
        """
        # Carica task prompt template
        task_template = await self.prompt_builder.load_template(
            task.prompt_template
        )
        
        # Render task prompt con context
        task_prompt = self.prompt_builder.render(
            template=task_template,
            variables={
                **context.get("task_input", {}),
                "agent_goal": agent.goal,
                "agent_backstory": agent.backstory
            }
        )
        
        # Combina system prompt + task prompt
        full_prompt = f"""{agent.system_prompt}

## Your Goal
{agent.goal}

## Your Backstory
{agent.backstory}

## Task
{task_prompt}
"""
        
        return full_prompt
    
    async def _initialize_tools(
        self,
        agent: Agent,
        tenant_id: str
    ) -> List[Tool]:
        """
        Initialize tools per agent.
        
        Carica tools specificati in agent.tools e li configura
        per il tenant specifico (es. API keys).
        """
        tools = []
        
        for tool_id in agent.tools:
            tool = await self.tool_manager.get_tool(
                tool_id=tool_id,
                tenant_id=tenant_id
            )
            tools.append(tool)
        
        return tools
```

---

## 4. PROMPT BUILDER

### 4.1 Cos'è il Prompt Builder?

Il **Prompt Builder** è un sistema basato su **Jinja2** per generare prompt dinamici da template.

**Responsabilità:**
- Caricare template Markdown (`.md`)
- Renderizzare template con variabili
- Supportare logica condizionale e loop
- Gestire template inheritance

### 4.2 Implementazione

```python
# app/infrastructure/prompt_builder.py

from jinja2 import Environment, FileSystemLoader, Template
from pathlib import Path
from typing import Dict, Any

class PromptBuilder:
    """
    Prompt Builder basato su Jinja2.
    
    Carica template Markdown e li renderizza con variabili.
    """
    
    def __init__(self, templates_dir: str):
        """
        Args:
            templates_dir: Path alla directory con template (es. "prompts/")
        """
        self.templates_dir = Path(templates_dir)
        
        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )
        
        # Add custom filters
        self.env.filters["word_count"] = lambda text: len(text.split())
        self.env.filters["truncate_words"] = self._truncate_words
    
    async def load_template(self, template_path: str) -> Template:
        """
        Carica template da file.
        
        Args:
            template_path: Path relativo a templates_dir (es. "copywriter/linkedin_post.md")
        
        Returns:
            Jinja2 Template object
        """
        return self.env.get_template(template_path)
    
    def render(
        self,
        template: Template,
        variables: Dict[str, Any]
    ) -> str:
        """
        Renderizza template con variabili.
        
        Args:
            template: Jinja2 Template object
            variables: Dict con variabili da sostituire
        
        Returns:
            Rendered string
        """
        return template.render(**variables)
    
    def render_string(
        self,
        template_str: str,
        variables: Dict[str, Any]
    ) -> str:
        """
        Renderizza template string (senza caricare da file).
        
        Utile per input_mapping in workflow YAML.
        
        Args:
            template_str: Template string (es. "{{ brand_name }}")
            variables: Dict con variabili
        
        Returns:
            Rendered string
        """
        template = self.env.from_string(template_str)
        return template.render(**variables)
    
    def _truncate_words(self, text: str, count: int) -> str:
        """Custom filter: truncate text to N words."""
        words = text.split()
        if len(words) <= count:
            return text
        return " ".join(words[:count]) + "..."
```

### 4.3 Template Structure

#### **Directory Structure**

```
prompts/
├── copywriter/
│   ├── linkedin_post.md
│   ├── blog_article.md
│   └── email_campaign.md
├── research/
│   ├── company_context.md
│   └── competitive_analysis.md
├── rag/
│   └── knowledge_retrieval.md
└── compliance/
    └── review.md
```

#### **Example Template: LinkedIn Post**

```markdown
<!-- prompts/copywriter/linkedin_post.md -->

# LinkedIn Post Generation Task

## Context
You are creating a LinkedIn post for **{{ company_name }}**.

### Company Description
{{ company_description }}

### Target Audience
{{ target_audience }}

### Main Message
{{ main_message }}

### Tone
{{ tone | default("professional") }}

{% if research_data %}
### Research Insights
{{ research_data }}
{% endif %}

## Task Instructions

Create a LinkedIn post that:

1. **Hook**: Start with an attention-grabbing opening (question, stat, or bold statement)
2. **Value**: Provide valuable insights or information
3. **Story**: Include a brief story or example if relevant
4. **CTA**: End with a clear call-to-action

## Requirements

- Length: 150-300 words
- Tone: {{ tone | default("professional") }}
- Include {{ hashtags_count | default(3) }} relevant hashtags
- Format: Use line breaks for readability
- Emoji: Use 1-2 relevant emojis (optional)

{% if cta %}
## Specific CTA
{{ cta }}
{% endif %}

## Output Format

Return a JSON object with:

```json
{
  "post_text": "The full LinkedIn post text",
  "hashtags": ["hashtag1", "hashtag2", "hashtag3"],
  "cta": "The call-to-action",
  "word_count": 250
}
```

## Example

```json
{
  "post_text": "🚀 Are you still manually managing your content workflow?\n\nWe recently helped a SaaS company reduce their content production time by 60% using AI-powered automation.\n\nHere's what they did:\n\n✅ Automated research and ideation\n✅ Streamlined approval workflows\n✅ Integrated brand voice consistency checks\n\nThe result? More content, better quality, less time.\n\nReady to transform your content workflow? Let's talk. 👇",
  "hashtags": ["ContentMarketing", "AIAutomation", "MarketingTech"],
  "cta": "Comment 'interested' below and I'll share our free workflow template",
  "word_count": 87
}
```

Now create the LinkedIn post for {{ company_name }}.
```

#### **Example Template: Research**

```markdown
<!-- prompts/research/company_context.md -->

# Company Research Task

## Company Information
- **Name**: {{ company_name }}
- **Description**: {{ company_description }}

## Research Objectives

Gather comprehensive information about {{ company_name }} including:

1. **Company Overview**
   - Industry and market position
   - Products/services
   - Target customers
   - Unique value proposition

2. **Recent News & Updates**
   - Product launches
   - Partnerships
   - Awards/recognition
   - Company milestones

3. **Competitive Landscape**
   - Main competitors
   - Market differentiation
   - Competitive advantages

4. **Brand Voice & Messaging**
   - Tone and style from existing content
   - Key messaging themes
   - Brand personality

## Tools Available

You have access to:
- **RAG Tool**: Search company knowledge base
- **Perplexity Tool**: Web research for recent information
- **Serper Tool**: Google search for additional context

## Output Format

Return a structured JSON object:

```json
{
  "company_overview": {
    "industry": "...",
    "market_position": "...",
    "products_services": ["..."],
    "target_customers": "...",
    "value_proposition": "..."
  },
  "recent_news": [
    {
      "title": "...",
      "date": "...",
      "summary": "..."
    }
  ],
  "competitive_landscape": {
    "main_competitors": ["..."],
    "differentiation": "...",
    "advantages": ["..."]
  },
  "brand_voice": {
    "tone": "...",
    "style": "...",
    "key_themes": ["..."]
  }
}
```

Begin your research now.
```

### 4.4 Jinja2 Features Used

#### **Variables**
```jinja2
{{ company_name }}
{{ target_audience }}
```

#### **Filters**
```jinja2
{{ tone | default("professional") }}
{{ text | word_count }}
{{ description | truncate_words(50) }}
```

#### **Conditionals**
```jinja2
{% if research_data %}
### Research Insights
{{ research_data }}
{% endif %}
```

#### **Loops**
```jinja2
{% for news_item in recent_news %}
- {{ news_item.title }} ({{ news_item.date }})
{% endfor %}
```

#### **Template Inheritance**
```jinja2
{% extends "base_prompt.md" %}

{% block task_instructions %}
Create a LinkedIn post...
{% endblock %}
```

---

## 5. TOOL SYSTEM

### 5.1 Cos'è un Tool?

Un **tool** è una **capability** che un agent può usare per eseguire azioni specifiche.

**Esempi:**
- **RAG Tool**: Semantic search nel knowledge base
- **Perplexity Tool**: Web research
- **Serper Tool**: Google search
- **Image Generation Tool**: Generare immagini

### 5.2 Tool Interface

```python
# app/infrastructure/tools/base_tool.py

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class ToolResult:
    """Risultato di una tool execution."""
    success: bool
    data: Any
    metadata: Dict[str, Any] = None
    error: str = None

class BaseTool(ABC):
    """
    Base class per tutti i tools.
    
    Ogni tool DEVE implementare:
    - execute(): Esegue il tool
    - get_schema(): Ritorna schema per LLM function calling
    """
    
    def __init__(self, tool_id: str, name: str, description: str):
        self.tool_id = tool_id
        self.name = name
        self.description = description
    
    @abstractmethod
    async def execute(
        self,
        params: Dict[str, Any],
        tenant_id: str
    ) -> ToolResult:
        """
        Esegue il tool.
        
        Args:
            params: Parametri per il tool
            tenant_id: Tenant ID (per tenant-aware execution)
        
        Returns:
            ToolResult con risultato
        """
        pass
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """
        Ritorna schema per LLM function calling.
        
        Returns:
            JSON schema compatibile con OpenAI function calling
        """
        pass
```

### 5.3 RAG Tool (🔥 CRITICO)

```python
# app/infrastructure/tools/rag_tool.py

from app.infrastructure.tools.base_tool import BaseTool, ToolResult
from app.infrastructure.database import DatabaseManager
import numpy as np

class RAGTool(BaseTool):
    """
    RAG (Retrieval-Augmented Generation) Tool.
    
    Esegue semantic search nel knowledge base usando pgvector.
    """
    
    def __init__(self, db: DatabaseManager, embedding_service: EmbeddingService):
        super().__init__(
            tool_id="rag_tool",
            name="Knowledge Base Search",
            description="Search company knowledge base for relevant information"
        )
        self.db = db
        self.embedding_service = embedding_service
    
    async def execute(
        self,
        params: Dict[str, Any],
        tenant_id: str
    ) -> ToolResult:
        """
        Esegue semantic search.
        
        Args:
            params: {
                "query": "search query",
                "top_k": 5,  # Number of results
                "filters": {}  # Optional filters
            }
            tenant_id: Tenant ID
        
        Returns:
            ToolResult con documenti trovati
        """
        query = params.get("query")
        top_k = params.get("top_k", 5)
        filters = params.get("filters", {})
        
        # 1. Generate embedding per query
        query_embedding = await self.embedding_service.embed(query)
        
        # 2. Semantic search usando pgvector
        results = await self._semantic_search(
            tenant_id=tenant_id,
            query_embedding=query_embedding,
            top_k=top_k,
            filters=filters
        )
        
        return ToolResult(
            success=True,
            data={
                "documents": results,
                "count": len(results)
            },
            metadata={
                "query": query,
                "top_k": top_k
            }
        )
    
    async def _semantic_search(
        self,
        tenant_id: str,
        query_embedding: List[float],
        top_k: int,
        filters: Dict
    ) -> List[Dict]:
        """
        Esegue semantic search usando pgvector.
        
        Query SQL:
        SELECT * FROM knowledge_base
        WHERE tenant_id = ?
        ORDER BY embedding <=> ?  -- Cosine distance
        LIMIT ?
        """
        query = """
            SELECT 
                document_id,
                content,
                metadata,
                1 - (embedding <=> $1::vector) AS similarity
            FROM knowledge_base
            WHERE tenant_id = $2
            ORDER BY embedding <=> $1::vector
            LIMIT $3
        """
        
        results = await self.db.fetch_all(
            query,
            query_embedding,
            tenant_id,
            top_k
        )
        
        return [
            {
                "document_id": row["document_id"],
                "content": row["content"],
                "metadata": row["metadata"],
                "similarity": row["similarity"]
            }
            for row in results
        ]
    
    def get_schema(self) -> Dict[str, Any]:
        """Schema per LLM function calling."""
        return {
            "type": "function",
            "function": {
                "name": "knowledge_base_search",
                "description": "Search company knowledge base for relevant information using semantic search",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query"
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of results to return (default: 5)",
                            "default": 5
                        }
                    },
                    "required": ["query"]
                }
            }
        }
```

### 5.4 Perplexity Tool

```python
# app/infrastructure/tools/perplexity_tool.py

from app.infrastructure.tools.base_tool import BaseTool, ToolResult
import httpx

class PerplexityTool(BaseTool):
    """
    Perplexity AI Tool.
    
    Esegue web research usando Perplexity API.
    """
    
    def __init__(self, api_key: str):
        super().__init__(
            tool_id="perplexity_tool",
            name="Web Research",
            description="Search the web for recent information using Perplexity AI"
        )
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai"
    
    async def execute(
        self,
        params: Dict[str, Any],
        tenant_id: str
    ) -> ToolResult:
        """
        Esegue web research.
        
        Args:
            params: {
                "query": "research query",
                "focus": "web" | "academic" | "news"
            }
            tenant_id: Tenant ID
        
        Returns:
            ToolResult con risultati research
        """
        query = params.get("query")
        focus = params.get("focus", "web")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.1-sonar-large-128k-online",
                    "messages": [
                        {
                            "role": "user",
                            "content": query
                        }
                    ],
                    "search_domain_filter": [focus] if focus != "web" else None
                }
            )
            
            result = response.json()
            
            return ToolResult(
                success=True,
                data={
                    "answer": result["choices"][0]["message"]["content"],
                    "sources": result.get("citations", [])
                },
                metadata={
                    "query": query,
                    "focus": focus
                }
            )
    
    def get_schema(self) -> Dict[str, Any]:
        """Schema per LLM function calling."""
        return {
            "type": "function",
            "function": {
                "name": "web_research",
                "description": "Search the web for recent information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The research query"
                        },
                        "focus": {
                            "type": "string",
                            "enum": ["web", "academic", "news"],
                            "description": "Focus area for research",
                            "default": "web"
                        }
                    },
                    "required": ["query"]
                }
            }
        }
```

### 5.5 Tool Manager

```python
# app/infrastructure/tools/tool_manager.py

from typing import Dict, List
from app.infrastructure.tools.base_tool import BaseTool
from app.infrastructure.tools.rag_tool import RAGTool
from app.infrastructure.tools.perplexity_tool import PerplexityTool
from app.infrastructure.tools.serper_tool import SerperTool

class ToolManager:
    """
    Manager per tools.
    
    Responsabilità:
    - Registrare tools
    - Recuperare tools per agent
    - Configurare tools per tenant
    """
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
    
    def register(self, tool: BaseTool):
        """Registra un tool."""
        self._tools[tool.tool_id] = tool
    
    async def get_tool(
        self,
        tool_id: str,
        tenant_id: str
    ) -> BaseTool:
        """
        Recupera tool configurato per tenant.
        
        Args:
            tool_id: ID del tool
            tenant_id: Tenant ID (per configurazione tenant-specific)
        
        Returns:
            BaseTool instance
        """
        if tool_id not in self._tools:
            raise ValueError(f"Tool not found: {tool_id}")
        
        tool = self._tools[tool_id]
        
        # TODO: Apply tenant-specific configuration
        # (es. API keys, rate limits)
        
        return tool
    
    def list_tools(self) -> List[BaseTool]:
        """Lista tutti i tools registrati."""
        return list(self._tools.values())
    
    def get_schemas(self, tool_ids: List[str]) -> List[Dict]:
        """
        Ottieni schemas per LLM function calling.
        
        Args:
            tool_ids: List di tool_id
        
        Returns:
            List di JSON schemas
        """
        return [
            self._tools[tool_id].get_schema()
            for tool_id in tool_ids
            if tool_id in self._tools
        ]
```

---

## 6. TENANT-AWARE ARCHITECTURE

### 6.1 Principio Fondamentale

**OGNI risorsa (workflow, agent, prompt, tool) ha 2 livelli:**

1. **Base (Generic):** Configurazione di default
2. **Tenant-Specific (Override):** Configurazione personalizzata

**Merge Logic:**
```python
final_config = merge(base_config, tenant_config)
# tenant_config OVERRIDE base_config
```

### 6.2 Tenant Context Middleware

```python
# app/middleware/tenant_context.py

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from contextvars import ContextVar

# Global context var per tenant_id
tenant_context: ContextVar[str] = ContextVar("tenant_id", default=None)

class TenantContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware che estrae tenant_id da request e lo salva in context.

    Tenant ID può venire da:
    - Header: X-Tenant-ID
    - JWT token (dopo auth)
    - API key (dopo auth)
    """

    async def dispatch(self, request: Request, call_next):
        # 1. Estrai tenant_id da header
        tenant_id = request.headers.get("X-Tenant-ID")

        # 2. Se non presente, estrai da JWT (dopo auth middleware)
        if not tenant_id and hasattr(request.state, "user"):
            tenant_id = request.state.user.tenant_id

        # 3. Salva in context
        if tenant_id:
            tenant_context.set(tenant_id)

        # 4. Process request
        response = await call_next(request)

        # 5. Clear context
        tenant_context.set(None)

        return response
```

### 6.3 Tenant-Aware Database Queries

**OGNI query DEVE filtrare per tenant_id:**

```python
# ✅ CORRETTO
query = """
    SELECT * FROM knowledge_base
    WHERE tenant_id = $1 AND document_id = $2
"""
result = await db.fetch_one(query, tenant_id, document_id)

# ❌ SBAGLIATO (manca tenant_id filter!)
query = """
    SELECT * FROM knowledge_base
    WHERE document_id = $1
"""
result = await db.fetch_one(query, document_id)
```

### 6.4 Tenant-Specific Customizations

#### **A. Agent Customization**

**Scenario:** ACME Corp vuole un copywriter con tono specifico.

**Base Agent (Generic):**
```python
COPYWRITER_AGENT = Agent(
    agent_id="copywriter",
    system_prompt="You are an expert copywriter...",
    goal="Create high-quality content",
    backstory="You've worked with Fortune 500 companies...",
    model_config=ModelConfig(provider="anthropic", model="claude-3-sonnet")
)
```

**Tenant Override (ACME Corp):**
```sql
INSERT INTO tenant_agent_configs (tenant_id, agent_id, custom_system_prompt, custom_goal, model_config)
VALUES (
    'acme-corp-uuid',
    'copywriter',
    'You are ACME Corp''s copywriter. ACME is a B2B SaaS company focused on AI automation. Always emphasize ROI and data-driven results.',
    'Create content that positions ACME as a thought leader in AI automation',
    '{"provider": "anthropic", "model": "claude-3-opus", "temperature": 0.8}'
);
```

**Result:**
```python
# AgentExecutor carica base + tenant config
base_agent = agent_registry.get("copywriter")
tenant_config = await db.fetch_tenant_config("acme-corp-uuid", "copywriter")

# Merge: tenant OVERRIDE base
agent = merge_configs(base_agent, tenant_config)

# agent.system_prompt = "You are ACME Corp's copywriter..."
# agent.model_config.model = "claude-3-opus"
```

#### **B. Workflow Customization**

**Scenario:** ACME Corp vuole un task extra nel workflow LinkedIn Post.

**Base Workflow (Generic):**
```yaml
tasks:
  - task_id: "research"
    agent_id: "research_specialist"
  - task_id: "generate_post"
    agent_id: "copywriter"
  - task_id: "compliance_review"
    agent_id: "compliance_specialist"
```

**Tenant Override (ACME Corp):**
```sql
INSERT INTO tenant_workflow_configs (tenant_id, workflow_id, custom_tasks)
VALUES (
    'acme-corp-uuid',
    'linkedin_post',
    '[
        {
            "task_id": "research",
            "agent_id": "research_specialist"
        },
        {
            "task_id": "generate_post",
            "agent_id": "copywriter"
        },
        {
            "task_id": "seo_optimization",
            "agent_id": "seo_specialist",
            "prompt_template": "seo/optimize_linkedin.md"
        },
        {
            "task_id": "compliance_review",
            "agent_id": "compliance_specialist"
        }
    ]'
);
```

**Result:** ACME Corp ha un task extra "seo_optimization" nel workflow.

#### **C. Prompt Template Customization**

**Scenario:** ACME Corp vuole un prompt template personalizzato.

**Base Template (Generic):**
```markdown
<!-- prompts/copywriter/linkedin_post.md -->
Create a LinkedIn post for {{ company_name }}.
Tone: {{ tone | default("professional") }}
```

**Tenant Template (ACME Corp):**
```markdown
<!-- prompts/tenants/acme-corp/copywriter/linkedin_post.md -->
Create a LinkedIn post for ACME Corp.

ACME's Brand Guidelines:
- Always emphasize ROI and data-driven results
- Use statistics and case studies
- Tone: Authoritative but approachable
- Include a clear CTA

Tone: data-driven and authoritative
```

**PromptBuilder logic:**
```python
async def load_template(self, template_path: str, tenant_id: str) -> Template:
    # 1. Check if tenant-specific template exists
    tenant_template_path = f"tenants/{tenant_id}/{template_path}"

    if self._template_exists(tenant_template_path):
        return self.env.get_template(tenant_template_path)

    # 2. Fallback to generic template
    return self.env.get_template(template_path)
```

---

## 7. DATABASE SCHEMA

### 7.1 Core Tables

#### **tenant_agent_configs**

```sql
CREATE TABLE tenant_agent_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    agent_id VARCHAR(50) NOT NULL,

    -- Customizations
    custom_system_prompt TEXT,
    custom_goal TEXT,
    custom_backstory TEXT,
    model_config JSONB,  -- {"provider": "anthropic", "model": "claude-3-opus", ...}
    tools JSONB,  -- ["rag_tool", "perplexity_tool"]

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES users(id),

    UNIQUE(tenant_id, agent_id)
);

CREATE INDEX idx_tenant_agent_configs_tenant ON tenant_agent_configs(tenant_id);
CREATE INDEX idx_tenant_agent_configs_agent ON tenant_agent_configs(agent_id);
```

#### **tenant_workflow_configs**

```sql
CREATE TABLE tenant_workflow_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    workflow_id VARCHAR(50) NOT NULL,

    -- Customizations
    custom_tasks JSONB,  -- Override task sequence
    custom_output_format JSONB,  -- Override output format

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES users(id),

    UNIQUE(tenant_id, workflow_id)
);

CREATE INDEX idx_tenant_workflow_configs_tenant ON tenant_workflow_configs(tenant_id);
CREATE INDEX idx_tenant_workflow_configs_workflow ON tenant_workflow_configs(workflow_id);
```

#### **workflow_runs**

```sql
CREATE TABLE workflow_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    workflow_id VARCHAR(50) NOT NULL,

    -- Input/Output
    input_data JSONB NOT NULL,
    output_data JSONB,

    -- Status
    status VARCHAR(20) NOT NULL,  -- 'pending', 'running', 'completed', 'failed'
    error_message TEXT,

    -- Execution metadata
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    duration_ms INTEGER,

    -- Task execution details
    task_results JSONB,  -- Array of task results

    -- Metadata
    created_by UUID REFERENCES users(id)
);

CREATE INDEX idx_workflow_runs_tenant ON workflow_runs(tenant_id);
CREATE INDEX idx_workflow_runs_workflow ON workflow_runs(workflow_id);
CREATE INDEX idx_workflow_runs_status ON workflow_runs(status);
CREATE INDEX idx_workflow_runs_created ON workflow_runs(started_at DESC);
```

#### **knowledge_base**

```sql
CREATE TABLE knowledge_base (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    document_id VARCHAR(255) NOT NULL,

    -- Content
    content TEXT NOT NULL,
    metadata JSONB,  -- {"source": "...", "type": "...", "tags": [...]}

    -- Embedding (pgvector)
    embedding vector(1536),  -- OpenAI ada-002 dimension

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(tenant_id, document_id)
);

CREATE INDEX idx_knowledge_base_tenant ON knowledge_base(tenant_id);
CREATE INDEX idx_knowledge_base_embedding ON knowledge_base USING ivfflat (embedding vector_cosine_ops);
```

#### **tool_configs**

```sql
CREATE TABLE tool_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    tool_id VARCHAR(50) NOT NULL,

    -- Configuration
    config JSONB,  -- {"api_key": "...", "rate_limit": 100, ...}
    enabled BOOLEAN DEFAULT TRUE,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(tenant_id, tool_id)
);

CREATE INDEX idx_tool_configs_tenant ON tool_configs(tenant_id);
CREATE INDEX idx_tool_configs_tool ON tool_configs(tool_id);
```

---

## 8. EXECUTION FLOW

### 8.1 End-to-End Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. API REQUEST                                                   │
├─────────────────────────────────────────────────────────────────┤
│ POST /api/v1/workflows/execute                                  │
│ Headers: { "X-Tenant-ID": "acme-corp-uuid" }                    │
│ Body: {                                                          │
│   "workflow_id": "linkedin_post",                               │
│   "input_data": {                                               │
│     "brand_name": "ACME Corp",                                  │
│     "target_audience": "Tech leaders",                          │
│     "main_message": "AI automation ROI"                         │
│   }                                                              │
│ }                                                                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. TENANT CONTEXT MIDDLEWARE                                     │
├─────────────────────────────────────────────────────────────────┤
│ - Extract tenant_id from header: "acme-corp-uuid"               │
│ - Save in context: tenant_context.set("acme-corp-uuid")         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. WORKFLOW ORCHESTRATOR                                         │
├─────────────────────────────────────────────────────────────────┤
│ WorkflowOrchestrator.execute(                                    │
│   workflow_id="linkedin_post",                                  │
│   input_data={...},                                             │
│   tenant_id="acme-corp-uuid"                                    │
│ )                                                                │
│                                                                  │
│ 3.1. Load workflow YAML (generic)                               │
│      → workflows/templates/linkedin_post.yaml                   │
│                                                                  │
│ 3.2. Load tenant workflow overrides                             │
│      → Query: tenant_workflow_configs                           │
│      → Result: ACME has custom task "seo_optimization"          │
│                                                                  │
│ 3.3. Merge: tenant OVERRIDE generic                             │
│      → Final workflow has 4 tasks (research, generate, seo, compliance) │
│                                                                  │
│ 3.4. Get handler: LinkedInPostHandler                           │
│                                                                  │
│ 3.5. Execute handler                                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. WORKFLOW HANDLER                                              │
├─────────────────────────────────────────────────────────────────┤
│ LinkedInPostHandler.execute()                                    │
│                                                                  │
│ 4.1. Validate input                                             │
│      ✅ brand_name, target_audience, main_message present       │
│                                                                  │
│ 4.2. Initialize context                                         │
│      context = {                                                │
│        "tenant_id": "acme-corp-uuid",                           │
│        "input": {...},                                          │
│        "tasks": {}                                              │
│      }                                                           │
│                                                                  │
│ 4.3. Execute tasks in sequence                                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 5. TASK 1: RESEARCH                                              │
├─────────────────────────────────────────────────────────────────┤
│ AgentExecutor.execute_task(                                      │
│   agent_id="research_specialist",                               │
│   task={...},                                                    │
│   context={...}                                                  │
│ )                                                                │
│                                                                  │
│ 5.1. Load base agent (generic)                                  │
│      → agent_registry.get("research_specialist")                │
│                                                                  │
│ 5.2. Load tenant agent config                                   │
│      → Query: tenant_agent_configs                              │
│      → Result: ACME has custom system_prompt                    │
│                                                                  │
│ 5.3. Merge: tenant OVERRIDE base                                │
│      → agent.system_prompt = "You are ACME's researcher..."     │
│                                                                  │
│ 5.4. Build prompt                                               │
│      → Load template: prompts/research/company_context.md       │
│      → Render with variables: {company_name: "ACME Corp", ...}  │
│                                                                  │
│ 5.5. Initialize tools                                           │
│      → RAG Tool (tenant-aware)                                  │
│      → Perplexity Tool (tenant-aware)                           │
│                                                                  │
│ 5.6. Execute with LLM                                           │
│      → LLM: gpt-4-turbo                                         │
│      → Prompt: "You are ACME's researcher... Research ACME..."  │
│      → Tools: [rag_tool, perplexity_tool]                       │
│      → Result: Research data (JSON)                             │
│                                                                  │
│ 5.7. Store result in context                                    │
│      → context["tasks"]["research"] = {"output": {...}}         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 6. TASK 2: GENERATE POST                                         │
├─────────────────────────────────────────────────────────────────┤
│ AgentExecutor.execute_task(                                      │
│   agent_id="copywriter",                                        │
│   task={...},                                                    │
│   context={...}                                                  │
│ )                                                                │
│                                                                  │
│ 6.1. Load base agent (generic)                                  │
│      → agent_registry.get("copywriter")                         │
│                                                                  │
│ 6.2. Load tenant agent config                                   │
│      → Query: tenant_agent_configs                              │
│      → Result: ACME has custom system_prompt + model            │
│                                                                  │
│ 6.3. Merge: tenant OVERRIDE base                                │
│      → agent.system_prompt = "You are ACME's copywriter..."     │
│      → agent.model_config.model = "claude-3-opus"               │
│                                                                  │
│ 6.4. Build prompt                                               │
│      → Check tenant template: prompts/tenants/acme-corp/...     │
│      → Found! Use ACME's custom template                        │
│      → Render with variables: {                                 │
│          company_name: "ACME Corp",                             │
│          research_data: context["tasks"]["research"]["output"], │
│          target_audience: "Tech leaders",                       │
│          main_message: "AI automation ROI"                      │
│        }                                                         │
│                                                                  │
│ 6.5. Execute with LLM                                           │
│      → LLM: claude-3-opus (ACME's custom model)                 │
│      → Prompt: "You are ACME's copywriter... Create post..."    │
│      → Result: LinkedIn post (JSON)                             │
│                                                                  │
│ 6.6. Store result in context                                    │
│      → context["tasks"]["generate_post"] = {"output": {...}}    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 7. TASK 3: SEO OPTIMIZATION (ACME's custom task)                │
├─────────────────────────────────────────────────────────────────┤
│ AgentExecutor.execute_task(                                      │
│   agent_id="seo_specialist",                                    │
│   task={...},                                                    │
│   context={...}                                                  │
│ )                                                                │
│                                                                  │
│ → Optimize post for SEO                                         │
│ → Store result in context                                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 8. TASK 4: COMPLIANCE REVIEW                                     │
├─────────────────────────────────────────────────────────────────┤
│ AgentExecutor.execute_task(                                      │
│   agent_id="compliance_specialist",                             │
│   task={...},                                                    │
│   context={...}                                                  │
│ )                                                                │
│                                                                  │
│ → Review post for compliance                                    │
│ → Store result in context                                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 9. FORMAT OUTPUT                                                 │
├─────────────────────────────────────────────────────────────────┤
│ LinkedInPostHandler._format_output()                             │
│                                                                  │
│ → Extract outputs from all tasks                                │
│ → Format final output:                                          │
│   {                                                              │
│     "content_id": "uuid",                                       │
│     "title": "LinkedIn Post: ACME Corp",                        │
│     "body": "🚀 Are you still manually...",                     │
│     "format": "markdown",                                       │
│     "word_count": 87,                                           │
│     "metadata": {                                               │
│       "display_type": "linkedin_post",                          │
│       "hashtags": ["AIAutomation", "ROI"],                      │
│       "cta": "Comment 'interested' below",                      │
│       "compliance_status": "approved",                          │
│       "seo_score": 85  ← From ACME's custom task                │
│     }                                                            │
│   }                                                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 10. RETURN RESULT                                                │
├─────────────────────────────────────────────────────────────────┤
│ Response: {                                                      │
│   "workflow_id": "linkedin_post",                               │
│   "status": "completed",                                        │
│   "output": {...},                                              │
│   "metadata": {                                                 │
│     "tenant_id": "acme-corp-uuid",                              │
│     "tasks_executed": 4,                                        │
│     "duration_ms": 12500                                        │
│   }                                                              │
│ }                                                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 9. FILE RILEVANTI

### 9.1 Directory Structure

```
app/
├── workflows/
│   ├── entities/
│   │   └── workflow.py                 # Workflow entity
│   ├── handlers/
│   │   ├── base_handler.py             # Base handler class
│   │   ├── linkedin_post_handler.py    # LinkedIn handler
│   │   ├── blog_article_handler.py     # Blog handler
│   │   └── analytics_handler.py        # Analytics handler
│   ├── loaders/
│   │   └── yaml_loader.py              # YAML workflow loader
│   ├── registry.py                     # Workflow registry
│   └── orchestrator.py                 # Workflow orchestrator
│
├── agents/
│   ├── entities/
│   │   └── agent.py                    # Agent entity
│   ├── specialists/
│   │   ├── copywriter_agent.py         # Copywriter specialist
│   │   ├── research_agent.py           # Research specialist
│   │   ├── rag_agent.py                # RAG specialist
│   │   └── compliance_agent.py         # Compliance specialist
│   ├── registry.py                     # Agent registry
│   └── executor.py                     # 🔥 Agent executor (tenant-aware)
│
├── infrastructure/
│   ├── prompt_builder.py               # 🔥 Prompt builder (Jinja2)
│   ├── llm/
│   │   ├── factory.py                  # LLM provider factory
│   │   ├── openai_adapter.py           # OpenAI adapter
│   │   ├── anthropic_adapter.py        # Anthropic adapter
│   │   └── gemini_adapter.py           # Gemini adapter
│   ├── tools/
│   │   ├── base_tool.py                # Base tool class
│   │   ├── rag_tool.py                 # 🔥 RAG tool
│   │   ├── perplexity_tool.py          # Perplexity tool
│   │   └── serper_tool.py              # Serper tool
│   └── database.py                     # Database manager
│
└── middleware/
    └── tenant_context.py               # Tenant context middleware

workflows/
└── templates/
    ├── linkedin_post.yaml              # LinkedIn workflow
    ├── blog_article.yaml               # Blog workflow
    └── analytics_dashboard.yaml        # Analytics workflow

prompts/
├── copywriter/
│   ├── linkedin_post.md                # LinkedIn prompt
│   └── blog_article.md                 # Blog prompt
├── research/
│   └── company_context.md              # Research prompt
└── tenants/
    └── acme-corp/
        └── copywriter/
            └── linkedin_post.md        # ACME's custom prompt
```

### 9.2 File Priorità

| File | Priorità | Descrizione |
|------|----------|-------------|
| `agents/executor.py` | 🔥 P0 | Agent executor tenant-aware |
| `infrastructure/prompt_builder.py` | 🔥 P0 | Prompt builder Jinja2 |
| `infrastructure/tools/rag_tool.py` | 🔥 P0 | RAG tool (semantic search) |
| `workflows/orchestrator.py` | 🔥 P0 | Workflow orchestrator |
| `workflows/handlers/base_handler.py` | P1 | Base handler class |
| `workflows/handlers/linkedin_post_handler.py` | P1 | LinkedIn handler |
| `agents/specialists/copywriter_agent.py` | P1 | Copywriter specialist |
| `agents/specialists/research_agent.py` | P1 | Research specialist |
| `infrastructure/llm/factory.py` | P1 | LLM provider factory |
| `infrastructure/tools/perplexity_tool.py` | P2 | Perplexity tool |

---

## 10. BEST PRACTICES

### 10.1 Tenant-Aware Development

#### **✅ DO:**

```python
# SEMPRE passa tenant_id
async def execute_workflow(workflow_id: str, input_data: dict, tenant_id: str):
    ...

# SEMPRE filtra per tenant_id in query
query = "SELECT * FROM knowledge_base WHERE tenant_id = $1"

# SEMPRE carica tenant config
tenant_config = await load_tenant_config(tenant_id, agent_id)

# SEMPRE merge tenant OVERRIDE base
final_config = merge(base_config, tenant_config)
```

#### **❌ DON'T:**

```python
# NON hardcodare tenant-specific logic
if tenant_id == "acme-corp":
    system_prompt = "You are ACME's copywriter..."

# NON dimenticare tenant_id in query
query = "SELECT * FROM knowledge_base WHERE document_id = $1"

# NON ignorare tenant config
agent = agent_registry.get(agent_id)  # Manca merge con tenant config!
```

### 10.2 Prompt Engineering

#### **✅ DO:**

```markdown
<!-- Usa variabili Jinja2 -->
{{ company_name }}
{{ target_audience }}

<!-- Usa filters -->
{{ tone | default("professional") }}
{{ text | truncate_words(50) }}

<!-- Usa conditionals -->
{% if research_data %}
### Research Insights
{{ research_data }}
{% endif %}

<!-- Fornisci esempi -->
## Example Output
```json
{
  "post_text": "...",
  "hashtags": ["..."]
}
```
```

#### **❌ DON'T:**

```markdown
<!-- NON hardcodare valori -->
Create a post for ACME Corp  <!-- Usa {{ company_name }} -->

<!-- NON dimenticare default values -->
Tone: {{ tone }}  <!-- Usa {{ tone | default("professional") }} -->

<!-- NON dimenticare esempi -->
Return a JSON object.  <!-- Fornisci esempio! -->
```

### 10.3 Error Handling

```python
# ✅ CORRETTO
try:
    result = await agent_executor.execute_task(...)
except AgentExecutionError as e:
    logger.error(f"Agent execution failed: {e}", extra={
        "tenant_id": tenant_id,
        "agent_id": agent_id,
        "task_id": task.task_id
    })
    raise WorkflowExecutionError(f"Task {task.task_id} failed") from e

# ❌ SBAGLIATO
result = await agent_executor.execute_task(...)  # No error handling!
```

### 10.4 Testing

```python
# ✅ Test tenant-aware logic
async def test_agent_executor_with_tenant_config():
    # Setup
    tenant_id = "test-tenant"
    agent_id = "copywriter"

    # Insert tenant config
    await db.execute("""
        INSERT INTO tenant_agent_configs (tenant_id, agent_id, custom_system_prompt)
        VALUES ($1, $2, $3)
    """, tenant_id, agent_id, "Custom prompt")

    # Execute
    result = await agent_executor.execute_task(
        agent_id=agent_id,
        task=test_task,
        context={"tenant_id": tenant_id}
    )

    # Assert: tenant config was used
    assert "Custom prompt" in result.metadata["prompt_used"]
```

---

## 11. TROUBLESHOOTING

### 11.1 Common Issues

#### **Issue: Agent non usa tenant config**

**Sintomo:** Agent usa sempre configurazione generic, ignora tenant config.

**Causa:** `AgentExecutor` non carica tenant config o merge non funziona.

**Debug:**
```python
# Add logging in AgentExecutor
logger.info(f"Loading tenant config for {tenant_id}, {agent_id}")
tenant_config = await self._load_tenant_agent_config(tenant_id, agent_id)
logger.info(f"Tenant config: {tenant_config}")

# Check merge
agent = self._merge_agent_configs(base_agent, tenant_config)
logger.info(f"Final agent system_prompt: {agent.system_prompt}")
```

**Fix:** Verifica che:
1. `tenant_agent_configs` table ha record per tenant
2. `_load_tenant_agent_config()` query è corretta
3. `_merge_agent_configs()` fa override correttamente

---

#### **Issue: Prompt template non trovato**

**Sintomo:** `TemplateNotFound: prompts/copywriter/linkedin_post.md`

**Causa:** Template path non esiste o `PromptBuilder` templates_dir è sbagliato.

**Debug:**
```python
# Check templates_dir
logger.info(f"Templates dir: {prompt_builder.templates_dir}")

# Check if template exists
template_path = prompt_builder.templates_dir / "copywriter/linkedin_post.md"
logger.info(f"Template exists: {template_path.exists()}")
```

**Fix:** Verifica che:
1. `templates_dir` punta a directory corretta
2. Template file esiste
3. Path in workflow YAML è corretto

---

#### **Issue: RAG tool non trova documenti**

**Sintomo:** RAG tool ritorna 0 risultati anche se knowledge base ha documenti.

**Causa:** Query non filtra per `tenant_id` o embedding non è stato generato.

**Debug:**
```python
# Check if documents exist for tenant
query = "SELECT COUNT(*) FROM knowledge_base WHERE tenant_id = $1"
count = await db.fetch_val(query, tenant_id)
logger.info(f"Documents for tenant {tenant_id}: {count}")

# Check if embeddings exist
query = "SELECT COUNT(*) FROM knowledge_base WHERE tenant_id = $1 AND embedding IS NOT NULL"
count = await db.fetch_val(query, tenant_id)
logger.info(f"Documents with embeddings: {count}")
```

**Fix:** Verifica che:
1. Knowledge base ha documenti per tenant
2. Embeddings sono stati generati
3. Query filtra per `tenant_id`

---

## 12. SUMMARY

### 12.1 Key Takeaways

1. **Separation of Concerns:**
   - Workflow = Orchestrazione
   - Agent = Esecuzione
   - Prompt Builder = Template rendering
   - Tool = Capabilities

2. **Tenant-Aware by Design:**
   - OGNI componente è tenant-aware
   - Base (Generic) + Tenant (Override) pattern
   - tenant_id passato ovunque

3. **YAML Workflows:**
   - Definiscono task sequence
   - Input schema + Output format
   - Tenant può override task sequence

4. **Specialist Agents:**
   - Copywriter, Research, RAG, Compliance
   - System prompt + Goal + Backstory
   - Tenant può override tutto

5. **Prompt Builder (Jinja2):**
   - Template Markdown (`.md`)
   - Variabili, filters, conditionals
   - Tenant può avere template custom

6. **Tool System:**
   - RAG (semantic search)
   - Perplexity (web research)
   - Serper (Google search)
   - Tenant-aware configuration

---

**Questo è il nostro DIFFERENZIANTE! 🔥**

Il sistema Agentic AI di Fylle è:
- ✅ **Tenant-aware** (personalizzazione completa)
- ✅ **Flessibile** (YAML workflows, Jinja2 prompts)
- ✅ **Scalabile** (registry pattern, dependency injection)
- ✅ **Testabile** (separation of concerns, mock-friendly)
- ✅ **Production-ready** (error handling, logging, monitoring)

---

**Fine documento AGENTIC_AI_CORE.md**

