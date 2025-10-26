# 🏗️ Newsletter Personalizzata - Architettura Completa

**Project**: Personalized Weekly Newsletter System  
**Version**: 1.0  
**Date**: 2025-10-25  
**Status**: Design Phase ✅

---

## 📐 SYSTEM ARCHITECTURE

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER JOURNEY                                 │
│                                                                  │
│  Onboarding → Adaptive Cards → Newsletter Opt-in →              │
│  → Preference Setup → Weekly Newsletter → Engagement Tracking   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  NEWSLETTER SYSTEM ARCHITECTURE                  │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Subscription │  │ Intelligence │  │  Generation  │         │
│  │  Management  │→ │   Engine     │→ │   Pipeline   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│         ↓                  ↓                  ↓                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Scheduling  │  │   Delivery   │  │  Analytics   │         │
│  │   & Cron     │→ │   (Brevo)    │→ │  & Feedback  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🧩 COMPONENT ARCHITECTURE

### 1. Subscription Management Layer

**Purpose**: Manage user subscriptions, preferences, and opt-in/opt-out flow

**Components**:

```python
# Domain Models
class NewsletterSubscription(BaseModel):
    subscription_id: UUID
    tenant_id: UUID
    user_id: UUID
    user_email: str
    company_snapshot_id: UUID
    status: SubscriptionStatus  # active, paused, cancelled
    frequency: Frequency  # weekly, biweekly, monthly
    preferred_day: DayOfWeek  # monday, tuesday, etc.
    preferred_time: time  # 09:00, 14:00, etc.
    topics_of_interest: List[str]  # competitors, trends, news, insights
    unsubscribe_token: str
    created_at: datetime
    updated_at: datetime
    last_sent_at: Optional[datetime]

class SubscriptionPreferences(BaseModel):
    include_competitors: bool = True
    include_trends: bool = True
    include_news: bool = True
    include_insights: bool = True
    max_competitors: int = 5
    max_trends: int = 3
    content_length: str = "medium"  # short, medium, long
    format: str = "html"  # html, plain_text
```

**Use Cases**:
- `CreateSubscriptionUseCase`: Create subscription after onboarding
- `UpdatePreferencesUseCase`: Update user preferences
- `UnsubscribeUseCase`: Handle unsubscribe requests
- `PauseSubscriptionUseCase`: Temporarily pause newsletter
- `ReactivateSubscriptionUseCase`: Reactivate paused subscription

**API Endpoints**:
```
POST   /api/v1/newsletters/subscribe
PUT    /api/v1/newsletters/subscriptions/{id}/preferences
POST   /api/v1/newsletters/subscriptions/{id}/pause
POST   /api/v1/newsletters/subscriptions/{id}/reactivate
DELETE /api/v1/newsletters/unsubscribe/{token}
GET    /api/v1/newsletters/subscriptions/{id}
```

---

### 2. Intelligence Engine Layer

**Purpose**: Gather and analyze competitor activities, market trends, and industry news

**Components**:

#### 2.1 Competitor Research Service

```python
class CompetitorResearchService:
    """
    Automated competitor discovery and monitoring.
    """
    
    async def discover_competitors(
        self,
        company_snapshot: CompanySnapshot,
    ) -> List[Competitor]:
        """
        Discover competitors using Perplexity.
        
        Query: "Who are the main competitors of {company_name} 
                in the {industry} industry?"
        """
    
    async def research_competitor_activities(
        self,
        competitor: Competitor,
        timeframe: str = "last 7 days",
    ) -> List[CompetitorActivity]:
        """
        Research recent competitor activities.
        
        Query: "What are the recent news, product launches, 
                and updates from {competitor_name}?"
        """
    
    async def analyze_competitive_landscape(
        self,
        company_snapshot: CompanySnapshot,
        competitors: List[Competitor],
    ) -> CompetitiveLandscape:
        """
        Analyze competitive positioning.
        """
```

#### 2.2 Market Trend Service

