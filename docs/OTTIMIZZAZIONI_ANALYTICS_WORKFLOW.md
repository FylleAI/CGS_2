# 🔧 Ottimizzazioni Analytics Workflow

**Data**: 2025-10-21  
**Branch**: `analytics-dashboard`  
**Obiettivo**: Fixare i problemi di rendering frontend per analytics dashboard

---

## 📋 PROBLEMI IDENTIFICATI

### **Problema 1: `display_type` non arriva al frontend**

**Root Cause**:
- Il workflow handler metteva `display_type` in `result["content"]["display_type"]`
- Il CGS use case cerca `workflow_result.get("metadata", {})` per estrarre metadata
- **Mismatch**: il campo era in `content` ma veniva cercato in `metadata` root!

**Impatto**:
- Frontend riceveva sempre `display_type="content_preview"` invece di `"analytics_dashboard"`
- Il renderer non sapeva quale componente usare

---

### **Problema 2: `analytics_data` non arriva al frontend**

**Root Cause**:
- Il workflow analytics generava testo (tramite agents standard)
- Non parsava il JSON dal body
- Non aggiungeva `analytics_data` a metadata

**Impatto**:
- Frontend non riceveva i dati strutturati per la dashboard
- `AnalyticsRenderer` ritornava `null` perché `content.analytics_data` era undefined

---

## ✅ MODIFICHE APPLICATE

### **1. Fix `_execute_standard_workflow` - Metadata Placement**

**File**: `core/infrastructure/workflows/handlers/onboarding_content_handler.py`  
**Linee**: 312-327

```python
async def _execute_standard_workflow(self, context: Dict[str, Any]) -> Dict[str, Any]:
    """Execute standard content generation workflow."""
    result = await self.execute_workflow(context)

    # Set display_type for frontend rendering in metadata
    if "content" in result and isinstance(result["content"], dict):
        if "metadata" not in result["content"]:
            result["content"]["metadata"] = {}
        result["content"]["metadata"]["display_type"] = "content_preview"
        
        # CRITICAL: Also add to root metadata for CGS use case to pick up
        result["metadata"] = result["content"]["metadata"].copy()

    return result
```

**Cosa fa**:
- ✅ Mette `display_type` in `content.metadata`
- ✅ **COPIA** `content.metadata` in `result.metadata` (root level)
- ✅ CGS use case ora trova `workflow_result.get("metadata")` correttamente

---

### **2. Fix `_generate_analytics` - JSON Parsing + Metadata**

**File**: `core/infrastructure/workflows/handlers/onboarding_content_handler.py`  
**Linee**: 557-613

```python
# Parse analytics JSON from body and add to metadata
if "content" in result and isinstance(result["content"], dict):
    import json
    
    # Initialize metadata if not present
    if "metadata" not in result["content"]:
        result["content"]["metadata"] = {}
    
    # Try to parse JSON from body
    try:
        body = result["content"].get("body", "")
        
        # Remove markdown code blocks if present
        if body.strip().startswith("```"):
            # Extract JSON from markdown code block
            lines = body.strip().split("\n")
            # Remove first line (```json or ```)
            if lines[0].startswith("```"):
                lines = lines[1:]
            # Remove last line (```)
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            body = "\n".join(lines)
        
        # Parse JSON
        analytics_data = json.loads(body.strip())
        
        # Validate structure
        required_keys = ["company_score", "content_opportunities", "optimization_insights"]
        if not all(k in analytics_data for k in required_keys):
            logger.warning(f"⚠️ Analytics JSON missing required keys: {required_keys}")
            # Still use it, but log warning
        
        # Add to metadata (both in content.metadata and root metadata)
        result["content"]["metadata"]["analytics_data"] = analytics_data
        result["content"]["metadata"]["display_type"] = "analytics_dashboard"
        
        # CRITICAL: Also add to root metadata for CGS use case to pick up
        result["metadata"] = result["content"]["metadata"].copy()
        
        logger.info("✅ Analytics JSON parsed successfully")
        logger.info(f"📦 Analytics data keys: {list(analytics_data.keys())}")
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ Failed to parse analytics JSON: {e}")
        logger.error(f"Body preview: {body[:200]}...")
        # Fallback: keep as text, use content_preview
        result["content"]["metadata"]["display_type"] = "content_preview"
        result["metadata"] = {"display_type": "content_preview"}
    except Exception as e:
        logger.error(f"❌ Unexpected error parsing analytics: {e}")
        result["content"]["metadata"]["display_type"] = "content_preview"
        result["metadata"] = {"display_type": "content_preview"}
```

**Cosa fa**:
- ✅ Parsa il JSON dal `body` generato dagli agents
- ✅ Rimuove markdown code blocks se presenti (```json ... ```)
- ✅ Valida la struttura JSON (required keys)
- ✅ Aggiunge `analytics_data` a `content.metadata`
- ✅ Aggiunge `display_type="analytics_dashboard"` a `content.metadata`
- ✅ **COPIA** `content.metadata` in `result.metadata` (root level)
- ✅ Fallback a `content_preview` se parsing fallisce

---

### **3. Miglioramento Prompt Analytics - JSON Output**

**File**: `core/infrastructure/workflows/handlers/onboarding_content_handler.py`  
**Linee**: 703-725

```python
REQUIREMENTS:
1. Company Score: Calculate based on brand voice, SEO, messaging, social strategy
2. Content Opportunities: Suggest 8-12 specific content pieces across different types
3. Optimization Insights: Analyze 4 areas with scores and actionable recommendations
4. Competitors: Identify 3-5 main competitors with analysis
5. Quick Wins: List 6-8 actionable tasks with time estimates
6. Full Report: Comprehensive markdown report (1500-2000 words) with:
   - Executive Summary
   - Content Opportunities Analysis
   - Optimization Insights (detailed)
   - Competitor Intelligence
   - Actionable Recommendations
   - KPIs to track

