# 🛠️ Card Modification Examples - Practical Guide

> **Obiettivo**: Esempi pratici di modifiche comuni al sistema di card

---

## 📋 Table of Contents

1. [Modifiche Visive](#modifiche-visive)
2. [Aggiungere Contenuto](#aggiungere-contenuto)
3. [Modificare Layout](#modificare-layout)
4. [Aggiungere Interattività](#aggiungere-interattività)
5. [Troubleshooting](#troubleshooting)

---

## 🎨 Modifiche Visive

### **Esempio 1: Cambiare Colore di una Card**

**Obiettivo**: Cambiare il colore della Company Card da verde (emerald) a blu (blue)

**File**: `onboarding-frontend/src/components/cards/FylleCard.tsx`

```typescript
// PRIMA (linea 14)
const categoryColors = {
  company: 'from-emerald-500/10 to-emerald-600/5 border-emerald-500/20 hover:border-emerald-500/40 hover:shadow-emerald-200/20',
  // ...
};

// DOPO
const categoryColors = {
  company: 'from-blue-500/10 to-blue-600/5 border-blue-500/20 hover:border-blue-500/40 hover:shadow-blue-200/20',
  // ...
};
```

**File**: `onboarding-frontend/src/components/cards/FylleCard.tsx` (icon colors)

```typescript
// PRIMA (linea 55)
const categoryIconColors = {
  company: 'text-emerald-600',
  // ...
};

// DOPO
const categoryIconColors = {
  company: 'text-blue-600',
  // ...
};
```

**File**: `onboarding-frontend/src/components/cards/CompanySnapshotCardV2.tsx`

```typescript
// PRIMA (linea 100)
className="rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-xs font-medium text-emerald-700"

// DOPO
className="rounded-lg border border-blue-200 bg-blue-50 px-3 py-1.5 text-xs font-medium text-blue-700"
```

---

### **Esempio 2: Aumentare Dimensione Font del Titolo**

**Obiettivo**: Titolo card più grande (da 18px a 24px)

**File**: `onboarding-frontend/src/components/cards/FylleCard.tsx`

```typescript
// PRIMA (linea 84)
<h3 className="text-lg font-semibold text-gray-900">{title}</h3>

// DOPO
<h3 className="text-2xl font-bold text-gray-900">{title}</h3>
```

---

### **Esempio 3: Modificare Confidence Threshold**

**Obiettivo**: Soglia "AI confident" da 85% a 90%

**File**: `onboarding-frontend/src/components/cards/FylleCard.tsx`

```typescript
// PRIMA (linea 69)
const getConfidenceLabel = (conf: number) => {
  if (conf >= 0.85) return { label: 'AI confident', color: 'text-emerald-600', emoji: '🧠' };
  if (conf >= 0.6) return { label: 'Under review', color: 'text-amber-600', emoji: '⚙️' };
  return { label: 'Low confidence', color: 'text-red-600', emoji: '🧩' };
};

// DOPO
const getConfidenceLabel = (conf: number) => {
  if (conf >= 0.90) return { label: 'AI confident', color: 'text-emerald-600', emoji: '🧠' };
  if (conf >= 0.70) return { label: 'Under review', color: 'text-amber-600', emoji: '⚙️' };
  return { label: 'Low confidence', color: 'text-red-600', emoji: '🧩' };
};
```

**Nota**: Aggiorna anche la progress bar (linea 104):

```typescript
// PRIMA
className={`h-full ${
  confidence >= 0.85 ? 'bg-emerald-500' : confidence >= 0.6 ? 'bg-amber-500' : 'bg-red-500'
}`}

// DOPO
className={`h-full ${
  confidence >= 0.90 ? 'bg-emerald-500' : confidence >= 0.70 ? 'bg-amber-500' : 'bg-red-500'
}`}
```

---

## 📝 Aggiungere Contenuto

### **Esempio 4: Mostrare Più Offerings (da 4 a 6)**

**Obiettivo**: Mostrare 6 key offerings invece di 4

**File**: `onboarding-frontend/src/components/cards/CompanySnapshotCardV2.tsx`

```typescript
// PRIMA (linea 64)
{snapshot.company.key_offerings.slice(0, 4).map((offering, idx) => (
  <Chip key={idx} variant="primary">{offering}</Chip>
))}

// DOPO
{snapshot.company.key_offerings.slice(0, 6).map((offering, idx) => (
  <Chip key={idx} variant="primary">{offering}</Chip>
))}
```

---

### **Esempio 5: Aggiungere Campo "Founded Year"**

**Obiettivo**: Mostrare anno di fondazione (se disponibile)

**File**: `onboarding-frontend/src/components/cards/CompanySnapshotCardV2.tsx`

```typescript
// Aggiungi dopo la descrizione (dopo linea 58)
{snapshot.company.founded_year && (
  <div className="flex items-center gap-2 text-sm text-gray-600">
    <Calendar className="h-4 w-4" />
    <span>Founded in {snapshot.company.founded_year}</span>
  </div>
)}
```

**Nota**: Importa l'icona:

```typescript
// Aggiungi in cima al file
import { Building2, ExternalLink, Sparkles, TrendingUp, Calendar } from 'lucide-react';
```

---

### **Esempio 6: Aggiungere Sezione "Certifications"**

**Obiettivo**: Nuova sezione per certificazioni aziendali

**File**: `onboarding-frontend/src/components/cards/CompanySnapshotCardV2.tsx`

```typescript
// Aggiungi dopo Differentiators (dopo linea 87)
{snapshot.company.certifications && snapshot.company.certifications.length > 0 && (
  <Section title="Certifications" icon={Award}>
    <div className="flex flex-wrap gap-2">
      {snapshot.company.certifications.map((cert, idx) => (
        <Chip key={idx} variant="secondary">
          {cert}
        </Chip>
      ))}
    </div>
  </Section>
)}
```

**Nota**: Importa l'icona:

```typescript
import { Building2, ExternalLink, Sparkles, TrendingUp, Award } from 'lucide-react';
```

---

### **Esempio 7: Aggiungere Tab "Competitors" in Strategic Insights**

**Obiettivo**: Nuovo tab per mostrare competitors

**File**: `onboarding-frontend/src/components/cards/StrategicInsightsCard.tsx`

**Step 1**: Aggiorna il type del state (linea 12)

```typescript
// PRIMA
const [activeTab, setActiveTab] = useState<'news' | 'messages'>('news');

// DOPO
const [activeTab, setActiveTab] = useState<'news' | 'messages' | 'competitors'>('news');
```

**Step 2**: Aggiungi il tab button (dopo linea 55)

```typescript
<button
  onClick={() => setActiveTab('competitors')}
  className={`
    pb-2 px-3 text-sm font-medium transition-all
    ${activeTab === 'competitors'
      ? 'border-b-2 border-amber-500 text-amber-700'
      : 'text-gray-500 hover:text-gray-700'
    }
  `}
>
  <div className="flex items-center gap-1.5">
    <Target className="h-4 w-4" />
    Competitors
  </div>
</button>
```

**Step 3**: Aggiungi il tab content (dopo linea 101)

```typescript
{activeTab === 'competitors' && (
  <div className="space-y-3">
    {insights.competitors && insights.competitors.length > 0 ? (
      <ul className="space-y-2">
        {insights.competitors.map((competitor, idx) => (
          <li key={idx} className="flex items-start gap-2 text-sm text-gray-700">
            <Target className="mt-0.5 h-4 w-4 flex-shrink-0 text-amber-600" />
            <span className="leading-relaxed">{competitor}</span>
          </li>
        ))}
      </ul>
    ) : (
      <div className="flex h-[200px] items-center justify-center text-sm text-gray-500">
        No competitors data available
      </div>
    )}
  </div>
)}
```

**Step 4**: Importa l'icona

```typescript
import { Lightbulb, Newspaper, MessageCircle, TrendingUp, Target } from 'lucide-react';
```

---

## 📐 Modificare Layout

### **Esempio 8: Cambiare Grid da 2x2 a 3 Colonne**

**Obiettivo**: Layout a 3 colonne invece di 2x2

**File**: `onboarding-frontend/src/components/cards/OnboardingResultsGrid.tsx`

```typescript
// PRIMA (linea 36)
<div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">

// DOPO
<div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
```

**Nota**: Con 3 colonne, considera di aggiungere una 5a o 6a card per riempire la griglia.

---

### **Esempio 9: Layout Hero + 2 Colonne**

**Obiettivo**: Company card full-width, altre 3 card sotto in 3 colonne

**File**: `onboarding-frontend/src/components/cards/OnboardingResultsGrid.tsx`

```typescript
// PRIMA (linea 35-72)
<div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
  <motion.div>...</motion.div>
  <motion.div>...</motion.div>
  <motion.div>...</motion.div>
  <motion.div>...</motion.div>
</div>

// DOPO
<div className="space-y-6 mb-8">
  {/* Hero Card - Full Width */}
  <motion.div
    initial={{ opacity: 0, scale: 0.95 }}
    animate={{ opacity: 1, scale: 1 }}
    transition={{ duration: 0.3, delay: 0.1 }}
  >
    <CompanySnapshotCardV2 snapshot={snapshot} />
  </motion.div>

  {/* 3 Cards Below */}
  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3, delay: 0.2 }}
    >
      <AudienceIntelligenceCard snapshot={snapshot} />
    </motion.div>

    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3, delay: 0.3 }}
    >
      <VoiceDNACard snapshot={snapshot} />
    </motion.div>

    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3, delay: 0.4 }}
    >
      <StrategicInsightsCard snapshot={snapshot} />
    </motion.div>
  </div>
</div>
```

---

### **Esempio 10: Aumentare Spacing tra Card**

**Obiettivo**: Gap da 24px a 32px

**File**: `onboarding-frontend/src/components/cards/OnboardingResultsGrid.tsx`

```typescript
// PRIMA (linea 36)
<div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">

// DOPO
<div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
```

---

## 🎯 Aggiungere Interattività

### **Esempio 11: Modal "Refine Details"**

**Obiettivo**: Aprire modal quando clicchi "Refine Details"

**File**: `onboarding-frontend/src/components/cards/CompanySnapshotCardV2.tsx`

**Step 1**: Aggiungi state per modal

```typescript
// Aggiungi dopo linea 11
const [isModalOpen, setIsModalOpen] = useState(false);
```

**Step 2**: Modifica il button

```typescript
// PRIMA (linea 98)
<button className="...">
  Refine Details
</button>

// DOPO
<button
  onClick={() => setIsModalOpen(true)}
  className="..."
>
  Refine Details
</button>
```

**Step 3**: Aggiungi modal component (dopo CardFooter)

```typescript
{isModalOpen && (
  <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
    <div className="bg-white rounded-2xl p-6 max-w-2xl w-full mx-4">
      <h2 className="text-2xl font-bold mb-4">Refine Company Details</h2>
      <p className="text-gray-600 mb-6">
        Edit your company information to improve AI accuracy.
      </p>
      {/* Form fields here */}
      <div className="flex gap-3 justify-end">
        <button
          onClick={() => setIsModalOpen(false)}
          className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
        >
          Cancel
        </button>
        <button className="px-4 py-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600">
          Save Changes
        </button>
      </div>
    </div>
  </div>
)}
```

---

### **Esempio 12: Tooltip su Confidence Badge**

**Obiettivo**: Mostrare tooltip con dettagli confidence

**File**: `onboarding-frontend/src/components/cards/FylleCard.tsx`

**Step 1**: Aggiungi state

```typescript
// Aggiungi in CardHeader component
const [showTooltip, setShowTooltip] = useState(false);
```

**Step 2**: Modifica confidence badge (linea 88)

```typescript
// PRIMA
{confidenceInfo && (
  <div className="flex items-center gap-1 text-xs">
    <span>{confidenceInfo.emoji}</span>
    <span className={`font-medium ${confidenceInfo.color}`}>
      {confidenceInfo.label}
    </span>
  </div>
)}

// DOPO
{confidenceInfo && (
  <div
    className="relative flex items-center gap-1 text-xs cursor-help"
    onMouseEnter={() => setShowTooltip(true)}
    onMouseLeave={() => setShowTooltip(false)}
  >
    <span>{confidenceInfo.emoji}</span>
    <span className={`font-medium ${confidenceInfo.color}`}>
      {confidenceInfo.label}
    </span>
    
    {showTooltip && (
      <div className="absolute top-full right-0 mt-2 bg-gray-900 text-white text-xs rounded-lg px-3 py-2 whitespace-nowrap z-10">
        Confidence: {Math.round(confidence * 100)}%
        <div className="absolute -top-1 right-4 w-2 h-2 bg-gray-900 rotate-45" />
      </div>
    )}
  </div>
)}
```

---

### **Esempio 13: Collapsible Section**

**Obiettivo**: Sezione "Differentiators" collapsible

**File**: `onboarding-frontend/src/components/cards/CompanySnapshotCardV2.tsx`

**Step 1**: Aggiungi state

```typescript
// Aggiungi dopo linea 11
const [isDifferentiatorsOpen, setIsDifferentiatorsOpen] = useState(true);
```

**Step 2**: Modifica Section (linea 75)

```typescript
// PRIMA
<Section title="Differentiators" icon={TrendingUp}>
  <ul className="space-y-2">
    {/* ... */}
  </ul>
</Section>

// DOPO
<div>
  <button
    onClick={() => setIsDifferentiatorsOpen(!isDifferentiatorsOpen)}
    className="flex items-center justify-between w-full text-left"
  >
    <div className="flex items-center gap-2">
      <TrendingUp className="h-4 w-4 text-gray-500" />
      <h4 className="text-sm font-semibold text-gray-700">Differentiators</h4>
    </div>
    <ChevronDown
      className={`h-4 w-4 text-gray-500 transition-transform ${
        isDifferentiatorsOpen ? 'rotate-180' : ''
      }`}
    />
  </button>
  
  {isDifferentiatorsOpen && (
    <ul className="space-y-2 mt-2">
      {snapshot.company.differentiators.slice(0, 3).map((diff, idx) => (
        <li key={idx} className="flex items-start gap-2 text-sm text-gray-700">
          <span className="mt-1 flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full bg-emerald-100 text-xs font-semibold text-emerald-700">
            {idx + 1}
          </span>
          <span className="leading-relaxed">{diff}</span>
        </li>
      ))}
    </ul>
  )}
</div>
```

**Step 3**: Importa icona

```typescript
import { Building2, ExternalLink, Sparkles, TrendingUp, ChevronDown } from 'lucide-react';
```

---

## 🐛 Troubleshooting

### **Problema 1: Tailwind Classes Non Funzionano**

**Sintomo**: Classi CSS non applicate, card senza stile

**Causa**: Tailwind non configurato o file non incluso in `content`

**Soluzione**:

1. Verifica `tailwind.config.js`:
```javascript
content: [
  "./index.html",
  "./src/**/*.{js,ts,jsx,tsx}",
],
```

2. Verifica `src/index.css`:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

3. Riavvia dev server: `npm run dev`

---

### **Problema 2: Classi Dinamiche Non Funzionano**

**Sintomo**: `bg-${color}-500` non applica il colore

**Causa**: Tailwind JIT non supporta template literals

**Soluzione**: Usa classi complete

```typescript
// ❌ NON FUNZIONA
<div className={`bg-${color}-500`} />

// ✅ FUNZIONA
const colorClasses = {
  emerald: 'bg-emerald-500',
  blue: 'bg-blue-500',
  purple: 'bg-purple-500',
};
<div className={colorClasses[color]} />
```

---

### **Problema 3: Card Non Renderizzata**

**Sintomo**: Card non appare, nessun errore console

**Causa**: Dati mancanti o condizione falsa

**Soluzione**: Aggiungi logging

```typescript
console.log('Snapshot:', snapshot);
console.log('Company:', snapshot.company);
console.log('Key Offerings:', snapshot.company.key_offerings);
```

Verifica condizioni:

```typescript
// ❌ Potrebbe essere undefined
{snapshot.company.key_offerings.length > 0 && ...}

// ✅ Safe check
{snapshot.company.key_offerings && snapshot.company.key_offerings.length > 0 && ...}
```

---

### **Problema 4: TypeScript Error**

**Sintomo**: `Property 'founded_year' does not exist on type 'CompanyInfo'`

**Causa**: Campo non definito nel type

**Soluzione**: Aggiungi al type

**File**: `onboarding-frontend/src/types/onboarding.ts`

```typescript
export interface CompanyInfo {
  name: string;
  website?: string;
  industry?: string;
  description: string;
  key_offerings?: string[];
  differentiators?: string[];
  founded_year?: number; // ← Aggiungi questo
  evidence?: Evidence[];
}
```

---

**Ultimo aggiornamento**: 2025-10-23  
**Versione**: 1.0

