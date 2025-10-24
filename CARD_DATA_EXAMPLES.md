# 📸 Card Data Examples - Esempi Visivi

> **Obiettivo**: Vedere esattamente come i dati del backend vengono trasformati in UI

---

## 🏢 Esempio Completo: Fylle AI

### **Backend: CompanySnapshot JSON**

```json
{
  "version": "1.0",
  "snapshot_id": "a3bf1154-fdd6-48c0-ad25-3a3230299501",
  "generated_at": "2025-01-15T10:30:00Z",
  "trace_id": "trace-abc-123",
  
  "company": {
    "name": "Fylle AI",
    "legal_name": "Fylle AI Inc.",
    "website": "https://fylle.ai",
    "industry": "AI/SaaS - Content Generation",
    "headquarters": "San Francisco, CA",
    "size_range": "10-50 employees",
    "description": "Fylle AI is an enterprise-grade AI content generation platform that helps marketing teams automate content creation at scale using multi-agent workflows. Our platform supports multiple LLM providers and provides comprehensive cost tracking.",
    "key_offerings": [
      "AI-powered content generation",
      "Multi-agent workflow orchestration",
      "Multi-provider LLM support (OpenAI, Anthropic, Gemini)",
      "Comprehensive cost tracking and analytics",
      "Real-time collaboration tools"
    ],
    "differentiators": [
      "Clean architecture with domain-driven design",
      "Multi-provider support with automatic failover",
      "Real-time cost tracking per workflow",
      "Enterprise-grade security and compliance"
    ],
    "evidence": [
      {
        "source": "https://fylle.ai",
        "excerpt": "Enterprise-grade AI content platform with multi-agent workflows",
        "confidence": 0.95
      },
      {
        "source": "https://fylle.ai/pricing",
        "excerpt": "Transparent pricing with real-time cost tracking",
        "confidence": 0.88
      }
    ]
  },
  
  "audience": {
    "primary": "Marketing teams and content creators in B2B SaaS companies",
    "secondary": [
      "Content marketing agencies",
      "Enterprise marketing departments",
      "Startup founders and growth teams"
    ],
    "pain_points": [
      "Time-consuming manual content creation process",
      "Difficulty maintaining brand voice consistency across channels",
      "High costs of hiring and managing content writers",
      "Lack of visibility into content production costs"
    ],
    "desired_outcomes": [
      "Automate content creation at scale without sacrificing quality",
      "Maintain consistent brand voice across all content",
      "Reduce content production costs by 50-70%",
      "Gain real-time insights into content performance"
    ],
    "demographics": "B2B SaaS companies with 10-500 employees, $1M-$50M ARR",
    "psychographics": "Data-driven, efficiency-focused, early adopters of AI technology"
  },
  
  "voice": {
    "tone": "professional yet approachable",
    "style_guidelines": [
      "Data-driven and results-focused language",
      "Clear and concise explanations without jargon",
      "Emphasize innovation, efficiency, and ROI",
      "Use active voice and action-oriented language"
    ],
    "cta_preferences": [
      "Start your free trial",
      "Book a demo with our team",
      "Learn more about our platform",
      "Download our whitepaper"
    ],
    "forbidden_phrases": [
      "Synergy",
      "Leverage",
      "Paradigm shift",
      "Game-changer"
    ],
    "preferred_phrases": [
      "Automate at scale",
      "Real-time insights",
      "Enterprise-grade"
    ]
  },
  
  "insights": {
    "positioning": "Enterprise-grade AI content platform for B2B SaaS companies",
    "recent_news": [
      "Launched multi-agent workflow orchestration in Q4 2024",
      "Added support for Anthropic Claude and Google Gemini models in January 2025"
    ],
    "key_messages": [
      "Automate content creation at scale without sacrificing quality",
      "Maintain brand voice consistency across all channels",
      "Reduce content production costs by up to 70%"
    ],
    "competitors": [
      "Jasper AI",
      "Copy.ai",
      "Writesonic"
    ],
    "competitive_advantages": [
      "Multi-provider LLM support with automatic failover",
      "Real-time cost tracking per workflow",
      "Enterprise-grade security and compliance"
    ],
    "content_opportunities": [
      "Case studies showcasing ROI",
      "Technical blog posts on multi-agent workflows",
      "Comparison guides vs. competitors"
    ]
  },
  
  "clarifying_questions": [
    {
      "id": "q1",
      "question": "What type of content do you primarily create?",
      "reason": "To tailor content generation templates",
      "expected_response_type": "multiselect",
      "options": ["Blog posts", "Social media", "Email campaigns", "Product descriptions"],
      "required": true
    }
  ]
}
```

