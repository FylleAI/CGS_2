# 📋 Newsletter Personalizzata - Linear Roadmap

**Project**: Personalized Weekly Newsletter System  
**Version**: 1.0  
**Date**: 2025-10-25  
**Total Story Points**: 134  
**Timeline**: 10-12 weeks  

---

## 📊 OVERVIEW

### Milestones

| Milestone | Description | Story Points | Timeline |
|-----------|-------------|--------------|----------|
| **M1: Foundation** | Subscription management + Database | 24 pts | Week 1-2 |
| **M2: Intelligence** | Competitor & trend research | 28 pts | Week 3-4 |
| **M3: Generation** | Newsletter generation pipeline | 32 pts | Week 5-6 |
| **M4: Automation** | Scheduling & delivery | 22 pts | Week 7-8 |
| **M5: Analytics** | Tracking & feedback | 18 pts | Week 9-10 |
| **M6: Integration** | Onboarding & Cards integration | 10 pts | Week 11-12 |

### Epics

| Epic | Description | Tasks | Story Points |
|------|-------------|-------|--------------|
| **EPIC 1: Subscription System** | User subscription management | 5 | 24 pts |
| **EPIC 2: Intelligence Engine** | Competitor & trend research | 6 | 28 pts |
| **EPIC 3: Content Generation** | Newsletter generation pipeline | 7 | 32 pts |
| **EPIC 4: Automation & Scheduling** | Background jobs & cron | 5 | 22 pts |
| **EPIC 5: Analytics & Feedback** | Engagement tracking | 4 | 18 pts |
| **EPIC 6: Integration** | Onboarding & Cards sync | 3 | 10 pts |

---

## 🎯 EPIC 1: Subscription System (24 pts)

### NL-1.1: Database Schema - Subscriptions

**Priority**: P0 (Critical)  
**Estimate**: 5 story points  
**Dependencies**: None  
**Milestone**: M1 - Foundation

**Description**:
Create database schema for newsletter subscriptions and preferences.

**Acceptance Criteria**:
- ✅ `newsletter_subscriptions` table created
- ✅ `subscription_preferences` table created
- ✅ Multi-tenant isolation (tenant_id)
- ✅ Unsubscribe token generation
- ✅ Indexes on tenant_id, user_email, status
- ✅ Foreign keys to company_contexts
- ✅ Migration script tested

**Technical Notes**:
```sql
CREATE TABLE newsletter_subscriptions (
    subscription_id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    user_id UUID,
    user_email TEXT NOT NULL,
    company_snapshot_id UUID REFERENCES company_contexts(context_id),
    status TEXT NOT NULL DEFAULT 'active',
    frequency TEXT NOT NULL DEFAULT 'weekly',
    preferred_day TEXT NOT NULL DEFAULT 'monday',
    preferred_time TIME NOT NULL DEFAULT '09:00',
    unsubscribe_token TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_sent_at TIMESTAMPTZ
);
```

---

### NL-1.2: Subscription Domain Models

**Priority**: P0 (Critical)  
**Estimate**: 3 story points  
**Dependencies**: NL-1.1  
**Milestone**: M1 - Foundation

**Description**:
Create Pydantic domain models for subscriptions and preferences.

**Acceptance Criteria**:
- ✅ `NewsletterSubscription` model created
- ✅ `SubscriptionPreferences` model created
- ✅ `SubscriptionStatus` enum (active, paused, cancelled)
- ✅ `Frequency` enum (weekly, biweekly, monthly)
- ✅ `DayOfWeek` enum
- ✅ Validation logic (email, preferences)
- ✅ Unit tests for models

**Technical Notes**:
```python
class NewsletterSubscription(BaseModel):
    subscription_id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    user_email: str = Field(..., regex=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    frequency: Frequency = Frequency.WEEKLY
    preferred_day: DayOfWeek = DayOfWeek.MONDAY
    preferred_time: time = time(9, 0)
    topics_of_interest: List[str] = Field(default_factory=list)
    unsubscribe_token: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
```

---

### NL-1.3: Subscription Use Cases

**Priority**: P0 (Critical)  
**Estimate**: 8 story points  
**Dependencies**: NL-1.2  
**Milestone**: M1 - Foundation

**Description**:
Implement use cases for subscription management.

