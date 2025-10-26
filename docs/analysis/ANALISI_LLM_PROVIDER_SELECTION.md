# Analisi: Selezione LLM Provider nel Flusso Onboarding → CGS

**Data**: 2025-10-16  
**Obiettivo**: Configurare tutti i payload da Onboarding per usare **Gemini Pro 2.5** (eccetto ricerca web con Perplexity)

---

## 📊 SITUAZIONE ATTUALE

### 🔄 Flusso Payload: Onboarding → CGS

```
┌─────────────────────────────────────────────────────────────────────┐
│ 1. ONBOARDING BACKEND                                               │
│    PayloadBuilder.build_payload()                                   │
│    ├─ Crea CgsPayloadLinkedInPost o CgsPayloadNewsletter           │
│    ├─ metadata.requested_provider: Optional[str] = None            │
│    └─ NO specifica provider/model di default                       │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 2. CGS ADAPTER                                                      │
│    CgsAdapter._convert_to_cgs_request()                            │
│    ├─ Converte payload → ContentGenerationRequestModel             │
│    ├─ Se metadata.requested_provider esiste:                       │
│    │  request["provider"] = metadata.requested_provider            │
│    └─ Altrimenti: NON specifica provider (usa default CGS)         │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 3. CGS API ENDPOINT                                                 │
│    POST /api/v1/content/generate                                   │
│    ContentGenerationRequestModel:                                  │
│    ├─ provider: str = "openai"  ← ⚠️ DEFAULT HARDCODED             │
│    ├─ model: str = "gpt-4o"     ← ⚠️ DEFAULT HARDCODED             │
│    └─ temperature: float = 0.7                                     │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 4. GENERATE CONTENT USE CASE                                       │
│    GenerateContentUseCase.execute()                                │
│    ├─ Usa provider_config passato dal dependency injection         │
│    ├─ AgentExecutor riceve provider_config                         │
│    └─ Tutti gli agent usano lo stesso provider_config              │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 5. AGENT EXECUTOR                                                   │
│    AgentExecutor.execute_agent()                                   │
│    ├─ _get_dynamic_provider_config(context)                        │
│    ├─ Cerca in context: provider_name, model, temperature          │
│    ├─ Se NON trovati → usa self.provider_config (default)          │
│    └─ Chiama llm_provider.generate_content(config=dynamic_config)  │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 6. TOOLS (Perplexity, Web Search, RAG, Image)                     │
│    ├─ PerplexityResearchTool: usa PERPLEXITY_API_KEY              │
│    │  └─ Modello: "sonar-pro" (hardcoded nel tool)                │
│    ├─ WebSearchTool: usa SERPER_API_KEY (Google Search)           │
│    ├─ RAGTool: usa il provider_config dell'agent                  │
│    └─ ImageGenerationTool: usa provider specifico (OpenAI/Gemini) │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔍 PUNTI CHIAVE

### 1. **Default Provider in CGS API**

**File**: `api/rest/v1/endpoints/content.py`

```python
class ContentGenerationRequestModel(BaseModel):
    provider: str = "openai"      # ← DEFAULT
    model: str = "gpt-4o"         # ← DEFAULT
    temperature: float = 0.7
```

⚠️ **Problema**: Se Onboarding NON specifica `requested_provider`, CGS usa OpenAI di default.

---

### 2. **Metadata in Payload Onboarding**

**File**: `onboarding/domain/cgs_contracts.py`

```python
class CgsPayloadMetadata(BaseModel):
    source: str = Field(default="onboarding_adapter")
    dry_run: bool = Field(default=False)
    requested_provider: Optional[str] = None  # ← Può specificare provider
    language: str = Field(default="it")
```

**File**: `onboarding/application/builders/payload_builder.py`

```python
def build_payload(
    self,
    session_id: UUID,
    trace_id: str,
    snapshot: CompanySnapshot,
    goal: OnboardingGoal,
    dry_run: bool = False,
    requested_provider: Optional[str] = None,  # ← Parametro disponibile
) -> CgsPayloadLinkedInPost | CgsPayloadNewsletter:
```

✅ **Soluzione**: PayloadBuilder già supporta `requested_provider`, ma NON lo usa di default.

---

### 3. **Conversione Payload → CGS Request**

**File**: `onboarding/infrastructure/adapters/cgs_adapter.py`

```python
def _convert_to_cgs_request(
    self,
    payload: CgsPayloadLinkedInPost | CgsPayloadNewsletter,
) -> Dict[str, Any]:
    # Base request
    request = {
        "workflow_type": payload.workflow,
        "client_profile": payload.input.client_profile,
    }
    
    # Add provider if specified
    if payload.metadata.requested_provider:
        request["provider"] = payload.metadata.requested_provider
