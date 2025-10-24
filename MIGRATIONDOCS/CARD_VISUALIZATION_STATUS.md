# 🎨 CARD VISUALIZATION - STATO ATTUALE

> **Data:** 2025-01-22  
> **Obiettivo:** Riepilogo completo del sistema di visualizzazione card metadata-driven

---

## 📊 PANORAMICA ARCHITETTURA

### **Flusso End-to-End**

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FLUSSO COMPLETO                              │
└─────────────────────────────────────────────────────────────────────┘

1. BACKEND (CGS)
   ↓
   Genera contenuto + metadata
   {
     "content": {
       "title": "...",
       "body": "...",
       "metadata": {
         "display_type": "company_snapshot",  ← CHIAVE!
         "company_snapshot": { ... }
       }
     }
   }

2. ONBOARDING API
   ↓
   Salva cgs_response in session
   GET /api/v1/onboarding/{session_id}
   → Ritorna session con cgs_response completo

3. FRONTEND
   ↓
   Step6Results legge display_type
   ↓
   RendererRegistry trova il renderer
   ↓
   Renderer estrae dati e renderizza card
```

---

## ✅ STATO ATTUALE - COSA FUNZIONA

### **1. Backend (CGS + Onboarding API)**

✅ **CGS genera metadata con display_type**
- File: `onboarding/infrastructure/adapters/cgs_adapter.py`
- Estrae `display_type` da `cgs_response.metadata.display_type`
- Salva in `ContentResult.display_type`

✅ **Onboarding API ritorna cgs_response completo**
- Endpoint: `GET /api/v1/onboarding/{session_id}`
- File: `onboarding/api/endpoints.py` (linea 310)
- Ritorna `SessionDetailResponse` con `cgs_response` completo

✅ **Session salva cgs_response**
- File: `onboarding/application/use_cases/execute_onboarding.py` (linea 103)
- `session.cgs_response = result.model_dump(mode="json")`

---

### **2. Frontend - Renderer Registry**

✅ **RendererRegistry implementato**
- File: `onboarding-frontend/src/renderers/RendererRegistry.ts`
- Pattern: `register(displayType, component, dataExtractor)`
- Metodi: `getRenderer()`, `hasRenderer()`, `getRegisteredTypes()`

✅ **3 Renderer registrati**

1. **CompanySnapshotRenderer** (`company_snapshot`)
   - File: `onboarding-frontend/src/renderers/CompanySnapshotRenderer.tsx`
   - Estrae: `session.cgs_response.metadata.company_snapshot`
   - Fallback: `session.snapshot`
   - Renderizza: `CompanySnapshotCard`

2. **AnalyticsRenderer** (`analytics_dashboard`)
   - File: `onboarding-frontend/src/renderers/AnalyticsRenderer.tsx`
   - Estrae: `session.cgs_response.metadata.analytics_data`
   - Renderizza: `Step6Dashboard`

3. **ContentRenderer** (`content_preview`)
   - File: `onboarding-frontend/src/renderers/ContentRenderer.tsx`
   - Estrae: `session.cgs_response.content.body`
   - Renderizza: `ContentPreview`
   - **FALLBACK RENDERER** (default)

---

### **3. Frontend - Step6Results (Orchestratore)**

✅ **Step6Results usa RendererRegistry**
- File: `onboarding-frontend/src/components/steps/Step6Results.tsx`
- Legge: `session.cgs_response.content.metadata.display_type`
- Trova renderer: `rendererRegistry.getRenderer(displayType)`
- Estrae dati: `renderer.dataExtractor(session)`
- Renderizza: `<RendererComponent data={data} />`

✅ **Fallback a content_preview**
- Se `display_type` non trovato → usa `content_preview`
- Se nessun renderer → mostra errore

---

### **4. Frontend - CompanySnapshotCard**

✅ **Card UI implementata**
- File: `onboarding-frontend/src/components/cards/CompanySnapshotCard.tsx`
- Sezioni:
  - Header (nome, industry, website)
  - Overview (description)
  - Value Proposition
  - Audience (primary, pain points)
  - Positioning
  - Competitors
  - Tone & Style
  - AI Summary (Fylle Insight)
  - CTAs (Generate AI Brief, Compare Competitors)

✅ **Mapping CompanySnapshot → CompanySnapshotCardData**
- File: `onboarding-frontend/src/renderers/CompanySnapshotRenderer.tsx` (linea 80)
- Funzione: `companySnapshotToCard(snapshot)`
- Normalizza struttura backend → formato UI

---

## 🔧 COMPONENTI CHIAVE

### **Backend**

#### **1. CGS Adapter**
<augment_code_snippet path="onboarding/infrastructure/adapters/cgs_adapter.py" mode="EXCERPT">
````python
# Estrae display_type da metadata
display_type = metadata.get("display_type", "content_preview")

content = ContentResult(
    content_id=cgs_response.get("content_id"),
    title=cgs_response.get("title", ""),
    body=cgs_response.get("body", ""),
    display_type=display_type,  # ← CHIAVE!
    metadata=metadata,
)
````
</augment_code_snippet>

#### **2. Onboarding API Endpoint**
<augment_code_snippet path="onboarding/api/endpoints.py" mode="EXCERPT">
````python
return SessionDetailResponse(
    session_id=session.session_id,
    trace_id=session.trace_id,
    brand_name=session.brand_name,
    # ...
    cgs_response=session.cgs_response,  # ✨ Include full CGS response
    # ...
)
````
</augment_code_snippet>

---

### **Frontend**

#### **1. RendererRegistry**
<augment_code_snippet path="onboarding-frontend/src/renderers/RendererRegistry.ts" mode="EXCERPT">
````typescript
class RendererRegistry {
  private renderers: Map<string, RendererConfig> = new Map();

  register(
    displayType: string,
    component: React.ComponentType<any>,
    dataExtractor: (session: OnboardingSession) => any
  ): void {
    this.renderers.set(displayType, { component, dataExtractor });
  }

  getRenderer(displayType: string): RendererConfig | undefined {
    return this.renderers.get(displayType);
  }
}
````
</augment_code_snippet>

#### **2. Step6Results (Orchestratore)**
<augment_code_snippet path="onboarding-frontend/src/components/steps/Step6Results.tsx" mode="EXCERPT">
````typescript
export const Step6Results: React.FC<Step6ResultsProps> = ({ session, onStartNew }) => {
  // Legge display_type da metadata
  const displayType = session.cgs_response?.content?.metadata?.display_type || 'content_preview';

  // Trova renderer
  const renderer = rendererRegistry.getRenderer(displayType);

  // Estrae dati e renderizza
  const data = renderer.dataExtractor(session);
  const RendererComponent = renderer.component;

  return <RendererComponent session={session} data={data} onStartNew={onStartNew} />;
};
````
</augment_code_snippet>

#### **3. CompanySnapshotRenderer**
<augment_code_snippet path="onboarding-frontend/src/renderers/CompanySnapshotRenderer.tsx" mode="EXCERPT">
````typescript
const extractCompanySnapshot = (session: OnboardingSession): CompanySnapshotCardData | null => {
  // 1. Try CGS response metadata
  const metadata = session.cgs_response?.metadata;
  let snapshot: CompanySnapshot | undefined = metadata?.company_snapshot;

  // 2. Fallback to session.snapshot
  if (!snapshot) {
    snapshot = session.snapshot;
  }

  if (!snapshot) return null;

  // 3. Map to card data
  return companySnapshotToCard(snapshot);
};

// Register
rendererRegistry.register(
  'company_snapshot',
  CompanySnapshotCardRenderer,
  extractCompanySnapshot
);
````
</augment_code_snippet>

---

## 📁 FILE RILEVANTI

### **Backend**

| File | Responsabilità | Priorità |
|------|----------------|----------|
| `onboarding/infrastructure/adapters/cgs_adapter.py` | Estrae `display_type` da CGS response | P0 |
| `onboarding/api/endpoints.py` | Ritorna `cgs_response` completo | P0 |
| `onboarding/application/use_cases/execute_onboarding.py` | Salva `cgs_response` in session | P0 |
| `onboarding/domain/cgs_contracts.py` | Definisce `ContentResult` con `display_type` | P0 |

### **Frontend**

| File | Responsabilità | Priorità |
|------|----------------|----------|
| `onboarding-frontend/src/renderers/RendererRegistry.ts` | Registry pattern per renderer | P0 |
| `onboarding-frontend/src/components/steps/Step6Results.tsx` | Orchestratore rendering | P0 |
| `onboarding-frontend/src/renderers/CompanySnapshotRenderer.tsx` | Renderer company snapshot | P0 |
| `onboarding-frontend/src/components/cards/CompanySnapshotCard.tsx` | UI card company snapshot | P0 |
| `onboarding-frontend/src/renderers/AnalyticsRenderer.tsx` | Renderer analytics dashboard | P1 |
| `onboarding-frontend/src/renderers/ContentRenderer.tsx` | Renderer content preview (fallback) | P1 |
| `onboarding-frontend/src/types/onboarding.ts` | Type definitions | P0 |

---

## 🎯 COME FUNZIONA - ESEMPIO PRATICO

### **Scenario: Visualizzare Company Snapshot**

#### **1. Backend genera contenuto**

CGS workflow `company_snapshot_generator` ritorna:

```json
{
  "content": {
    "title": "ACME Corp - Company Snapshot",
    "body": "...",
    "metadata": {
      "display_type": "company_snapshot",
      "company_snapshot": {
        "company": {
          "name": "ACME Corp",
          "industry": "B2B SaaS",
          "description": "AI automation platform"
        },
        "audience": {
          "primary": "CTOs and Engineering Leaders"
        },
        "voice": {
          "tone": "Authoritative but approachable"
        }
      }
    }
  }
}
```

#### **2. Onboarding API salva e ritorna**

```python
# execute_onboarding.py
session.cgs_response = result.model_dump(mode="json")
await repository.save_session(session)

