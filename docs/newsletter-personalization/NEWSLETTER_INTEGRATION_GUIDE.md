# 🔗 Newsletter Personalization - Integration Guide

**Project**: Personalized Weekly Newsletter System  
**Version**: 1.0  
**Date**: 2025-10-25  

---

## 📋 OVERVIEW

This document describes how the Newsletter Personalization system integrates with existing systems:
1. Onboarding Flow
2. Adaptive Knowledge Base (Cards)
3. Publishing Systems (HubSpot/LinkedIn)
4. Existing Newsletter Workflow (Siebert)

---

## 1️⃣ INTEGRATION WITH ONBOARDING FLOW

### Current Onboarding Flow

```
User Input → Research Company → Synthesize Snapshot → 
→ Clarifying Questions → User Answers → Execute Workflow → 
→ Deliver Content → Done
```

### New Flow with Newsletter Opt-in

```
User Input → Research Company → Synthesize Snapshot → 
→ Clarifying Questions → User Answers → Execute Workflow → 
→ Deliver Content → Show Adaptive Cards →
→ [NEW] Newsletter Opt-in Modal →
→ [NEW] Create Subscription (if opted in) →
→ [NEW] Send Welcome Email →
→ [NEW] Schedule First Newsletter →
→ Done
```

---

### Implementation

#### Step 1: Modify Onboarding Completion Handler

**File**: `onboarding/application/use_cases/execute_onboarding.py`

```python
# EXISTING CODE
async def execute(self, session: OnboardingSession) -> OnboardingResult:
    # ... existing workflow execution ...
    
    # Deliver content
    if session.user_email and self.enable_auto_delivery:
        await self._deliver_content(session, result)
    
    # NEW: Trigger newsletter opt-in flow
    if result.is_successful():
        await self._trigger_newsletter_opt_in(session)
    
    return result

# NEW METHOD
async def _trigger_newsletter_opt_in(self, session: OnboardingSession):
    """
    Trigger newsletter opt-in flow after successful onboarding.
    
    This sets a flag in session metadata that the frontend
    can use to show the opt-in modal.
    """
    session.metadata["newsletter_opt_in_eligible"] = True
    session.metadata["newsletter_opt_in_shown"] = False
    
    await self.session_repo.update(session)
```

---

#### Step 2: Frontend Integration

**File**: `onboarding-frontend/src/components/OnboardingComplete.tsx`

```typescript
import { NewsletterOptInModal } from './NewsletterOptInModal';

export const OnboardingComplete: React.FC = () => {
  const [showNewsletterModal, setShowNewsletterModal] = useState(false);
  const { session } = useOnboardingSession();
  
  useEffect(() => {
    // Show newsletter opt-in modal if eligible
    if (session?.metadata?.newsletter_opt_in_eligible && 
        !session?.metadata?.newsletter_opt_in_shown) {
      setShowNewsletterModal(true);
    }
  }, [session]);
  
  const handleNewsletterOptIn = async (subscribed: boolean) => {
    // Mark as shown
    await updateSessionMetadata(session.session_id, {
      newsletter_opt_in_shown: true,
      newsletter_subscribed: subscribed,
    });
    
    setShowNewsletterModal(false);
  };
  
  return (
    <>
      {/* Existing onboarding complete UI */}
      <AdaptiveCardsDisplay cards={session.adaptive_cards} />
      
      {/* NEW: Newsletter opt-in modal */}
      <NewsletterOptInModal
        open={showNewsletterModal}
        onClose={() => handleNewsletterOptIn(false)}
        onSubscribe={() => handleNewsletterOptIn(true)}
        userEmail={session.user_email}
        companySnapshotId={session.snapshot.snapshot_id}
      />
    </>
  );
};
```

---

#### Step 3: Auto-populate Subscription from CompanySnapshot

**File**: `newsletter/application/use_cases/create_subscription.py`

