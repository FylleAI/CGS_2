# 🚀 PIANO SVILUPPO: API WORKFLOW ESTERNI

> **Obiettivo:** Trasformare CGSRef da app locale a servizio API riutilizzabile
> **Approccio:** Sistema a ticket asincrono con autenticazione API key
> **Impatto:** Zero modifiche al core, massima compatibilità

---

## 📋 PANORAMICA PROGETTO

### 🎯 **COSA VOGLIAMO OTTENERE**

**PRIMA (Situazione Attuale):**
```
Tu → Interfaccia Web CGS → Workflow → Risultato
```

**DOPO (Con API Esterni):**
```
Qualsiasi App → API CGS → Workflow → Risultato
CMS → API CGS → Workflow → Risultato
Sistema Marketing → API CGS → Workflow → Risultato
App Custom → API CGS → Workflow → Risultato
```

### 💡 **BENEFICI**
- **Per Te:** CGS diventa motore riutilizzabile
- **Per Altri:** Integrazione semplice nei loro sistemi
- **Scalabilità:** Un core, infinite interfacce
- **Business:** Possibilità di vendere accesso API

---

## ✅ PIANO SEMPLIFICATO (SENZA JOB MANAGER)

### Obiettivo rapido
- Esporre subito API utilizzabili sfruttando gli endpoint già presenti e sincroni
- Nessun sistema a ticket: la richiesta resta aperta finché il workflow termina e torna il risultato

### Architettura (semplificata)
```
Client → FastAPI esistente → Workflow (handlers dinamici) → Risultato
```

### Endpoint da usare
1) Content ad alto livello (consigliato)
- POST /api/v1/content/generate
- Payload tipico:
```json
{
  "topic": "AI nel Fintech",
  "workflow_type": "enhanced_article",             // opzionale, default: enhanced_article
  "client_profile": "default",                     // es. "siebert" per workflow Siebert
  "provider": "openai",                            // openai | anthropic | deepseek | gemini
  "model": "gpt-4o",
  "temperature": 0.7,
  "target_word_count": 800,
  "target_audience": "investitori retail",
  "tone": "professionale",
  "include_statistics": true,
  "include_examples": true,
  "context": "focus su trend 2025 e impatto normativo"
}
```
- Risposta: contiene title, body (contenuto generato), metadati e (se disponibili) metriche del workflow.

2) Esecuzione workflow diretta (basso livello)
- POST /api/v1/workflows/execute
- Payload tipico:
```json
{
  "workflow_id": "enhanced_article",
  "parameters": {
    "topic": "AI nel Fintech",
    "target_audience": "investitori retail",
    "tone": "professionale",
    "context": "focus su trend 2025 e impatto normativo",
    "include_statistics": true,
    "include_examples": true,
    "client_profile": "default",
    "target_word_count": 800
  }
}
```
- Risposta: stato di esecuzione e outputs dei task.

### Esempi rapidi
- cURL (content/generate):
```bash
curl -X POST http://localhost:8000/api/v1/content/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "AI nel Fintech",
    "workflow_type": "enhanced_article",
    "client_profile": "default",
    "provider": "openai",
    "model": "gpt-4o",
    "temperature": 0.7,
    "target_word_count": 800,
    "target_audience": "investitori retail",
    "tone": "professionale",
    "include_statistics": true,
    "include_examples": true,
    "context": "focus su trend 2025 e impatto normativo"
  }'
```

- cURL (workflows/execute):
```bash
curl -X POST http://localhost:8000/api/v1/workflows/execute \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id": "enhanced_article",
    "parameters": {
      "topic": "AI nel Fintech",
      "target_audience": "investitori retail",
      "tone": "professionale",
      "context": "focus su trend 2025 e impatto normativo",
      "include_statistics": true,
      "include_examples": true,
      "client_profile": "default",
      "target_word_count": 800
    }
  }'
```

### Script di test inclusi
- scripts/test_generate.py → chiamata Python a /api/v1/content/generate
- scripts/test_curl_commands.sh → comandi cURL pronti

### Roadmap (opzionale, fasi successive)
- Aggiungere API key (Bearer) sugli endpoint
- Introdurre Job Manager asincrono (ticket) mantenendo stessi payload
- Router /api/v1/external dedicato