Be specific, actionable, and data-driven. Use the user variables to personalize recommendations.

CRITICAL OUTPUT INSTRUCTIONS:
- Return ONLY valid JSON
- Do NOT wrap in markdown code blocks (no ```json or ```)
- Do NOT add any explanatory text before or after the JSON
- Start directly with { and end with }
- Ensure all strings are properly escaped
- Use double quotes for all keys and string values
```

**Cosa fa**:
- ✅ Enfatizza che l'output deve essere **SOLO JSON**
- ✅ Specifica di **NON usare** markdown code blocks
- ✅ Riduce la probabilità che l'LLM aggiunga testo extra

---

## 🔄 FLUSSO DATI COMPLETO (DOPO FIX)

```
1. User → Onboarding Frontend
   ↓
2. Onboarding Service → CGS Backend
   payload: {
     workflow: "onboarding_content_generator",
     content_type: "analytics",
     ...
   }
   ↓
3. CGS Backend → OnboardingContentHandler.execute()
   ↓
4. Handler → _generate_analytics()
   ↓
5. _generate_analytics() → _execute_standard_workflow()
   ↓
6. Workflow → Agents (writer, editor) generano JSON
   ↓
7. _generate_analytics() → Parsa JSON dal body
   ↓
8. Result structure:
   {
     "status": "completed",
     "content": {
       "title": "Analytics Report: Company X",
       "body": "{...JSON...}",
       "metadata": {
         "display_type": "analytics_dashboard",
         "analytics_data": {...parsed JSON...}
       }
     },
     "metadata": {  ← CRITICAL: Root level metadata
       "display_type": "analytics_dashboard",
       "analytics_data": {...parsed JSON...}
     }
   }
   ↓
9. CGS Use Case → Merge workflow_result.get("metadata")
   ↓
10. ContentGenerationResponse.metadata = {
      "display_type": "analytics_dashboard",
      "analytics_data": {...}
    }
   ↓
11. CGS Adapter → Estrae metadata e crea ContentResult
   ↓
12. ResultEnvelope.content = {
      "display_type": "analytics_dashboard",
      "metadata": {
        "analytics_data": {...}
      }
    }
   ↓
13. Onboarding Service → Salva in session.cgs_response
   ↓
14. Frontend → Riceve session.cgs_response.content
   ↓
15. Step6Results → Estrae display_type
   ↓
16. RendererRegistry → Trova AnalyticsRenderer
   ↓
17. AnalyticsRenderer → Estrae analytics_data
   ↓
18. Step6Dashboard → Mostra analytics dashboard! ✅
```

---

## 🧪 TESTING

### **Test Manuale**

1. **Apri** http://localhost:3001
2. **Inserisci** azienda (es. "ikea", "netflix", "apple")
3. **Seleziona** goal: `COMPANY_ANALYTICS`
4. **Rispondi** alle 3 domande generate
5. **Clicca** "Generate"

**Risultato Atteso**:
- ✅ Workflow completa con successo
- ✅ Frontend riceve `display_type="analytics_dashboard"`
- ✅ Frontend riceve `analytics_data` con struttura completa
- ✅ `AnalyticsRenderer` viene selezionato
- ✅ `Step6Dashboard` mostra la dashboard analytics

**Log da Verificare**:

**CGS Backend**:
```
✅ Analytics JSON parsed successfully
📦 Analytics data keys: ['company_score', 'content_opportunities', ...]
📦 Merged workflow metadata: ['display_type', 'analytics_data']
```

**Frontend Console**:
```
🎨 Rendering with display_type: analytics_dashboard
✅ Analytics data extracted successfully
```

---

## 📊 METRICHE DI SUCCESSO

- ✅ `display_type` arriva correttamente al frontend
- ✅ `analytics_data` è presente e strutturato
- ✅ Renderer corretto viene selezionato
- ✅ Dashboard analytics viene mostrata
- ✅ Nessun errore di parsing JSON
- ✅ Fallback a `content_preview` se JSON invalido

---

## 🚀 PROSSIMI PASSI

1. ✅ **Test end-to-end** del flusso analytics
2. ⏳ **Verificare** che tutti i campi analytics siano popolati
3. ⏳ **Ottimizzare** prompt per migliorare qualità JSON
4. ⏳ **Considerare** structured output con Gemini (response_schema)
5. ⏳ **Creare** custom analytics agent invece di usare writer generico

---

## 📝 NOTE TECNICHE

### **Perché copiare metadata a root level?**

Il CGS use case (linea 228) fa:
```python
workflow_metadata = workflow_result.get("metadata", {})
```

Ma il workflow handler ritorna:
```python
{
  "content": {
    "metadata": {...}
  }
}
```

Quindi dobbiamo **anche** mettere metadata a root level:
```python
result["metadata"] = result["content"]["metadata"].copy()
```

### **Perché parsare JSON dal body?**

Il sistema di agents standard genera **testo**, non oggetti Python. Quindi:
1. Agents generano JSON come **stringa**
2. Viene messo in `content.body`
3. Dobbiamo **parsare** la stringa per ottenere l'oggetto
4. Poi metterlo in `metadata.analytics_data`

### **Gestione Errori**

- ✅ Rimuove markdown code blocks automaticamente
- ✅ Valida struttura JSON (required keys)
- ✅ Fallback a `content_preview` se parsing fallisce
- ✅ Log dettagliati per debugging

---

**Fine documento** 🎉

