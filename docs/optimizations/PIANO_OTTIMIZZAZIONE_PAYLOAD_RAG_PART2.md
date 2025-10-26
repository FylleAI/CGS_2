# 📋 PIANO OTTIMIZZAZIONE: Payload Arricchito + RAG Integration (PARTE 2)

**Continua da**: `PIANO_OTTIMIZZAZIONE_PAYLOAD_RAG.md`

---

## 🛠️ IMPLEMENTAZIONE (Continua)

### Task 3: Modificare `StartOnboardingUseCase` per RAG Lookup

**File**: `onboarding/application/use_cases/start_onboarding.py`

```python
class StartOnboardingUseCase:
    def __init__(
        self,
        perplexity: PerplexityAdapter,
        gemini: GeminiSynthesisAdapter,
        repository: OnboardingRepository,
        context_repository: CompanyContextRepository,  # NUOVO
    ):
        self.perplexity = perplexity
        self.gemini = gemini
        self.repository = repository
        self.context_repository = context_repository  # NUOVO
    
    async def execute(
        self,
        brand_name: str,
        website: Optional[str],
        goal: OnboardingGoal,
        user_email: Optional[str] = None,
    ) -> OnboardingSession:
        # 1. Create session
        session = OnboardingSession(
            brand_name=brand_name,
            website=website,
            goal=goal,
            user_email=user_email,
        )
        
        # 2. Check for existing context (RAG)
        existing_context = await self.context_repository.find_by_company_name(
            company_name=brand_name,
            max_age_days=30  # Configurable
        )
        
        if existing_context:
            logger.info(f"✅ RAG HIT: Found context for {brand_name} (v{existing_context['version']})")
            
            # Load snapshot from existing context
            session.snapshot = CompanySnapshot(**existing_context["company_snapshot"])
            session.company_context_id = existing_context["context_id"]
            session.update_state(SessionState.AWAITING_USER)
            
            # Increment usage counter
            await self.context_repository.increment_usage(existing_context["context_id"])
            
            # Save session
            await self.repository.save_session(session)
            
            return session
        
        # 3. No existing context → Create new one
        logger.info(f"❌ RAG MISS: No context for {brand_name}, creating new")
        
        # Research (Perplexity)
        session.update_state(SessionState.RESEARCHING)
        await self.repository.save_session(session)
        
        research_data = await self.perplexity.research_company(
            brand_name=brand_name,
            website=website,
        )
        
        # Synthesis (Gemini)
        session.update_state(SessionState.SYNTHESIZING)
        await self.repository.save_session(session)
        
        snapshot = await self.gemini.synthesize_snapshot(
            brand_name=brand_name,
            research_data=research_data,
            goal=goal,
        )
        
        session.snapshot = snapshot
        session.update_state(SessionState.AWAITING_USER)
        
        # Save session
        await self.repository.save_session(session)
        
        # NOTE: Context will be saved AFTER user answers
        # (in ExecuteOnboardingUseCase)
        
        return session
```

---

### Task 4: Salvare Context dopo Risposte Utente

**File**: `onboarding/application/use_cases/execute_onboarding.py`

```python
class ExecuteOnboardingUseCase:
    def __init__(
        self,
        payload_builder: PayloadBuilder,
        cgs: CgsAdapter,
        repository: OnboardingRepository,
        context_repository: CompanyContextRepository,  # NUOVO
    ):
        self.payload_builder = payload_builder
        self.cgs = cgs
        self.repository = repository
        self.context_repository = context_repository  # NUOVO
    
    async def execute(
        self,
        session: OnboardingSession,
        dry_run: bool = False,
        requested_provider: Optional[str] = None,
    ) -> ResultEnvelope:
        # Validate
        if not session.snapshot or not session.snapshot.is_complete():
            raise ValueError("Session snapshot is incomplete")
        
        # 1. Save company context (if not already saved from RAG)
        if not session.company_context_id:
            logger.info(f"💾 Saving new company context for {session.brand_name}")
            
            context = await self.context_repository.create_context(
                company_name=session.brand_name,
                company_display_name=session.brand_name,
                website=session.website,
                snapshot=session.snapshot,
                source_session_id=session.session_id,
            )
            
            session.company_context_id = context["context_id"]
            logger.info(f"✅ Context saved: {context['context_id']} (v{context['version']})")
            
            await self.repository.save_session(session)
        else:
            logger.info(f"♻️ Reusing existing context: {session.company_context_id}")
        
        # 2. Build payload (ENHANCED)
        payload = self.payload_builder.build_payload(
            session_id=session.session_id,
            trace_id=session.trace_id,
            snapshot=session.snapshot,
            goal=session.goal,
            dry_run=dry_run,
            requested_provider=requested_provider,
        )
        
        session.cgs_payload = payload.model_dump(mode="json")
        await self.repository.save_session(session)
        
        # 3. Execute CGS workflow
        session.update_state(SessionState.EXECUTING)
        await self.repository.update_session_state(
            session.session_id, SessionState.EXECUTING
        )
        
        result = await self.cgs.execute_workflow(payload)
        
        # 4. Store result
        session.cgs_run_id = result.cgs_run_id
        session.cgs_response = result.model_dump(mode="json")
        
        if result.status == "completed":
            session.update_state(SessionState.DELIVERING)
        else:
            session.update_state(SessionState.FAILED)
            session.error_message = result.error.get("message") if result.error else "Unknown error"
        
        await self.repository.save_session(session)
        
        return result
```

