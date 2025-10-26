# 🔍 ANALISI CODICE: Parti Coinvolte nel Workflow Onboarding

**Data**: 2025-10-16  
**Scopo**: Analizzare in dettaglio tutte le parti di codice coinvolte nella creazione del workflow generico per onboarding.

---

## 📊 MAPPA DELLE DIPENDENZE

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                         │
│  onboarding-frontend/src/                                   │
│  ├─ components/steps/Step1CompanyInput.tsx                  │
│  │  └─ Goal selection UI                                    │
│  └─ types/onboarding.ts                                     │
│     └─ OnboardingGoal enum                                  │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP POST /api/v1/onboarding/start
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              ONBOARDING BACKEND (FastAPI)                   │
│  onboarding/                                                │
│  ├─ api/endpoints.py                                        │
│  │  └─ start_onboarding() endpoint                          │
│  ├─ domain/models.py                                        │
│  │  ├─ OnboardingGoal enum ← MODIFICARE                     │
│  │  └─ OnboardingSession                                    │
│  ├─ domain/cgs_contracts.py                                 │
│  │  ├─ CgsPayloadLinkedInPost ← SOSTITUIRE                  │
│  │  ├─ CgsPayloadNewsletter ← SOSTITUIRE                    │
│  │  └─ CgsPayloadOnboardingContent ← CREARE                 │
│  ├─ application/builders/payload_builder.py                 │
│  │  └─ build_payload() ← MODIFICARE                         │
│  ├─ infrastructure/adapters/cgs_adapter.py                  │
│  │  └─ execute_workflow() ← MODIFICARE                      │
│  └─ config/settings.py                                      │
│     └─ default_workflow_mappings ← MODIFICARE               │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP POST /api/v1/content/generate
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                 CGS BACKEND (FastAPI)                       │
│  core/                                                      │
│  ├─ api/routes/content.py                                   │
│  │  └─ generate_content() endpoint                          │
│  ├─ infrastructure/workflows/registry.py                    │
│  │  ├─ WorkflowRegistry                                     │
│  │  └─ execute_dynamic_workflow() ← USA                     │
│  ├─ infrastructure/workflows/handlers/                      │
│  │  ├─ enhanced_article_handler.py                          │
│  │  ├─ premium_newsletter_handler.py                        │
│  │  └─ onboarding_content_handler.py ← CREARE               │
│  └─ infrastructure/workflows/__init__.py ← MODIFICARE       │
│     └─ Import nuovo handler                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 PARTE 1: ONBOARDING GOAL SELECTION

### **File: `onboarding/domain/models.py`**

**Codice Attuale**:
```python
class OnboardingGoal(str, Enum):
    """Supported onboarding goals."""
    
    LINKEDIN_POST = "linkedin_post"
    NEWSLETTER = "newsletter"
    NEWSLETTER_PREMIUM = "newsletter_premium"
    ARTICLE = "article"
```

**Modifiche Necessarie**:
```python
class OnboardingGoal(str, Enum):
    """Supported onboarding goals."""
    
    # Social Media
    LINKEDIN_POST = "linkedin_post"           # Post breve (200-400 parole)
    LINKEDIN_ARTICLE = "linkedin_article"     # ← NUOVO! Articolo lungo (800-1500)
    
    # Email Marketing
    NEWSLETTER = "newsletter"                 # Newsletter standard (1000-1500)
    NEWSLETTER_PREMIUM = "newsletter_premium" # Newsletter premium
    
    # Content Marketing
    BLOG_POST = "blog_post"                   # ← NUOVO! Blog SEO (1200-2000)
    ARTICLE = "article"                       # Articolo generico
```

**Impatto**:
- ✅ Backward compatible (mantiene valori esistenti)
- ✅ Aggiunge 2 nuovi goal: `LINKEDIN_ARTICLE`, `BLOG_POST`
- ⚠️ Richiede aggiornamento frontend types

---

### **File: `onboarding-frontend/src/types/onboarding.ts`**

**Codice Attuale**:
```typescript
export enum OnboardingGoal {
  LINKEDIN_POST = 'linkedin_post',
  NEWSLETTER = 'newsletter',
  NEWSLETTER_PREMIUM = 'newsletter_premium',
  ARTICLE = 'article',
}
```