# endpoints.py
return SessionDetailResponse(
    session_id=session.session_id,
    cgs_response=session.cgs_response,  # ← Contiene tutto!
)
```

#### **3. Frontend renderizza**

```typescript
// Step6Results.tsx
const displayType = session.cgs_response.content.metadata.display_type;
// → "company_snapshot"

const renderer = rendererRegistry.getRenderer("company_snapshot");
// → CompanySnapshotRenderer

const data = renderer.dataExtractor(session);
// → Estrae company_snapshot da metadata

const RendererComponent = renderer.component;
// → CompanySnapshotCardRenderer

return <RendererComponent data={data} />;
// → Renderizza CompanySnapshotCard
```

---

## ✅ COSA È STATO RISOLTO

### **Problema Iniziale**
❌ CompanySnapshotCard non veniva visualizzata

### **Causa**
- Frontend chiamava endpoint sbagliato (status invece di details)
- `cgs_response` non era disponibile

### **Soluzione**
✅ Frontend ora chiama `GET /api/v1/onboarding/{session_id}` (details)
✅ Endpoint ritorna `cgs_response` completo
✅ `CompanySnapshotRenderer` estrae dati correttamente
✅ Card viene renderizzata

---

## 🚀 COME AGGIUNGERE NUOVE CARD

### **Step 1: Backend - Genera metadata con display_type**

Nel workflow CGS, assicurati che il metadata contenga:

```python
metadata = {
    "display_type": "linkedin_post",  # ← Nome univoco
    "linkedin_post": {  # ← Dati specifici
        "text": "...",
        "hashtags": ["#AI", "#SaaS"],
        "cta": "Learn more"
    }
}
```

### **Step 2: Frontend - Crea Card Component**

```typescript
// src/components/cards/LinkedInPostCard.tsx
export interface LinkedInPostCardData {
  text: string;
  hashtags: string[];
  cta: string;
}