---

### Task 5: Modificare `CgsAdapter` per Passare Rich Context

**File**: `onboarding/infrastructure/adapters/cgs_adapter.py`

```python
def _convert_to_cgs_request(
    self,
    payload: CgsPayloadLinkedInPost | CgsPayloadNewsletter,
) -> Dict[str, Any]:
    """Convert onboarding payload to CGS API request format (ENHANCED)."""
    
    # Base request
    request = {
        "workflow_type": payload.workflow,
        "client_profile": payload.input.client_profile,
    }
    
    # Add provider if specified
    if payload.metadata.requested_provider:
        request["provider"] = payload.metadata.requested_provider
        if payload.metadata.requested_provider == "gemini":
            request["model"] = "gemini-2.5-pro"
    
    # Map based on workflow type
    if isinstance(payload, CgsPayloadLinkedInPost):
        request.update({
            # Parametri estratti (come prima)
            "topic": payload.input.topic,
            "client_name": payload.input.client_name,
            "target_audience": payload.input.target_audience,
            "tone": payload.input.tone,
            "target_word_count": payload.input.target_word_count,
            "include_statistics": payload.input.include_statistics,
            "include_examples": payload.input.include_examples,
            "include_sources": payload.input.include_sources,
            "context": payload.input.context,
            "custom_instructions": payload.input.custom_instructions,
            
            # ✨ NUOVO: Rich context completo
            "company_snapshot": payload.company_snapshot.model_dump(mode="json"),
            "clarifying_answers": payload.clarifying_answers,
        })
        
        logger.info(f"📦 Sending ENHANCED payload to CGS:")
        logger.info(f"  - Snapshot size: {len(str(payload.company_snapshot))} chars")
        logger.info(f"  - Answers: {len(payload.clarifying_answers)} questions")
    
    elif isinstance(payload, CgsPayloadNewsletter):
        request.update({
            # Parametri estratti
            "topic": payload.input.topic,
            "client_name": payload.input.client_name,
            "target_audience": payload.input.target_audience,
            "tone": payload.input.tone,
            "sections": payload.input.sections,
            "context": payload.input.context,
            "custom_instructions": payload.input.custom_instructions,
            
            # ✨ NUOVO: Rich context completo
            "company_snapshot": payload.company_snapshot.model_dump(mode="json"),
            "clarifying_answers": payload.clarifying_answers,
        })
    
    return request
```

---

### Task 6: Aggiornare Agenti CGS per Usare Rich Context

**File**: `data/profiles/onboarding/agents/researcher.yaml`

