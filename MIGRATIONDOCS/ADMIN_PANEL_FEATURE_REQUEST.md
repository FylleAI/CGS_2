# [FYL-XX] Admin Panel: Workflow, Agent & Tool Configuration Management

> **Type:** Feature Request  
> **Priority:** P1 (High)  
> **Status:** Backlog  
> **Team:** Frontend + Backend  
> **Effort Estimate:** 80 hours (2 weeks)  
> **Created:** 2025-01-22

---

## 📋 OVERVIEW

### Summary

Build an admin panel that allows administrators to configure and customize:
1. **Workflows** (generic + tenant-specific task sequences)
2. **Agents** (generic + tenant-specific system prompts, goals, backstories)
3. **Tools** (descriptions, tenant-specific configurations)

This admin panel is critical for enabling **tenant-specific customizations** without code changes


---

## 👤 USER STORIES

### Story 1: Workflow Management

**As an** admin  
**I want to** view and modify workflow task sequences (generic and tenant-specific)  
**So that** I can customize content generation workflows for specific tenants without code changes

**Acceptance Criteria:**
- [ ] Can view list of all available workflows
- [ ] Can view task sequence for each workflow (generic)
- [ ] Can add/remove/reorder tasks in a workflow (tenant-specific override)
- [ ] Can modify task parameters (agent_id, prompt_template, tools)
- [ ] Can preview YAML representation of workflow
- [ ] Can test workflow execution with sample input
- [ ] Changes are saved to `tenant_workflow_configs` table
- [ ] Can revert to generic workflow (delete tenant override)

---

### Story 2: Agent Configuration Management

**As an** admin  
**I want to** configure agent system prompts, goals, and backstories (generic and tenant-specific)  
**So that** I can customize AI agent behavior for specific tenants

**Acceptance Criteria:**
- [ ] Can view list of all available agents (copywriter, research, RAG, compliance)
- [ ] Can view agent details (system_prompt, goal, backstory, model_config, tools)
- [ ] Can edit generic agent configuration (affects all tenants)
- [ ] Can create tenant-specific agent override (system_prompt, goal, backstory)
- [ ] Can modify model configuration (provider, model, temperature, max_tokens)
- [ ] Can enable/disable tools for agent
- [ ] Can preview how agent will behave with sample task
- [ ] Changes are saved to `tenant_agent_configs` table
- [ ] Can revert to generic agent (delete tenant override)

---

### Story 3: Tool Configuration Management

**As an** admin  
**I want to** configure tool descriptions and tenant-specific settings  
**So that** I can enable/disable tools and configure API keys per tenant

**Acceptance Criteria:**
- [ ] Can view list of all available tools (RAG, Perplexity, Serper, Image Gen)
- [ ] Can view tool details (description, parameters, schema)
- [ ] Can edit tool description (affects LLM function calling)
- [ ] Can configure tenant-specific tool settings (API keys, rate limits)
- [ ] Can enable/disable tool for specific tenant
- [ ] Can test tool execution with sample parameters
- [ ] Changes are saved to `tool_configs` table
- [ ] Can view tool usage analytics per tenant

---

## 🎨 UI/UX REQUIREMENTS

### Navigation Structure

```
Admin Panel
├── Dashboard
│   ├── Overview (stats, recent changes)
│   └── Quick Actions
│
├── Workflows
│   ├── List View (all workflows)
│   ├── Detail View (workflow tasks)
│   └── Tenant Overrides (per tenant customizations)
│
├── Agents
│   ├── List View (all agents)
│   ├── Detail View (agent config)
│   └── Tenant Overrides (per tenant customizations)
│
└── Tools
    ├── List View (all tools)
    ├── Detail View (tool config)
    └── Tenant Configs (per tenant settings)
```

### Key UI Components

#### 1. Workflow List View

