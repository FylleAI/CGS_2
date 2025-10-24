# 📊 PIANO: Dashboard Analytics per Onboarding

**Data**: 2025-10-16  
**Obiettivo**: Trasformare l'onboarding da generatore di contenuti a **dashboard analytics aziendale** con visualizzazione stile dashboard finanziaria.

---

## 🎯 OBIETTIVO FINALE

### **Cosa Cambia**

#### **PRIMA** (Attuale):
- ✅ Survey con domande specifiche per content type
- ✅ Genera contenuto (LinkedIn Post, Article, Newsletter, Blog)
- ✅ Mostra contenuto in preview semplice con Copy/Download
- ✅ Focus: **Generazione contenuto**

#### **DOPO** (Nuovo):
- ✨ Survey con **variabili generiche** (Variabile 1/2/3/4)
- ✨ Payload: **Company Snapshot + Variabili**
- ✨ Workflow genera: **Company Analytics Report**
- ✨ Visualizzazione: **Dashboard stile finanziaria** (reference image)
- ✨ Focus: **Analisi aziendale e insights**

---

## 📋 CONTENUTO DEL REPORT GENERATO

### **Nuovo Output: Company Analytics Report**

Il workflow `onboarding_content_generator` (rinominato in `onboarding_analytics_generator`) genera:

```markdown
# Company Analytics Report: {company_name}

## 1. Executive Summary
- Company overview
- Market position
- Key strengths
- Critical opportunities

## 2. Content Opportunities Analysis
- Recommended content types (LinkedIn, Blog, Newsletter)
- Topic suggestions based on differentiators
- Audience targeting recommendations
- Content calendar suggestions

## 3. Optimization Insights
- Brand voice optimization
- Messaging improvements
- SEO opportunities
- Social media strategy

## 4. Competitor Intelligence
- Main competitors identified
- Competitive advantages
- Market gaps
- Differentiation strategies

## 5. Actionable Recommendations
- Quick wins (0-30 days)
- Medium-term initiatives (1-3 months)
- Long-term strategy (3-6 months)
- KPIs to track
```

---

## 🎨 NUOVA VISUALIZZAZIONE: DASHBOARD ANALYTICS

### **Ispirazione: Dashboard Finanziaria**

Basato sulla reference image fornita, creiamo una dashboard con:

#### **Layout Grid (3 colonne)**

