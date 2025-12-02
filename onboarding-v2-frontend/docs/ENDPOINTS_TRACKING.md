# 📡 Endpoints Tracking - Onboarding & Cards

## Overview
Documentazione completa degli endpoint utilizzati dal frontend per **Onboarding** e **Cards**.

---

## 🚀 ONBOARDING ENDPOINTS

### Configurazione
- **Routing**: `api-routing.yaml` → `onboarding: LOCAL_MOCKS`
- **Mock Path**: `public/mocks/onboarding/`
- **Hook**: `client/src/hooks/useOnboarding.ts`
- **Types**: `shared/types/onboarding.ts`

---

### 1. POST `/api/v1/onboarding/start`
**Scopo**: Avvia sessione onboarding, ricerca azienda, genera snapshot e domande.

**Request Body**:
```json
{
  "brand_name": "Fylle AI",           // required
  "website": "https://fylle.ai",      // optional
  "goal": "content_generation",       // required: "company_snapshot" | "content_generation"
  "user_email": "demo@fylle.ai",      // required
  "additional_context": "Focus B2B"   // optional
}
```

**Response** (`start.json`):
```json
{
  "session_id": "uuid",
  "trace_id": "trace-id",
  "state": "awaiting_user",
  "snapshot_summary": {
    "company_name": "...",
    "industry": "...",
    "description": "...",
    "target_audience": "...",
    "tone": "...",
    "questions_count": 3
  },
  "clarifying_questions": [
    {
      "id": "q1",
      "question": "...",
      "reason": "...",
      "expected_response_type": "string|select|boolean|number",
      "options": ["..."],
      "required": true
    }
  ],
  "message": "...",
  "next_action": "POST /api/v1/onboarding/{session_id}/answers"
}
```

**Mock File**: `public/mocks/onboarding/start.json`

---

### 2. POST `/api/v1/onboarding/{session_id}/answers`
**Scopo**: Invia risposte alle domande, arricchisce snapshot, crea cards.

**Request Body**:
```json
{
  "answers": {
    "q1": "LinkedIn posts and social media",
    "q2": "B2B marketing teams in tech",
    "q3": "Educational and helpful"
  }
}
```

**Response** (`submit.json`):
```json
{
  "session_id": "uuid",
  "state": "payload_ready",
  "message": "Answers collected. 4 cards created.",
  "snapshot": { ... },
  "card_ids": ["card-1", "card-2", "card-3", "card-4"],
  "cards_created": 4,
  "cards_service_url": "/cards"
}
```

**Mock File**: `public/mocks/onboarding/submit.json`

---

### 3. GET `/api/v1/onboarding/{session_id}/status`
**Scopo**: Stato sessione leggero (per polling).

**Response** (`status.json`):
```json
{
  "session_id": "uuid",
  "trace_id": "...",
  "brand_name": "...",
  "goal": "content_generation",
  "state": "awaiting_user",
  "created_at": "...",
  "updated_at": "...",
  "has_snapshot": true,
  "snapshot_complete": true,
  "error_message": null
}
```

**Polling Intervals**:
- `researching`, `synthesizing`: 3000ms
- `executing`, `delivering`: 5000ms
- `awaiting_user`, `done`, `failed`: no polling

**Mock Files**:
- `status.json` - awaiting_user
- `status-executing.json` - executing
- `status-delivering.json` - delivering
- `status-done.json` - done

---

### 4. GET `/api/v1/onboarding/{session_id}`
**Scopo**: Dettagli completi sessione (include snapshot).

**Response** (`details.json`):
```json
{
  "session_id": "uuid",
  "trace_id": "...",
  "brand_name": "...",
  "website": "...",
  "goal": "content_generation",
  "user_email": "...",
  "state": "payload_ready",
  "created_at": "...",
  "updated_at": "...",
  "snapshot": { ... },
  "metadata": { ... }
}
```

**Mock File**: `public/mocks/onboarding/details.json`

---

### 5. GET `/api/v1/onboarding/health`
**Scopo**: Health check servizio.

**Response** (`health.json`):
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "perplexity": true,
    "gemini": true,
    "supabase": true,
    "cgs": false,
    "cards": true
  },
  "cgs_healthy": false
}
```

**Mock File**: `public/mocks/onboarding/health.json`

---

### Session States
```
created → researching → synthesizing → awaiting_user → payload_ready → executing → delivering → done
                                                                                              ↘ failed