```
┌─────────────────────────────────────────────────────────────────┐
│ Workflows                                          [+ New]       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ ┌──────────────────────────────────────────────────────────┐   │
│ │ 📄 LinkedIn Post Generator                    [Edit] [⚙️] │   │
│ │ Generate professional LinkedIn posts                      │   │
│ │ Tasks: 3 • Version: 1.0 • Tenants with overrides: 5      │   │
│ └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│ ┌──────────────────────────────────────────────────────────┐   │
│ │ 📝 Blog Article Generator                     [Edit] [⚙️] │   │
│ │ Generate SEO-optimized blog articles                      │   │
│ │ Tasks: 4 • Version: 1.0 • Tenants with overrides: 2      │   │
│ └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│ ┌──────────────────────────────────────────────────────────┐   │
│ │ 🏢 Company Snapshot                           [Edit] [⚙️] │   │
│ │ Generate comprehensive company snapshot                   │   │
│ │ Tasks: 2 • Version: 1.0 • Tenants with overrides: 8      │   │
│ └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### 2. Workflow Detail View (Generic)

```
┌─────────────────────────────────────────────────────────────────┐
│ ← Back to Workflows                                             │
├─────────────────────────────────────────────────────────────────┤
│ LinkedIn Post Generator                                          │
│ Generate professional LinkedIn posts based on company context    │
│                                                                  │
│ [Generic Config] [Tenant Overrides (5)]                         │
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Task Sequence                                    [+ Add Task]│ │
│ ├─────────────────────────────────────────────────────────────┤ │
│ │                                                              │ │
│ │ 1. Research                                      [Edit] [×]  │ │
│ │    Agent: research_specialist                               │ │
│ │    Prompt: research/company_context.md                      │ │
│ │    Tools: rag_tool, perplexity_tool                         │ │
│ │                                                              │ │
│ │ 2. Generate Post                                 [Edit] [×]  │ │
│ │    Agent: copywriter                                        │ │
│ │    Prompt: copywriter/linkedin_post.md                      │ │
│ │    Tools: rag_tool                                          │ │
│ │                                                              │ │
│ │ 3. Compliance Review                             [Edit] [×]  │ │
│ │    Agent: compliance_specialist                             │ │
│ │    Prompt: compliance/review.md                             │ │
│ │    Tools: rag_tool                                          │ │
│ │                                                              │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Input Schema                                                 │ │
│ ├─────────────────────────────────────────────────────────────┤ │
│ │ Required: brand_name, target_audience, main_message         │ │
│ │ Optional: tone, hashtags_count, cta                         │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Output Format                                                │ │
│ ├─────────────────────────────────────────────────────────────┤ │
│ │ Content Type: linkedin_post                                 │ │
│ │ Display Type: linkedin_post                                 │ │
│ │ Metadata: hashtags, cta, word_count, compliance_status      │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ [Preview YAML] [Test Workflow] [Save Changes]                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### 3. Workflow Tenant Overrides View

```
┌─────────────────────────────────────────────────────────────────┐
│ ← Back to Workflow                                              │
├─────────────────────────────────────────────────────────────────┤
│ LinkedIn Post Generator - Tenant Overrides                       │
│                                                                  │
│ Select Tenant: [ACME Corp ▼]                    [+ New Override]│
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ ACME Corp Override                          [Delete Override]│ │
│ ├─────────────────────────────────────────────────────────────┤ │
│ │                                                              │ │
│ │ Task Sequence (4 tasks - 1 added)                           │ │
│ │                                                              │ │
│ │ 1. Research                                      [Edit] [×]  │ │
│ │    Agent: research_specialist                               │ │
│ │    Prompt: research/company_context.md                      │ │
│ │    Tools: rag_tool, perplexity_tool                         │ │
│ │                                                              │ │
│ │ 2. Generate Post                                 [Edit] [×]  │ │
│ │    Agent: copywriter                                        │ │
│ │    Prompt: copywriter/linkedin_post.md                      │ │
│ │    Tools: rag_tool                                          │ │
│ │                                                              │ │
│ │ 3. SEO Optimization                              [Edit] [×]  │ │
│ │    Agent: seo_specialist                    🆕 CUSTOM TASK  │ │
│ │    Prompt: seo/optimize_linkedin.md                         │ │
│ │    Tools: rag_tool                                          │ │
│ │                                                              │ │
│ │ 4. Compliance Review                             [Edit] [×]  │ │
│ │    Agent: compliance_specialist                             │ │
│ │    Prompt: compliance/review.md                             │ │
│ │    Tools: rag_tool                                          │ │
│ │                                                              │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ [Preview YAML] [Test Workflow] [Save Changes]                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### 4. Agent List View

```
┌─────────────────────────────────────────────────────────────────┐
│ Agents                                                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ ┌──────────────────────────────────────────────────────────┐   │
│ │ ✍️ Copywriter Specialist                      [Edit] [⚙️] │   │
│ │ Expert in creating engaging, persuasive content           │   │
│ │ Model: claude-3-sonnet • Tenants with overrides: 12      │   │
│ └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│ ┌──────────────────────────────────────────────────────────┐   │
│ │ 🔍 Research Specialist                        [Edit] [⚙️] │   │
│ │ Expert in gathering and analyzing information             │   │
│ │ Model: gpt-4-turbo • Tenants with overrides: 5           │   │
│ └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│ ┌──────────────────────────────────────────────────────────┐   │
│ │ 📚 RAG Specialist                             [Edit] [⚙️] │   │
│ │ Expert in retrieving and using company knowledge          │   │
│ │ Model: gpt-4-turbo • Tenants with overrides: 3           │   │
│ └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│ ┌──────────────────────────────────────────────────────────┐   │
│ │ ✅ Compliance Specialist                      [Edit] [⚙️] │   │
│ │ Expert in content compliance and brand guidelines         │   │
│ │ Model: claude-3-sonnet • Tenants with overrides: 8       │   │
│ └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### 5. Agent Detail View (Generic)

