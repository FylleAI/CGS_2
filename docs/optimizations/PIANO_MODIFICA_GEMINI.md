# Piano Modifica: Gemini Pro 2.5 per Onboarding

**Data**: 2025-10-16  
**Obiettivo**: Configurare payload Onboarding per usare Gemini Pro 2.5 (eccetto Perplexity)

---

## 🎯 OBIETTIVO

Fare in modo che tutti i payload in arrivo da **Onboarding** utilizzino sempre **Gemini Pro 2.5** per gli agent, ad eccezione della ricerca web dove continuiamo a usare **Perplexity (sonar-pro)**.

---

## 📊 SITUAZIONE ATTUALE

### ❌ **Problema**
- PayloadBuilder NON specifica `requested_provider` di default
- CGS API usa `provider="openai"` come default hardcoded
- Risultato: Onboarding usa OpenAI invece di Gemini

### ✅ **Cosa Funziona Già**
- PayloadBuilder supporta parametro `requested_provider`
- CgsAdapter passa `requested_provider` a CGS se specificato
- AgentExecutor supporta Gemini Pro 2.5
- PerplexityResearchTool è indipendente (usa sempre sonar-pro)

---

## 🔧 MODIFICHE NECESSARIE

### **Modifica 1: PayloadBuilder - LinkedIn Payload**

**File**: `onboarding/application/builders/payload_builder.py`  
**Riga**: 134-139

**Prima**:
```python
# Build metadata
metadata = CgsPayloadMetadata(
    source="onboarding_adapter",
    dry_run=dry_run,
    requested_provider=requested_provider,  # ← None se non specificato
    language="it",
)
```

**Dopo**:
```python
# Build metadata
metadata = CgsPayloadMetadata(
    source="onboarding_adapter",
    dry_run=dry_run,
    requested_provider=requested_provider or "gemini",  # ← DEFAULT: gemini
    language="it",
)
```

---

### **Modifica 2: PayloadBuilder - Newsletter Payload**

**File**: `onboarding/application/builders/payload_builder.py`  
**Riga**: 194-199

**Prima**:
```python
# Build metadata
metadata = CgsPayloadMetadata(
    source="onboarding_adapter",
    dry_run=dry_run,
    requested_provider=requested_provider,  # ← None se non specificato
    language="it",
)
```

**Dopo**:
```python
# Build metadata
metadata = CgsPayloadMetadata(
    source="onboarding_adapter",
    dry_run=dry_run,
    requested_provider=requested_provider or "gemini",  # ← DEFAULT: gemini
    language="it",
)
```

---

### **Modifica 3: CgsAdapter - Specifica Model per Gemini**

**File**: `onboarding/infrastructure/adapters/cgs_adapter.py`  
**Riga**: 132-134

**Prima**:
```python
# Add provider if specified
if payload.metadata.requested_provider:
    request["provider"] = payload.metadata.requested_provider
```

**Dopo**:
```python
# Add provider if specified
if payload.metadata.requested_provider:
    request["provider"] = payload.metadata.requested_provider
    # Add default model for Gemini
    if payload.metadata.requested_provider == "gemini":
        request["model"] = "gemini-2.5-pro"
```

---

## 📝 RIEPILOGO MODIFICHE

| # | File | Righe | Modifica | Impatto |
|---|------|-------|----------|---------|
| 1 | `payload_builder.py` | 137 | `requested_provider or "gemini"` | LinkedIn usa Gemini |
| 2 | `payload_builder.py` | 197 | `requested_provider or "gemini"` | Newsletter usa Gemini |
| 3 | `cgs_adapter.py` | 133-136 | Aggiungi `model="gemini-2.5-pro"` | Specifica modello corretto |

**Totale**: 3 modifiche, 5 righe di codice

---

## ✅ VANTAGGI

