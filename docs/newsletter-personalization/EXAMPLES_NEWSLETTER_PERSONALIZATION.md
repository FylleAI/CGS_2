# 💻 Newsletter Personalization - Code Examples

**Project**: Personalized Weekly Newsletter System  
**Version**: 1.0  
**Date**: 2025-10-25  

---

## 📁 FILE STRUCTURE

```
newsletter/
├── domain/
│   ├── models.py                    # Domain models
│   └── enums.py                     # Enums
├── application/
│   ├── use_cases/
│   │   ├── create_subscription.py
│   │   ├── generate_newsletter.py
│   │   ├── send_newsletter.py
│   │   └── track_engagement.py
│   └── services/
│       ├── competitor_research_service.py
│       ├── market_trend_service.py
│       ├── content_curation_service.py
│       └── newsletter_analytics_service.py
├── infrastructure/
│   ├── repositories/
│   │   ├── subscription_repository.py
│   │   ├── competitor_repository.py
│   │   └── newsletter_repository.py
│   ├── adapters/
│   │   └── newsletter_delivery_adapter.py
│   └── workflows/
│       ├── templates/
│       │   └── personalized_newsletter.json
│       └── handlers/
│           └── personalized_newsletter_handler.py
└── api/
    └── routes/
        ├── subscriptions.py
        ├── newsletters.py
        └── analytics.py
```

---

## 1️⃣ DOMAIN MODELS

### `newsletter/domain/models.py`

