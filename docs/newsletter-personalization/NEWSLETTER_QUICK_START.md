# 🚀 Newsletter Personalizzata - Quick Start Guide

**Project**: Personalized Weekly Newsletter System  
**Version**: 1.0  
**Date**: 2025-10-25  
**Estimated Time**: 2-3 ore per setup iniziale

---

## 🎯 OBIETTIVO

Questo documento ti guida attraverso il setup iniziale del sistema di Newsletter Personalizzata in **2-3 ore**.

Al termine avrai:
- ✅ Database schema creato
- ✅ Domain models implementati
- ✅ Prima subscription creata
- ✅ Test di generazione newsletter funzionante

---

## 📋 PREREQUISITI

### Software Richiesto

- [x] Python 3.11+
- [x] PostgreSQL 14+ (Supabase)
- [x] Redis (opzionale per MVP, richiesto per production)
- [x] Node.js 18+ (per frontend)

### Accessi Richiesti

- [x] Supabase project access
- [x] Perplexity API key
- [x] Brevo API key
- [x] Repository access (CGS_2)

### Conoscenze Richieste

- [x] Python (FastAPI, Pydantic, SQLAlchemy)
- [x] PostgreSQL (SQL, migrations)
- [x] React/TypeScript (per frontend)

---

## 🏁 STEP 1: DATABASE SETUP (30 min)

### 1.1 Create Migration File

```bash
cd /Users/davidescantamburlo/Desktop/Test\ Onboarding\ /CGS_2

# Create migration directory if not exists
mkdir -p newsletter/infrastructure/database/migrations

# Copy schema file
cp DATABASE_SCHEMA_NEWSLETTER_PERSONALIZATION.sql \
   newsletter/infrastructure/database/migrations/001_create_newsletter_schema.sql
```

### 1.2 Run Migration

**Option A: Using Supabase CLI**

```bash
# Install Supabase CLI if not installed
brew install supabase/tap/supabase

# Login to Supabase
supabase login

# Link to your project
supabase link --project-ref YOUR_PROJECT_REF

# Run migration
supabase db push
```

**Option B: Using psql**

```bash
# Connect to Supabase
psql "postgresql://postgres:[YOUR-PASSWORD]@[YOUR-PROJECT-REF].supabase.co:5432/postgres"

# Run migration
\i newsletter/infrastructure/database/migrations/001_create_newsletter_schema.sql

# Verify tables created
\dt newsletter*
```

### 1.3 Verify Schema

```sql
-- Check tables
SELECT table_name 
FROM information_schema.tables 
WHERE table_name LIKE 'newsletter%';

-- Expected output:
-- newsletter_subscriptions
-- competitors
-- competitor_activities
-- market_trends
-- user_trend_relevance
-- newsletter_editions
-- newsletter_deliveries
-- newsletter_engagement
-- newsletter_feedback
-- newsletter_jobs

-- Check views
SELECT table_name 
FROM information_schema.views 
WHERE table_name LIKE '%subscription%';

-- Expected output:
-- active_subscriptions
-- subscription_engagement_metrics
```

---

## 🏁 STEP 2: DOMAIN MODELS (30 min)

### 2.1 Create Directory Structure

```bash
mkdir -p newsletter/domain
mkdir -p newsletter/application/use_cases
mkdir -p newsletter/application/services
mkdir -p newsletter/infrastructure/repositories
mkdir -p newsletter/api/routes
```

### 2.2 Create Domain Models

**File**: `newsletter/domain/models.py`

```bash
# Copy from examples
cp EXAMPLES_NEWSLETTER_PERSONALIZATION.md newsletter/domain/models.py

# Extract only the domain models section (lines 1-200)
# You can do this manually or use a text editor
```

**Or create manually**:

```python
# newsletter/domain/models.py
"""
Newsletter domain models.
"""
from datetime import datetime, time
from typing import List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, EmailStr
from enum import Enum
import secrets


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
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            time: lambda v: v.isoformat(),
        }
```

### 2.3 Test Models

