# 🎯 PIANO: Workflow Generico per Onboarding

**Data**: 2025-10-16  
**Obiettivo**: Creare un workflow generico in CGS che supporti 4 tipi di contenuto diversi, attivato dalla selezione in onboarding con variabili dinamiche.

---

## 📊 ANALISI SITUAZIONE ATTUALE

### **Mapping Attuale: Goal → Workflow**

```python
# onboarding/config/settings.py
default_workflow_mappings = {
    "linkedin_post": "enhanced_article",        # ❌ Riusa workflow esistente
    "newsletter": "premium_newsletter",         # ❌ Riusa workflow esistente
    "newsletter_premium": "premium_newsletter", # ❌ Riusa workflow esistente
    "article": "enhanced_article",              # ❌ Riusa workflow esistente
}
```

**Problemi**:
1. ❌ **Riuso improprio**: LinkedIn post usa `enhanced_article` (pensato per articoli lunghi)
2. ❌ **Mancanza di flessibilità**: Non possiamo personalizzare il workflow per onboarding
3. ❌ **Limitazione**: Solo 2 workflow (enhanced_article, premium_newsletter)
4. ❌ **Nessuna variabile dinamica**: I workflow non ricevono parametri specifici da onboarding

### **Workflow CGS Disponibili**

```python
# core/infrastructure/workflows/__init__.py
WORKFLOW_HANDLERS = {
    "enhanced_article",                    # ✅ Articoli lunghi con ricerca
    "enhanced_article_with_image",         # ✅ Articoli + immagine
    "premium_newsletter",                  # ✅ Newsletter premium generica
    "siebert_premium_newsletter",          # ⚠️ Client-specific (Siebert)
    "siebert_newsletter_html",             # ⚠️ Client-specific (Siebert)
    "reopla_enhanced_article_with_image",  # ⚠️ Client-specific (Reopla)
}
```

**Osservazioni**:
- ✅ Sistema di registry dinamico già presente
- ✅ Supporto per workflow custom
- ❌ Nessun workflow generico per onboarding

---

## 🎯 OBIETTIVO FINALE

### **Nuovo Workflow: `onboarding_content_generator`**

Un **workflow generico** che:
1. ✅ Accetta **variabili dinamiche** da onboarding
2. ✅ Supporta **4 tipi di contenuto** diversi
3. ✅ Si adatta al **goal** selezionato dall'utente
4. ✅ Produce contenuti **ad alto impatto**
5. ✅ Riutilizza **company_snapshot** e **clarifying_answers**

### **4 Tipi di Contenuto da Supportare**

| # | Tipo Contenuto | Descrizione | Word Count | Caratteristiche |
|---|----------------|-------------|------------|-----------------|
| 1 | **LinkedIn Post** | Post breve e impattante | 200-400 | Hook, storytelling, CTA, emoji |
| 2 | **LinkedIn Article** | Articolo lungo thought leadership | 800-1500 | Struttura, dati, esempi, SEO |
| 3 | **Newsletter** | Newsletter curata con sezioni | 1000-1500 | Multi-sezione, link, visual |
| 4 | **Blog Post** | Articolo blog SEO-friendly | 1200-2000 | SEO, H2/H3, immagini, link |

---

## 🏗️ ARCHITETTURA PROPOSTA

### **1. Nuovo Workflow Handler**

```
core/infrastructure/workflows/handlers/
└── onboarding_content_handler.py  ← NUOVO!
```

**Responsabilità**:
- Riceve `content_type` come variabile
- Routing interno verso sub-workflow specifico
- Riutilizza company_snapshot e clarifying_answers
- Produce output ottimizzato per tipo

### **2. Mapping Aggiornato**

```python
# onboarding/config/settings.py
default_workflow_mappings = {
    "linkedin_post": "onboarding_content_generator",      # ✅ NUOVO
    "linkedin_article": "onboarding_content_generator",   # ✅ NUOVO
    "newsletter": "onboarding_content_generator",         # ✅ NUOVO
    "blog_post": "onboarding_content_generator",          # ✅ NUOVO
}
```

### **3. Variabili Dinamiche**

```python
# Payload inviato a CGS
{
    "workflow_type": "onboarding_content_generator",
    "client_profile": "onboarding",
    "context": {
        "company_snapshot": {...},           # ✅ Rich context
        "clarifying_answers": {...},         # ✅ User answers
        "content_type": "linkedin_post",     # ✅ NUOVO! Tipo contenuto
        "content_config": {                  # ✅ NUOVO! Config specifica
            "word_count": 300,
            "tone": "professional",
            "include_emoji": true,
            "include_hashtags": true,
            "include_cta": true
        }
    },
    "topic": "AI automation for SMBs",
    "target_audience": "Small business owners",
    ...
}
```

---

## 📋 PIANO DI IMPLEMENTAZIONE

### **FASE 1: Definizione Content Types** ✅ (Pianificazione)

