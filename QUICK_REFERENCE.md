# 🚀 Quick Reference: Onboarding System

**Versione**: 2.0 (Semplificata)  
**Data**: 2025-10-23

---

## 📋 Goal Types (2)

| Goal | Content Type | Workflow | Display Type | Output |
|------|--------------|----------|--------------|--------|
| `company_snapshot` | `company_snapshot` | `onboarding_content_generator` | `company_snapshot` | Card visuale |
| `content_generation` | `blog_post` | `onboarding_content_generator` | `content_preview` | Contenuto markdown |

---

## 🔄 Flusso Rapido

```
User Input → Research (Perplexity/RAG) → Synthesis (Gemini) → 
Questions → User Answers → Payload Build → CGS Execution → 
Frontend Rendering
```

---

## 📦 Payload Structure

### Company Snapshot

```python
{
  "workflow_type": "onboarding_content_generator",
  "content_type": "company_snapshot",
  "context": {
    "company_snapshot": {...},
    "clarifying_answers": {...},
    "content_type": "company_snapshot",
    "content_config": {}
  }
}
```

### Content Generation

```python
{
  "workflow_type": "onboarding_content_generator",
  "content_type": "blog_post",
  "context": {
    "company_snapshot": {...},
    "clarifying_answers": {...},
    "content_type": "blog_post",
    "content_config": {"word_count": 800}
  },
  "custom_instructions": "Highlight differentiators... | Address pain points..."
}
```

---

## 🎯 Clarifying Questions

### Generazione (Gemini)

- **Numero**: Esattamente 3
- **Tipi**: `string`, `enum`, `boolean`, `number`
- **Enum**: DEVE avere 3-5 opzioni
- **Required**: Tutte required di default

### Validazione (Backend)

```python
# collect_answers.py
if question.expected_response_type == "enum":
    if answer not in question.options:
        raise ValueError("Invalid option")
```

### Utilizzo (CGS Payload)

```python
# Passate come rich context
"context": {
    "clarifying_answers": {
        "q1": "Replit Agent",
        "q2": "Beginner",
        "q3": "Product awareness"
    }
}
```

---

## 🎨 Rendering System

### Registry Pattern

```typescript
// Register renderer
rendererRegistry.register(
  'company_snapshot',
  CompanySnapshotCardRenderer,
  extractCompanySnapshot
);

// Get renderer
const renderer = rendererRegistry.getRenderer(displayType);
```

### Fallback Cascade

```typescript
// 1. Primary
snapshot = content.metadata.company_snapshot;

// 2. Fallback root
if (!snapshot) snapshot = metadata.company_snapshot;

// 3. Fallback session
if (!snapshot) snapshot = session.snapshot;

// 4. Error
if (!snapshot) return <ErrorMessage />;
```

---

## 📁 File Chiave

### Backend

| File | Scopo |
|------|-------|
| `payload_builder.py` | Costruisce payload CGS da snapshot + answers |
| `cgs_adapter.py` | Invia payload a CGS, converte response |
| `gemini_adapter.py` | Genera snapshot + clarifying questions |
| `collect_answers.py` | Valida e raccoglie risposte utente |
| `settings.py` | Mappings goal → content_type |

### Frontend

| File | Scopo |
|------|-------|
| `RendererRegistry.ts` | Registry pattern per renderer |
| `CompanySnapshotRenderer.tsx` | Renderer per company snapshot card |
| `ContentRenderer.tsx` | Renderer fallback generico |
| `Step6Results.tsx` | Componente principale rendering |

---

## 🔧 Settings Mappings

```python
# onboarding/config/settings.py

workflow_mappings = {
    "company_snapshot": "onboarding_content_generator",
    "content_generation": "onboarding_content_generator"
}

content_type_mappings = {
    "company_snapshot": "company_snapshot",
    "content_generation": "blog_post"  # ← blog_post è il più flessibile
}
```

---

