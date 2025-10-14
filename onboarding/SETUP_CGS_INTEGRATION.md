# 🔗 Setup Onboarding Service con Configurazione CGS Esistente

Questa guida spiega come il servizio di onboarding **riusa la configurazione esistente di CGS** senza duplicare credenziali.

---

## 📋 Configurazione Rilevata

Ho analizzato la tua configurazione CGS esistente e trovato:

### ✅ Credenziali Disponibili

| Servizio | Status | Valore |
|----------|--------|--------|
| **Perplexity API** | ✅ Configurato | `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` |
| **Gemini API** | ✅ Configurato | `AIzaSyCos3jhCIoWKYb4bpJ1XxBpSaejs4A9T30` |
| **Vertex AI (GCP)** | ✅ Configurato | Project: `startup-program-461116` |
| **GCP Credentials** | ✅ Configurato | File JSON presente |
| **Supabase** | ✅ Configurato | URL + Anon Key |
| **CGS API Key** | ✅ Configurato | `cgs-api-key-12345-test-local` |
| **Brevo Email** | ⚠️ Da configurare | Aggiungi la tua API key |

---

## 🎯 Come Funziona l'Integrazione

### 1. Riuso Diretto delle Credenziali

Il servizio di onboarding **legge le stesse variabili d'ambiente** usate da CGS:

```bash
# CGS usa:
PERPLEXITY_API_KEY=pplx-...
GEMINI_API_KEY=AIzaSy...
SUPABASE_URL=https://...

# Onboarding riusa le stesse variabili!
# Nessuna duplicazione necessaria
```

### 2. File di Configurazione

**Opzione A: Usa il file `.env.` esistente di CGS** (raccomandato)

```bash
# Il servizio di onboarding può leggere direttamente da .env.
# Basta avviarlo nella stessa directory
cd /Users/davidescantamburlo/Desktop/Test\ Onboarding\ /CGS_2
uvicorn onboarding.api.main:app --reload --port 8001 --env-file .env.
```

**Opzione B: Usa il file `onboarding/.env` dedicato**

```bash
# Ho già creato onboarding/.env con le credenziali copiate
cd onboarding
uvicorn onboarding.api.main:app --reload --port 8001
```

---

## 🚀 Quick Start (3 minuti)

### Step 1: Aggiungi API Key Brevo

Modifica `onboarding/.env` e aggiungi la tua chiave Brevo:

```bash
BREVO_API_KEY=xkeysib-your-actual-brevo-api-key-here
```

### Step 2: Verifica Path Credenziali GCP

Il file `.env` punta a:
```bash
GOOGLE_APPLICATION_CREDENTIALS=/Users/davidescantamburlo/Desktop/Test Onboarding /CGS_2/startup-program-461116-e59705839bd1.json
```

✅ **Verificato**: Il file esiste nella posizione corretta!

### Step 3: Setup Database Supabase

Esegui lo schema SQL in Supabase:

```bash
# 1. Vai su https://app.supabase.com
# 2. Apri il progetto: iimymnlepgilbuoxnkqa
# 3. SQL Editor → New Query
# 4. Copia e incolla il contenuto di:
cat onboarding/infrastructure/database/supabase_schema.sql
# 5. Run
```

### Step 4: Avvia il Servizio

```bash
# Opzione A: Dalla root di CGS (usa .env. esistente)
cd /Users/davidescantamburlo/Desktop/Test\ Onboarding\ /CGS_2
uvicorn onboarding.api.main:app --reload --port 8001 --env-file .env.

# Opzione B: Dalla directory onboarding (usa onboarding/.env)
cd onboarding
uvicorn onboarding.api.main:app --reload --port 8001
```

### Step 5: Verifica

```bash
# Health check
curl http://localhost:8001/health

# API Docs
open http://localhost:8001/docs
```

---

## 🔧 Configurazione Dettagliata

### Variabili d'Ambiente Riusate da CGS

| Variabile CGS | Uso in Onboarding | Valore Attuale |
|---------------|-------------------|----------------|
| `PERPLEXITY_API_KEY` | Research azienda | ✅ Configurato |
| `GEMINI_API_KEY` | Synthesis snapshot | ✅ Configurato |
| `USE_VERTEX_GEMINI` | Usa Vertex AI | `true` |
| `GCP_PROJECT_ID` | Project GCP | `startup-program-461116` |
| `GCP_LOCATION` | Region GCP | `us-central1` |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path JSON | ✅ File presente |
| `SUPABASE_URL` | Database | ✅ Configurato |
| `SUPABASE_ANON_KEY` | Auth Supabase | ✅ Configurato |
| `USE_SUPABASE` | Enable DB | `true` |

### Variabili Specifiche per Onboarding

| Variabile | Descrizione | Default | Richiesto |
|-----------|-------------|---------|-----------|
| `ONBOARDING_API_PORT` | Porta servizio | `8001` | No |
| `CGS_API_URL` | URL backend CGS | `http://localhost:8000` | Sì |
| `CGS_API_KEY` | Auth CGS | Da `.env.` | Sì |
| `BREVO_API_KEY` | Email delivery | - | **Sì** |
| `BREVO_SENDER_EMAIL` | Email mittente | `onboarding@fylle.ai` | No |