1. **Costo**: Gemini Pro 2.5 è più economico di GPT-4o
2. **Context Window**: Gemini supporta fino a 2M tokens (vs 128K di GPT-4o)
3. **Qualità**: Gemini Pro 2.5 è competitivo con GPT-4o per content generation
4. **Flessibilità**: Override possibile passando `requested_provider` esplicito
5. **Compatibilità**: Nessun impatto su altri client CGS o profili esistenti

---

## ⚠️ PREREQUISITI

### **Environment Variables**

Verifica che `.env` contenga:

```bash
# Gemini API Key (RICHIESTO)
GEMINI_API_KEY=your-gemini-api-key-here

# Perplexity API Key (RICHIESTO per ricerca)
PERPLEXITY_API_KEY=your-perplexity-api-key-here

# Vertex AI (OPZIONALE, per Gemini via GCP)
USE_VERTEX_GEMINI=true
GCP_PROJECT_ID=your-gcp-project-id
GCP_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=.secrets/your-service-account.json
```

### **Verifica API Keys**

```bash
# Test Gemini API Key
curl -X POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -d '{"contents":[{"parts":[{"text":"Hello"}]}]}'

# Test Perplexity API Key
curl -X POST https://api.perplexity.ai/chat/completions \
  -H "Authorization: Bearer $PERPLEXITY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"sonar-pro","messages":[{"role":"user","content":"Hello"}]}'
```

---

## 🧪 PIANO DI TEST

### **Test 1: Verifica Payload**

```bash
# Crea sessione onboarding
curl -X POST http://localhost:8001/api/v1/onboarding/start \
  -H "Content-Type: application/json" \
  -d '{
    "brand_name": "Test Brand",
    "website": "https://testbrand.com",
    "goal": "linkedin_post",
    "additional_context": "AI startup"
  }'

# Verifica nei log Onboarding:
# ✅ metadata.requested_provider = "gemini"
```

### **Test 2: Verifica CGS Request**

```bash
# Nei log CGS (terminal 49), cerca:
# ✅ "provider": "gemini"
# ✅ "model": "gemini-2.5-pro"
# ✅ "client_profile": "onboarding"
```

### **Test 3: Verifica Agent Execution**

```bash
# Nei log CGS, cerca AgentExecutor:
# ✅ "Using dynamic config: gemini/gemini-2.5-pro"
# ✅ "LLM request: provider=gemini, model=gemini-2.5-pro"
```

### **Test 4: Verifica Perplexity Tool**

```bash
# Nei log CGS, cerca PerplexityResearchTool:
# ✅ "model_used": "sonar-pro"
# ✅ "provider": "perplexity"
# ✅ Tool execution separato da agent LLM calls
```

### **Test 5: Verifica Override**

```python
# Test override manuale (se necessario):
from onboarding.application.builders.payload_builder import PayloadBuilder

builder = PayloadBuilder()
payload = builder.build_payload(
    session_id=session_id,
    trace_id=trace_id,
    snapshot=snapshot,
    goal=OnboardingGoal.LINKEDIN_POST,
    requested_provider="openai"  # ← Override esplicito
)

# ✅ Deve usare OpenAI invece di Gemini
```

---

## 📋 CHECKLIST IMPLEMENTAZIONE

- [ ] **1. Backup**: Commit stato attuale su branch separato
- [ ] **2. Modifica 1**: PayloadBuilder LinkedIn (riga 137)
- [ ] **3. Modifica 2**: PayloadBuilder Newsletter (riga 197)
- [ ] **4. Modifica 3**: CgsAdapter model mapping (righe 133-136)
- [ ] **5. Test 1**: Verifica payload contiene `requested_provider="gemini"`
- [ ] **6. Test 2**: Verifica CGS riceve `provider="gemini"` e `model="gemini-2.5-pro"`
- [ ] **7. Test 3**: Verifica AgentExecutor usa Gemini
- [ ] **8. Test 4**: Verifica Perplexity continua a funzionare
- [ ] **9. Test 5**: Verifica override funziona
- [ ] **10. Test End-to-End**: Completa sessione onboarding e verifica output
- [ ] **11. Commit**: Commit modifiche con messaggio descrittivo
- [ ] **12. Push**: Push su branch Onboarding-test
- [ ] **13. Documentazione**: Aggiorna README se necessario