```python
"""
Newsletter domain models.
"""
from datetime import datetime, time
from typing import List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, EmailStr
from enum import Enum


class SubscriptionStatus(str, Enum):
    """Subscription status."""
    ACTIVE = "active"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class Frequency(str, Enum):
    """Newsletter frequency."""
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"


class DayOfWeek(str, Enum):
    """Day of week."""
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class SubscriptionPreferences(BaseModel):
    """Newsletter subscription preferences."""
    include_competitors: bool = True
    include_trends: bool = True
    include_news: bool = True
    include_insights: bool = True
    max_competitors: int = Field(default=5, ge=1, le=10)
    max_trends: int = Field(default=3, ge=1, le=5)
    content_length: str = Field(default="medium", pattern="^(short|medium|long)$")
    format: str = Field(default="html", pattern="^(html|plain_text)$")


class NewsletterSubscription(BaseModel):
    """Newsletter subscription."""
    subscription_id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    user_id: Optional[UUID] = None
    user_email: EmailStr
    company_snapshot_id: Optional[UUID] = None
    
    # Status
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    
    # Delivery preferences
    frequency: Frequency = Frequency.WEEKLY
    preferred_day: DayOfWeek = DayOfWeek.MONDAY
    preferred_time: time = time(9, 0)
    
    # Content preferences
    preferences: SubscriptionPreferences = Field(default_factory=SubscriptionPreferences)
    topics_of_interest: List[str] = Field(default_factory=list)
    
    # Unsubscribe
    unsubscribe_token: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    unsubscribed_at: Optional[datetime] = None
    unsubscribe_reason: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_sent_at: Optional[datetime] = None
    
    # Metadata
    metadata: dict = Field(default_factory=dict)


class Competitor(BaseModel):
    """Competitor profile."""
    competitor_id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    company_id: UUID
    
    # Competitor info
    competitor_name: str
    competitor_website: Optional[str] = None
    competitor_industry: Optional[str] = None
    competitor_description: Optional[str] = None
    
    # Relationship
    relationship_type: str = "direct"  # direct, indirect, emerging, adjacent
    
    # Monitoring
    monitoring_enabled: bool = True
    last_researched_at: Optional[datetime] = None
    research_frequency_days: int = 7
    
    # Snapshot
    snapshot: dict = Field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Metadata
    metadata: dict = Field(default_factory=dict)


class CompetitorActivity(BaseModel):
    """Competitor activity."""
    activity_id: UUID = Field(default_factory=uuid4)
    competitor_id: UUID
    
    # Activity info
    activity_type: str  # product_launch, funding, news, hiring, partnership, acquisition
    title: str
    description: Optional[str] = None
    source_url: Optional[str] = None
    published_at: Optional[datetime] = None
    
    # Relevance
    relevance_score: Optional[float] = Field(None, ge=0, le=1)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Metadata
    metadata: dict = Field(default_factory=dict)


class MarketTrend(BaseModel):
    """Market trend."""
    trend_id: UUID = Field(default_factory=uuid4)
    
    # Trend info
    industry: str
    trend_name: str
    trend_description: Optional[str] = None
    trend_category: Optional[str] = None  # technology, regulation, consumer_behavior, etc.
    
    # Detection
    first_detected_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Momentum
    momentum_score: Optional[float] = Field(None, ge=0, le=1)
    momentum_direction: Optional[str] = None  # growing, stable, declining
    
    # Sources
    sources: List[dict] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Metadata
    metadata: dict = Field(default_factory=dict)


class NewsletterEdition(BaseModel):
    """Newsletter edition."""
    edition_id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    subscription_id: UUID
    
    # Edition info
    edition_date: datetime
    edition_number: Optional[int] = None
    
    # Content
    content: dict  # Structured content
    html_content: Optional[str] = None
    plain_text_content: Optional[str] = None
    
    # Generation
    workflow_run_id: Optional[UUID] = None
    generation_status: str = "pending"  # pending, generating, completed, failed
    generated_at: Optional[datetime] = None
    generation_duration_ms: Optional[int] = None
    generation_cost_usd: Optional[float] = None
    
    # Delivery
    delivery_status: str = "pending"  # pending, scheduled, sent, failed, cancelled
    scheduled_for: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Metadata
    metadata: dict = Field(default_factory=dict)


class NewsletterDelivery(BaseModel):
    """Newsletter delivery."""
    delivery_id: UUID = Field(default_factory=uuid4)
    edition_id: UUID
    subscription_id: UUID
    
    # Delivery info
    sent_at: Optional[datetime] = None
    delivery_status: str  # sent, bounced, failed, spam
    brevo_message_id: Optional[str] = None
    
    # Engagement
    opened_at: Optional[datetime] = None
    first_click_at: Optional[datetime] = None
    click_count: int = 0
    
    # Unsubscribe
    unsubscribed_at: Optional[datetime] = None
    
    # Error info
    error_message: Optional[str] = None
    bounce_type: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Metadata
    metadata: dict = Field(default_factory=dict)


class PersonalizedNewsletter(BaseModel):
    """Personalized newsletter content."""
    newsletter_id: UUID = Field(default_factory=uuid4)
    subscription_id: UUID
    
    # Sections
    intro: str
    competitors: List[dict]  # [{name, activity, source_url}]
    trends: List[dict]  # [{name, description, momentum}]
    news: List[dict]  # [{title, summary, url}]
    insights: str
    cta: dict  # {text, url}
    
    # Metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    generation_cost_usd: float = 0.0
    word_count: int = 0
```

---

## 2️⃣ USE CASES

### `newsletter/application/use_cases/create_subscription.py`

