# 📊 REPORT: 3 AREE HARDCODING - ANALISI E SOLUZIONE

**Data**: 2025-10-19  
**Branch**: `analytics-dashboard`  
**Obiettivo**: Analisi chiara e sintetica delle 3 aree architetturali

---

## 🎯 AREA 1: SELEZIONE WORKFLOW (Richiesta a CGS)

### **COSA FA**
Determina **quale workflow CGS** eseguire in base al goal selezionato dall'utente.

### **FLUSSO ATTUALE**

```
User seleziona goal (frontend)
    ↓
OnboardingGoal enum ("company_analytics", "linkedin_post", etc.)
    ↓
Settings.get_workflow_type(goal) → workflow_type
    ↓
PayloadBuilder.build_payload() → if/elif per goal
    ↓
CGS riceve workflow_type ("onboarding_analytics_generator", "onboarding_content_generator")
```

---

### **CODICE COINVOLTO**

#### **1.1 Frontend - Selezione Goal**
**File**: `onboarding-frontend/src/components/steps/Step1CompanyInput.tsx`  
**Linee**: 190-220

```tsx
// ❌ HARDCODED: Array di goals
{GOAL_OPTIONS.map((option) => (
  <WizardChoice
    label={option.label}
    description={option.description}
    icon={option.icon}
    onClick={() => handleChoiceSelect(option.value as OnboardingGoal)}
  />
))}
```

**File**: `onboarding-frontend/src/config/constants.ts`  
**Linee**: 35-78

```tsx
// ❌ HARDCODED: Goals definiti staticamente
export const GOAL_OPTIONS = [
  { value: 'company_analytics', label: 'Company Analytics', icon: '📊', ... },
  { value: 'linkedin_post', label: 'LinkedIn Post', icon: '💼', ... },
  { value: 'linkedin_article', label: 'LinkedIn Article', icon: '📄', ... },
  { value: 'newsletter', label: 'Newsletter', icon: '📧', ... },
  { value: 'newsletter_premium', label: 'Premium Newsletter', icon: '⭐', ... },
  { value: 'blog_post', label: 'Blog Post', icon: '✍️', ... },
  { value: 'article', label: 'Article', icon: '📝', ... },
];
```

**Problema**: Ogni nuovo goal richiede modifica frontend + deploy.

---

#### **1.2 Backend - Mapping Goal → Workflow**
**File**: `onboarding/config/settings.py`  
**Linee**: 107-133

```python
# ✅ CONFIGURABILE: Mapping in settings
default_workflow_mappings: dict = Field(
    default={
        "company_analytics": "onboarding_analytics_generator",
        "linkedin_post": "onboarding_content_generator",
        "linkedin_article": "onboarding_content_generator",
        "newsletter": "onboarding_content_generator",
        "newsletter_premium": "onboarding_content_generator",
        "blog_post": "onboarding_content_generator",
        "article": "onboarding_content_generator",
    }
)

content_type_mappings: dict = Field(
    default={
        "company_analytics": "analytics",
        "linkedin_post": "linkedin_post",
        "linkedin_article": "linkedin_article",
        "newsletter": "newsletter",
        "newsletter_premium": "newsletter",
        "blog_post": "blog_post",
        "article": "blog_post",
    }
)

def get_workflow_type(self, goal: str) -> str:
    """Map onboarding goal to CGS workflow type."""
    return self.default_workflow_mappings.get(
        goal.lower(), "onboarding_content_generator"
    )
```

**Stato**: ✅ **GIÀ MODULARE** - Mapping configurabile, non hardcoded.

---

#### **1.3 Backend - Costruzione Payload**
**File**: `onboarding/application/builders/payload_builder.py`  
**Linee**: 35-79

```python
def build_payload(self, session_id, trace_id, snapshot, goal, dry_run, requested_provider):
    """Build CGS payload based on goal."""
    
    # ❌ HARDCODED: if-elif per goal type
    if goal == OnboardingGoal.COMPANY_ANALYTICS:
        return self._build_analytics_payload(...)
    
    elif goal in {
        OnboardingGoal.LINKEDIN_POST,
        OnboardingGoal.LINKEDIN_ARTICLE,
        OnboardingGoal.BLOG_POST,
        OnboardingGoal.NEWSLETTER,
        OnboardingGoal.NEWSLETTER_PREMIUM,
        OnboardingGoal.ARTICLE,
    }:
        return self._build_onboarding_content_payload(...)
    
    else:
        raise ValueError(f"Unsupported goal: {goal}")
```