```
┌─────────────────────────────────────────────────────────────────┐
│ ← Back to Agents                                                │
├─────────────────────────────────────────────────────────────────┤
│ Copywriter Specialist                                            │
│ Expert in creating engaging, persuasive content                  │
│                                                                  │
│ [Generic Config] [Tenant Overrides (12)]                        │
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ System Prompt                                        [Edit] │ │
│ ├─────────────────────────────────────────────────────────────┤ │
│ │ You are an expert copywriter with 10+ years of experience. │ │
│ │                                                              │ │
│ │ Your expertise includes:                                    │ │
│ │ - Crafting compelling narratives                            │ │
│ │ - Understanding target audience psychology                  │ │
│ │ - Writing in various tones and styles                       │ │
│ │ - SEO optimization                                          │ │
│ │ - Brand voice consistency                                   │ │
│ │                                                              │ │
│ │ You always:                                                 │ │
│ │ - Focus on clarity and impact                               │ │
│ │ - Use data-driven insights                                  │ │
│ │ - Adapt to brand voice                                      │ │
│ │ - Follow best practices for the content type                │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Goal                                                 [Edit] │ │
│ ├─────────────────────────────────────────────────────────────┤ │
│ │ Create high-quality, engaging content that resonates with  │ │
│ │ the target audience                                         │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Backstory                                            [Edit] │ │
│ ├─────────────────────────────────────────────────────────────┤ │
│ │ You've worked with Fortune 500 companies and startups      │ │
│ │ alike, crafting content that drives engagement and         │ │
│ │ conversions. You understand the nuances of different       │ │
│ │ platforms (LinkedIn, blogs, emails) and adapt your         │ │
│ │ writing accordingly.                                        │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Model Configuration                                  [Edit] │ │
│ ├─────────────────────────────────────────────────────────────┤ │
│ │ Provider: Anthropic                                         │ │
│ │ Model: claude-3-sonnet                                      │ │
│ │ Temperature: 0.7                                            │ │
│ │ Max Tokens: 2000                                            │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Tools                                                [Edit] │ │
│ ├─────────────────────────────────────────────────────────────┤ │
│ │ ✅ RAG Tool (Knowledge Base Search)                         │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ [Preview Agent] [Test with Sample Task] [Save Changes]          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### 6. Agent Tenant Override View

```
┌─────────────────────────────────────────────────────────────────┐
│ ← Back to Agent                                                 │
├─────────────────────────────────────────────────────────────────┤
│ Copywriter Specialist - Tenant Overrides                         │
│                                                                  │
│ Select Tenant: [ACME Corp ▼]                    [+ New Override]│
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ ACME Corp Override                          [Delete Override]│ │
│ ├─────────────────────────────────────────────────────────────┤ │
│ │                                                              │ │
│ │ System Prompt (OVERRIDDEN)                          [Edit]  │ │
│ │ ┌──────────────────────────────────────────────────────┐   │ │
│ │ │ You are ACME Corp's copywriter. ACME is a B2B SaaS  │   │ │
│ │ │ company focused on AI automation.                   │   │ │
│ │ │                                                      │   │ │
│ │ │ Always emphasize:                                   │   │ │
│ │ │ - ROI and data-driven results                       │   │ │
│ │ │ - AI automation benefits                            │   │ │
│ │ │ - Technical credibility                             │   │ │
│ │ │                                                      │   │ │
│ │ │ Tone: Authoritative but approachable                │   │ │
│ │ └──────────────────────────────────────────────────────┘   │ │
│ │                                                              │ │
│ │ Goal (OVERRIDDEN)                                   [Edit]  │ │
│ │ ┌──────────────────────────────────────────────────────┐   │ │
│ │ │ Create content that positions ACME as a thought     │   │ │
│ │ │ leader in AI automation                             │   │ │
│ │ └──────────────────────────────────────────────────────┘   │ │
│ │                                                              │ │
│ │ Backstory (Using Generic)                           [Edit]  │ │
│ │ ┌──────────────────────────────────────────────────────┐   │ │
│ │ │ You've worked with Fortune 500 companies...         │   │ │
│ │ └──────────────────────────────────────────────────────┘   │ │
│ │                                                              │ │
│ │ Model Configuration (OVERRIDDEN)                    [Edit]  │ │
│ │ ┌──────────────────────────────────────────────────────┐   │ │
│ │ │ Provider: Anthropic                                 │   │ │
│ │ │ Model: claude-3-opus  🆕 UPGRADED                   │   │ │
│ │ │ Temperature: 0.8                                    │   │ │
│ │ │ Max Tokens: 2000                                    │   │ │
│ │ └──────────────────────────────────────────────────────┘   │ │
│ │                                                              │ │
│ │ Tools (Using Generic)                               [Edit]  │ │
│ │ ┌──────────────────────────────────────────────────────┐   │ │
│ │ │ ✅ RAG Tool (Knowledge Base Search)                 │   │ │
│ │ └──────────────────────────────────────────────────────┘   │ │
│ │                                                              │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ [Preview Agent] [Test with Sample Task] [Save Changes]          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### 7. Tool List View

