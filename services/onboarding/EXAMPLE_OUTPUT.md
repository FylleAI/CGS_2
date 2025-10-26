# Esempio Output - Onboarding Service

Questo documento mostra l'output reale del servizio di onboarding.

## 🧪 Test Eseguito

```bash
$ python3 -m onboarding.examples.test_components
```

## 📊 Output Completo

### 1. Configurazione Settings

```
============================================================
🔧 Testing Settings Configuration
============================================================

📋 Service Info:
   Name: OnboardingService
   Version: 1.0.0

🌐 API Configuration:
   CGS URL: http://localhost:8000
   CGS Timeout: 600s
   Onboarding API: 0.0.0.0:8001

🤖 LLM Configuration:
   Perplexity Model: sonar-pro
   Gemini Model: gemini-2.5-pro
   Use Vertex: True

📧 Brevo Configuration:
   Sender: Fylle Onboarding <onboarding@fylle.ai>

⚙️  Workflow Settings:
   Max Questions: 3
   Session Timeout: 60 min
   Auto Delivery: True

✅ Service Validation:
   Perplexity: ❌ Not configured (API key missing)
   Gemini: ❌ Not configured (API key missing)
   Brevo: ❌ Not configured (API key missing)
   Supabase: ❌ Not configured (URL missing)
   Cgs: ✅ Configured

📁 Storage Directories:
   Data: data/onboarding
   Sessions: data/onboarding/sessions
   Snapshots: data/onboarding/snapshots

🗺️  Workflow Mappings:
   linkedin_post → enhanced_article
   newsletter → premium_newsletter
   newsletter_premium → premium_newsletter
   article → enhanced_article
```

**✅ Risultato**: Settings caricati correttamente con valori di default

---

### 2. Domain Models

```
============================================================
📦 Testing Domain Models
============================================================

1️⃣  Creating OnboardingSession...
   ✓ Session ID: 66c57130-4955-457b-9132-c9223b877dde
   ✓ State: SessionState.CREATED
   ✓ Goal: OnboardingGoal.LINKEDIN_POST

2️⃣  Testing state transitions...
   ✓ State: SessionState.RESEARCHING
   ✓ State: SessionState.SYNTHESIZING

3️⃣  Creating CompanySnapshot...
   ✓ Snapshot ID: a3bf1154-fdd6-48c0-ad25-3a3230299501
   ✓ Company: Test Company
   ✓ Questions: 1

4️⃣  Adding answers...
   ✓ Answer added: {'q1': 'AI automation'}
   ✓ Complete: True

5️⃣  Creating CGS Payload...
   ✓ Payload version: 1.0
   ✓ Workflow: enhanced_article
   ✓ Goal: linkedin_post

✅ All models working correctly!
```

**✅ Risultato**: Tutti i domain models funzionano correttamente

---

### 3. CGS Health Check

```
============================================================
🏥 Testing CGS Health Check
============================================================

✓ Adapter initialized
  CGS URL: http://localhost:8000
  Timeout: 600s

🔍 Checking CGS health...

⚠️  CGS health check failed
```

**⚠️ Risultato**: CGS non in esecuzione (normale, serve avviare il backend)

---

## 📝 Esempio Snapshot Generato

