# 🏢 ONBOARDING MICROSERVICE - Struttura e Responsabilità

## 📂 File Structure (Solo Tua Area)

```
fylle-core-pulse/
└── app/
    └── onboarding/                         # ✅ TUA AREA - Microservice isolato
        ├── domain/                         # Domain layer
        │   ├── models.py                   # 🔥 CORE - CompanySnapshot, OnboardingSession
        │   ├── contracts.py                # CGS integration contracts
        │   └── content_types.py            # Content type enums
        │
        ├── use_cases/                      # 🔥 CORE - Business logic
        │   ├── create_session.py           # 1. Crea sessione onboarding
        │   ├── research_company.py         # 2. Research (Perplexity)
        │   ├── synthesize_snapshot.py      # 3. Synthesis (Gemini)
        │   ├── collect_answers.py          # 4. Raccoglie risposte utente
        │   └── execute_onboarding.py       # 5. Esegue workflow CGS
        │
        ├── adapters/                       # External service adapters
        │   ├── perplexity_adapter.py       # Perplexity API client
        │   ├── gemini_adapter.py           # Gemini API client
        │   ├── brevo_adapter.py            # Brevo email client
        │   └── cgs_adapter.py              # 🔥 CORE - CGS backend client
        │
        ├── builders/                       # Payload builders
        │   └── payload_builder.py          # 🔥 CORE - Costruisce payload CGS
        │
        ├── api/                            # API endpoints
        │   ├── endpoints.py                # Onboarding REST API
        │   └── schemas.py                  # Request/Response schemas
        │
        └── repository/                     # Data access (usa DatabaseManager)
            └── onboarding_repository.py    # CRUD operations
```

---

## 🎯 RESPONSABILITÀ CHIAVE

### **Onboarding è un MICROSERVICE ISOLATO:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    ONBOARDING MICROSERVICE                       │
├─────────────────────────────────────────────────────────────────┤
│  INPUT:  Brand name, Website, Goal, Email                       │
│  OUTPUT: Structured CGS response (metadata-driven)               │
│                                                                  │
│  FLOW:                                                           │
│  1. Research company (Perplexity)                                │
│  2. Synthesize CompanySnapshot (Gemini)                          │
│  3. Generate clarification questions                             │
│  4. Collect user answers                                         │
│  5. Build CGS payload                                            │
│  6. Call CGS workflow                                            │
│  7. Return structured response                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                       CGS BACKEND                                │
├─────────────────────────────────────────────────────────────────┤
│  INPUT:  CGS payload (brand, audience, tone, goal)               │
│  OUTPUT: Content + Metadata (display_type, structured data)      │
│                                                                  │
│  FLOW:                                                           │
│  1. Execute workflow (onboarding_content)                        │
│  2. Run tasks with agents                                        │
│  3. Generate content                                             │
│  4. Return structured response                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔑 USE CASES (Business Logic)

### **1. CreateSession**

```python
# app/onboarding/use_cases/create_session.py

from app.onboarding.domain.models import OnboardingSession, OnboardingGoal
from app.onboarding.repository.onboarding_repository import OnboardingRepository

class CreateSessionUseCase:
    def __init__(self, repository: OnboardingRepository):
        self.repository = repository
    
    async def execute(
        self,
        brand_name: str,
        website: str,
        goal: OnboardingGoal,
        email: str,
        tenant_id: str  # ← Fornito da middleware
    ) -> OnboardingSession:
        """
        Crea una nuova sessione di onboarding.
        """
        session = OnboardingSession(
            brand_name=brand_name,
            website=website,
            goal=goal,
            email=email,
            tenant_id=tenant_id,
            state="CREATED"
        )
        
        # Salva in database
        await self.repository.create(session)
        
        return session
```

---

### **2. ResearchCompany**

```python
# app/onboarding/use_cases/research_company.py

from app.onboarding.adapters.perplexity_adapter import PerplexityAdapter
from app.onboarding.domain.models import CompanySnapshot

class ResearchCompanyUseCase:
    def __init__(self, perplexity: PerplexityAdapter):
        self.perplexity = perplexity
    
    async def execute(
        self,
        brand_name: str,
        website: str
    ) -> dict:
        """
        Research company usando Perplexity.
        
        Ritorna raw research data (non ancora CompanySnapshot).
        """
        # Build research query
        query = f"""
        Research the company "{brand_name}" (website: {website}).
        
        Provide:
        1. Company overview and mission
        2. Products/services
        3. Target audience
        4. Industry and competitors
        5. Recent news and updates
        6. Brand voice and tone (from website content)
        """
        
        # Call Perplexity
        research_result = await self.perplexity.research(query)
        
        return {
            "brand_name": brand_name,
            "website": website,
            "research_data": research_result.content,
            "sources": research_result.sources
        }
```

