# CGS_2

## Overview
CGS_2 è un sistema di content generation multi‑agent con:
- Backend FastAPI che orchestra workflow e agent
- Agent e workflow configurati via YAML per profilo cliente (data/profiles/<client>/agents/*.yaml)
- Tooling per ricerche real‑time (Perplexity), RAG su knowledge base (Supabase) e web search
- Frontend React per avviare run e ispezionare output

### Architettura (alto livello)
- API layer: FastAPI (api/rest), WebSocket, tracking opzionale su Supabase
- Orchestrazione: Workflow handler + AgentExecutor (registry tool, parsing tool call, logging/costi)
- Agents: YAML con system_message, tools, goal/backstory
- Prompt: template Markdown per task (core/prompts/*.md), renderizzati con Jinja2 se disponibile
- Storage & Tracking: Supabase (opzionale) o filesystem locale
- Frontend: web/react-app (dev locale)

Riferimenti codice:
- core/infrastructure/workflows/handlers/* (logica di workflow)
- core/infrastructure/workflows/templates/*.json (task graph e mapping agent)
- core/infrastructure/orchestration/agent_executor.py (esecuzione agent + system message)
- core/infrastructure/orchestration/prompt_builder.py (render prompt)
- core/infrastructure/tools/* (Perplexity, RAG, WebSearch)
- core/infrastructure/config/settings.py (settings/env)

---

## Avvio rapido

### 1) Backend (locale)
Prerequisiti: Python 3.11+, virtualenv consigliato.

```bash
# Da root repository
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Avvia backend (default http://localhost:8000)
python3 start_backend.py
```

Endpoint utili:
- Health: http://localhost:8000/health
- System info: http://localhost:8000/api/v1/system/info
- OpenAPI docs: http://localhost:8000/docs

Porte backend: 8000 (override via .env: API_HOST, API_PORT)

### 2) Frontend (React)
```bash
cd web/react-app
npm install
# Configurare l’URL dell’API nel .env del frontend
# web/react-app/.env
# REACT_APP_API_URL=http://localhost:8000
npm start
# Dev server su http://localhost:3000
```

Nota: il frontend NON usa il campo "proxy" nel package.json; usa REACT_APP_API_URL. Se cambi porta/host dell’API, aggiorna web/react-app/.env.

### 3) Docker (opzionale)
Se usi docker-compose, l’API è tipicamente esposta su http://localhost:8000.

---

## Configurazione (.env)
Crea un file .env nella root del repository. Il backend carica i valori con Pydantic Settings.

Minimo consigliato:

```env
# App & API
ENVIRONMENT=development
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=replace-with-a-secure-random-string

# Provider AI (configura almeno uno)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
DEEPSEEK_API_KEY=
GEMINI_API_KEY=

# Perplexity (ricerche real‑time)
PERPLEXITY_API_KEY=

# Supabase (tracking e KB opzionali)
USE_SUPABASE=true
SUPABASE_URL=
SUPABASE_ANON_KEY=

# Database (se non usi Postgres via docker-compose)
# DATABASE_URL=sqlite:///./cgsref.db

# CORS (lista separata da virgole)
# CORS_ALLOWED_ORIGINS=http://localhost:3000

# Fonti premium di default (lista separata da virgole)
# PREMIUM_DEFAULT_SOURCES=https://www.bloomberg.com,https://www.reuters.com,https://www.wsj.com
```

Provider di default e token:
- Override via env: DEFAULT_PROVIDER, DEFAULT_MODEL, DEFAULT_TEMPERATURE, MAX_TOKENS

### Configurazione frontend
Crea web/react-app/.env:
```
REACT_APP_API_URL=http://localhost:8000
```

---

## Logging di default (più silenzioso)

- Di default il backend lavora con log più puliti quando DEBUG=false (vedi .env). In questa modalità:
  - httpx e uvicorn.access sono portati a WARNING (meno rumore nelle richieste HTTP)
  - i provider senza API key vengono loggati a DEBUG in fase di discovery; compaiono WARNING solo se richiedi esplicitamente quel provider senza chiave
  - nei workflow, alcune condizioni aspettate passano a INFO/DEBUG (es. nessuna variabile di template sostituita, fallback agent per ruolo)
  - Anthropic: se la SDK richiede streaming, facciamo retry automatico in streaming e logghiamo INFO; ERROR solo se fallisce anche lo stream
  - Il reporter calcola la lunghezza dell’output finale usando final_output oppure un fallback per-task (niente più "Output Length: 0" fuorviante)

### Come abilitare/disabilitare la verbosità
- Verboso (debug): imposta `DEBUG=true` nel tuo `.env` oppure usa lo starter di debug dedicato.
- Silenzioso (default): imposta `DEBUG=false` nel tuo `.env` oppure avvia temporaneamente così:

```bash
DEBUG=false uvicorn api.rest.main:app --host 0.0.0.0 --port 8000 --reload
```

### Avvio in debug esplicito (developer)
- Per sessioni di debug dettagliate puoi usare lo script dedicato:

```bash
python3 start_backend_debug.py
```

Questo imposta livelli di log più verbosi su FastAPI, moduli core e provider.


## Come funzionano workflow, task, agent e system message

### Esempio: workflow "enhanced_article"
- Definito in: core/infrastructure/workflows/templates/enhanced_article.json
- Sequenza task → agent:
  - task1_brief → agent: rag_specialist → prompt: core/prompts/enhanced_article_task1_brief.md
  - task2_research → agent: web_searcher → prompt: core/prompts/enhanced_article_task2_research.md
  - task3_content → agent: enhanced_article_writer → prompt: core/prompts/enhanced_article_task3_content.md
  - task4_compliance_review → agent: enhanced_article_compliance_specialist → prompt: core/prompts/enhanced_article_task4_compliance_review.md

### Nuovo workflow: "siebert_newsletter_html"
- Template: core/infrastructure/workflows/templates/siebert_newsletter_html.json
- Handler: core/infrastructure/workflows/handlers/siebert_newsletter_html_handler.py
- Task sequence (stesso stack del Premium Siebert, con un task finale extra):
  1. **RAG brand setup** → agent `rag_specialist`
  2. **Perplexity research** → agent `research_specialist`
  3. **Newsletter assembly (markdown 8 sezioni)** → agent `copywriter`
  4. **Compliance review** → agent `compliance_specialist`
  5. **HTML Builder** → nuovo agent `html_email_builder` che converte il markdown approvato in un singolo `<div>` con soli inline style
- Il task 5 riceve anche `html_design_system_instructions` con palette, spacing, layout (numeri in tabella 2×2, quote box, community violet, footer scuro, ecc.).
- Guardrail automatici: il handler valida assenza di `<html>/<head>/<body>/<style>/<script>`, assenza di class/id, presenza `max-width: 600px`, niente em dash e link solo http/https/mailto. Se qualcosa rompe le regole il workflow fallisce.
- Output nella tracking: `final_output` + `metadata.html_email_container` (div pronto da incollare) e `metadata.compliance_markdown` (archivio markdown post-compliance).
- Frontend: nel pannello risultati compaiono pulsanti **Copy HTML**, **Download .html**, e anteprima HTML + markdown di archivio.
- HubSpot/Mailchimp: copia/incolla direttamente il contenuto HTML (unico `<div>`). Nessun `<body>` o CSS esterno, quindi gli editor WYSIWYG non mostrano warning.

### Dove sono definiti gli agent
- YAML per profilo cliente: data/profiles/<client>/agents/*.yaml (es. data/profiles/default/agents/)
- Ogni file include: name, role, system_message, goal, backstory, tools, metadata

### Composizione della system message (runtime)
Durante l’esecuzione di un task, AgentExecutor costruisce la system message così:
1) Base: `agent.system_message` dal file YAML (se non presente, fallback per ruolo)
2) Append: `backstory` e `goal` dell’agent (se presenti)
3) Append: contesto dinamico (es. client_profile, target_audience)
4) Se l’agent ha tools, aggiunge elenco tool e FORMATO esatto per invocare i tool (es. `[rag_get_client_content] client [/rag_get_client_content]`)

Il prompt utente del task è renderizzato dal template Markdown con il context (Jinja2 se disponibile), tramite `prompt_builder`.

---

## Esecuzione via API (esempio)
```bash
curl -X POST http://localhost:8000/api/v1/content/generate \
  -H 'Content-Type: application/json' \
  -d '{
    "topic": "Gen Z investing trends 2025",
    "workflow_type": "enhanced_article",
    "client_profile": "default",
    "provider": "openai",
    "model": "gpt-4o",
    "temperature": 0.7,
    "include_sources": true
  }'
```

---

## Requisiti (Python)
Le dipendenze principali sono in requirements.txt e coprono backend API, provider AI, RAG e tool:
- FastAPI, Uvicorn, Pydantic, pydantic-settings
- OpenAI/Anthropic/Gemini SDK, LangChain
- Supabase, SQLAlchemy, Alembic, ChromaDB
- httpx, aiofiles, websockets, requests, aiohttp
- Jinja2 (render dei prompt), typer, rich
- pytest e tool di sviluppo (black/isort/flake8/mypy/pre-commit)

Se aggiungi/aggiorni dipendenze, rigenera l’ambiente:
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Testing
```bash
pytest -q
# Oppure test mirati
pytest tests/test_workflows.py -q
```

---

## Troubleshooting
- Frontend: errore "REACT_APP_API_URL is not defined" → crea web/react-app/.env e imposta REACT_APP_API_URL
- CORS: imposta CORS_ALLOWED_ORIGINS in .env come lista separata da virgole (es. http://localhost:3000)
- Provider non configurati: imposta almeno una API key (OPENAI_API_KEY, ANTHROPIC_API_KEY, …)
- Supabase: verifica SUPABASE_URL e SUPABASE_ANON_KEY, e USE_SUPABASE=true


---

## Modelli e limiti token: context_window vs max_tokens

Per evitare errori 400 dai provider e rendere trasparente la capacità dei modelli, distinguiamo:
- context_window: capacità totale per richiesta (prompt + output). È informativa in UI.
- max_tokens (output): massimo di token di OUTPUT per singola chiamata API. È vincolante.

Comportamento nell’applicazione:
- Backend espone per ogni modello sia max_tokens (output cap) sia context_window (se disponibile) su GET /api/v1/content/providers.
- Frontend mostra la context window e consente di selezionare i “Max output tokens” fino al limite reale del modello.
- Ogni chiamata LLM nel workflow applica il cap di output selezionato; quindi il limite è per‑chiamata, configurato a livello di run.

Esempio rapida verifica endpoint modelli:
```bash
curl -s http://localhost:8000/api/v1/content/providers | jq '.'
```

Evitare 400 Invalid Request:
- Anche se la context window è molto ampia, i provider impongono un cap separato per l’output.
- Esempio: Anthropic claude-3-7-sonnet-20250219 → max output 64.000 token; chiedere 200.000 genera 400.
- Tenendo max_tokens entro i limiti del modello per ogni chiamata, il workflow non fallisce per eccesso di output.

Nota avanzata: è possibile introdurre lato backend un “clamp dinamico” (opzionale) per ridurre automaticamente l’output massimo in base alla lunghezza del prompt: effective_max = min(model_max_output, context_window − prompt_tokens − margine).

---

## Supabase tracking: abilitazione, tabelle e health check

Abilitazione:
- .env → USE_SUPABASE=true, SUPABASE_URL, SUPABASE_ANON_KEY.
- Il tracker viene creato automaticamente se le variabili sono presenti.

Tabelle utilizzate:
- workflow_runs: testate/chiuse le esecuzioni di workflow
- run_logs: log di run
- agent_executions: esecuzioni per agente/step
- run_documents: documenti usati dal RAG
- run_document_chunks: chunk RAG (opzionale)
- content_generations: contenuti finali salvati per la run

Health check rapido (read‑only):
```bash
python3 - <<'PY'
from core.infrastructure.database.supabase_tracker import get_tracker
trk = get_tracker()
assert trk is not None, 'Tracker non inizializzato'
print('Tracker OK')
print('workflow_runs sample:', trk.client.table('workflow_runs').select('id').limit(1).execute().data)
print('run_logs sample:', trk.client.table('run_logs').select('id').limit(1).execute().data)
PY
```

Questo verifica connettività e permessi di lettura senza scrivere dati. Per un test end‑to‑end con insert/update, avvia un run reale oppure chiama i metodi del tracker (start_workflow_run → add_log → complete_workflow_run) su una run di test.
