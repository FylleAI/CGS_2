# 🎨 FRONTEND ELASTICO - Struttura e Responsabilità

## 📂 File Structure (Solo Tua Area)

```
onboarding-frontend/
└── src/
    ├── components/
    │   ├── steps/                          # 🔥 CORE - Wizard steps
    │   │   ├── Step1Input.tsx              # Input brand/website
    │   │   ├── Step2SnapshotReview.tsx     # Review snapshot
    │   │   ├── Step3Questions.tsx          # Answer questions
    │   │   ├── Step4Execution.tsx          # Loading/progress
    │   │   └── Step6Results.tsx            # 🔥 CRITICO - Display results
    │   │
    │   ├── cards/                          # 🔥 CORE - Content cards
    │   │   ├── CompanySnapshotCard.tsx     # Card per Company Snapshot
    │   │   ├── AnalyticsDashboardCard.tsx  # Card per Analytics
    │   │   ├── LinkedInPostCard.tsx        # Card per LinkedIn Post
    │   │   ├── BlogArticleCard.tsx         # Card per Blog Article
    │   │   └── GenericContentCard.tsx      # Card generico (fallback)
    │   │
    │   └── wizard/
    │       └── OnboardingWizard.tsx        # Wizard container
    │
    ├── renderers/                          # 🔥 CORE - Renderer Registry Pattern
    │   ├── RendererRegistry.ts             # Registry pattern (metadata-driven)
    │   ├── CompanySnapshotRenderer.tsx     # Renderer per snapshot
    │   ├── AnalyticsRenderer.tsx           # Renderer per analytics
    │   ├── LinkedInPostRenderer.tsx        # Renderer per LinkedIn
    │   ├── BlogArticleRenderer.tsx         # Renderer per Blog
    │   └── GenericContentRenderer.tsx      # Renderer generico (fallback)
    │
    ├── hooks/
    │   └── useOnboarding.ts                # 🔥 CORE - Onboarding hook
    │
    ├── store/
    │   └── onboardingStore.ts              # Zustand state management
    │
    ├── services/
    │   └── api/
    │       ├── client.ts                   # HTTP client (axios/fetch)
    │       └── onboardingApi.ts            # Onboarding API client
    │
    └── types/
        └── onboarding.ts                   # TypeScript types
```

---

## 🎯 RESPONSABILITÀ CHIAVE

### **Frontend è METADATA-DRIVEN:**

```
BACKEND (CGS)                          FRONTEND (React)
─────────────────                      ────────────────

Genera content + metadata             Riceve response
         ↓                                    ↓
{                                      Estrae display_type
  "content": {                                ↓
    "metadata": {                      RendererRegistry.get(display_type)
      "display_type": "company_snapshot"     ↓
    }                                  Renderer.render(data)
  }                                           ↓
}                                      Mostra Card appropriata
```

**Principio chiave:** Il backend decide **COSA** mostrare (display_type), il frontend decide **COME** mostrarlo (rendering).

---

## 🔑 RENDERER REGISTRY PATTERN (🔥 CRITICO)

### **Concetto:**

Il Renderer Registry è un **pattern di design** che:
1. Mappa `display_type` → Renderer component
2. Permette rendering dinamico basato su metadata
3. Facile aggiungere nuovi renderer (senza modificare Step6Results)

### **Implementazione:**

```typescript
// src/renderers/RendererRegistry.ts

import { CompanySnapshotRenderer } from './CompanySnapshotRenderer';
import { AnalyticsRenderer } from './AnalyticsRenderer';
import { LinkedInPostRenderer } from './LinkedInPostRenderer';
import { BlogArticleRenderer } from './BlogArticleRenderer';
import { GenericContentRenderer } from './GenericContentRenderer';

export interface Renderer {
  /**
   * Render content basato su CGS response.
   */
  render(data: any): JSX.Element;
}

class RendererRegistryClass {
  private renderers = new Map<string, Renderer>();
  
  constructor() {
    // Registra renderer per ogni display_type
    this.register('company_snapshot', new CompanySnapshotRenderer());
    this.register('analytics_dashboard', new AnalyticsRenderer());
    this.register('linkedin_post', new LinkedInPostRenderer());
    this.register('blog_article', new BlogArticleRenderer());
    this.register('content', new GenericContentRenderer());  // Fallback
  }
  
  /**
   * Registra un nuovo renderer.
   */
  register(displayType: string, renderer: Renderer): void {
    this.renderers.set(displayType, renderer);
  }
  
  /**
   * Ottiene renderer per display_type.
   * 
   * Se non trovato, ritorna GenericContentRenderer (fallback).
   */
  get(displayType: string): Renderer {
    return this.renderers.get(displayType) || this.renderers.get('content')!;
  }
  
  /**
   * Render content usando renderer appropriato.
   */
  render(displayType: string, data: any): JSX.Element {
    const renderer = this.get(displayType);
    return renderer.render(data);
  }
}

// Singleton instance
export const RendererRegistry = new RendererRegistryClass();
```