```python
"""
Create newsletter subscription use case.
"""
from uuid import UUID
from typing import Optional
from newsletter.domain.models import (
    NewsletterSubscription,
    SubscriptionPreferences,
    DayOfWeek,
    Frequency,
)
from newsletter.infrastructure.repositories.subscription_repository import (
    SubscriptionRepository,
)
from onboarding.infrastructure.adapters.brevo_adapter import BrevoAdapter


class CreateSubscriptionUseCase:
    """Create newsletter subscription."""
    
    def __init__(
        self,
        subscription_repo: SubscriptionRepository,
        brevo_adapter: BrevoAdapter,
    ):
        self.subscription_repo = subscription_repo
        self.brevo = brevo_adapter
    
    async def execute(
        self,
        tenant_id: UUID,
        user_email: str,
        company_snapshot_id: Optional[UUID],
        preferences: SubscriptionPreferences,
        frequency: Frequency = Frequency.WEEKLY,
        preferred_day: DayOfWeek = DayOfWeek.MONDAY,
    ) -> NewsletterSubscription:
        """
        Create newsletter subscription.
        
        Steps:
        1. Validate inputs
        2. Check for existing subscription
        3. Create subscription
        4. Save to database
        5. Send welcome email
        6. Return subscription
        """
        
        # Check for existing subscription
        existing = await self.subscription_repo.find_by_email(
            tenant_id=tenant_id,
            user_email=user_email,
        )
        
        if existing and existing.status == "active":
            raise ValueError(f"Active subscription already exists for {user_email}")
        
        # Create subscription
        subscription = NewsletterSubscription(
            tenant_id=tenant_id,
            user_email=user_email,
            company_snapshot_id=company_snapshot_id,
            preferences=preferences,
            frequency=frequency,
            preferred_day=preferred_day,
        )
        
        # Save to database
        await self.subscription_repo.save(subscription)
        
        # Send welcome email
        await self._send_welcome_email(subscription)
        
        return subscription
    
    async def _send_welcome_email(self, subscription: NewsletterSubscription):
        """Send welcome email to new subscriber."""
        
        # Build email content
        subject = "Welcome to Your Personalized Newsletter!"
        
        html_content = f"""
        <h1>Welcome!</h1>
        <p>Thank you for subscribing to your personalized weekly newsletter.</p>
        <p>You'll receive your first newsletter on {subscription.preferred_day.value.capitalize()} at {subscription.preferred_time}.</p>
        <p><a href="https://app.fylle.ai/newsletters/preferences/{subscription.subscription_id}">Manage Preferences</a></p>
        <p><a href="https://app.fylle.ai/newsletters/unsubscribe/{subscription.unsubscribe_token}">Unsubscribe</a></p>
        """
        
        # Send via Brevo
        await self.brevo.send_email(
            to_email=subscription.user_email,
            subject=subject,
            html_content=html_content,
            tags=["newsletter", "welcome"],
        )
```

---

## 3️⃣ SERVICES

### `newsletter/application/services/competitor_research_service.py`