```python
async def execute(
    self,
    tenant_id: UUID,
    user_email: str,
    company_snapshot_id: Optional[UUID],
    preferences: SubscriptionPreferences,
) -> NewsletterSubscription:
    """
    Create subscription with data from CompanySnapshot.
    """
    
    # Load company snapshot
    company_snapshot = None
    if company_snapshot_id:
        company_snapshot = await self.company_context_repo.find_by_id(
            company_snapshot_id
        )
    
    # Auto-populate topics of interest from snapshot
    topics_of_interest = []
    if company_snapshot:
        # Extract from snapshot
        topics_of_interest = [
            company_snapshot.company.industry,
            *company_snapshot.company.key_offerings[:3],
        ]
        
        # Auto-discover competitors if not already done
        if not company_snapshot.insights.competitors:
            competitors = await self.competitor_service.discover_competitors(
                tenant_id=tenant_id,
                company_snapshot=company_snapshot,
            )
    
    # Create subscription
    subscription = NewsletterSubscription(
        tenant_id=tenant_id,
        user_email=user_email,
        company_snapshot_id=company_snapshot_id,
        preferences=preferences,
        topics_of_interest=topics_of_interest,
    )
    
    await self.subscription_repo.save(subscription)
    
    return subscription
```

---

## 2️⃣ INTEGRATION WITH ADAPTIVE CARDS

### Bidirectional Sync

```
Newsletter Content ←→ Adaptive Cards
```

**Direction 1**: Newsletter → Cards (Create/Update cards from newsletter content)  
**Direction 2**: Cards → Newsletter (Use cards to inform personalization)

---

### Implementation

#### Direction 1: Newsletter → Cards

**File**: `newsletter/application/services/adaptive_cards_sync_service.py`

```python
"""
Sync newsletter content with Adaptive Cards.
"""
from uuid import UUID
from typing import List
from newsletter.domain.models import PersonalizedNewsletter
from adaptive_cards.domain.models import ContextCard


class AdaptiveCardsSyncService:
    """Sync newsletter content with Adaptive Cards."""
    
    async def sync_newsletter_to_cards(
        self,
        newsletter: PersonalizedNewsletter,
        tenant_id: UUID,
    ) -> List[ContextCard]:
        """
        Create/Update Adaptive Cards from newsletter content.
        
        Creates:
        - Competitor Cards (from newsletter.competitors)
        - Trend Cards (from newsletter.trends)
        - News Cards (from newsletter.news)
        """
        
        created_cards = []
        
        # Create Competitor Cards
        for competitor in newsletter.competitors:
            card = await self.card_service.create_or_update_card(
                tenant_id=tenant_id,
                card_type="competitor",
                title=competitor["name"],
                content={
                    "competitor_name": competitor["name"],
                    "recent_activity": competitor["activity"],
                    "source_url": competitor["source_url"],
                    "detected_at": newsletter.generated_at.isoformat(),
                },
                source_type="newsletter",
                source_id=str(newsletter.newsletter_id),
                version=1,
            )
            created_cards.append(card)
        
        # Create Trend Cards
        for trend in newsletter.trends:
            card = await self.card_service.create_or_update_card(
                tenant_id=tenant_id,
                card_type="trend",
                title=trend["name"],
                content={
                    "trend_name": trend["name"],
                    "description": trend["description"],
                    "momentum": trend["momentum"],
                    "relevance_score": trend.get("relevance_score"),
                    "detected_at": newsletter.generated_at.isoformat(),
                },
                source_type="newsletter",
                source_id=str(newsletter.newsletter_id),
                version=1,
            )
            created_cards.append(card)
        
        return created_cards
```

**Trigger**: After newsletter generation, before delivery

```python
# In GenerateNewsletterUseCase
async def execute(self, subscription_id: UUID) -> NewsletterEdition:
    # ... generate newsletter ...
    
    # Sync to Adaptive Cards
    await self.cards_sync_service.sync_newsletter_to_cards(
        newsletter=personalized_newsletter,
        tenant_id=subscription.tenant_id,
    )
    
    # ... continue with delivery ...
```

---

#### Direction 2: Cards → Newsletter

**Use Case**: Use existing Adaptive Cards to inform newsletter personalization

```python
# In PersonalizedNewsletterHandler
async def prepare_context(self, variables: dict) -> dict:
    """
    Prepare context for newsletter generation.
    
    Include relevant Adaptive Cards in context.
    """
    
    subscription_id = variables["subscription_id"]
    subscription = await self.subscription_repo.find_by_id(subscription_id)
    
    # Load existing Adaptive Cards
    cards = await self.card_service.get_cards_for_tenant(
        tenant_id=subscription.tenant_id,
        card_types=["competitor", "trend", "persona", "product"],
        is_active=True,
    )
    
    # Add cards to context
    variables["adaptive_cards"] = [
        {
            "type": card.card_type,
            "title": card.title,
            "content": card.content,
            "performance": card.metrics,
        }
        for card in cards
    ]
    
    return variables
```