```
┌─────────────────────────────────────────────────────────────┐
│  HEADER: Company Name + Logo                                │
├─────────────────┬─────────────────┬─────────────────────────┤
│                 │                 │                         │
│  CARD 1         │  CARD 2         │  CARD 3                 │
│  Company Score  │  Content Opps   │  Competitor Intel       │
│  (Gauge)        │  (Number)       │  (List)                 │
│                 │                 │                         │
├─────────────────┴─────────────────┴─────────────────────────┤
│                                                               │
│  CARD 4: Optimization Insights                               │
│  (Multi-section with icons)                                  │
│                                                               │
├─────────────────┬─────────────────┬─────────────────────────┤
│                 │                 │                         │
│  CARD 5         │  CARD 6         │  CARD 7                 │
│  Quick Wins     │  Content Types  │  Metrics                │
│  (Checklist)    │  (Chart)        │  (Stats)                │
│                 │                 │                         │
├─────────────────┴─────────────────┴─────────────────────────┤
│                                                               │
│  CARD 8: Full Report (Expandable)                           │
│  (Markdown content with sections)                            │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

#### **Card Components**

1. **Company Score Card** (Top-left)
   - Circular gauge (0-100)
   - Color gradient (red → yellow → green)
   - Label: "Overall Readiness Score"
   - Subtitle: "Based on 5 factors"

2. **Content Opportunities Card** (Top-center)
   - Large number: "12 Opportunities"
   - Icon: 💡
   - Breakdown: "4 LinkedIn, 5 Blog, 3 Newsletter"

3. **Competitor Intelligence Card** (Top-right)
   - List of 3-5 competitors
   - Avatar icons
   - "View Details" button

4. **Optimization Insights Card** (Full-width)
   - 4 sections with icons:
     - 🎯 Brand Voice
     - 📈 SEO Opportunities
     - 💬 Messaging
     - 📱 Social Strategy
   - Each with score + recommendation

5. **Quick Wins Card** (Bottom-left)
   - Checklist of 3-5 actionable items
   - Estimated time (e.g., "2 hours")
   - Priority indicator

6. **Content Types Chart** (Bottom-center)
   - Bar chart or pie chart
   - Distribution of recommended content types

7. **Metrics Card** (Bottom-right)
   - Key stats:
     - Estimated reach
     - Engagement potential
     - SEO score
     - Brand consistency

8. **Full Report Card** (Bottom full-width)
   - Expandable/collapsible
   - Full markdown report
   - Download PDF button
   - Share button

---

## 🔧 MODIFICHE TECNICHE

### **FASE 1: Backend - Workflow Update**

#### **File: `core/infrastructure/workflows/handlers/onboarding_content_handler.py`**

**Modifiche**:
1. Rinominare workflow: `onboarding_content_generator` → `onboarding_analytics_generator`
2. Cambiare output da "content" a "analytics_report"
3. Nuovo prompt per generare report strutturato
4. Output JSON con sezioni separate:
   ```json
   {
     "company_score": 78,
     "content_opportunities": [
       {"type": "linkedin_post", "topic": "...", "priority": "high"},
       ...
     ],
     "optimization_insights": {
       "brand_voice": {"score": 85, "recommendation": "..."},
       "seo": {"score": 62, "recommendation": "..."},
       ...
     },
     "competitors": [
       {"name": "Competitor A", "advantage": "..."},
       ...
     ],
     "quick_wins": [
       {"action": "...", "time": "2 hours", "impact": "high"},
       ...
     ],
     "full_report": "# Company Analytics Report\n\n..."
   }
   ```

#### **File: `onboarding/domain/models.py`**

**Modifiche**:
1. Aggiornare `OnboardingGoal`:
   ```python
   class OnboardingGoal(str, Enum):
       COMPANY_ANALYTICS = "company_analytics"  # Nuovo goal unico
   ```

2. Rimuovere goal specifici (linkedin_post, newsletter, etc.)

#### **File: `onboarding/application/builders/payload_builder.py`**

**Modifiche**:
1. Semplificare payload:
   ```python
   {
     "workflow_type": "onboarding_analytics_generator",
     "context": {
       "company_snapshot": {...},
       "variables": {
         "variable_1": "...",  # User input
         "variable_2": "...",  # User input
         "variable_3": "...",  # User input
         "variable_4": "..."   # User input
       }
     }
   }
   ```

---

### **FASE 2: Frontend - Survey Update**

#### **File: `onboarding-frontend/src/components/steps/Step1CompanyInput.tsx`**

**Modifiche**:
1. Rimuovere selezione goal (LinkedIn Post, Newsletter, etc.)
2. Unico goal: "Company Analytics"
3. Form semplificato:
   ```tsx
   - Brand Name
   - Website (optional)
   - Email
   ```

#### **File: `onboarding-frontend/src/components/steps/Step4QuestionsForm.tsx`**

**Modifiche**:
1. Domande generiche invece di specifiche per content type:
   ```
   Q1: "What is your primary business objective?" (Variable 1)
   Q2: "What is your target market?" (Variable 2)
   Q3: "What is your biggest challenge?" (Variable 3)
   Q4: "What makes you unique?" (Variable 4)
   ```

---

### **FASE 3: Frontend - Dashboard Results**

#### **File: `onboarding-frontend/src/components/steps/Step6Results.tsx`**

**COMPLETA RISCRITTURA** - Nuovo componente: `Step6Dashboard.tsx`

**Struttura**:
```tsx
import { Grid, Card, CardContent, Typography, Box } from '@mui/material';
import { Gauge } from '@mui/x-charts/Gauge';  // MUI X Charts
import { BarChart } from '@mui/x-charts/BarChart';