---

### **3. SynthesizeSnapshot**

```python
# app/onboarding/use_cases/synthesize_snapshot.py

from app.onboarding.adapters.gemini_adapter import GeminiAdapter
from app.onboarding.domain.models import CompanySnapshot

class SynthesizeSnapshotUseCase:
    def __init__(self, gemini: GeminiAdapter):
        self.gemini = gemini
    
    async def execute(
        self,
        research_data: dict
    ) -> CompanySnapshot:
        """
        Sintetizza CompanySnapshot da research data usando Gemini.
        """
        # Build synthesis prompt
        prompt = f"""
        Based on the following research data, create a structured company snapshot.
        
        Research Data:
        {research_data['research_data']}
        
        Extract and structure:
        1. Company info (name, website, industry, description)
        2. Voice & Tone (professional/casual, formal/informal, technical/simple)
        3. Target Audience (demographics, pain points, goals)
        4. Positioning (unique value proposition, differentiators)
        5. Recent News (latest updates, achievements)
        
        Return as JSON matching CompanySnapshot schema.
        """
        
        # Call Gemini
        result = await self.gemini.generate(
            prompt=prompt,
            response_format="json"
        )
        
        # Parse to CompanySnapshot
        snapshot = CompanySnapshot.model_validate_json(result.content)
        
        return snapshot
```

---

### **4. CollectAnswers**

```python
# app/onboarding/use_cases/collect_answers.py

from app.onboarding.repository.onboarding_repository import OnboardingRepository

class CollectAnswersUseCase:
    def __init__(self, repository: OnboardingRepository):
        self.repository = repository
    
    async def execute(
        self,
        session_id: str,
        answers: dict
    ) -> None:
        """
        Raccoglie risposte utente e aggiorna sessione.
        """
        # Carica sessione
        session = await self.repository.get(session_id)
        
        # Valida risposte
        self._validate_answers(answers, session.goal)
        
        # Aggiorna sessione
        session.answers = answers
        session.state = "ANSWERS_COLLECTED"
        
        # Salva
        await self.repository.update(session)
```

---

### **5. ExecuteOnboarding (🔥 CRITICO)**

```python
# app/onboarding/use_cases/execute_onboarding.py

from app.onboarding.adapters.cgs_adapter import CGSAdapter
from app.onboarding.builders.payload_builder import PayloadBuilder
from app.onboarding.repository.onboarding_repository import OnboardingRepository

class ExecuteOnboardingUseCase:
    def __init__(
        self,
        repository: OnboardingRepository,
        cgs_adapter: CGSAdapter,
        payload_builder: PayloadBuilder
    ):
        self.repository = repository
        self.cgs_adapter = cgs_adapter
        self.payload_builder = payload_builder
    
    async def execute(
        self,
        session_id: str
    ) -> dict:
        """
        Esegue workflow CGS e ritorna risultato strutturato.
        
        Questo è il PONTE tra Onboarding e CGS.
        """
        # 1. Carica sessione
        session = await self.repository.get(session_id)
        
        # 2. Build CGS payload
        cgs_payload = self.payload_builder.build(
            goal=session.goal,
            snapshot=session.company_snapshot,
            answers=session.answers
        )
        
        # 3. Call CGS workflow
        cgs_response = await self.cgs_adapter.execute_workflow(
            workflow_id="onboarding_content",
            payload=cgs_payload,
            tenant_id=session.tenant_id  # ← Passa tenant_id a CGS
        )
        
        # 4. Aggiorna sessione
        session.cgs_run_id = cgs_response["session_id"]
        session.cgs_response = cgs_response  # ← Salva response completo
        session.state = "COMPLETED"
        
        await self.repository.update(session)
        
        # 5. Ritorna response strutturato
        return {
            "session_id": session.session_id,
            "cgs_run_id": session.cgs_run_id,
            "cgs_response": cgs_response,  # ← Include metadata per rendering
            "content_title": cgs_response["content"]["title"],
            "content_preview": cgs_response["content"]["body"][:200],
            "word_count": cgs_response["content"]["word_count"],
            "display_type": cgs_response["content"]["metadata"]["display_type"]  # ← CHIAVE!
        }
```