```python
"""
Competitor research service.
"""
from typing import List
from uuid import UUID
from datetime import datetime, timedelta
from newsletter.domain.models import Competitor, CompetitorActivity
from newsletter.infrastructure.repositories.competitor_repository import (
    CompetitorRepository,
)
from onboarding.infrastructure.adapters.perplexity_adapter import PerplexityAdapter
from onboarding.domain.models import CompanySnapshot


class CompetitorResearchService:
    """Automated competitor discovery and monitoring."""
    
    def __init__(
        self,
        competitor_repo: CompetitorRepository,
        perplexity: PerplexityAdapter,
    ):
        self.competitor_repo = competitor_repo
        self.perplexity = perplexity
    
    async def discover_competitors(
        self,
        tenant_id: UUID,
        company_snapshot: CompanySnapshot,
    ) -> List[Competitor]:
        """
        Discover competitors using Perplexity.
        
        Query: "Who are the main competitors of {company_name} 
                in the {industry} industry?"
        """
        
        # Build query
        query = f"""
        Who are the main competitors of {company_snapshot.company.name} 
        in the {company_snapshot.company.industry} industry?
        
        For each competitor, provide:
        - Company name
        - Website
        - Brief description
        - Relationship type (direct, indirect, emerging)
        
        Focus on the top 5-10 most relevant competitors.
        """
        
        # Research with Perplexity
        result = await self.perplexity.search(
            query=query,
            search_recency_filter="month",  # Last month
        )
        
        # Parse competitors from result
        competitors = self._parse_competitors(
            tenant_id=tenant_id,
            company_id=company_snapshot.context_id,
            research_result=result,
        )
        
        # Save to database
        for competitor in competitors:
            await self.competitor_repo.save(competitor)
        
        return competitors
    
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
        
        # Build query
        query = f"""
        What are the recent news, product launches, partnerships, 
        and updates from {competitor.competitor_name}?
        
        Focus on the {timeframe}.
        
        For each activity, provide:
        - Type (product_launch, funding, news, hiring, partnership, acquisition)
        - Title
        - Brief description
        - Source URL
        - Published date
        """
        
        # Research with Perplexity
        result = await self.perplexity.search(
            query=query,
            search_recency_filter="week",  # Last week
        )
        
        # Parse activities
        activities = self._parse_activities(
            competitor_id=competitor.competitor_id,
            research_result=result,
        )
        
        # Save to database
        for activity in activities:
            await self.competitor_repo.save_activity(activity)
        
        # Update last_researched_at
        competitor.last_researched_at = datetime.utcnow()
        await self.competitor_repo.update(competitor)
        
        return activities
    
    async def get_weekly_competitor_updates(
        self,
        tenant_id: UUID,
        company_id: UUID,
    ) -> List[CompetitorActivity]:
        """
        Get all competitor activities from last 7 days.
        """
        
        # Get all competitors for company
        competitors = await self.competitor_repo.find_by_company(
            tenant_id=tenant_id,
            company_id=company_id,
            monitoring_enabled=True,
        )
        
        all_activities = []
        
        # Research each competitor
        for competitor in competitors:
            # Check if research is needed
            if self._needs_research(competitor):
                activities = await self.research_competitor_activities(competitor)
                all_activities.extend(activities)
            else:
                # Get cached activities
                activities = await self.competitor_repo.get_recent_activities(
                    competitor_id=competitor.competitor_id,
                    days=7,
                )
                all_activities.extend(activities)
        
        # Sort by relevance and published date
        all_activities.sort(
            key=lambda a: (a.relevance_score or 0, a.published_at or datetime.min),
            reverse=True,
        )
        
        return all_activities
    
    def _needs_research(self, competitor: Competitor) -> bool:
        """Check if competitor needs fresh research."""
        if not competitor.last_researched_at:
            return True
        
        days_since_research = (datetime.utcnow() - competitor.last_researched_at).days
        return days_since_research >= competitor.research_frequency_days
    
    def _parse_competitors(
        self,
        tenant_id: UUID,
        company_id: UUID,
        research_result: dict,
    ) -> List[Competitor]:
        """Parse competitors from Perplexity result."""
        # TODO: Implement parsing logic
        # This would use LLM to extract structured data from research_result
        pass
    
    def _parse_activities(
        self,
        competitor_id: UUID,
        research_result: dict,
    ) -> List[CompetitorActivity]:
        """Parse activities from Perplexity result."""
        # TODO: Implement parsing logic
        pass
```

---

### `newsletter/application/services/market_trend_service.py`

