# 💻 Code Examples: Onboarding System

**Versione**: 2.0  
**Data**: 2025-10-23

---

## 📦 1. Payload Building Examples

### Example 1: Company Snapshot Payload

```python
# File: onboarding/application/builders/payload_builder.py

def _build_company_snapshot_payload(
    self,
    session_id: UUID,
    trace_id: str,
    snapshot: CompanySnapshot,
    goal: OnboardingGoal,
    dry_run: bool,
    requested_provider: Optional[str],
) -> CgsPayloadOnboardingContent:
    """Build company snapshot payload."""
    
    # Build rich context with company snapshot
    rich_context = {
        "company_snapshot": snapshot.model_dump(),
    }
    
    # Build metadata
    metadata = CgsPayloadMetadata(
        source="onboarding_adapter",
        dry_run=dry_run,
        requested_provider=requested_provider or "gemini",
        language="it",
    )
    
    # Build input
    snapshot_input = OnboardingContentInput(
        topic=f"Company snapshot for {snapshot.company.name}",
        client_name=snapshot.company.name,
        context=json.dumps(rich_context, default=str),
        content_type="company_snapshot",
        content_config={},
        custom_instructions="",
    )
    
    # Build payload
    payload = CgsPayloadOnboardingContent(
        session_id=session_id,
        goal=goal.value,
        workflow="onboarding_content_generator",
        company_snapshot=snapshot,
        clarifying_answers=snapshot.clarifying_answers,
        input=snapshot_input,
        metadata=metadata,
        trace_id=trace_id,
    )
    
    logger.info(f"✅ Built company snapshot payload: {snapshot.company.name}")
    
    return payload
```

---

### Example 2: Content Generation Payload

```python
# File: onboarding/application/builders/payload_builder.py

def _build_content_generation_payload(
    self,
    session_id: UUID,
    trace_id: str,
    snapshot: CompanySnapshot,
    goal: OnboardingGoal,
    dry_run: bool,
    requested_provider: Optional[str],
) -> CgsPayloadOnboardingContent:
    """Build content generation payload."""
    
    # Get settings
    settings = get_onboarding_settings()
    
    # Map goal to content type
    content_type = settings.get_content_type(goal.value)  # → "blog_post"
    
    # Extract parameters intelligently
    topic = self._extract_topic(snapshot)
    target_audience = snapshot.audience.primary or "Business professionals"
    tone = snapshot.voice.tone or "professional"
    context = self._build_context(snapshot)
    
    # Build content config
    custom_params = self._extract_content_config_from_answers(snapshot, content_type)
    content_config = build_content_config(content_type, custom_params)
    
    # Build custom instructions
    custom_instructions = self._build_custom_instructions(snapshot, content_type)
    
    # Build input
    onboarding_input = OnboardingContentInput(
        content_type=content_type,
        topic=topic,
        client_name=snapshot.company.name,
        client_profile="onboarding",
        target_audience=target_audience,
        tone=tone,
        context=context,
        content_config=content_config,
        custom_instructions=custom_instructions,
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
        workflow="onboarding_content_generator",
        goal=goal.value,
        company_snapshot=snapshot,
        clarifying_answers=snapshot.clarifying_answers,
        input=onboarding_input,
        metadata=metadata,
    )
    
    logger.info(
        f"Content payload built: content_type={content_type}, "
        f"topic='{topic}', word_count={content_config.get('word_count')}"
    )
    
    return payload
```

---

### Example 3: Intelligent Parameter Extraction

