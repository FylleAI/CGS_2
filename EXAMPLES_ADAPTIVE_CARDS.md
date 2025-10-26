# 📚 Adaptive Cards - Practical Examples

## 🎯 Overview

This document provides practical examples of how to use the Adaptive Knowledge Base system.

---

## 1️⃣ Creating Cards

### Example 1.1: Create a Product Card (API)

```bash
POST /api/v1/cards
Content-Type: application/json
Authorization: Bearer {token}

{
  "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
  "card_type": "product",
  "title": "Enterprise CRM Platform",
  "description": "Full-featured CRM for enterprise sales teams",
  "category": "product",
  "tags": ["crm", "enterprise", "sales"],
  "content": {
    "name": "Enterprise CRM Platform",
    "value_proposition": "Streamline your sales process with AI-powered insights and automation",
    "features": [
      {
        "name": "AI Lead Scoring",
        "description": "Automatically prioritize leads based on conversion probability",
        "benefit": "Focus on high-value opportunities"
      },
      {
        "name": "Pipeline Automation",
        "description": "Automate repetitive tasks and workflows",
        "benefit": "Save 10+ hours per week per rep"
      }
    ],
    "differentiators": [
      "Only CRM with built-in AI forecasting",
      "Native integration with 500+ tools",
      "99.99% uptime SLA"
    ],
    "use_cases": [
      {
        "scenario": "Enterprise sales team with complex deal cycles",
        "outcome": "Reduced sales cycle by 30%"
      }
    ],
    "pricing_tier": "Enterprise"
  },
  "metrics": {
    "conversion_rate": 0.15,
    "avg_deal_size": 50000,
    "sales_cycle_days": 45
  },
  "confidence_score": 0.9
}
```

**Response:**
```json
{
  "card_id": "123e4567-e89b-12d3-a456-426614174000",
  "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
  "card_type": "product",
  "title": "Enterprise CRM Platform",
  "version": 1,
  "is_active": true,
  "created_at": "2025-10-25T10:00:00Z",
  "created_by": "user:john@company.com",
  "quality_score": null
}
```

---

### Example 1.2: Create a Persona Card (Python)

```python
from onboarding.infrastructure.repositories.context_card_repository import ContextCardRepository
from onboarding.domain.card_models import PersonaCard, PersonaContent

# Initialize repository
repo = ContextCardRepository(supabase_client)

# Create persona content
persona_content = PersonaContent(
    name="Enterprise IT Director",
    demographics={
        "job_title": "IT Director / VP of IT",
        "company_size": "1000-5000 employees",
        "industry": ["Technology", "Finance", "Healthcare"]
    },
    psychographics={
        "pain_points": [
            "Managing multiple disconnected systems",
            "Security compliance requirements",
            "Budget constraints with growing demands"
        ],
        "goals": [
            "Consolidate tech stack",
            "Improve team productivity",
            "Reduce operational costs"
        ],
        "motivations": [
            "Career advancement",
            "Team success",
            "Innovation"
        ],
        "objections": [
            "Implementation complexity",
            "Change management",
            "ROI uncertainty"
        ]
    },
    communication={
        "preferred_channels": ["LinkedIn", "Email", "Webinars"],
        "language_style": "Professional, data-driven, ROI-focused",
        "content_preferences": ["Case studies", "Whitepapers", "Product demos"]
    }
)

# Create card
card = await repo.create_card(
    tenant_id="550e8400-e29b-41d4-a716-446655440000",
    card_type="persona",
    title="Enterprise IT Director",
    content=persona_content.model_dump(),
    category="audience",
    tags=["enterprise", "it", "decision-maker"],
    created_by="agent:research_specialist"
)

print(f"Created persona card: {card['card_id']}")
```

---

## 2️⃣ Updating Cards

### Example 2.1: Update Card Content (API)

```bash
PATCH /api/v1/cards/123e4567-e89b-12d3-a456-426614174000
Content-Type: application/json

{
  "content": {
    "features": [
      {
        "name": "AI Lead Scoring",
        "description": "Automatically prioritize leads based on conversion probability",
        "benefit": "Focus on high-value opportunities"
      },
      {
        "name": "Pipeline Automation",
        "description": "Automate repetitive tasks and workflows",
        "benefit": "Save 10+ hours per week per rep"
      },
      {
        "name": "Real-time Analytics",
        "description": "Live dashboards with actionable insights",
        "benefit": "Make data-driven decisions instantly"
      }
    ]
  },
  "updated_by": "user:sarah@company.com"
}
```