---

## 🔌 ADAPTERS (External Services)

### **CGS Adapter (🔥 CRITICO)**

```python
# app/onboarding/adapters/cgs_adapter.py

import httpx
from typing import Dict, Any

class CGSAdapter:
    """
    Adapter per chiamare CGS backend.
    
    CGS è un servizio SEPARATO che esegue workflow agentic.
    """
    
    def __init__(self, cgs_base_url: str):
        self.cgs_base_url = cgs_base_url
        self.client = httpx.AsyncClient(timeout=300.0)  # 5 min timeout
    
    async def execute_workflow(
        self,
        workflow_id: str,
        payload: dict,
        tenant_id: str
    ) -> dict:
        """
        Esegue workflow CGS.
        
        Args:
            workflow_id: ID del workflow (es. "onboarding_content")
            payload: Payload CGS (brand, audience, tone, goal)
            tenant_id: Tenant ID (per multi-tenancy)
        
        Returns:
            CGS response con content + metadata
        """
        url = f"{self.cgs_base_url}/api/v1/workflows/execute"
        
        headers = {
            "X-Tenant-ID": tenant_id,  # ← Multi-tenancy header
            "Content-Type": "application/json"
        }
        
        request_body = {
            "workflow_id": workflow_id,
            "input_data": payload
        }
        
        # Call CGS
        response = await self.client.post(
            url,
            json=request_body,
            headers=headers
        )
        
        response.raise_for_status()
        
        return response.json()
```

---

## 🏗️ PAYLOAD BUILDER (🔥 CRITICO)

```python
# app/onboarding/builders/payload_builder.py

from app.onboarding.domain.models import OnboardingGoal, CompanySnapshot

class PayloadBuilder:
    """
    Costruisce payload CGS da sessione onboarding.
    
    Questo è il CONTRATTO tra Onboarding e CGS.
    """
    
    def build(
        self,
        goal: OnboardingGoal,
        snapshot: CompanySnapshot,
        answers: dict
    ) -> dict:
        """
        Costruisce payload CGS.
        
        Il payload include:
        - Brand info (da snapshot)
        - Audience (da snapshot + answers)
        - Tone (da snapshot + answers)
        - Goal-specific data
        """
        # Base payload (comune a tutti i goal)
        payload = {
            "brand": {
                "name": snapshot.company.name,
                "website": snapshot.company.website,
                "industry": snapshot.company.industry,
                "description": snapshot.company.description
            },
            "voice_tone": {
                "tone": snapshot.voice_tone.tone,
                "style": snapshot.voice_tone.style,
                "language_complexity": snapshot.voice_tone.language_complexity
            },
            "target_audience": {
                "demographics": snapshot.target_audience.demographics,
                "pain_points": snapshot.target_audience.pain_points,
                "goals": snapshot.target_audience.goals
            }
        }
        
        # Goal-specific payload
        if goal == OnboardingGoal.COMPANY_SNAPSHOT:
            payload.update(self._build_company_snapshot_payload(snapshot, answers))
        
        elif goal == OnboardingGoal.LINKEDIN_POST:
            payload.update(self._build_linkedin_post_payload(snapshot, answers))
        
        elif goal == OnboardingGoal.BLOG_ARTICLE:
            payload.update(self._build_blog_article_payload(snapshot, answers))
        
        elif goal == OnboardingGoal.ANALYTICS_DASHBOARD:
            payload.update(self._build_analytics_dashboard_payload(snapshot, answers))
        
        return payload
    
    def _build_company_snapshot_payload(
        self,
        snapshot: CompanySnapshot,
        answers: dict
    ) -> dict:
        """Payload specifico per Company Snapshot."""
        return {
            "goal": "company_snapshot",
            "positioning": {
                "unique_value_proposition": snapshot.positioning.unique_value_proposition,
                "differentiators": snapshot.positioning.differentiators
            },
            "recent_news": snapshot.recent_news,
            "additional_context": answers.get("additional_context", "")
        }
    
    def _build_linkedin_post_payload(
        self,
        snapshot: CompanySnapshot,
        answers: dict
    ) -> dict:
        """Payload specifico per LinkedIn Post."""
        return {
            "goal": "linkedin_post",
            "topic": answers.get("topic"),
            "cta": answers.get("cta"),
            "hashtags": answers.get("hashtags", [])
        }
    
    # ... altri goal-specific builders
```