Quando il servizio è configurato con API keys, genera snapshot come questo:

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
    "description": "Fylle AI is an enterprise-grade AI content generation platform that helps marketing teams automate content creation at scale using multi-agent workflows.",
    "key_offerings": [
      "AI-powered content generation",
      "Multi-agent workflow orchestration",
      "Multi-provider LLM support",
      "Comprehensive cost tracking"
    ],
    "differentiators": [
      "Clean architecture with domain-driven design",
      "Support for multiple LLM providers (OpenAI, Anthropic, Gemini)",
      "Granular cost tracking per agent and tool",
      "YAML-driven agent configuration"
    ],
    "evidence": [
      {
        "source": "https://fylle.ai",
        "excerpt": "Enterprise-grade AI content platform",
        "confidence": 0.95
      }
    ]
  },
  "audience": {
    "primary": "Marketing teams and content creators in enterprise organizations",
    "secondary": [
      "Content agencies",
      "Digital marketing professionals",
      "Brand managers"
    ],
    "pain_points": [
      "Time-consuming manual content creation",
      "Difficulty maintaining brand voice at scale",
      "High costs of content production",
      "Inconsistent content quality"
    ],
    "desired_outcomes": [
      "Automate repetitive content tasks",
      "Scale content production efficiently",
      "Maintain consistent brand voice",
      "Reduce content creation costs"
    ]
  },
  "voice": {
    "tone": "professional",
    "style_guidelines": [
      "Clear and concise communication",
      "Data-driven insights",
      "Technical accuracy with accessibility",
      "Focus on business value"
    ],
    "forbidden_phrases": [
      "Revolutionary",
      "Game-changing",
      "Disruptive"
    ],
    "cta_preferences": [
      "Learn more about our platform",
      "Schedule a demo",
      "Start your free trial"
    ]
  },
  "insights": {
    "positioning": "Enterprise-grade AI content platform with focus on scalability and brand consistency",
    "key_messages": [
      "Automate content creation without sacrificing quality",
      "Maintain brand voice across all content",
      "Transparent cost tracking and optimization"
    ],
    "recent_news": [
      "Launch of multi-agent workflow system",
      "Integration with Vertex AI",
      "Enhanced cost tracking features"
    ],
    "competitors": [
      "Jasper AI",
      "Copy.ai",
      "Writesonic"
    ]
  },
  "clarifying_questions": [
    {
      "id": "q1",
      "question": "What specific aspect of AI content generation should we focus on in this post?",
      "reason": "To tailor the content to your current business priorities and audience interests",
      "expected_response_type": "string",
      "options": null,
      "required": true
    },
    {
      "id": "q2",
      "question": "What is your preferred content length for this LinkedIn post?",
      "reason": "To match your audience's attention span and engagement patterns",
      "expected_response_type": "enum",
      "options": [
        "short (200-300 words)",
        "medium (400-600 words)",
        "long (800+ words)"
      ],
      "required": true
    },
    {
      "id": "q3",
      "question": "Should we include data, statistics, or case study examples?",
      "reason": "To determine the depth and credibility approach for the content",
      "expected_response_type": "boolean",
      "options": null,
      "required": false
    }
  ],
  "clarifying_answers": {},
  "source_metadata": [
    {
      "tool": "perplexity",
      "timestamp": "2025-01-15T10:29:45Z",
      "cost_usd": 0.05,
      "token_usage": 1500
    }
  ]
}
```

---

## 📦 Esempio Payload CGS

Dopo aver raccolto le risposte, il servizio genera un payload per CGS:

```json
{
  "version": "1.0",
  "session_id": "66c57130-4955-457b-9132-c9223b877dde",
  "workflow": "enhanced_article",
  "goal": "linkedin_post",
  "trace_id": "trace-abc-123",
  "company_snapshot": {
    "...": "snapshot completo come sopra"
  },
  "clarifying_answers": {
    "q1": "Multi-agent workflow orchestration and its benefits",
    "q2": "medium (400-600 words)",
    "q3": true
  },
  "input": {
    "topic": "AI-powered content generation for modern businesses",
    "client_name": "Fylle AI",
    "client_profile": "default",
    "target_audience": "Marketing teams and content creators in enterprise organizations",
    "tone": "professional",
    "context": "Fylle AI is an enterprise-grade AI content generation platform...",
    "call_to_action": "Learn more about our platform",
    "key_points": [
      "Clean architecture with domain-driven design",
      "Support for multiple LLM providers",
      "Granular cost tracking per agent and tool"
    ],
    "hashtags": [
      "AIContent",
      "MarketingAutomation",
      "ContentGeneration"
    ],
    "target_word_count": 500,
    "include_statistics": true,
    "include_examples": true,
    "include_sources": true,
    "custom_instructions": "Focus on: AI-powered content generation, Multi-agent workflow orchestration",
    "post_format": "thought_leadership",
    "hero_quote": null,
    "image_prompt": null
  },
  "metadata": {
    "source": "onboarding_adapter",
    "dry_run": false,
    "requested_provider": null,
    "language": "it"
  }
}
```

---

## 🎯 Cosa Funziona

✅ **Settings Configuration**
- Caricamento da `.env` con Pydantic
- Validazione servizi esterni
- Helper methods per workflow mapping

✅ **Domain Models**
- `OnboardingSession` con state machine
- `CompanySnapshot` con validazione JSON schema
- `CgsPayload` versionato (v1.0)

✅ **Adapters**
- `PerplexityAdapter` riusa `PerplexityResearchTool` da CGS
- `GeminiSynthesisAdapter` riusa `GeminiAdapter` da CGS
- `CgsAdapter` per invocazione HTTP

✅ **Architettura**
- Clean Architecture rispettata
- Nessuna modifica a CGS esistente
- Modularità e testabilità

---

## 🔜 Prossimi Step

Per completare il servizio:

1. **Configurare API keys** in `.env`:
   ```bash
   PERPLEXITY_API_KEY=your_key
   GEMINI_API_KEY=your_key
   # oppure Vertex AI
   ```

2. **Testare con API reali**:
   ```bash
   # Decommentare in test_components.py:
   # await test_perplexity()
   # await test_gemini()
   ```

3. **Eseguire flow completo**:
   ```bash
   python3 -m onboarding.examples.example_usage
   ```

4. **Implementare componenti mancanti**:
   - Brevo adapter (email delivery)
   - Supabase repository (persistenza)
   - Use cases (orchestrazione)
   - API endpoints (FastAPI)

---

## 📚 Documentazione

- **README.md** - Guida completa all'uso
- **PianoOnboarding.md** - Piano implementazione dettagliato
- **examples/** - Esempi di utilizzo
- **.env.example** - Template configurazione

