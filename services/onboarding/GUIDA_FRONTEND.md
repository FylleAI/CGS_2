# 🎨 GUIDA FRONTEND - Quiz Onboarding

**Versione**: 1.0  
**Data**: 2025-10-14  
**Backend API**: http://localhost:8001/api/v1/onboarding

---

## 📋 INDICE

1. [Panoramica](#panoramica)
2. [Endpoint API](#endpoint-api)
3. [Flusso Completo](#flusso-completo)
4. [Modelli Dati](#modelli-dati)
5. [Implementazione Frontend](#implementazione-frontend)
6. [UI/UX Raccomandazioni](#uiux-raccomandazioni)
7. [Esempi Codice](#esempi-codice)
8. [Testing](#testing)
9. [Deployment](#deployment)

---

## 🎯 PANORAMICA

### Obiettivo

Creare un'interfaccia frontend per il quiz di onboarding che:
1. Raccoglie informazioni iniziali sul brand
2. Mostra snapshot generato dall'AI
3. Presenta domande di chiarimento dinamiche
4. Genera contenuto personalizzato
5. Mostra risultato finale

### Architettura

```
Frontend (React/Vue/Next.js)
    ↓ HTTP/REST
Onboarding API (FastAPI) :8001
    ↓
CGS Backend :8000
    ↓
Contenuto Generato
```

### Tecnologie Consigliate

- **Framework**: React, Next.js, Vue.js, o Svelte
- **HTTP Client**: fetch API, axios, o SWR
- **State Management**: React hooks, Zustand, o Pinia
- **UI Library**: Tailwind CSS, Material-UI, o Chakra UI

---

## 🔌 ENDPOINT API

### Base URL

```
http://localhost:8001/api/v1/onboarding
```

### 1. POST `/start` - Avvia Onboarding

**Descrizione**: Inizia una nuova sessione di onboarding

**Request**:
```json
{
  "brand_name": "Fylle",
  "website": "https://fylle.ai",
  "goal": "linkedin_post",
  "user_email": "[email protected]"
}
```

**Campi**:
- `brand_name` (string, required): Nome del brand
- `website` (string, required): URL del sito web
- `goal` (enum, required): Tipo di contenuto desiderato
  - `"linkedin_post"` → Enhanced Article
  - `"newsletter"` → Newsletter Standard
  - `"newsletter_premium"` → Newsletter Premium
  - `"article"` → Article
- `user_email` (string, required): Email utente

**Response** (200 OK):
```json
{
  "session_id": "9d60ab50-a232-470c-9587-71864985c406",
  "state": "researching",
  "message": "Onboarding session started"
}
```

**Errori**:
- `422 Unprocessable Entity`: Validazione fallita

---

### 2. GET `/{session_id}` - Ottieni Stato Sessione

**Descrizione**: Recupera lo stato corrente della sessione

**Response** (quando `state = "awaiting_user"`):
```json
{
  "session_id": "9d60ab50-a232-470c-9587-71864985c406",
  "state": "awaiting_user",
  "brand_name": "Fylle",
  "goal": "linkedin_post",
  "snapshot": {
    "company": {
      "name": "Fylle",
      "description": "AI-powered marketing team platform...",
      "industry": "AI-driven marketing automation",
      "website": "https://fylle.ai",
      "differentiators": [
        "AI-powered content generation",
        "Multi-agent system"
      ],
      "key_offerings": [
        "Content generation",
        "Marketing automation"
      ]
    },
    "audience": {
      "primary": "Marketing teams and business owners",
      "secondary": ["SMBs", "Agencies"],
      "pain_points": [
        "Time-consuming content creation",
        "Inconsistent brand voice"
      ],
      "desired_outcomes": [
        "Faster content production",
        "Consistent messaging"
      ]
    },
    "voice": {
      "tone": "professional, innovative, authoritative",
      "style_guidelines": [
        "Use clear, concise language",
        "Focus on value proposition"
      ],
      "cta_preferences": [
        "Learn more",
        "Get started"
      ],
      "forbidden_phrases": []
    },
    "insights": {
      "positioning": "Leading AI marketing automation platform",
      "key_messages": [
        "Scale marketing without expanding headcount",
        "AI-powered efficiency"
      ],
      "recent_news": [
        "Product launch announcement"
      ]
    }
  },
  "questions": [
    {
      "id": "q1",
      "question_text": "What are the top 3 marketing channels you're currently focusing on?",
      "expected_response_type": "string",
      "context": "This helps us tailor content to your distribution strategy",
      "example_answer": "LinkedIn, email newsletters, and blog content"
    },
    {
      "id": "q2",
      "question_text": "What is your primary goal for using Fylle?",
      "expected_response_type": "enum",
      "enum_options": [
        "Increase brand awareness",
        "Generate leads",
        "Drive sales",
        "Improve customer engagement",
        "Reduce marketing costs"
      ],
      "context": "Understanding your goal helps us optimize content",
      "example_answer": "Increase brand awareness"
    },
    {
      "id": "q3",
      "question_text": "Do you have existing brand guidelines or style guides?",
      "expected_response_type": "boolean",
      "context": "We can integrate existing guidelines into AI knowledge base",
      "example_answer": true
    }
  ]
}
```

**Response** (quando `state = "done"`):
```json
{
  "session_id": "9d60ab50-a232-470c-9587-71864985c406",
  "state": "done",
  "content_title": "Scaling Marketing Without Expanding Headcount",
  "content_preview": "## Scaling Marketing Without Expanding Headcount\n\nIn the fast-evolving...",
  "word_count": 418,
  "delivery_status": "delivered",
  "workflow_metrics": {
    "total_cost_usd": 0.0086,
    "total_tokens": 1151,
    "execution_time_seconds": 23.9,
    "agents_used": 4,
    "tasks_completed": 4,
    "tasks_failed": 0
  }
}
```

**Stati Possibili**:
- `created` - Sessione creata
- `researching` - Ricerca in corso (Perplexity)
- `synthesizing` - Sintesi snapshot (Gemini)
- `awaiting_user` - In attesa risposte utente
- `payload_ready` - Payload CGS pronto
- `executing` - Generazione contenuto in corso
- `delivering` - Invio email in corso
- `done` - Completato con successo
- `failed` - Fallito

---

### 3. POST `/{session_id}/answers` - Invia Risposte

**Descrizione**: Invia le risposte alle domande di chiarimento

**Request**:
```json
{
  "answers": {
    "q1": "LinkedIn, email newsletters, and blog content",
    "q2": "Increase brand awareness",
    "q3": true
  }
}
```

**Formato Risposte**:
- `string`: Testo libero
- `enum`: Esattamente uno dei valori in `enum_options`
- `boolean`: `true` o `false`
- `number`: Numero valido

**Response** (200 OK):
```json
{
  "session_id": "9d60ab50-a232-470c-9587-71864985c406",
  "state": "payload_ready",
  "message": "Answers received and validated"
}
```

**Errori**:
```json
{
  "detail": "Invalid answer for question q2: must be one of ['Increase brand awareness', 'Generate leads', 'Drive sales', 'Improve customer engagement', 'Reduce marketing costs']"
}
```

**Validazione Backend**:
- ✅ Tutte le domande devono avere risposta
- ✅ Enum: valore deve essere esattamente uno degli `enum_options`
- ✅ Boolean: deve essere `true` o `false`
- ✅ Number: deve essere numero valido

---

### 4. POST `/{session_id}/execute` - Esegui Generazione

**Descrizione**: Avvia la generazione del contenuto con CGS

**Request**: Nessun body

**Response** (200 OK):
```json
{
  "session_id": "9d60ab50-a232-470c-9587-71864985c406",
  "state": "executing",
  "message": "CGS workflow started"
}
```

---

### 5. GET `/health` - Health Check

**Descrizione**: Verifica stato servizi

**Response**:
```json
{
  "status": "healthy",
  "services": {
    "perplexity": true,
    "gemini": true,
    "cgs": true,
    "supabase": true,
    "brevo": false
  }
}
```

---

## 🔄 FLUSSO COMPLETO

### Diagramma Stati

```
┌─────────────────────────────────────────────────────────────┐
│                     FLUSSO ONBOARDING                        │
└─────────────────────────────────────────────────────────────┘

1. FORM INIZIALE
   ↓
   [POST /start]
   ↓
2. RESEARCH (30-40s)
   state: "researching" → "synthesizing"
   ↓
   [Poll GET /{session_id} ogni 3s]
   ↓
3. SNAPSHOT + QUIZ
   state: "awaiting_user"
   ↓
   [Mostra snapshot e domande]
   ↓
   [POST /{session_id}/answers]
   ↓
4. GENERAZIONE (20-30s)
   [POST /{session_id}/execute]
   state: "executing" → "delivering"
   ↓
   [Poll GET /{session_id} ogni 5s]
   ↓
5. RISULTATO
   state: "done"
   ↓
   [Mostra contenuto generato]
```

### Timing Indicativo

| Fase | Durata | Stato |
|------|--------|-------|
| Research (Perplexity) | 20-30s | `researching` |
| Synthesis (Gemini) | 10-15s | `synthesizing` |
| User Input | Variabile | `awaiting_user` |
| CGS Workflow | 20-30s | `executing` |
| Email Delivery | 5-10s | `delivering` |
| **Totale** | **~60-90s** | `done` |

### Strategia Polling

**Durante Research/Synthesis**:
```javascript
// Poll ogni 3 secondi
const pollResearch = async (sessionId) => {
  const interval = setInterval(async () => {
    const response = await fetch(`/api/v1/onboarding/${sessionId}`);
    const data = await response.json();
    
    if (data.state === 'awaiting_user') {
      clearInterval(interval);
      // Mostra snapshot e domande
      showQuiz(data);
    }
    
    if (data.state === 'failed') {
      clearInterval(interval);
      // Mostra errore
      showError(data);
    }
  }, 3000);
};
```

**Durante Execution**:
```javascript
// Poll ogni 5 secondi
const pollExecution = async (sessionId) => {
  const interval = setInterval(async () => {
    const response = await fetch(`/api/v1/onboarding/${sessionId}`);
    const data = await response.json();
    
    if (data.state === 'done') {
      clearInterval(interval);
      // Mostra risultato
      showResult(data);
    }
    
    if (data.state === 'failed') {
      clearInterval(interval);
      // Mostra errore
      showError(data);
    }
  }, 5000);
};
```

---

## 📦 MODELLI DATI

### TypeScript Interfaces

```typescript
// Enums
export type OnboardingGoal = 
  | 'linkedin_post' 
  | 'newsletter' 
  | 'newsletter_premium' 
  | 'article';

export type OnboardingState = 
  | 'created'
  | 'researching'
  | 'synthesizing'
  | 'awaiting_user'
  | 'payload_ready'
  | 'executing'
  | 'delivering'
  | 'done'
  | 'failed';

export type QuestionType = 'string' | 'enum' | 'boolean' | 'number';

// Models
export interface StartOnboardingRequest {
  brand_name: string;
  website: string;
  goal: OnboardingGoal;
  user_email: string;
}

export interface Question {
  id: string;
  question_text: string;
  expected_response_type: QuestionType;
  enum_options?: string[];
  context?: string;
  example_answer?: any;
}

export interface CompanyInfo {
  name: string;
  description: string;
  industry: string;
  website: string;
  differentiators: string[];
  key_offerings: string[];
}

export interface AudienceInfo {
  primary: string;
  secondary: string[];
  pain_points: string[];
  desired_outcomes: string[];
}

export interface VoiceInfo {
  tone: string;
  style_guidelines: string[];
  cta_preferences: string[];
  forbidden_phrases: string[];
}

export interface InsightsInfo {
  positioning: string;
  key_messages: string[];
  recent_news: string[];
}

export interface Snapshot {
  company: CompanyInfo;
  audience: AudienceInfo;
  voice: VoiceInfo;
  insights: InsightsInfo;
}

export interface WorkflowMetrics {
  total_cost_usd: number;
  total_tokens: number;
  execution_time_seconds: number;
  agents_used: number;
  tasks_completed: number;
  tasks_failed: number;
}

export interface OnboardingSession {
  session_id: string;
  state: OnboardingState;
  brand_name?: string;
  goal?: OnboardingGoal;
  snapshot?: Snapshot;
  questions?: Question[];
  content_title?: string;
  content_preview?: string;
  word_count?: number;
  delivery_status?: 'delivered' | 'failed';
  workflow_metrics?: WorkflowMetrics;
  message?: string;
}

export interface SubmitAnswersRequest {
  answers: Record<string, any>;
}
```

---

## 💻 IMPLEMENTAZIONE FRONTEND

### API Client

```typescript
// api/onboarding.ts
const API_BASE = 'http://localhost:8001/api/v1/onboarding';

export class OnboardingAPI {
  
  static async start(data: StartOnboardingRequest): Promise<OnboardingSession> {
    const response = await fetch(`${API_BASE}/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to start onboarding');
    }
    
    return response.json();
  }
  
  static async getSession(sessionId: string): Promise<OnboardingSession> {
    const response = await fetch(`${API_BASE}/${sessionId}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch session');
    }
    
    return response.json();
  }
  
  static async submitAnswers(
    sessionId: string,
    answers: Record<string, any>
  ): Promise<OnboardingSession> {
    const response = await fetch(`${API_BASE}/${sessionId}/answers`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ answers }),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to submit answers');
    }
    
    return response.json();
  }
  
  static async execute(sessionId: string): Promise<OnboardingSession> {
    const response = await fetch(`${API_BASE}/${sessionId}/execute`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      throw new Error('Failed to execute workflow');
    }
    
    return response.json();
  }
  
  static async healthCheck(): Promise<any> {
    const response = await fetch(`${API_BASE}/../health`);
    return response.json();
  }
}
```

### React Hook

```typescript
// hooks/useOnboarding.ts
import { useState, useEffect, useCallback } from 'react';
import { OnboardingAPI } from '../api/onboarding';
import type { OnboardingSession, OnboardingState } from '../types';

export function useOnboarding(sessionId: string | null) {
  const [session, setSession] = useState<OnboardingSession | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSession = useCallback(async () => {
    if (!sessionId) return;
    
    try {
      const data = await OnboardingAPI.getSession(sessionId);
      setSession(data);
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      return null;
    }
  }, [sessionId]);

  // Auto-polling per stati async
  useEffect(() => {
    if (!sessionId || !session) return;

    const asyncStates: OnboardingState[] = [
      'researching',
      'synthesizing',
      'executing',
      'delivering'
    ];

    if (!asyncStates.includes(session.state)) return;

    const pollInterval = session.state === 'executing' || session.state === 'delivering'
      ? 5000  // 5s per execution
      : 3000; // 3s per research

    const interval = setInterval(fetchSession, pollInterval);

    return () => clearInterval(interval);
  }, [sessionId, session?.state, fetchSession]);

  return {
    session,
    loading,
    error,
    refetch: fetchSession,
  };
}
```

### Main Component

```typescript
// components/OnboardingFlow.tsx
import { useState, useEffect } from 'react';
import { OnboardingAPI } from '../api/onboarding';
import { useOnboarding } from '../hooks/useOnboarding';
import type { StartOnboardingRequest } from '../types';

type Step = 'form' | 'research' | 'quiz' | 'generate' | 'result';

export function OnboardingFlow() {
  const [step, setStep] = useState<Step>('form');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const { session, error } = useOnboarding(sessionId);

  // Auto-advance steps based on session state
  useEffect(() => {
    if (!session) return;

    if (session.state === 'awaiting_user' && step !== 'quiz') {
      setStep('quiz');
    } else if (session.state === 'done' && step !== 'result') {
      setStep('result');
    } else if (session.state === 'failed') {
      console.error('Onboarding failed:', session);
    }
  }, [session?.state, step]);

  const handleStart = async (formData: StartOnboardingRequest) => {
    try {
      setStep('research');
      const result = await OnboardingAPI.start(formData);
      setSessionId(result.session_id);
    } catch (err) {
      console.error('Failed to start:', err);
      setStep('form');
    }
  };

  const handleSubmitAnswers = async (answers: Record<string, any>) => {
    if (!sessionId) return;

    try {
      setStep('generate');
      await OnboardingAPI.submitAnswers(sessionId, answers);
      await OnboardingAPI.execute(sessionId);
    } catch (err) {
      console.error('Failed to submit answers:', err);
      setStep('quiz');
    }
  };

  return (
    <div className="onboarding-container">
      {error && <div className="error-banner">{error}</div>}

      {step === 'form' && (
        <OnboardingForm onSubmit={handleStart} />
      )}

      {step === 'research' && (
        <LoadingResearch />
      )}

      {step === 'quiz' && session && (
        <QuizForm
          snapshot={session.snapshot}
          questions={session.questions || []}
          onSubmit={handleSubmitAnswers}
        />
      )}

      {step === 'generate' && (
        <LoadingGenerate />
      )}

      {step === 'result' && session && (
        <ResultView session={session} />
      )}
    </div>
  );
}
```

---

## 🎨 UI/UX RACCOMANDAZIONI

### Step 1: Form Iniziale

**Esempio Codice Completo**:
```typescript
// components/OnboardingForm.tsx
import { useState } from 'react';
import type { StartOnboardingRequest, OnboardingGoal } from '../types';

interface Props {
  onSubmit: (data: StartOnboardingRequest) => void;
}

export function OnboardingForm({ onSubmit }: Props) {
  const [formData, setFormData] = useState<StartOnboardingRequest>({
    brand_name: '',
    website: '',
    goal: '' as OnboardingGoal,
    user_email: '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.brand_name || formData.brand_name.length < 2) {
      newErrors.brand_name = 'Brand name must be at least 2 characters';
    }

    if (!formData.website || !/^https?:\/\/.+\..+/.test(formData.website)) {
      newErrors.website = 'Please enter a valid URL (e.g., https://example.com)';
    }

    if (!formData.user_email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.user_email)) {
      newErrors.user_email = 'Please enter a valid email address';
    }

    if (!formData.goal) {
      newErrors.goal = 'Please select a content goal';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (validate()) {
      onSubmit(formData);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="onboarding-form">
      <h1>🚀 Start Your Onboarding</h1>

      <div className="form-field">
        <label htmlFor="brand_name">Brand Name *</label>
        <input
          id="brand_name"
          type="text"
          placeholder="e.g., Fylle"
          value={formData.brand_name}
          onChange={(e) => setFormData({...formData, brand_name: e.target.value})}
          className={errors.brand_name ? 'error' : ''}
        />
        {errors.brand_name && <span className="error-text">{errors.brand_name}</span>}
      </div>

      <div className="form-field">
        <label htmlFor="website">Website *</label>
        <input
          id="website"
          type="url"
          placeholder="https://example.com"
          value={formData.website}
          onChange={(e) => setFormData({...formData, website: e.target.value})}
          className={errors.website ? 'error' : ''}
        />
        {errors.website && <span className="error-text">{errors.website}</span>}
      </div>

      <div className="form-field">
        <label htmlFor="goal">Content Goal *</label>
        <select
          id="goal"
          value={formData.goal}
          onChange={(e) => setFormData({...formData, goal: e.target.value as OnboardingGoal})}
          className={errors.goal ? 'error' : ''}
        >
          <option value="">Select a goal...</option>
          <option value="linkedin_post">LinkedIn Post (Enhanced Article)</option>
          <option value="newsletter">Newsletter (Standard)</option>
          <option value="newsletter_premium">Newsletter (Premium)</option>
          <option value="article">Article</option>
        </select>
        {errors.goal && <span className="error-text">{errors.goal}</span>}
      </div>

      <div className="form-field">
        <label htmlFor="user_email">Email *</label>
        <input
          id="user_email"
          type="email"
          placeholder="[email protected]"
          value={formData.user_email}
          onChange={(e) => setFormData({...formData, user_email: e.target.value})}
          className={errors.user_email ? 'error' : ''}
        />
        {errors.user_email && <span className="error-text">{errors.user_email}</span>}
      </div>

      <button type="submit" className="btn-primary">
        Start Onboarding
      </button>
    </form>
  );
}
```

---

### Step 2: Loading Research

```typescript
// components/LoadingResearch.tsx
import { useState, useEffect } from 'react';

export function LoadingResearch() {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress(prev => Math.min(prev + 2, 90));
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="loading-container">
      <h2>🔍 Researching Your Brand</h2>

      <div className="checklist">
        <div className="check-item">✓ Company information</div>
        <div className="check-item">✓ Industry positioning</div>
        <div className="check-item">✓ Target audience</div>
        <div className="check-item">✓ Brand voice</div>
      </div>

      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${progress}%` }} />
      </div>

      <p className="hint">This takes about 30-40 seconds</p>
    </div>
  );
}
```

---

### Step 3: Quiz Dinamico

```typescript
// components/QuizForm.tsx
import { useState } from 'react';
import type { Question, Snapshot } from '../types';

interface Props {
  snapshot?: Snapshot;
  questions: Question[];
  onSubmit: (answers: Record<string, any>) => void;
}

export function QuizForm({ snapshot, questions, onSubmit }: Props) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, any>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});

  const currentQuestion = questions[currentIndex];

  const handleAnswer = (questionId: string, value: any) => {
    setAnswers({ ...answers, [questionId]: value });
    setErrors({ ...errors, [questionId]: '' });
  };

  const validateCurrentAnswer = (): boolean => {
    const answer = answers[currentQuestion.id];

    if (answer === undefined || answer === null || answer === '') {
      setErrors({ ...errors, [currentQuestion.id]: 'This question is required' });
      return false;
    }

    // Validate enum
    if (currentQuestion.expected_response_type === 'enum') {
      if (!currentQuestion.enum_options?.includes(answer)) {
        setErrors({
          ...errors,
          [currentQuestion.id]: `Please select one of the provided options`
        });
        return false;
      }
    }

    return true;
  };

  const handleNext = () => {
    if (!validateCurrentAnswer()) return;

    if (currentIndex < questions.length - 1) {
      setCurrentIndex(currentIndex + 1);
    } else {
      onSubmit(answers);
    }
  };

  const handleBack = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  const renderQuestionInput = (question: Question) => {
    switch (question.expected_response_type) {
      case 'string':
        return (
          <textarea
            placeholder={question.example_answer || 'Your answer...'}
            value={answers[question.id] || ''}
            onChange={(e) => handleAnswer(question.id, e.target.value)}
            rows={4}
            className="input-textarea"
          />
        );

      case 'enum':
        return (
          <div className="radio-group">
            {question.enum_options?.map(option => (
              <label key={option} className="radio-label">
                <input
                  type="radio"
                  name={question.id}
                  value={option}
                  checked={answers[question.id] === option}
                  onChange={(e) => handleAnswer(question.id, e.target.value)}
                />
                <span>{option}</span>
              </label>
            ))}
          </div>
        );

      case 'boolean':
        return (
          <div className="boolean-buttons">
            <button
              type="button"
              className={`btn-boolean ${answers[question.id] === true ? 'active' : ''}`}
              onClick={() => handleAnswer(question.id, true)}
            >
              Yes
            </button>
            <button
              type="button"
              className={`btn-boolean ${answers[question.id] === false ? 'active' : ''}`}
              onClick={() => handleAnswer(question.id, false)}
            >
              No
            </button>
          </div>
        );

      case 'number':
        return (
          <input
            type="number"
            placeholder={question.example_answer || '0'}
            value={answers[question.id] || ''}
            onChange={(e) => handleAnswer(question.id, Number(e.target.value))}
            className="input-number"
          />
        );

      default:
        return null;
    }
  };

  return (
    <div className="quiz-container">
      <div className="progress-indicator">
        Question {currentIndex + 1} of {questions.length}
      </div>

      <h2>{currentQuestion.question_text}</h2>

      {currentQuestion.context && (
        <p className="context">💡 {currentQuestion.context}</p>
      )}

      <div className="question-input">
        {renderQuestionInput(currentQuestion)}
      </div>

      {errors[currentQuestion.id] && (
        <span className="error-text">{errors[currentQuestion.id]}</span>
      )}

      {currentQuestion.example_answer && currentQuestion.expected_response_type === 'string' && (
        <p className="example">Example: {currentQuestion.example_answer}</p>
      )}

      <div className="button-group">
        {currentIndex > 0 && (
          <button onClick={handleBack} className="btn-secondary">
            Back
          </button>
        )}

        <button onClick={handleNext} className="btn-primary">
          {currentIndex < questions.length - 1 ? 'Next' : 'Generate Content'}
        </button>
      </div>
    </div>
  );
}
```

---

### Step 4: Loading Generate

```typescript
// components/LoadingGenerate.tsx
export function LoadingGenerate() {
  return (
    <div className="loading-container">
      <h2>✨ Generating Your Content</h2>

      <div className="checklist">
        <div className="check-item">✓ Creating content brief</div>
        <div className="check-item">✓ Researching topic</div>
        <div className="check-item active">⏳ Writing content</div>
        <div className="check-item">⏳ Reviewing compliance</div>
      </div>

      <p className="hint">This takes about 20-30 seconds</p>
    </div>
  );
}
```

---

### Step 5: Risultato Finale

```typescript
// components/ResultView.tsx
import type { OnboardingSession } from '../types';

interface Props {
  session: OnboardingSession;
}

export function ResultView({ session }: Props) {
  const handleDownload = () => {
    const blob = new Blob([session.content_preview || ''], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${session.content_title || 'content'}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleNewSession = () => {
    window.location.reload();
  };

  return (
    <div className="result-container">
      <h1>🎉 Your Content is Ready!</h1>

      <h2>{session.content_title}</h2>

      <div className="content-preview">
        <pre>{session.content_preview}</pre>
      </div>

      <div className="metrics">
        <h3>📊 Metrics</h3>
        <div className="metrics-grid">
          <div className="metric">
            <span className="metric-label">Words</span>
            <span className="metric-value">{session.word_count}</span>
          </div>
          <div className="metric">
            <span className="metric-label">Cost</span>
            <span className="metric-value">
              ${session.workflow_metrics?.total_cost_usd.toFixed(4)}
            </span>
          </div>
          <div className="metric">
            <span className="metric-label">Time</span>
            <span className="metric-value">
              {session.workflow_metrics?.execution_time_seconds.toFixed(1)}s
            </span>
          </div>
          <div className="metric">
            <span className="metric-label">Agents</span>
            <span className="metric-value">{session.workflow_metrics?.agents_used}</span>
          </div>
        </div>
      </div>

      <div className="delivery-status">
        {session.delivery_status === 'delivered' ? (
          <span className="status-success">✉️ Sent to email</span>
        ) : (
          <span className="status-error">❌ Delivery failed</span>
        )}
      </div>

      <div className="button-group">
        <button onClick={handleDownload} className="btn-secondary">
          Download
        </button>
        <button onClick={handleNewSession} className="btn-primary">
          New Session
        </button>
      </div>
    </div>
  );
}
```

---

## 🧪 TESTING

### Test con cURL

```bash
# 1. Start onboarding
SESSION_ID=$(curl -s -X POST http://localhost:8001/api/v1/onboarding/start \
  -H "Content-Type: application/json" \
  -d '{
    "brand_name": "TestBrand",
    "website": "https://testbrand.com",
    "goal": "linkedin_post",
    "user_email": "test@testbrand.com"
  }' | jq -r '.session_id')

echo "Session ID: $SESSION_ID"

# 2. Poll status (aspettare 30-40s)
sleep 40
curl -s "http://localhost:8001/api/v1/onboarding/$SESSION_ID" | jq '.state'
# Output atteso: "awaiting_user"

# 3. Get questions
curl -s "http://localhost:8001/api/v1/onboarding/$SESSION_ID" | jq '.questions'

# 4. Submit answers
curl -X POST "http://localhost:8001/api/v1/onboarding/$SESSION_ID/answers" \
  -H "Content-Type: application/json" \
  -d '{
    "answers": {
      "q1": "LinkedIn, email newsletters, and blog content",
      "q2": "Increase brand awareness",
      "q3": true
    }
  }'

# 5. Execute workflow
curl -X POST "http://localhost:8001/api/v1/onboarding/$SESSION_ID/execute"

# 6. Poll result (aspettare 20-30s)
sleep 30
curl -s "http://localhost:8001/api/v1/onboarding/$SESSION_ID" | jq '{
  state,
  content_title,
  word_count,
  delivery_status
}'
```

### Test Frontend Locale

```bash
# 1. Avviare backend onboarding
cd /path/to/CGS_2/onboarding
python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8001 --reload

# 2. Avviare CGS backend (necessario per execute)
cd /path/to/CGS_2
python3 -m uvicorn api.rest.main:app --host 0.0.0.0 --port 8000 --reload

# 3. Avviare frontend (esempio Next.js)
cd /path/to/frontend
npm run dev
```

### Swagger UI

Documentazione API interattiva:
```
http://localhost:8001/docs
```

---

## 🚀 DEPLOYMENT

### Environment Variables

**Frontend `.env`**:
```bash
NEXT_PUBLIC_ONBOARDING_API_URL=http://localhost:8001/api/v1/onboarding
# In produzione:
# NEXT_PUBLIC_ONBOARDING_API_URL=https://api.fylle.ai/onboarding/v1
```

### CORS

Il backend ha già CORS configurato per sviluppo:

```python
# onboarding/api/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In produzione: specificare domini
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Per produzione**: Modificare `allow_origins`:
```python
allow_origins=[
    "https://app.fylle.ai",
    "https://fylle.ai",
]
```

### Build e Deploy

**Next.js**:
```bash
npm run build
npm run start
```

**React (Vite)**:
```bash
npm run build
# Deploy cartella dist/
```

**Vercel/Netlify**:
- Configurare `NEXT_PUBLIC_ONBOARDING_API_URL` nelle environment variables
- Deploy automatico da GitHub

---

## 📝 CHECKLIST SVILUPPO

### Setup Iniziale
- [ ] Creare progetto frontend (React/Next.js/Vue)
- [ ] Installare dipendenze (axios/SWR se necessario)
- [ ] Configurare TypeScript (opzionale ma raccomandato)
- [ ] Setup Tailwind CSS o UI library

### Implementazione API
- [ ] Creare `api/onboarding.ts` con tutti gli endpoint
- [ ] Implementare error handling
- [ ] Testare chiamate con cURL

### Implementazione UI
- [ ] Form iniziale con validazione
- [ ] Loading state per research
- [ ] Quiz dinamico (supporto string/enum/boolean/number)
- [ ] Loading state per generation
- [ ] Risultato finale con metriche

### Polling e Stati
- [ ] Implementare polling per stati async
- [ ] Gestire transizioni stati
- [ ] Cleanup interval su unmount

### Testing
- [ ] Test manuale flusso completo
- [ ] Test validazione form
- [ ] Test validazione risposte
- [ ] Test error handling

### Deploy
- [ ] Configurare environment variables
- [ ] Build produzione
- [ ] Deploy su hosting
- [ ] Verificare CORS

---

## 🎯 QUICK START

### 1. Avviare Backend

```bash
# Terminal 1: Onboarding API
cd /path/to/CGS_2/onboarding
python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8001 --reload

# Terminal 2: CGS Backend
cd /path/to/CGS_2
python3 -m uvicorn api.rest.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Testare API

```bash
# Health check
curl http://localhost:8001/health

# Swagger UI
open http://localhost:8001/docs
```

### 3. Sviluppare Frontend

Usa gli esempi di codice in questa guida per:
1. Creare API client
2. Implementare hook per polling
3. Creare componenti UI per ogni step
4. Gestire validazione e errori

---

## 📚 RISORSE

### Documentazione API

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **OpenAPI JSON**: http://localhost:8001/openapi.json

### Guide Backend

- [README.md](README.md) - Panoramica generale
- [QUICKSTART.md](QUICKSTART.md) - Setup rapido backend
- [INTEGRATION_TEST_GUIDE.md](INTEGRATION_TEST_GUIDE.md) - Test integrazione

### Esempi

Tutti gli esempi di codice in questa guida sono pronti all'uso e testati.

---

## 🆘 TROUBLESHOOTING

### Problema: CORS Error

**Sintomo**:
```
Access to fetch at 'http://localhost:8001/api/v1/onboarding/start'
from origin 'http://localhost:3000' has been blocked by CORS policy
```

**Soluzione**:
Il backend ha già CORS configurato. Verificare che il backend sia in esecuzione su porta 8001.

---

### Problema: Polling Non Si Ferma

**Sintomo**: Il polling continua anche dopo `state = "done"`

**Soluzione**:
```typescript
useEffect(() => {
  if (!sessionId || !session) return;

  // Stati finali
  const finalStates = ['awaiting_user', 'done', 'failed'];
  if (finalStates.includes(session.state)) {
    return; // Non fare polling
  }

  const interval = setInterval(fetchSession, 3000);
  return () => clearInterval(interval); // Cleanup
}, [sessionId, session?.state]);
```

---

### Problema: Validazione Enum Fallisce

**Sintomo**:
```
Invalid answer for question q2: must be one of [...]
```

**Soluzione**:
Assicurarsi che il valore inviato sia **esattamente** uno degli `enum_options`:

```typescript
// ❌ SBAGLIATO
answers.q2 = "increase brand awareness" // lowercase

// ✅ CORRETTO
answers.q2 = "Increase brand awareness" // Esattamente come in enum_options
```

---

### Problema: Session Not Found

**Sintomo**:
```
404 Not Found
```

**Soluzione**:
- Verificare che `session_id` sia valido UUID
- Verificare che la sessione non sia scaduta (TTL: 24h)
- Controllare che il backend Supabase sia raggiungibile

---

## 🎨 DESIGN SYSTEM RACCOMANDATO

### Colori

```css
:root {
  --primary: #6366f1;      /* Indigo */
  --success: #10b981;      /* Green */
  --warning: #f59e0b;      /* Amber */
  --error: #ef4444;        /* Red */
  --background: #ffffff;
  --surface: #f9fafb;
  --text: #111827;
  --text-secondary: #6b7280;
}
```

### Typography

```css
h1 { font-size: 2.25rem; font-weight: 700; }
h2 { font-size: 1.875rem; font-weight: 600; }
h3 { font-size: 1.5rem; font-weight: 600; }
body { font-size: 1rem; line-height: 1.5; }
.hint { font-size: 0.875rem; color: var(--text-secondary); }
```

### Spacing

```css
.container { max-width: 640px; margin: 0 auto; padding: 2rem; }
.section { margin-bottom: 2rem; }
.field { margin-bottom: 1.5rem; }
```

---

## ✅ CONCLUSIONE

Questa guida fornisce tutto il necessario per sviluppare il frontend del quiz onboarding:

✅ **API Endpoints** - Tutti i 5 endpoint documentati
✅ **Flusso Completo** - Diagramma stati e timing
✅ **Modelli Dati** - TypeScript interfaces
✅ **Codice Esempio** - React components pronti all'uso
✅ **UI/UX** - Wireframes e raccomandazioni
✅ **Testing** - Comandi cURL e strategie
✅ **Deployment** - Setup produzione

**Prossimi Step**:
1. Scegliere framework frontend (React/Next.js/Vue)
2. Implementare API client
3. Creare componenti UI
4. Testare con backend locale
5. Deploy

**Supporto**: Per domande o problemi, consultare la documentazione backend o aprire issue su GitHub.

---

**Ultimo aggiornamento**: 2025-10-14
**Versione API**: v1
**Backend**: http://localhost:8001