export const LinkedInPostCard: React.FC<{ data: LinkedInPostCardData }> = ({ data }) => {
  return (
    <div className="card">
      <p>{data.text}</p>
      <div>{data.hashtags.join(' ')}</div>
      <button>{data.cta}</button>
    </div>
  );
};
```

### **Step 3: Frontend - Crea Renderer**

```typescript
// src/renderers/LinkedInPostRenderer.tsx
import { rendererRegistry } from './RendererRegistry';
import { LinkedInPostCard } from '@/components/cards/LinkedInPostCard';

const extractLinkedInPost = (session: OnboardingSession): LinkedInPostCardData | null => {
  const metadata = session.cgs_response?.content?.metadata;
  const post = metadata?.linkedin_post;

  if (!post) return null;

  return {
    text: post.text,
    hashtags: post.hashtags || [],
    cta: post.cta || "Learn more"
  };
};

const LinkedInPostRenderer: React.FC<{ data: LinkedInPostCardData | null }> = ({ data }) => {
  if (!data) return <div>No LinkedIn post available</div>;
  return <LinkedInPostCard data={data} />;
};

// Register
rendererRegistry.register(
  'linkedin_post',
  LinkedInPostRenderer,
  extractLinkedInPost
);
```

### **Step 4: Frontend - Import in Step6Results**

```typescript
// src/components/steps/Step6Results.tsx
import '@/renderers/LinkedInPostRenderer';  // ← Auto-registra
```

**FATTO!** Ora quando CGS ritorna `display_type: "linkedin_post"`, la card viene renderizzata automaticamente.

---

## 📊 RENDERER REGISTRATI

| Display Type | Renderer | Card Component | Status |
|--------------|----------|----------------|--------|
| `company_snapshot` | CompanySnapshotRenderer | CompanySnapshotCard | ✅ Funzionante |
| `analytics_dashboard` | AnalyticsRenderer | Step6Dashboard | ✅ Funzionante |
| `content_preview` | ContentRenderer | ContentPreview | ✅ Funzionante (fallback) |
| `linkedin_post` | - | - | ❌ Da implementare |
| `newsletter` | - | - | ❌ Da implementare |
| `blog_article` | - | - | ❌ Da implementare |

---

## 🎯 PROSSIMI PASSI

### **P0 - Completare Card Esistenti**
- [ ] Testare CompanySnapshotCard con dati reali
- [ ] Verificare fallback a `content_preview`
- [ ] Testare analytics_dashboard

### **P1 - Nuove Card**
- [ ] LinkedInPostCard (display_type: `linkedin_post`)
- [ ] NewsletterCard (display_type: `newsletter`)
- [ ] BlogArticleCard (display_type: `blog_article`)

### **P2 - Miglioramenti**
- [ ] Animazioni transizione tra card
- [ ] Loading states per card
- [ ] Error boundaries per renderer
- [ ] Preview card in admin panel

---

## 🐛 TROUBLESHOOTING

### **Card non viene visualizzata**

1. **Verifica display_type nel backend**
   ```python
   print(session.cgs_response.get("content", {}).get("metadata", {}).get("display_type"))
   ```

2. **Verifica renderer registrato**
   ```typescript
   console.log(rendererRegistry.getRegisteredTypes());
   ```

3. **Verifica dati estratti**
   ```typescript
   const data = renderer.dataExtractor(session);
   console.log('Extracted data:', data);
   ```

### **Fallback a content_preview**

Se vedi sempre `content_preview`:
- Backend non sta settando `display_type` correttamente
- Frontend non sta leggendo `session.cgs_response.content.metadata.display_type`

### **Renderer non trovato**

Se vedi "No renderer found":
- Renderer non è stato importato in `Step6Results.tsx`
- `display_type` non corrisponde al nome registrato

---

**Fine del documento**
