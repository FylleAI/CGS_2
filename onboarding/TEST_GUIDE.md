# 🧪 Guida Test Onboarding Service

Questa guida ti aiuta a testare il servizio di onboarding passo-passo.

---

## 📋 Prerequisiti

✅ **Completati**:
- [x] Configurazione verificata (17/17 check)
- [x] Schema SQL Supabase eseguito
- [x] Credenziali CGS riusate

⚠️ **Da fare dopo** (opzionale per ora):
- [ ] Brevo API key (solo per invio email finale)

---

## 🎯 Cosa Testeremo

Il servizio di onboarding ha **2 modalità di test**:

### Modalità 1: Test Componenti Singoli (SENZA chiamate API reali)
✅ Veloce (< 1 minuto)  
✅ Nessun costo API  
✅ Verifica che il codice funzioni  

### Modalità 2: Test Flow Completo (CON chiamate API reali)
⚠️ Più lento (2-3 minuti)  
⚠️ Usa crediti API (Perplexity, Gemini)  
✅ Test end-to-end reale  

---

## 🚀 Test Modalità 1: Componenti Singoli

### Step 1: Avvia il Servizio

```bash
# Dalla directory onboarding
cd /path/to/your/CGS_2/onboarding

# Avvia il server
uvicorn onboarding.api.main:app --reload --port 8001
```

**Output atteso**:
```
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 2: Test Health Check

**In un NUOVO terminale**:

```bash
curl http://localhost:8001/health
```

**Output atteso**:
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
    "brevo": false,
    "supabase": true
  }
}
```

✅ Se vedi questo, il servizio è **ATTIVO**!

### Step 3: Apri API Docs Interattiva

```bash
open http://localhost:8001/docs
```

Vedrai l'interfaccia Swagger con tutti gli endpoint disponibili:
- `POST /api/v1/onboarding/start` - Inizia onboarding
- `GET /api/v1/onboarding/{session_id}` - Ottieni stato sessione
- `POST /api/v1/onboarding/{session_id}/answers` - Invia risposte
- `POST /api/v1/onboarding/{session_id}/execute` - Esegui generazione contenuto

---

## 🔥 Test Modalità 2: Flow Completo End-to-End

Questo test esegue l'intero flusso di onboarding con chiamate API reali.

### Prerequisiti

1. **CGS Backend deve essere attivo** sulla porta 8000:

```bash
# In un terminale separato, avvia CGS
cd /path/to/your/CGS_2
uvicorn core.api.main:app --reload --port 8000
```

2. **Onboarding Service deve essere attivo** sulla porta 8001 (vedi Step 1 sopra)

### Test Scenario: Onboarding di un'Azienda Reale

Useremo **Fylle.ai** come esempio (puoi sostituire con qualsiasi azienda).

#### Step 1: Inizia Onboarding Session

```bash
curl -X POST http://localhost:8001/api/v1/onboarding/start \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Fylle",
    "company_website": "https://fylle.ai",
    "user_email": "test@fylle.ai",
    "onboarding_goal": "LINKEDIN_POST"
  }'
```

**Output atteso**:
```json
{
  "session_id": "uuid-generato-automaticamente",
  "state": "researching",
  "company_name": "Fylle",
  "created_at": "2025-01-15T...",
  "message": "Onboarding started. Researching company..."
}
```

📝 **Salva il `session_id`** - ti servirà per i prossimi step!

**Cosa succede dietro le quinte**:
1. ✅ Crea sessione in Supabase
2. 🔍 Chiama Perplexity per ricercare info su Fylle
3. 🤖 Chiama Gemini/Vertex AI per sintetizzare snapshot
4. ❓ Genera 3 domande di chiarimento

⏱️ **Tempo**: ~30-60 secondi

#### Step 2: Verifica Stato e Domande

```bash
# Sostituisci SESSION_ID con l'ID ricevuto
curl http://localhost:8001/api/v1/onboarding/SESSION_ID
```

**Output atteso**:
```json
{
  "session_id": "...",
  "state": "awaiting_user",
  "company_name": "Fylle",
  "snapshot": {
    "version": "1.0.0",
    "company": {
      "name": "Fylle",
      "description": "AI-powered content generation platform...",
      "offerings": ["AI content creation", "Workflow automation", ...],
      "differentiators": ["Advanced AI models", "Custom workflows", ...]
    },
    "audience": {
      "primary": "Marketing teams and content creators",
      "pain_points": ["Time-consuming content creation", ...],
      "desired_outcomes": ["Faster content production", ...]
    },
    "voice": {
      "tone": "Professional yet approachable",
      "style_guidelines": ["Clear and concise", ...]
    },
    "clarifying_questions": [
      {
        "id": "q1",
        "question": "What specific type of content do you create most often?",
        "context": "To tailor the AI suggestions to your needs"
      },
      {
        "id": "q2",
        "question": "Who is your primary target audience?",
        "context": "To ensure content resonates with the right people"
      },
      {
        "id": "q3",
        "question": "What tone of voice best represents your brand?",
        "context": "To maintain brand consistency"
      }
    ]
  },
  "created_at": "...",
  "updated_at": "..."
}
```

✅ Se vedi questo, **research e synthesis hanno funzionato**!

#### Step 3: Rispondi alle Domande

