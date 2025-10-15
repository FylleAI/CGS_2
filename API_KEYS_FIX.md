# 🔧 API Keys Fix - Centralizzazione .env

**Data**: 2025-10-15  
**Problema**: Dopo centralizzazione del `.env`, le chiavi API erano su più righe causando errori di autenticazione

---

## 🐛 **Problema Identificato**

### **Sintomo**
```
Error code: 401 - {'error': {'message': 'Incorrect API key provided: skproj-3*******...
```

### **Causa Root**
Le chiavi API nel `.env` erano formattate su **più righe** invece di una singola riga:

**❌ PRIMA (ERRATO)**:
```bash
OPENAI_API_KEY=sk-proj-FIRST_PART_OF_KEY
SECOND_PART_OF_KEY_ON_NEW_LINE
ANTHROPIC_API_KEY=sk-ant-api03-FIRST_PART_OF_KEY-
SECOND_PART_OF_KEY_ON_NEW_LINE
THIRD_PART_OF_KEY-ENDING
```

**Problema**: I parser `.env` (Pydantic, python-dotenv) leggono solo la prima riga, troncando la chiave.

---

## ✅ **Soluzione Implementata**

### **1. Corretto Formato Chiavi API**

**✅ DOPO (CORRETTO)**:
```bash
# AI Provider API Keys
OPENAI_API_KEY=sk-proj-YOUR_OPENAI_KEY_HERE
ANTHROPIC_API_KEY=sk-ant-api03-YOUR_ANTHROPIC_KEY_HERE
DEEPSEEK_API_KEY=sk-YOUR_DEEPSEEK_KEY_HERE
GEMINI_API_KEY=AIzaSy_YOUR_GEMINI_KEY_HERE
SERPER_API_KEY=YOUR_SERPER_KEY_HERE
PERPLEXITY_API_KEY=pplx-YOUR_PERPLEXITY_KEY_HERE
```

**Regola**: Ogni chiave API deve essere su **una singola riga**, senza interruzioni.

---

### **2. Riavviati Backend**

Dopo la correzione, riavviati entrambi i backend per caricare le chiavi corrette:

```bash
# CGS Backend
python start_backend.py

# Onboarding Backend
python -m onboarding.api.main
```

---

## 🧪 **Verifica Funzionamento**

### **Test 1: Verifica Provider Disponibili**

```bash
curl http://localhost:8000/api/v1/content/providers
```

**Risultato Atteso**:
```json
{
  "providers": [
    {
      "name": "openai",
      "available": true,
      "models": [...]
    },
    {
      "name": "anthropic",
      "available": true,
      "models": [...]
    },
    {
      "name": "deepseek",
      "available": true,
      "models": [...]
    },
    {
      "name": "gemini",
      "available": true,
      "models": [...]
    }
  ]
}
```

✅ **Tutti i provider mostrano `"available": true`**

---

### **Test 2: Verifica Vertex AI**

Vertex AI usa il file JSON delle credenziali Service Account:

**File**: `.secrets/startup-program-461116-e59705839bd1.json`

**Configurazione `.env`**:
```bash
# Vertex AI (Gemini)
USE_VERTEX_GEMINI=true
GCP_PROJECT_ID=startup-program-461116
GCP_LOCATION=us-central1
VERTEX_API_ENDPOINT=aiplatform.googleapis.com
VERTEX_API_VERSION=v1
GOOGLE_APPLICATION_CREDENTIALS=.secrets/startup-program-461116-e59705839bd1.json
```

**Verifica**:
```bash
# Controlla che il file esista
ls .secrets/startup-program-461116-e59705839bd1.json
```

---

## 📊 **Configurazione Completa Provider**

### **OpenAI**
- ✅ API Key configurata
- ✅ Modelli disponibili: gpt-4o, gpt-4o-mini, o1-preview, o1-mini, etc.
- ✅ Default: gpt-4o

### **Anthropic (Claude)**
- ✅ API Key configurata
- ✅ Modelli disponibili: claude-opus-4, claude-sonnet-4, claude-3-7-sonnet, etc.
- ✅ Default: claude-3-7-sonnet-latest

### **DeepSeek**
- ✅ API Key configurata
- ✅ Modelli disponibili: deepseek-chat, deepseek-reasoner
- ✅ Default: deepseek-chat

### **Gemini**
- ✅ API Key configurata (fallback)
- ✅ Vertex AI configurato (preferito)
- ✅ Service Account JSON presente
- ✅ Modelli disponibili: gemini-2.5-pro, gemini-2.5-flash, etc.
- ✅ Default: gemini-2.5-pro

### **Perplexity**
- ✅ API Key configurata
- ✅ Usato per research in Onboarding
- ✅ Modello: sonar-pro

### **Serper**
- ✅ API Key configurata
- ✅ Usato per web search

---

## 🔍 **Come Funziona Vertex AI**

### **Autenticazione**

Vertex AI supporta **due metodi** di autenticazione:

#### **1. Service Account (Preferito)**
```bash
GOOGLE_APPLICATION_CREDENTIALS=.secrets/startup-program-461116-e59705839bd1.json
```

Il sistema:
1. Legge il file JSON
2. Estrae le credenziali Service Account
3. Genera un OAuth2 Bearer Token
4. Usa il token per chiamate REST API a Vertex AI

