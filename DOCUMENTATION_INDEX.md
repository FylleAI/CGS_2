# 📚 Onboarding System: Documentation Index

**Versione**: 2.0 (Semplificata)  
**Data**: 2025-10-23  
**Autore**: Augment Agent

---

## 🎯 Overview

Il sistema di onboarding è stato **semplificato da 8 a 2 goal types** (-75% complessità), mantenendo un'architettura **metadata-driven** robusta e scalabile.

### Goal Types Supportati

1. **Company Snapshot** → Card visuale del profilo aziendale
2. **Content Generation** → Generazione contenuto generico (blog post)

### Caratteristiche Principali

- ✅ **Workflow Unificato**: `onboarding_content_generator` in CGS
- ✅ **Metadata-Driven Rendering**: Backend controlla il frontend tramite `display_type`
- ✅ **Domande Personalizzate**: Generate da Gemini basate su ricerca reale
- ✅ **RAG Caching**: Riutilizzo snapshot per aziende già ricercate
- ✅ **Fallback Robusti**: Cascade di fallback per data extraction
- ✅ **Rich Context**: CGS riceve snapshot completo + risposte utente

---

## 📖 Documenti Disponibili

### 1. **ONBOARDING_FLOW_ANALYSIS.md** (Analisi Completa)

**Scopo**: Analisi approfondita del flusso end-to-end

**Contenuto**:
- 📦 **Parte 1**: Analisi Payload CGS
  - Company Snapshot Payload
  - Content Generation Payload
  - Differenze chiave tra i due goal types
  
- 🎯 **Parte 2**: Sistema Domande Personalizzate
  - Generazione domande (Gemini)
  - Raccolta risposte (Frontend → Backend)
  - Utilizzo risposte in CGS Payload
  
- 🎨 **Parte 3**: Sistema di Rendering Metadata-Driven
  - Architettura Renderer Registry
  - Company Snapshot Renderer
  - Content Renderer (Fallback)
  - Step6Results: Metadata-Driven Rendering
  
- 🔄 **Flusso Completo End-to-End**
  
- 📋 **Appendice**: Esempi Concreti dai Log
  - Log Company Snapshot (Successo)
  - Log Content Generation (Prima/Dopo Fix)
  - Esempi Clarifying Questions
  - Esempi CGS Response Metadata
  - Frontend Rendering Log
  
- 🎓 **Lezioni Apprese**

**Quando Usarlo**: Per comprendere in dettaglio come funziona il sistema

---

### 2. **QUICK_REFERENCE.md** (Riferimento Rapido)

**Scopo**: Guida rapida per sviluppatori

**Contenuto**:
- 📋 Goal Types (tabella comparativa)
- 🔄 Flusso Rapido
- 📦 Payload Structure (esempi JSON)
- 🎯 Clarifying Questions (generazione, validazione, utilizzo)
- 🎨 Rendering System (registry pattern, fallback cascade)
- 📁 File Chiave (backend + frontend)
- 🔧 Settings Mappings
- ⚠️ Common Issues (errori comuni + fix)
- 🧪 Testing Checklist
- 📊 Metrics & Logs (success/error indicators)
- 🎓 Best Practices
- 📞 Quick Commands (backend + frontend)

**Quando Usarlo**: Per riferimento veloce durante lo sviluppo

---

### 3. **CODE_EXAMPLES.md** (Esempi di Codice)

**Scopo**: Esempi di codice pronti all'uso

**Contenuto**:
- 📦 **Payload Building Examples**
  - Company Snapshot Payload
  - Content Generation Payload
  - Intelligent Parameter Extraction
  
- 🎯 **Clarifying Questions Examples**
  - Gemini Synthesis Prompt
  - Answer Validation
  
- 🎨 **Frontend Rendering Examples**
  - Renderer Registration
  - Metadata-Driven Rendering
  
- 🔧 **Configuration Examples**
  - Settings Mappings

**Quando Usarlo**: Per copiare/incollare codice durante l'implementazione

---

### 4. **CLEANUP_SUMMARY.md** (Riepilogo Pulizia)

**Scopo**: Documentazione della semplificazione da 8 a 2 goal types

**Contenuto**:
- 🎯 Obiettivo Raggiunto
- 📊 Prima vs Dopo (8 → 2 goal types)
- 🔧 Modifiche Effettuate (backend + frontend)
- 📄 Documentazione Creata
- 🔜 Prossimi Passi Consigliati

**Quando Usarlo**: Per capire la storia del refactoring

---

### 5. **STABLE_STATE.md** (Stato Stabile)

**Scopo**: Documentazione dello stato stabile del sistema

**Contenuto**:
- ✅ Sistema Metadata-Driven: FUNZIONANTE
- ✅ Company Snapshot Renderer: FUNZIONANTE
- ✅ Fallback System: FUNZIONANTE
- ✅ TypeScript: NESSUN ERRORE
- ✅ Console: PULITA
- 🟡 UI Quality: BASIC (da migliorare)

**Quando Usarlo**: Per verificare lo stato attuale del sistema

---

## 🗺️ Diagrammi Interattivi

### 1. **Onboarding System: End-to-End Flow**

Diagramma del flusso completo da input utente a rendering finale.

**Componenti**:
- User Input
- RAG Cache
- Perplexity Research
- Gemini Synthesis
- User Answers
- Payload Building
- CGS Execution
- Frontend Rendering

---

### 2. **Data Flow: Clarifying Questions & Answers**

