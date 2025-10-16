# Step 4: Rich Context to CGS - COMPLETATO ✅

## 📋 Panoramica

Abbiamo completato l'integrazione del **rich context** nel flusso da Onboarding a CGS. Ora gli agent CGS hanno accesso completo a:

1. **`company_snapshot`** - Tutti i dati estratti dalla ricerca Perplexity + sintesi Gemini
2. **`clarifying_answers`** - Risposte dell'utente alle domande di chiarimento

Questo risolve il problema critico identificato nell'analisi: prima solo i parametri estratti venivano passati a CGS, perdendo informazioni preziose come `differentiators`, `pain_points`, `style_guidelines`, `key_messages`, `forbidden_phrases`.

---

## 🎯 Problema Risolto

### **Prima (Data Loss)**

```
Onboarding → CGS
├─ company_snapshot (salvato in Supabase) ❌ NON inviato a CGS
├─ clarifying_answers (salvato in Supabase) ❌ NON inviato a CGS
└─ input parameters (estratti) ✅ Inviati a CGS
   ├─ topic
   ├─ target_audience
   ├─ tone
   └─ context (solo description + offerings)
```

**Risultato**: Gli agent CGS non avevano accesso a:
- `company.differentiators` - Punti di forza unici
- `audience.pain_points` - Problemi del target
- `voice.style_guidelines` - Linee guida di scrittura
- `voice.forbidden_phrases` - Frasi da evitare
- `insights.key_messages` - Messaggi chiave da enfatizzare
- `insights.positioning` - Posizionamento di mercato

### **Dopo (Rich Context)**

```
Onboarding → CGS
├─ company_snapshot ✅ Inviato in context.company_snapshot
├─ clarifying_answers ✅ Inviato in context.clarifying_answers
└─ input parameters ✅ Inviati come prima
```

**Risultato**: Gli agent CGS hanno accesso completo a tutti i dati!

---

## 🔧 Modifiche Implementate

### 1. **CgsAdapter - Inclusione Rich Context**

**File**: `onboarding/infrastructure/adapters/cgs_adapter.py`

**Modifiche** (righe 117-160):

```python
def _convert_to_cgs_request(
    self,
    payload: CgsPayloadLinkedInPost | CgsPayloadNewsletter,
) -> Dict[str, Any]:
    """
    Convert onboarding payload to CGS API request format.
    
    Includes rich context (company_snapshot + clarifying_answers) for agents.
    """
    # Base request
    request = {
        "workflow_type": payload.workflow,
        "client_profile": payload.input.client_profile,
    }
    
    # Add provider if specified
    if payload.metadata.requested_provider:
        request["provider"] = payload.metadata.requested_provider
        if payload.metadata.requested_provider == "gemini":
            request["model"] = "gemini-2.5-pro"
    
    # 🆕 RICH CONTEXT: Add company_snapshot and clarifying_answers
    rich_context = {}
    
    if payload.company_snapshot:
        rich_context["company_snapshot"] = payload.company_snapshot.model_dump(mode="json")
        logger.info(
            f"📦 Rich context: Including company_snapshot "
            f"(industry={payload.company_snapshot.company.industry}, "
            f"differentiators={len(payload.company_snapshot.company.differentiators)})"
        )
    
    if payload.clarifying_answers:
        rich_context["clarifying_answers"] = payload.clarifying_answers
        logger.info(
            f"📦 Rich context: Including {len(payload.clarifying_answers)} clarifying answers"
        )
    
    # Add rich context to request
    if rich_context:
        request["context"] = rich_context
    
    # ... rest of the method (input parameters mapping)
```

**Cosa fa**:
- Serializza `company_snapshot` in JSON
- Aggiunge `clarifying_answers` (già dict)
- Inserisce tutto nel campo `context` della request CGS
- Logga informazioni per debugging

---

### 2. **Agent YAML - Istruzioni per Accesso Rich Context**

