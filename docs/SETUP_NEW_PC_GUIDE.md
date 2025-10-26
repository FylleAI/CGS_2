# 🖥️ Guida Setup Ambiente su Nuovo PC

**Data**: 2025-10-25  
**Progetto**: CGS_2 (Content Generation System v2)  
**Repository**: https://github.com/FylleAI/CGS_2.git

---

## 📍 Dove Sei Ora

### **Workspace Corrente**
```
📂 Location: /Users/davidescantamburlo/Desktop/Test Onboarding /CGS_2
📂 Repository Root: /Users/davidescantamburlo/Desktop/Test Onboarding /CGS_2
🌿 Branch: main
```

### **Struttura Progetto**
```
CGS_2/
├── 📁 onboarding/              # Onboarding microservice (Python/FastAPI)
│   ├── api/                    # REST endpoints
│   ├── application/            # Use cases & services
│   ├── domain/                 # Models & business logic
│   ├── infrastructure/         # Repositories, adapters
│   └── config/                 # Configuration
│
├── 📁 onboarding-frontend/     # Frontend React/TypeScript
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── services/           # API clients
│   │   └── types/              # TypeScript types
│   └── package.json
│
├── 📁 core/                    # Core CGS system
│   ├── application/            # Content generation use cases
│   ├── domain/                 # Content models
│   └── infrastructure/         # Workflows, agents, tools
│
├── 📁 docs/                    # Documentazione completa
│   ├── transparency/           # Transparency feature docs
│   ├── onboarding/             # Onboarding docs
│   ├── CARD_IMPLEMENTATION_STRATEGY.md
│   └── FEATURE_OVERVIEW_ESSENTIALS.md
│
├── 📁 .secrets/                # ⚠️ GITIGNORED - Credenziali GCP
│   └── startup-program-461116-e59705839bd1.json
│
├── .env                        # ⚠️ GITIGNORED - Variabili ambiente
├── .env.backup                 # Backup configurazione
├── docker-compose.yml          # Docker setup
├── requirements.txt            # Python dependencies
└── pyproject.toml              # Python project config
```

---

## 🚀 Setup su Nuovo PC - Guida Completa

### **Prerequisiti**

Prima di iniziare, assicurati di avere installato:

```bash
# 1. Python 3.11+
python --version  # Deve essere >= 3.11

# 2. Node.js 18+ e npm
node --version    # Deve essere >= 18
npm --version

# 3. Git
git --version

# 4. (Opzionale) Docker Desktop
docker --version
docker-compose --version
```

---

## 📥 Step 1: Clone Repository

```bash
# 1. Naviga nella cartella dove vuoi il progetto
cd ~/Desktop  # O qualsiasi altra cartella

# 2. Clona il repository
git clone https://github.com/FylleAI/CGS_2.git

# 3. Entra nella cartella
cd CGS_2

# 4. Verifica branch
git branch  # Dovresti essere su 'main'
```

---

## 🔐 Step 2: Configurare File `.env`

### **2.1: Copia Template**

```bash
# Il file .env è gitignored, quindi NON è nel repository
# Devi crearlo manualmente

# Opzione A: Copia da .env.backup (se esiste nel repo)
cp .env.backup .env

# Opzione B: Crea da zero
touch .env
```

### **2.2: Popola `.env` con Credenziali**

Apri `.env` con un editor e inserisci le seguenti variabili:

