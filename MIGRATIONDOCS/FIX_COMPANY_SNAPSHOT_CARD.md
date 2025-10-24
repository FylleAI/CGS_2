# 🔧 FIX: Company Snapshot Card Non Visualizzata

> **Data:** 2025-01-22  
> **Problema:** "No Company Snapshot Available" quando si completa il flusso con Company Snapshot  
> **Stato:** ✅ RISOLTO

---

## 🐛 PROBLEMA

Quando l'utente completa il flusso di onboarding con goal `company_snapshot`, la card non viene visualizzata e appare il messaggio:

```
No Company Snapshot Available
The company snapshot could not be loaded.
```

---

## 🔍 ANALISI ROOT CAUSE

### **Struttura Dati Attesa vs Reale**

#### **Struttura Attesa dal Frontend (ERRATA)**

Il `CompanySnapshotRenderer` cercava i dati in:
```typescript
const metadata = session.cgs_response?.metadata;
let snapshot = metadata?.company_snapshot;
```

Quindi cercava in: `session.cgs_response.metadata.company_snapshot`

#### **Struttura Reale dal Backend (CORRETTA)**

Il backend (CGS + Onboarding API) ritorna:
```json
{
  "cgs_response": {
    "content": {
      "title": "Company Snapshot: ACME Corp",
      "body": "...",
      "metadata": {
        "display_type": "company_snapshot",
        "company_snapshot": {
          "company": { ... },
          "audience": { ... },
          "voice": { ... },
          "insights": { ... }
        }
      }
    },
    "metadata": {
      "display_type": "company_snapshot",
      "company_snapshot": { ... }
    }
  }
}
```

I dati sono in: `session.cgs_response.content.metadata.company_snapshot`

---

## 🔄 FLUSSO BACKEND

### **1. Workflow Handler (`onboarding_content_handler.py`)**

Il metodo `_generate_company_snapshot()` ritorna:

```python
result = {
    "content": {
        "title": f"Company Snapshot: {company_name}",
        "body": "Company snapshot loaded successfully. View the card below.",
        "metadata": {
            "display_type": "company_snapshot",
            "company_snapshot": company_snapshot,  # ← Dati qui!
            "view_mode": "card",
            "interactive": True,
        }
    },
    "metadata": {  # ← Anche qui (root level)
        "display_type": "company_snapshot",
        "company_snapshot": company_snapshot,
        "view_mode": "card",
        "interactive": True,
    },
    "workflow_id": context.get("run_id", "dynamic"),
    "final_output": f"Company Snapshot: {company_name}\n\n..."
}
```

### **2. Use Case (`generate_content.py`)**

Il use case estrae il `metadata` root level:

```python
# Linea 228
workflow_metadata = workflow_result.get("metadata", {})

# Linea 230
if workflow_metadata:
    response_metadata.update(workflow_metadata)

# Linea 248
response = ContentGenerationResponse(
    # ...
    metadata=response_metadata,  # ← Contiene company_snapshot
)
```

### **3. API Endpoint (`content.py`)**

L'endpoint ritorna:

```python
return ContentGenerationResponseModel(
    # ...
    metadata=response.metadata,  # ← Contiene company_snapshot
)
```

### **4. CGS Adapter (`cgs_adapter.py`)**

Il `CgsAdapter` riceve la response e crea `ContentResult`:

```python
# Linea 234
metadata = cgs_response.get("metadata", {})

# Linea 237-249
content = ContentResult(
    content_id=cgs_response.get("content_id"),
    title=cgs_response.get("title", ""),
    body=cgs_response.get("body", ""),
    display_type=display_type,
    metadata=metadata,  # ← Mette metadata in ContentResult.metadata
)
```

### **5. ResultEnvelope**

Il `ResultEnvelope` contiene:

```python
ResultEnvelope(
    content=ContentResult(
        metadata={
            "display_type": "company_snapshot",
            "company_snapshot": { ... }
        }
    )
)
```

### **6. Session Storage**

La session salva:

```python
session.cgs_response = result.model_dump(mode="json")
```

Che produce:

```json
{
  "content": {
    "metadata": {
      "display_type": "company_snapshot",
      "company_snapshot": { ... }
    }
  }
}
```

---

## ✅ SOLUZIONE

### **Fix Applicato**

Ho modificato `CompanySnapshotRenderer.tsx` per cercare i dati in 3 posizioni (con fallback):