---

### Example 2.2: Update Metrics (Python)

```python
# Update performance metrics
await repo.update_card(
    card_id="123e4567-e89b-12d3-a456-426614174000",
    updates={
        "metrics": {
            "conversion_rate": 0.18,  # Improved from 0.15
            "avg_deal_size": 55000,   # Increased
            "sales_cycle_days": 42    # Reduced from 45
        }
    },
    updated_by="automation:performance_tracker"
)
```

---

## 3️⃣ Creating Relationships

### Example 3.1: Link Product to Persona (API)

```bash
POST /api/v1/cards/123e4567-e89b-12d3-a456-426614174000/relationships
Content-Type: application/json

{
  "target_card_id": "persona-card-id-here",
  "relationship_type": "references",
  "strength": 0.9,
  "metadata": {
    "reason": "This product is designed specifically for this persona"
  }
}
```

---

### Example 3.2: Create Insight from Multiple Cards (Python)

```python
from onboarding.infrastructure.repositories.card_relationship_repository import CardRelationshipRepository

# Create insight card
insight_card = await card_repo.create_card(
    tenant_id="550e8400-e29b-41d4-a716-446655440000",
    card_type="insight",
    title="Video content drives 3x engagement for IT personas",
    content={
        "description": "Analysis of 100+ content pieces shows video content significantly outperforms text for IT decision-makers",
        "evidence": [
            "Video content: 15% avg engagement rate",
            "Text content: 5% avg engagement rate",
            "Webinars: 25% conversion rate"
        ],
        "recommendations": [
            "Prioritize video content for IT audience",
            "Create product demo videos",
            "Host monthly webinars"
        ],
        "confidence": 0.85
    },
    created_by="agent:insight_generator"
)

# Link to source cards
relationship_repo = CardRelationshipRepository(supabase_client)

# Link to persona card
await relationship_repo.create_relationship(
    source_card_id=insight_card['card_id'],
    target_card_id="persona-card-id",
    relationship_type="derived_from",
    strength=1.0,
    created_by="agent:insight_generator"
)

# Link to performance card
await relationship_repo.create_relationship(
    source_card_id=insight_card['card_id'],
    target_card_id="performance-card-id",
    relationship_type="derived_from",
    strength=1.0,
    created_by="agent:insight_generator"
)
```

---

## 4️⃣ Submitting Feedback

### Example 4.1: User Thumbs Up (Frontend)

```typescript
// User clicks thumbs up on a card
const handleThumbsUp = async (cardId: string) => {
  await fetch(`/api/v1/cards/${cardId}/feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      source_type: 'user_rating',
      source_id: currentUser.id,
      feedback_type: 'validation',
      feedback_data: {
        rating: 'positive',
        comment: 'This card is accurate and helpful'
      }
    })
  });
  
  toast.success('Thanks for your feedback!');
};
```

---

### Example 4.2: Agent Updates Card with Reasoning (Python)

```python
from onboarding.infrastructure.repositories.card_feedback_repository import CardFeedbackRepository

feedback_repo = CardFeedbackRepository(supabase_client)

# Agent updates card and creates feedback entry
await feedback_repo.create_feedback(
    card_id="123e4567-e89b-12d3-a456-426614174000",
    tenant_id="550e8400-e29b-41d4-a716-446655440000",
    source_type="agent_update",
    source_id="research_specialist",
    feedback_type="enhancement",
    feedback_data={
        "field_updated": "content.differentiators",
        "old_value": ["Only CRM with built-in AI forecasting"],
        "new_value": [
            "Only CRM with built-in AI forecasting",
            "Native integration with 500+ tools"
        ],
        "reason": "Discovered new competitive advantage from recent market research",
        "confidence": 0.85
    }
)
```

---

## 5️⃣ Tracking Performance

### Example 5.1: Track Content Generation Event (Python)

```python
from onboarding.infrastructure.repositories.card_performance_repository import CardPerformanceRepository