```bash
# =============================================================================
# APPLICATION SETTINGS
# =============================================================================
APP_NAME=CGSRef
APP_VERSION=1.0.0
ENVIRONMENT=development
DEBUG=true

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# =============================================================================
# AI PROVIDER API KEYS
# =============================================================================

# OpenAI (per GPT-4, embeddings)
OPENAI_API_KEY=sk-proj-YOUR_OPENAI_KEY_HERE

# Anthropic Claude (opzionale)
ANTHROPIC_API_KEY=sk-ant-YOUR_ANTHROPIC_KEY_HERE

# DeepSeek (opzionale)
DEEPSEEK_API_KEY=sk-YOUR_DEEPSEEK_KEY_HERE

# Google Gemini (per synthesis)
GEMINI_API_KEY=AIzaSy_YOUR_GEMINI_KEY_HERE

# Serper (per web search - opzionale)
SERPER_API_KEY=YOUR_SERPER_KEY_HERE

# Perplexity (per research)
PERPLEXITY_API_KEY=pplx-YOUR_PERPLEXITY_KEY_HERE

# =============================================================================
# DATABASE - SUPABASE
# =============================================================================

# Supabase Project URL
SUPABASE_URL=https://YOUR_PROJECT_ID.supabase.co

# Supabase Anon Key (public key)
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...YOUR_ANON_KEY

# Enable Supabase
USE_SUPABASE=true

# Local SQLite (fallback)
DATABASE_URL=sqlite:///./cgsref.db
DATABASE_ECHO=false

# =============================================================================
# FILE STORAGE
# =============================================================================
DATA_DIR=data
OUTPUT_DIR=data/output
PROFILES_DIR=data/profiles
WORKFLOWS_DIR=data/workflows
KNOWLEDGE_BASE_DIR=data/knowledge_base
CACHE_DIR=data/cache

# =============================================================================
# RAG SETTINGS
# =============================================================================
RAG_ENABLED=true
RAG_CHUNK_SIZE=1000
RAG_CHUNK_OVERLAP=200
RAG_MAX_RESULTS=5

# ChromaDB
CHROMA_HOST=localhost
CHROMA_PORT=8000
CHROMA_PERSIST_DIRECTORY=data/chroma

# =============================================================================
# LOGGING
# =============================================================================
LOG_LEVEL=INFO
LOG_FORMAT="%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# =============================================================================
# CONTENT GENERATION DEFAULTS
# =============================================================================
DEFAULT_PROVIDER=openai
DEFAULT_MODEL=gpt-4o
DEFAULT_TEMPERATURE=0.7

# =============================================================================
# WORKFLOW SETTINGS
# =============================================================================
WORKFLOW_TIMEOUT_SECONDS=600
MAX_RETRIES=3

# =============================================================================
# WEBSOCKET
# =============================================================================
WEBSOCKET_ENABLED=true
WEBSOCKET_PATH=/ws

# =============================================================================
# EXTERNAL API KEY (per CGS integration)
# =============================================================================
EXTERNAL_API_KEY=cgs-api-key-12345-test-local

# =============================================================================
# VERTEX AI (GEMINI via GCP)
# =============================================================================

# ⚠️ IMPORTANTE: Abilita Vertex AI per usare Gemini via GCP
USE_VERTEX_GEMINI=true

# Model Configuration
GEMINI_MODEL=gemini-2.0-flash-exp
PERPLEXITY_MODEL=sonar-pro

# GCP Project Settings
GCP_PROJECT_ID=startup-program-461116
GCP_LOCATION=us-central1

# Vertex API Settings
VERTEX_API_ENDPOINT=aiplatform.googleapis.com
VERTEX_API_VERSION=v1

# ⚠️ CRITICAL: Path to GCP Service Account JSON
# Questo file DEVE essere in .secrets/ (vedi Step 3)
GOOGLE_APPLICATION_CREDENTIALS=.secrets/startup-program-461116-e59705839bd1.json

# =============================================================================
# ONBOARDING SERVICE CONFIGURATION
# =============================================================================

# Service Settings
ONBOARDING_SERVICE_NAME=OnboardingService
ONBOARDING_SERVICE_VERSION=1.0.0
ONBOARDING_API_HOST=0.0.0.0
ONBOARDING_API_PORT=8001

# CGS Integration
CGS_API_URL=http://localhost:8000
CGS_API_TIMEOUT=600
CGS_API_KEY=cgs-api-key-12345-test-local

# Workflow Settings
ONBOARDING_MAX_CLARIFYING_QUESTIONS=3
ONBOARDING_SESSION_TIMEOUT_MINUTES=60
ONBOARDING_ENABLE_AUTO_DELIVERY=true

# Retry & Resilience
ONBOARDING_MAX_RETRIES=3
ONBOARDING_RETRY_BACKOFF_SECONDS=2.0

# Storage
ONBOARDING_DATA_DIR=data/onboarding
ONBOARDING_SESSIONS_DIR=data/onboarding/sessions
ONBOARDING_SNAPSHOTS_DIR=data/onboarding/snapshots

# Logging
ONBOARDING_LOG_LEVEL=INFO
ONBOARDING_DEBUG=false

# Feature Flags
ONBOARDING_ENABLE_SNAPSHOT_CACHING=true
ONBOARDING_ENABLE_COST_TRACKING=true
```

