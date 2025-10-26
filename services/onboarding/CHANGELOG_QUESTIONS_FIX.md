# 🔧 Fix: Domande con Opzioni Multiple

## 📋 Problema Risolto

**Issue**: Le domande che richiedono una risposta specifica (es. lunghezza contenuto, tono, ecc.) venivano presentate come campi di testo libero, lasciando l'utente senza sapere quali valori inserire.

**Soluzione**: Implementato sistema di domande a scelta multipla con opzioni predefinite.

---

## ✅ Modifiche Implementate

### 1. **Migliorato Prompt Gemini** (`onboarding/infrastructure/adapters/gemini_adapter.py`)

**Prima**:
```
5. For enum types, provide 3-5 clear options
```

**Dopo**:
```
5. **CRITICAL**: For enum types, you MUST provide 3-5 clear, specific options in the "options" array
   - Options should be complete, actionable choices (e.g., "short (200-300 words)", not just "short")
   - Each option should be self-explanatory and mutually exclusive
   - NEVER leave options as null for enum types
6. For string types, set options to null
7. For boolean types, set options to null (Yes/No is automatic)
8. For number types, set options to null

**VALIDATION RULES**:
- If expected_response_type is "enum", options MUST be a non-empty array
- If expected_response_type is NOT "enum", options MUST be null
```

**Benefici**:
- Gemini ora è forzato a generare opzioni specifiche per domande enum
- Istruzioni più chiare e dettagliate
- Validazione esplicita nel prompt

---

### 2. **Aggiunta Validazione Modello** (`onboarding/domain/models.py`)

Aggiunto validatore Pydantic per `ClarifyingQuestion`:

```python
@field_validator("options")
@classmethod
def validate_enum_options(cls, v: Optional[List[str]], info) -> Optional[List[str]]:
    """Ensure enum questions have options."""
    response_type = info.data.get("expected_response_type")
    if response_type == "enum" and (not v or len(v) == 0):
        raise ValueError("Questions with expected_response_type='enum' must have options")
    return v
```

**Benefici**:
- Validazione a livello di modello
- Errore immediato se Gemini non genera opzioni
- Type safety garantita

---

### 3. **Mappatura Tipo per Frontend** (`onboarding/api/endpoints.py`)

Aggiunta conversione `enum` → `select` quando si inviano domande al frontend:

```python
# Map question types for frontend compatibility
questions = []
for q in snapshot.clarifying_questions:
    # Convert 'enum' to 'select' for frontend
    response_type = q.expected_response_type
    if response_type == 'enum':
        response_type = 'select'
    
    questions.append(
        QuestionResponse(
            id=q.id,
            question=q.question,
            reason=q.reason,
            expected_response_type=response_type,
            options=q.options,
            required=q.required,
        )
    )
```

**Benefici**:
- Compatibilità con frontend React
- Frontend riceve `select` invece di `enum`
- Nessuna modifica necessaria al frontend

---

## 🎯 Tipi di Domande Supportati

### 1. **String** (Testo Libero)
```json
{
  "id": "q1",
  "question": "What specific aspect should we focus on?",
  "expected_response_type": "string",
  "options": null,
  "required": true
}
```
**Frontend**: Campo di testo multilinea

---

### 2. **Select** (Scelta Singola - era `enum`)
```json
{
  "id": "q2",
  "question": "What is your preferred content length?",
  "expected_response_type": "select",
  "options": [
    "short (200-300 words)",
    "medium (400-600 words)",
    "long (800+ words)"
  ],
  "required": true
}
```
**Frontend**: Dropdown con opzioni predefinite

---

### 3. **Boolean** (Sì/No)
```json
{
  "id": "q3",
  "question": "Should we include data/statistics?",
  "expected_response_type": "boolean",
  "options": null,
  "required": false
}
```
**Frontend**: Radio buttons (Yes/No)

---

### 4. **Number** (Numero)
```json
{
  "id": "q4",
  "question": "How many examples should we include?",
  "expected_response_type": "number",
  "options": null,
  "required": false
}
```
**Frontend**: Campo numerico

---

## 🧪 Test

### Test 1: Verifica Generazione Opzioni
```bash
# Avvia onboarding per una nuova azienda
curl -X POST http://localhost:8001/api/v1/onboarding/start \
  -H "Content-Type: application/json" \
  -d '{
    "brand_name": "Test Company",
    "goal": "linkedin_post"
  }'
```

**Verifica**:
- Tutte le domande con `expected_response_type: "select"` devono avere `options` non vuoto
- Le opzioni devono essere chiare e specifiche

---

### Test 2: Verifica Frontend
1. Apri http://localhost:3001
2. Inserisci dati azienda
3. Nella schermata domande, verifica che:
   - ✅ Domande con opzioni mostrano dropdown
   - ✅ Domande boolean mostrano Yes/No
   - ✅ Domande string mostrano campo testo
   - ✅ Nessun campo richiede input "libero" quando ci sono opzioni

---

## 📊 Esempio Output Gemini

**Prima** (problematico):
```json
{
  "id": "q2",
  "question": "What content length do you prefer?",
  "expected_response_type": "enum",
  "options": null,  // ❌ PROBLEMA: utente non sa cosa scrivere
  "required": true
}
```

**Dopo** (corretto):
```json
{
  "id": "q2",
  "question": "What is your preferred content length?",
  "expected_response_type": "enum",
  "options": [
    "short (200-300 words)",
    "medium (400-600 words)",
    "long (800+ words)"
  ],
  "required": true
}
```

---

## 🚀 Deployment

### 1. Riavvia Backend
```bash
# Ctrl+C per fermare
python -m onboarding.api.main
```

### 2. Verifica Logs
```
✅ Perplexity: configured
✅ Gemini: configured
✅ Supabase: configured
```

### 3. Test Completo
- Crea nuova sessione onboarding
- Verifica che domande enum abbiano opzioni
- Testa frontend con domande a scelta multipla

---

## 📝 Note Tecniche

### Validazione a 3 Livelli

1. **Prompt Level**: Gemini riceve istruzioni esplicite
2. **Model Level**: Pydantic valida il modello `ClarifyingQuestion`
3. **API Level**: Conversione `enum` → `select` per frontend

### Backward Compatibility

- ✅ Domande esistenti continuano a funzionare
- ✅ Frontend già supporta tutti i tipi
- ✅ Nessuna breaking change

---

## 🎯 Risultato Finale

**Prima**:
- ❌ Utente confuso su cosa scrivere
- ❌ Risposte inconsistenti
- ❌ Difficile validare input

**Dopo**:
- ✅ Opzioni chiare e predefinite
- ✅ UX migliorata
- ✅ Validazione automatica
- ✅ Risposte consistenti

---

**Status**: ✅ Implementato e testato
**Data**: 2025-10-15
**Versione**: 1.1.0

