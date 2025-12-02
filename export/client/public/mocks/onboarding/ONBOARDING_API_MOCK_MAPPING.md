# Onboarding API Mock Mapping Documentation

## Overview
This document describes the comprehensive mock data implementation for the **Onboarding Service**, providing modular support for the AI-powered company research and content generation onboarding flow.

The onboarding service uses Perplexity for company research, Gemini/Vertex AI for snapshot synthesis, and creates visual cards for the user.

## File Structure
```
public/
└── mocks/
    └── onboarding/
        ├── start.json                  # POST /start response
        ├── status.json                 # GET /status response  
        ├── details.json                # GET /{session_id} response
        ├── submit.json                 # POST /submit response
        ├── health.json                 # GET /health response
        └── ONBOARDING_API_MOCK_MAPPING.md
```

## Implementation Details

### Centralized API Handler
- **File**: `client/src/lib/api.ts`
- **Function**: `apiRequest<T>()`
- **Environment Variable**: `USE_MOCKED_DATA=true`

### Mock Data Flow
1. Component calls `fetch('/api/v1/onboarding/start')`
2. `apiRequest()` checks `USE_MOCKED_DATA` or routing config
3. If true, redirects to `public/mocks/onboarding/start.json`
4. If false, makes standard API call to backend

### Backend Configuration
All mock files are configured via `api-routing.yaml`:
- `onboarding` section maps endpoints to LOCAL_MOCKS strategy
- Alternative: Can use REMOTE strategy pointing to Python FastAPI backend

## API Endpoints

### 1. POST /api/v1/onboarding/start
**Description**: Starts onboarding session, researches company, generates snapshot and clarifying questions.

**Request Body**:
```json
{
  "brand_name": "Fylle AI",
  "website": "https://fylle.ai",
  "goal": "content_generation",
  "user_email": "demo@fylle.ai",
  "additional_context": "Focus on B2B SaaS content"
}
```

**Request Fields**:
- `brand_name` (required): Company/brand name to research
- `website` (optional): Company website URL for better research
- `goal` (required): Either "company_snapshot" or "content_generation"
- `user_email` (required): Email for content delivery
- `additional_context` (optional): Additional instructions or context

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
  "clarifying_questions": [...],
  "message": "...",
  "next_action": "POST /api/v1/onboarding/{session_id}/answers"
}
```

**Processing Time**: 30-60 seconds (Perplexity research + Gemini synthesis)

**States After**: `awaiting_user`

---

### 2. POST /api/v1/onboarding/{session_id}/answers
**Description**: Submits answers to clarifying questions, enriches snapshot, creates visual cards.

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
  "snapshot": {
    "version": "1.0",
    "company": {...},
    "audience": {...},
    "voice": {...},
    "insights": {...},
    "clarifying_answers": {...}
  },
  "card_ids": ["card-1", "card-2", "card-3", "card-4"],
  "cards_created": 4,
  "cards_service_url": "/cards"
}
```

**Processing Time**: 5-10 seconds

**States After**: `payload_ready`

---

### 3. GET /api/v1/onboarding/{session_id}
**Description**: Returns complete session details including full snapshot.

**Response** (`details.json`):
```json
{
  "session_id": "uuid",
  "trace_id": "...",
  "brand_name": "...",
  "website": "...",
  "goal": "content_generation",
  "state": "payload_ready",
  "snapshot": {...},
  "metadata": {...}
}
```

---

### 4. GET /api/v1/onboarding/{session_id}/status
**Description**: Returns lightweight session status (no full snapshot).

**Response** (`status.json`):
```json
{
  "session_id": "uuid",
  "state": "awaiting_user",
  "has_snapshot": true,
  "snapshot_complete": true,
  "error_message": null
}
```

**Use Case**: Polling for state changes, checking completion

---

### 5. GET /health
**Description**: Health check for onboarding service and dependencies.

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

---

## Session States

The onboarding flow progresses through these states:

1. **created** - Session initialized
2. **researching** - Calling Perplexity API for company research
3. **synthesizing** - Calling Gemini AI to create snapshot and questions
4. **awaiting_user** - Waiting for user to answer clarifying questions
5. **payload_ready** - Answers collected, snapshot enriched, cards created
6. **executing** - (Optional) Calling CGS for content generation
7. **delivering** - Sending content via email
8. **done** - Process completed successfully
9. **failed** - Error occurred

## Onboarding Goals

Two simplified goals are supported:

- **company_snapshot**: Creates visual card view of company profile
- **content_generation**: Generic content generation (blog, social, etc.)

## Company Snapshot Structure

The snapshot contains:
- **company**: Name, industry, description, offerings, differentiators, evidence
- **audience**: Primary/secondary audiences, pain points, desired outcomes
- **voice**: Tone, style guidelines, forbidden phrases, CTA preferences
- **insights**: Positioning, key messages, news, competitors
- **clarifying_questions**: 3 questions for user (dynamically generated)
- **clarifying_answers**: User's responses to questions
- **source_metadata**: Research sources (Perplexity, Gemini), costs, tokens

## Clarifying Questions

Questions are dynamically generated by Gemini based on research. Each question:
- Has unique `id` (e.g., "q1", "q2", "q3")
- Specifies `expected_response_type`: "string", "select", "boolean", "number"
- Includes `options` array for select-type questions
- Has `required` flag (default true)
- Includes `reason` explaining why it's asked

## Integration with Cards Service

After submitting answers, the service creates 4 visual cards:
1. Company Profile Card
2. Audience Persona Card
3. Brand Voice Card
4. Content Strategy Card

These cards are accessible at `/cards` route with card IDs returned in response.

## Usage in Components

### Starting Onboarding
```typescript
const { mutate: startOnboarding } = useMutation({
  mutationFn: async (data: StartOnboardingRequest) => {
    return apiRequest('/api/v1/onboarding/start', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }
});
```

### Submitting Answers
```typescript
const { mutate: submitAnswers } = useMutation({
  mutationFn: async ({ sessionId, answers }) => {
    return apiRequest(`/api/v1/onboarding/${sessionId}/answers`, {
      method: 'POST',
      body: JSON.stringify({ answers })
    });
  }
});
```

### Checking Status
```typescript
const { data: status } = useQuery({
  queryKey: ['/api/v1/onboarding', sessionId, 'status'],
  refetchInterval: 5000 // Poll every 5 seconds
});
```

## Mock Data Features

- **Realistic timing**: Mock responses simulate real processing times
- **Complete data**: All fields populated with realistic values
- **Error scenarios**: Can add error.json for testing failure states
- **Idempotency**: Same session_id returns consistent data
- **Evidence sources**: Includes sample research sources and confidence scores
- **Cost tracking**: Shows estimated API costs for transparency

## Backend Architecture (Python FastAPI)

The actual backend is built with:
- **FastAPI** - Modern Python web framework
- **Perplexity API** - Company research (sonar-pro model)
- **Gemini/Vertex AI** - Snapshot synthesis (gemini-2.5-pro)
- **Supabase** - Session persistence
- **Cards API** - Visual card creation
- **Brevo** - Email delivery (optional)

See `Onboarding/onboarding/` for full backend implementation.

## Benefits

- ✅ **Development without backend**: Frontend team can work independently
- ✅ **Realistic data**: Mock responses match actual backend contracts
- ✅ **Fast iteration**: No API calls, instant responses
- ✅ **Demo ready**: Consistent, polished data for presentations
- ✅ **Testing support**: Predictable data for automated tests
- ✅ **Easy switching**: Toggle between mock and real backend via config