---

## 🎨 RENDERER IMPLEMENTATIONS

### **1. CompanySnapshotRenderer**

```typescript
// src/renderers/CompanySnapshotRenderer.tsx

import { Renderer } from './RendererRegistry';
import { CompanySnapshotCard } from '../components/cards/CompanySnapshotCard';

export class CompanySnapshotRenderer implements Renderer {
  render(data: any): JSX.Element {
    // Estrae company_snapshot da metadata
    const snapshot = data?.content?.metadata?.company_snapshot;
    
    if (!snapshot) {
      console.error('CompanySnapshotRenderer: missing company_snapshot in metadata');
      return <div>Error: Missing company snapshot data</div>;
    }
    
    return <CompanySnapshotCard snapshot={snapshot} />;
  }
}
```

### **2. AnalyticsRenderer**

```typescript
// src/renderers/AnalyticsRenderer.tsx

import { Renderer } from './RendererRegistry';
import { AnalyticsDashboardCard } from '../components/cards/AnalyticsDashboardCard';

export class AnalyticsRenderer implements Renderer {
  render(data: any): JSX.Element {
    // Estrae analytics_data da metadata
    const analytics = data?.content?.metadata?.analytics_data;
    
    if (!analytics) {
      console.error('AnalyticsRenderer: missing analytics_data in metadata');
      return <div>Error: Missing analytics data</div>;
    }
    
    return <AnalyticsDashboardCard analytics={analytics} />;
  }
}
```

### **3. LinkedInPostRenderer**

```typescript
// src/renderers/LinkedInPostRenderer.tsx

import { Renderer } from './RendererRegistry';
import { LinkedInPostCard } from '../components/cards/LinkedInPostCard';

export class LinkedInPostRenderer implements Renderer {
  render(data: any): JSX.Element {
    // Estrae post content da body
    const post = {
      content: data?.content?.body,
      hashtags: data?.content?.metadata?.hashtags || [],
      cta: data?.content?.metadata?.cta
    };
    
    return <LinkedInPostCard post={post} />;
  }
}
```

### **4. GenericContentRenderer (Fallback)**

```typescript
// src/renderers/GenericContentRenderer.tsx

import { Renderer } from './RendererRegistry';
import { GenericContentCard } from '../components/cards/GenericContentCard';

export class GenericContentRenderer implements Renderer {
  render(data: any): JSX.Element {
    // Fallback: mostra title + body
    const content = {
      title: data?.content?.title || 'Content Generated',
      body: data?.content?.body || '',
      wordCount: data?.content?.word_count || 0
    };
    
    return <GenericContentCard content={content} />;
  }
}
```

---

## 📄 STEP6RESULTS (🔥 CRITICO)

```typescript
// src/components/steps/Step6Results.tsx

import { RendererRegistry } from '../../renderers/RendererRegistry';

interface Step6ResultsProps {
  session: OnboardingSession;
}

export function Step6Results({ session }: Step6ResultsProps) {
  // 1. Estrae display_type da metadata
  const displayType = session.cgs_response?.content?.metadata?.display_type || 'content';
  
  console.log(`🎨 Rendering with display_type: ${displayType}`);
  console.log(`📦 CGS Response:`, session.cgs_response);
  console.log(`📦 Content metadata:`, session.cgs_response?.content?.metadata);
  
  // 2. Usa RendererRegistry per rendering dinamico
  return (
    <div className="step6-results">
      <h2>Your Content is Ready! 🎉</h2>
      
      {/* 3. Rendering metadata-driven */}
      {RendererRegistry.render(displayType, session.cgs_response)}
      
      {/* 4. Actions */}
      <div className="actions">
        <button onClick={() => downloadContent(session)}>
          Download
        </button>
        <button onClick={() => shareContent(session)}>
          Share
        </button>
      </div>
    </div>
  );
}
```

**Vantaggi:**
- ✅ **Elastico:** Aggiungere nuovo renderer = 2 file (Renderer + Card)
- ✅ **Metadata-driven:** Backend controlla rendering
- ✅ **Fallback:** Se display_type sconosciuto, usa GenericContentRenderer
- ✅ **Testabile:** Ogni renderer è isolato

---

## 🃏 CONTENT CARDS

### **CompanySnapshotCard**