## 🏗️ ARCHITETTURA TECNICA

### **Sistema a Ticket Asincrono**
```
1. Client → POST /workflows/{type} + dati → job_id
2. Client → GET /jobs/{job_id}/status → "running" | "completed"
3. Client → GET /jobs/{job_id}/result → contenuto generato
```

### **Componenti Nuovi**
- **Job Manager:** Gestione ticket e stato lavori
- **API Key Auth:** Autenticazione semplice ma sicura
- **External API Layer:** Endpoint dedicati per esterni
- **Job Storage:** Memoria temporanea risultati (in-memory → Redis futuro)

### **Sicurezza**
- Autenticazione via API Key (Bearer token)
- Validazione input rigorosa
- Rate limiting (futuro)
- Logging completo accessi

---

## 📁 STRUTTURA FILE DA CREARE

```
📁 core/infrastructure/jobs/
├── __init__.py
└── job_manager.py              # ⭐ Core: gestione ticket asincroni

📁 core/infrastructure/auth/
├── __init__.py
└── api_key_auth.py             # ⭐ Autenticazione API key

📁 api/rest/external/
├── __init__.py
└── workflows.py                # ⭐ Endpoint API esterni

📁 tests/external/
├── __init__.py
├── test_job_manager.py         # Test unitari
├── test_api_auth.py            # Test autenticazione
└── test_external_api.py        # Test integrazione

📁 scripts/
├── test_external_api.py        # ⭐ Script test completo
└── test_curl_commands.sh       # Test con cURL

📁 docs/external_api/
├── README.md                   # Documentazione API
├── examples.md                 # Esempi integrazione
└── authentication.md          # Guida autenticazione
```

---

## 🔧 IMPLEMENTAZIONE STEP-BY-STEP

### **FASE 1: Job Manager (Core Logic)**
**File:** `core/infrastructure/jobs/job_manager.py`

**Funzionalità:**
- ✅ Creazione job con UUID unico
- ✅ Gestione stati: PENDING → RUNNING → COMPLETED/FAILED
- ✅ Esecuzione asincrona workflow esistenti
- ✅ Storage in-memory (estendibile a Redis)
- ✅ Progress tracking (0-100%)
- ✅ Error handling robusto

**Metodi Principali:**
```python
create_job(workflow_type, input_data) → job_id
get_job_status(job_id) → status_dict
get_job_result(job_id) → result_dict
start_job(job_id, use_case) → bool
execute_job(job_id, use_case) → async execution
```

### **FASE 2: API Key Authentication**
**File:** `core/infrastructure/auth/api_key_auth.py`

**Funzionalità:**
- ✅ Validazione Bearer token
- ✅ Mapping API key → client_id
- ✅ FastAPI dependency injection
- ✅ Error handling 401/403
- ✅ Configurazione via .env

**Sicurezza:**
```python
# .env
EXTERNAL_API_KEY=

# Headers richiesti
Authorization: Bearer cgs-api-key-12345-test-local
```

### **FASE 3: External API Endpoints**
**File:** `api/rest/external/workflows.py`

**Endpoint Implementati:**
```python
POST   /api/v1/external/workflows/{workflow_type}  # Avvia workflow
GET    /api/v1/external/jobs/{job_id}/status       # Stato job
GET    /api/v1/external/jobs/{job_id}/result       # Risultato job
GET    /api/v1/external/jobs                       # Lista jobs
GET    /api/v1/external/workflows                  # Lista workflow disponibili
```

**Workflow Supportati:**
- `enhanced_article` - Articolo con ricerca avanzata
- `premium_newsletter` - Newsletter premium
- `siebert_premium_newsletter` - Newsletter Siebert

### **FASE 4: Configurazione Sistema**
**File:** `core/infrastructure/config/settings.py`

**Nuove Configurazioni:**
```python
# External API
external_api_key: Optional[str] = Field(env="EXTERNAL_API_KEY")

# Job Management
job_cleanup_interval: int = Field(default=3600)  # 1 ora
max_concurrent_jobs: int = Field(default=10)
job_timeout_seconds: int = Field(default=1800)   # 30 minuti
```

### **FASE 5: Integrazione FastAPI**
**File:** `api/rest/main.py`

**Modifiche:**
```python
from api.rest.external.workflows import router as external_router

# Aggiungi router esterno
app.include_router(external_router)
```

