# CGS_2

## Overview
CGS_2 is a multi‑agent content generation system 
- A FastAPI backend that orchestrates workflows and agents
- YAML‑configured agents and workflows per client profile (e.g., Siebert)
- Tooling for real‑time research (Perplexity), RAG over client knowledge bases (Supabase), and web search
- A React frontend for triggering runs and inspecting outputs

### High‑level architecture
- API layer: FastAPI (api/rest), WebSocket updates, tracking to Supabase
- Orchestration: Workflow handlers + AgentExecutor (tools registry, tool call parsing, logging)
- Agents: YAML profiles (data/profiles/*/agents/*.yaml) with system messages, tools, and parameters
- Tools:
  - PerplexityResearchTool (real‑time research via Perplexity API)
  - RAGTool (Supabase KB retrieval and similarity search)
  - WebSearchTool (generic/financial search)
- Storage & Tracking: Supabase (optional), local filesystem fallback
- Frontend: web/react-app (local dev with proxy to API)

Reference code:
- core/infrastructure/workflows/handlers/* (workflow business logic)
- core/infrastructure/orchestration/agent_executor.py (tool invocation model)
- core/infrastructure/tools/* (Perplexity, RAG, WebSearch)
- core/infrastructure/config/settings.py (env settings)

---

## Quick start

### 1) Backend (local script)
Prerequisites: Python 3.11+, virtualenv recommended.

```bash
# From repo root
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start backend (defaults to http://localhost:8000)
python3 start_backend.py
```

### 2) Backend (Docker Compose)
```bash
# Build and run API, Postgres and Chroma services
docker-compose up -d --build
# API will be exposed at http://localhost:8000
```

### 3) Frontend (React)
```bash
cd web/react-app
npm install
npm start
# Dev server at http://localhost:3000
```

> Note: The frontend dev server typically proxies API calls to the backend. If you change API_PORT, update the proxy setting in web/react-app/package.json accordingly.

---

## Configuration (.env)
Create a .env file in the repository root. The backend reads all keys via Pydantic Settings (core/infrastructure/config/settings.py).

Minimum recommended variables:

```env
# App & API
ENVIRONMENT=development
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=replace-with-a-secure-random-string

# AI Providers (set at least one)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
DEEPSEEK_API_KEY=
GEMINI_API_KEY=

# Perplexity (for research tool)
PERPLEXITY_API_KEY=

# Supabase (optional but recommended for tracking & KB)
USE_SUPABASE=true
SUPABASE_URL=
SUPABASE_ANON_KEY=

# Database (when not using docker-compose Postgres)
# DATABASE_URL=sqlite:///./cgsref.db

# CORS (optional)
# CORS_ALLOWED_ORIGINS=http://localhost:3000

# Premium research source defaults (optional, comma-separated URLs)
# PREMIUM_DEFAULT_SOURCES=https://www.bloomberg.com,https://www.reuters.com,https://www.wsj.com
```

### Provider models and temps
- Default provider/model/temperature can be overridden via env:
  - DEFAULT_PROVIDER, DEFAULT_MODEL, DEFAULT_TEMPERATURE, MAX_TOKENS

---

## Running a newsletter workflow (Siebert)
- Client profile YAML: data/profiles/siebert
- Key agents: copywriter, compliance_specialist, research_specialist
- Handler: core/infrastructure/workflows/handlers/siebert_premium_newsletter_handler.py
- Trigger via frontend (Start Run) or POST /api/v1/content/generate

Example request (simplified):
```bash
curl -X POST http://localhost:8000/api/v1/content/generate \
  -H 'Content-Type: application/json' \
  -d '{
    "topic": "Finance News of the last 7 Days",
    "workflow_type": "siebert_premium_newsletter",
    "client_profile": "siebert",
    "provider": "anthropic",
    "model": "claude-opus-4-20250514",
    "temperature": 0.7,
    "include_sources": true
  }'
```

---

## Requirements check
We reviewed runtime imports vs requirements.txt. Suggested updates:
- The code imports aiohttp in PerplexityResearchTool → add: `aiohttp>=3.9.0`
- The diagnostics script imports requests → add: `requests>=2.31.0`

Current requirements.txt includes FastAPI, Uvicorn, httpx, Supabase, SQLAlchemy, LangChain, OpenAI/Anthropic/Gemini SDKs, pytest, and dev tools. If you want, we can update requirements.txt to include the two missing dependencies.

---

## Testing
```bash
pytest -q
# Or target specific tests, e.g.
pytest test_siebert_workflow.py -q
```

---

## Troubleshooting
- Backend not responding? Check logs from start_backend.py or `docker-compose logs -f api`.
- ECONNREFUSED from frontend? Ensure API_PORT matches the proxy in web/react-app/package.json.
- Supabase issues? Verify SUPABASE_URL and SUPABASE_ANON_KEY are set and reachable.
- No providers configured? Set at least one of OPENAI_API_KEY / ANTHROPIC_API_KEY / DEEPSEEK_API_KEY / GEMINI_API_KEY.