perf_repo = CardPerformanceRepository(supabase_client)

# Track that content was generated using this card
await perf_repo.create_event(
    card_id="product-card-id",
    tenant_id="550e8400-e29b-41d4-a716-446655440000",
    event_type="content_generated",
    event_data={
        "content_type": "linkedin_post",
        "content_id": "post-123",
        "workflow_run_id": "run-456",
        "channel": "linkedin"
    },
    workflow_run_id="run-456"
)
```

---

### Example 5.2: Track Engagement Event (API)

```bash
POST /api/v1/cards/product-card-id/performance
Content-Type: application/json

{
  "event_type": "engagement",
  "event_data": {
    "content_id": "post-123",
    "channel": "linkedin",
    "engagement_type": "click"
  },
  "engagement_rate": 0.12
}
```

---

## 6️⃣ Agent Integration

### Example 6.1: Agent Reads Cards for Context (Python)

```python
from core.infrastructure.tools.context_card_tool import ContextCardTool

# Initialize tool
card_tool = ContextCardTool(
    supabase_client=supabase,
    agent_name="copywriter"
)

# Agent retrieves relevant cards
cards = await card_tool.get_cards(
    tenant_id="550e8400-e29b-41d4-a716-446655440000",
    card_type="persona",
    tags=["enterprise"]
)

# Use cards in prompt
persona_context = "\n".join([
    f"Target Persona: {card['title']}\n"
    f"Pain Points: {', '.join(card['content']['psychographics']['pain_points'])}\n"
    f"Preferred Style: {card['content']['communication']['language_style']}"
    for card in cards
])

prompt = f"""
Write a LinkedIn post for our Enterprise CRM product.

{persona_context}

Make it compelling and address their pain points.
"""
```

---

### Example 6.2: Agent Creates Card from Research (Python)

```python
# Agent creates competitor card from research
competitor_card = await card_tool.create_card(
    tenant_id="550e8400-e29b-41d4-a716-446655440000",
    card_type="competitor",
    title="Competitor X - Salesforce",
    content={
        "name": "Salesforce",
        "positioning": "Market leader in CRM",
        "messaging": [
            "Customer 360",
            "AI-powered insights",
            "Ecosystem of apps"
        ],
        "strengths": [
            "Brand recognition",
            "Large ecosystem",
            "Enterprise features"
        ],
        "weaknesses": [
            "Complex pricing",
            "Steep learning curve",
            "Expensive for SMBs"
        ],
        "opportunities": [
            "Target SMBs with simpler solution",
            "Emphasize ease of use",
            "Competitive pricing"
        ]
    },
    category="competitive_intelligence",
    tags=["competitor", "crm", "enterprise"],
    reason="Discovered from market research and competitive analysis"
)
```

---

## 7️⃣ Auto-Evolution

### Example 7.1: Quality Score Calculation (SQL)

```sql
-- Calculate quality score for a card
SELECT calculate_quality_score(
    '123e4567-e89b-12d3-a456-426614174000',  -- card_id
    0.6,  -- performance weight
    0.3,  -- feedback weight
    0.1   -- confidence weight
);

-- Update card with new quality score
UPDATE context_cards
SET quality_score = calculate_quality_score(card_id)
WHERE card_id = '123e4567-e89b-12d3-a456-426614174000';
```

---

### Example 7.2: Auto-Update Trigger (Python)

```python
from onboarding.workers.card_evolution_worker import CardEvolutionWorker

worker = CardEvolutionWorker(supabase_client)

# Process pending feedback
await worker.process_feedback_queue(
    tenant_id="550e8400-e29b-41d4-a716-446655440000"
)

# Check for cards needing updates
low_quality_cards = await worker.find_cards_needing_review(
    tenant_id="550e8400-e29b-41d4-a716-446655440000",
    quality_threshold=0.5
)

for card in low_quality_cards:
    # Create review task
    await worker.create_review_task(
        card_id=card['card_id'],
        reason=f"Quality score dropped to {card['quality_score']}"
    )
    
    # Notify user
    await worker.notify_user(
        user_id=card['created_by'],
        message=f"Card '{card['title']}' needs review"
    )