#### **A. RAG Specialist**

**File**: `data/profiles/onboarding/agents/rag_specialist.yaml`

**Modifiche**: Aggiunta sezione `RICH CONTEXT ACCESS`

```yaml
RICH CONTEXT ACCESS (Onboarding Sessions):
  - For onboarding clients, you have access to rich context via `context.company_snapshot`
  - Available fields:
    * context.company_snapshot.company.name - Company name
    * context.company_snapshot.company.industry - Industry
    * context.company_snapshot.company.description - Company description
    * context.company_snapshot.company.key_offerings - List of key offerings
    * context.company_snapshot.company.differentiators - Unique selling points
    * context.company_snapshot.audience.primary - Target audience
    * context.company_snapshot.audience.pain_points - Customer pain points
    * context.company_snapshot.voice.tone - Brand tone
    * context.company_snapshot.voice.style_guidelines - Writing style guidelines
    * context.company_snapshot.voice.forbidden_phrases - Phrases to avoid
    * context.company_snapshot.insights.positioning - Market positioning
    * context.company_snapshot.insights.key_messages - Core messages to emphasize
    * context.clarifying_answers - User answers to clarifying questions
  - Use this rich context to create more accurate and personalized briefs
  - Prioritize rich context over generic knowledge base content when available
```

**Guardrails aggiornati**:
- Base briefs on retrieved material **OR rich context**
- When rich context is available, use it as the **primary source of truth**

#### **B. Copywriter**

**File**: `data/profiles/onboarding/agents/copywriter.yaml`

**Modifiche**: Aggiunta sezione `RICH CONTEXT ACCESS`

```yaml
RICH CONTEXT ACCESS (Onboarding Sessions):
  - For onboarding clients, you have access to rich context via `context.company_snapshot`
  - Key fields for copywriting:
    * context.company_snapshot.company.differentiators - Highlight these unique selling points
    * context.company_snapshot.audience.pain_points - Address these in your content
    * context.company_snapshot.voice.tone - Match this tone
    * context.company_snapshot.voice.style_guidelines - Follow these writing guidelines
    * context.company_snapshot.voice.forbidden_phrases - NEVER use these phrases
    * context.company_snapshot.insights.key_messages - Emphasize these core messages
    * context.clarifying_answers - User preferences for this specific content
  - Use rich context to personalize content and maintain brand consistency
```

**Guardrails aggiornati**:
- **CRITICAL**: Never use phrases from `context.company_snapshot.voice.forbidden_phrases`
- **CRITICAL**: Always emphasize `context.company_snapshot.insights.key_messages`

#### **C. Research Specialist**

**File**: `data/profiles/onboarding/agents/research_specialist.yaml`

**Modifiche**: Aggiunta sezione `RICH CONTEXT ACCESS`

```yaml
RICH CONTEXT ACCESS (Onboarding Sessions):
  - For onboarding clients, you have access to rich context via `context.company_snapshot`
  - Key fields for research:
    * context.company_snapshot.company.industry - Focus research on this industry
    * context.company_snapshot.company.key_offerings - Research trends related to these offerings
    * context.company_snapshot.audience.primary - Target research to this audience
    * context.company_snapshot.audience.pain_points - Find solutions/statistics for these pain points
    * context.company_snapshot.insights.recent_news - Existing news (avoid duplicates)
  - Use rich context to make research more targeted and relevant
  - Avoid researching information already available in the snapshot
```

**Guardrails aggiornati**:
- When rich context is available, focus research on **NEW information** not in the snapshot

---

## 📊 Struttura Rich Context

### **Campo `context` nella Request CGS**