**Problema**: Ogni nuovo goal richiede modifica del codice (nuovo if/elif).

---

### **SOLUZIONE PROPOSTA: Registry Pattern**

#### **Approccio**
Usare **PayloadBuilder Registry** per mappare goal → builder method.

#### **Implementazione**

```python
# File: onboarding/application/builders/payload_registry.py (NUOVO)

class PayloadBuilderRegistry:
    """Registry for payload builders."""
    
    def __init__(self):
        self._builders: Dict[str, Callable] = {}
    
    def register(self, goal: str, builder_method: Callable):
        """Register a payload builder for a goal."""
        self._builders[goal] = builder_method
    
    def get_builder(self, goal: str) -> Callable:
        """Get builder for goal."""
        if goal not in self._builders:
            raise ValueError(f"No builder registered for goal: {goal}")
        return self._builders[goal]

# Global registry
payload_registry = PayloadBuilderRegistry()
```

```python
# File: onboarding/application/builders/payload_builder.py (MODIFICARE)

class PayloadBuilder:
    def __init__(self, settings: OnboardingSettings):
        self.settings = settings
        
        # Register builders
        self._register_builders()
    
    def _register_builders(self):
        """Register all payload builders."""
        payload_registry.register("company_analytics", self._build_analytics_payload)
        payload_registry.register("linkedin_post", self._build_onboarding_content_payload)
        payload_registry.register("linkedin_article", self._build_onboarding_content_payload)
        payload_registry.register("newsletter", self._build_onboarding_content_payload)
        # ... etc
    
    def build_payload(self, session_id, trace_id, snapshot, goal, dry_run, requested_provider):
        """Build CGS payload based on goal."""
        
        # ✅ MODULARE: Usa registry invece di if-elif
        builder = payload_registry.get_builder(goal.value)
        return builder(session_id, trace_id, snapshot, goal, dry_run, requested_provider)
```

**Benefici**:
- ✅ Nessun if-elif hardcoded
- ✅ Facile aggiungere nuovi goals (register + method)
- ✅ Testabile in isolamento

---

### **SOLUZIONE PROPOSTA: Dynamic Goals API**

#### **Approccio**
Frontend carica goals da API invece di array hardcoded.

#### **Implementazione**

```python
# File: onboarding/api/endpoints.py (AGGIUNGERE)

@router.get("/goals", response_model=List[GoalOption])
async def list_available_goals(
    settings: OnboardingSettings = Depends(get_onboarding_settings),
):
    """List available onboarding goals."""
    
    goals = []
    for goal_value in settings.default_workflow_mappings.keys():
        goals.append(GoalOption(
            value=goal_value,
            label=GOAL_LABELS.get(goal_value, goal_value.replace("_", " ").title()),
            icon=GOAL_ICONS.get(goal_value, "📄"),
            description=GOAL_DESCRIPTIONS.get(goal_value, ""),
            enabled=True,
            recommended=(goal_value == "company_analytics"),
        ))
    
    return goals
```

```typescript
// File: onboarding-frontend/src/services/api/goals.ts (NUOVO)

export interface GoalOption {
  value: string;
  label: string;
  icon: string;
  description: string;
  enabled: boolean;
  recommended: boolean;
}

export const goalsApi = {
  async listGoals(): Promise<GoalOption[]> {
    const response = await api.get<GoalOption[]>('/api/v1/goals');
    return response.data;
  },
};
```

```tsx
// File: Step1CompanyInput.tsx (MODIFICARE)

const [goalOptions, setGoalOptions] = useState<GoalOption[]>([]);

useEffect(() => {
  // ✅ DINAMICO: Carica da API
  goalsApi.listGoals().then(setGoalOptions);
}, []);

// Render
{goalOptions.map((option) => (
  <WizardChoice ... />
))}
```

**Benefici**:
- ✅ Goals configurabili da backend
- ✅ Nessun deploy frontend per nuovi goals
- ✅ Facile abilitare/disabilitare goals

---

## 🎯 AREA 2: DOMANDE AGGIUNTIVE (Completamento Contesto)

### **COSA FA**
Genera **domande personalizzate** basate su company snapshot e goal, per completare il contesto prima di inviare a CGS.