```python
# File: onboarding/application/builders/payload_builder.py

def _extract_topic(self, snapshot: CompanySnapshot) -> str:
    """Extract topic from answers or infer from company."""
    
    # 1. Check answers for topic-related questions
    for q_id, answer in snapshot.clarifying_answers.items():
        question = next((q for q in snapshot.clarifying_questions if q.id == q_id), None)
        if question and "topic" in question.question.lower():
            return str(answer)
        if question and "focus" in question.question.lower():
            return str(answer)
    
    # 2. Infer from company offerings
    if snapshot.company.key_offerings:
        return f"{snapshot.company.key_offerings[0]} for {snapshot.audience.primary or 'businesses'}"
    
    # 3. Fallback to company description
    return snapshot.company.description[:100]


def _extract_word_count(self, snapshot: CompanySnapshot, default: int) -> int:
    """Extract word count from answers."""
    
    for q_id, answer in snapshot.clarifying_answers.items():
        question = next((q for q in snapshot.clarifying_questions if q.id == q_id), None)
        if question and "length" in question.question.lower():
            # Parse answer like "medium (400-600 words)"
            answer_str = str(answer).lower()
            if "short" in answer_str:
                return 250
            elif "medium" in answer_str:
                return 500
            elif "long" in answer_str:
                return 1000
            
            # Try to extract number
            import re
            numbers = re.findall(r'\d+', answer_str)
            if numbers:
                return int(numbers[0])
    
    return default


def _build_custom_instructions(
    self, snapshot: CompanySnapshot, content_type: str
) -> Optional[str]:
    """Build custom instructions from snapshot."""
    
    instructions = []
    
    # Add differentiators
    if snapshot.company.differentiators:
        diff_text = ", ".join(snapshot.company.differentiators[:3])
        instructions.append(f"Highlight these differentiators: {diff_text}")
    
    # Add pain points
    if snapshot.audience.pain_points:
        pain_text = ", ".join(snapshot.audience.pain_points[:2])
        instructions.append(f"Address these pain points: {pain_text}")
    
    # Add style guidelines
    if snapshot.voice.style_guidelines:
        style_text = ", ".join(snapshot.voice.style_guidelines[:2])
        instructions.append(f"Follow these style guidelines: {style_text}")
    
    return " | ".join(instructions) if instructions else None
```

---

## 🎯 2. Clarifying Questions Examples

### Example 4: Gemini Synthesis Prompt

```python
# File: onboarding/infrastructure/adapters/gemini_adapter.py

def _build_synthesis_prompt(
    self,
    brand_name: str,
    research_content: str,
    website: Optional[str] = None,
) -> str:
    """Build prompt for company snapshot synthesis."""
    
    prompt = f"""You are an expert business analyst synthesizing company research.

COMPANY: {brand_name}
WEBSITE: {website or 'Not provided'}

RESEARCH DATA:
{research_content}

YOUR TASK:
Generate a structured JSON with:
1. Company info (name, industry, description, differentiators, etc.)
2. Audience info (primary, pain_points, desired_outcomes)
3. Voice info (tone, style_guidelines)
4. Insights (positioning, key_messages, competitors)
5. **EXACTLY 3 clarifying questions**

CLARIFYING QUESTIONS RULES:
- Generate EXACTLY 3 questions (q1, q2, q3)
- Questions must be specific and actionable
- expected_response_type: "string" | "enum" | "boolean" | "number"
- For enum types: MUST provide 3-5 clear options
- For other types: set options to null

Example:
{{
  "clarifying_questions": [
    {{
      "id": "q1",
      "question": "Which product feature should we focus on?",
      "reason": "To align content with product strengths",
      "expected_response_type": "enum",
      "options": ["Feature A", "Feature B", "Feature C", "All features"],
      "required": true
    }},
    {{
      "id": "q2",
      "question": "What is the target audience's experience level?",
      "reason": "To adjust technical depth",
      "expected_response_type": "enum",
      "options": ["Beginner", "Intermediate", "Advanced"],
      "required": true
    }},
    {{
      "id": "q3",
      "question": "What is the primary content goal?",
      "reason": "To tailor content to business objectives",
      "expected_response_type": "enum",
      "options": ["Awareness", "Lead gen", "Education", "Branding"],
      "required": true
    }}
  ]
}}

Return ONLY valid JSON, no markdown.
"""
    return prompt
```

---

### Example 5: Answer Validation

```python
# File: onboarding/application/use_cases/collect_answers.py

async def execute(
    self, session: OnboardingSession, answers: Dict[str, Any]
) -> OnboardingSession:
    """Collect and validate answers."""
    
    logger.info(f"Collecting answers for session: {session.session_id}")
    
    # 1. Validate state
    if session.state != SessionState.AWAITING_USER:
        raise ValueError(f"Invalid state for collecting answers: {session.state}")
    
    # 2. Validate and add answers
    for question_id, answer in answers.items():
        # Find question
        question = next(
            (q for q in session.snapshot.clarifying_questions if q.id == question_id),
            None,
        )
        
        if not question:
            logger.warning(f"Unknown question ID: {question_id}")
            continue
        
        # Validate answer type
        self._validate_answer(question, answer)
        
        # Add answer
        session.snapshot.add_answer(question_id, answer)
    
    # 3. Check completeness
    if not session.snapshot.is_complete():
        missing = [
            q.id
            for q in session.snapshot.clarifying_questions
            if q.required and q.id not in session.snapshot.clarifying_answers
        ]
        raise ValueError(f"Missing required answers: {missing}")
    
    # 4. Update state
    session.update_state(SessionState.PAYLOAD_READY)
    
    return session


def _validate_answer(self, question, answer: Any) -> None:
    """Validate answer against question type."""
    
    expected_type = question.expected_response_type
    
    if expected_type == "boolean":
        if not isinstance(answer, bool):
            raise ValueError(f"Question {question.id} expects boolean, got {type(answer)}")
    
    elif expected_type == "number":
        if not isinstance(answer, (int, float)):
            raise ValueError(f"Question {question.id} expects number, got {type(answer)}")
    
    elif expected_type == "enum":
        if question.options and answer not in question.options:
            raise ValueError(
                f"Question {question.id} expects one of {question.options}, got {answer}"
            )
    
    elif expected_type == "string":
        if not isinstance(answer, str):
            raise ValueError(f"Question {question.id} expects string, got {type(answer)}")
```