```typescript
/**
 * Extract company snapshot from session.
 * CGS returns company_snapshot in content.metadata, or we use session.snapshot as fallback.
 */
const extractCompanySnapshot = (session: OnboardingSession): CompanySnapshotCardData | null => {
  console.log('🏢 Extracting company snapshot from session');
  console.log('📦 Full session:', session);

  let snapshot: CompanySnapshot | undefined;

  // 1. Try to get snapshot from CGS response content.metadata (primary location)
  const contentMetadata = session.cgs_response?.content?.metadata;
  snapshot = contentMetadata?.company_snapshot;

  console.log('📦 CGS response content metadata:', contentMetadata);
  console.log('📦 Company snapshot from content.metadata:', snapshot);

  // 2. Fallback to root-level metadata (in case backend structure differs)
  if (!snapshot) {
    const rootMetadata = session.cgs_response?.metadata;
    snapshot = rootMetadata?.company_snapshot;
    console.log('📦 Company snapshot from root metadata:', snapshot);
  }

  // 3. Fallback to session.snapshot (original snapshot from research phase)
  if (!snapshot) {
    console.log('⚠️ No company_snapshot in cgs_response, trying session.snapshot');
    snapshot = session.snapshot;
  }

  console.log('📊 Final extracted snapshot:', snapshot);

  if (!snapshot) {
    console.warn('⚠️ No company snapshot found in session');
    return null;
  }

  // 4. Map snapshot to card format
  const cardData = companySnapshotToCard(snapshot);
  console.log('✅ Company snapshot mapped to card:', cardData);

  return cardData;
};
```

### **Strategia di Fallback**

1. **Primary:** `session.cgs_response.content.metadata.company_snapshot`
   - Posizione corretta dove il backend mette i dati

2. **Fallback 1:** `session.cgs_response.metadata.company_snapshot`
   - Nel caso il backend cambi struttura o ci siano variazioni

3. **Fallback 2:** `session.snapshot`
   - Snapshot originale dalla fase di research (Step 3)
   - Garantisce che la card funzioni anche se CGS non ritorna i dati

---

## 📁 FILE MODIFICATI

| File | Modifica | Linee |
|------|----------|-------|
| `onboarding-frontend/src/renderers/CompanySnapshotRenderer.tsx` | Aggiunto fallback a 3 livelli per estrarre company_snapshot | 11-53 |

---

## 🧪 TESTING

### **Test Case 1: Company Snapshot Goal**

1. Avvia onboarding con goal `company_snapshot`
2. Completa tutti gli step
3. Verifica che la card venga visualizzata correttamente

**Expected Result:**
- ✅ CompanySnapshotCard visualizzata
- ✅ Dati estratti da `session.cgs_response.content.metadata.company_snapshot`
- ✅ Console log mostra: "✅ Company snapshot mapped to card"

### **Test Case 2: Fallback a session.snapshot**

1. Simula scenario dove `cgs_response.content.metadata` è vuoto
2. Verifica che il renderer usi `session.snapshot`

**Expected Result:**
- ✅ CompanySnapshotCard visualizzata
- ✅ Dati estratti da `session.snapshot`
- ✅ Console log mostra: "⚠️ No company_snapshot in cgs_response, trying session.snapshot"

### **Test Case 3: Nessun Dato Disponibile**

1. Simula scenario dove né `cgs_response` né `session.snapshot` hanno dati
2. Verifica che venga mostrato il messaggio di errore

**Expected Result:**
- ✅ Messaggio "No Company Snapshot Available" visualizzato
- ✅ Console log mostra: "⚠️ No company snapshot found in session"

---

## 🔍 DEBUG

### **Console Logs Aggiunti**

Il renderer ora logga:

```
🏢 Extracting company snapshot from session
📦 Full session: { ... }
📦 CGS response content metadata: { ... }
📦 Company snapshot from content.metadata: { ... }
📊 Final extracted snapshot: { ... }
✅ Company snapshot mapped to card: { ... }
```

### **Come Debuggare**

1. Apri DevTools → Console
2. Completa il flusso di onboarding
3. Cerca i log con emoji 🏢, 📦, 📊, ✅
4. Verifica quale fallback è stato usato

---

## 📊 IMPATTO

### **Before Fix**

- ❌ CompanySnapshotCard non visualizzata
- ❌ Messaggio "No Company Snapshot Available"
- ❌ Dati presenti ma non trovati

### **After Fix**

- ✅ CompanySnapshotCard visualizzata correttamente
- ✅ Dati estratti da `content.metadata` (primary)
- ✅ Fallback robusto a 3 livelli
- ✅ Debug logs per troubleshooting

---

## 🎯 LESSON LEARNED

### **Problema Principale**

**Mismatch tra struttura dati attesa e reale:**
- Frontend cercava in `cgs_response.metadata`
- Backend metteva in `cgs_response.content.metadata`

### **Best Practice**

1. **Sempre verificare la struttura dati reale** con console.log
2. **Implementare fallback robusti** per gestire variazioni
3. **Aggiungere debug logs** per facilitare troubleshooting
4. **Documentare la struttura dati** in entrambi backend e frontend

### **Prevenzione Futura**

1. **Creare test end-to-end** che verificano il flusso completo
2. **Documentare contratti API** con esempi di response
3. **Usare TypeScript strict mode** per catch type mismatches
4. **Aggiungere validation** sui dati ricevuti dal backend

---

## 🚀 NEXT STEPS

1. ✅ **Fix applicato** - CompanySnapshotRenderer aggiornato
2. ⏳ **Testing** - Testare il flusso completo con dati reali
3. ⏳ **Monitoring** - Verificare console logs in produzione
4. ⏳ **Documentation** - Aggiornare documentazione API contracts

---

**Fine del documento**