---

## 🔑 Step 3: Configurare Credenziali GCP (Google Cloud)

### **3.1: Creare Cartella `.secrets/`**

```bash
# Crea cartella .secrets nella root del progetto
mkdir -p .secrets

# Verifica che .secrets/ sia in .gitignore
cat .gitignore | grep .secrets
# Dovrebbe mostrare: .secrets/
```

### **3.2: Ottenere Service Account JSON**

**Opzione A: Hai già il file**
```bash
# Copia il file JSON nella cartella .secrets/
cp ~/Downloads/startup-program-461116-e59705839bd1.json .secrets/

# Verifica permessi (solo owner può leggere)
chmod 600 .secrets/startup-program-461116-e59705839bd1.json
```

**Opzione B: Scaricarlo da GCP Console**
1. Vai su [Google Cloud Console](https://console.cloud.google.com)
2. Seleziona progetto: `startup-program-461116`
3. Vai su **IAM & Admin** → **Service Accounts**
4. Trova service account con permessi Vertex AI
5. Click **Actions** → **Manage Keys**
6. Click **Add Key** → **Create New Key** → **JSON**
7. Salva il file scaricato in `.secrets/startup-program-461116-e59705839bd1.json`

### **3.3: Verificare Configurazione**

```bash
# Verifica che il file esista
ls -la .secrets/

# Output atteso:
# -rw------- 1 user staff 2345 Oct 25 10:00 startup-program-461116-e59705839bd1.json

# Verifica che .env punti al file corretto
cat .env | grep GOOGLE_APPLICATION_CREDENTIALS
# Output atteso:
# GOOGLE_APPLICATION_CREDENTIALS=.secrets/startup-program-461116-e59705839bd1.json
```

---

## 📦 Step 4: Installare Dipendenze

### **4.1: Backend (Python)**

```bash
# Crea virtual environment
python -m venv venv

# Attiva virtual environment
# Su macOS/Linux:
source venv/bin/activate

# Su Windows:
# venv\Scripts\activate

# Aggiorna pip
pip install --upgrade pip

# Installa dipendenze
pip install -r requirements.txt

# Verifica installazione
pip list | grep -E "fastapi|supabase|openai|google"
```

### **4.2: Frontend (React/TypeScript)**

```bash
# Entra nella cartella frontend
cd onboarding-frontend

# Installa dipendenze
npm install

# Torna alla root
cd ..
```

---

## ✅ Step 5: Verificare Setup

### **5.1: Test Backend**

```bash
# Dalla root del progetto
python -c "
from onboarding.config.settings import get_settings
settings = get_settings()
print(f'✅ Settings loaded')
print(f'Supabase URL: {settings.supabase_url}')
print(f'GCP Project: {settings.gcp_project_id}')
print(f'Gemini Model: {settings.gemini_model}')
"
```

**Output atteso**:
```
✅ Settings loaded
Supabase URL: https://iimymnlepgilbuoxnkqa.supabase.co
GCP Project: startup-program-461116
Gemini Model: gemini-2.0-flash-exp
```

### **5.2: Test Connessione Supabase**

```bash
python scripts/test_company_context_repository.py
```

**Output atteso**:
```
✅ Supabase connection successful
✅ company_contexts table exists
```

---

## 🚀 Step 6: Avviare Servizi

### **6.1: Avviare Backend (CGS + Onboarding)**

```bash
# Terminal 1: Avvia CGS Core
python start_backend.py

# Terminal 2: Avvia Onboarding Service
cd onboarding
uvicorn api.main:app --host 0.0.0.0 --port 8001 --reload
```

**Output atteso**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (CGS)
INFO:     Uvicorn running on http://0.0.0.0:8001 (Onboarding)
```

### **6.2: Avviare Frontend**

```bash
# Terminal 3: Avvia React app
cd onboarding-frontend
npm run dev
```

**Output atteso**:
```
  VITE v5.x.x  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

---

## 🧪 Step 7: Test Completo

### **7.1: Test API Health**

```bash
# Test CGS Core
curl http://localhost:8000/health

# Test Onboarding Service
curl http://localhost:8001/health
```

**Output atteso**:
```json
{"status": "healthy", "service": "CGS", "version": "1.0.0"}
{"status": "healthy", "service": "OnboardingService", "version": "1.0.0"}
```

### **7.2: Test Frontend**

Apri browser su `http://localhost:5173` e verifica che:
- ✅ La pagina si carica
- ✅ Non ci sono errori in console
- ✅ Puoi iniziare onboarding

---

## 📋 Checklist Finale

Prima di iniziare a lavorare, verifica:

- [ ] ✅ Repository clonato
- [ ] ✅ File `.env` creato e popolato con tutte le API keys
- [ ] ✅ Cartella `.secrets/` creata con GCP service account JSON
- [ ] ✅ Virtual environment Python creato e attivato
- [ ] ✅ Dipendenze Python installate (`pip install -r requirements.txt`)
- [ ] ✅ Dipendenze Node installate (`npm install` in `onboarding-frontend/`)
- [ ] ✅ Test connessione Supabase funzionante
- [ ] ✅ Backend CGS avviato su porta 8000
- [ ] ✅ Backend Onboarding avviato su porta 8001
- [ ] ✅ Frontend React avviato su porta 5173
- [ ] ✅ Health checks passano per tutti i servizi

---

## 🔒 Sicurezza - IMPORTANTE!

### **File da NON Committare MAI**

```bash
# Verifica che questi file siano in .gitignore:
.env
.env.local
.env.*.local
.secrets/
*.json  # (nella cartella .secrets/)
venv/
node_modules/
```

### **Backup Sicuro**

Se vuoi fare backup delle credenziali:

```bash
# ❌ MAI committare su Git
# ✅ Usa password manager (1Password, LastPass, etc.)
# ✅ Oppure encrypted storage (Keybase, encrypted USB)
```

---

## 🆘 Troubleshooting

### **Problema: `ModuleNotFoundError`**
```bash
# Soluzione: Assicurati che venv sia attivato
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### **Problema: `GOOGLE_APPLICATION_CREDENTIALS not found`**
```bash
# Soluzione: Verifica path in .env
echo $GOOGLE_APPLICATION_CREDENTIALS
ls -la .secrets/startup-program-461116-e59705839bd1.json
```

### **Problema: `Supabase connection failed`**
```bash
# Soluzione: Verifica credenziali in .env
cat .env | grep SUPABASE
# Verifica che SUPABASE_URL e SUPABASE_ANON_KEY siano corretti
```

### **Problema: Frontend non si connette al backend**
```bash
# Soluzione: Verifica CORS e URL in frontend
# File: onboarding-frontend/src/services/api/onboardingApi.ts
# Verifica che baseURL sia http://localhost:8001
```

---

## 📚 Documentazione Utile

- **Onboarding System**: `onboarding/README.md`
- **Card Implementation**: `docs/CARD_IMPLEMENTATION_STRATEGY.md`
- **Feature Overview**: `docs/FEATURE_OVERVIEW_ESSENTIALS.md`
- **Transparency Feature**: `docs/transparency/README.md`
- **Frontend Guide**: `onboarding-frontend/README.md`

---

**Prepared by**: Fylle AI Team  
**Last Updated**: 2025-10-25  
**Status**: ✅ Ready to Use