---

## 🚀 ESECUZIONE

### **Step 1: Verifica Servizi Attivi**

```bash
# Verifica che tutti i servizi siano running:
# - Terminal 46: Onboarding Backend (port 8001)
# - Terminal 49: CGS Backend (port 8000)
# - Terminal 50: CGS Frontend (port 3000)
# - Terminal 62: Onboarding Frontend (port 3001)
```

### **Step 2: Applica Modifiche**

```bash
# Usa str-replace-editor per modificare i 2 file
# (vedi sezione "Modifiche Necessarie" sopra)
```

### **Step 3: Restart Onboarding Backend**

```bash
# Kill terminal 46
# Restart: python -m onboarding.api.main
```

### **Step 4: Test Completo**

```bash
# Esegui tutti i test della sezione "Piano di Test"
```

### **Step 5: Commit e Push**

```bash
git add onboarding/application/builders/payload_builder.py
git add onboarding/infrastructure/adapters/cgs_adapter.py
git commit -m "feat: Configure Onboarding to use Gemini Pro 2.5 by default

- Set default requested_provider='gemini' in PayloadBuilder
- Added model='gemini-2.5-pro' mapping in CgsAdapter
- Perplexity tool continues to use sonar-pro independently
- Override still possible via requested_provider parameter

Testing:
- ✅ Verified payload contains requested_provider='gemini'
- ✅ Verified CGS receives provider='gemini' and model='gemini-2.5-pro'
- ✅ Verified AgentExecutor uses Gemini for all agents
- ✅ Verified Perplexity tool uses sonar-pro independently"

git push origin Onboarding-test
```

---

## 📊 METRICHE DI SUCCESSO

### **Prima (OpenAI)**
- Provider: OpenAI
- Model: gpt-4o
- Costo stimato: ~$0.015 per 1K tokens output
- Context window: 128K tokens

### **Dopo (Gemini)**
- Provider: Gemini
- Model: gemini-2.5-pro
- Costo stimato: ~$0.0075 per 1K tokens output (50% risparmio)
- Context window: 2M tokens (15x più grande)

### **Perplexity (Invariato)**
- Provider: Perplexity
- Model: sonar-pro
- Costo: ~$0.005 per ricerca
- Uso: Solo per tool `perplexity_search`

---

## 🔍 TROUBLESHOOTING

### **Problema 1: Gemini API Key Non Configurato**

**Errore**: `ValueError: Gemini API key not configured`

**Soluzione**:
```bash
# Aggiungi a .env:
GEMINI_API_KEY=your-api-key-here

# Restart backend:
# Kill terminal 46 e 49
# Restart entrambi
```

### **Problema 2: CGS Continua a Usare OpenAI**

**Causa**: Modifiche non applicate o backend non restartato

**Soluzione**:
```bash
# Verifica modifiche:
git diff onboarding/application/builders/payload_builder.py
git diff onboarding/infrastructure/adapters/cgs_adapter.py

# Restart backend:
# Kill terminal 46
# python -m onboarding.api.main
```

### **Problema 3: Perplexity Non Funziona**

**Causa**: API key mancante o errata

**Soluzione**:
```bash
# Verifica API key in .env:
echo $PERPLEXITY_API_KEY

# Test manuale:
curl -X POST https://api.perplexity.ai/chat/completions \
  -H "Authorization: Bearer $PERPLEXITY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"sonar-pro","messages":[{"role":"user","content":"Test"}]}'
```

---

## 📚 RIFERIMENTI

- **Analisi Completa**: `docs/ANALISI_LLM_PROVIDER_SELECTION.md`
- **Gemini Pricing**: https://ai.google.dev/pricing
- **Perplexity Docs**: https://docs.perplexity.ai/
- **CGS Architecture**: `README.md`

---

**Fine Piano** 🎯