```yaml
name: researcher
role: Research Specialist
is_active: true
workflows:
  - enhanced_article
  - premium_newsletter

system_prompt: |
  You are a research specialist for {client_name}.
  
  Your task is to research the topic: "{topic}"
  Target audience: {target_audience}
  Tone: {tone}
  
  ## Company Context (Basic)
  {context}
  
  ## 🎯 Rich Company Information (ENHANCED)
  {% if company_snapshot %}
  
  **Company Details:**
  - Industry: {{ company_snapshot.company.industry }}
  - Description: {{ company_snapshot.company.description }}
  - Key Offerings: {{ company_snapshot.company.key_offerings | join(', ') }}
  - Differentiators: {{ company_snapshot.company.differentiators | join(', ') }}
  
  **Target Audience:**
  - Primary: {{ company_snapshot.audience.primary }}
  {% if company_snapshot.audience.pain_points %}
  - Pain Points: {{ company_snapshot.audience.pain_points | join(', ') }}
  {% endif %}
  {% if company_snapshot.audience.demographics %}
  - Demographics: {{ company_snapshot.audience.demographics }}
  {% endif %}
  
  **Voice & Style:**
  - Tone: {{ company_snapshot.voice.tone }}
  {% if company_snapshot.voice.style_guidelines %}
  - Style Guidelines: {{ company_snapshot.voice.style_guidelines | join(', ') }}
  {% endif %}
  {% if company_snapshot.voice.forbidden_phrases %}
  - ⚠️ NEVER USE: {{ company_snapshot.voice.forbidden_phrases | join(', ') }}
  {% endif %}
  
  **Key Insights:**
  - Positioning: {{ company_snapshot.insights.positioning }}
  {% if company_snapshot.insights.key_messages %}
  - Key Messages: {{ company_snapshot.insights.key_messages | join(', ') }}
  {% endif %}
  {% if company_snapshot.insights.content_opportunities %}
  - Content Opportunities: {{ company_snapshot.insights.content_opportunities | join(', ') }}
  {% endif %}
  
  {% endif %}
  
  ## 💬 User Preferences
  {% if clarifying_answers %}
  The user has provided these specific preferences:
  {% for question_id, answer in clarifying_answers.items() %}
  - {{ answer }}
  {% endfor %}
  {% endif %}
  
  {custom_instructions}
  
  **Research Guidelines:**
  - Find credible sources that align with the company's positioning
  - Focus on topics that address the target audience's pain points
  - Prioritize content opportunities identified in the insights
  - Ensure sources support the key messages

tools:
  - perplexity_search

provider_override: null  # Usa Perplexity (sonar-pro)
```

**File**: `data/profiles/onboarding/agents/writer.yaml`

```yaml
name: writer
role: Content Writer
is_active: true
workflows:
  - enhanced_article
  - premium_newsletter

system_prompt: |
  You are a professional content writer for {client_name}.
  
  Write about: "{topic}"
  Target audience: {target_audience}
  Tone: {tone}
  Target word count: {target_word_count}
  
  ## 🎯 Rich Company Information (ENHANCED)
  {% if company_snapshot %}
  
  **Company Differentiators (HIGHLIGHT THESE):**
  {% for diff in company_snapshot.company.differentiators %}
  - ✨ {{ diff }}
  {% endfor %}
  
  **Audience Pain Points (ADDRESS THESE):**
  {% if company_snapshot.audience.pain_points %}
  {% for pain in company_snapshot.audience.pain_points %}
  - 🎯 {{ pain }}
  {% endfor %}
  {% endif %}
  
  **Voice Guidelines (FOLLOW STRICTLY):**
  - Tone: {{ company_snapshot.voice.tone }}
  {% if company_snapshot.voice.style_guidelines %}
  - Style: {{ company_snapshot.voice.style_guidelines | join(', ') }}
  {% endif %}
  
  **Key Messages to Incorporate:**
  {% if company_snapshot.insights.key_messages %}
  {% for message in company_snapshot.insights.key_messages %}
  - 💡 {{ message }}
  {% endfor %}
  {% endif %}
  
  **⛔ FORBIDDEN PHRASES (NEVER USE):**
  {% if company_snapshot.voice.forbidden_phrases %}
  {% for phrase in company_snapshot.voice.forbidden_phrases %}
  - "{{ phrase }}"
  {% endfor %}
  {% endif %}
  
  **Positioning Statement:**
  {{ company_snapshot.insights.positioning }}
  
  {% endif %}
  
  {% if include_statistics %}
  ✅ Include relevant statistics and data to support your points.
  {% endif %}
  
  {% if include_examples %}
  ✅ Include concrete examples and case studies.
  {% endif %}
  
  {% if include_sources %}
  ✅ Cite credible sources for all claims.
  {% endif %}
  
  {% if custom_instructions %}
  **Additional Instructions:**
  {custom_instructions}
  {% endif %}
  
  **Writing Checklist:**
  - [ ] Addresses at least one audience pain point
  - [ ] Highlights at least one company differentiator
  - [ ] Incorporates at least one key message
  - [ ] Follows voice and style guidelines
  - [ ] Avoids all forbidden phrases
  - [ ] Aligns with positioning statement

tools:
  - llm_generate

provider_override: gemini
model_override: gemini-2.5-pro
```

---

## 📊 RIEPILOGO MODIFICHE

### File da Creare (Nuovi)
1. `onboarding/infrastructure/database/supabase_schema_contexts.sql` - Schema tabella
2. `onboarding/infrastructure/repositories/company_context_repository.py` - Repository
3. `onboarding/api/models.py` - Response models (CompanyContextResponse, etc.)