```python
"""
Market trend identification and tracking service.
"""
from typing import List
from uuid import UUID
from datetime import datetime
from newsletter.domain.models import MarketTrend
from newsletter.infrastructure.repositories.trend_repository import TrendRepository
from onboarding.infrastructure.adapters.perplexity_adapter import PerplexityAdapter
from onboarding.domain.models import CompanySnapshot


class MarketTrendService:
    """Market trend identification and tracking."""

    def __init__(
        self,
        trend_repo: TrendRepository,
        perplexity: PerplexityAdapter,
    ):
        self.trend_repo = trend_repo
        self.perplexity = perplexity

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

        # Build query
        query = f"""
        What are the emerging trends in the {industry} industry in the {timeframe}?

        For each trend, provide:
        - Trend name
        - Brief description
        - Category (technology, regulation, consumer_behavior, economic, competitive)
        - Key indicators of momentum (growing, stable, declining)
        - Source URLs
        - Relevant keywords

        Focus on trends that would be relevant to companies in this industry.
        """

        # Research with Perplexity
        result = await self.perplexity.search(
            query=query,
            search_recency_filter="month",
        )

        # Parse trends
        trends = self._parse_trends(
            industry=industry,
            research_result=result,
        )

        # Save or update trends
        for trend in trends:
            existing = await self.trend_repo.find_by_name(
                industry=industry,
                trend_name=trend.trend_name,
            )

            if existing:
                # Update existing trend
                existing.last_updated_at = datetime.utcnow()
                existing.sources.extend(trend.sources)
                existing.momentum_score = trend.momentum_score
                existing.momentum_direction = trend.momentum_direction
                await self.trend_repo.update(existing)
            else:
                # Save new trend
                await self.trend_repo.save(trend)

        return trends

    async def score_trend_relevance(
        self,
        trend: MarketTrend,
        company_snapshot: CompanySnapshot,
    ) -> float:
        """
        Score trend relevance (0-1) for specific company.

        Uses LLM to analyze relevance based on:
        - Company industry alignment
        - Company products/services
        - Company target audience
        - Trend category and keywords
        """

        # Build prompt for relevance scoring
        prompt = f"""
        Analyze the relevance of this market trend to the company.

        TREND:
        - Name: {trend.trend_name}
        - Description: {trend.trend_description}
        - Category: {trend.trend_category}
        - Keywords: {', '.join(trend.keywords)}

        COMPANY:
        - Name: {company_snapshot.company.name}
        - Industry: {company_snapshot.company.industry}
        - Description: {company_snapshot.company.description}
        - Key Offerings: {', '.join(company_snapshot.company.key_offerings)}
        - Target Audience: {company_snapshot.audience.primary}

        Score the relevance from 0 to 1, where:
        - 0 = Not relevant at all
        - 0.5 = Moderately relevant
        - 1 = Highly relevant

        Provide:
        1. Relevance score (0-1)
        2. Brief reason for the score

        Format: {"score": 0.8, "reason": "..."}
        """

        # Use LLM to score (could use Gemini or GPT)
        # For now, simplified scoring based on keyword overlap
        score = self._calculate_keyword_overlap_score(trend, company_snapshot)

        return score

    async def get_relevant_trends_for_company(
        self,
        company_snapshot: CompanySnapshot,
        max_trends: int = 3,
    ) -> List[tuple[MarketTrend, float]]:
        """
        Get most relevant trends for company.

        Returns: List of (trend, relevance_score) tuples
        """

        # Get all trends for industry
        trends = await self.trend_repo.find_by_industry(
            industry=company_snapshot.company.industry,
        )

        # Score each trend
        scored_trends = []
        for trend in trends:
            score = await self.score_trend_relevance(trend, company_snapshot)
            scored_trends.append((trend, score))

        # Sort by score and return top N
        scored_trends.sort(key=lambda x: x[1], reverse=True)
        return scored_trends[:max_trends]

    def _parse_trends(
        self,
        industry: str,
        research_result: dict,
    ) -> List[MarketTrend]:
        """Parse trends from Perplexity result."""
        # TODO: Implement parsing logic using LLM
        pass

    def _calculate_keyword_overlap_score(
        self,
        trend: MarketTrend,
        company_snapshot: CompanySnapshot,
    ) -> float:
        """Calculate relevance score based on keyword overlap."""
        # Simplified scoring logic
        company_keywords = set([
            company_snapshot.company.industry.lower(),
            *[offering.lower() for offering in company_snapshot.company.key_offerings],
        ])

        trend_keywords = set([kw.lower() for kw in trend.keywords])

        overlap = len(company_keywords & trend_keywords)
        total = len(company_keywords | trend_keywords)

        return overlap / total if total > 0 else 0.0
```

---

### `newsletter/application/services/content_curation_service.py`