---

## 🎨 3. Frontend Rendering Examples

### Example 6: Renderer Registration

```typescript
// File: onboarding-frontend/src/renderers/CompanySnapshotRenderer.tsx

import { rendererRegistry } from './RendererRegistry';
import CompanySnapshotCard from '../components/cards/CompanySnapshotCard';

// Data extractor with fallback cascade
const extractCompanySnapshot = (session: OnboardingSession): CompanySnapshotCardData | null => {
  let snapshot: CompanySnapshot | undefined;

  // 1. Primary: content.metadata
  snapshot = session.cgs_response?.content?.metadata?.company_snapshot;

  // 2. Fallback: root metadata
  if (!snapshot) {
    snapshot = session.cgs_response?.metadata?.company_snapshot;
  }

  // 3. Fallback: session.snapshot
  if (!snapshot) {
    snapshot = session.snapshot;
  }

  if (!snapshot) {
    console.warn('⚠️ No snapshot found');
    return null;
  }

  // Map to card format
  return companySnapshotToCard(snapshot);
};

// Wrapper component
const CompanySnapshotCardRenderer: React.FC<{
  session: OnboardingSession;
  data: CompanySnapshotCardData | null;
}> = ({ data }) => {
  if (!data) {
    return <ErrorMessage message="No snapshot available" />;
  }

  return (
    <CompanySnapshotCard
      data={data}
      onGenerateBrief={handleGenerateBrief}
      onCompareCompetitors={handleCompareCompetitors}
    />
  );
};

// Register renderer
rendererRegistry.register(
  'company_snapshot',
  CompanySnapshotCardRenderer,
  extractCompanySnapshot
);
```

---

### Example 7: Metadata-Driven Rendering

```typescript
// File: onboarding-frontend/src/components/steps/Step6Results.tsx

export const Step6Results: React.FC<Step6ResultsProps> = ({ session, onStartNew }) => {
  // 1. Extract display_type from CGS response (metadata-driven!)
  const displayType = session.cgs_response?.content?.metadata?.display_type || 'content_preview';
  
  console.log(`🎨 Rendering display_type="${displayType}"`);
  
  // 2. Get renderer from registry
  const renderer = rendererRegistry.getRenderer(displayType);
  
  // 3. Fallback if not found
  if (!renderer) {
    console.warn(`⚠️ No renderer for "${displayType}", using fallback`);
    
    const fallbackRenderer = rendererRegistry.getRenderer('content_preview');
    if (!fallbackRenderer) {
      return <ErrorMessage message="No renderer available" />;
    }
    
    const fallbackData = fallbackRenderer.dataExtractor(session);
    const FallbackComponent = fallbackRenderer.component;
    return <FallbackComponent session={session} data={fallbackData} onStartNew={onStartNew} />;
  }
  
  // 4. Extract data and render
  const data = renderer.dataExtractor(session);
  const RendererComponent = renderer.component;
  
  return <RendererComponent session={session} data={data} onStartNew={onStartNew} />;
};
```

---

## 🔧 4. Configuration Examples

### Example 8: Settings Mappings

```python
# File: onboarding/config/settings.py

class OnboardingSettings(BaseSettings):
    """Onboarding service settings."""
    
    # Workflow mappings (goal -> workflow)
    workflow_mappings: dict = Field(
        default={
            "company_snapshot": "onboarding_content_generator",
            "content_generation": "onboarding_content_generator",
        }
    )
    
    # Content type mappings (goal -> content_type)
    content_type_mappings: dict = Field(
        default={
            "company_snapshot": "company_snapshot",
            "content_generation": "blog_post",  # Most flexible generic type
        }
    )
    
    def get_workflow(self, goal: str) -> str:
        """Get workflow for goal."""
        return self.workflow_mappings.get(goal, "onboarding_content_generator")
    
    def get_content_type(self, goal: str) -> str:
        """Get content type for goal."""
        return self.content_type_mappings.get(goal, "blog_post")
```

---

**End of Examples** 🎉