---

## 🧪 PIANO TESTING COMPLETO

### **1. Test Unitari**
```bash
# Test job manager
pytest tests/external/test_job_manager.py -v

# Test autenticazione
pytest tests/external/test_api_auth.py -v

# Test API endpoints
pytest tests/external/test_external_api.py -v
```

### **2. Test Integrazione Python**
**File:** `scripts/test_external_api.py`

**Scenario Completo:**
```python
1. Lista workflow disponibili
2. Avvia workflow enhanced_article
3. Polling status ogni 2 secondi
4. Recupera risultato finale
5. Verifica contenuto generato
6. Lista jobs recenti
```

**Esecuzione:**
```bash
python scripts/test_external_api.py
```

**Output Atteso:**
```
🧪 Testing External API...
1. 📋 Listing available workflows... ✅
2. 🚀 Starting workflow... ✅ job_id: abc123
3. 🔄 Polling status... running (30%) → completed (100%)
4. 📄 Getting result... ✅ Content generated!
5. 📊 Listing jobs... Found 1 jobs
```

### **3. Test cURL Commands**
**File:** `scripts/test_curl_commands.sh`

**Comandi Automatici:**
```bash
# Lista workflow
curl -H "Authorization: Bearer $API_KEY" /api/v1/external/workflows

# Avvia workflow
curl -X POST -H "Authorization: Bearer $API_KEY" \
  -d '{"topic":"AI Test"}' /api/v1/external/workflows/enhanced_article

# Controlla status
curl -H "Authorization: Bearer $API_KEY" /api/v1/external/jobs/{job_id}/status
```

### **4. Test Browser (Swagger UI)**
```
URL: http://localhost:8000/docs
1. Click "Authorize"
2. Inserisci: Bearer cgs-api-key-12345-test-local
3. Testa endpoint interattivamente
```

---

## 🚀 PROCEDURA DEPLOYMENT

### **Setup Locale (Sviluppo)**
```bash
# 1. Aggiorna .env
echo "EXTERNAL_API_KEY=cgs-api-key-12345-test-local" >> .env

# 2. Installa dipendenze (se nuove)
pip install -r requirements.txt

# 3. Avvia server
python -m api.rest.main

# 4. Test rapido
python scripts/test_external_api.py
```

### **Verifica Funzionamento**
```bash
# Server attivo su http://localhost:8000
# Documentazione API: http://localhost:8000/docs
# Test endpoint: http://localhost:8000/api/v1/external/workflows
```

---

## 📊 ESEMPI INTEGRAZIONE

### **JavaScript/Node.js**
```javascript
// Avvia workflow
const response = await fetch('http://localhost:8000/api/v1/external/workflows/enhanced_article', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer cgs-api-key-12345-test-local',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    topic: 'AI in Finance',
    client_profile: 'siebert'
  })
});

const { job_id } = await response.json();

// Polling status
const checkStatus = async () => {
  const statusResponse = await fetch(`http://localhost:8000/api/v1/external/jobs/${job_id}/status`, {
    headers: { 'Authorization': 'Bearer cgs-api-key-12345-test-local' }
  });

  const { status, progress } = await statusResponse.json();

  if (status === 'completed') {
    // Recupera risultato
    const resultResponse = await fetch(`http://localhost:8000/api/v1/external/jobs/${job_id}/result`, {
      headers: { 'Authorization': 'Bearer cgs-api-key-12345-test-local' }
    });

    const result = await resultResponse.json();
    console.log('Contenuto generato:', result.result.body);
  }
};
```

### **Python Client**
```python
import requests
import time

API_KEY = "cgs-api-key-12345-test-local"
BASE_URL = "http://localhost:8000"

headers = {"Authorization": f"Bearer {API_KEY}"}

# Avvia workflow
response = requests.post(
    f"{BASE_URL}/api/v1/external/workflows/enhanced_article",
    headers=headers,
    json={"topic": "AI Testing", "client_profile": "siebert"}
)

job_id = response.json()["job_id"]

# Attendi completamento
while True:
    status_response = requests.get(f"{BASE_URL}/api/v1/external/jobs/{job_id}/status", headers=headers)
    status = status_response.json()["status"]

    if status == "completed":
        result_response = requests.get(f"{BASE_URL}/api/v1/external/jobs/{job_id}/result", headers=headers)
        result = result_response.json()
        print("Contenuto:", result["result"]["body"])
        break

    time.sleep(2)