### **FLUSSO ATTUALE**

```
Perplexity Research → raw_content
    ↓
Gemini Synthesis → CompanySnapshot + clarifying_questions (personalizzate!)
    ↓
Frontend mostra domande (Step4QuestionsForm)
    ↓
User risponde
    ↓
Risposte salvate in snapshot.clarifying_answers
    ↓
PayloadBuilder include answers nel payload CGS
```

---

### **CODICE COINVOLTO**

#### **2.1 Backend - Generazione Domande**
**File**: `onboarding/infrastructure/adapters/gemini_adapter.py`  
**Linee**: 68-173

```python
def _build_synthesis_prompt(self, brand_name, research_content, website):
    """Build prompt for company snapshot synthesis."""
    
    prompt = f"""You are an expert business analyst synthesizing company research.

COMPANY: {brand_name}
WEBSITE: {website}

RESEARCH DATA:
{research_content}

YOUR TASK:
Produce a structured JSON with:

1. company: {...}
2. audience: {...}
3. voice: {...}
4. insights: {...}
5. clarifying_questions: [
    {{
      "id": "q1",
      "question": "What specific aspect of [topic] should we focus on?",
      "reason": "To tailor content to business priorities",
      "expected_response_type": "string",
      "options": null,
      "required": true
    }},
    {{
      "id": "q2",
      "question": "What is your preferred content length?",
      "reason": "To match audience attention span",
      "expected_response_type": "enum",
      "options": ["short (200-300 words)", "medium (400-600 words)", "long (800+ words)"],
      "required": true
    }},
    {{
      "id": "q3",
      "question": "Should we include data/statistics?",
      "reason": "To determine content depth",
      "expected_response_type": "boolean",
      "required": false
    }}
  ]
"""
    return prompt
```

**Stato**: ✅ **GIÀ MODULARE** - Gemini genera domande personalizzate basate su research.

**Nota**: Le domande sono **dinamiche** e **personalizzate** per ogni azienda. Non hardcoded!

---

#### **2.2 Frontend - Rendering Domande**
**File**: `onboarding-frontend/src/components/steps/Step4QuestionsForm.tsx`  
**Linee**: 1-80

```tsx
export const Step4QuestionsForm: React.FC<Step4QuestionsFormProps> = ({
  questions,  // ✅ Ricevute da backend (personalizzate!)
  onSubmit,
  isLoading,
}) => {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, any>>({});

  // Convert questions to wizard format
  const wizardQuestions = useMemo(
    () => questions.map(convertToWizardQuestion),
    [questions]
  );

  const currentQuestion = wizardQuestions[currentQuestionIndex];

  const handleAnswer = (value: any) => {
    const newAnswers = { ...answers, [currentQuestion.id]: value };
    setAnswers(newAnswers);

    if (currentQuestionIndex === wizardQuestions.length - 1) {
      onSubmit(newAnswers);  // Submit all answers
    } else {
      setCurrentQuestionIndex((prev) => prev + 1);
    }
  };

  return (
    <WizardQuestion
      question={currentQuestion}
      currentIndex={currentQuestionIndex}
      totalQuestions={wizardQuestions.length}
      onAnswer={handleAnswer}
      isLoading={isLoading}
    />
  );
};
```

**Stato**: ✅ **GIÀ MODULARE** - Frontend renderizza domande ricevute da backend, nessun hardcoding.

---

### **PROBLEMA IDENTIFICATO: NESSUNO!**

**Area 2 è già completamente modulare**:
- ✅ Domande generate dinamicamente da Gemini
- ✅ Personalizzate per ogni azienda
- ✅ Frontend agnostico (renderizza qualsiasi domanda)
- ✅ Nessun hardcoding

**Nessuna modifica necessaria in questa area.** 🎉

---

## 🎯 AREA 3: RESTITUZIONE RISULTATO (Visualizzazione Response CGS)

### **COSA FA**
Mostra il **risultato** della richiesta CGS all'utente in base al tipo di contenuto generato.

### **FLUSSO ATTUALE**

```
CGS esegue workflow → ResultEnvelope
    ↓
ResultEnvelope.content (ContentResult)
    ↓
Frontend riceve session.cgs_response
    ↓
Step6Results controlla session.goal
    ↓
if goal == COMPANY_ANALYTICS → Step6Dashboard (8 cards)
else → ContentPreview (text + copy/download)
```