## ⚠️ Common Issues

### 1. Invalid ContentType Error

**Errore**: `'generic_content' is not a valid ContentType`

**Fix**: Usare solo ContentType validi:
- ✅ `company_snapshot`
- ✅ `blog_post`
- ✅ `linkedin_post`
- ✅ `newsletter`
- ❌ `generic_content`

### 2. Missing Snapshot in Frontend

**Errore**: `No snapshot found in session`

**Fix**: Verificare fallback cascade:
1. `content.metadata.company_snapshot`
2. `metadata.company_snapshot`
3. `session.snapshot`

### 3. Invalid Enum Answer

**Errore**: `Invalid option: {answer}`

**Fix**: Verificare che:
- Risposta sia in `question.options`
- Tipo sia corretto (string per enum)

---

## 🧪 Testing Checklist

### Company Snapshot

- [ ] RAG cache hit funziona
- [ ] RAG cache miss → Perplexity + Gemini
- [ ] 3 domande generate correttamente
- [ ] Risposte validate correttamente
- [ ] Payload costruito con `content_type=company_snapshot`
- [ ] CGS ritorna `display_type=company_snapshot`
- [ ] Frontend renderizza `CompanySnapshotCard`

### Content Generation

- [ ] Payload costruito con `content_type=blog_post`
- [ ] `custom_instructions` generato correttamente
- [ ] `word_count` estratto da risposte
- [ ] CGS ritorna contenuto markdown
- [ ] Frontend renderizza `ContentPreview`

---

## 📊 Metrics & Logs

### Success Indicators

```
✅ RAG HIT: Found context {id} (v{version}, used {count} times)
✅ Gemini: Snapshot synthesized ({n} questions)
✅ Built company snapshot payload: {company}, provider={provider}
✅ Mapped CgsPayloadOnboardingContent to request (content_type={type})
✅ CGS workflow completed: status=completed, run_id={id}
```

### Error Indicators

```
❌ CGS request failed: 400 - {"error": "...", "message": "..."}
❌ RAG MISS: No context found for {company}
❌ Synthesis failed: {error}
❌ No renderer for "{displayType}", using fallback
```

---

## 🎓 Best Practices

### 1. Payload Building

```python
# ✅ DO: Extract intelligently
topic = self._extract_topic(snapshot)
word_count = self._extract_word_count(snapshot, default=800)

# ❌ DON'T: Hardcode values
topic = "Generic topic"
word_count = 500
```

### 2. Frontend Rendering

```typescript
// ✅ DO: Use metadata-driven approach
const displayType = session.cgs_response?.content?.metadata?.display_type;
const renderer = rendererRegistry.getRenderer(displayType);

// ❌ DON'T: Hardcode rendering logic
if (session.goal === 'company_snapshot') {
  return <CompanySnapshotCard />;
}
```

### 3. Error Handling

```python
# ✅ DO: Provide context in errors
raise ValueError(f"Invalid state for collecting answers: {session.state}")

# ❌ DON'T: Generic errors
raise ValueError("Invalid state")
```

---

## 🔗 Related Documents

- **Full Analysis**: `ONBOARDING_FLOW_ANALYSIS.md`
- **Cleanup Summary**: `CLEANUP_SUMMARY.md`
- **Stable State**: `STABLE_STATE.md`

---

## 📞 Quick Commands

### Backend

```bash
# Start backend
cd onboarding && python3 -m uvicorn onboarding.api.main:app --reload --port 8001

# Check logs
tail -f logs/onboarding.log

# Test endpoint
curl -X POST http://localhost:8001/api/v1/onboarding/start \
  -H "Content-Type: application/json" \
  -d '{"brand_name": "Apple", "goal": "company_snapshot"}'
```

### Frontend

```bash
# Start frontend
cd onboarding-frontend && npm run dev

# Check console
# Open browser DevTools → Console
```

---

**Last Updated**: 2025-10-23 13:00 UTC