**Modifiche Necessarie**:
```typescript
export enum OnboardingGoal {
  // Social Media
  LINKEDIN_POST = 'linkedin_post',
  LINKEDIN_ARTICLE = 'linkedin_article',     // ← NUOVO!
  
  // Email Marketing
  NEWSLETTER = 'newsletter',
  NEWSLETTER_PREMIUM = 'newsletter_premium',
  
  // Content Marketing
  BLOG_POST = 'blog_post',                   // ← NUOVO!
  ARTICLE = 'article',
}

// ← NUOVO! Labels per UI
export const GOAL_LABELS: Record<OnboardingGoal, string> = {
  [OnboardingGoal.LINKEDIN_POST]: 'LinkedIn Post',
  [OnboardingGoal.LINKEDIN_ARTICLE]: 'LinkedIn Article',
  [OnboardingGoal.NEWSLETTER]: 'Newsletter',
  [OnboardingGoal.NEWSLETTER_PREMIUM]: 'Premium Newsletter',
  [OnboardingGoal.BLOG_POST]: 'Blog Post',
  [OnboardingGoal.ARTICLE]: 'Article',
};

// ← NUOVO! Descriptions per UI
export const GOAL_DESCRIPTIONS: Record<OnboardingGoal, string> = {
  [OnboardingGoal.LINKEDIN_POST]: 'Short, engaging post (200-400 words)',
  [OnboardingGoal.LINKEDIN_ARTICLE]: 'Long-form thought leadership (800-1500 words)',
  [OnboardingGoal.NEWSLETTER]: 'Curated newsletter (1000-1500 words)',
  [OnboardingGoal.NEWSLETTER_PREMIUM]: 'Premium newsletter with research',
  [OnboardingGoal.BLOG_POST]: 'SEO-optimized blog article (1200-2000 words)',
  [OnboardingGoal.ARTICLE]: 'Generic article',
};
```

---

## 🎯 PARTE 2: WORKFLOW MAPPING

### **File: `onboarding/config/settings.py`**

**Codice Attuale**:
```python
# Default workflow mappings (goal -> CGS workflow_type)
default_workflow_mappings: dict = Field(
    default={
        "linkedin_post": "enhanced_article",        # ❌ Improprio
        "newsletter": "premium_newsletter",
        "newsletter_premium": "premium_newsletter",
        "article": "enhanced_article",
    }
)
```

**Modifiche Necessarie**:
```python
# Default workflow mappings (goal -> CGS workflow_type)
default_workflow_mappings: dict = Field(
    default={
        # ✅ NUOVO WORKFLOW GENERICO
        "linkedin_post": "onboarding_content_generator",
        "linkedin_article": "onboarding_content_generator",
        "newsletter": "onboarding_content_generator",
        "newsletter_premium": "onboarding_content_generator",
        "blog_post": "onboarding_content_generator",
        "article": "onboarding_content_generator",
    }
)

# ← NUOVO! Content type mapping
content_type_mappings: dict = Field(
    default={
        "linkedin_post": "linkedin_post",
        "linkedin_article": "linkedin_article",
        "newsletter": "newsletter",
        "newsletter_premium": "newsletter",
        "blog_post": "blog_post",
        "article": "blog_post",  # Fallback to blog_post
    }
)
```

**Nuovo Metodo**:
```python
def get_content_type(self, goal: str) -> str:
    """Map onboarding goal to content type."""
    return self.content_type_mappings.get(
        goal.lower(), "linkedin_post"  # Default fallback
    )
```

---

## 🎯 PARTE 3: PAYLOAD BUILDER

### **File: `onboarding/application/builders/payload_builder.py`**

**Codice Attuale**:
```python
def build_payload(
    self,
    session_id: UUID,
    trace_id: str,
    snapshot: CompanySnapshot,
    goal: OnboardingGoal,
    dry_run: bool = False,
    requested_provider: Optional[str] = None,
) -> CgsPayloadLinkedInPost | CgsPayloadNewsletter:
    """Build CGS payload based on goal."""
    logger.info(f"Building payload for goal: {goal}")
    
    if goal == OnboardingGoal.LINKEDIN_POST:
        return self._build_linkedin_payload(...)
    elif goal in {OnboardingGoal.NEWSLETTER, OnboardingGoal.NEWSLETTER_PREMIUM}:
        return self._build_newsletter_payload(...)
    elif goal == OnboardingGoal.ARTICLE:
        return self._build_linkedin_payload(..., is_article=True)
    else:
        raise ValueError(f"Unsupported goal: {goal}")
```

**Modifiche Necessarie**:
```python
def build_payload(
    self,
    session_id: UUID,
    trace_id: str,
    snapshot: CompanySnapshot,
    goal: OnboardingGoal,
    dry_run: bool = False,
    requested_provider: Optional[str] = None,
) -> CgsPayloadOnboardingContent:  # ← NUOVO! Payload unificato
    """Build CGS payload based on goal."""
    logger.info(f"Building payload for goal: {goal}")
    
    # ✅ NUOVO! Usa sempre il workflow generico
    return self._build_onboarding_content_payload(
        session_id=session_id,
        trace_id=trace_id,
        snapshot=snapshot,
        goal=goal,
        dry_run=dry_run,
        requested_provider=requested_provider,
    )
```