```python
"""
Content curation and prioritization service.
"""
from typing import List, Dict, Any
from newsletter.domain.models import (
    CompetitorActivity,
    MarketTrend,
    SubscriptionPreferences,
)


class ContentCurationService:
    """Content curation and prioritization."""

    def curate_content(
        self,
        competitors: List[CompetitorActivity],
        trends: List[tuple[MarketTrend, float]],
        news: List[Dict[str, Any]],
        preferences: SubscriptionPreferences,
    ) -> Dict[str, Any]:
        """
        Curate and prioritize content for newsletter.

        Steps:
        1. Filter by preferences
        2. Deduplicate content
        3. Score by relevance
        4. Select top N items per section
        5. Order by priority
        """

        curated = {}

        # Curate competitors
        if preferences.include_competitors:
            curated["competitors"] = self._curate_competitors(
                competitors,
                max_items=preferences.max_competitors,
            )

        # Curate trends
        if preferences.include_trends:
            curated["trends"] = self._curate_trends(
                trends,
                max_items=preferences.max_trends,
            )

        # Curate news
        if preferences.include_news:
            curated["news"] = self._curate_news(
                news,
                max_items=5,
            )

        return curated

    def _curate_competitors(
        self,
        activities: List[CompetitorActivity],
        max_items: int,
    ) -> List[Dict[str, Any]]:
        """Curate competitor activities."""

        # Deduplicate by title
        seen_titles = set()
        unique_activities = []

        for activity in activities:
            if activity.title not in seen_titles:
                seen_titles.add(activity.title)
                unique_activities.append(activity)

        # Sort by relevance and date
        unique_activities.sort(
            key=lambda a: (a.relevance_score or 0, a.published_at or datetime.min),
            reverse=True,
        )

        # Select top N
        top_activities = unique_activities[:max_items]

        # Format for newsletter
        return [
            {
                "name": activity.title,
                "activity": activity.description,
                "source_url": activity.source_url,
                "published_at": activity.published_at.isoformat() if activity.published_at else None,
            }
            for activity in top_activities
        ]

    def _curate_trends(
        self,
        trends: List[tuple[MarketTrend, float]],
        max_items: int,
    ) -> List[Dict[str, Any]]:
        """Curate market trends."""

        # Already sorted by relevance score
        top_trends = trends[:max_items]

        # Format for newsletter
        return [
            {
                "name": trend.trend_name,
                "description": trend.trend_description,
                "momentum": trend.momentum_direction,
                "relevance_score": relevance_score,
            }
            for trend, relevance_score in top_trends
        ]

    def _curate_news(
        self,
        news: List[Dict[str, Any]],
        max_items: int,
    ) -> List[Dict[str, Any]]:
        """Curate industry news."""

        # Deduplicate by URL
        seen_urls = set()
        unique_news = []

        for article in news:
            url = article.get("url")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_news.append(article)

        # Select top N
        return unique_news[:max_items]
```

---

## 4️⃣ API ENDPOINTS

### `newsletter/api/routes/subscriptions.py`

