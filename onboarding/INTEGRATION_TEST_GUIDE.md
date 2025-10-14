# 🧪 Guida Test Integrazione Completa

**Onboarding Service + CGS Backend**

---

## ✅ Prerequisiti

Entrambi i servizi devono essere attivi:

```bash
# Terminal 1: Onboarding Service (porta 8001)
cd onboarding
python3 -m uvicorn onboarding.api.main:app --reload --port 8001 --env-file .env

# Terminal 2: CGS Backend (porta 8000)
cd /path/to/your/CGS_2
python3 -m uvicorn api.rest.main:app --host 0.0.0.0 --port 8000 --reload
```

Verifica che siano attivi:
```bash
curl http://localhost:8001/health  # Onboarding
curl http://localhost:8000/health  # CGS
```

---

## 🚀 Test Manuale con API Docs (Raccomandato)

### Step 1: Apri Swagger UI

```bash
open http://localhost:8001/docs
```

### Step 2: Start Onboarding

1. Clicca su **POST /api/v1/onboarding/start**
2. Clicca su **Try it out**
3. Usa questo payload:

```json
{
  "brand_name": "Fylle",
  "website": "https://fylle.ai",
  "goal": "linkedin_post",
  "user_email": "test@fylle.ai"
}
```

4. Clicca **Execute**
5. **Copia il `session_id`** dalla risposta (es: `07a25be8-ef89-4fe7-a402-87c1ea16bd8a`)
6. **Aspetta 30 secondi** per completamento research + synthesis

### Step 3: Get Snapshot

1. Clicca su **GET /api/v1/onboarding/{session_id}**
2. Clicca **Try it out**
3. Incolla il `session_id` copiato prima
4. Clicca **Execute**
5. **Leggi le domande** nella risposta sotto `snapshot.clarifying_questions`

Esempio domande:
```json
{
  "id": "q1",
  "question": "What are your key performance indicators (KPIs)?",
  "expected_response_type": "string"
},
{
  "id": "q2",
  "question": "Which marketing channels are most important?",
  "expected_response_type": "enum",
  "options": ["Social Media", "Email Marketing", "Content Marketing", "Paid Advertising", "Website"]
},
{
  "id": "q3",
  "question": "Are there specific compliance requirements?",
  "expected_response_type": "string"
}
```

### Step 4: Submit Answers

1. Clicca su **POST /api/v1/onboarding/{session_id}/answers**
2. Clicca **Try it out**
3. Incolla il `session_id`
4. **IMPORTANTE**: Usa risposte che corrispondono ai tipi delle domande!

Esempio payload (adatta alle tue domande):
```json
{
  "answers": {
    "q1": "Engagement rate, click-through rate, and conversion rate",
    "q2": "Social Media",
    "q3": "GDPR compliance for EU users"
  }
}
```

**Note**:
- Per domande `enum`: usa ESATTAMENTE una delle opzioni mostrate
- Per domande `string`: testo libero
- Per domande `boolean`: `true` o `false`
- Per domande `number`: numero

5. Clicca **Execute**
6. Verifica risposta `200 OK`

### Step 5: Execute (Chiamata a CGS)

1. Clicca su **POST /api/v1/onboarding/{session_id}/execute**
2. Clicca **Try it out**
3. Incolla il `session_id`
4. Clicca **Execute**
5. **Aspetta 1-2 minuti** - CGS sta generando il contenuto!

Risposta attesa:
```json
{
  "session_id": "...",
  "state": "executing",
  "message": "Content generation started"
}
```

### Step 6: Verifica Risultato

1. Clicca di nuovo su **GET /api/v1/onboarding/{session_id}**
2. Verifica che `state` sia `done` o `delivering`
3. Controlla il campo `cgs_result` per il contenuto generato

---

## 🔧 Test con cURL

Se preferisci la command line:

### 1. Start Onboarding
```bash
SESSION_ID=$(curl -s -X POST http://localhost:8001/api/v1/onboarding/start \
  -H "Content-Type: application/json" \
  -d '{
    "brand_name": "Fylle",
    "website": "https://fylle.ai",
    "goal": "linkedin_post",
    "user_email": "test@fylle.ai"
  }' | python3 -c "import sys, json; print(json.load(sys.stdin)['session_id'])")

echo "Session ID: $SESSION_ID"
sleep 30
```

### 2. Get Snapshot
```bash
curl -s http://localhost:8001/api/v1/onboarding/$SESSION_ID | python3 -m json.tool
```

### 3. Submit Answers (ADATTA LE RISPOSTE!)
```bash
curl -s -X POST http://localhost:8001/api/v1/onboarding/$SESSION_ID/answers \
  -H "Content-Type: application/json" \
  -d '{
    "answers": {
      "q1": "Engagement and conversion rates",
      "q2": "Social Media",
      "q3": "GDPR compliance"
    }
  }' | python3 -m json.tool
```

### 4. Execute
```bash
curl -s -X POST http://localhost:8001/api/v1/onboarding/$SESSION_ID/execute | python3 -m json.tool
sleep 60
```