---

## 3️⃣ INTEGRATION WITH PUBLISHING SYSTEMS

### Content Repurposing Flow

```
Newsletter Content →
  → LinkedIn Post (Monday)
  → HubSpot Blog Post (Wednesday)
  → Twitter Thread (Friday)
```

---

### Implementation

#### Step 1: Extract Sections for Publishing

**File**: `newsletter/application/services/content_repurposing_service.py`

```python
"""
Repurpose newsletter content for publishing platforms.
"""
from newsletter.domain.models import PersonalizedNewsletter


class ContentRepurposingService:
    """Repurpose newsletter content for different platforms."""
    
    def extract_linkedin_posts(
        self,
        newsletter: PersonalizedNewsletter,
    ) -> List[dict]:
        """
        Extract LinkedIn posts from newsletter.
        
        Strategy:
        - Top competitor activity → LinkedIn post
        - Top market trend → LinkedIn post
        - Key insight → LinkedIn post
        """
        
        posts = []
        
        # Post 1: Top competitor activity
        if newsletter.competitors:
            top_competitor = newsletter.competitors[0]
            posts.append({
                "platform": "linkedin",
                "content_type": "post",
                "title": f"Competitor Update: {top_competitor['name']}",
                "body": f"""
                🎯 Competitor Intelligence
                
                {top_competitor['name']} just {top_competitor['activity']}
                
                What this means for your business:
                {self._generate_implication(top_competitor)}
                
                #CompetitiveIntelligence #MarketTrends
                """,
                "source_url": top_competitor.get("source_url"),
            })
        
        # Post 2: Top market trend
        if newsletter.trends:
            top_trend = newsletter.trends[0]
            posts.append({
                "platform": "linkedin",
                "content_type": "post",
                "title": f"Market Trend: {top_trend['name']}",
                "body": f"""
                📈 Emerging Trend Alert
                
                {top_trend['name']} is {top_trend['momentum']}
                
                {top_trend['description']}
                
                Is your business ready for this shift?
                
                #MarketTrends #BusinessStrategy
                """,
            })
        
        return posts
    
    def extract_hubspot_blog_post(
        self,
        newsletter: PersonalizedNewsletter,
    ) -> dict:
        """
        Extract HubSpot blog post from newsletter.
        
        Strategy:
        - Combine all sections into comprehensive blog post
        - Add introduction and conclusion
        - Format for SEO
        """
        
        return {
            "platform": "hubspot",
            "content_type": "blog_post",
            "title": f"Weekly Market Intelligence: {newsletter.generated_at.strftime('%B %d, %Y')}",
            "body": f"""
            <h2>Introduction</h2>
            <p>{newsletter.intro}</p>
            
            <h2>Competitor Updates</h2>
            {self._format_competitors_for_blog(newsletter.competitors)}
            
            <h2>Market Trends</h2>
            {self._format_trends_for_blog(newsletter.trends)}
            
            <h2>Industry News</h2>
            {self._format_news_for_blog(newsletter.news)}
            
            <h2>Key Insights</h2>
            <p>{newsletter.insights}</p>
            
            <h2>Conclusion</h2>
            <p>Stay ahead of the competition with weekly intelligence delivered to your inbox.</p>
            """,
            "tags": ["market-intelligence", "competitive-analysis", "industry-trends"],
            "meta_description": f"Weekly market intelligence covering competitor updates, emerging trends, and industry news.",
        }
```

---

#### Step 2: Trigger Publishing After Newsletter Delivery

```python
# In NewsletterDeliveryService
async def send_newsletter(
    self,
    subscription: NewsletterSubscription,
    newsletter: PersonalizedNewsletter,
) -> NewsletterDelivery:
    # Send newsletter via email
    delivery = await self._send_via_brevo(subscription, newsletter)
    
    # NEW: Trigger content repurposing (async)
    if subscription.preferences.get("enable_content_repurposing"):
        await self._trigger_content_repurposing(newsletter)
    
    return delivery

async def _trigger_content_repurposing(
    self,
    newsletter: PersonalizedNewsletter,
):
    """
    Trigger content repurposing to LinkedIn/HubSpot.
    
    This creates publishing jobs that will be executed
    by the publishing system.
    """
    
    # Extract LinkedIn posts
    linkedin_posts = self.repurposing_service.extract_linkedin_posts(newsletter)
    
    for post in linkedin_posts:
        await self.publishing_service.schedule_post(
            platform="linkedin",
            content=post["body"],
            scheduled_for=datetime.utcnow() + timedelta(hours=2),
        )
    
    # Extract HubSpot blog post
    blog_post = self.repurposing_service.extract_hubspot_blog_post(newsletter)
    
    await self.publishing_service.schedule_post(
        platform="hubspot",
        content_type="blog_post",
        content=blog_post["body"],
        title=blog_post["title"],
        scheduled_for=datetime.utcnow() + timedelta(days=2),
    )
```