#### **Task 1.1: Definire Enum ContentType**
- File: `onboarding/domain/models.py`
- Aggiungere `ContentType` enum con 4 valori
- Mappare `OnboardingGoal` → `ContentType`

#### **Task 1.2: Definire Content Configs**
- File: `onboarding/domain/content_configs.py` (NUOVO)
- Creare dataclass per ogni content type
- Parametri: word_count, structure, features, tone

#### **Task 1.3: Aggiornare OnboardingGoal**
- File: `onboarding/domain/models.py`
- Aggiungere nuovi goal: `LINKEDIN_ARTICLE`, `BLOG_POST`
- Mantenere backward compatibility

---

### **FASE 2: Workflow Handler Generico** 🔨 (Implementazione)

#### **Task 2.1: Creare OnboardingContentHandler**
- File: `core/infrastructure/workflows/handlers/onboarding_content_handler.py`
- Ereditare da `WorkflowHandler`
- Implementare routing per content_type
- Registrare con `@register_workflow("onboarding_content_generator")`

#### **Task 2.2: Implementare Sub-Workflows**
- `_generate_linkedin_post()` - Post breve impattante
- `_generate_linkedin_article()` - Articolo lungo
- `_generate_newsletter()` - Newsletter multi-sezione
- `_generate_blog_post()` - Blog SEO-friendly

#### **Task 2.3: Prompt Engineering**
- Creare prompt specifici per ogni content type
- Utilizzare company_snapshot per personalizzazione
- Integrare clarifying_answers nelle istruzioni

---

### **FASE 3: Payload Builder Update** 🔧 (Integrazione)

#### **Task 3.1: Aggiornare PayloadBuilder**
- File: `onboarding/application/builders/payload_builder.py`
- Aggiungere metodo `_build_onboarding_content_payload()`
- Mappare goal → content_type
- Costruire content_config dinamicamente

#### **Task 3.2: Nuovo Contract CGS**
- File: `onboarding/domain/cgs_contracts.py`
- Creare `CgsPayloadOnboardingContent` (unificato)
- Sostituire `CgsPayloadLinkedInPost` e `CgsPayloadNewsletter`
- Aggiungere campo `content_type` e `content_config`

#### **Task 3.3: Aggiornare CgsAdapter**
- File: `onboarding/infrastructure/adapters/cgs_adapter.py`
- Supportare nuovo payload type
- Passare `content_type` e `content_config` a CGS

---

### **FASE 4: Frontend Update** 🎨 (UI)

#### **Task 4.1: Aggiornare Goal Selection**
- File: `onboarding-frontend/src/components/steps/Step1CompanyInput.tsx`
- Aggiungere nuove opzioni: LinkedIn Article, Blog Post
- Aggiornare labels e descriptions

#### **Task 4.2: Aggiornare Types**
- File: `onboarding-frontend/src/types/onboarding.ts`
- Aggiungere nuovi OnboardingGoal values
- Sincronizzare con backend

---

### **FASE 5: Testing & Validation** ✅ (Verifica)

#### **Task 5.1: Unit Tests**
- Test `OnboardingContentHandler` routing
- Test payload building per ogni content type
- Test prompt generation

#### **Task 5.2: Integration Tests**
- Test end-to-end per ogni content type
- Verificare output quality
- Validare metriche (word count, structure)

#### **Task 5.3: A/B Testing**
- Confrontare output vecchio vs nuovo workflow
- Validare miglioramenti qualità
- Raccogliere feedback utenti

---

## 🎨 DESIGN DETTAGLIATO: Content Types

### **1. LinkedIn Post** (200-400 parole)

**Struttura**:
```
[HOOK] - Frase impattante che cattura attenzione
[PROBLEMA] - Pain point del target audience
[SOLUZIONE] - Come il brand risolve il problema
[PROOF] - Dato/esempio concreto
[CTA] - Call to action chiara
[HASHTAGS] - 3-5 hashtag rilevanti
```

**Features**:
- ✅ Emoji strategici (max 3-4)
- ✅ Line breaks per leggibilità
- ✅ Tone conversazionale
- ✅ Personal storytelling
- ✅ Engagement-focused

**Prompt Template**:
```
You are a LinkedIn content expert creating a high-impact post.

COMPANY: {company_name}
INDUSTRY: {industry}
TARGET AUDIENCE: {target_audience}
DIFFERENTIATORS: {differentiators}

TOPIC: {topic}
TONE: {tone}

STRUCTURE:
1. Hook (1 sentence, max 15 words)
2. Problem statement (2-3 sentences)
3. Solution (2-3 sentences, highlight differentiators)
4. Proof point (1 data point or example)
5. CTA (1 sentence, actionable)

REQUIREMENTS:
- 200-400 words
- Use 3-4 strategic emojis
- Include line breaks for readability
- End with 3-5 relevant hashtags
- Conversational, engaging tone
```

---

### **2. LinkedIn Article** (800-1500 parole)