```typescript
// src/components/cards/CompanySnapshotCard.tsx

interface CompanySnapshotCardProps {
  snapshot: CompanySnapshot;
}

export function CompanySnapshotCard({ snapshot }: CompanySnapshotCardProps) {
  return (
    <div className="company-snapshot-card">
      {/* Company Info */}
      <section className="company-info">
        <h3>{snapshot.company.name}</h3>
        <p>{snapshot.company.description}</p>
        <a href={snapshot.company.website} target="_blank">
          {snapshot.company.website}
        </a>
      </section>
      
      {/* Voice & Tone */}
      <section className="voice-tone">
        <h4>Voice & Tone</h4>
        <div className="tags">
          <span>{snapshot.voice_tone.tone}</span>
          <span>{snapshot.voice_tone.style}</span>
          <span>{snapshot.voice_tone.language_complexity}</span>
        </div>
      </section>
      
      {/* Target Audience */}
      <section className="audience">
        <h4>Target Audience</h4>
        <p>{snapshot.target_audience.demographics}</p>
        <ul>
          {snapshot.target_audience.pain_points.map((point, i) => (
            <li key={i}>{point}</li>
          ))}
        </ul>
      </section>
      
      {/* Positioning */}
      <section className="positioning">
        <h4>Positioning</h4>
        <p>{snapshot.positioning.unique_value_proposition}</p>
        <ul>
          {snapshot.positioning.differentiators.map((diff, i) => (
            <li key={i}>{diff}</li>
          ))}
        </ul>
      </section>
      
      {/* Recent News */}
      {snapshot.recent_news && snapshot.recent_news.length > 0 && (
        <section className="recent-news">
          <h4>Recent News</h4>
          <ul>
            {snapshot.recent_news.map((news, i) => (
              <li key={i}>{news}</li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
```

### **AnalyticsDashboardCard**

```typescript
// src/components/cards/AnalyticsDashboardCard.tsx

interface AnalyticsDashboardCardProps {
  analytics: AnalyticsData;
}

export function AnalyticsDashboardCard({ analytics }: AnalyticsDashboardCardProps) {
  return (
    <div className="analytics-dashboard-card">
      {/* KPIs */}
      <section className="kpis">
        <div className="kpi">
          <h4>Total Reach</h4>
          <p>{analytics.total_reach.toLocaleString()}</p>
        </div>
        <div className="kpi">
          <h4>Engagement Rate</h4>
          <p>{analytics.engagement_rate}%</p>
        </div>
        <div className="kpi">
          <h4>Conversion Rate</h4>
          <p>{analytics.conversion_rate}%</p>
        </div>
      </section>
      
      {/* Charts */}
      <section className="charts">
        <div className="chart">
          <h4>Performance Over Time</h4>
          {/* Chart component */}
        </div>
      </section>
      
      {/* Insights */}
      <section className="insights">
        <h4>Key Insights</h4>
        <ul>
          {analytics.insights.map((insight, i) => (
            <li key={i}>{insight}</li>
          ))}
        </ul>
      </section>
    </div>
  );
}
```

---

## 🔌 API CLIENT

```typescript
// src/services/api/onboardingApi.ts

import { apiClient } from './client';

export const onboardingApi = {
  /**
   * Step 1: Avvia onboarding.
   */
  async startOnboarding(data: {
    brand_name: string;
    website: string;
    goal: string;
    email: string;
  }) {
    const response = await apiClient.post('/api/v1/onboarding/start', data);
    return response.data;
  },
  
  /**
   * Step 2: Submit answers ed esegui workflow CGS.
   */
  async submitAnswers(sessionId: string, answers: Record<string, any>) {
    const response = await apiClient.post(
      `/api/v1/onboarding/${sessionId}/answers`,
      { answers }
    );
    return response.data;
  },
  
  /**
   * Get session details (include cgs_response).
   */
  async getSessionDetails(sessionId: string) {
    const response = await apiClient.get(`/api/v1/onboarding/${sessionId}`);
    return response.data;
  }
};
```

---

## 🪝 ONBOARDING HOOK

```typescript
// src/hooks/useOnboarding.ts

import { useState } from 'react';
import { onboardingApi } from '../services/api/onboardingApi';

export function useOnboarding() {
  const [session, setSession] = useState<OnboardingSession | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const startOnboarding = async (data: StartOnboardingData) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await onboardingApi.startOnboarding(data);
      
      setSession({
        session_id: result.session_id,
        company_snapshot: result.company_snapshot,
        state: 'SNAPSHOT_READY'
      });
      
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };
  
  const submitAnswers = async (answers: Record<string, any>) => {
    if (!session) throw new Error('No active session');
    
    setLoading(true);
    setError(null);
    
    try {
      // 1. Submit answers
      const result = await onboardingApi.submitAnswers(session.session_id, answers);
      
      // 2. Fetch full session details (include cgs_response)
      const sessionDetails = await onboardingApi.getSessionDetails(result.session_id);
      
      // 3. Update session state
      setSession({
        ...session,
        state: sessionDetails.state,
        cgs_response: sessionDetails.cgs_response,  // ← CHIAVE!
        updated_at: sessionDetails.updated_at
      });
      
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };
  
  return {
    session,
    loading,
    error,
    startOnboarding,
    submitAnswers
  };
}
```