**Nuovo Metodo**:
```python
def _build_onboarding_content_payload(
    self,
    session_id: UUID,
    trace_id: str,
    snapshot: CompanySnapshot,
    goal: OnboardingGoal,
    dry_run: bool,
    requested_provider: Optional[str],
) -> CgsPayloadOnboardingContent:
    """Build unified onboarding content payload."""
    
    # Determine content type from goal
    from onboarding.config.settings import get_onboarding_settings
    settings = get_onboarding_settings()
    content_type = settings.get_content_type(goal.value)
    
    # Build content config based on content type
    content_config = self._build_content_config(content_type, snapshot)
    
    # Extract common parameters
    topic = self._extract_topic(snapshot)
    target_audience = snapshot.audience.primary or "Business professionals"
    tone = snapshot.voice.tone or "professional"
    context = self._build_context(snapshot)
    
    # Build unified input
    onboarding_input = OnboardingContentInput(
        content_type=content_type,
        topic=topic,
        client_name=snapshot.company.name,
        client_profile="onboarding",
        target_audience=target_audience,
        tone=tone,
        context=context,
        content_config=content_config,
        custom_instructions=self._build_custom_instructions(snapshot),
    )
    
    # Build metadata
    metadata = CgsPayloadMetadata(
        source="onboarding_adapter",
        dry_run=dry_run,
        requested_provider=requested_provider or "gemini",
        language="it",
    )
    
    # Build payload
    payload = CgsPayloadOnboardingContent(
        session_id=session_id,
        trace_id=trace_id,
        workflow="onboarding_content_generator",  # ← NUOVO!
        goal=goal.value,
        company_snapshot=snapshot,
        clarifying_answers=snapshot.clarifying_answers,
        input=onboarding_input,
        metadata=metadata,
    )
    
    logger.info(
        f"Onboarding content payload built: "
        f"content_type={content_type}, topic='{topic}'"
    )
    
    return payload

def _build_content_config(
    self, content_type: str, snapshot: CompanySnapshot
) -> Dict[str, Any]:
    """Build content-specific configuration."""
    
    # Extract word count from answers
    word_count = self._extract_word_count(snapshot, default=None)
    
    # Content type specific configs
    if content_type == "linkedin_post":
        return {
            "word_count": word_count or 300,
            "include_emoji": True,
            "include_hashtags": True,
            "include_cta": True,
            "max_hashtags": 5,
        }
    
    elif content_type == "linkedin_article":
        return {
            "word_count": word_count or 1200,
            "include_headings": True,
            "include_statistics": self._extract_boolean_answer(snapshot, "statistic", True),
            "include_examples": self._extract_boolean_answer(snapshot, "example", True),
            "include_sources": True,
        }
    
    elif content_type == "newsletter":
        return {
            "word_count": word_count or 1200,
            "num_sections": 4,
            "include_links": True,
            "include_cta": True,
            "format": "multi_section",
        }
    
    elif content_type == "blog_post":
        return {
            "word_count": word_count or 1500,
            "seo_optimized": True,
            "include_headings": True,
            "include_faq": True,
            "include_meta_description": True,
        }
    
    else:
        # Default config
        return {
            "word_count": word_count or 800,
        }
```

---

## 🎯 PARTE 4: CGS CONTRACTS

### **File: `onboarding/domain/cgs_contracts.py`**

**Nuovo Contract**:
```python
class OnboardingContentInput(BaseModel):
    """Unified input for onboarding content generation."""
    
    # Content type
    content_type: str = Field(
        ...,
        description="Type of content: linkedin_post, linkedin_article, newsletter, blog_post"
    )
    
    # Common fields
    topic: str = Field(..., min_length=1)
    client_name: str = Field(..., min_length=1)
    client_profile: str = Field(default="onboarding")
    target_audience: str = Field(default="Business professionals")
    tone: str = Field(default="professional")
    context: str = Field(default="")
    custom_instructions: Optional[str] = None
    
    # Content-specific configuration
    content_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Content type specific configuration"
    )


class CgsPayloadOnboardingContent(BaseModel):
    """
    Unified CGS Payload for onboarding content generation.
    
    Supports multiple content types via onboarding_content_generator workflow.
    """
    
    version: str = Field(default="2.0")
    session_id: UUID
    workflow: str = Field(default="onboarding_content_generator")
    goal: str  # Original onboarding goal
    trace_id: Optional[str] = None
    
    company_snapshot: CompanySnapshot
    clarifying_answers: Dict[str, Any] = Field(default_factory=dict)
    input: OnboardingContentInput
    metadata: CgsPayloadMetadata = Field(default_factory=CgsPayloadMetadata)
```

---

## 🎯 PARTE 5: CGS ADAPTER

### **File: `onboarding/infrastructure/adapters/cgs_adapter.py`**