```python
class MarketTrendService:
    """
    Identify and track market trends.
    """
    
    async def identify_trends(
        self,
        industry: str,
        timeframe: str = "last 30 days",
    ) -> List[MarketTrend]:
        """
        Identify emerging trends in industry.
        
        Query: "What are the emerging trends in the {industry} 
                industry in the last 30 days?"
        """
    
    async def score_trend_relevance(
        self,
        trend: MarketTrend,
        company_snapshot: CompanySnapshot,
    ) -> float:
        """
        Score trend relevance (0-1) for specific company.
        """
    
    async def track_trend_momentum(
        self,
        trend_id: UUID,
    ) -> TrendMomentum:
        """
        Track trend momentum over time (growing, stable, declining).
        """
```

#### 2.3 Industry News Aggregator

```python
class IndustryNewsAggregator:
    """
    Aggregate industry-specific news.
    """
    
    async def aggregate_news(
        self,
        industry: str,
        keywords: List[str],
        timeframe: str = "last 7 days",
    ) -> List[NewsArticle]:
        """
        Aggregate news from multiple sources.
        """
    
    async def filter_by_relevance(
        self,
        news: List[NewsArticle],
        company_snapshot: CompanySnapshot,
    ) -> List[NewsArticle]:
        """
        Filter news by relevance to company.
        """
```

---

### 3. Content Generation Pipeline

**Purpose**: Generate personalized newsletter content

**Workflow**:

```
Step 1: Data Collection
  ├─ Fetch subscription preferences
  ├─ Load company snapshot
  ├─ Research competitor activities (last 7 days)
  ├─ Identify relevant trends
  └─ Aggregate industry news

Step 2: Content Curation
  ├─ Score content by relevance
  ├─ Deduplicate content
  ├─ Select top N items per category
  └─ Order by priority

Step 3: Newsletter Generation
  ├─ Build newsletter structure
  ├─ Generate personalized intro
  ├─ Generate competitor section
  ├─ Generate trends section
  ├─ Generate news section
  ├─ Generate insights section
  └─ Generate CTA

Step 4: Quality Assurance
  ├─ Validate content length
  ├─ Check for broken links
  ├─ Verify personalization
  └─ Apply brand voice

Step 5: Formatting
  ├─ Convert to HTML
  ├─ Apply email template
  ├─ Add unsubscribe link
  └─ Generate plain text version
```

**Workflow Template** (Reuse Siebert):

```json
{
  "name": "personalized_newsletter",
  "version": "1.0",
  "description": "Personalized weekly newsletter generation",
  "handler": "personalized_newsletter_handler",
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
    },
    {
      "name": "news",
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
      "prompt_id": "personalized_newsletter_task5_html_builder"
    }
  ]
}
```

---

### 4. Scheduling & Automation Layer

**Purpose**: Automate weekly newsletter generation and delivery

**Options**:

#### Option 1: APScheduler (Simpler, MVP)

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

# Run every Monday at 9 AM
scheduler.add_job(
    generate_monday_newsletters,
    trigger="cron",
    day_of_week="mon",
    hour=9,
    minute=0,
    id="monday_newsletters",
)

# Run every Tuesday at 9 AM
scheduler.add_job(
    generate_tuesday_newsletters,
    trigger="cron",
    day_of_week="tue",
    hour=9,
    minute=0,
    id="tuesday_newsletters",
)

scheduler.start()
```

#### Option 2: Celery + Redis (Production)

```python
from celery import Celery
from celery.schedules import crontab

app = Celery("newsletter", broker="redis://localhost:6379/0")

@app.task
def generate_weekly_newsletters(day_of_week: str):
    """Generate newsletters for specific day."""
    subscriptions = get_active_subscriptions(
        day=day_of_week,
        status="active",
    )
    
    for sub in subscriptions:
        generate_and_send_newsletter.delay(sub.subscription_id)

@app.task(bind=True, max_retries=3)
def generate_and_send_newsletter(self, subscription_id: UUID):
    """Generate and send single newsletter."""
    try:
        # Generate newsletter
        newsletter = await newsletter_service.generate(subscription_id)
        
        # Send via Brevo
        delivery = await brevo_adapter.send_newsletter(newsletter)
        
        # Track delivery
        await track_delivery(subscription_id, delivery)
        
    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