---

### **Frontend: Card 1 - Company Snapshot**

**Rendering**:

```
┌─────────────────────────────────────────────────────────────┐
│ 🏢  Fylle AI                              🧠 AI confident   │
│     AI/SaaS - Content Generation                92%         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Fylle AI is an enterprise-grade AI content generation      │
│ platform that helps marketing teams automate content       │
│ creation at scale using multi-agent workflows. Our         │
│ platform supports multiple LLM providers and provides      │
│ comprehensive cost tracking.                                │
│                                                             │
│ 🔗 fylle.ai                                                 │
│                                                             │
│ ✨ Key Offerings                                            │
│ ┌─────────────────────┐ ┌─────────────────────┐            │
│ │ AI-powered content  │ │ Multi-agent workflow│            │
│ │ generation          │ │ orchestration       │            │
│ └─────────────────────┘ └─────────────────────┘            │
│ ┌─────────────────────┐ ┌─────────────────────┐            │
│ │ Multi-provider LLM  │ │ Comprehensive cost  │            │
│ │ support             │ │ tracking            │            │
│ └─────────────────────┘ └─────────────────────┘            │
│                                                             │
│ 📈 Differentiators                                          │
│ 1. Clean architecture with domain-driven design            │
│ 2. Multi-provider support with automatic failover          │
│ 3. Real-time cost tracking per workflow                    │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ Updated Jan 15, 2025              [Refine Details]         │
└─────────────────────────────────────────────────────────────┘
```

**Campi Usati**:
- ✅ `company.name` → "Fylle AI"
- ✅ `company.industry` → "AI/SaaS - Content Generation"
- ✅ `company.evidence[].confidence` → 92% (media di 0.95 e 0.88)
- ✅ `company.description` → Truncated a 280 char
- ✅ `company.website` → "fylle.ai"
- ✅ `company.key_offerings` → Primi 4 items (su 5 disponibili)
- ✅ `company.differentiators` → Primi 3 items (su 4 disponibili)
- ✅ `generated_at` → "Jan 15, 2025"

**Campi NON Usati**:
- ❌ `company.legal_name` → "Fylle AI Inc."
- ❌ `company.headquarters` → "San Francisco, CA"
- ❌ `company.size_range` → "10-50 employees"

---

### **Frontend: Card 2 - Audience Intelligence**

**Rendering**:

```
┌─────────────────────────────────────────────────────────────┐
│ 👥  Audience Intelligence                                   │
│     Who you're reaching                                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 🎯 Target Audience                                          │
│ Primary                                                     │
│ ┌───────────────────────────────────────────────────────┐   │
│ │ 👤 Marketing teams and content creators in B2B SaaS   │   │
│ │    companies                                          │   │
│ └───────────────────────────────────────────────────────┘   │
│                                                             │
│ Secondary                                                   │
│ ┌──────────────────┐ ┌──────────────────┐ ┌─────────────┐  │
│ │ Content agencies │ │ Enterprise depts │ │ Startups    │  │
│ └──────────────────┘ └──────────────────┘ └─────────────┘  │
│                                                             │
│ 🚨 Pain Points                                              │
│ • Time-consuming manual content creation process           │
│ • Difficulty maintaining brand voice consistency           │
│ • High costs of hiring and managing content writers        │
│                                                             │
│ ✅ Desired Outcomes                                         │
│ • Automate content creation at scale without sacrificing   │
│   quality                                                   │
│ • Maintain consistent brand voice across all content       │
│ • Reduce content production costs by 50-70%                │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ 🧠 AI understanding based on market research               │
└─────────────────────────────────────────────────────────────┘
```