Sequence diagram del flusso dati per domande e risposte.

**Partecipanti**:
- User
- Frontend
- OnboardingAPI
- Gemini
- PayloadBuilder
- CGS

---

### 3. **Frontend Rendering Architecture (Metadata-Driven)**

Diagramma dell'architettura di rendering metadata-driven.

**Componenti**:
- CGS Service (Backend)
- Step6Results Component
- Renderer Registry
- Data Extractors
- Fallback Cascade
- UI Components

---

## 🚀 Getting Started

### Per Nuovi Sviluppatori

1. **Inizia con**: `QUICK_REFERENCE.md`
   - Comprendi i 2 goal types
   - Familiarizza con il flusso rapido
   - Leggi i common issues

2. **Approfondisci con**: `ONBOARDING_FLOW_ANALYSIS.md`
   - Studia il flusso end-to-end
   - Analizza gli esempi dai log
   - Comprendi le lezioni apprese

3. **Implementa con**: `CODE_EXAMPLES.md`
   - Copia esempi di payload building
   - Usa esempi di rendering
   - Segui best practices

### Per Debugging

1. **Controlla**: `QUICK_REFERENCE.md` → Common Issues
2. **Verifica**: `STABLE_STATE.md` → Stato attuale
3. **Analizza**: `ONBOARDING_FLOW_ANALYSIS.md` → Appendice (log examples)

### Per Nuove Feature

1. **Studia**: `ONBOARDING_FLOW_ANALYSIS.md` → Architettura
2. **Riferisci**: `CODE_EXAMPLES.md` → Pattern esistenti
3. **Testa**: `QUICK_REFERENCE.md` → Testing Checklist

---

## 📁 Struttura File Progetto

### Backend (Python)

```
onboarding/
├── api/
│   ├── main.py                    # FastAPI app
│   └── endpoints.py               # API endpoints
├── application/
│   ├── builders/
│   │   └── payload_builder.py     # ⭐ Costruisce payload CGS
│   └── use_cases/
│       ├── create_session.py
│       ├── research_company.py
│       ├── synthesize_snapshot.py
│       ├── collect_answers.py     # ⭐ Valida risposte
│       └── execute_onboarding.py
├── domain/
│   ├── models.py                  # Domain models
│   ├── cgs_contracts.py           # ⭐ CGS payload contracts
│   └── content_types.py
├── infrastructure/
│   ├── adapters/
│   │   ├── cgs_adapter.py         # ⭐ Invia payload a CGS
│   │   ├── gemini_adapter.py      # ⭐ Genera domande
│   │   └── perplexity_adapter.py
│   └── repositories/
│       ├── supabase_repository.py
│       └── company_context_repository.py
└── config/
    └── settings.py                # ⭐ Mappings goal → content_type
```

### Frontend (TypeScript/React)

```
onboarding-frontend/src/
├── components/
│   ├── steps/
│   │   ├── Step6Results.tsx       # ⭐ Metadata-driven rendering
│   │   └── ContentPreview.tsx
│   └── cards/
│       └── CompanySnapshotCard.tsx
├── renderers/
│   ├── RendererRegistry.ts        # ⭐ Registry pattern
│   ├── CompanySnapshotRenderer.tsx # ⭐ Snapshot renderer
│   └── ContentRenderer.tsx        # ⭐ Fallback renderer
└── types/
    └── onboarding.ts              # TypeScript types
```

---

## 🔗 Link Utili

### Repository

- **GitHub**: https://github.com/FylleAI/CGS_2
- **Branch**: `analytics-dashboard`

### Servizi Esterni

- **CGS API**: http://localhost:8000
- **Onboarding API**: http://localhost:8001
- **Frontend**: http://localhost:3002
- **Supabase**: https://iimymnlepgilbuoxnkqa.supabase.co

---

## 📞 Supporto

### Domande Frequenti

**Q: Come aggiungo un nuovo goal type?**

A: Segui questi passi:
1. Aggiungi enum in `domain/models.py` (OnboardingGoal)
2. Aggiungi mapping in `config/settings.py` (workflow + content_type)
3. Implementa payload builder in `payload_builder.py`
4. Crea renderer in `onboarding-frontend/src/renderers/`
5. Registra renderer in registry
6. Testa end-to-end

**Q: Come aggiungo un nuovo display type?**

A: Segui questi passi:
1. Crea nuovo renderer component
2. Crea data extractor function
3. Registra in `RendererRegistry`
4. CGS deve ritornare il nuovo `display_type` in metadata

**Q: Perché il rendering non funziona?**

A: Verifica:
1. CGS ritorna `display_type` in `content.metadata`
2. Renderer è registrato in registry
3. Data extractor trova i dati (fallback cascade)
4. Component riceve dati corretti

---

## 📊 Metriche di Successo

### Semplificazione

- ✅ **Goal Types**: 8 → 2 (-75%)
- ✅ **Codice Rimosso**: ~195 linee
- ✅ **Complessità**: Drasticamente ridotta

### Stabilità

- ✅ **TypeScript Errors**: 0
- ✅ **Console Errors**: 0
- ✅ **Test Coverage**: Company Snapshot funzionante

### Prossimi Obiettivi

- 🟡 **UI Quality**: Da BASIC a PROFESSIONAL
- 🟡 **Content Generation**: Renderer dedicato
- 🟡 **Testing**: Test end-to-end automatizzati

---

**Last Updated**: 2025-10-23 13:00 UTC  
**Maintained By**: Augment Agent