```

---

## 🃏 CARDS ENDPOINTS

### Configurazione
- **Routing**: Fetch diretto da `/mocks/cards/` (no dynamic router)
- **Mock Path**: `public/mocks/cards/`
- **Hook**: `client/src/hooks/useCards.ts`
- **Types**: `shared/types/cards.ts`

---

### 1. GET `/mocks/cards/snapshot.json`
**Scopo**: Recupera tutte le cards generate.

**Response** (`snapshot.json`):
```json
{
  "sessionId": "session-abc123",
  "generatedAt": "2024-01-15T10:30:00Z",
  "cards": [
    {
      "id": "card-uuid",
      "type": "product|target|campaigns|topic|brand_voice|competitor|performance|feedback",
      "title": "...",
      "createdAt": "...",
      "updatedAt": "...",
      "sessionId": "...",
      // ... type-specific fields
    }
  ]
}
```

**Mock File**: `public/mocks/cards/snapshot.json`

---

### 2. UPDATE Card (Client-Side Only)
**Scopo**: Aggiorna card localmente (optimistic update).

**Implementazione**: `useCards().updateCard.mutate(updatedCard)`

```typescript
// Optimistic update - modifica locale immediata
updateCard.mutate({
  ...card,
  title: "Nuovo titolo",
  // ... altri campi
});
```

**Note**: Attualmente solo client-side. Per persistenza serve endpoint backend.

---

### 3. DELETE Card (Client-Side Only)
**Scopo**: Elimina card localmente.

**Implementazione**: `useCards().deleteCard.mutate(cardId)`

```typescript
deleteCard.mutate("card-uuid");
```

**Note**: Attualmente solo client-side. Per persistenza serve endpoint backend.

---

### Card Types (8 tipi)

| Type | Label IT | Campi Specifici |
|------|----------|-----------------|
| `product` | Prodotto/Servizio | valueProposition, features, differentiators, useCases, performanceMetrics |
| `target` | Target | icpName, description, painPoints, goals, preferredLanguage, communicationChannels, demographics |
| `campaigns` | Campagne | objective, keyMessages, tone, assets, results, learnings |
| `topic` | Topic | description, keywords, angles, relatedContent, trends |
| `brand_voice` | Brand Voice | toneDescription, styleGuidelines, dosExamples, dontsExamples, termsToUse, termsToAvoid |
| `competitor` | Competitor | competitorName, positioning, keyMessages, strengths, weaknesses, differentiationOpportunities |
| `performance` | Performance | period, metrics, topPerformingContent, insights |
| `feedback` | Feedback | source, summary, details, actionItems, relatedCards, priority |

---

## 📁 File Structure

```
public/mocks/
├── onboarding/
│   ├── start.json              # POST /start
│   ├── status.json             # GET /status (awaiting_user)
│   ├── status-executing.json   # GET /status (executing)
│   ├── status-delivering.json  # GET /status (delivering)
│   ├── status-done.json        # GET /status (done)
│   ├── details.json            # GET /{session_id}
│   ├── submit.json             # POST /answers
│   └── health.json             # GET /health
└── cards/
    └── snapshot.json           # GET snapshot

client/src/hooks/
├── useOnboarding.ts            # Hook onboarding
└── useCards.ts                 # Hook cards

shared/types/
├── onboarding.ts               # Types onboarding
└── cards.ts                    # Types cards
```

---

## 🔧 API Routing Config

```yaml
# api-routing.yaml
onboarding:
  endpoints: LOCAL_MOCKS
  mocks_path: ./public/mocks/onboarding/
```

Per usare backend reale:
```yaml
onboarding:
  endpoints: REMOTE
```

---

## 🔄 Future Backend Endpoints (TODO)

### Cards API (da implementare)
```
GET    /api/v1/cards                    # Lista cards
GET    /api/v1/cards/:id                # Dettaglio card
POST   /api/v1/cards                    # Crea card
PATCH  /api/v1/cards/:id                # Aggiorna card
DELETE /api/v1/cards/:id                # Elimina card
GET    /api/v1/cards/session/:sessionId # Cards per sessione
```