```bash
curl -X POST http://localhost:8001/api/v1/onboarding/SESSION_ID/answers \
  -H "Content-Type: application/json" \
  -d '{
    "answers": [
      {
        "question_id": "q1",
        "answer": "LinkedIn posts and newsletters about AI and automation"
      },
      {
        "question_id": "q2",
        "answer": "B2B marketing teams and content managers in tech companies"
      },
      {
        "question_id": "q3",
        "answer": "Professional, innovative, and helpful - we want to educate while inspiring"
      }
    ]
  }'
```

**Output atteso**:
```json
{
  "session_id": "...",
  "state": "payload_ready",
  "message": "Answers collected. Ready to execute onboarding.",
  "answers_count": 3
}
```

✅ Ora il sistema ha tutte le informazioni necessarie!

#### Step 4: Esegui Generazione Contenuto (Chiama CGS)

```bash
curl -X POST http://localhost:8001/api/v1/onboarding/SESSION_ID/execute
```

**Cosa succede**:
1. 🔨 Costruisce payload CGS da snapshot + risposte
2. 📤 Chiama CGS backend `/api/v1/content/generate`
3. ⏳ CGS esegue workflow (Perplexity → Gemini → generazione)
4. 📧 (Opzionale) Invia email con Brevo

⏱️ **Tempo**: ~60-120 secondi (dipende da CGS)

**Output atteso**:
```json
{
  "session_id": "...",
  "state": "done",
  "message": "Onboarding completed successfully!",
  "result": {
    "content": {
      "title": "How AI is Transforming Content Creation in 2025",
      "body": "In today's fast-paced digital landscape...",
      "metadata": {
        "word_count": 250,
        "tone": "professional",
        "target_audience": "B2B marketing teams"
      }
    },
    "workflow_metrics": {
      "total_duration_seconds": 45.2,
      "steps_executed": 5,
      "tokens_used": 1250
    }
  }
}
```

🎉 **SUCCESSO!** Hai completato l'intero flusso di onboarding!

---

## 🧪 Test Automatizzato

Ho creato uno script Python che esegue tutti gli step automaticamente:

```bash
cd /path/to/your/CGS_2/onboarding

# Test completo con azienda di esempio
python3 -m examples.test_full_flow
```

---

## 📊 Cosa Verificare Durante i Test

### ✅ Checklist Test

**Health Check**:
- [ ] Servizio risponde su porta 8001
- [ ] Tutti i dependencies sono `true` (tranne brevo)
- [ ] Timestamp è corretto

**Start Onboarding**:
- [ ] Ricevi `session_id` valido
- [ ] State è `researching` → `synthesizing` → `awaiting_user`
- [ ] Snapshot contiene info azienda
- [ ] 3 domande di chiarimento generate

**Collect Answers**:
- [ ] State diventa `payload_ready`
- [ ] Risposte salvate correttamente

**Execute**:
- [ ] Chiamata a CGS va a buon fine
- [ ] Contenuto generato ricevuto
- [ ] State diventa `done`
- [ ] Metriche workflow presenti

**Database**:
- [ ] Sessione salvata in Supabase
- [ ] Snapshot salvato correttamente
- [ ] Risposte salvate
- [ ] Risultato salvato

---

## 🐛 Troubleshooting

### Problema: "Connection refused" su porta 8001

**Soluzione**: Verifica che il servizio sia avviato:
```bash
lsof -i :8001
# Se non vedi nulla, avvia il servizio
```

### Problema: "Connection refused" su porta 8000 (CGS)

**Soluzione**: Avvia CGS backend:
```bash
cd /path/to/your/CGS_2
uvicorn core.api.main:app --reload --port 8000
```

### Problema: "Perplexity API error"

**Soluzione**: Verifica API key:
```bash
grep PERPLEXITY_API_KEY onboarding/.env
```

### Problema: "Vertex AI authentication failed"

**Soluzione**: Verifica path credenziali GCP:
```bash
ls -la /path/to/your/CGS_2/startup-program-461116-e59705839bd1.json
```

### Problema: "Supabase error"

**Soluzione**: Verifica che lo schema SQL sia stato eseguito:
```sql
-- In Supabase SQL Editor
SELECT * FROM onboarding_sessions LIMIT 1;
```

---

## 📝 Log e Debug

### Vedere i Log del Servizio

I log appaiono nel terminale dove hai avviato `uvicorn`:

```
INFO:     127.0.0.1:52345 - "POST /api/v1/onboarding/start HTTP/1.1" 200 OK
INFO:     Research completed for company: Fylle
INFO:     Synthesis completed, snapshot generated
INFO:     Session state: researching → awaiting_user
```

### Aumentare Verbosità

Modifica `onboarding/.env`:
```bash
LOG_LEVEL=DEBUG
```

Poi riavvia il servizio.

---

## 🎯 Prossimi Step Dopo i Test

Una volta che i test funzionano:

1. **Aggiungi Brevo API key** per testare invio email
2. **Personalizza prompt** in `gemini_adapter.py` se necessario
3. **Aggiungi più goal** (NEWSLETTER, BLOG_POST, etc.)
4. **Deploy in produzione** (vedi `DEPLOYMENT.md`)

---

## 📚 Riferimenti

- **API Docs**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health
- **Supabase Dashboard**: https://app.supabase.com/project/iimymnlepgilbuoxnkqa
- **Documentazione Completa**: `README.md`

---

**Pronto per iniziare i test?** 🚀

Segui gli step sopra e fammi sapere se incontri problemi!