**Acceptance Criteria**:
- ✅ `CreateSubscriptionUseCase` implemented
- ✅ `UpdatePreferencesUseCase` implemented
- ✅ `UnsubscribeUseCase` implemented
- ✅ `PauseSubscriptionUseCase` implemented
- ✅ `ReactivateSubscriptionUseCase` implemented
- ✅ Repository pattern for persistence
- ✅ Unit tests for all use cases
- ✅ Integration tests with Supabase

**Technical Notes**:
```python
class CreateSubscriptionUseCase:
    async def execute(
        self,
        tenant_id: UUID,
        user_email: str,
        company_snapshot_id: UUID,
        preferences: SubscriptionPreferences,
    ) -> NewsletterSubscription:
        # Validate inputs
        # Create subscription
        # Generate unsubscribe token
        # Save to database
        # Send welcome email
        # Return subscription
```

---

### NL-1.4: Subscription API Endpoints

**Priority**: P0 (Critical)  
**Estimate**: 5 story points  
**Dependencies**: NL-1.3  
**Milestone**: M1 - Foundation

**Description**:
Create REST API endpoints for subscription management.

**Acceptance Criteria**:
- ✅ `POST /api/v1/newsletters/subscribe` endpoint
- ✅ `PUT /api/v1/newsletters/subscriptions/{id}/preferences` endpoint
- ✅ `POST /api/v1/newsletters/subscriptions/{id}/pause` endpoint
- ✅ `POST /api/v1/newsletters/subscriptions/{id}/reactivate` endpoint
- ✅ `DELETE /api/v1/newsletters/unsubscribe/{token}` endpoint
- ✅ `GET /api/v1/newsletters/subscriptions/{id}` endpoint
- ✅ Request/Response models
- ✅ Error handling
- ✅ API documentation (OpenAPI)
- ✅ Integration tests

---

### NL-1.5: Subscription Frontend Components

**Priority**: P1 (High)  
**Estimate**: 3 story points  
**Dependencies**: NL-1.4  
**Milestone**: M1 - Foundation

**Description**:
Create React components for newsletter subscription.

**Acceptance Criteria**:
- ✅ `NewsletterOptInModal` component (after onboarding)
- ✅ `PreferencesForm` component
- ✅ `UnsubscribeConfirmation` component
- ✅ Form validation
- ✅ API integration
- ✅ Loading states
- ✅ Error handling
- ✅ Success messages

---

## 🎯 EPIC 2: Intelligence Engine (28 pts)

### NL-2.1: Competitor Database Schema

**Priority**: P0 (Critical)  
**Estimate**: 5 story points  
**Dependencies**: NL-1.1  
**Milestone**: M2 - Intelligence

**Description**:
Create database schema for competitor tracking.

**Acceptance Criteria**:
- ✅ `competitors` table created
- ✅ `competitor_activities` table created
- ✅ Multi-tenant isolation
- ✅ Relationship to company_contexts
- ✅ Indexes on tenant_id, company_id, competitor_name
- ✅ Migration script tested

**Technical Notes**:
```sql
CREATE TABLE competitors (
    competitor_id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    company_id UUID REFERENCES company_contexts(context_id),
    competitor_name TEXT NOT NULL,
    competitor_website TEXT,
    competitor_industry TEXT,
    relationship_type TEXT DEFAULT 'direct',
    monitoring_enabled BOOLEAN DEFAULT true,
    last_researched_at TIMESTAMPTZ,
    snapshot JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE competitor_activities (
    activity_id UUID PRIMARY KEY,
    competitor_id UUID REFERENCES competitors(competitor_id),
    activity_type TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    source_url TEXT,
    published_at TIMESTAMPTZ,
    relevance_score FLOAT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

### NL-2.2: Market Trends Database Schema

**Priority**: P0 (Critical)  
**Estimate**: 5 story points  
**Dependencies**: NL-1.1  
**Milestone**: M2 - Intelligence

**Description**:
Create database schema for market trend tracking.

**Acceptance Criteria**:
- ✅ `market_trends` table created
- ✅ `user_trend_relevance` table created
- ✅ Trend momentum tracking
- ✅ Industry categorization
- ✅ Indexes on industry, trend_name
- ✅ Migration script tested

---

### NL-2.3: Competitor Research Service

**Priority**: P0 (Critical)  
**Estimate**: 8 story points  
**Dependencies**: NL-2.1  
**Milestone**: M2 - Intelligence

**Description**:
Implement automated competitor discovery and monitoring.

**Acceptance Criteria**:
- ✅ `CompetitorResearchService` class implemented
- ✅ `discover_competitors()` method (uses Perplexity)
- ✅ `research_competitor_activities()` method
- ✅ `analyze_competitive_landscape()` method
- ✅ Caching to avoid duplicate research
- ✅ Cost tracking
- ✅ Unit tests
- ✅ Integration tests with Perplexity

**Technical Notes**:
```python
class CompetitorResearchService:
    async def discover_competitors(
        self,
        company_snapshot: CompanySnapshot,
    ) -> List[Competitor]:
        query = f"""
        Who are the main competitors of {company_snapshot.company.name} 
        in the {company_snapshot.company.industry} industry?
        Provide company names, websites, and brief descriptions.
        """
        result = await self.perplexity.search(query)
        competitors = self._parse_competitors(result)
        return competitors