export const Step6Dashboard: React.FC<Props> = ({ analyticsReport }) => {
  return (
    <Box sx={{ p: 4, backgroundColor: '#f5f7fa' }}>
      {/* Header */}
      <Typography variant="h3">{analyticsReport.company_name}</Typography>
      
      {/* Grid Layout */}
      <Grid container spacing={3}>
        {/* Row 1 */}
        <Grid item xs={12} md={4}>
          <CompanyScoreCard score={analyticsReport.company_score} />
        </Grid>
        <Grid item xs={12} md={4}>
          <ContentOpportunitiesCard opportunities={analyticsReport.content_opportunities} />
        </Grid>
        <Grid item xs={12} md={4}>
          <CompetitorCard competitors={analyticsReport.competitors} />
        </Grid>
        
        {/* Row 2 */}
        <Grid item xs={12}>
          <OptimizationInsightsCard insights={analyticsReport.optimization_insights} />
        </Grid>
        
        {/* Row 3 */}
        <Grid item xs={12} md={4}>
          <QuickWinsCard wins={analyticsReport.quick_wins} />
        </Grid>
        <Grid item xs={12} md={4}>
          <ContentTypesChart data={analyticsReport.content_distribution} />
        </Grid>
        <Grid item xs={12} md={4}>
          <MetricsCard metrics={analyticsReport.metrics} />
        </Grid>
        
        {/* Row 4 */}
        <Grid item xs={12}>
          <FullReportCard report={analyticsReport.full_report} />
        </Grid>
      </Grid>
    </Box>
  );
};
```

**Nuovi Componenti da Creare**:
1. `CompanyScoreCard.tsx` - Gauge chart con score
2. `ContentOpportunitiesCard.tsx` - Number display con breakdown
3. `CompetitorCard.tsx` - List con avatars
4. `OptimizationInsightsCard.tsx` - 4-section grid con icons
5. `QuickWinsCard.tsx` - Checklist interattiva
6. `ContentTypesChart.tsx` - Bar/Pie chart
7. `MetricsCard.tsx` - Stats grid
8. `FullReportCard.tsx` - Expandable markdown viewer

---

## 📦 DIPENDENZE NUOVE

### **Frontend**
```json
{
  "@mui/x-charts": "^7.0.0",  // Per Gauge, BarChart, PieChart
  "recharts": "^2.10.0",       // Alternative per charts
  "react-markdown": "^9.0.0",  // Per rendering markdown
  "framer-motion": "^11.0.0"   // Già presente, per animations
}
```

---

## 🎨 DESIGN SYSTEM

### **Colori**
```css
--primary-green: #00D084
--secondary-blue: #4F46E5
--success-green: #10B981
--warning-yellow: #F59E0B
--danger-red: #EF4444
--background-light: #F5F7FA
--card-background: #FFFFFF
--text-primary: #1F2937
--text-secondary: #6B7280
```

### **Card Styles**
```tsx
sx={{
  borderRadius: 3,
  boxShadow: '0 4px 6px rgba(0, 0, 0, 0.05)',
  background: 'linear-gradient(135deg, #FFFFFF 0%, #F9FAFB 100%)',
  border: '1px solid rgba(0, 0, 0, 0.05)',
  transition: 'all 0.3s ease',
  '&:hover': {
    boxShadow: '0 8px 12px rgba(0, 0, 0, 0.1)',
    transform: 'translateY(-2px)',
  }
}}
```

---

## 📋 PIANO DI IMPLEMENTAZIONE

### **FASE 1: Backend Workflow** (4-6 ore)
- [ ] Modificare `onboarding_content_handler.py`
- [ ] Nuovo prompt per analytics report
- [ ] Output JSON strutturato
- [ ] Test con sessione esistente

### **FASE 2: Backend Payload** (2-3 ore)
- [ ] Aggiornare `OnboardingGoal` enum
- [ ] Semplificare `PayloadBuilder`
- [ ] Aggiornare `cgs_contracts.py`
- [ ] Test payload building

### **FASE 3: Frontend Survey** (2-3 ore)
- [ ] Semplificare Step1 (rimuovere goal selection)
- [ ] Aggiornare Step4 con domande generiche
- [ ] Aggiornare types TypeScript
- [ ] Test flow completo

### **FASE 4: Frontend Dashboard** (8-10 ore)
- [ ] Installare dipendenze (@mui/x-charts)
- [ ] Creare 8 nuovi componenti card
- [ ] Implementare layout grid
- [ ] Styling e animazioni
- [ ] Responsive design
- [ ] Test visualizzazione

### **FASE 5: Testing & Polish** (3-4 ore)
- [ ] Test end-to-end completo
- [ ] Verificare responsive
- [ ] Ottimizzare performance
- [ ] Aggiungere loading states
- [ ] Error handling

**TOTALE STIMATO**: 19-26 ore

---

## 🔄 FLUSSO COMPLETO NUOVO

```
1. USER INPUT
   ├─ Brand Name: "Acme Corp"
   ├─ Website: "acme.com"
   ├─ Email: "user@acme.com"
   └─ Goal: "Company Analytics" (fisso)