**Codice** (`core/infrastructure/external_services/gemini_adapter.py`):
```python
def _get_sa_bearer_token(self) -> Optional[str]:
    """Return OAuth2 Bearer token from Service Account."""
    path = (
        os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        or self.sa_credentials_path
    )
    if not path:
        return None
    
    from google.oauth2 import service_account
    from google.auth.transport.requests import Request
    
    creds = service_account.Credentials.from_service_account_file(
        path, scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    creds.refresh(Request())
    return creds.token
```

#### **2. API Key (Fallback)**
```bash
GEMINI_API_KEY=AIzaSy_YOUR_GEMINI_KEY_HERE
```

Se Service Account non è disponibile, usa Google AI Studio API.

---

### **Chiamate API**

**Vertex AI REST Endpoint**:
```
POST https://aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models/{model}:generateContent
```

**Headers**:
```
Authorization: Bearer {oauth2_token}
Content-Type: application/json
```

**Body**:
```json
{
  "contents": [
    {
      "role": "user",
      "parts": [{"text": "Your prompt here"}]
    }
  ],
  "generation_config": {
    "temperature": 0.7,
    "max_output_tokens": 8192
  }
}
```

---

## 🎯 **Benefici della Centralizzazione**

### **Prima (Problematico)**
```
.env (root)
web/react-app/.env
onboarding/.env
```

**Problemi**:
- ❌ Chiavi duplicate in 3 file
- ❌ Disallineamento tra file
- ❌ Difficile manutenzione
- ❌ Rischio di chiavi obsolete

### **Dopo (Centralizzato)**
```
.env (root) ← UNICA FONTE DI VERITÀ
web/react-app/.env (solo REACT_APP_*)
```

**Vantaggi**:
- ✅ Chiavi API in un solo posto
- ✅ Facile aggiornamento
- ✅ Nessun disallineamento
- ✅ Configurazione unificata CGS + Onboarding

---

## 📝 **Regole per `.env`**

### **1. Formato Chiavi API**
```bash
# ✅ CORRETTO - Una singola riga
API_KEY=YOUR_COMPLETE_API_KEY_ON_SINGLE_LINE

# ❌ ERRATO - Più righe
API_KEY=FIRST_PART_OF_KEY
SECOND_PART_ON_NEW_LINE
```

### **2. Commenti**
```bash
# ✅ CORRETTO - Commento su riga separata
# OpenAI API Key
OPENAI_API_KEY=YOUR_KEY_HERE

# ❌ ERRATO - Commento inline
OPENAI_API_KEY=YOUR_KEY_HERE  # OpenAI key
```

### **3. Valori con Spazi**
```bash
# ✅ CORRETTO - Usa virgolette
APP_NAME="My Application Name"

# ❌ ERRATO - Senza virgolette
APP_NAME=My Application Name
```

### **4. Percorsi File**
```bash
# ✅ CORRETTO - Percorso relativo o assoluto
GOOGLE_APPLICATION_CREDENTIALS=.secrets/service-account.json

# ✅ CORRETTO - Percorso assoluto Windows
GOOGLE_APPLICATION_CREDENTIALS=C:\Users\david\Desktop\onboarding\.secrets\service-account.json

# ⚠️ ATTENZIONE - Usa forward slash o doppio backslash
GOOGLE_APPLICATION_CREDENTIALS=.secrets/service-account.json
# oppure
GOOGLE_APPLICATION_CREDENTIALS=.secrets\\service-account.json
```

---

## 🚀 **Status Finale**

### ✅ **Tutti i Servizi Operativi**

| Servizio | URL | Status |
|----------|-----|--------|
| CGS Backend | http://localhost:8000 | ✅ Running |
| CGS Frontend | http://localhost:3000 | ✅ Running |
| Onboarding Backend | http://localhost:8001 | ✅ Running |
| Onboarding Frontend | http://localhost:3001 | ✅ Running |

### ✅ **Tutti i Provider Configurati**

| Provider | Status | Autenticazione |
|----------|--------|----------------|
| OpenAI | ✅ Available | API Key |
| Anthropic | ✅ Available | API Key |
| DeepSeek | ✅ Available | API Key |
| Gemini | ✅ Available | Vertex AI (Service Account) + API Key (fallback) |
| Perplexity | ✅ Available | API Key |
| Serper | ✅ Available | API Key |

---

## 🔧 **Troubleshooting**

### **Problema**: Provider mostra `"available": false`

**Soluzione**:
1. Verifica che la chiave API sia su **una singola riga** nel `.env`
2. Riavvia il backend:
   ```bash
   # Ctrl+C per fermare
   python start_backend.py
   ```
3. Verifica di nuovo:
   ```bash
   curl http://localhost:8000/api/v1/content/providers
   ```

### **Problema**: Vertex AI non funziona

**Soluzione**:
1. Verifica che il file JSON esista:
   ```bash
   ls .secrets/startup-program-461116-e59705839bd1.json
   ```
2. Verifica configurazione `.env`:
   ```bash
   USE_VERTEX_GEMINI=true
   GCP_PROJECT_ID=startup-program-461116
   GOOGLE_APPLICATION_CREDENTIALS=.secrets/startup-program-461116-e59705839bd1.json
   ```
3. Controlla i log del backend per errori di autenticazione

### **Problema**: Errore 401 "Incorrect API key"

**Soluzione**:
1. Verifica che la chiave non sia troncata (deve essere completa)
2. Controlla che non ci siano spazi prima/dopo la chiave
3. Riavvia il backend dopo modifiche al `.env`

---

**Ultimo aggiornamento**: 2025-10-15 22:15