```

---

### NL-2.4: Market Trend Service

**Priority**: P0 (Critical)  
**Estimate**: 5 story points  
**Dependencies**: NL-2.2  
**Milestone**: M2 - Intelligence

**Description**:
Implement market trend identification and tracking.

**Acceptance Criteria**:
- ✅ `MarketTrendService` class implemented
- ✅ `identify_trends()` method (uses Perplexity)
- ✅ `score_trend_relevance()` method
- ✅ `track_trend_momentum()` method
- ✅ Trend deduplication
- ✅ Unit tests
- ✅ Integration tests

---

### NL-2.5: Industry News Aggregator

**Priority**: P1 (High)  
**Estimate**: 3 story points  
**Dependencies**: None  
**Milestone**: M2 - Intelligence

**Description**:
Implement industry news aggregation.

**Acceptance Criteria**:
- ✅ `IndustryNewsAggregator` class implemented
- ✅ `aggregate_news()` method (uses Perplexity/Serper)
- ✅ `filter_by_relevance()` method
- ✅ News deduplication
- ✅ Unit tests

---

### NL-2.6: Intelligence Orchestrator

**Priority**: P0 (Critical)  
**Estimate**: 2 story points  
**Dependencies**: NL-2.3, NL-2.4, NL-2.5  
**Milestone**: M2 - Intelligence

**Description**:
Orchestrate all intelligence gathering services.

**Acceptance Criteria**:
- ✅ `IntelligenceOrchestrator` class implemented
- ✅ Parallel execution of research tasks
- ✅ Error handling and fallbacks
- ✅ Cost tracking
- ✅ Unit tests

---

## 🎯 EPIC 3: Content Generation (32 pts)

### NL-3.1: Newsletter Workflow Template

**Priority**: P0 (Critical)  
**Estimate**: 5 story points  
**Dependencies**: NL-2.6  
**Milestone**: M3 - Generation

**Description**:
Create workflow template for personalized newsletter generation.

**Acceptance Criteria**:
- ✅ `personalized_newsletter.json` template created
- ✅ 5-task workflow (Context, Research, Curation, Assembly, HTML)
- ✅ Variable definitions
- ✅ Agent assignments
- ✅ Prompt IDs defined
- ✅ Template tested with CGS

---

### NL-3.2: Newsletter Workflow Handler

**Priority**: P0 (Critical)  
**Estimate**: 8 story points  
**Dependencies**: NL-3.1  
**Milestone**: M3 - Generation

**Description**:
Implement workflow handler for personalized newsletter.

**Acceptance Criteria**:
- ✅ `PersonalizedNewsletterHandler` class implemented
- ✅ `prepare_context()` method
- ✅ `post_process_task()` method
- ✅ `post_process_workflow()` method
- ✅ Integration with intelligence services
- ✅ Cost tracking
- ✅ Unit tests
- ✅ Integration tests

---

### NL-3.3: Newsletter Prompts

**Priority**: P0 (Critical)  
**Estimate**: 5 story points  
**Dependencies**: NL-3.1  
**Milestone**: M3 - Generation

**Description**:
Create prompts for all newsletter generation tasks.

**Acceptance Criteria**:
- ✅ `personalized_newsletter_task1_context_setup.md` prompt
- ✅ `personalized_newsletter_task2_intelligence_research.md` prompt
- ✅ `personalized_newsletter_task3_content_curation.md` prompt
- ✅ `personalized_newsletter_task4_newsletter_assembly.md` prompt
- ✅ `personalized_newsletter_task5_html_builder.md` prompt
- ✅ Prompts tested with agents
- ✅ Quality validation

---

### NL-3.4: Content Curation Service

**Priority**: P0 (Critical)  
**Estimate**: 5 story points  
**Dependencies**: NL-2.6  
**Milestone**: M3 - Generation

**Description**:
Implement content curation and prioritization logic.

**Acceptance Criteria**:
- ✅ `ContentCurationService` class implemented
- ✅ Relevance scoring algorithm
- ✅ Content deduplication
- ✅ Priority ordering
- ✅ Max items per section enforcement
- ✅ Unit tests

---

### NL-3.5: Newsletter Email Template

**Priority**: P0 (Critical)  
**Estimate**: 5 story points  
**Dependencies**: None  
**Milestone**: M3 - Generation

**Description**:
Create HTML email template for newsletters.

**Acceptance Criteria**:
- ✅ Responsive HTML template
- ✅ Sections: Intro, Competitors, Trends, News, Insights, CTA
- ✅ Unsubscribe link
- ✅ Tracking pixel
- ✅ Plain text fallback
- ✅ Tested across email clients (Gmail, Outlook, Apple Mail)

---

### NL-3.6: Newsletter Generation Use Case

**Priority**: P0 (Critical)  
**Estimate**: 3 story points  
**Dependencies**: NL-3.2, NL-3.4  
**Milestone**: M3 - Generation

**Description**:
Implement end-to-end newsletter generation use case.

**Acceptance Criteria**:
- ✅ `GenerateNewsletterUseCase` class implemented
- ✅ Orchestrates intelligence + generation + formatting
- ✅ Error handling
- ✅ Cost tracking
- ✅ Unit tests
- ✅ Integration tests

---

### NL-3.7: Newsletter Preview API

**Priority**: P1 (High)  
**Estimate**: 1 story point  
**Dependencies**: NL-3.6  
**Milestone**: M3 - Generation

**Description**:
Create API endpoint for newsletter preview (before sending).

**Acceptance Criteria**:
- ✅ `POST /api/v1/newsletters/preview` endpoint
- ✅ Generate newsletter without sending
- ✅ Return HTML + plain text
- ✅ API documentation

---

## 🎯 EPIC 4: Automation & Scheduling (22 pts)

### NL-4.1: Job Queue Infrastructure

**Priority**: P0 (Critical)  
**Estimate**: 8 story points  
**Dependencies**: None  
**Milestone**: M4 - Automation

**Description**:
Setup background job queue system (APScheduler or Celery).

**Acceptance Criteria**:
- ✅ Choose job queue (APScheduler for MVP, Celery for production)
- ✅ Setup Redis (if Celery)
- ✅ Configure job worker
- ✅ Job status tracking table
- ✅ Retry logic (max 3 attempts)
- ✅ Job timeout configuration
- ✅ Monitoring setup
- ✅ Documentation

**Technical Notes**:
```python
# MVP: APScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()
scheduler.add_job(
    generate_weekly_newsletters,
    trigger="cron",
    day_of_week="mon",
    hour=9,
    minute=0,
)
scheduler.start()
```

---

### NL-4.2: Newsletter Job Scheduler

**Priority**: P0 (Critical)  
**Estimate**: 5 story points  
**Dependencies**: NL-4.1  
**Milestone**: M4 - Automation

**Description**:
Implement newsletter generation job scheduler.

**Acceptance Criteria**:
- ✅ `NewsletterScheduler` class implemented
- ✅ Schedule jobs for each day of week
- ✅ Batch processing (100 newsletters/batch)
- ✅ Rate limiting (respect Perplexity/Brevo limits)
- ✅ Error handling
- ✅ Job status tracking
- ✅ Unit tests

---

### NL-4.3: Newsletter Delivery Service

**Priority**: P0 (Critical)  
**Estimate**: 5 story points  
**Dependencies**: NL-3.6  
**Milestone**: M4 - Automation

**Description**:
Implement newsletter delivery via Brevo.

**Acceptance Criteria**:
- ✅ `NewsletterDeliveryService` class implemented
- ✅ Integration with BrevoAdapter
- ✅ Delivery tracking
- ✅ Bounce handling
- ✅ Retry logic
- ✅ Unit tests
- ✅ Integration tests with Brevo

---

### NL-4.4: Job Monitoring Dashboard

**Priority**: P2 (Medium)  
**Estimate**: 3 story points  
**Dependencies**: NL-4.2  
**Milestone**: M4 - Automation

**Description**:
Create admin dashboard for monitoring newsletter jobs.

**Acceptance Criteria**:
- ✅ View active jobs
- ✅ View job history
- ✅ View failed jobs
- ✅ Retry failed jobs
- ✅ Cancel pending jobs
- ✅ Job statistics (success rate, avg duration)

---

### NL-4.5: Welcome Email Flow

**Priority**: P1 (High)  
**Estimate**: 1 story point  
**Dependencies**: NL-1.3  
**Milestone**: M4 - Automation

**Description**:
Implement welcome email sent after subscription.

**Acceptance Criteria**:
- ✅ Welcome email template
- ✅ Send immediately after subscription
- ✅ Include preferences link
- ✅ Include unsubscribe link
- ✅ Tested

---

## 🎯 EPIC 5: Analytics & Feedback (18 pts)

### NL-5.1: Analytics Database Schema

**Priority**: P0 (Critical)  
**Estimate**: 3 story points  
**Dependencies**: NL-1.1  
**Milestone**: M5 - Analytics

**Description**:
Create database schema for newsletter analytics.

**Acceptance Criteria**:
- ✅ `newsletter_deliveries` table created
- ✅ `newsletter_engagement` table created
- ✅ `newsletter_feedback` table created
- ✅ Indexes for performance
- ✅ Migration script tested

---

### NL-5.2: Analytics Tracking Service

**Priority**: P0 (Critical)  
**Estimate**: 8 story points  
**Dependencies**: NL-5.1  
**Milestone**: M5 - Analytics

**Description**:
Implement analytics tracking for opens, clicks, and engagement.

**Acceptance Criteria**:
- ✅ `NewsletterAnalytics` class implemented
- ✅ `track_open()` method (tracking pixel)
- ✅ `track_click()` method (link tracking)
- ✅ `track_unsubscribe()` method
- ✅ `calculate_engagement_score()` method
- ✅ `identify_churn_risk()` method
- ✅ Unit tests
- ✅ Integration tests

---

### NL-5.3: Feedback Collection System

**Priority**: P1 (High)  
**Estimate**: 5 story points  
**Dependencies**: NL-5.1  
**Milestone**: M5 - Analytics

**Description**:
Implement feedback collection embedded in emails.

**Acceptance Criteria**:
- ✅ Feedback links in email template
- ✅ `POST /api/v1/newsletters/feedback` endpoint
- ✅ Feedback storage
- ✅ Feedback aggregation
- ✅ Feedback analysis
- ✅ Unit tests

---

### NL-5.4: Analytics Dashboard

**Priority**: P2 (Medium)  
**Estimate**: 2 story points  
**Dependencies**: NL-5.2  
**Milestone**: M5 - Analytics

**Description**:
Create analytics dashboard for newsletter performance.

**Acceptance Criteria**:
- ✅ Overall metrics (open rate, click rate, engagement)
- ✅ Per-newsletter metrics
- ✅ Trend charts
- ✅ Churn risk alerts
- ✅ Export to CSV

---

## 🎯 EPIC 6: Integration (10 pts)

### NL-6.1: Onboarding Integration

**Priority**: P0 (Critical)  
**Estimate**: 5 story points  
**Dependencies**: NL-1.3, NL-1.5  
**Milestone**: M6 - Integration

**Description**:
Integrate newsletter opt-in into onboarding flow.

**Acceptance Criteria**:
- ✅ Opt-in modal after onboarding completion
- ✅ Create subscription if user opts in
- ✅ Send welcome email
- ✅ Schedule first newsletter
- ✅ Update onboarding session metadata
- ✅ Integration tests

---

### NL-6.2: Adaptive Cards Integration

**Priority**: P1 (High)  
**Estimate**: 3 story points  
**Dependencies**: NL-3.6  
**Milestone**: M6 - Integration

**Description**:
Sync newsletter content with Adaptive Cards.

**Acceptance Criteria**:
- ✅ Create Competitor Cards from newsletter
- ✅ Create Trend Cards from newsletter
- ✅ Update existing cards
- ✅ Link cards to newsletter source
- ✅ Unit tests

---

### NL-6.3: Publishing Integration

**Priority**: P2 (Medium)  
**Estimate**: 2 story points  
**Dependencies**: NL-3.6  
**Milestone**: M6 - Integration

**Description**:
Enable repurposing newsletter content to LinkedIn/HubSpot.

**Acceptance Criteria**:
- ✅ Extract sections for social posts
- ✅ Format for LinkedIn
- ✅ Format for HubSpot blog
- ✅ API endpoint for content export
- ✅ Documentation

---

**Status**: ✅ **ROADMAP COMPLETE**  
**Total Tasks**: 30  
**Total Story Points**: 134  
**Last Updated**: 2025-10-25