```python
"""
Newsletter subscription API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, EmailStr
from newsletter.domain.models import (
    NewsletterSubscription,
    SubscriptionPreferences,
    DayOfWeek,
    Frequency,
)
from newsletter.application.use_cases.create_subscription import (
    CreateSubscriptionUseCase,
)
from newsletter.application.use_cases.update_preferences import (
    UpdatePreferencesUseCase,
)
from newsletter.application.use_cases.unsubscribe import UnsubscribeUseCase


router = APIRouter(prefix="/api/v1/newsletters", tags=["newsletters"])


# Request/Response Models
class CreateSubscriptionRequest(BaseModel):
    """Create subscription request."""
    user_email: EmailStr
    company_snapshot_id: Optional[UUID] = None
    preferences: SubscriptionPreferences = SubscriptionPreferences()
    frequency: Frequency = Frequency.WEEKLY
    preferred_day: DayOfWeek = DayOfWeek.MONDAY


class SubscriptionResponse(BaseModel):
    """Subscription response."""
    subscription_id: UUID
    user_email: str
    status: str
    frequency: str
    preferred_day: str
    created_at: str


class UpdatePreferencesRequest(BaseModel):
    """Update preferences request."""
    preferences: SubscriptionPreferences


# Endpoints
@router.post("/subscribe", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    request: CreateSubscriptionRequest,
    tenant_id: UUID,  # From auth middleware
    create_subscription_uc: CreateSubscriptionUseCase = Depends(),
):
    """
    Create newsletter subscription.

    After onboarding, user can opt-in to receive weekly personalized newsletter.
    """
    try:
        subscription = await create_subscription_uc.execute(
            tenant_id=tenant_id,
            user_email=request.user_email,
            company_snapshot_id=request.company_snapshot_id,
            preferences=request.preferences,
            frequency=request.frequency,
            preferred_day=request.preferred_day,
        )

        return SubscriptionResponse(
            subscription_id=subscription.subscription_id,
            user_email=subscription.user_email,
            status=subscription.status.value,
            frequency=subscription.frequency.value,
            preferred_day=subscription.preferred_day.value,
            created_at=subscription.created_at.isoformat(),
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put("/subscriptions/{subscription_id}/preferences", response_model=SubscriptionResponse)
async def update_preferences(
    subscription_id: UUID,
    request: UpdatePreferencesRequest,
    update_preferences_uc: UpdatePreferencesUseCase = Depends(),
):
    """Update subscription preferences."""
    try:
        subscription = await update_preferences_uc.execute(
            subscription_id=subscription_id,
            preferences=request.preferences,
        )

        return SubscriptionResponse(
            subscription_id=subscription.subscription_id,
            user_email=subscription.user_email,
            status=subscription.status.value,
            frequency=subscription.frequency.value,
            preferred_day=subscription.preferred_day.value,
            created_at=subscription.created_at.isoformat(),
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete("/unsubscribe/{unsubscribe_token}", status_code=status.HTTP_204_NO_CONTENT)
async def unsubscribe(
    unsubscribe_token: str,
    reason: Optional[str] = None,
    unsubscribe_uc: UnsubscribeUseCase = Depends(),
):
    """Unsubscribe from newsletter."""
    try:
        await unsubscribe_uc.execute(
            unsubscribe_token=unsubscribe_token,
            reason=reason,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/subscriptions/{subscription_id}", response_model=SubscriptionResponse)
async def get_subscription(
    subscription_id: UUID,
    subscription_repo = Depends(),
):
    """Get subscription details."""
    subscription = await subscription_repo.find_by_id(subscription_id)

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found",
        )

    return SubscriptionResponse(
        subscription_id=subscription.subscription_id,
        user_email=subscription.user_email,
        status=subscription.status.value,
        frequency=subscription.frequency.value,
        preferred_day=subscription.preferred_day.value,
        created_at=subscription.created_at.isoformat(),
    )
```

---

## 5️⃣ FRONTEND COMPONENTS (React/TypeScript)

### `NewsletterOptInModal.tsx`