**Modifiche al Metodo `_convert_to_cgs_request`**:
```python
def _convert_to_cgs_request(
    self,
    payload: CgsPayloadOnboardingContent,  # ← NUOVO! Tipo unificato
) -> Dict[str, Any]:
    """Convert onboarding payload to CGS API request format."""
    
    # Base request
    request = {
        "workflow_type": payload.workflow,  # "onboarding_content_generator"
        "client_profile": payload.input.client_profile,
    }
    
    # Add provider if specified
    if payload.metadata.requested_provider:
        request["provider"] = payload.metadata.requested_provider
        if payload.metadata.requested_provider == "gemini":
            request["model"] = "gemini-2.5-pro"
    
    # Rich context
    rich_context = {}
    
    if payload.company_snapshot:
        rich_context["company_snapshot"] = payload.company_snapshot.model_dump(mode="json")
    
    if payload.clarifying_answers:
        rich_context["clarifying_answers"] = payload.clarifying_answers
    
    # ← NUOVO! Add content type and config
    rich_context["content_type"] = payload.input.content_type
    rich_context["content_config"] = payload.input.content_config
    
    if rich_context:
        request["context"] = rich_context
    
    # Add input fields
    request.update({
        "topic": payload.input.topic,
        "client_name": payload.input.client_name,
        "target_audience": payload.input.target_audience,
        "tone": payload.input.tone,
        "context": payload.input.context,
        "custom_instructions": payload.input.custom_instructions,
    })
    
    return request
```

---

## 🎯 PARTE 6: CGS WORKFLOW HANDLER

### **File: `core/infrastructure/workflows/handlers/onboarding_content_handler.py`** (NUOVO!)

**Struttura Completa**:
```python
"""Onboarding Content Generator workflow handler."""

import logging
from typing import Any, Dict

from ..base_handler import WorkflowHandler
from ..registry import register_workflow

logger = logging.getLogger(__name__)


@register_workflow("onboarding_content_generator")
class OnboardingContentHandler(WorkflowHandler):
    """
    Generic workflow handler for onboarding content generation.
    
    Supports multiple content types:
    - linkedin_post: Short engaging post (200-400 words)
    - linkedin_article: Long-form thought leadership (800-1500 words)
    - newsletter: Multi-section newsletter (1000-1500 words)
    - blog_post: SEO-optimized blog article (1200-2000 words)
    """
    
    def __init__(self, workflow_type: str):
        super().__init__(workflow_type)
        self.workflow_type = workflow_type
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute onboarding content generation workflow."""
        
        logger.info(f"🚀 Executing {self.workflow_type}")
        
        # Extract content type from context
        content_type = context.get("context", {}).get("content_type", "linkedin_post")
        
        logger.info(f"📝 Content type: {content_type}")
        
        # Route to appropriate sub-workflow
        if content_type == "linkedin_post":
            return await self._generate_linkedin_post(context)
        elif content_type == "linkedin_article":
            return await self._generate_linkedin_article(context)
        elif content_type == "newsletter":
            return await self._generate_newsletter(context)
        elif content_type == "blog_post":
            return await self._generate_blog_post(context)
        else:
            raise ValueError(f"Unsupported content type: {content_type}")
    
    async def _generate_linkedin_post(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate LinkedIn post (200-400 words)."""
        # Implementation in next document
        pass
    
    async def _generate_linkedin_article(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate LinkedIn article (800-1500 words)."""
        # Implementation in next document
        pass
    
    async def _generate_newsletter(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate newsletter (1000-1500 words)."""
        # Implementation in next document
        pass
    
    async def _generate_blog_post(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate blog post (1200-2000 words)."""
        # Implementation in next document
        pass
```

---

## 📊 RIEPILOGO FILE COINVOLTI

| # | File | Tipo | Azione |
|---|------|------|--------|
| 1 | `onboarding/domain/models.py` | Backend | MODIFICARE (enum) |
| 2 | `onboarding/config/settings.py` | Backend | MODIFICARE (mappings) |
| 3 | `onboarding/application/builders/payload_builder.py` | Backend | MODIFICARE (metodi) |
| 4 | `onboarding/domain/cgs_contracts.py` | Backend | CREARE (nuovo contract) |
| 5 | `onboarding/infrastructure/adapters/cgs_adapter.py` | Backend | MODIFICARE (convert) |
| 6 | `onboarding-frontend/src/types/onboarding.ts` | Frontend | MODIFICARE (enum) |
| 7 | `onboarding-frontend/src/components/steps/Step1CompanyInput.tsx` | Frontend | MODIFICARE (UI) |
| 8 | `core/infrastructure/workflows/handlers/onboarding_content_handler.py` | CGS | CREARE (handler) |
| 9 | `core/infrastructure/workflows/__init__.py` | CGS | MODIFICARE (import) |

**Totale**: 9 file (2 nuovi, 7 modifiche)

---

**Fine Documento**