# Schedule
app.conf.beat_schedule = {
    "monday-newsletters": {
        "task": "generate_weekly_newsletters",
        "schedule": crontab(day_of_week="mon", hour=9, minute=0),
        "args": ("monday",),
    },
    "tuesday-newsletters": {
        "task": "generate_weekly_newsletters",
        "schedule": crontab(day_of_week="tue", hour=9, minute=0),
        "args": ("tuesday",),
    },
    # ... other days
}
```

**Job Tracking**:

```sql
CREATE TABLE newsletter_jobs (
    job_id UUID PRIMARY KEY,
    subscription_id UUID REFERENCES newsletter_subscriptions(subscription_id),
    status TEXT NOT NULL,  -- pending, running, completed, failed
    scheduled_at TIMESTAMPTZ NOT NULL,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

### 5. Delivery Layer

**Purpose**: Send newsletters via email with tracking

**Components**:

```python
class NewsletterDeliveryService:
    """
    Newsletter delivery via Brevo.
    """
    
    def __init__(self, brevo_adapter: BrevoAdapter):
        self.brevo = brevo_adapter
    
    async def send_newsletter(
        self,
        subscription: NewsletterSubscription,
        newsletter: PersonalizedNewsletter,
    ) -> NewsletterDelivery:
        """
        Send newsletter via Brevo.
        
        Steps:
        1. Build email payload
        2. Add tracking pixels
        3. Add unsubscribe link
        4. Send via Brevo
        5. Record delivery
        """
        
        # Build email
        email_payload = self._build_email_payload(
            subscription=subscription,
            newsletter=newsletter,
        )
        
        # Send
        result = await self.brevo.send_email(email_payload)
        
        # Track
        delivery = NewsletterDelivery(
            delivery_id=uuid4(),
            subscription_id=subscription.subscription_id,
            newsletter_id=newsletter.newsletter_id,
            sent_at=datetime.utcnow(),
            delivery_status="sent",
            brevo_message_id=result["message_id"],
        )
        
        await self.repository.save_delivery(delivery)
        
        return delivery
```

**Email Template Structure**:

```html
<!DOCTYPE html>
<html>
<head>
    <title>{{company_name}} Weekly Intelligence</title>
</head>
<body>
    <!-- Header -->
    <div class="header">
        <h1>{{company_name}} Weekly Intelligence</h1>
        <p>{{current_date}}</p>
    </div>
    
    <!-- Personalized Intro -->
    <div class="intro">
        <p>Hi {{user_name}},</p>
        <p>{{personalized_intro}}</p>
    </div>
    
    <!-- Competitor Section -->
    <div class="section">
        <h2>🎯 Competitor Updates</h2>
        {{#each competitors}}
        <div class="competitor">
            <h3>{{name}}</h3>
            <p>{{activity}}</p>
            <a href="{{source_url}}">Read more →</a>
        </div>
        {{/each}}
    </div>
    
    <!-- Trends Section -->
    <div class="section">
        <h2>📈 Market Trends</h2>
        {{#each trends}}
        <div class="trend">
            <h3>{{name}}</h3>
            <p>{{description}}</p>
            <span class="momentum">{{momentum}}</span>
        </div>
        {{/each}}
    </div>
    
    <!-- News Section -->
    <div class="section">
        <h2>📰 Industry News</h2>
        {{#each news}}
        <div class="news">
            <h3>{{title}}</h3>
            <p>{{summary}}</p>
            <a href="{{url}}">Read more →</a>
        </div>
        {{/each}}
    </div>
    
    <!-- Insights Section -->
    <div class="section">
        <h2>💡 Key Insights</h2>
        <p>{{insights}}</p>
    </div>
    
    <!-- CTA -->
    <div class="cta">
        <a href="{{cta_url}}" class="button">{{cta_text}}</a>
    </div>
    
    <!-- Footer -->
    <div class="footer">
        <p>Manage preferences | <a href="{{unsubscribe_url}}">Unsubscribe</a></p>
        <p>Powered by Fylle AI</p>
    </div>
    
    <!-- Tracking Pixel -->
    <img src="{{tracking_pixel_url}}" width="1" height="1" />
</body>
</html>
```

---

### 6. Analytics & Feedback Layer

**Purpose**: Track engagement and improve personalization

**Metrics Tracked**:

```python
class NewsletterAnalytics:
    """
    Newsletter analytics and engagement tracking.
    """
    
    async def track_open(
        self,
        delivery_id: UUID,
        opened_at: datetime,
    ):
        """Track newsletter open event."""
    
    async def track_click(
        self,
        delivery_id: UUID,
        link_url: str,
        clicked_at: datetime,
    ):
        """Track link click event."""
    
    async def track_unsubscribe(
        self,
        subscription_id: UUID,
        reason: Optional[str],
    ):
        """Track unsubscribe event."""
    
    async def calculate_engagement_score(
        self,
        subscription_id: UUID,
    ) -> float:
        """
        Calculate engagement score (0-1).
        
        Factors:
        - Open rate (last 4 weeks)
        - Click rate (last 4 weeks)
        - Time spent reading
        - Feedback ratings
        """
    
    async def identify_churn_risk(
        self,
        subscription_id: UUID,
    ) -> ChurnRisk:
        """
        Identify users at risk of churning.
        
        Signals:
        - No opens in last 3 newsletters
        - Declining engagement trend
        - Low feedback ratings
        """
```

**Feedback Collection**:

```html
<!-- Embedded in email -->
<div class="feedback">
    <p>How useful was this newsletter?</p>
    <a href="{{feedback_url}}?rating=5">⭐⭐⭐⭐⭐</a>
    <a href="{{feedback_url}}?rating=4">⭐⭐⭐⭐</a>
    <a href="{{feedback_url}}?rating=3">⭐⭐⭐</a>
    <a href="{{feedback_url}}?rating=2">⭐⭐</a>
    <a href="{{feedback_url}}?rating=1">⭐</a>
</div>
```

---

## 🔗 INTEGRATION ARCHITECTURE

### Integration with Onboarding

```python
# After onboarding completion
async def complete_onboarding(session: OnboardingSession):
    # Existing flow
    result = await execute_onboarding_uc.execute(session)
    
    # NEW: Offer newsletter subscription
    if result.is_successful():
        # Show opt-in modal/banner
        newsletter_offer = NewsletterOffer(
            company_snapshot=session.snapshot,
            user_email=session.user_email,
        )
        
        # If user opts in
        if user_opts_in:
            subscription = await create_subscription_uc.execute(
                tenant_id=session.tenant_id,
                user_email=session.user_email,
                company_snapshot_id=session.snapshot.snapshot_id,
                preferences=user_preferences,
            )
            
            # Send welcome email
            await send_welcome_email(subscription)
            
            # Schedule first newsletter (next preferred day)
            await schedule_first_newsletter(subscription)
```

### Integration with Adaptive Cards

```python
# Bidirectional sync
async def sync_newsletter_with_cards(newsletter: PersonalizedNewsletter):
    """
    Create/Update Adaptive Cards from newsletter content.
    """
    
    # Create Competitor Cards
    for competitor in newsletter.competitors:
        card = await card_service.create_or_update_card(
            card_type="competitor",
            tenant_id=newsletter.tenant_id,
            content={
                "competitor_name": competitor.name,
                "recent_activity": competitor.activity,
                "source_url": competitor.source_url,
            },
            source_newsletter_id=newsletter.newsletter_id,
        )
    
    # Create Trend Cards
    for trend in newsletter.trends:
        card = await card_service.create_or_update_card(
            card_type="trend",
            tenant_id=newsletter.tenant_id,
            content={
                "trend_name": trend.name,
                "description": trend.description,
                "momentum": trend.momentum,
            },
            source_newsletter_id=newsletter.newsletter_id,
        )
```

---

**Status**: ✅ **ARCHITECTURE COMPLETE**  
**Next**: Linear Roadmap & Database Schema  
**Last Updated**: 2025-10-25