**Struttura**:
```
[TITLE] - Titolo SEO-friendly
[INTRO] - Hook + context
[SECTION 1] - Problema/Challenge
[SECTION 2] - Analisi/Insights
[SECTION 3] - Soluzione/Framework
[SECTION 4] - Esempi/Case studies
[CONCLUSION] - Recap + CTA
```

**Features**:
- ✅ H2/H3 headings
- ✅ Bullet points e liste
- ✅ Dati e statistiche
- ✅ Esempi concreti
- ✅ Thought leadership tone

---

### **3. Newsletter** (1000-1500 parole)

**Struttura**:
```
[SUBJECT LINE] - Catchy subject
[INTRO] - Benvenuto + tema
[SECTION 1] - Trend/News principale
[SECTION 2] - Insight/Analisi
[SECTION 3] - Tip/Consiglio pratico
[SECTION 4] - Risorse/Link
[OUTRO] - CTA + firma
```

**Features**:
- ✅ Multi-sezione con titoli
- ✅ Link a risorse esterne
- ✅ Visual breaks (emoji, separatori)
- ✅ Scannable format
- ✅ Personal touch

---

### **4. Blog Post** (1200-2000 parole)

**Struttura**:
```
[SEO TITLE] - Keyword-optimized
[META DESCRIPTION] - 150-160 caratteri
[INTRO] - Hook + preview
[H2] - Sezione principale 1
[H3] - Sottosezione
[H2] - Sezione principale 2
[H3] - Sottosezione
[CONCLUSION] - Recap + CTA
[FAQ] - 3-5 domande frequenti
```

**Features**:
- ✅ SEO-optimized (keywords, meta)
- ✅ H2/H3 structure
- ✅ Internal/external links
- ✅ Image suggestions
- ✅ Long-form, comprehensive

---

## 🔄 FLUSSO COMPLETO

```
┌─────────────────────────────────────────────────────────────┐
│ 1. USER SELECTS GOAL                                        │
│    Frontend: "LinkedIn Post"                                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. ONBOARDING BACKEND                                       │
│    - Research (Perplexity)                                  │
│    - Synthesis (Gemini) → company_snapshot                  │
│    - Questions → clarifying_answers                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. PAYLOAD BUILDER                                          │
│    goal="linkedin_post" →                                   │
│    workflow="onboarding_content_generator"                  │
│    content_type="linkedin_post"                             │
│    content_config={word_count: 300, ...}                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. CGS WORKFLOW EXECUTION                                   │
│    OnboardingContentHandler.execute()                       │
│    ├─ Route to _generate_linkedin_post()                    │
│    ├─ Use company_snapshot for context                      │
│    ├─ Apply content_config                                  │
│    └─ Generate optimized content                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. RESULT                                                   │
│    - High-impact LinkedIn post (300 words)                  │
│    - Personalized with company differentiators              │
│    - Optimized structure + emoji + hashtags                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 FILE DA CREARE/MODIFICARE

### **Nuovi File** (6)
1. ✅ `core/infrastructure/workflows/handlers/onboarding_content_handler.py`
2. ✅ `onboarding/domain/content_configs.py`
3. ✅ `core/infrastructure/workflows/templates/onboarding_content_generator.json`
4. ✅ `tests/workflows/test_onboarding_content_handler.py`
5. ✅ `docs/ONBOARDING_CONTENT_TYPES.md`
6. ✅ `docs/WORKFLOW_ONBOARDING_CONTENT_GENERATOR.md`

### **File da Modificare** (8)
1. ✅ `onboarding/domain/models.py` - Aggiungere ContentType enum + nuovi goals
2. ✅ `onboarding/config/settings.py` - Aggiornare workflow_mappings
3. ✅ `onboarding/application/builders/payload_builder.py` - Nuovo metodo build
4. ✅ `onboarding/domain/cgs_contracts.py` - Nuovo payload unificato
5. ✅ `onboarding/infrastructure/adapters/cgs_adapter.py` - Supporto nuovo payload
6. ✅ `onboarding-frontend/src/types/onboarding.ts` - Nuovi goal types
7. ✅ `onboarding-frontend/src/components/steps/Step1CompanyInput.tsx` - Nuove opzioni
8. ✅ `core/infrastructure/workflows/__init__.py` - Import nuovo handler

---

## ⏱️ STIMA TEMPI

| Fase | Tasks | Tempo Stimato |
|------|-------|---------------|
| **FASE 1** | Definizione Content Types | 2-3 ore |
| **FASE 2** | Workflow Handler | 6-8 ore |
| **FASE 3** | Payload Builder Update | 4-5 ore |
| **FASE 4** | Frontend Update | 2-3 ore |
| **FASE 5** | Testing & Validation | 4-6 ore |
| **TOTALE** | | **18-25 ore** |

---

## 🎯 PROSSIMI PASSI IMMEDIATI

1. **Conferma Approccio**: Validare architettura proposta
2. **Definire Content Types**: Finalizzare 4 tipi di contenuto
3. **Creare Task List**: Breakdown dettagliato con task management
4. **Iniziare FASE 1**: Definizione enum e configs

---

**Fine Documento**