### File da Modificare (Esistenti)
1. `onboarding/application/use_cases/start_onboarding.py` - RAG lookup
2. `onboarding/application/use_cases/execute_onboarding.py` - Save context
3. `onboarding/infrastructure/adapters/cgs_adapter.py` - Pass rich context
4. `onboarding/api/endpoints.py` - Nuovi endpoints per contexts
5. `onboarding/domain/models.py` - Aggiungere `company_context_id` field
6. `data/profiles/onboarding/agents/researcher.yaml` - Rich prompts
7. `data/profiles/onboarding/agents/writer.yaml` - Rich prompts

### Dependency Injection
```python
# onboarding/api/dependencies.py

def get_context_repository() -> CompanyContextRepository:
    """Get company context repository."""
    supabase_client = get_supabase_client()
    return CompanyContextRepository(supabase_client)

def get_start_onboarding_use_case() -> StartOnboardingUseCase:
    """Get start onboarding use case with RAG support."""
    return StartOnboardingUseCase(
        perplexity=get_perplexity_adapter(),
        gemini=get_gemini_adapter(),
        repository=get_repository(),
        context_repository=get_context_repository(),  # NUOVO
    )

def get_execute_onboarding_use_case() -> ExecuteOnboardingUseCase:
    """Get execute onboarding use case with context saving."""
    return ExecuteOnboardingUseCase(
        payload_builder=get_payload_builder(),
        cgs=get_cgs_adapter(),
        repository=get_repository(),
        context_repository=get_context_repository(),  # NUOVO
    )
```

---

## 🎯 ESEMPIO COMPLETO: Prima vs Dopo

### PRIMA (Senza RAG)

**Sessione 1** (Peterlegwood):
```
1. User input → Perplexity research (30s, $0.005)
2. Gemini synthesis (10s, $0.002)
3. User answers
4. CGS execution con parametri limitati
   - topic, audience, tone, context (3 campi)
   - NO differentiators, pain_points, key_messages
5. Contenuto generato (qualità: 7/10)
```

**Sessione 2** (Peterlegwood, 1 settimana dopo):
```
1. User input → Perplexity research (30s, $0.005) ← DUPLICATO!
2. Gemini synthesis (10s, $0.002) ← DUPLICATO!
3. User answers
4. CGS execution con parametri limitati
5. Contenuto generato (qualità: 7/10)
```

**Totale**: 80s, $0.014, qualità 7/10

---

### DOPO (Con RAG)

**Sessione 1** (Peterlegwood):
```
1. User input → Check RAG (0.1s) → NOT FOUND
2. Perplexity research (30s, $0.005)
3. Gemini synthesis (10s, $0.002)
4. Save to company_contexts ✅
5. User answers
6. CGS execution con RICH CONTEXT
   - topic, audience, tone, context
   - + company_snapshot completo
   - + clarifying_answers complete
   - Agenti usano differentiators, pain_points, key_messages
7. Contenuto generato (qualità: 9/10) ← MIGLIORE!
```

**Sessione 2** (Peterlegwood, 1 settimana dopo):
```
1. User input → Check RAG (0.1s) → FOUND ✅
2. Load snapshot from company_contexts (0.2s)
3. Skip Perplexity ← RISPARMIO!
4. Skip Gemini ← RISPARMIO!
5. User answers
6. CGS execution con RICH CONTEXT
7. Contenuto generato (qualità: 9/10)
```

**Totale Sessione 1**: 40s, $0.007, qualità 9/10  
**Totale Sessione 2**: 5s, $0.000, qualità 9/10  

**Risparmio**: 75s (94%), $0.007 (100% su sessione 2), +2 punti qualità

---

## ✅ CONCLUSIONI

### Benefici Chiave

1. **🚀 Performance**
   - Sessioni ricorrenti: da 80s → 5s (94% più veloce)
   - Eliminazione ricerca duplicata

2. **💰 Costi**
   - Risparmio 100% su Perplexity per sessioni ricorrenti
   - ROI positivo dopo 2 sessioni per stessa azienda

3. **✨ Qualità**
   - Agenti hanno accesso a tutti i dati raccolti
   - Contenuto più personalizzato e allineato al brand
   - Rispetto di style guidelines e forbidden phrases

4. **📊 Riutilizzo**
   - Context salvato e versionato
   - Possibilità di refresh manuale
   - Analytics su usage patterns

### Prossimi Passi

1. **Review del piano** con team
2. **Prioritizzazione tasks** (quali fare prima?)
3. **Stima effort** (giorni/persona)
4. **Setup environment** (staging database)
5. **Kick-off implementazione**

---

**Fine Piano Parte 2** 🎉