```python
# test_models.py
from newsletter.domain.models import NewsletterSubscription, SubscriptionPreferences
from uuid import uuid4

# Create test subscription
subscription = NewsletterSubscription(
    tenant_id=uuid4(),
    user_email="test@example.com",
    preferences=SubscriptionPreferences(
        include_competitors=True,
        max_competitors=5,
    ),
)

print(f"Subscription created: {subscription.subscription_id}")
print(f"Unsubscribe token: {subscription.unsubscribe_token}")
print(f"Status: {subscription.status.value}")

# Test JSON serialization
print(subscription.model_dump_json(indent=2))
```

---

## 🏁 STEP 3: REPOSITORY (30 min)

### 3.1 Create Repository

**File**: `newsletter/infrastructure/repositories/subscription_repository.py`

```python
"""
Newsletter subscription repository.
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from newsletter.domain.models import NewsletterSubscription, SubscriptionStatus
from supabase import Client


class SubscriptionRepository:
    """Newsletter subscription repository."""
    
    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.table = "newsletter_subscriptions"
    
    async def save(self, subscription: NewsletterSubscription) -> NewsletterSubscription:
        """Save subscription to database."""
        
        data = {
            "subscription_id": str(subscription.subscription_id),
            "tenant_id": str(subscription.tenant_id),
            "user_id": str(subscription.user_id) if subscription.user_id else None,
            "user_email": subscription.user_email,
            "company_snapshot_id": str(subscription.company_snapshot_id) if subscription.company_snapshot_id else None,
            "status": subscription.status.value,
            "frequency": subscription.frequency.value,
            "preferred_day": subscription.preferred_day.value,
            "preferred_time": subscription.preferred_time.isoformat(),
            "preferences": subscription.preferences.model_dump(),
            "topics_of_interest": subscription.topics_of_interest,
            "unsubscribe_token": subscription.unsubscribe_token,
            "created_at": subscription.created_at.isoformat(),
            "updated_at": subscription.updated_at.isoformat(),
        }
        
        result = self.supabase.table(self.table).insert(data).execute()
        
        return subscription
    
    async def find_by_id(self, subscription_id: UUID) -> Optional[NewsletterSubscription]:
        """Find subscription by ID."""
        
        result = self.supabase.table(self.table).select("*").eq(
            "subscription_id", str(subscription_id)
        ).execute()
        
        if not result.data:
            return None
        
        return self._to_model(result.data[0])
    
    async def find_by_email(
        self,
        tenant_id: UUID,
        user_email: str,
    ) -> Optional[NewsletterSubscription]:
        """Find subscription by email."""
        
        result = self.supabase.table(self.table).select("*").eq(
            "tenant_id", str(tenant_id)
        ).eq(
            "user_email", user_email
        ).execute()
        
        if not result.data:
            return None
        
        return self._to_model(result.data[0])
    
    def _to_model(self, data: dict) -> NewsletterSubscription:
        """Convert database row to model."""
        
        from newsletter.domain.models import (
            SubscriptionStatus,
            Frequency,
            DayOfWeek,
            SubscriptionPreferences,
        )
        
        return NewsletterSubscription(
            subscription_id=UUID(data["subscription_id"]),
            tenant_id=UUID(data["tenant_id"]),
            user_id=UUID(data["user_id"]) if data.get("user_id") else None,
            user_email=data["user_email"],
            company_snapshot_id=UUID(data["company_snapshot_id"]) if data.get("company_snapshot_id") else None,
            status=SubscriptionStatus(data["status"]),
            frequency=Frequency(data["frequency"]),
            preferred_day=DayOfWeek(data["preferred_day"]),
            preferred_time=datetime.fromisoformat(data["preferred_time"]).time(),
            preferences=SubscriptionPreferences(**data["preferences"]),
            topics_of_interest=data.get("topics_of_interest", []),
            unsubscribe_token=data["unsubscribe_token"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            last_sent_at=datetime.fromisoformat(data["last_sent_at"]) if data.get("last_sent_at") else None,
        )
```

---

## 🏁 STEP 4: CREATE FIRST SUBSCRIPTION (15 min)