```

✅ **Funziona**: Se `metadata.requested_provider` è impostato, viene passato a CGS.

---

### 4. **Agent Executor - Dynamic Config**

**File**: `core/infrastructure/orchestration/agent_executor.py`

```python
def _get_dynamic_provider_config(self, context: Dict[str, Any]) -> ProviderConfig:
    """Get dynamic provider config from context or use default."""
    provider_name = context.get("provider_name") or context.get("provider")
    model = context.get("model")
    temperature = context.get("temperature")
    
    # Create dynamic config
    if provider_name:
        provider = LLMProvider(provider_name)
    else:
        provider = self.provider_config.provider  # ← Usa default
    
    # Use model from context or default for provider
    if not model:
        defaults = {
            LLMProvider.OPENAI: "gpt-4o",
            LLMProvider.ANTHROPIC: "claude-3-7-sonnet-latest",
            LLMProvider.DEEPSEEK: "deepseek-chat",
            LLMProvider.GEMINI: "gemini-2.5-pro",  # ← ✅ Gemini supportato
        }
        model = defaults.get(provider, self.provider_config.model)
```

✅ **Supporto Gemini**: AgentExecutor supporta già Gemini Pro 2.5.

---

### 5. **Tools - Perplexity**

**File**: `core/infrastructure/tools/perplexity_research_tool.py`

```python
class PerplexityResearchTool:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = 30,
    ):
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        self.model = model or "sonar-pro"  # ← Modello Perplexity
```

✅ **Indipendente**: Perplexity usa il proprio modello, NON il provider_config degli agent.

---

### 6. **Provider Factory - Gemini**

**File**: `core/infrastructure/factories/provider_factory.py`

```python
@staticmethod
def create_provider(provider_type: LLMProvider, settings: Settings) -> LLMProviderInterface:
    if provider_type == LLMProvider.GEMINI:
        api_key = settings.gemini_api_key
        if not api_key:
            raise ValueError("Gemini API key not configured")
        return GeminiAdapter(api_key)
```

✅ **Gemini Supportato**: Factory può creare GeminiAdapter.

---

## 🎯 COSA DOBBIAMO MODIFICARE

### ✅ **Obiettivo**
- Tutti i payload da Onboarding usano **Gemini Pro 2.5** per gli agent
- Perplexity continua a usare **sonar-pro** per ricerca web
- Nessuna modifica ai tool (Perplexity, Web Search, RAG, Image)

---

### 📝 **Modifiche Necessarie**

#### **1. PayloadBuilder - Imposta Default Provider**

**File**: `onboarding/application/builders/payload_builder.py`

**Modifica**: Nelle funzioni `_build_linkedin_payload()` e `_build_newsletter_payload()`:

```python
# Build metadata
metadata = CgsPayloadMetadata(
    source="onboarding_adapter",
    dry_run=dry_run,
    requested_provider=requested_provider or "gemini",  # ← DEFAULT: gemini
    language="it",
)
```

**Righe da modificare**:
- Riga 134-139 (LinkedIn)
- Riga 194-199 (Newsletter)

**Impatto**: 
- ✅ Se `requested_provider` NON è specificato → usa "gemini"
- ✅ Se `requested_provider` è specificato → usa quello (override possibile)

---

#### **2. CgsAdapter - Aggiungi Model Default**

**File**: `onboarding/infrastructure/adapters/cgs_adapter.py`

**Modifica**: In `_convert_to_cgs_request()`:

```python
# Add provider if specified
if payload.metadata.requested_provider:
    request["provider"] = payload.metadata.requested_provider
    # Add default model for Gemini
    if payload.metadata.requested_provider == "gemini":
        request["model"] = "gemini-2.5-pro"