---

## 🎯 COME AGGIUNGERE NUOVO RENDERER

### **Scenario:** Vuoi aggiungere rendering per "Email Campaign"

**Step 1: Crea Card Component**

```typescript
// src/components/cards/EmailCampaignCard.tsx

export function EmailCampaignCard({ campaign }: EmailCampaignCardProps) {
  return (
    <div className="email-campaign-card">
      <h3>{campaign.subject}</h3>
      <div dangerouslySetInnerHTML={{ __html: campaign.html_body }} />
      <div className="preview-text">{campaign.preview_text}</div>
    </div>
  );
}
```

**Step 2: Crea Renderer**

```typescript
// src/renderers/EmailCampaignRenderer.tsx

import { Renderer } from './RendererRegistry';
import { EmailCampaignCard } from '../components/cards/EmailCampaignCard';

export class EmailCampaignRenderer implements Renderer {
  render(data: any): JSX.Element {
    const campaign = data?.content?.metadata?.email_campaign;
    
    if (!campaign) {
      return <div>Error: Missing email campaign data</div>;
    }
    
    return <EmailCampaignCard campaign={campaign} />;
  }
}
```

**Step 3: Registra Renderer**

```typescript
// src/renderers/RendererRegistry.ts

import { EmailCampaignRenderer } from './EmailCampaignRenderer';

constructor() {
  // ... existing renderers
  this.register('email_campaign', new EmailCampaignRenderer());  // ← ADD THIS
}
```

**FATTO!** ✅

Ora quando CGS ritorna `display_type: "email_campaign"`, il frontend renderà automaticamente `EmailCampaignCard`.

---

## 🔄 SECONDO FRONTEND (Elastic Rendering)

### **Scenario:** Vuoi un secondo frontend per visualizzare contenuti già generati

```
content-viewer-frontend/
└── src/
    ├── components/
    │   └── ContentViewer.tsx           # Viewer component
    │
    ├── renderers/                      # 🔥 RIUSA STESSO REGISTRY!
    │   └── RendererRegistry.ts         # Importato da onboarding-frontend
    │
    └── services/
        └── api/
            └── contentApi.ts           # API per fetch content
```

**ContentViewer Component:**

```typescript
// content-viewer-frontend/src/components/ContentViewer.tsx

import { RendererRegistry } from 'onboarding-frontend/src/renderers/RendererRegistry';

interface ContentViewerProps {
  contentId: string;
}

export function ContentViewer({ contentId }: ContentViewerProps) {
  const [content, setContent] = useState(null);
  
  useEffect(() => {
    // Fetch content da API
    contentApi.getContent(contentId).then(setContent);
  }, [contentId]);
  
  if (!content) return <div>Loading...</div>;
  
  // Estrae display_type
  const displayType = content.metadata?.display_type || 'content';
  
  // Rendering usando STESSO RendererRegistry!
  return (
    <div className="content-viewer">
      {RendererRegistry.render(displayType, content)}
    </div>
  );
}
```

**Vantaggi:**
- ✅ **Riusa renderer:** Stesso RendererRegistry per tutti i frontend
- ✅ **Elastico:** Qualsiasi content type viene renderizzato correttamente
- ✅ **Consistente:** Stesso look & feel in tutti i frontend

---

## ✅ CHECKLIST: Frontend Elastico

- [ ] **Renderer Registry implementato** (pattern di design)
- [ ] **Renderer per ogni display_type** (company_snapshot, analytics, etc.)
- [ ] **Fallback renderer** (GenericContentRenderer)
- [ ] **Step6Results usa RendererRegistry** (metadata-driven)
- [ ] **Cards riutilizzabili** (possono essere usati in altri frontend)
- [ ] **API client gestisce cgs_response** (fetch completo)
- [ ] **Hook useOnboarding aggiornato** (fetch session details dopo submit)

---

## 🎯 COME RAGIONARE

### **Quando backend aggiunge nuovo content type:**

1. Backend genera `display_type: "new_type"` in metadata
2. Frontend crea `NewTypeCard.tsx`
3. Frontend crea `NewTypeRenderer.tsx`
4. Frontend registra renderer in `RendererRegistry`
5. **FATTO!** Nessuna modifica a `Step6Results.tsx`

### **Quando vuoi secondo frontend:**

1. Crea nuovo progetto React
2. **Riusa** `RendererRegistry` da onboarding-frontend
3. **Riusa** Cards da onboarding-frontend
4. Crea solo `ContentViewer.tsx` (fetch + render)
5. **FATTO!** Rendering elastico funziona ovunque

---

**Ora hai una visione completa! Vuoi che creiamo un diagramma di flusso completo?** 🚀

