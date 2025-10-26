# ⚡ Quick Start - Onboarding Service

Guida rapida per avviare il servizio in 5 minuti.

---

## 🚀 Setup Rapido

### 1. Installa Dipendenze (30 secondi)

```bash
cd onboarding
pip install -r requirements.txt
```

### 2. Configura Environment (2 minuti)

```bash
# Copia template
cp .env.example .env

# Modifica .env con le tue API keys
# Minimo richiesto:
# - SUPABASE_URL
# - SUPABASE_SERVICE_ROLE_KEY
# - PERPLEXITY_API_KEY
# - GEMINI_API_KEY
# - CGS_BASE_URL
```

### 3. Setup Database (1 minuto)

```bash
# 1. Vai su https://app.supabase.com
# 2. Apri SQL Editor
# 3. Copia e incolla il contenuto di:
#    infrastructure/database/supabase_schema.sql
# 4. Esegui
```

### 4. Avvia Servizio (10 secondi)

```bash
uvicorn onboarding.api.main:app --reload --port 8001
```

### 5. Verifica (10 secondi)

```bash
# Health check
curl http://localhost:8001/health

# API Docs
open http://localhost:8001/docs
```

---

## 🧪 Test Rapido

### Opzione 1: Test Componenti (senza API keys)

```bash
python -m onboarding.examples.test_components
```

### Opzione 2: Test API Completo (con API keys)

```bash
# Assicurati che il servizio sia in esecuzione
python -m onboarding.examples.test_api
```

### Opzione 3: Test con curl

```bash
# Start onboarding
curl -X POST http://localhost:8001/api/v1/onboarding/start \
  -H "Content-Type: application/json" \
  -d '{
    "brand_name": "Test Company",
    "website": "https://test.com",
    "goal": "linkedin_post",
    "user_email": "test@test.com"
  }'

# Copia session_id dalla risposta

# Submit answers
curl -X POST http://localhost:8001/api/v1/onboarding/{session_id}/answers \
  -H "Content-Type: application/json" \
  -d '{
    "answers": {
      "q1": "AI automation",
      "q2": "medium (400-600 words)",
      "q3": true
    }
  }'
```

---

## 📊 Cosa Succede?

### Flow Completo

```
1. POST /start
   ↓
   Crea sessione → Research (Perplexity) → Synthesis (Gemini)
   ↓
   Ritorna: snapshot + clarifying questions

2. POST /{session_id}/answers
   ↓
   Valida risposte → Build payload → Execute CGS → Send email
   ↓
   Ritorna: content + metrics
```

### Durata Tipica

- **Research**: ~10-15 secondi
- **Synthesis**: ~5-10 secondi
- **CGS Execution**: ~20-30 secondi
- **Email Delivery**: ~2-3 secondi
- **TOTALE**: ~40-60 secondi

---

## 🔧 Troubleshooting Rapido

### Problema: "Service not configured"

```bash
# Verifica che tutte le API keys siano configurate
python -c "from onboarding.config.settings import get_onboarding_settings; s = get_onboarding_settings(); print(s.validate_required_services())"
```

### Problema: "CGS not reachable"

```bash
# Verifica che CGS sia in esecuzione
curl http://localhost:8000/health

# Controlla CGS_BASE_URL in .env
```

### Problema: "Supabase connection error"

```bash
# Verifica credenziali Supabase
# Controlla SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY in .env

# Test connessione
python -c "from supabase import create_client; client = create_client('YOUR_URL', 'YOUR_KEY'); print('OK')"
```

---

## 📚 Prossimi Step

1. **Leggi la documentazione completa**: `README.md`
2. **Esplora l'architettura**: `IMPLEMENTATION_STATUS.md`
3. **Deployment in produzione**: `DEPLOYMENT.md`
4. **API Docs interattiva**: http://localhost:8001/docs

---

## 🎯 Endpoints Principali

| Endpoint | Metodo | Descrizione |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/v1/onboarding/start` | POST | Avvia onboarding |
| `/api/v1/onboarding/{id}/answers` | POST | Invia risposte |
| `/api/v1/onboarding/{id}/status` | GET | Stato sessione |
| `/api/v1/onboarding/{id}` | GET | Dettagli completi |

---

## ✅ Checklist Setup

- [ ] Dipendenze installate
- [ ] File `.env` configurato
- [ ] Supabase schema eseguito
- [ ] CGS backend in esecuzione
- [ ] Servizio onboarding avviato
- [ ] Health check OK
- [ ] Test API eseguito con successo

---

**Pronto per partire!** 🚀

Per domande: consulta `README.md` o `DEPLOYMENT.md`