---

## 4️⃣ INTEGRATION WITH EXISTING NEWSLETTER WORKFLOW (Siebert)

### Reuse Strategy

**Reuse**:
- ✅ Workflow template structure (3-5 tasks)
- ✅ HTML email builder
- ✅ Brand voice integration
- ✅ Cost tracking
- ✅ Workflow handler pattern

**Customize**:
- ❌ Task prompts (personalized vs generic)
- ❌ Input variables (subscription vs topic)
- ❌ Output format (personalized sections vs generic)

---

### Implementation

#### Extend Siebert Workflow Template

**File**: `core/infrastructure/workflows/templates/personalized_newsletter.json`

```json
{
  "name": "personalized_newsletter",
  "version": "1.0",
  "description": "Personalized weekly newsletter generation",
  "handler": "personalized_newsletter_handler",
  "extends": "siebert_newsletter_html",
  "variables": [
    {
      "name": "subscription_id",
      "type": "string",
      "required": true
    },
    {
      "name": "company_snapshot",
      "type": "object",
      "required": true
    },
    {
      "name": "competitors",
      "type": "array",
      "required": true
    },
    {
      "name": "trends",
      "type": "array",
      "required": true
    }
  ],
  "tasks": [
    {
      "id": "task1_context_setup",
      "name": "Company Context & Brand Voice Setup",
      "agent": "rag_specialist",
      "dependencies": [],
      "prompt_id": "personalized_newsletter_task1_context_setup"
    },
    {
      "id": "task2_intelligence_research",
      "name": "Competitor & Trend Research",
      "agent": "research_specialist",
      "dependencies": ["task1_context_setup"],
      "prompt_id": "personalized_newsletter_task2_intelligence_research"
    },
    {
      "id": "task3_content_curation",
      "name": "Content Curation & Prioritization",
      "agent": "curator",
      "dependencies": ["task2_intelligence_research"],
      "prompt_id": "personalized_newsletter_task3_content_curation"
    },
    {
      "id": "task4_newsletter_assembly",
      "name": "Personalized Newsletter Assembly",
      "agent": "copywriter",
      "dependencies": ["task3_content_curation"],
      "prompt_id": "personalized_newsletter_task4_newsletter_assembly"
    },
    {
      "id": "task5_html_builder",
      "name": "HTML Email Builder",
      "agent": "html_email_builder",
      "dependencies": ["task4_newsletter_assembly"],
      "prompt_id": "siebert_newsletter_html_task5_html_builder"
    }
  ]
}
```

**Note**: Task 5 reuses the existing Siebert HTML builder!

---

## 🎯 INTEGRATION CHECKLIST

### Onboarding Integration

- [ ] Modify `execute_onboarding.py` to trigger opt-in
- [ ] Create `NewsletterOptInModal` component
- [ ] Update `OnboardingComplete` component
- [ ] Test opt-in flow end-to-end
- [ ] Track opt-in conversion rate

### Adaptive Cards Integration

- [ ] Create `AdaptiveCardsSyncService`
- [ ] Trigger sync after newsletter generation
- [ ] Use cards in newsletter context
- [ ] Test bidirectional sync
- [ ] Monitor card performance

### Publishing Integration

- [ ] Create `ContentRepurposingService`
- [ ] Implement LinkedIn post extraction
- [ ] Implement HubSpot blog extraction
- [ ] Schedule publishing jobs
- [ ] Test cross-platform publishing

### Siebert Workflow Integration

- [ ] Create `personalized_newsletter.json` template
- [ ] Reuse HTML email builder
- [ ] Create custom prompts
- [ ] Test workflow execution
- [ ] Compare cost with Siebert workflow

---

**Status**: ✅ **INTEGRATION GUIDE COMPLETE**  
**Last Updated**: 2025-10-25

