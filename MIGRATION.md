# Migration Guide: Prompt Centralization & Prompt Builder

This guide explains the refactor introduced in this branch: centralized prompts, a single Prompt Builder, canonical tool names with aliases, YAML‑based agents, and declarative workflows.

## What changed (high level)
- Prompt templates moved to Markdown files per task (core/prompts/*.md)
- A centralized Prompt Builder renders templates with Jinja2 (fallback to simple substitution)
- Agents are defined in YAML per client profile (data/profiles/<client>/agents/*.yaml)
- System messages are composed at runtime (YAML.system_message + backstory + goal + context + tool instructions)
- Canonical tool names + aliases unify references across code, prompts, and YAML
- Workflows use templates (JSON) to map tasks → agent → prompt

## Components
- Prompt Builder: core/infrastructure/orchestration/prompt_builder.py
- Agent Executor: core/infrastructure/orchestration/agent_executor.py
- Tool names & aliases: core/infrastructure/tools/tool_names.py
- Tools: core/infrastructure/tools/*.py (rag, web_search, perplexity)
- Workflow templates: core/infrastructure/workflows/templates/*.json
- Workflow handlers: core/infrastructure/workflows/handlers/*
- Agents (YAML): data/profiles/<client>/agents/*.yaml
- Task prompts (Markdown): core/prompts/*.md

## System message composition (runtime)
At task execution time, AgentExecutor builds the final system message:
1) Base: agent.system_message from YAML (or role fallback)
2) Append: backstory and goal if present
3) Append: context hints (e.g., client_profile, target_audience)
4) Append: tool list and exact call format when the agent has tools

## Tool calls — canonical names and syntax
Canonical names (ToolNames):
- rag_get_client_content
- rag_search_content
- web_search (Serper/Google)
- perplexity_search (Perplexity)

Accepted aliases (for legacy prompts):
- research_premium_financial → perplexity_search
- research_client_sources → perplexity_search
- research_general_topic → perplexity_search
- research_financial_premium → perplexity_search
- web_search_financial → web_search

Exact call format parsed at runtime:
- [rag_get_client_content] client_name [/rag_get_client_content]
- [rag_get_client_content] client_name, document_name [/rag_get_client_content]
- [rag_search_content] client_name, search_query [/rag_search_content]
- [rag_search_content] search_query [/rag_search_content]  (defaults to client "siebert")
- [web_search] your search query [/web_search]
- [perplexity_search] your research query [/perplexity_search]

## Workflow example: enhanced_article
Template: core/infrastructure/workflows/templates/enhanced_article.json
- task1_brief → agent: rag_specialist → prompt: core/prompts/enhanced_article_task1_brief.md
- task2_research → agent: web_searcher → prompt: core/prompts/enhanced_article_task2_research.md
- task3_content → agent: enhanced_article_writer → prompt: core/prompts/enhanced_article_task3_content.md
- task4_compliance_review → agent: enhanced_article_compliance_specialist → prompt: core/prompts/enhanced_article_task4_compliance_review.md

## Migrating existing prompts
- Move/convert inline strings to Markdown in core/prompts/ (one file per task)
- Use Jinja2 placeholders for variables ({{topic}}, {{client_name}}, …)
- Replace legacy tool names with canonical names when editing (aliases still work)
- Keep prompts minimal and task‑focused; offload agent‑level guidance to YAML system_message

## Migrating agents
- Create/update YAML in data/profiles/<client>/agents/<agent>.yaml with:
  - name, role, system_message, goal, backstory, tools, metadata
- If a task uses a tool, prefer listing it in the agent’s tools so users see tool instructions in system message
- Keep client‑specific overrides in the client profile directory

## Backward compatibility
- Legacy tool names continue to work via ALIASES mapping
- Legacy workflows fallback path exists, but declarative templates are preferred
- AgentFactory logs fallbacks when resolving legacy names

## How to verify
Backend
- Create .venv and install: `pip install -r requirements.txt`
- Start API: `python start_backend.py` → http://localhost:8000
- Sanity: GET /health, GET /api/v1/system/info
- Execute: POST /api/v1/content/generate with workflow_type=enhanced_article

Frontend
- Set web/react-app/.env: `REACT_APP_API_URL=http://localhost:8000`
- `npm install && npm start` → http://localhost:3000

Tests
- `pytest -q` (add targeted tests for tool parsing and system message composition as needed)

## Coding guidelines (post‑refactor)
- Keep prompts minimal and declarative; avoid business logic in Markdown
- Centralize tool usage via canonical names and register once in AgentExecutor
- Prefer per‑client YAML agent overrides over hardcoded differences
- Add new tools under core/infrastructure/tools and map them in ToolNames (+optional aliases)
- Update README and MIGRATION when changing developer workflow

## Next steps (suggested PR sequence)
1) Refactor: Prompt centralization + Prompt Builder (this PR)
2) Prompt minimali per enhanced_article (+ add rag_search_content to analyst if used)
3) Normalizzazione agent naming (e.g., converge on perplexity_researcher)
4) Pulizia alias (remove legacy names after all prompts are migrated)