```
┌─────────────────────────────────────────────────────────────────┐
│ Tools                                                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ ┌──────────────────────────────────────────────────────────┐   │
│ │ 📚 RAG Tool                                   [Edit] [⚙️] │   │
│ │ Search company knowledge base using semantic search       │   │
│ │ Status: Active • Tenants configured: 25                   │   │
│ └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│ ┌──────────────────────────────────────────────────────────┐   │
│ │ 🌐 Perplexity Tool                            [Edit] [⚙️] │   │
│ │ Search the web for recent information                     │   │
│ │ Status: Active • Tenants configured: 18                   │   │
│ └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│ ┌──────────────────────────────────────────────────────────┐   │
│ │ 🔍 Serper Tool                                [Edit] [⚙️] │   │
│ │ Google search API for web research                        │   │
│ │ Status: Active • Tenants configured: 12                   │   │
│ └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│ ┌──────────────────────────────────────────────────────────┐   │
│ │ 🎨 Image Generation Tool                      [Edit] [⚙️] │   │
│ │ Generate images using AI                                  │   │
│ │ Status: Beta • Tenants configured: 3                      │   │
│ └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### 8. Tool Detail View

```
┌─────────────────────────────────────────────────────────────────┐
│ ← Back to Tools                                                 │
├─────────────────────────────────────────────────────────────────┤
│ RAG Tool                                                         │
│ Search company knowledge base using semantic search              │
│                                                                  │
│ [Generic Config] [Tenant Configs (25)]                          │
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Description (for LLM)                                [Edit] │ │
│ ├─────────────────────────────────────────────────────────────┤ │
│ │ Search company knowledge base for relevant information     │ │
│ │ using semantic search. Use this when you need to retrieve  │ │
│ │ company-specific information, brand guidelines, or         │ │
│ │ historical content.                                         │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Parameters                                                  │ │
│ ├─────────────────────────────────────────────────────────────┤ │
│ │ • query (string, required): The search query               │ │
│ │ • top_k (integer, optional): Number of results (default: 5)│ │
│ │ • filters (object, optional): Additional filters           │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Function Schema (JSON)                          [View Full] │ │
│ ├─────────────────────────────────────────────────────────────┤ │
│ │ {                                                           │ │
│ │   "type": "function",                                       │ │
│ │   "function": {                                             │ │
│ │     "name": "knowledge_base_search",                        │ │
│ │     "description": "Search company knowledge base...",      │ │
│ │     "parameters": {...}                                     │ │
│ │   }                                                         │ │
│ │ }                                                           │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ [Test Tool] [Save Changes]                                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 TECHNICAL REQUIREMENTS

### Frontend Requirements