### 4.1 Test Script

**File**: `scripts/test_newsletter_subscription.py`

```python
"""
Test newsletter subscription creation.
"""
import asyncio
from uuid import uuid4
from newsletter.domain.models import NewsletterSubscription, SubscriptionPreferences
from newsletter.infrastructure.repositories.subscription_repository import SubscriptionRepository
from supabase import create_client
import os


async def main():
    # Initialize Supabase
    supabase = create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_ANON_KEY"),
    )
    
    # Create repository
    repo = SubscriptionRepository(supabase)
    
    # Create test subscription
    subscription = NewsletterSubscription(
        tenant_id=uuid4(),
        user_email="davide@fylle.ai",
        preferences=SubscriptionPreferences(
            include_competitors=True,
            include_trends=True,
            max_competitors=5,
            max_trends=3,
        ),
    )
    
    print(f"Creating subscription for {subscription.user_email}...")
    
    # Save to database
    saved = await repo.save(subscription)
    
    print(f"✅ Subscription created!")
    print(f"   ID: {saved.subscription_id}")
    print(f"   Email: {saved.user_email}")
    print(f"   Status: {saved.status.value}")
    print(f"   Unsubscribe token: {saved.unsubscribe_token}")
    
    # Verify by reading back
    found = await repo.find_by_id(saved.subscription_id)
    
    if found:
        print(f"✅ Subscription verified in database!")
    else:
        print(f"❌ Subscription not found in database!")


if __name__ == "__main__":
    asyncio.run(main())
```

### 4.2 Run Test

```bash
# Set environment variables
export SUPABASE_URL="your-supabase-url"
export SUPABASE_ANON_KEY="your-supabase-anon-key"

# Run test
python scripts/test_newsletter_subscription.py
```

**Expected Output**:
```
Creating subscription for davide@fylle.ai...
✅ Subscription created!
   ID: 123e4567-e89b-12d3-a456-426614174000
   Email: davide@fylle.ai
   Status: active
   Unsubscribe token: abc123...
✅ Subscription verified in database!
```

---

## 🏁 STEP 5: VERIFY SETUP (15 min)

### 5.1 Check Database

```sql
-- Connect to Supabase
psql "postgresql://postgres:[YOUR-PASSWORD]@[YOUR-PROJECT-REF].supabase.co:5432/postgres"

-- Check subscription
SELECT 
    subscription_id,
    user_email,
    status,
    frequency,
    preferred_day,
    created_at
FROM newsletter_subscriptions
ORDER BY created_at DESC
LIMIT 5;
```

### 5.2 Check Views

```sql
-- Check active subscriptions view
SELECT * FROM active_subscriptions;

-- Check engagement metrics view
SELECT * FROM subscription_engagement_metrics;
```

---

## ✅ NEXT STEPS

Congratulazioni! Hai completato il setup iniziale. 🎉

### Immediate Next Steps

1. **Implement Use Cases** (NL-1.3)
   - CreateSubscriptionUseCase
   - UpdatePreferencesUseCase
   - UnsubscribeUseCase

2. **Create API Endpoints** (NL-1.4)
   - POST /api/v1/newsletters/subscribe
   - PUT /api/v1/newsletters/subscriptions/{id}/preferences
   - DELETE /api/v1/newsletters/unsubscribe/{token}

3. **Create Frontend Components** (NL-1.5)
   - NewsletterOptInModal
   - PreferencesForm

### Follow the Roadmap

Continua con il [Linear Roadmap](LINEAR_ROADMAP_NEWSLETTER_PERSONALIZATION.md):
- Week 1-2: Complete EPIC 1 (Subscription System)
- Week 3-4: EPIC 2 (Intelligence Engine)
- Week 5-6: EPIC 3 (Content Generation)

---

**Status**: ✅ **QUICK START COMPLETE**  
**Time Spent**: ~2-3 hours  
**Next**: [Linear Roadmap](LINEAR_ROADMAP_NEWSLETTER_PERSONALIZATION.md)  
**Last Updated**: 2025-10-25