---

### **CODICE COINVOLTO**

#### **3.1 Backend - Response Structure**
**File**: `onboarding/domain/cgs_contracts.py`  
**Linee**: 124-137

```python
class ContentResult(BaseModel):
    """Content result from CGS workflow."""
    
    content_id: Optional[UUID] = None
    title: str
    body: str
    format: str = Field(default="markdown")
    word_count: int = Field(default=0, ge=0)
    character_count: int = Field(default=0, ge=0)
    reading_time_minutes: Optional[float] = Field(default=None, ge=0.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)  # ← Può contenere analytics_data
    generated_image: Optional[Dict[str, Any]] = None
    image_metadata: Optional[Dict[str, Any]] = None
```

**File**: `core/infrastructure/workflows/handlers/onboarding_analytics_handler.py`  
**Linee**: 115-136

```python
# Analytics handler ritorna:
result = {
    "status": "completed",
    "content": {
        "title": f"Company Analytics Report: {context['company_name']}",
        "body": analytics_report.get("full_report", ""),
        "format": "json",
        "metadata": {...},
        "analytics_data": analytics_report,  # ← Campo custom per analytics
    },
}
```

**Problema**: `analytics_data` è un campo **custom** non previsto in `ContentResult` schema.

---

#### **3.2 Frontend - Conditional Rendering**
**File**: `onboarding-frontend/src/components/steps/Step6Results.tsx`  
**Linee**: 21-47

```tsx
export const Step6Results: React.FC<Step6ResultsProps> = ({ session, onStartNew }) => {
  // ❌ HARDCODED: Check per analytics goal
  const isAnalytics = session.goal === OnboardingGoal.COMPANY_ANALYTICS;

  // Extract analytics data
  const analyticsData: AnalyticsData | null = React.useMemo(() => {
    if (!isAnalytics || !session.cgs_response) return null;
    const content = session.cgs_response.content;
    if (!content || !content.analytics_data) return null;
    return content.analytics_data as AnalyticsData;
  }, [isAnalytics, session.cgs_response]);

  // ❌ HARDCODED: if per analytics
  if (isAnalytics && analyticsData) {
    return (
      <Step6Dashboard
        analyticsData={analyticsData}
        companyName={session.brand_name}
        onReset={onStartNew}
      />
    );
  }

  // Otherwise, render content preview (legacy)
  const contentPreview = session.cgs_response?.content?.body || 'Your content is ready!';
  // ... render content preview
};
```

**Problema**: Ogni nuovo tipo di visualizzazione richiede nuovo `if` hardcoded.

---

### **SOLUZIONE PROPOSTA: Metadata-Driven Rendering**

#### **Approccio**
Backend specifica **display_type** in metadata, frontend usa **Renderer Registry**.

#### **Implementazione**

**Step 1: Aggiungere `display_type` a ContentResult**

```python
# File: onboarding/domain/cgs_contracts.py (MODIFICARE)

class ContentResult(BaseModel):
    """Content result from CGS workflow."""
    
    content_id: Optional[UUID] = None
    title: str
    body: str
    format: str = Field(default="markdown")
    display_type: str = Field(default="content_preview")  # ← NUOVO!
    # Possibili valori: "content_preview", "analytics_dashboard", "competitor_analysis", etc.
    
    word_count: int = Field(default=0, ge=0)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    # ... rest
```

**Step 2: Analytics Handler setta display_type**

```python
# File: core/infrastructure/workflows/handlers/onboarding_analytics_handler.py (MODIFICARE)

result = {
    "content": {
        "title": f"Company Analytics Report: {context['company_name']}",
        "body": analytics_report.get("full_report", ""),
        "format": "json",
        "display_type": "analytics_dashboard",  # ← NUOVO!
        "analytics_data": analytics_report,
    },
}
```

**Step 3: Content Handler setta display_type**

```python
# File: core/infrastructure/workflows/handlers/onboarding_content_handler.py (MODIFICARE)

async def _execute_standard_workflow(self, context):
    result = await self.execute_workflow(context)
    
    # Set display_type
    if "content" in result:
        result["content"]["display_type"] = "content_preview"  # ← NUOVO!
    
    return result
```

**Step 4: Frontend Renderer Registry**