#### Technology Stack
- **Framework:** React 18+ with TypeScript
- **State Management:** Zustand or React Query
- **UI Library:** Shadcn/ui or Material-UI
- **Form Handling:** React Hook Form + Zod validation
- **Code Editor:** Monaco Editor (for YAML/JSON editing)
- **Markdown Editor:** MDX Editor or similar (for prompts)

#### Key Components

1. **WorkflowEditor**
   - Drag-and-drop task reordering
   - Task configuration modal
   - YAML preview panel
   - Test workflow modal

2. **AgentEditor**
   - Rich text editor for system prompt
   - Model configuration selector
   - Tool multi-select
   - Preview panel

3. **ToolEditor**
   - Description editor
   - Parameter schema viewer
   - Test tool modal

4. **TenantSelector**
   - Dropdown with search
   - "All Tenants" vs specific tenant toggle
   - Override indicator badge

#### State Management

```typescript
// Workflow Store
interface WorkflowStore {
  workflows: Workflow[];
  selectedWorkflow: Workflow | null;
  selectedTenant: string | null;
  tenantOverrides: Map<string, WorkflowOverride>;
  
  loadWorkflows: () => Promise<void>;
  selectWorkflow: (id: string) => void;
  selectTenant: (id: string) => void;
  updateWorkflow: (workflow: Workflow) => Promise<void>;
  createTenantOverride: (tenantId: string, override: WorkflowOverride) => Promise<void>;
  deleteTenantOverride: (tenantId: string) => Promise<void>;
}

// Agent Store
interface AgentStore {
  agents: Agent[];
  selectedAgent: Agent | null;
  selectedTenant: string | null;
  tenantOverrides: Map<string, AgentOverride>;
  
  loadAgents: () => Promise<void>;
  selectAgent: (id: string) => void;
  selectTenant: (id: string) => void;
  updateAgent: (agent: Agent) => Promise<void>;
  createTenantOverride: (tenantId: string, override: AgentOverride) => Promise<void>;
  deleteTenantOverride: (tenantId: string) => Promise<void>;
}

// Tool Store
interface ToolStore {
  tools: Tool[];
  selectedTool: Tool | null;
  selectedTenant: string | null;
  tenantConfigs: Map<string, ToolConfig>;
  
  loadTools: () => Promise<void>;
  selectTool: (id: string) => void;
  selectTenant: (id: string) => void;
  updateTool: (tool: Tool) => Promise<void>;
  createTenantConfig: (tenantId: string, config: ToolConfig) => Promise<void>;
  deleteTenantConfig: (tenantId: string) => Promise<void>;
}
```

---

### Backend Requirements

#### API Endpoints

##### Workflow Endpoints

```
GET    /api/v1/admin/workflows
GET    /api/v1/admin/workflows/{workflow_id}
PUT    /api/v1/admin/workflows/{workflow_id}
GET    /api/v1/admin/workflows/{workflow_id}/tenants/{tenant_id}/override
POST   /api/v1/admin/workflows/{workflow_id}/tenants/{tenant_id}/override
PUT    /api/v1/admin/workflows/{workflow_id}/tenants/{tenant_id}/override
DELETE /api/v1/admin/workflows/{workflow_id}/tenants/{tenant_id}/override
POST   /api/v1/admin/workflows/{workflow_id}/test
```

##### Agent Endpoints

```
GET    /api/v1/admin/agents
GET    /api/v1/admin/agents/{agent_id}
PUT    /api/v1/admin/agents/{agent_id}
GET    /api/v1/admin/agents/{agent_id}/tenants/{tenant_id}/override
POST   /api/v1/admin/agents/{agent_id}/tenants/{tenant_id}/override
PUT    /api/v1/admin/agents/{agent_id}/tenants/{tenant_id}/override
DELETE /api/v1/admin/agents/{agent_id}/tenants/{tenant_id}/override
POST   /api/v1/admin/agents/{agent_id}/test
```

##### Tool Endpoints

```
GET    /api/v1/admin/tools
GET    /api/v1/admin/tools/{tool_id}
PUT    /api/v1/admin/tools/{tool_id}
GET    /api/v1/admin/tools/{tool_id}/tenants/{tenant_id}/config
POST   /api/v1/admin/tools/{tool_id}/tenants/{tenant_id}/config
PUT    /api/v1/admin/tools/{tool_id}/tenants/{tenant_id}/config
DELETE /api/v1/admin/tools/{tool_id}/tenants/{tenant_id}/config
POST   /api/v1/admin/tools/{tool_id}/test
```