```

### **WordPress Plugin (Esempio)**
```php
<?php
// WordPress plugin per CGS integration
function cgs_generate_content($topic, $client_profile = 'default') {
    $api_key = get_option('cgs_api_key');
    $base_url = get_option('cgs_base_url', 'http://localhost:8000');

    // Avvia workflow
    $response = wp_remote_post($base_url . '/api/v1/external/workflows/enhanced_article', [
        'headers' => [
            'Authorization' => 'Bearer ' . $api_key,
            'Content-Type' => 'application/json'
        ],
        'body' => json_encode([
            'topic' => $topic,
            'client_profile' => $client_profile
        ])
    ]);

    $job_data = json_decode(wp_remote_retrieve_body($response), true);
    $job_id = $job_data['job_id'];

    // Polling status (implementare con AJAX per UI non bloccante)
    return $job_id;
}
```

---

## 🔮 ROADMAP ESTENSIONI FUTURE

### **FASE 2: Scalabilità**
- **Redis Storage:** Persistenza job tra restart
- **Database Jobs:** Storico completo lavori
- **Rate Limiting:** Protezione abuse
- **Webhook Notifications:** Notifiche automatiche completamento

### **FASE 3: Funzionalità Avanzate**
- **Batch Processing:** Multipli workflow simultanei
- **Priority Queues:** Job prioritari
- **Scheduled Jobs:** Workflow programmati
- **Custom Workflows:** Upload workflow personalizzati

### **FASE 4: Monitoring & Analytics**
- **Dashboard Admin:** Monitoraggio job in tempo reale
- **Usage Analytics:** Statistiche utilizzo API
- **Performance Metrics:** Tempi esecuzione, successi/errori
- **Billing Integration:** Tracking costi per client

### **FASE 5: Enterprise Features**
- **Multi-tenant:** Isolamento dati per client
- **SSO Integration:** Autenticazione enterprise
- **API Versioning:** Backward compatibility
- **SLA Monitoring:** Garanzie performance

---

## ✅ CHECKLIST IMPLEMENTAZIONE

### **Pre-Sviluppo**
- [ ] Backup codebase attuale
- [ ] Verifica ambiente sviluppo funzionante
- [ ] Conferma workflow esistenti operativi

### **Sviluppo Core**
- [ ] Implementa `job_manager.py`
- [ ] Implementa `api_key_auth.py`
- [ ] Implementa `workflows.py` (external API)
- [ ] Aggiorna `settings.py`
- [ ] Aggiorna `main.py` FastAPI

### **Testing**
- [ ] Crea script `test_external_api.py`
- [ ] Crea script `test_curl_commands.sh`
- [ ] Test unitari job manager
- [ ] Test autenticazione
- [ ] Test integrazione completa

### **Documentazione**
- [ ] README API esterni
- [ ] Esempi integrazione
- [ ] Guida troubleshooting

### **Deployment**
- [ ] Aggiorna `.env.example`
- [ ] Test deployment locale
- [ ] Verifica documentazione Swagger
- [ ] Test performance base

---

## 🎯 CRITERI SUCCESSO

### **Funzionalità Minime**
- ✅ API accetta richieste autenticate
- ✅ Job vengono creati e tracciati
- ✅ Workflow esistenti eseguiti correttamente
- ✅ Risultati recuperabili via API
- ✅ Error handling robusto

### **Performance Target**
- **Response Time:** < 200ms per status check
- **Job Creation:** < 500ms
- **Concurrent Jobs:** Almeno 5 simultanei
- **Uptime:** 99%+ durante test

### **Sicurezza Minima**
- ✅ Autenticazione API key obbligatoria
- ✅ Input validation completa
- ✅ Error messages non espongono internals
- ✅ Logging accessi e errori

---

## 🚀 PROSSIMI STEP

1. **Conferma Piano** ✅
2. **Implementazione Core** (30-45 min)
3. **Testing Locale** (15 min)
4. **Documentazione** (15 min)
5. **Demo & Feedback** 🎉

**Pronto per iniziare l'implementazione?** 🔥