```

---

## 8️⃣ Frontend Usage

### Example 8.1: Interactive Card Component (React)

```typescript
import { InteractiveCard } from '@/components/cards/InteractiveCard';
import { useCardStore } from '@/store/cardsStore';

const ProductCardView: React.FC = () => {
  const { cards, updateCard, submitFeedback } = useCardStore();
  const productCard = cards.find(c => c.card_type === 'product');
  
  const handleUpdate = async (updates: Partial<ContextCard>) => {
    await updateCard(productCard.card_id, updates);
  };
  
  const handleFeedback = async (feedback: CardFeedback) => {
    await submitFeedback(productCard.card_id, feedback);
  };
  
  return (
    <InteractiveCard
      card={productCard}
      editable={true}
      onUpdate={handleUpdate}
      onFeedback={handleFeedback}
      showMetrics={true}
      showRelationships={true}
    />
  );
};
```

---

### Example 8.2: Card Editor (React)

```typescript
import { ProductCardEditor } from '@/components/cards/editors/ProductCardEditor';

const EditProductCard: React.FC<{ card: ProductCard }> = ({ card }) => {
  const [content, setContent] = useState(card.content);
  const [isSaving, setIsSaving] = useState(false);
  
  const handleSave = async () => {
    setIsSaving(true);
    try {
      await fetch(`/api/v1/cards/${card.card_id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content,
          updated_by: `user:${currentUser.id}`
        })
      });
      toast.success('Card updated successfully!');
    } catch (error) {
      toast.error('Failed to update card');
    } finally {
      setIsSaving(false);
    }
  };
  
  return (
    <ProductCardEditor
      content={content}
      onChange={setContent}
      onSave={handleSave}
      isSaving={isSaving}
    />
  );
};
```

---

## 9️⃣ Querying Cards

### Example 9.1: Find Related Cards (SQL)

```sql
-- Get all cards related to a product card
WITH RECURSIVE card_graph AS (
    -- Base case: direct relationships
    SELECT 
        r.target_card_id as card_id,
        r.relationship_type,
        r.strength,
        1 as depth
    FROM card_relationships r
    WHERE r.source_card_id = '123e4567-e89b-12d3-a456-426614174000'
    
    UNION
    
    -- Recursive case: relationships of relationships (up to depth 2)
    SELECT 
        r.target_card_id,
        r.relationship_type,
        r.strength,
        cg.depth + 1
    FROM card_relationships r
    JOIN card_graph cg ON r.source_card_id = cg.card_id
    WHERE cg.depth < 2
)
SELECT DISTINCT
    c.*,
    cg.relationship_type,
    cg.strength,
    cg.depth
FROM card_graph cg
JOIN context_cards c ON cg.card_id = c.card_id
WHERE c.is_active = true
ORDER BY cg.depth, cg.strength DESC;
```

---

### Example 9.2: Search Cards (Python)

```python
# Full-text search
results = await repo.search_cards(
    tenant_id="550e8400-e29b-41d4-a716-446655440000",
    query="enterprise sales automation",
    card_types=["product", "persona"],
    limit=10
)

# Filter by tags
enterprise_cards = await repo.list_cards(
    tenant_id="550e8400-e29b-41d4-a716-446655440000",
    tags=["enterprise"],
    active_only=True
)

# Get top performers
top_cards = await repo.list_cards(
    tenant_id="550e8400-e29b-41d4-a716-446655440000",
    order_by="quality_score",
    order_direction="desc",
    limit=10
)
```

---

## 🎯 Best Practices

### 1. Card Granularity
- ✅ **DO**: Create one card per distinct concept
- ❌ **DON'T**: Cram multiple products into one card

### 2. Relationships
- ✅ **DO**: Link related cards to build knowledge graph
- ❌ **DON'T**: Create circular dependencies

### 3. Feedback
- ✅ **DO**: Provide specific, actionable feedback
- ❌ **DON'T**: Submit vague feedback like "bad card"

### 4. Performance Tracking
- ✅ **DO**: Track all content generation and engagement events
- ❌ **DON'T**: Forget to link events to source cards

### 5. Quality Scores
- ✅ **DO**: Regularly recalculate quality scores
- ❌ **DON'T**: Rely solely on initial confidence scores

---

**Last Updated**: 2025-10-25  
**Version**: 1.0