```json
{
  "workflow_type": "enhanced_article",
  "client_profile": "onboarding",
  "provider": "gemini",
  "model": "gemini-2.5-pro",
  "topic": "AI in Healthcare",
  "target_audience": "Healthcare professionals",
  "tone": "professional",
  "context": {
    "company_snapshot": {
      "version": "1.0",
      "snapshot_id": "uuid",
      "company": {
        "name": "Peterlegwood",
        "industry": "Healthcare AI",
        "description": "...",
        "key_offerings": ["AI diagnostics", "Patient monitoring"],
        "differentiators": ["FDA approved", "99% accuracy"]
      },
      "audience": {
        "primary": "Hospital administrators",
        "pain_points": ["High costs", "Staff shortage"]
      },
      "voice": {
        "tone": "professional",
        "style_guidelines": ["Data-driven", "Empathetic"],
        "forbidden_phrases": ["cheap", "revolutionary"]
      },
      "insights": {
        "positioning": "Enterprise-grade healthcare AI",
        "key_messages": ["Proven accuracy", "Regulatory compliant"]
      }
    },
    "clarifying_answers": {
      "q1": "Focus on cost reduction",
      "q2": "Include case studies",
      "q3": "800 words"
    }
  }
}
```

---

## 🎯 Benefici

### **Qualità del Contenuto**

| Aspetto | Prima | Dopo |
|---------|-------|------|
| **Differenziatori** | ❌ Non disponibili | ✅ Evidenziati nel contenuto |
| **Pain Points** | ❌ Non disponibili | ✅ Affrontati direttamente |
| **Style Guidelines** | ❌ Non disponibili | ✅ Rispettate |
| **Forbidden Phrases** | ❌ Non disponibili | ✅ Evitate |
| **Key Messages** | ❌ Non disponibili | ✅ Enfatizzati |
| **Positioning** | ❌ Non disponibile | ✅ Riflesso nel tono |

### **Personalizzazione**

- ✅ **Brand Voice**: Tono e stile coerenti con le linee guida
- ✅ **Target Audience**: Contenuto mirato ai pain points specifici
- ✅ **Unique Value**: Differenziatori evidenziati
- ✅ **Compliance**: Frasi proibite evitate automaticamente

### **Efficienza**

- ✅ **Meno iterazioni**: Contenuto più accurato al primo tentativo
- ✅ **Meno editing**: Rispetto automatico delle linee guida
- ✅ **Più consistenza**: Stesso brand voice in tutti i contenuti

---

## 🧪 Testing

### **Come Testare**

1. **Avviare backend Onboarding**:
   ```bash
   python -m onboarding.main
   ```

2. **Avviare backend CGS**:
   ```bash
   python main.py
   ```

3. **Creare nuova sessione** con frontend o API

4. **Verificare nei log**:
   ```
   📦 Rich context: Including company_snapshot (industry=Healthcare AI, differentiators=2)
   📦 Rich context: Including 3 clarifying answers
   ```

5. **Verificare nel contenuto generato**:
   - Differenziatori menzionati?
   - Pain points affrontati?
   - Forbidden phrases evitate?
   - Key messages enfatizzati?

---

## 📝 File Modificati

### **Modificati** (4 file):
1. ✅ `onboarding/infrastructure/adapters/cgs_adapter.py` - Rich context inclusion
2. ✅ `data/profiles/onboarding/agents/rag_specialist.yaml` - Context access instructions
3. ✅ `data/profiles/onboarding/agents/copywriter.yaml` - Context access instructions
4. ✅ `data/profiles/onboarding/agents/research_specialist.yaml` - Context access instructions

---

## ✅ Checklist Completamento

- [x] CgsAdapter modificato per includere rich context
- [x] Logging aggiunto per debugging
- [x] Agent YAML aggiornati con istruzioni
- [x] Guardrails aggiornati per usare rich context
- [x] Documentazione creata
- [ ] Test end-to-end con contenuto reale
- [ ] Verifica qualità contenuto (differenziatori, pain points, etc.)
- [ ] Verifica forbidden phrases evitate

---

**Stato**: ✅ **STEP 4 COMPLETATO**

**Pronto per**: Test end-to-end e verifica qualità contenuto