---

## 📊 Architettura Integrata

```
┌─────────────────────────────────────────────────────────┐
│                  Onboarding Service                     │
│                  (Port 8001)                            │
│  ┌───────────────────────────────────────────────────┐  │
│  │  API Endpoints                                    │  │
│  │  - POST /api/v1/onboarding/start                  │  │
│  │  - POST /api/v1/onboarding/{id}/answers           │  │
│  └───────────────────────────────────────────────────┘  │
│                         ↓                               │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Use Cases                                        │  │
│  │  - Research → Synthesis → Execute                 │  │
│  └───────────────────────────────────────────────────┘  │
│                         ↓                               │
│  ┌─────────────┬─────────────┬─────────────┬─────────┐  │
│  │ Perplexity  │   Gemini    │     CGS     │  Brevo  │  │
│  │  Adapter    │   Adapter   │   Adapter   │ Adapter │  │
│  └─────────────┴─────────────┴─────────────┴─────────┘  │
└─────────────────────────────────────────────────────────┘
         ↓              ↓              ↓            ↓
    ┌─────────┐   ┌─────────┐   ┌─────────┐  ┌─────────┐
    │Perplexity│   │ Vertex  │   │   CGS   │  │  Brevo  │
    │   API   │   │AI/Gemini│   │Backend  │  │   API   │
    └─────────┘   └─────────┘   │(Port8000)│  └─────────┘
                                 └─────────┘
                                      ↓
                              ┌──────────────┐
                              │   Supabase   │
                              │  (Shared DB) │
                              └──────────────┘
```

### Flusso di Dati

1. **Onboarding Service** (porta 8001) riceve richieste
2. **Perplexity Adapter** → Riusa `PERPLEXITY_API_KEY` da `.env.`
3. **Gemini Adapter** → Riusa `GEMINI_API_KEY` + Vertex AI config
4. **CGS Adapter** → Chiama CGS backend (porta 8000) con `CGS_API_KEY`
5. **Brevo Adapter** → Invia email con `BREVO_API_KEY`
6. **Supabase** → Database condiviso tra CGS e Onboarding

---

## 🔐 Sicurezza

### File Credenziali GCP

Il file `startup-program-461116-e59705839bd1.json` contiene:
- Service Account credentials
- Private key per autenticazione GCP
- Accesso a Vertex AI

**⚠️ IMPORTANTE**: 
- ✅ File già presente nella root di CGS
- ✅ Path configurato in `.env.`
- ⚠️ NON committare questo file su Git
- ✅ Già in `.gitignore` (verifica)

### API Keys

Tutte le API keys sono in `.env.` che:
- ✅ NON deve essere committato
- ✅ Deve essere in `.gitignore`
- ✅ Deve avere permessi `600` (solo owner può leggere)

```bash
# Verifica permessi
chmod 600 .env.
chmod 600 startup-program-461116-e59705839bd1.json
```

---

## 🧪 Test Rapido

### 1. Test Componenti (senza API calls)

```bash
cd onboarding
python -m examples.test_components
```

### 2. Test Health Check

```bash
# Avvia servizio
uvicorn onboarding.api.main:app --reload --port 8001 --env-file ../.env.

# In un altro terminale
curl http://localhost:8001/health
```

Risposta attesa:
```json
{
  "status": "healthy",
  "service": "OnboardingService",
  "version": "1.0.0",
  "timestamp": "2025-01-15T...",
  "dependencies": {
    "perplexity": true,
    "gemini": true,
    "cgs": true,
    "brevo": false,  // ⚠️ false se BREVO_API_KEY non configurato
    "supabase": true
  }
}
```

### 3. Test API Completo

```bash
# Dopo aver configurato BREVO_API_KEY
cd onboarding
python -m examples.test_api
```

---

## 🎯 Checklist Setup

- [x] ✅ Perplexity API key configurato (da `.env.`)
- [x] ✅ Gemini API key configurato (da `.env.`)
- [x] ✅ Vertex AI configurato (GCP project + credentials)
- [x] ✅ Supabase configurato (URL + key da `.env.`)
- [x] ✅ CGS API key configurato (da `.env.`)
- [ ] ⚠️ **Brevo API key da configurare** (aggiungi in `onboarding/.env`)
- [ ] ⚠️ **Supabase schema da eseguire** (vedi Step 3)

---

## 🚀 Prossimi Step

1. **Aggiungi Brevo API Key** in `onboarding/.env`
2. **Esegui schema SQL** in Supabase
3. **Avvia servizio** con `uvicorn`
4. **Testa** con `curl` o API docs
5. **Prova flow completo** con `examples/test_api.py`

---

## 📚 Documentazione

- **Setup completo**: `QUICKSTART.md`
- **Deployment**: `DEPLOYMENT.md`
- **API Reference**: `README.md`
- **Questa guida**: `SETUP_CGS_INTEGRATION.md`

---

**Tutto pronto!** Il servizio è configurato per riusare le credenziali esistenti di CGS. 🎉

Manca solo:
1. Brevo API key
2. Eseguire schema SQL in Supabase

Poi puoi avviare il servizio! 🚀