---

## 📡 API ENDPOINTS

```python
# app/onboarding/api/endpoints.py

from fastapi import APIRouter, Depends
from app.onboarding.use_cases import *
from app.core.tenant_context import get_current_tenant_id

router = APIRouter(prefix="/api/v1/onboarding", tags=["onboarding"])

@router.post("/start")
async def start_onboarding(
    request: StartOnboardingRequest,
    tenant_id: str = Depends(get_current_tenant_id),  # ← Fornito da middleware
    create_session: CreateSessionUseCase = Depends(),
    research_company: ResearchCompanyUseCase = Depends(),
    synthesize_snapshot: SynthesizeSnapshotUseCase = Depends()
):
    """
    Step 1: Avvia onboarding.
    
    1. Crea sessione
    2. Research company (Perplexity)
    3. Synthesize snapshot (Gemini)
    4. Ritorna snapshot per review
    """
    # 1. Crea sessione
    session = await create_session.execute(
        brand_name=request.brand_name,
        website=request.website,
        goal=request.goal,
        email=request.email,
        tenant_id=tenant_id
    )
    
    # 2. Research
    research_data = await research_company.execute(
        brand_name=request.brand_name,
        website=request.website
    )
    
    # 3. Synthesize
    snapshot = await synthesize_snapshot.execute(research_data)
    
    # 4. Salva snapshot in sessione
    session.company_snapshot = snapshot
    await repository.update(session)
    
    return {
        "session_id": session.session_id,
        "company_snapshot": snapshot.model_dump()
    }


@router.post("/{session_id}/answers")
async def submit_answers(
    session_id: str,
    request: SubmitAnswersRequest,
    collect_answers: CollectAnswersUseCase = Depends(),
    execute_onboarding: ExecuteOnboardingUseCase = Depends()
):
    """
    Step 2: Raccoglie risposte ed esegue workflow CGS.
    
    1. Salva risposte
    2. Build CGS payload
    3. Call CGS workflow
    4. Ritorna risultato strutturato
    """
    # 1. Salva risposte
    await collect_answers.execute(
        session_id=session_id,
        answers=request.answers
    )
    
    # 2. Esegui workflow CGS
    result = await execute_onboarding.execute(session_id)
    
    return result


@router.get("/{session_id}")
async def get_session_details(
    session_id: str,
    repository: OnboardingRepository = Depends()
):
    """
    Ritorna dettagli completi sessione (include cgs_response).
    """
    session = await repository.get(session_id)
    
    return {
        "session_id": session.session_id,
        "state": session.state,
        "company_snapshot": session.company_snapshot.model_dump() if session.company_snapshot else None,
        "cgs_response": session.cgs_response,  # ← Include metadata per rendering
        "created_at": session.created_at,
        "updated_at": session.updated_at
    }
```

---

## 🎯 COME RAGIONARE

### **Onboarding è un PONTE:**

```
Frontend → Onboarding Microservice → CGS Backend
```

**Responsabilità Onboarding:**
- ✅ Research company (Perplexity)
- ✅ Synthesize snapshot (Gemini)
- ✅ Collect user input
- ✅ Build CGS payload
- ✅ Call CGS workflow
- ✅ Return structured response

**Responsabilità CGS:**
- ✅ Execute workflow (task orchestration)
- ✅ Run agents (content generation)
- ✅ Return content + metadata

**Responsabilità Frontend:**
- ✅ Wizard UI
- ✅ Display snapshot for review
- ✅ Collect answers
- ✅ Render results (metadata-driven)

---

## ✅ CHECKLIST: Onboarding Microservice

- [ ] **Isolato da CGS** (comunicazione via HTTP)
- [ ] **Tenant-aware** (passa tenant_id a CGS)
- [ ] **Payload builder generico** (supporta tutti i goal)
- [ ] **Response strutturato** (include metadata per rendering)
- [ ] **Error handling** (gestisce errori Perplexity, Gemini, CGS)
- [ ] **Timeout appropriati** (CGS può richiedere 2-5 minuti)

---

**Ora passiamo al Frontend elastico?** 🚀