```typescript
/**
 * Newsletter opt-in modal shown after onboarding completion.
 */
import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Checkbox,
  FormGroup,
  Typography,
  Box,
} from '@mui/material';
import { NewsletterSubscription, SubscriptionPreferences } from '../types/newsletter';
import { createSubscription } from '../api/newsletterApi';

interface NewsletterOptInModalProps {
  open: boolean;
  onClose: () => void;
  userEmail: string;
  companySnapshotId: string;
}

export const NewsletterOptInModal: React.FC<NewsletterOptInModalProps> = ({
  open,
  onClose,
  userEmail,
  companySnapshotId,
}) => {
  const [frequency, setFrequency] = useState<'weekly' | 'biweekly' | 'monthly'>('weekly');
  const [preferredDay, setPreferredDay] = useState<string>('monday');
  const [preferences, setPreferences] = useState<SubscriptionPreferences>({
    include_competitors: true,
    include_trends: true,
    include_news: true,
    include_insights: true,
    max_competitors: 5,
    max_trends: 3,
    content_length: 'medium',
    format: 'html',
  });
  const [loading, setLoading] = useState(false);

  const handleSubscribe = async () => {
    setLoading(true);

    try {
      await createSubscription({
        user_email: userEmail,
        company_snapshot_id: companySnapshotId,
        preferences,
        frequency,
        preferred_day: preferredDay,
      });

      // Show success message
      alert('Successfully subscribed to newsletter!');
      onClose();
    } catch (error) {
      console.error('Failed to subscribe:', error);
      alert('Failed to subscribe. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        📧 Get Your Personalized Weekly Newsletter
      </DialogTitle>

      <DialogContent>
        <Typography variant="body1" gutterBottom>
          Stay ahead of the competition with weekly insights tailored to your business:
        </Typography>

        <Box sx={{ mt: 2, mb: 3 }}>
          <ul>
            <li>Competitor activities and updates</li>
            <li>Emerging market trends</li>
            <li>Industry news and insights</li>
            <li>Personalized recommendations</li>
          </ul>
        </Box>

        {/* Frequency */}
        <FormControl component="fieldset" sx={{ mb: 2 }}>
          <FormLabel component="legend">Frequency</FormLabel>
          <RadioGroup
            value={frequency}
            onChange={(e) => setFrequency(e.target.value as any)}
          >
            <FormControlLabel value="weekly" control={<Radio />} label="Weekly" />
            <FormControlLabel value="biweekly" control={<Radio />} label="Bi-weekly" />
            <FormControlLabel value="monthly" control={<Radio />} label="Monthly" />
          </RadioGroup>
        </FormControl>

        {/* Preferred Day */}
        <FormControl component="fieldset" sx={{ mb: 2 }}>
          <FormLabel component="legend">Preferred Day</FormLabel>
          <RadioGroup
            value={preferredDay}
            onChange={(e) => setPreferredDay(e.target.value)}
            row
          >
            <FormControlLabel value="monday" control={<Radio />} label="Mon" />
            <FormControlLabel value="tuesday" control={<Radio />} label="Tue" />
            <FormControlLabel value="wednesday" control={<Radio />} label="Wed" />
            <FormControlLabel value="thursday" control={<Radio />} label="Thu" />
            <FormControlLabel value="friday" control={<Radio />} label="Fri" />
          </RadioGroup>
        </FormControl>

        {/* Content Preferences */}
        <FormControl component="fieldset">
          <FormLabel component="legend">Content Preferences</FormLabel>
          <FormGroup>
            <FormControlLabel
              control={
                <Checkbox
                  checked={preferences.include_competitors}
                  onChange={(e) => setPreferences({
                    ...preferences,
                    include_competitors: e.target.checked,
                  })}
                />
              }
              label="Competitor Updates"
            />
            <FormControlLabel
              control={
                <Checkbox
                  checked={preferences.include_trends}
                  onChange={(e) => setPreferences({
                    ...preferences,
                    include_trends: e.target.checked,
                  })}
                />
              }
              label="Market Trends"
            />
            <FormControlLabel
              control={
                <Checkbox
                  checked={preferences.include_news}
                  onChange={(e) => setPreferences({
                    ...preferences,
                    include_news: e.target.checked,
                  })}
                />
              }
              label="Industry News"
            />
            <FormControlLabel
              control={
                <Checkbox
                  checked={preferences.include_insights}
                  onChange={(e) => setPreferences({
                    ...preferences,
                    include_insights: e.target.checked,
                  })}
                />
              }
              label="Personalized Insights"
            />
          </FormGroup>
        </FormControl>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          Skip for Now
        </Button>
        <Button
          onClick={handleSubscribe}
          variant="contained"
          color="primary"
          disabled={loading}
        >
          {loading ? 'Subscribing...' : 'Subscribe'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};
```

---

**Status**: ✅ **EXAMPLES COMPLETE**
**Total Lines**: ~1200
**Last Updated**: 2025-10-25

