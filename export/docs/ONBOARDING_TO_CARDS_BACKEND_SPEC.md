# 🎯 Onboarding → Cards: Specifica Backend & Layer AI

> **Obiettivo**: Al termine dell'onboarding, generare un `CardsSnapshot` completo con tutte le 8 category di card, popolate con i dati raccolti (input utente + ricerca AI).

---

## 📋 Indice

1. [Overview Flusso](#1-overview-flusso)
2. [Input: Dati Onboarding](#2-input-dati-onboarding)
3. [Output: CardsSnapshot](#3-output-cardssnapshot)
4. [Layer AI: Come Lavora](#4-layer-ai-come-lavora)
5. [Mapping Onboarding → Cards](#5-mapping-onboarding--cards)
6. [Gestione Resilienza](#6-gestione-resilienza)
7. [Card Placeholder (Performance/Feedback)](#7-card-placeholder)
8. [Esempi Output](#8-esempi-output)

---

## 1. Overview Flusso

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ONBOARDING FLOW                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  [1. START]  →  [2. RESEARCH]  →  [3. SYNTHESIS]  →  [4. CARDS]             │
│                                                                              │
│  User Input     Perplexity        Gemini            CardsSnapshot           │
│  - Company      - Competitors     - Genera card     - 8 category            │
│  - Website      - Market trends   - Sintetizza      - N card per type       │
│  - Industry     - Industry data   - Completa gaps   - Ready for UI          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Stati Sessione
```
created → researching → synthesizing → generating_cards → done/failed
```

---

## 2. Input: Dati Onboarding

### 2.1 Input Utente (Obbligatori)
```typescript
interface OnboardingInput {
  company: {
    name: string;              // "Fylle"
    website: string;           // "https://fylle.ai"
    industry: string;          // "SaaS B2B"
    description?: string;      // Breve descrizione
  };
  
  audience: {
    primary_target: string;    // "Marketing Manager PMI"
    pain_points: string[];     // ["Poco tempo", "Budget limitato"]
    desired_outcomes: string[];// ["Più lead", "Meno tempo su content"]
  };
  
  competitors?: string[];      // ["ContentAI", "WriteBot"] - opzionale
}
```

### 2.2 Dati Arricchiti da AI (Perplexity)
```typescript
interface ResearchData {
  company_analysis: {
    value_proposition: string;
    key_offerings: string[];
    differentiators: string[];
    market_position: string;
  };
  
  competitor_analysis: {
    name: string;
    positioning: string;
    strengths: string[];
    weaknesses: string[];
    pricing?: string;
  }[];
  
  market_insights: {
    trends: string[];
    keywords: string[];
    opportunities: string[];
  };
  
  target_enrichment: {
    demographics: object;
    channels: string[];
    content_preferences: string[];
  };
}
```

---

## 3. Output: CardsSnapshot

```typescript
interface CardsSnapshot {
  sessionId: string;
  generatedAt: string;       // ISO timestamp
  cards: Card[];             // Array di tutte le card
  metadata: {
    generation_time_ms: number;
    ai_models_used: string[];
    completeness_score: number;  // 0-100%
  };
}
```

### Card per Category

| CardType | Min | Max | Note |
|----------|-----|-----|------|
| `product` | 1 | 1 | Sempre 1, basata su company |
| `target` | 1 | 5 | 1 per ogni ICP identificato |
| `brand_voice` | 1 | 1 | Sempre 1, derivata da tone |
| `competitor` | 0 | 10 | 1 per competitor analizzato |
| `topic` | 1 | 5 | Temi principali per content |
| `campaigns` | 1 | 3 | Template campagne suggerite |
| `performance` | 1 | 1 | Placeholder - si popola nel tempo |
| `feedback` | 1 | 1 | Placeholder - si popola nel tempo |

---

## 4. Layer AI: Come Lavora

### 4.1 Perplexity (Ricerca)

**Scopo**: Arricchire i dati utente con informazioni di mercato reali.

**Query da eseguire**:
```
1. COMPANY ANALYSIS
   "Analyze {company_name} ({website}): value proposition, 
    key products/services, market positioning, differentiators"

2. COMPETITOR ANALYSIS (per ogni competitor)
   "Analyze {competitor_name} in {industry}: positioning, 
    pricing, strengths, weaknesses vs {company_name}"

3. MARKET TRENDS
   "Top trends and keywords in {industry} for {target_audience} 
    in 2024-2025, content marketing opportunities"

4. TARGET ENRICHMENT
   "Demographics and preferred channels for {primary_target} 
    in {industry}, content consumption habits"
```

**Fallback**: Se Perplexity fallisce, usare solo input utente + Gemini.

### 4.2 Gemini (Sintesi & Generazione)

**Scopo**: Sintetizzare dati e generare card complete.

**Prompt Structure**:
```
CONTEXT:
- Company: {company_data}
- Research: {perplexity_results}
- User Input: {onboarding_input}

TASK:
Generate a complete CardsSnapshot with all 8 card types.
For each card, provide all required fields.

RULES:
1. If data is missing, generate reasonable defaults based on context
2. Mark incomplete fields with confidence: "low"
3. Never leave required fields empty
4. Use Italian language for content
5. Be specific, avoid generic phrases

OUTPUT FORMAT:
{CardsSnapshot JSON schema}
```

---

## 5. Mapping Onboarding → Cards

### 5.1 Product Card
```
INPUT                              → OUTPUT (ProductCard)
─────────────────────────────────────────────────────────
company.name                       → title
company.description                → valueProposition
perplexity.key_offerings           → features[]
perplexity.differentiators         → differentiators[]
perplexity.market_position         → useCases[] (derivati)
[generated]                        → performanceMetrics[]
```

### 5.2 Target Card(s)
```
INPUT                              → OUTPUT (TargetCard)
─────────────────────────────────────────────────────────
audience.primary_target            → icpName, title
[gemini generated]                 → description
audience.pain_points               → painPoints[]
audience.desired_outcomes          → goals[]
perplexity.target.channels         → communicationChannels[]
perplexity.target.demographics     → demographics{}
[default: "Italiano"]              → preferredLanguage
```
**Nota**: Se AI identifica più ICP distinti, genera N TargetCard.

### 5.3 Brand Voice Card
```
INPUT                              → OUTPUT (BrandVoiceCard)
─────────────────────────────────────────────────────────
[gemini: derive from company tone] → toneDescription
[gemini: generate guidelines]      → styleGuidelines[]
[gemini: generate examples]        → dosExamples[]
[gemini: generate anti-examples]   → dontsExamples[]
[gemini: derive from industry]     → termsToUse[], termsToAvoid[]
```

### 5.4 Competitor Card(s)
```
INPUT                              → OUTPUT (CompetitorCard)
─────────────────────────────────────────────────────────
competitors[i]                     → competitorName, title
perplexity.competitor.positioning  → positioning
perplexity.competitor.strengths    → strengths[]
perplexity.competitor.weaknesses   → weaknesses[]
[gemini: vs company analysis]      → keyMessages[]
[gemini: opportunities]            → differentiationOpportunities[]
```
**Nota**: 1 card per ogni competitor. Se nessun competitor fornito, Perplexity ne identifica 2-3.

### 5.5 Topic Card(s)
```
INPUT                              → OUTPUT (TopicCard)
─────────────────────────────────────────────────────────
perplexity.market.trends           → trends[]
perplexity.market.keywords         → keywords[]
[gemini: content angles]           → angles[]
[gemini: suggest content]          → relatedContent[]
[gemini: derive from all data]     → description
```

### 5.6 Campaigns Card(s)
```
INPUT                              → OUTPUT (CampaignsCard)
─────────────────────────────────────────────────────────
[gemini: suggest campaign]         → title, objective
audience.desired_outcomes          → keyMessages[]
brand_voice.tone                   → tone
[gemini: suggest assets]           → assets[]
[]                                 → results (empty initially)
[gemini: best practices]           → learnings[]
```

---

## 6. Gestione Resilienza

### ⚠️ PRINCIPIO FONDAMENTALE
```
┌────────────────────────────────────────────────────────────────┐
│  ❌ MAI BLOCCARE LA PIPELINE                                   │
│  ✅ GENERA SEMPRE TUTTE LE CARD                                │
│  ✅ SEGNALA COSA È INCOMPLETO                                  │
└────────────────────────────────────────────────────────────────┘
```

### 6.1 Flag di Completezza

Ogni card include metadata di completezza:

```typescript
interface CardMetadata {
  confidence: 'high' | 'medium' | 'low';
  incomplete_fields?: string[];
  data_sources: ('user_input' | 'perplexity' | 'gemini' | 'default')[];
  requires_review: boolean;
  message?: string;  // "Completa i dati mancanti per migliorare questa card"
}
```

### 6.2 Scenari di Fallback

| Scenario | Azione | Risultato |
|----------|--------|-----------|
| Perplexity timeout | Usa solo input utente + Gemini | `confidence: "medium"` |
| Perplexity error | Retry 1x, poi fallback Gemini | `confidence: "low"` |
| Gemini error | Genera card con campi minimi | `confidence: "low"`, `requires_review: true` |
| Campo obbligatorio mancante | Genera placeholder intelligente | `incomplete_fields: ["campo"]` |
| Competitor non trovato | Segnala, non creare card vuota | Nessuna CompetitorCard |

### 6.3 Esempio Card Incompleta

```json
{
  "id": "card-target-001",
  "type": "target",
  "title": "Target Primario",
  "icpName": "Marketing Manager",
  "description": "Profilo da completare con più dettagli",
  "painPoints": ["Poco tempo per content creation"],
  "goals": [],
  "demographics": null,

  "_metadata": {
    "confidence": "low",
    "incomplete_fields": ["goals", "demographics", "communicationChannels"],
    "data_sources": ["user_input"],
    "requires_review": true,
    "message": "Aggiungi obiettivi e dati demografici per migliorare questa card"
  }
}
```

---

## 7. Card Placeholder

### Performance Card
```json
{
  "id": "card-performance-placeholder",
  "type": "performance",
  "title": "Performance Campagne",
  "period": "In attesa di dati",
  "metrics": [],
  "topPerformingContent": [],
  "insights": [],

  "_metadata": {
    "status": "awaiting_data",
    "message": "Questa card si popolerà automaticamente con le metriche delle tue campagne",
    "auto_update": true,
    "data_sources_expected": ["campaigns", "analytics", "social_metrics"],
    "estimated_first_data": "Dopo la prima campagna completata"
  }
}
```

### Feedback Card
```json
{
  "id": "card-feedback-placeholder",
  "type": "feedback",
  "title": "Feedback & Learnings",
  "source": "other",
  "summary": "In attesa di feedback",
  "details": "Questa sezione raccoglierà i feedback dai clienti, dal team e dai test A/B.",
  "actionItems": [],
  "priority": "medium",

  "_metadata": {
    "status": "awaiting_data",
    "message": "I feedback verranno raccolti automaticamente dalle tue attività",
    "auto_update": true,
    "data_sources_expected": ["customer_feedback", "team_notes", "ab_tests"],
    "how_to_populate": [
      "Completa la prima campagna",
      "Raccogli feedback clienti",
      "Esegui A/B test sui contenuti"
    ]
  }
}
```

---

## 8. Esempi Output

### 8.1 Flusso Completo Successo

```
INPUT:
  company: { name: "Fylle", website: "fylle.ai", industry: "MarTech SaaS" }
  audience: { primary_target: "Marketing Manager PMI", pain_points: ["poco tempo"] }
  competitors: ["Jasper", "Copy.ai"]

PERPLEXITY QUERIES:
  ✅ Company analysis → value proposition, offerings
  ✅ Jasper analysis → positioning, strengths, weaknesses
  ✅ Copy.ai analysis → positioning, strengths, weaknesses
  ✅ Market trends → AI content, automation keywords

GEMINI SYNTHESIS:
  ✅ Generate all cards with full data

OUTPUT: CardsSnapshot
  ├── ProductCard (1) - confidence: high
  ├── TargetCard (2) - confidence: high (AI identified 2 ICP)
  ├── BrandVoiceCard (1) - confidence: high
  ├── CompetitorCard (2) - confidence: high
  ├── TopicCard (3) - confidence: high
  ├── CampaignsCard (2) - confidence: medium
  ├── PerformanceCard (1) - status: awaiting_data
  └── FeedbackCard (1) - status: awaiting_data

  metadata.completeness_score: 85%
```

### 8.2 Flusso con Fallback

```
INPUT:
  company: { name: "Acme", website: "acme.com", industry: "B2B" }
  audience: { primary_target: "Sales Director" }
  competitors: []  // nessuno fornito

PERPLEXITY QUERIES:
  ✅ Company analysis → OK
  ⚠️ Competitor discovery → timeout
  ✅ Market trends → OK

GEMINI SYNTHESIS:
  ✅ Generate cards with available data
  ⚠️ CompetitorCard skipped (no data)

OUTPUT: CardsSnapshot
  ├── ProductCard (1) - confidence: high
  ├── TargetCard (1) - confidence: medium (no enrichment)
  ├── BrandVoiceCard (1) - confidence: medium
  ├── CompetitorCard (0) - NONE (message: "Aggiungi competitor per analisi")
  ├── TopicCard (2) - confidence: high
  ├── CampaignsCard (1) - confidence: medium
  ├── PerformanceCard (1) - status: awaiting_data
  └── FeedbackCard (1) - status: awaiting_data

  metadata.completeness_score: 65%
  metadata.warnings: ["Competitor analysis skipped - add competitors manually"]
```

---

## 📎 Appendice: Checklist Implementazione

### Per il DEV Backend
- [ ] Endpoint `POST /onboarding/generate-cards`
- [ ] Integrazione Perplexity API con retry logic
- [ ] Integrazione Gemini API con prompt engineering
- [ ] Timeout handling (max 30s per query)
- [ ] Logging transaction_id per debug
- [ ] Salvataggio CardsSnapshot in DB

### Per il Layer AI
- [ ] Prompt templates per ogni card type
- [ ] Fallback prompts quando mancano dati
- [ ] Validazione output JSON schema
- [ ] Confidence scoring logic
- [ ] Multi-language support (IT/EN)

---

*Documento generato: 2024-12-02*
*Versione: 1.0*

