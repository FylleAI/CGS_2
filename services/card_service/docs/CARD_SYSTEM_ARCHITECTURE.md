# 🎴 Card System Architecture - Complete Reference

> **Obiettivo**: Documentazione completa del sistema di card UI per modifiche puntuali e sicure

---

## 📋 Table of Contents

1. [Architettura Overview](#architettura-overview)
2. [File Structure](#file-structure)
3. [Data Flow](#data-flow)
4. [Base Components](#base-components)
5. [Specialized Cards](#specialized-cards)
6. [Styling System](#styling-system)
7. [Modifica Sicura](#modifica-sicura)
8. [Common Patterns](#common-patterns)

---

## 🏗️ Architettura Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        RENDERING PIPELINE                        │
└─────────────────────────────────────────────────────────────────┘

Backend (CGS)
    ↓
    └─→ Response con metadata.display_type = "company_snapshot"
         ↓
Frontend (RendererRegistry)
    ↓
    └─→ Seleziona CompanySnapshotRenderer
         ↓
CompanySnapshotRenderer
    ↓
    ├─→ extractCompanySnapshot(session) → CompanySnapshot
    └─→ CompanySnapshotCardRenderer
         ↓
OnboardingResultsGrid
    ↓
    ├─→ CompanySnapshotCardV2 (Card 1)
    ├─→ AudienceIntelligenceCard (Card 2)
    ├─→ VoiceDNACard (Card 3)
    └─→ StrategicInsightsCard (Card 4)
         ↓
FylleCard (Base Component)
    ↓
    ├─→ CardHeader (icon, title, confidence)
    ├─→ CardContent (main content)
    └─→ CardFooter (CTA, metadata)
```

---

## 📁 File Structure

### **1. Entry Point & Orchestration**

```
onboarding-frontend/src/renderers/
├── CompanySnapshotRenderer.tsx    # Entry point, data extraction
├── ContentRenderer.tsx             # Fallback renderer
└── RendererRegistry.ts             # Registry pattern
```

### **2. Layout & Grid**

```
onboarding-frontend/src/components/cards/
└── OnboardingResultsGrid.tsx      # 2x2 grid layout + header/footer
```

### **3. Base Components (Reusable)**

```
onboarding-frontend/src/components/cards/
└── FylleCard.tsx                  # Base components library
    ├── FylleCard                  # Wrapper con animazioni
    ├── CardHeader                 # Header con icon + confidence
    ├── CardContent                # Content area
    ├── CardFooter                 # Footer con CTA
    ├── Chip                       # Tag/badge component
    ├── ConfidenceBadge            # Confidence indicator
    └── Section                    # Section con title + icon
```

### **4. Specialized Cards (Domain-Specific)**

```
onboarding-frontend/src/components/cards/
├── CompanySnapshotCardV2.tsx      # Company info card
├── AudienceIntelligenceCard.tsx   # Audience insights card
├── VoiceDNACard.tsx               # Brand voice card
└── StrategicInsightsCard.tsx      # News + messages card
```

### **5. Exports**

```
onboarding-frontend/src/components/cards/
└── index.ts                       # Centralized exports
```

---

## 🔄 Data Flow

### **Step 1: Backend Response**

```json
{
  "metadata": {
    "display_type": "company_snapshot"
  },
  "content": {
    "metadata": {
      "company_snapshot": { /* CompanySnapshot object */ }
    }
  }
}
```

### **Step 2: Data Extraction (CompanySnapshotRenderer.tsx)**

```typescript
const extractCompanySnapshot = (session: OnboardingSession): CompanySnapshot | null => {
  // 1. Try content.metadata.company_snapshot (primary)
  let snapshot = session.cgs_response?.content?.metadata?.company_snapshot;
  
  // 2. Fallback to root metadata
  if (!snapshot) {
    snapshot = session.cgs_response?.metadata?.company_snapshot;
  }
  
  // 3. Fallback to session.snapshot
  if (!snapshot) {
    snapshot = session.snapshot;
  }
  
  return snapshot || null;
};
```

### **Step 3: CompanySnapshot Structure**

```typescript
interface CompanySnapshot {
  version: string;
  snapshot_id: string;
  generated_at: string;
  trace_id?: string;
  
  company: {
    name: string;
    website?: string;
    industry?: string;
    description: string;
    key_offerings?: string[];
    differentiators?: string[];
    evidence?: Array<{
      source: string;
      excerpt: string;
      confidence: number;
    }>;
  };
  
  audience: {
    primary: string;
    secondary?: string[];
    pain_points?: string[];
    desired_outcomes?: string[];
  };
  
  voice: {
    tone: string;
    style_guidelines?: string[];
    cta_preferences?: string[];
    forbidden_phrases?: string[];
  };
  
  insights: {
    positioning?: string;
    recent_news?: string[];
    key_messages?: string[];
    competitors?: string[];
  };
  
  clarifying_questions: ClarifyingQuestion[];
  clarifying_answers?: Record<string, any>;
}
```

---

## 🧱 Base Components

### **FylleCard** (Wrapper)

**File**: `FylleCard.tsx` (lines 20-44)

**Props**:
```typescript
{
  category: 'company' | 'audience' | 'voice' | 'insight';
  children: React.ReactNode;
  className?: string;
  onMouseEnter?: () => void;
  onMouseLeave?: () => void;
}
```

**Styling**:
- Category-based gradient backgrounds
- Hover effects (shadow, border)
- Framer Motion animations (fade + scale)
- Rounded corners (rounded-2xl)

**Modifica Sicura**:
- ✅ Cambia `categoryColors` per nuovi colori
- ✅ Aggiungi nuove categorie (es. `'analytics'`)
- ⚠️ NON modificare la struttura base (motion.div)

---

### **CardHeader** (Header con Icon + Confidence)

**File**: `FylleCard.tsx` (lines 61-115)

**Props**:
```typescript
{
  icon: LucideIcon;
  title: string;
  subtitle?: string;
  confidence?: number;
  category: 'company' | 'audience' | 'voice' | 'insight';
}
```

**Features**:
- Icon colorato per categoria
- Confidence badge (emoji + label)
- Animated progress bar
- Responsive layout

**Confidence Levels**:
- `≥ 0.85`: "AI confident" 🧠 (green)
- `0.6-0.85`: "Under review" ⚙️ (amber)
- `< 0.6`: "Low confidence" 🧩 (red)

**Modifica Sicura**:
- ✅ Cambia threshold confidence (es. 0.85 → 0.90)
- ✅ Aggiungi nuovi livelli
- ✅ Modifica emoji/label
- ⚠️ NON rimuovere la progress bar (UX importante)

---

### **CardContent** (Content Area)

**File**: `FylleCard.tsx` (lines 122-124)

**Props**:
```typescript
{
  children: React.ReactNode;
  className?: string;
}
```

**Styling**: Padding standard (px-6 py-4)

**Modifica Sicura**:
- ✅ Aggiungi className custom
- ✅ Modifica padding (es. `py-6` per più spazio)

---

### **CardFooter** (Footer con CTA)

**File**: `FylleCard.tsx` (lines 131-137)

**Props**:
```typescript
{
  children: React.ReactNode;
  className?: string;
}
```

**Styling**: Border top + background semi-trasparente

**Modifica Sicura**:
- ✅ Aggiungi className custom
- ✅ Rimuovi border (se non serve)

---

### **Chip** (Tag/Badge)

**File**: `FylleCard.tsx` (lines 145-163)

**Props**:
```typescript
{
  children: React.ReactNode;
  variant?: 'default' | 'primary' | 'secondary';
  className?: string;
}
```

**Variants**:
- `default`: Gray
- `primary`: Emerald (green)
- `secondary`: Blue

**Modifica Sicura**:
- ✅ Aggiungi nuovi variant (es. `'warning'`, `'danger'`)
- ✅ Modifica colori esistenti

---

### **ConfidenceBadge** (Confidence Indicator)

**File**: `FylleCard.tsx` (lines 170-184)

**Props**:
```typescript
{
  confidence: number;
  source?: string;
}
```

**Display**: `92% confidence • Source [1]`

**Modifica Sicura**:
- ✅ Cambia formato (es. `0.92` → `92%`)
- ✅ Aggiungi tooltip
- ⚠️ Attenzione: colore dinamico usa template literals (bug potenziale con Tailwind JIT)

---

### **Section** (Section con Title + Icon)

**File**: `FylleCard.tsx` (lines 193-203)

**Props**:
```typescript
{
  title: string;
  icon?: LucideIcon;
  children: React.ReactNode;
  className?: string;
}
```

**Modifica Sicura**:
- ✅ Aggiungi collapsible behavior
- ✅ Modifica spacing (space-y-2)

---

## 🎴 Specialized Cards

### **1. CompanySnapshotCardV2**

**File**: `CompanySnapshotCardV2.tsx`

**Data Used**:
- `snapshot.company.name`
- `snapshot.company.industry`
- `snapshot.company.description` (truncated 280 chars)
- `snapshot.company.website`
- `snapshot.company.key_offerings` (max 4)
- `snapshot.company.differentiators` (max 3)
- `snapshot.company.evidence` (for confidence)
- `snapshot.generated_at`

**Features**:
- Hover state (button opacity)
- Truncation intelligente
- External link icon
- Numbered differentiators

**Modifica Sicura**:
```typescript
// ✅ Cambia max offerings
snapshot.company.key_offerings.slice(0, 4) → slice(0, 6)

// ✅ Cambia truncation length
truncateText(snapshot.company.description, 280) → 350

// ✅ Aggiungi nuovo campo
{snapshot.company.founded_year && (
  <div>Founded: {snapshot.company.founded_year}</div>
)}
```

---

### **2. AudienceIntelligenceCard**

**File**: `AudienceIntelligenceCard.tsx`

**Data Used**:
- `snapshot.audience.primary`
- `snapshot.audience.secondary` (max 3)
- `snapshot.audience.pain_points` (max 3)
- `snapshot.audience.desired_outcomes` (max 3)

**Features**:
- Primary/Secondary distinction
- Icon-based lists (AlertCircle, CheckCircle2)
- Color-coded chips

**Modifica Sicura**:
```typescript
// ✅ Cambia max items
audience.pain_points.slice(0, 3) → slice(0, 5)

// ✅ Aggiungi nuovo campo
{audience.demographics && (
  <Section title="Demographics">
    {audience.demographics}
  </Section>
)}
```

---

### **3. VoiceDNACard**

**File**: `VoiceDNACard.tsx`

**Data Used**:
- `snapshot.voice.tone` (capitalized)
- `snapshot.voice.style_guidelines` (max 3)
- `snapshot.voice.cta_preferences` (max 3)
- `snapshot.voice.forbidden_phrases`

**Features**:
- Dynamic tone color (getToneColor)
- Interactive CTA buttons
- Conditional forbidden phrases

**Modifica Sicura**:
```typescript
// ✅ Aggiungi nuovo tone color
const getToneColor = (tone: string) => {
  if (lowerTone.includes('enthusiastic')) return 'from-yellow-500/10 to-yellow-600/5';
  // ...
};

// ✅ Cambia CTA display
<button> → <Chip variant="primary">
```

---

### **4. StrategicInsightsCard**

**File**: `StrategicInsightsCard.tsx`

**Data Used**:
- `snapshot.insights.recent_news` (max 2)
- `snapshot.insights.key_messages` (max 3)
- `snapshot.company.evidence` (max 2)

**Features**:
- Tab navigation (News / Messages)
- Active tab state
- Evidence with confidence badges
- Empty states

**Modifica Sicura**:
```typescript
// ✅ Aggiungi nuovo tab
const [activeTab, setActiveTab] = useState<'news' | 'messages' | 'competitors'>('news');

// ✅ Cambia max items
insights.recent_news.slice(0, 2) → slice(0, 4)

// ✅ Aggiungi filtro
{insights.recent_news.filter(news => news.includes('funding')).map(...)}
```

---

## 🎨 Styling System

### **Tailwind Configuration**

**File**: `tailwind.config.js`

```javascript
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
```

### **Color Palette**

| Category  | Primary Color | Gradient                          | Border                  |
|-----------|---------------|-----------------------------------|-------------------------|
| Company   | Emerald       | `from-emerald-500/10 to-emerald-600/5` | `border-emerald-500/20` |
| Audience  | Blue          | `from-blue-500/10 to-blue-600/5`       | `border-blue-500/20`    |
| Voice     | Purple        | `from-purple-500/10 to-purple-600/5`   | `border-purple-500/20`  |
| Insight   | Amber         | `from-amber-500/10 to-amber-600/5`     | `border-amber-500/20`   |

### **Typography**

- **Font**: Inter (Google Fonts)
- **Base Size**: 14-16px (text-sm, text-base)
- **Titles**: 18-24px (text-lg, text-xl)
- **Weight**: 400 (normal), 600 (semibold), 700 (bold)

### **Spacing**

- **Card Gap**: 24px (`gap-6`)
- **Internal Padding**: 24px (`p-6`)
- **Section Spacing**: 16px (`space-y-4`)

### **Animations**

**Framer Motion**:
```typescript
// Card entrance
initial={{ opacity: 0, scale: 0.95 }}
animate={{ opacity: 1, scale: 1 }}
transition={{ duration: 0.3, delay: 0.1 }}

// Confidence bar
initial={{ width: 0 }}
animate={{ width: `${confidence * 100}%` }}
transition={{ duration: 0.6, delay: 0.2 }}
```

---

## ✅ Modifica Sicura - Checklist

### **Prima di Modificare**

1. ✅ Identifica il file corretto (usa questa doc)
2. ✅ Verifica le dipendenze (quali card usano questo component?)
3. ✅ Controlla il tipo TypeScript (CompanySnapshot)
4. ✅ Testa con dati reali (usa snapshot Timeflow/IKEA)

### **Modifiche Sicure (Low Risk)**

✅ **Cambiare colori** (categoryColors, variants)  
✅ **Aggiungere campi** (se esistono in CompanySnapshot)  
✅ **Modificare max items** (slice(0, 3) → slice(0, 5))  
✅ **Aggiungere sezioni** (nuovo Section component)  
✅ **Modificare testi** (labels, placeholders)  
✅ **Aggiungere animazioni** (Framer Motion)  

### **Modifiche Rischiose (High Risk)**

⚠️ **Cambiare struttura FylleCard** (può rompere tutte le card)  
⚠️ **Modificare extractCompanySnapshot** (può rompere data flow)  
⚠️ **Rimuovere campi obbligatori** (name, title, etc.)  
⚠️ **Cambiare grid layout** (può rompere responsive)  
⚠️ **Modificare TypeScript types** (richiede update backend)  

---

## 🔧 Common Patterns

### **Pattern 1: Aggiungere un Nuovo Campo**

```typescript
// 1. Verifica che il campo esista in CompanySnapshot
// 2. Aggiungi nella card appropriata

{snapshot.company.founded_year && (
  <div className="text-sm text-gray-600">
    Founded: {snapshot.company.founded_year}
  </div>
)}
```

### **Pattern 2: Aggiungere una Nuova Sezione**

```typescript
{snapshot.company.certifications && snapshot.company.certifications.length > 0 && (
  <Section title="Certifications" icon={Award}>
    <div className="flex flex-wrap gap-2">
      {snapshot.company.certifications.map((cert, idx) => (
        <Chip key={idx} variant="primary">{cert}</Chip>
      ))}
    </div>
  </Section>
)}
```

### **Pattern 3: Aggiungere una Nuova Card**

```typescript
// 1. Crea nuovo file: CompetitorsCard.tsx
export const CompetitorsCard: React.FC<{ snapshot: CompanySnapshot }> = ({ snapshot }) => {
  return (
    <FylleCard category="insight" className="h-full">
      <CardHeader icon={Target} title="Competitors" category="insight" />
      <CardContent>
        {/* Content */}
      </CardContent>
    </FylleCard>
  );
};

// 2. Aggiungi in OnboardingResultsGrid.tsx
<motion.div transition={{ delay: 0.5 }}>
  <CompetitorsCard snapshot={snapshot} />
</motion.div>

// 3. Esporta in index.ts
export { CompetitorsCard } from './CompetitorsCard';
```

### **Pattern 4: Modificare il Grid Layout**

```typescript
// Da 2x2 a 3 colonne
<div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
  {/* 3 card per row */}
</div>

// Hero + 2 colonne
<div className="space-y-6">
  {/* Hero card full width */}
  <CompanySnapshotCardV2 snapshot={snapshot} />
  
  {/* 2 colonne sotto */}
  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
    <AudienceIntelligenceCard snapshot={snapshot} />
    <VoiceDNACard snapshot={snapshot} />
  </div>
</div>
```

---

## 🎯 Quick Reference

### **Voglio modificare...**

| Cosa                          | File                          | Linee      |
|-------------------------------|-------------------------------|------------|
| Colori card                   | `FylleCard.tsx`               | 13-18      |
| Confidence threshold          | `FylleCard.tsx`               | 68-72      |
| Max offerings mostrati        | `CompanySnapshotCardV2.tsx`   | 64         |
| Max pain points               | `AudienceIntelligenceCard.tsx`| 56         |
| Tone colors                   | `VoiceDNACard.tsx`            | 20-27      |
| Tab content                   | `StrategicInsightsCard.tsx`   | 59-102     |
| Grid layout                   | `OnboardingResultsGrid.tsx`   | 36         |
| Header/Footer                 | `OnboardingResultsGrid.tsx`   | 21-33, 95-113 |
| Data extraction fallback      | `CompanySnapshotRenderer.tsx` | 16-40      |

---

## 📝 Notes

- **Tailwind JIT**: Classi dinamiche (es. `bg-${color}-500`) potrebbero non funzionare. Usa classi complete.
- **Framer Motion**: Delay staggered (0.1, 0.2, 0.3, 0.4) per effetto cascata.
- **Responsive**: Breakpoint `md:` = 768px. Sotto = stack verticale.
- **TypeScript**: Tutti i component sono type-safe. Usa `CompanySnapshot` type.
- **Empty States**: Gestisci sempre il caso `length === 0` o `undefined`.

---

**Ultimo aggiornamento**: 2025-10-23  
**Versione**: 1.0  
**Autore**: Fylle AI Team