2. RESEARCH & SYNTHESIS
   ├─ Perplexity → Company research
   ├─ Gemini → CompanySnapshot
   └─ Generate 4 generic questions

3. USER ANSWERS (Variables)
   ├─ Variable 1: "Increase brand awareness"
   ├─ Variable 2: "B2B SaaS companies"
   ├─ Variable 3: "Limited content resources"
   └─ Variable 4: "AI-powered automation"

4. CGS EXECUTION
   ├─ Workflow: onboarding_analytics_generator
   ├─ Input: CompanySnapshot + Variables
   └─ Output: Analytics Report (JSON)

5. DASHBOARD VISUALIZATION
   ├─ Company Score: 78/100
   ├─ Content Opportunities: 12
   ├─ Optimization Insights: 4 areas
   ├─ Competitor Intel: 5 competitors
   ├─ Quick Wins: 6 actions
   └─ Full Report: Markdown
```

---

## ✅ CHECKLIST PRE-IMPLEMENTAZIONE

Prima di iniziare, verificare:
- [ ] Nuovo branch creato (`analytics-dashboard` o simile)
- [ ] Servizi backend/frontend funzionanti
- [ ] Dipendenze installabili (@mui/x-charts disponibile)
- [ ] Reference image salvata per design
- [ ] Piano approvato dal team

---

**Fine Piano - Pronto per Implementazione**

---

## 📊 TASK BREAKDOWN DETTAGLIATO

### **BACKEND TASKS**

#### **Task 1.1: Rinominare e Aggiornare Workflow Handler**
**File**: `core/infrastructure/workflows/handlers/onboarding_content_handler.py`
- [ ] Rinominare decorator: `@register_workflow("onboarding_analytics_generator")`
- [ ] Aggiornare docstring con nuovo scopo
- [ ] Modificare metodo `execute()` per generare analytics report
- [ ] Creare nuovo prompt template per analytics
- [ ] Output JSON strutturato invece di markdown semplice
**Stima**: 2-3 ore

#### **Task 1.2: Creare Nuovo Prompt Template**
**File**: `core/infrastructure/workflows/handlers/onboarding_content_handler.py`
- [ ] Prompt per Company Score (0-100)
- [ ] Prompt per Content Opportunities (lista strutturata)
- [ ] Prompt per Optimization Insights (4 aree)
- [ ] Prompt per Competitor Intelligence
- [ ] Prompt per Quick Wins (actionable items)
- [ ] Prompt per Full Report (markdown)
**Stima**: 2-3 ore

#### **Task 1.3: Aggiornare Domain Models**
**File**: `onboarding/domain/models.py`
- [ ] Modificare `OnboardingGoal` enum (solo `COMPANY_ANALYTICS`)
- [ ] Creare `AnalyticsReport` model (Pydantic)
- [ ] Creare sub-models: `ContentOpportunity`, `OptimizationInsight`, `QuickWin`
**Stima**: 1-2 ore

#### **Task 1.4: Semplificare Payload Builder**
**File**: `onboarding/application/builders/payload_builder.py`
- [ ] Rimuovere logica content-type specifica
- [ ] Nuovo metodo `_build_analytics_payload()`
- [ ] Mappare user answers → variables (generic)
- [ ] Aggiornare `CgsPayloadOnboardingContent` → `CgsPayloadAnalytics`
**Stima**: 2-3 ore

#### **Task 1.5: Aggiornare CGS Contracts**
**File**: `onboarding/domain/cgs_contracts.py`
- [ ] Creare `CgsPayloadAnalytics` (nuovo)
- [ ] Creare `AnalyticsInput` (variabili generiche)
- [ ] Deprecare vecchi payload (LinkedInPost, Newsletter)
**Stima**: 1 ora

#### **Task 1.6: Aggiornare Settings**
**File**: `onboarding/config/settings.py`
- [ ] Aggiornare `default_workflow_mappings`:
  ```python
  {
    "company_analytics": "onboarding_analytics_generator"
  }
  ```
**Stima**: 15 minuti

---

### **FRONTEND TASKS**

#### **Task 2.1: Installare Dipendenze**
**File**: `onboarding-frontend/package.json`
- [ ] Installare `@mui/x-charts`
- [ ] Installare `react-markdown` (se non presente)
- [ ] Verificare compatibilità versioni
**Stima**: 30 minuti

#### **Task 2.2: Aggiornare Types**
**File**: `onboarding-frontend/src/types/onboarding.ts`
- [ ] Aggiornare `OnboardingGoal` type
- [ ] Creare `AnalyticsReport` interface
- [ ] Creare sub-interfaces: `ContentOpportunity`, `OptimizationInsight`, etc.
**Stima**: 1 ora

#### **Task 2.3: Semplificare Step1**
**File**: `onboarding-frontend/src/components/steps/Step1CompanyInput.tsx`
- [ ] Rimuovere goal selection dropdown
- [ ] Goal fisso: "company_analytics"
- [ ] Form semplificato: Brand Name, Website, Email
**Stima**: 1 ora

#### **Task 2.4: Aggiornare Step4 Questions**
**File**: `onboarding-frontend/src/components/steps/Step4QuestionsForm.tsx`
- [ ] Domande generiche invece di content-specific
- [ ] Labels: "Variable 1", "Variable 2", etc.
- [ ] Placeholder text descrittivi
**Stima**: 1 ora

#### **Task 2.5: Creare Dashboard Components**
**Directory**: `onboarding-frontend/src/components/dashboard/`

**Sub-tasks**:
- [ ] `CompanyScoreCard.tsx` - Gauge chart (1-2 ore)
- [ ] `ContentOpportunitiesCard.tsx` - Number display (1 ora)
- [ ] `CompetitorCard.tsx` - List with avatars (1-2 ore)
- [ ] `OptimizationInsightsCard.tsx` - 4-section grid (2 ore)
- [ ] `QuickWinsCard.tsx` - Checklist (1-2 ore)
- [ ] `ContentTypesChart.tsx` - Bar/Pie chart (1-2 ore)
- [ ] `MetricsCard.tsx` - Stats grid (1 ora)
- [ ] `FullReportCard.tsx` - Markdown viewer (1-2 ore)

**Stima Totale**: 10-14 ore

#### **Task 2.6: Creare Step6Dashboard**
**File**: `onboarding-frontend/src/components/steps/Step6Dashboard.tsx`
- [ ] Layout grid (3 colonne)
- [ ] Integrare 8 card components
- [ ] Responsive design (mobile/tablet/desktop)
- [ ] Animations (framer-motion)
- [ ] Loading states
**Stima**: 3-4 ore

#### **Task 2.7: Aggiornare Routing**
**File**: `onboarding-frontend/src/pages/OnboardingPage.tsx`
- [ ] Sostituire `Step6Results` con `Step6Dashboard`
- [ ] Passare `analyticsReport` invece di `session.metadata`
**Stima**: 30 minuti

---

### **TESTING TASKS**

#### **Task 3.1: Backend Unit Tests**
- [ ] Test `onboarding_analytics_generator` workflow
- [ ] Test payload building con variabili generiche
- [ ] Test output JSON structure
**Stima**: 2-3 ore

#### **Task 3.2: Frontend Component Tests**
- [ ] Test rendering di ogni card component
- [ ] Test responsive layout
- [ ] Test interactions (expand/collapse, etc.)
**Stima**: 2-3 ore

#### **Task 3.3: End-to-End Test**
- [ ] Test flusso completo: Start → Analytics Dashboard
- [ ] Verificare dati corretti in ogni card
- [ ] Test con diversi input (edge cases)
**Stima**: 2 ore

---

### **DOCUMENTATION TASKS**

#### **Task 4.1: Aggiornare README**
- [ ] Documentare nuovo flusso analytics
- [ ] Screenshot dashboard
- [ ] Esempi di output
**Stima**: 1 ora

#### **Task 4.2: API Documentation**
- [ ] Documentare nuovo payload structure
- [ ] Documentare analytics report format
- [ ] Esempi di request/response
**Stima**: 1 ora

---

## 📈 TIMELINE STIMATA

| Fase | Durata | Dipendenze |
|------|--------|------------|
| **Backend Workflow** | 4-6 ore | Nessuna |
| **Backend Payload** | 2-3 ore | Workflow completato |
| **Frontend Types & Survey** | 3-4 ore | Backend payload definito |
| **Frontend Dashboard** | 13-18 ore | Types definiti |
| **Testing** | 6-8 ore | Tutto implementato |
| **Documentation** | 2 ore | Testing completato |
| **TOTALE** | **30-41 ore** | - |

**Suddivisione per Sprint**:
- **Sprint 1** (8-10 ore): Backend completo
- **Sprint 2** (10-12 ore): Frontend survey + types + 4 card components
- **Sprint 3** (10-12 ore): Rimanenti 4 card components + dashboard layout
- **Sprint 4** (6-8 ore): Testing + documentation + polish

---

## 🎯 PRIORITÀ TASKS

### **P0 - Critici** (Blockers)
1. Task 1.1 - Workflow handler update
2. Task 1.3 - Domain models
3. Task 2.2 - Frontend types
4. Task 2.5 - Dashboard components

### **P1 - Importanti** (Core features)
5. Task 1.2 - Prompt templates
6. Task 1.4 - Payload builder
7. Task 2.6 - Dashboard layout
8. Task 3.3 - E2E testing

### **P2 - Nice to have** (Polish)
9. Task 2.5 (animations)
10. Task 4.1 - Documentation
11. Task 3.2 - Component tests

---

## 🚀 QUICK START GUIDE

### **Per iniziare l'implementazione**:

1. **Crea nuovo branch**:
   ```bash
   git checkout -b analytics-dashboard
   ```

2. **Inizia con Backend** (Task 1.1):
   ```bash
   # Apri file
   code core/infrastructure/workflows/handlers/onboarding_content_handler.py

   # Modifica decorator
   @register_workflow("onboarding_analytics_generator")
   ```

3. **Testa subito**:
   ```bash
   # Avvia backend
   uvicorn api.rest.main:app --reload --port 8000

   # Test workflow
   curl -X POST http://localhost:8000/api/v1/content/generate \
     -H "Content-Type: application/json" \
     -d '{"workflow_type": "onboarding_analytics_generator", ...}'
   ```

4. **Procedi con Frontend** (Task 2.1):
   ```bash
   cd onboarding-frontend
   npm install @mui/x-charts react-markdown
   ```

---

**Piano Completo - Pronto per Implementazione! 🚀**