#### Request/Response Schemas

##### Get Workflow

```typescript
// GET /api/v1/admin/workflows/{workflow_id}

Response: {
  workflow_id: string;
  name: string;
  description: string;
  version: string;
  input_schema: {
    required: string[];
    optional: string[];
  };
  tasks: Array<{
    task_id: string;
    name: string;
    agent_id: string;
    prompt_template: string;
    input_mapping: Record<string, string>;
    tools: string[];
    output_key: string;
  }>;
  output_format: {
    content_type: string;
    display_type: string;
    metadata: string[];
  };
  tenant_overrides_count: number;
}
```

##### Create Tenant Workflow Override

```typescript
// POST /api/v1/admin/workflows/{workflow_id}/tenants/{tenant_id}/override

Request: {
  custom_tasks: Array<{
    task_id: string;
    name: string;
    agent_id: string;
    prompt_template: string;
    input_mapping: Record<string, string>;
    tools: string[];
    output_key: string;
  }>;
  custom_output_format?: {
    content_type: string;
    display_type: string;
    metadata: string[];
  };
}

Response: {
  id: string;
  tenant_id: string;
  workflow_id: string;
  custom_tasks: Array<...>;
  custom_output_format: {...};
  created_at: string;
  updated_at: string;
}
```

##### Get Agent

```typescript
// GET /api/v1/admin/agents/{agent_id}

Response: {
  agent_id: string;
  name: string;
  description: string;
  system_prompt: string;
  goal: string;
  backstory: string;
  model_config: {
    provider: string;
    model: string;
    temperature: number;
    max_tokens: number;
    top_p: number;
  };
  tools: string[];
  metadata: Record<string, any>;
  tenant_overrides_count: number;
}
```

##### Create Tenant Agent Override

```typescript
// POST /api/v1/admin/agents/{agent_id}/tenants/{tenant_id}/override

Request: {
  custom_system_prompt?: string;
  custom_goal?: string;
  custom_backstory?: string;
  model_config?: {
    provider?: string;
    model?: string;
    temperature?: number;
    max_tokens?: number;
    top_p?: number;
  };
  tools?: string[];
}

Response: {
  id: string;
  tenant_id: string;
  agent_id: string;
  custom_system_prompt: string | null;
  custom_goal: string | null;
  custom_backstory: string | null;
  model_config: {...} | null;
  tools: string[] | null;
  created_at: string;
  updated_at: string;
}
```

---

## 📊 DATABASE CHANGES

### New Tables

None required - using existing tables:
- `tenant_workflow_configs`
- `tenant_agent_configs`
- `tool_configs`

### New Indexes

```sql
-- For faster admin panel queries
CREATE INDEX idx_tenant_workflow_configs_workflow ON tenant_workflow_configs(workflow_id);
CREATE INDEX idx_tenant_agent_configs_agent ON tenant_agent_configs(agent_id);
CREATE INDEX idx_tool_configs_tool ON tool_configs(tool_id);
```

---

## 🔐 SECURITY & PERMISSIONS

### Role-Based Access Control

```typescript
enum AdminRole {
  SUPER_ADMIN = "super_admin",  // Can edit generic + all tenant configs
  TENANT_ADMIN = "tenant_admin", // Can edit only their tenant configs
  VIEWER = "viewer"              // Read-only access
}

// Permission matrix
const permissions = {
  super_admin: {
    workflows: { read: true, edit_generic: true, edit_tenant: true },
    agents: { read: true, edit_generic: true, edit_tenant: true },
    tools: { read: true, edit_generic: true, edit_tenant: true }
  },
  tenant_admin: {
    workflows: { read: true, edit_generic: false, edit_tenant: true },
    agents: { read: true, edit_generic: false, edit_tenant: true },
    tools: { read: true, edit_generic: false, edit_tenant: true }
  },
  viewer: {
    workflows: { read: true, edit_generic: false, edit_tenant: false },
    agents: { read: true, edit_generic: false, edit_tenant: false },
    tools: { read: true, edit_generic: false, edit_tenant: false }
  }
};
```

### Audit Logging

All changes MUST be logged:

```sql
CREATE TABLE admin_audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    action VARCHAR(50) NOT NULL,  -- 'create', 'update', 'delete'
    resource_type VARCHAR(50) NOT NULL,  -- 'workflow', 'agent', 'tool'
    resource_id VARCHAR(255) NOT NULL,
    tenant_id UUID,  -- NULL for generic config changes
    changes JSONB NOT NULL,  -- Before/after values
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_admin_audit_log_user ON admin_audit_log(user_id);
CREATE INDEX idx_admin_audit_log_resource ON admin_audit_log(resource_type, resource_id);
CREATE INDEX idx_admin_audit_log_created ON admin_audit_log(created_at DESC);
```

---

## ✅ ACCEPTANCE CRITERIA

### Must Have (P0)

- [ ] Admin can view all workflows, agents, and tools
- [ ] Admin can edit generic workflow task sequences
- [ ] Admin can create tenant-specific workflow overrides
- [ ] Admin can edit generic agent system prompts, goals, backstories
- [ ] Admin can create tenant-specific agent overrides
- [ ] Admin can edit tool descriptions
- [ ] Admin can create tenant-specific tool configurations
- [ ] All changes are saved to database correctly
- [ ] All changes are logged in audit log
- [ ] UI is responsive and works on desktop (tablet/mobile not required)
- [ ] Form validation prevents invalid configurations
- [ ] Error handling shows clear error messages

### Should Have (P1)

- [ ] YAML preview for workflows
- [ ] Test workflow execution with sample input
- [ ] Test agent execution with sample task
- [ ] Test tool execution with sample parameters
- [ ] Search/filter workflows, agents, tools
- [ ] Bulk operations (e.g., apply override to multiple tenants)
- [ ] Version history for configurations
- [ ] Rollback to previous version

### Nice to Have (P2)

- [ ] Visual workflow builder (drag-and-drop)
- [ ] AI-assisted prompt generation
- [ ] Configuration templates (e.g., "E-commerce copywriter")
- [ ] Analytics dashboard (usage stats per workflow/agent/tool)
- [ ] Export/import configurations (JSON/YAML)
- [ ] Collaboration features (comments, approvals)

---

## 📅 IMPLEMENTATION PLAN

### Phase 1: Backend API (Week 1)
- [ ] Implement workflow endpoints
- [ ] Implement agent endpoints
- [ ] Implement tool endpoints
- [ ] Add audit logging
- [ ] Add RBAC middleware
- [ ] Write API tests

### Phase 2: Frontend Core (Week 1-2)
- [ ] Setup project structure
- [ ] Implement workflow list/detail views
- [ ] Implement agent list/detail views
- [ ] Implement tool list/detail views
- [ ] Implement tenant selector
- [ ] Implement form validation

### Phase 3: Advanced Features (Week 2)
- [ ] Implement YAML preview
- [ ] Implement test execution modals
- [ ] Implement override management
- [ ] Add error handling
- [ ] Add loading states
- [ ] Polish UI/UX

### Phase 4: Testing & Deployment (Week 2)
- [ ] End-to-end testing
- [ ] User acceptance testing
- [ ] Performance testing
- [ ] Documentation
- [ ] Deploy to staging
- [ ] Deploy to production

---

## 🎯 SUCCESS CRITERIA

### Functional
- [ ] All acceptance criteria met
- [ ] Zero critical bugs
- [ ] < 5 minor bugs
- [ ] All tests passing (unit + integration + e2e)

### Performance
- [ ] Page load time < 2s
- [ ] API response time < 500ms (p95)
- [ ] Form submission < 1s

### UX
- [ ] User can complete workflow customization in < 5 minutes
- [ ] User can complete agent customization in < 3 minutes
- [ ] User satisfaction score > 4/5

---

## 📝 NOTES

### Dependencies
- Requires `AGENTIC_AI_CORE` implementation to be complete
- Requires database schema from Fylle Core Pulse
- Requires authentication/authorization system

### Risks
- **Complexity:** Managing generic + tenant-specific configs can be confusing
  - **Mitigation:** Clear UI indicators (badges, colors) for overrides
- **Performance:** Loading all workflows/agents/tools could be slow
  - **Mitigation:** Pagination, lazy loading, caching
- **Data integrity:** Invalid configurations could break workflows
  - **Mitigation:** Strong validation, test execution before save

### Future Enhancements
- AI-powered configuration suggestions
- A/B testing for different agent configurations
- Multi-language support for prompts
- Integration with version control (Git)

---

**End of Feature Request**