```typescript
// File: onboarding-frontend/src/renderers/RendererRegistry.ts (NUOVO)

class RendererRegistry {
  private renderers: Map<string, {
    component: React.ComponentType<any>;
    dataExtractor: (session: OnboardingSession) => any;
  }> = new Map();

  register(displayType: string, component: any, dataExtractor: any) {
    this.renderers.set(displayType, { component, dataExtractor });
  }

  getRenderer(displayType: string) {
    return this.renderers.get(displayType);
  }
}

export const rendererRegistry = new RendererRegistry();
```

**Step 5: Registrare Renderers**

```typescript
// File: onboarding-frontend/src/renderers/AnalyticsRenderer.tsx (NUOVO)

import { rendererRegistry } from './RendererRegistry';
import { Step6Dashboard } from '@/components/steps/Step6Dashboard';

const extractAnalyticsData = (session) => {
  return session.cgs_response?.content?.analytics_data || null;
};

rendererRegistry.register(
  'analytics_dashboard',
  Step6Dashboard,
  extractAnalyticsData
);
```

```typescript
// File: onboarding-frontend/src/renderers/ContentRenderer.tsx (NUOVO)

import { rendererRegistry } from './RendererRegistry';
import { ContentPreview } from '@/components/steps/ContentPreview';  // Estratto da Step6Results

const extractContentData = (session) => {
  return {
    contentTitle: session.metadata?.content_title || 'Content Generated',
    contentPreview: session.cgs_response?.content?.body || '',
    wordCount: session.metadata?.word_count || 0,
  };
};

rendererRegistry.register(
  'content_preview',
  ContentPreview,
  extractContentData
);
```

**Step 6: Step6Results usa Registry**

```tsx
// File: Step6Results.tsx (MODIFICARE COMPLETAMENTE)

import { rendererRegistry } from '@/renderers/RendererRegistry';
import '@/renderers/AnalyticsRenderer';  // Auto-register
import '@/renderers/ContentRenderer';    // Auto-register

export const Step6Results: React.FC<Step6ResultsProps> = ({ session, onStartNew }) => {
  // ✅ METADATA-DRIVEN: Usa display_type da response
  const displayType = session.cgs_response?.content?.display_type || 'content_preview';
  
  // Get renderer
  const renderer = rendererRegistry.getRenderer(displayType);
  
  if (!renderer) {
    // Fallback
    const fallback = rendererRegistry.getRenderer('content_preview');
    if (!fallback) return <div>Error: No renderer available</div>;
    const data = fallback.dataExtractor(session);
    return <fallback.component session={session} data={data} onStartNew={onStartNew} />;
  }
  
  // Extract data and render
  const data = renderer.dataExtractor(session);
  const RendererComponent = renderer.component;
  
  return <RendererComponent session={session} data={data} onStartNew={onStartNew} />;
};
```

**Benefici**:
- ✅ Nessun hardcoding di goal types
- ✅ Backend controlla rendering tramite metadata
- ✅ Facile aggiungere nuovi renderers (1 file + register)
- ✅ Fallback automatico

---

## 📊 SUMMARY: PROBLEMI E SOLUZIONI

| Area | Problema | Soluzione | Priorità |
|------|----------|-----------|----------|
| **Area 1: Selezione Workflow** | ❌ GOAL_OPTIONS hardcoded<br>❌ if-elif in PayloadBuilder | ✅ Dynamic Goals API<br>✅ Payload Registry Pattern | **MEDIA** |
| **Area 2: Domande Aggiuntive** | ✅ Nessuno (già modulare) | - | - |
| **Area 3: Restituzione Risultato** | ❌ if hardcoded per analytics<br>❌ Nessun display_type | ✅ Metadata-Driven Rendering<br>✅ Renderer Registry | **ALTA** |

---

## 🎯 RACCOMANDAZIONE

**Priorità di implementazione**:

1. **AREA 3** (Alta priorità - 3-4 ore)
   - Aggiungere `display_type` a `ContentResult`
   - Implementare Renderer Registry
   - Modificare Step6Results

2. **AREA 1** (Media priorità - 4-5 ore)
   - Implementare Dynamic Goals API
   - Implementare Payload Registry Pattern

3. **AREA 2** (Nessuna azione necessaria)
   - Già completamente modulare ✅

**Tempo totale stimato**: 7-9 ore

---

**Fine Report** 🎉