```

**Righe da modificare**:
- Riga 132-134

**Impatto**:
- ✅ Quando provider è "gemini" → specifica anche model "gemini-2.5-pro"
- ✅ Evita che CGS usi il default "gpt-4o"

---

#### **3. (Opzionale) CGS API - Cambia Default**

**File**: `api/rest/v1/endpoints/content.py`

**Modifica**: Cambia default in `ContentGenerationRequestModel`:

```python
class ContentGenerationRequestModel(BaseModel):
    provider: str = "gemini"           # ← Cambiato da "openai"
    model: str = "gemini-2.5-pro"      # ← Cambiato da "gpt-4o"
    temperature: float = 0.7
```

**Righe da modificare**:
- Riga 36-37

**Impatto**:
- ⚠️ Cambia default per TUTTE le richieste CGS (non solo Onboarding)
- ✅ Utile se vuoi Gemini come default globale
- ❌ Potrebbe rompere altri client che si aspettano OpenAI

**Raccomandazione**: NON modificare (lascia OpenAI come default globale CGS).

---

## 📋 RIEPILOGO MODIFICHE

| File | Riga | Modifica | Priorità |
|------|------|----------|----------|
| `onboarding/application/builders/payload_builder.py` | 137 | `requested_provider or "gemini"` | ✅ **ALTA** |
| `onboarding/application/builders/payload_builder.py` | 197 | `requested_provider or "gemini"` | ✅ **ALTA** |
| `onboarding/infrastructure/adapters/cgs_adapter.py` | 133-136 | Aggiungi `model="gemini-2.5-pro"` | ✅ **ALTA** |
| `api/rest/v1/endpoints/content.py` | 36-37 | Cambia default globale | ❌ **BASSA** (sconsigliato) |

---

## ✅ VERIFICA POST-MODIFICA

### **Test 1: Payload Onboarding → CGS**

```bash
# Crea sessione onboarding
curl -X POST http://localhost:8001/api/v1/onboarding/start \
  -H "Content-Type: application/json" \
  -d '{"brand_name":"Test","website":"https://test.com","goal":"linkedin_post"}'

# Verifica nei log CGS:
# ✅ Deve mostrare: provider='gemini', model='gemini-2.5-pro'
```

### **Test 2: Perplexity Tool**

```bash
# Verifica nei log CGS durante ricerca:
# ✅ Deve mostrare: PerplexityResearchTool usando model='sonar-pro'
# ✅ Agent executor usando provider='gemini', model='gemini-2.5-pro'
```

### **Test 3: Override Provider**

```python
# Nel codice onboarding, testa override:
payload = builder.build_payload(
    session_id=session_id,
    trace_id=trace_id,
    snapshot=snapshot,
    goal=goal,
    requested_provider="openai"  # ← Override
)
# ✅ Deve usare OpenAI invece di Gemini
```

---

## 🔧 CONFIGURAZIONE NECESSARIA

### **Environment Variables**

Assicurati che `.env` contenga:

```bash
# Gemini API Key (richiesto)
GEMINI_API_KEY=your-gemini-api-key

# Perplexity API Key (richiesto per ricerca)
PERPLEXITY_API_KEY=your-perplexity-api-key

# Vertex AI (opzionale, per Gemini via GCP)
USE_VERTEX_GEMINI=true
GCP_PROJECT_ID=your-gcp-project
GCP_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=.secrets/your-service-account.json
```

---

## 🎯 PROSSIMI PASSI

1. ✅ **Modifica PayloadBuilder** (2 righe)
2. ✅ **Modifica CgsAdapter** (3 righe)
3. ✅ **Test end-to-end** con sessione onboarding
4. ✅ **Verifica log** per confermare provider/model
5. ✅ **Commit modifiche** su branch Onboarding-test

---

## 📊 IMPATTO

### **Vantaggi**
- ✅ Gemini Pro 2.5 è più economico di GPT-4o
- ✅ Gemini ha context window più grande (2M tokens)
- ✅ Perplexity continua a funzionare per ricerca web
- ✅ Override possibile se necessario

### **Rischi**
- ⚠️ Gemini potrebbe avere latenza diversa da OpenAI
- ⚠️ Verificare qualità output con Gemini vs OpenAI
- ⚠️ Assicurarsi che GEMINI_API_KEY sia configurato

### **Compatibilità**
- ✅ Nessun breaking change per altri client CGS
- ✅ Frontend CGS continua a funzionare normalmente
- ✅ Profili cliente (Siebert, etc.) non impattati

---

**Fine Analisi** 🎯

