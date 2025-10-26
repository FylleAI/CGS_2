# 🎯 CGS_2 - Feature Overview Essentials

**Progetto**: Content Generation System v2  
**Organizzazione**: Fylle AI  
**Data**: 2025-10-25  
**Versione**: 1.0

---

## 📋 Indice

1. [Integrazione HubSpot](#-integrazione-hubspot)
2. [Integrazione LinkedIn](#-integrazione-linkedin)
3. [Concetto Card](#-concetto-card)
4. [Card Interazione](#-card-interazione)
5. [Card Architettura e Gestione Informazione](#-card-architettura-e-gestione-informazione)
6. [Concetto Trasparenza](#-concetto-trasparenza)

---

## 🔗 Integrazione HubSpot

**Status**: 🟡 Pianificato

L'integrazione HubSpot permette a Fylle di sincronizzare automaticamente i contatti, le aziende e le interazioni dal CRM dell'utente per arricchire il contesto aziendale utilizzato nella generazione di contenuti. Il sistema importa dati strutturati (nome azienda, settore, dimensione, deal stage) e li trasforma in **Context Cards** che alimentano gli agenti AI, consentendo la personalizzazione automatica di email, post LinkedIn e newsletter basate sul lifecycle stage del prospect. L'integrazione è bidirezionale: non solo importa dati da HubSpot, ma può anche pubblicare contenuti generati direttamente come note, email o task nel CRM, creando un loop chiuso tra generazione contenuti e sales engagement. La sincronizzazione avviene tramite webhook per aggiornamenti real-time e batch jobs notturni per import massivi, garantendo che il contesto AI sia sempre allineato con lo stato attuale del CRM senza duplicazioni o conflitti di dati.

**Riferimenti**:
- Documentazione: `docs/publishing/` (placeholder)
- Architettura: Multi-tenant con OAuth 2.0
- Sync: Webhook + Batch jobs

---

## 📱 Integrazione LinkedIn

**Status**: 🟡 Pianificato

L'integrazione LinkedIn trasforma Fylle in un assistente intelligente per la pubblicazione professionale, permettendo agli utenti di generare, schedulare e pubblicare post direttamente sulla piattaforma senza lasciare l'applicazione. Il sistema utilizza le **Context Cards** (brand voice, audience, recent news) per creare post personalizzati che rispettano il tono aziendale e sono ottimizzati per l'engagement LinkedIn (hashtag, menzioni, lunghezza ottimale 1200-1500 caratteri). Gli utenti possono scegliere tra pubblicazione immediata, scheduling per orari ottimali (basati su analytics storici), o salvataggio come bozza per revisione manuale. L'integrazione include anche un sistema di analytics che traccia performance (impressions, engagement rate, click-through) e alimenta un feedback loop che migliora progressivamente la qualità dei contenuti generati, imparando quali tipologie di post performano meglio per ogni specifico brand e audience. La pubblicazione supporta sia post testuali che caroselli multi-immagine, con preview real-time di come apparirà il contenuto sul feed LinkedIn.

**Riferimenti**:
- Documentazione: `docs/publishing/` (placeholder)
- API: LinkedIn Marketing API v2
- Features: Scheduling, Analytics, A/B testing

---

## 🎴 Concetto Card

**Status**: ✅ Implementato

Le **Context Cards** sono l'unità fondamentale di conoscenza in Fylle: contenitori strutturati di informazioni aziendali che rappresentano diversi aspetti del business (prodotto, audience, brand voice, competitor, performance, insights). Ogni card è un documento JSONB flessibile che combina dati strutturati (campi predefiniti come company_name, industry) con contenuto dinamico (insights generati da AI, metriche di performance), ed è arricchita da metadati di qualità (confidence score, source references, versioning). Le card sono **multi-tenant** (isolate per tenant_id), **versionabili** (ogni modifica crea una nuova versione mantenendo lo storico), e **relazionabili** (possono essere linkate tra loro per creare grafi di conoscenza). Il sistema supporta 8 tipi di card principali (product, persona, campaign, topic, brand_voice, competitor, performance, insight), ognuna con uno schema specifico ma estensibile. Le card non sono statiche: vengono continuamente aggiornate da workflow di onboarding, ricerche Perplexity, sintesi Gemini, e feedback utente, creando un **"living knowledge base"** che evolve con il business dell'utente e migliora la qualità dei contenuti generati nel tempo.

**Riferimenti**:
- Schema: `DATABASE_SCHEMA_ADAPTIVE_CARDS.sql`
- Modelli: `onboarding/domain/models.py`
- Tipi: 8 card types (product, persona, campaign, topic, brand_voice, competitor, performance, insight)

---

## 🔄 Card Interazione

**Status**: ✅ Implementato

Le card non sono solo repository passivi di dati, ma **interfacce interattive** che permettono agli utenti di visualizzare, verificare, modificare e arricchire la conoscenza che l'AI ha del loro business. Ogni card è renderizzata nel frontend come un componente React interattivo (FylleCard) con sezioni espandibili, badge di confidenza, e azioni contestuali (edit, refine, verify, archive). Gli utenti possono cliccare su qualsiasi campo per vedere le **source citations** (da dove proviene l'informazione), il **confidence score** (quanto l'AI è sicura), e la **agent usage history** (quali agenti hanno usato quel dato e per cosa). Le card supportano **feedback in-line**: se un utente corregge un'informazione (es. "il mio target è SMB, non Enterprise"), il sistema aggiorna immediatamente la card, aumenta la confidence a 100%, e propaga la modifica a tutte le card correlate e ai contenuti futuri. Le card sono anche **collaborative**: più utenti dello stesso tenant possono commentare, suggerire modifiche, e votare sulla qualità delle informazioni, creando un processo di "crowd-sourced verification" che migliora continuamente l'accuratezza del knowledge base aziendale.

**Riferimenti**:
- Frontend: `onboarding-frontend/src/components/cards/`
- Componenti: FylleCard, CardHeader, CardContent, CardFooter
- Interazioni: Edit, Refine, Verify, Archive, Comment

---

## 🏗️ Card Architettura e Gestione Informazione

**Status**: ✅ Implementato (con enhancement pianificati)

L'architettura delle card segue un **approccio ibrido** che bilancia flessibilità e governance: i dati sono memorizzati in PostgreSQL con schema flessibile JSONB (permettendo evoluzione rapida senza migration), ma con **materialized views** per analytics performanti e **Row-Level Security (RLS)** per isolamento multi-tenant garantito a livello database. Ogni card ha un ciclo di vita gestito da una **state machine** (draft → active → archived) con transizioni tracciate in `card_performance_events`. Le informazioni nelle card provengono da **multiple fonti** orchestrate in pipeline: (1) **Onboarding** - dati iniziali da form utente e ricerca Perplexity, (2) **Company Context** - snapshot centralizzato che funge da "single source of truth" sincronizzato con le card, (3) **Workflow Results** - contenuti generati e performance metrics che arricchiscono le card nel tempo, (4) **User Feedback** - correzioni e verifiche manuali con confidence 100%. Il sistema implementa **automatic sync** tramite trigger PostgreSQL che mantengono coerenza tra `company_contexts` (master data) e `context_cards` (derived views), mentre un **deduplication engine** previene card duplicate usando similarity matching su embedding vettoriali. Le card sono ottimizzate per **RAG (Retrieval-Augmented Generation)**: ogni card ha embedding vettoriali per semantic search, metadata per filtering, e reference tracking per explainability, permettendo agli agenti AI di recuperare esattamente il contesto rilevante per ogni task di generazione contenuti.

**Riferimenti**:
- Database: `context_cards` table con JSONB + RLS
- Sync: `company_contexts` ↔️ `context_cards` via triggers
- RAG: Vector embeddings + semantic search
- Governance: Versioning, deduplication, quality scores

---

## 🔍 Concetto Trasparenza

**Status**: 📋 Pianificato (6 settimane, 63 SP, ROI 2,150%)

La **Transparency & Explainability** è il differenziatore strategico di Fylle: mentre i competitor offrono "AI black box", Fylle permette agli utenti di **vedere cosa l'AI sa, capire come lo sa, e verificare che sia corretto**. Ogni singolo campo in ogni card ha **field-level source citations** (URL, excerpt, confidence score, extraction method) che mostrano esattamente da dove proviene l'informazione - se da ricerca Perplexity (con link alla fonte), sintesi Gemini (con reasoning), o input utente (confidence 100%). Il sistema traccia **agent usage** in una tabella dedicata (`agent_card_usage`) che registra ogni volta che un agente legge una card, quali campi ha usato, e per quale scopo (es. "Copywriter ha usato brand_voice.tone per generare LinkedIn post"), creando un **audit trail completo** che risponde alla domanda "perché l'AI ha scritto questo?". Gli utenti possono **verificare e correggere** qualsiasi informazione direttamente nell'interfaccia: cliccando su un campo vedono le fonti, possono marcare come "verified" o "incorrect", e le correzioni propagano immediatamente a tutti i contenuti futuri con confidence aggiornata. Questa trasparenza non è solo UX, ma **compliance-ready**: soddisfa GDPR Article 22 (right to explanation), EU AI Act (transparency obligations), e prepara Fylle per certificazioni enterprise (SOC 2, ISO 27001), trasformando la piattaforma da "AI tool" a "trusted AI partner" che le aziende possono auditare, verificare, e di cui possono fidarsi per decisioni business-critical.

**Riferimenti**:
- Documentazione: `docs/transparency/`
- Executive Summary: ROI 2,150%, payback 16 giorni, +€900k ARR
- Componenti: FieldReference, SourceCitation, AgentUsageTracker
- Compliance: GDPR, EU AI Act, SOC 2 ready

---

## 📊 Riepilogo Status

| Feature | Status | Priorità | Timeline | Investment |
|---------|--------|----------|----------|------------|
| **Integrazione HubSpot** | 🟡 Pianificato | Alta | 4-6 settimane | €30-40k |
| **Integrazione LinkedIn** | 🟡 Pianificato | Alta | 3-4 settimane | €25-35k |
| **Concetto Card** | ✅ Implementato | - | Completato | - |
| **Card Interazione** | ✅ Implementato | - | Completato | - |
| **Card Architettura** | ✅ Implementato | - | Completato | - |
| **Concetto Trasparenza** | 📋 Pianificato | 🔥 Critica | 6 settimane | €44k |

---

## 🎯 Priorità Strategiche

### **Immediate (Q1 2025)**
1. ✅ **Trasparenza & Explainability** - Differenziatore competitivo critico
2. 🟡 **Integrazione LinkedIn** - Quick win per user engagement
3. 🟡 **Newsletter Personalizzata** - Retention driver (+30%)

### **Short-term (Q2 2025)**
4. 🟡 **Integrazione HubSpot** - Enterprise readiness
5. 🟡 **Advanced Analytics** - Data-driven optimization
6. 🟡 **Multi-language Support** - Market expansion

### **Long-term (H2 2025)**
7. 🟡 **API Platform** - Developer ecosystem
8. 🟡 **White-label Solution** - B2B2C expansion
9. 🟡 **AI Model Fine-tuning** - Performance optimization

---

## 🔗 Collegamenti Rapidi

### **Documentazione Completa**
- 📚 [Indice Generale](./README.md)
- 🏗️ [Architettura Sistema](./architecture/README.md)
- 🔍 [Transparency Feature](./transparency/README.md)
- 📧 [Newsletter Personalization](./newsletter-personalization/README_NEWSLETTER_PERSONALIZATION.md)

### **Per Ruolo**
- **Executive**: [Transparency Executive Summary](./transparency/EXECUTIVE_SUMMARY.md)
- **Product Manager**: [Newsletter Summary](./newsletter-personalization/NEWSLETTER_PERSONALIZATION_SUMMARY.md)
- **Developer**: [Transparency Technical Spec](./transparency/TRANSPARENCY_EXPLAINABILITY_FEATURE.md)
- **Tech Lead**: [Card Architecture](./CARD_SYSTEM_ARCHITECTURE.md)

---

## 📞 Contatti

**Team**: Fylle AI  
**Email**: davide@fylle.ai  
**Repository**: https://github.com/FylleAI/CGS_2.git

---

**Ultimo Aggiornamento**: 2025-10-25  
**Versione**: 1.0  
**Status**: ✅ Completo