**Campi Usati**:
- ✅ `audience.primary` → Chip grande
- ✅ `audience.secondary` → Primi 3 items (su 3 disponibili)
- ✅ `audience.pain_points` → Primi 3 items (su 4 disponibili)
- ✅ `audience.desired_outcomes` → Primi 3 items (su 4 disponibili)

**Campi NON Usati**:
- ❌ `audience.demographics` → "B2B SaaS companies with 10-500 employees..."
- ❌ `audience.psychographics` → "Data-driven, efficiency-focused..."

---

### **Frontend: Card 3 - Voice DNA**

**Rendering**:

```
┌─────────────────────────────────────────────────────────────┐
│ 💬  Voice DNA                                               │
│     How you communicate                                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Brand Tone                                                  │
│ ┌───────────────────────────────────────────────────────┐   │
│ │         🎤 Professional Yet Approachable              │   │
│ └───────────────────────────────────────────────────────┘   │
│                                                             │
│ 🛡️ Style Guidelines                                         │
│ ✓ Data-driven and results-focused language                 │
│ ✓ Clear and concise explanations without jargon            │
│ ✓ Emphasize innovation, efficiency, and ROI                │
│                                                             │
│ 🖱️ Preferred CTAs                                           │
│ ┌──────────────────┐ ┌──────────────────┐ ┌─────────────┐  │
│ │ Start free trial │ │ Book a demo      │ │ Learn more  │  │
│ └──────────────────┘ └──────────────────┘ └─────────────┘  │
│                                                             │
│ ⚠️ Avoid These Phrases                                      │
│ "Synergy", "Leverage", "Paradigm shift"                    │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ 🎨 Voice profile analyzed from brand communications        │
└─────────────────────────────────────────────────────────────┘
```

**Campi Usati**:
- ✅ `voice.tone` → "Professional Yet Approachable" (capitalized)
- ✅ `voice.style_guidelines` → Primi 3 items (su 4 disponibili)
- ✅ `voice.cta_preferences` → Primi 3 items (su 4 disponibili)
- ✅ `voice.forbidden_phrases` → Tutti (3 items)

**Campi NON Usati**:
- ❌ `voice.preferred_phrases` → ["Automate at scale", "Real-time insights", ...]

---

### **Frontend: Card 4 - Strategic Insights**

**Rendering (Tab: News)**:

```
┌─────────────────────────────────────────────────────────────┐
│ 💡  Strategic Insights                                      │
│     Context & intelligence                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ┌─────────┬──────────┐                                      │
│ │ 📰 News │ Messages │                                      │
│ └─────────┴──────────┘                                      │
│                                                             │
│ 📈 Launched multi-agent workflow orchestration in Q4 2024  │
│                                                             │
│ 📈 Added support for Anthropic Claude and Google Gemini    │
│    models in January 2025                                   │
│                                                             │
│ ─────────────────────────────────────────────────────────   │
│ Evidence                                                    │
│                                                             │
│ "Enterprise-grade AI content platform with multi-agent     │
│  workflows"                                                 │
│ 95% confidence • Source [1]                                 │
│                                                             │
│ "Transparent pricing with real-time cost tracking"         │
│ 88% confidence • Source [2]                                 │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│              [Generate Content Plan]                        │
└─────────────────────────────────────────────────────────────┘
```

**Rendering (Tab: Messages)**:

```
┌─────────────────────────────────────────────────────────────┐
│ 💡  Strategic Insights                                      │
│     Context & intelligence                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ┌──────┬──────────────┐                                     │
│ │ News │ 💬 Messages  │                                     │
│ └──────┴──────────────┘                                     │
│                                                             │
│ 1. Automate content creation at scale without sacrificing  │
│    quality                                                  │
│                                                             │
│ 2. Maintain brand voice consistency across all channels    │
│                                                             │
│ 3. Reduce content production costs by up to 70%            │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│              [Generate Content Plan]                        │
└─────────────────────────────────────────────────────────────┘
```

**Campi Usati**:
- ✅ `insights.recent_news` → 2 items (su 2 disponibili)
- ✅ `insights.key_messages` → 3 items (su 3 disponibili)
- ✅ `company.evidence` → 2 items (su 2 disponibili)

**Campi NON Usati**:
- ❌ `insights.positioning` → "Enterprise-grade AI content platform..."
- ❌ `insights.competitors` → ["Jasper AI", "Copy.ai", "Writesonic"]
- ❌ `insights.competitive_advantages` → [...]
- ❌ `insights.content_opportunities` → [...]

---

## 📊 Riepilogo Utilizzo Campi

### **Campi Usati (15/28 = 54%)**

| Sezione | Campo | Usato in Card |
|---------|-------|---------------|
| company | name | ✅ Card 1 |
| company | industry | ✅ Card 1 |
| company | description | ✅ Card 1 |
| company | website | ✅ Card 1 |
| company | key_offerings | ✅ Card 1 |
| company | differentiators | ✅ Card 1 |
| company | evidence | ✅ Card 1, Card 4 |
| audience | primary | ✅ Card 2 |
| audience | secondary | ✅ Card 2 |
| audience | pain_points | ✅ Card 2 |
| audience | desired_outcomes | ✅ Card 2 |
| voice | tone | ✅ Card 3 |
| voice | style_guidelines | ✅ Card 3 |
| voice | cta_preferences | ✅ Card 3 |
| voice | forbidden_phrases | ✅ Card 3 |
| insights | recent_news | ✅ Card 4 |
| insights | key_messages | ✅ Card 4 |

### **Campi NON Usati (13/28 = 46%)**

| Sezione | Campo | Disponibile ma Non Mostrato |
|---------|-------|----------------------------|
| company | legal_name | ❌ |
| company | headquarters | ❌ |
| company | size_range | ❌ |
| audience | demographics | ❌ |
| audience | psychographics | ❌ |
| voice | preferred_phrases | ❌ |
| insights | positioning | ❌ |
| insights | competitors | ❌ |
| insights | market_position | ❌ |
| insights | competitive_advantages | ❌ |
| insights | recent_developments | ❌ |
| insights | content_opportunities | ❌ |
| metadata | clarifying_questions | ❌ (mostrate altrove) |

---

## 💡 Opportunità di Miglioramento

### **1. Mostrare Campi Esistenti**

Puoi facilmente aggiungere questi campi alle card esistenti:

- **Card 1 (Company)**: `headquarters`, `size_range`
- **Card 2 (Audience)**: `demographics`, `psychographics`
- **Card 3 (Voice)**: `preferred_phrases`
- **Card 4 (Insights)**: `positioning`, `competitors`, `competitive_advantages`

### **2. Creare Nuove Card**

Potresti creare card dedicate per:

- **Competitors Card**: Mostrare `insights.competitors` + `competitive_advantages`
- **Content Opportunities Card**: Mostrare `insights.content_opportunities`
- **Company Details Card**: Mostrare `legal_name`, `headquarters`, `size_range`

### **3. Aumentare Limiti**

Attualmente molti array sono limitati (es. max 3-4 items). Potresti:

- Aumentare i limiti (es. 4 → 6 offerings)
- Aggiungere "Show more" button
- Creare modal con lista completa

---

**Ultimo aggiornamento**: 2025-10-23  
**Versione**: 1.0