### 5. Get Result
```bash
curl -s http://localhost:8001/api/v1/onboarding/$SESSION_ID | python3 -m json.tool
```

---

## 📊 Cosa Aspettarsi

### Timeline Completa

| Step | Durata | Cosa Succede |
|------|--------|--------------|
| **Start** | ~25s | Perplexity research + Gemini synthesis |
| **Get Snapshot** | <1s | Recupero dati da Supabase |
| **Submit Answers** | <1s | Validazione e salvataggio risposte |
| **Execute** | 60-120s | CGS genera contenuto (workflow completo) |
| **Get Result** | <1s | Recupero contenuto generato |

### State Transitions

```
created → researching → synthesizing → awaiting_user → 
payload_ready → executing → delivering → done
```

### Costi Stimati

- **Perplexity**: $0.00 (tier free)
- **Gemini/Vertex AI**: Incluso in GCP credits
- **CGS**: Dipende dal workflow (Gemini + altri servizi)
- **Supabase**: $0.00 (tier free)

---

## 🐛 Troubleshooting

### Errore 400: "Question expects one of..."

**Problema**: Risposta non valida per domanda enum

**Soluzione**: Usa ESATTAMENTE una delle opzioni mostrate in `options`

Esempio:
```json
// ❌ SBAGLIATO
"q2": "social media and email"

// ✅ CORRETTO
"q2": "Social Media"
```

### Errore 400: "Invalid state"

**Problema**: Stai chiamando un endpoint nello stato sbagliato

**Soluzione**: Verifica lo stato con GET e segui il flusso corretto

### CGS non risponde

**Problema**: CGS backend non attivo o in errore

**Soluzione**:
```bash
# Verifica CGS
curl http://localhost:8000/health

# Riavvia se necessario
python3 -m uvicorn api.rest.main:app --host 0.0.0.0 --port 8000 --reload
```

### Timeout durante Execute

**Problema**: CGS workflow richiede molto tempo

**Soluzione**: Normale per workflow complessi. Aspetta 2-3 minuti e ricontrolla lo stato.

---

## 📝 Verifica Dati in Supabase

Puoi vedere tutti i dati salvati:

1. Vai su: https://app.supabase.com/project/iimymnlepgilbuoxnkqa
2. Clicca su **Table Editor**
3. Seleziona tabella `onboarding_sessions`
4. Cerca il tuo `session_id`

Campi importanti:
- `state`: Stato corrente
- `snapshot`: Snapshot azienda + domande
- `cgs_payload`: Payload inviato a CGS
- `cgs_result`: Contenuto generato
- `error_message`: Eventuali errori

---

## 🎯 Esempio Completo di Successo

### Request Start
```json
{
  "brand_name": "Fylle",
  "website": "https://fylle.ai",
  "goal": "linkedin_post",
  "user_email": "test@fylle.ai"
}
```

### Response Start
```json
{
  "session_id": "07a25be8-ef89-4fe7-a402-87c1ea16bd8a",
  "state": "awaiting_user",
  "message": "Onboarding started for Fylle. Please answer the clarifying questions."
}
```

### Snapshot (dopo 30s)
```json
{
  "session_id": "07a25be8-ef89-4fe7-a402-87c1ea16bd8a",
  "state": "awaiting_user",
  "snapshot": {
    "company": {
      "name": "Fylle",
      "description": "AI-driven marketing platform...",
      "differentiators": [...]
    },
    "clarifying_questions": [
      {
        "id": "q1",
        "question": "What are your KPIs?",
        "expected_response_type": "string"
      },
      {
        "id": "q2",
        "question": "Which channels?",
        "expected_response_type": "enum",
        "options": ["Social Media", "Email", "Content", "Paid Ads"]
      }
    ]
  }
}
```

### Request Answers
```json
{
  "answers": {
    "q1": "Engagement rate and conversions",
    "q2": "Social Media"
  }
}
```

### Response Execute
```json
{
  "session_id": "07a25be8-ef89-4fe7-a402-87c1ea16bd8a",
  "state": "executing",
  "message": "Content generation started"
}
```

### Final Result (dopo 1-2 min)
```json
{
  "session_id": "07a25be8-ef89-4fe7-a402-87c1ea16bd8a",
  "state": "done",
  "cgs_result": {
    "content": "🚀 Transform Your Marketing with AI...",
    "metadata": {...}
  }
}
```

---

## 🎉 Successo!

Se hai completato tutti gli step e vedi `state: "done"` con contenuto in `cgs_result`, 
**l'integrazione funziona perfettamente!** 🎊

Il servizio di onboarding ha:
1. ✅ Ricercato l'azienda con Perplexity
2. ✅ Generato snapshot con Gemini/Vertex AI
3. ✅ Raccolto risposte utente con validazione
4. ✅ Costruito payload per CGS
5. ✅ Chiamato CGS per generazione contenuto
6. ✅ Salvato tutto in Supabase

**Il sistema è production-ready!** 🚀

