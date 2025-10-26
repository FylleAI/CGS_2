# 🗺️ Card Fields Mapping - Guida Completa

> **Obiettivo**: Capire esattamente quali campi vengono mostrati nelle card e come vengono popolati

---

## 📋 Table of Contents

1. [Struttura Dati CompanySnapshot](#struttura-dati-companysnapshot)
2. [Card 1: Company Snapshot](#card-1-company-snapshot)
3. [Card 2: Audience Intelligence](#card-2-audience-intelligence)
4. [Card 3: Voice DNA](#card-3-voice-dna)
5. [Card 4: Strategic Insights](#card-4-strategic-insights)
6. [Campi Disponibili ma Non Usati](#campi-disponibili-ma-non-usati)
7. [Come Aggiungere Nuovi Campi](#come-aggiungere-nuovi-campi)

---

## 📊 Struttura Dati CompanySnapshot

### **Schema Completo**

```typescript
interface CompanySnapshot {
  // Metadata
  version: string;                    // "1.0"
  snapshot_id: string;                // UUID
  generated_at: string;               // ISO timestamp
  trace_id?: string;                  // Trace ID per debugging
  
  // Dati principali (4 sezioni)
  company: CompanyInfo;
  audience: AudienceInfo;
  voice: VoiceInfo;
  insights: InsightsInfo;
  
  // Domande di chiarimento
  clarifying_questions: ClarifyingQuestion[];
  clarifying_answers?: Record<string, any>;
}
```

---

### **CompanyInfo** (Informazioni Azienda)

```typescript
interface CompanyInfo {
  // ✅ OBBLIGATORI
  name: string;                       // Nome azienda
  description: string;                // Descrizione azienda
  key_offerings: string[];            // Prodotti/servizi principali
  differentiators: string[];          // Differenziatori competitivi
  evidence: Evidence[];               // Prove/fonti con confidence
  
  // ⚪ OPZIONALI
  legal_name?: string;                // Ragione sociale
  website?: string;                   // URL sito web
  industry?: string;                  // Settore/industria
  headquarters?: string;              // Sede principale
  size_range?: string;                // Dimensione azienda (es. "10-50 employees")
}
```

**Evidence Structure**:
```typescript
interface Evidence {
  source: string;                     // URL o nome fonte
  excerpt: string;                    // Estratto testo
  confidence: number;                 // 0.0 - 1.0
}
```

---

### **AudienceInfo** (Informazioni Audience)

```typescript
interface AudienceInfo {
  // ✅ OBBLIGATORI
  primary: string;                    // Audience primaria
  pain_points: string[];              // Problemi/sfide del target
  
  // ⚪ OPZIONALI
  secondary?: string[];               // Audience secondarie
  desired_outcomes?: string[];        // Risultati desiderati
  demographics?: string;              // Dati demografici
  psychographics?: string;            // Dati psicografici
}
```

---

### **VoiceInfo** (Informazioni Voice/Tone)

```typescript
interface VoiceInfo {
  // ✅ OBBLIGATORI
  tone: string;                       // Tono di voce (es. "professional", "friendly")
  style_guidelines: string[];         // Linee guida di stile
  
  // ⚪ OPZIONALI
  cta_preferences?: string[];         // CTA preferite
  forbidden_phrases?: string[];       // Frasi da evitare
  preferred_phrases?: string[];       // Frasi preferite
}
```

---

### **InsightsInfo** (Informazioni Strategiche)

```typescript
interface InsightsInfo {
  // ⚪ TUTTI OPZIONALI
  positioning?: string;               // Posizionamento di mercato
  key_messages?: string[];            // Messaggi chiave
  recent_news?: string[];             // Notizie recenti
  competitors?: string[];             // Competitor principali
  market_position?: string;           // Posizione di mercato
  competitive_advantages?: string[];  // Vantaggi competitivi
  recent_developments?: string[];     // Sviluppi recenti
  content_opportunities?: string[];   // Opportunità di contenuto
}
```

---

## 🏢 Card 1: Company Snapshot

### **Campi Mostrati**

| Campo UI | Fonte Dati | Obbligatorio | Limite | Note |
|----------|------------|--------------|--------|------|
| **Titolo Card** | `snapshot.company.name` | ✅ | - | Nome azienda |
| **Sottotitolo** | `snapshot.company.industry` | ⚪ | - | Fallback: "Industry not specified" |
| **Confidence Badge** | Calcolato da `evidence[]` | ⚪ | - | Media dei confidence values |
| **Descrizione** | `snapshot.company.description` | ✅ | 280 char | Truncated con "..." |
| **Website Link** | `snapshot.company.website` | ⚪ | - | Con icona ExternalLink |
| **Key Offerings** | `snapshot.company.key_offerings` | ⚪ | 4 items | Chip verdi |
| **Differentiators** | `snapshot.company.differentiators` | ⚪ | 3 items | Lista numerata |
| **Last Updated** | `snapshot.generated_at` | ✅ | - | Formato: "Jan 15, 2025" |

### **Codice di Rendering**

<augment_code_snippet path="onboarding-frontend/src/components/cards/CompanySnapshotCardV2.tsx" mode="EXCERPT">
````typescript
// Titolo e sottotitolo
<CardHeader
  icon={Building2}
  title={snapshot.company.name}                    // ← Nome azienda
  subtitle={snapshot.company.industry || 'Industry not specified'}  // ← Industry
  confidence={avgConfidence}                       // ← Calcolato da evidence
  category="company"
/>

// Descrizione
<p className="text-sm leading-relaxed text-gray-700">
  {truncateText(snapshot.company.description)}    // ← Max 280 char
</p>

// Website
{snapshot.company.website && (
  <a href={snapshot.company.website}>
    {snapshot.company.website.replace(/^https?:\/\//, '')}
  </a>
)}

// Key Offerings (max 4)
{snapshot.company.key_offerings.slice(0, 4).map((offering, idx) => (
  <Chip key={idx} variant="primary">{offering}</Chip>
))}

// Differentiators (max 3)
{snapshot.company.differentiators.slice(0, 3).map((diff, idx) => (
  <li>{idx + 1}. {diff}</li>
))}
````
</augment_code_snippet>

### **Esempio Dati Reali**

```json
{
  "company": {
    "name": "Fylle AI",
    "industry": "AI/SaaS - Content Generation",
    "description": "Fylle AI is an enterprise-grade AI content generation platform that helps marketing teams automate content creation at scale using multi-agent workflows.",
    "website": "https://fylle.ai",
    "key_offerings": [
      "AI-powered content generation",
      "Multi-agent workflow orchestration",
      "Multi-provider LLM support",
      "Comprehensive cost tracking"
    ],
    "differentiators": [
      "Clean architecture with domain-driven design",
      "Multi-provider support (OpenAI, Anthropic, Gemini)",
      "Real-time cost tracking and analytics"
    ],
    "evidence": [
      {
        "source": "https://fylle.ai",
        "excerpt": "Enterprise-grade AI content platform...",
        "confidence": 0.92
      }
    ]
  }
}
```

**Risultato UI**:
- **Titolo**: "Fylle AI"
- **Sottotitolo**: "AI/SaaS - Content Generation"
- **Confidence**: 92% (verde, "AI confident")
- **Descrizione**: "Fylle AI is an enterprise-grade AI content generation platform that helps marketing teams automate content creation at scale using multi-agent workflows."
- **Website**: "fylle.ai" (link cliccabile)
- **Key Offerings**: 4 chip verdi con i primi 4 items
- **Differentiators**: Lista numerata 1-3

---

## 👥 Card 2: Audience Intelligence

### **Campi Mostrati**

| Campo UI | Fonte Dati | Obbligatorio | Limite | Note |
|----------|------------|--------------|--------|------|
| **Primary Audience** | `snapshot.audience.primary` | ✅ | - | Chip grande con emoji 👤 |
| **Secondary Audiences** | `snapshot.audience.secondary` | ⚪ | 3 items | Chip piccoli |
| **Pain Points** | `snapshot.audience.pain_points` | ⚪ | 3 items | Con icona AlertCircle rossa |
| **Desired Outcomes** | `snapshot.audience.desired_outcomes` | ⚪ | 3 items | Con icona CheckCircle verde |

### **Codice di Rendering**

<augment_code_snippet path="onboarding-frontend/src/components/cards/AudienceIntelligenceCard.tsx" mode="EXCERPT">
````typescript
// Primary Audience
<Chip variant="primary" className="text-base">
  👤 {audience.primary}
</Chip>

// Secondary Audiences (max 3)
{audience.secondary.slice(0, 3).map((sec, idx) => (
  <Chip key={idx} variant="secondary">{sec}</Chip>
))}

// Pain Points (max 3)
{audience.pain_points.slice(0, 3).map((pain, idx) => (
  <li>
    <AlertCircle className="text-red-500" />
    {pain}
  </li>
))}

// Desired Outcomes (max 3)
{audience.desired_outcomes.slice(0, 3).map((outcome, idx) => (
  <li>
    <CheckCircle2 className="text-emerald-500" />
    {outcome}
  </li>
))}
````
</augment_code_snippet>

### **Esempio Dati Reali**

```json
{
  "audience": {
    "primary": "Marketing teams and content creators in B2B SaaS companies",
    "secondary": [
      "Content agencies",
      "Enterprise marketing departments",
      "Startup founders"
    ],
    "pain_points": [
      "Time-consuming content creation process",
      "Difficulty maintaining brand voice consistency",
      "High costs of hiring content writers"
    ],
    "desired_outcomes": [
      "Automate content creation at scale",
      "Maintain consistent brand voice",
      "Reduce content production costs by 50%"
    ]
  }
}
```

**Risultato UI**:
- **Primary**: Chip grande "👤 Marketing teams and content creators in B2B SaaS companies"
- **Secondary**: 3 chip piccoli (Content agencies, Enterprise marketing, Startup founders)
- **Pain Points**: 3 bullet con icona rossa
- **Desired Outcomes**: 3 bullet con icona verde

---

## 🎨 Card 3: Voice DNA

### **Campi Mostrati**

| Campo UI | Fonte Dati | Obbligatorio | Limite | Note |
|----------|------------|--------------|--------|------|
| **Brand Tone** | `snapshot.voice.tone` | ✅ | - | Card colorata dinamica |
| **Style Guidelines** | `snapshot.voice.style_guidelines` | ⚪ | 3 items | Checklist con ✓ |
| **Preferred CTAs** | `snapshot.voice.cta_preferences` | ⚪ | 3 items | Pulsanti interattivi |
| **Forbidden Phrases** | `snapshot.voice.forbidden_phrases` | ⚪ | - | Badge rosso o "No restrictions" |

### **Codice di Rendering**

<augment_code_snippet path="onboarding-frontend/src/components/cards/VoiceDNACard.tsx" mode="EXCERPT">
````typescript
// Brand Tone (capitalized + colored)
const formattedTone = voice.tone
  .split(' ')
  .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
  .join(' ');

<div className={`bg-gradient-to-r ${getToneColor(voice.tone)}`}>
  <Mic className="h-5 w-5 text-purple-600" />
  <span>{formattedTone}</span>
</div>

// Style Guidelines (max 3)
{voice.style_guidelines.slice(0, 3).map((guideline, idx) => (
  <li>
    <span className="bg-purple-100">✓</span>
    {guideline}
  </li>
))}

// CTA Preferences (max 3)
{voice.cta_preferences.slice(0, 3).map((cta, idx) => (
  <button className="border-purple-200">{cta}</button>
))}

// Forbidden Phrases
{voice.forbidden_phrases && voice.forbidden_phrases.length > 0 ? (
  <div className="border-red-200">
    {voice.forbidden_phrases.map((phrase) => `"${phrase}"`)}
  </div>
) : (
  <div className="border-emerald-200">
    ✓ No content restrictions detected
  </div>
)}
````
</augment_code_snippet>

### **Esempio Dati Reali**

```json
{
  "voice": {
    "tone": "professional yet approachable",
    "style_guidelines": [
      "Data-driven and results-focused",
      "Clear and concise language",
      "Emphasize innovation and efficiency"
    ],
    "cta_preferences": [
      "Start your free trial",
      "Book a demo",
      "Learn more"
    ],
    "forbidden_phrases": [
      "Synergy",
      "Leverage",
      "Paradigm shift"
    ]
  }
}
```

**Risultato UI**:
- **Tone**: Card colorata "Professional Yet Approachable" (capitalized)
- **Style Guidelines**: 3 bullet con checkmark viola
- **CTAs**: 3 pulsanti interattivi
- **Forbidden**: Badge rosso con "Synergy", "Leverage", "Paradigm shift"

---

## 💡 Card 4: Strategic Insights

### **Campi Mostrati**

| Campo UI | Fonte Dati | Obbligatorio | Limite | Note |
|----------|------------|--------------|--------|------|
| **Recent News** (Tab 1) | `snapshot.insights.recent_news` | ⚪ | 2 items | Con icona TrendingUp |
| **Key Messages** (Tab 2) | `snapshot.insights.key_messages` | ⚪ | 3 items | Lista numerata |
| **Evidence** | `snapshot.company.evidence` | ⚪ | 2 items | Con confidence badge |

### **Codice di Rendering**

<augment_code_snippet path="onboarding-frontend/src/components/cards/StrategicInsightsCard.tsx" mode="EXCERPT">
````typescript
// Tab Navigation
const [activeTab, setActiveTab] = useState<'news' | 'messages'>('news');

// Recent News (max 2)
{insights.recent_news.slice(0, 2).map((news, idx) => (
  <div className="border-amber-200">
    <TrendingUp className="text-amber-600" />
    <p>{news}</p>
  </div>
))}

// Key Messages (max 3)
{insights.key_messages.slice(0, 3).map((message, idx) => (
  <li>
    <span className="bg-amber-100">{idx + 1}</span>
    {message}
  </li>
))}

// Evidence (max 2)
{company.evidence.slice(0, 2).map((evidence, idx) => (
  <div>
    <p>"{evidence.excerpt.slice(0, 120)}..."</p>
    <ConfidenceBadge confidence={evidence.confidence} source={evidence.source} />
  </div>
))}
````
</augment_code_snippet>

### **Esempio Dati Reali**

```json
{
  "insights": {
    "positioning": "Enterprise-grade AI content platform for B2B SaaS",
    "recent_news": [
      "Launched multi-agent workflow orchestration in Q4 2024",
      "Added support for Anthropic Claude and Google Gemini models"
    ],
    "key_messages": [
      "Automate content creation at scale without sacrificing quality",
      "Maintain brand voice consistency across all channels",
      "Reduce content production costs by up to 70%"
    ]
  },
  "company": {
    "evidence": [
      {
        "source": "https://fylle.ai/blog/multi-agent-workflows",
        "excerpt": "Our new multi-agent system allows teams to orchestrate complex content workflows with unprecedented efficiency...",
        "confidence": 0.95
      }
    ]
  }
}
```

**Risultato UI**:
- **Tab News**: 2 card con icona TrendingUp
- **Tab Messages**: 3 messaggi numerati
- **Evidence**: 2 card con excerpt (120 char) + confidence badge (95%)

---

## 🔍 Campi Disponibili ma Non Usati

### **CompanyInfo**
- ❌ `legal_name` - Ragione sociale
- ❌ `headquarters` - Sede principale
- ❌ `size_range` - Dimensione azienda

### **AudienceInfo**
- ❌ `demographics` - Dati demografici
- ❌ `psychographics` - Dati psicografici

### **VoiceInfo**
- ❌ `preferred_phrases` - Frasi preferite

### **InsightsInfo**
- ❌ `positioning` - Posizionamento (disponibile ma non mostrato)
- ❌ `competitors` - Competitor
- ❌ `market_position` - Posizione di mercato
- ❌ `competitive_advantages` - Vantaggi competitivi
- ❌ `recent_developments` - Sviluppi recenti
- ❌ `content_opportunities` - Opportunità di contenuto

---

## ➕ Come Aggiungere Nuovi Campi

### **Scenario 1: Campo Già Disponibile nel Backend**

**Esempio**: Mostrare `headquarters` nella Company Card

**Step 1**: Verifica che il campo esista in `CompanyInfo` (TypeScript)
```typescript
// onboarding-frontend/src/types/onboarding.ts
export interface CompanyInfo {
  headquarters?: string;  // ✅ Già presente
}
```

**Step 2**: Aggiungi nella card
```typescript
// onboarding-frontend/src/components/cards/CompanySnapshotCardV2.tsx
{snapshot.company.headquarters && (
  <div className="flex items-center gap-2 text-sm text-gray-600">
    <MapPin className="h-4 w-4" />
    <span>{snapshot.company.headquarters}</span>
  </div>
)}
```

**Step 3**: Importa icona
```typescript
import { Building2, ExternalLink, Sparkles, TrendingUp, MapPin } from 'lucide-react';
```

---

### **Scenario 2: Campo Nuovo (Non Esiste nel Backend)**

**Esempio**: Aggiungere `founded_year`

**Step 1**: Aggiungi al type TypeScript (Frontend)
```typescript
// onboarding-frontend/src/types/onboarding.ts
export interface CompanyInfo {
  founded_year?: number;  // ← Nuovo campo
}
```

**Step 2**: Aggiungi al model Pydantic (Backend)
```python
# onboarding/domain/models.py
class CompanyInfo(BaseModel):
    founded_year: Optional[int] = None  # ← Nuovo campo
```

**Step 3**: Aggiorna il prompt Gemini per generare il campo
```python
# onboarding/infrastructure/adapters/gemini_adapter.py
# Nel prompt di synthesis, aggiungi:
# "founded_year": year company was founded (integer, optional)
```

**Step 4**: Aggiungi nella card (Frontend)
```typescript
{snapshot.company.founded_year && (
  <div className="text-sm text-gray-600">
    Founded in {snapshot.company.founded_year}
  </div>
)}
```

---

## 📊 Riepilogo Limiti

| Card | Campo | Limite Attuale | Modificabile in |
|------|-------|----------------|-----------------|
| Company | Description | 280 char | `CompanySnapshotCardV2.tsx:21` |
| Company | Key Offerings | 4 items | `CompanySnapshotCardV2.tsx:64` |
| Company | Differentiators | 3 items | `CompanySnapshotCardV2.tsx:77` |
| Audience | Secondary | 3 items | `AudienceIntelligenceCard.tsx:41` |
| Audience | Pain Points | 3 items | `AudienceIntelligenceCard.tsx:56` |
| Audience | Desired Outcomes | 3 items | `AudienceIntelligenceCard.tsx:70` |
| Voice | Style Guidelines | 3 items | `VoiceDNACard.tsx:56` |
| Voice | CTA Preferences | 3 items | `VoiceDNACard.tsx:72` |
| Insights | Recent News | 2 items | `StrategicInsightsCard.tsx:63` |
| Insights | Key Messages | 3 items | `StrategicInsightsCard.tsx:86` |
| Insights | Evidence | 2 items | `StrategicInsightsCard.tsx:108` |

---

**Ultimo aggiornamento**: 2025-10-23  
**Versione**: 1.0

