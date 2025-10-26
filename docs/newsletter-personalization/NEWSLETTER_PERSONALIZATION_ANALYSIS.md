# 📧 Newsletter Personalizzata Settimanale - Analisi Completa

**Project**: Personalized Weekly Newsletter for User Retention  
**Version**: 1.0  
**Date**: 2025-10-25  
**Status**: Planning Phase ✅

---

## 🎯 EXECUTIVE SUMMARY

### Obiettivo Strategico

Creare un sistema di **Newsletter Personalizzata Settimanale** che massimizzi la **retention** degli utenti attraverso contenuti di alto valore tailor-made basati su:
- Profilo aziendale dell'utente
- Settore di business
- Competitor e loro attività
- Trend di mercato rilevanti

### Valore di Business

- ✅ **Retention**: Touchpoint settimanale automatico con valore concreto
- ✅ **Engagement**: Contenuti personalizzati aumentano aperture e click
- ✅ **Upsell**: Opportunità di promuovere feature premium
- ✅ **Brand Authority**: Posizionamento come fonte di intelligence di mercato
- ✅ **Data Collection**: Feedback loop per migliorare personalizzazione

---

## 📊 STATO ATTUALE - COSA ABBIAMO

### 1. ✅ Newsletter Workflow Esistente (Siebert)

**Componenti Disponibili**:

| Componente | File | Riutilizzabile | Note |
|------------|------|----------------|------|
| **Workflow Template** | `siebert_premium_newsletter.json` | ✅ Sì | 3-task workflow (RAG + Research + Assembly) |
| **HTML Workflow** | `siebert_newsletter_html.json` | ✅ Sì | Include HTML email builder |
| **Premium Handler** | `premium_newsletter_handler.py` | ✅ Sì | Gestione brand guidelines + sources |
| **Siebert Handler** | `siebert_premium_newsletter_handler.py` | ⚠️ Parziale | Troppo specifico per Siebert |
| **HTML Handler** | `siebert_newsletter_html_handler.py` | ✅ Sì | HTML design system |
| **Newsletter Config** | `NewsletterConfig` in `content_types.py` | ✅ Sì | Pydantic model per config |

**Workflow Structure** (Siebert Premium):
```
Task 1: RAG Specialist → Brand Context & Template Setup
Task 2: Research Specialist → Perplexity Multi-Source Research
Task 3: Copywriter → Newsletter Assembly (8 sections)
Task 4: Compliance Specialist → FINRA/SEC Review (optional)
Task 5: HTML Email Builder → HTML Container (optional)
```

**Features Esistenti**:
- ✅ Multi-source research con Perplexity
- ✅ RAG integration per brand context
- ✅ Customizable word count (800-1500)
- ✅ Customizable sections (3-8)
- ✅ HTML email output
- ✅ Brand voice integration
- ✅ Cost tracking e metrics

---

### 2. ✅ Onboarding System

**Componenti Disponibili**:

| Componente | File | Riutilizzabile | Note |
|------------|------|----------------|------|
| **Company Research** | `ResearchCompanyUseCase` | ✅ Sì | Perplexity research con RAG cache |
| **Company Snapshot** | `CompanySnapshot` model | ✅ Sì | Rich company profile |
| **User Profiling** | `OnboardingSession` | ⚠️ Parziale | Manca subscription preferences |
| **Email Delivery** | `BrevoAdapter` | ✅ Sì | Transactional email ready |
| **Persistence** | `SupabaseSessionRepository` | ✅ Sì | Session tracking |

**Company Snapshot Fields** (Riutilizzabili):
```python
CompanySnapshot:
  - company: CompanyInfo
    - name, industry, description
    - key_offerings, differentiators
  - audience: AudienceInfo
    - primary, secondary, pain_points
  - voice: VoiceInfo
    - tone, style_guidelines
  - insights: InsightsInfo
    - positioning, key_messages
    - recent_news, competitors  ← IMPORTANTE!
```

**Onboarding Flow**:
```
1. Research Company (Perplexity)
2. Synthesize Snapshot (Gemini)
3. Generate Clarifying Questions
4. Collect Answers
5. Execute Workflow
6. Deliver via Email (Brevo)
7. Persist to Supabase
```

---

### 3. ✅ Research & Intelligence Tools

**Componenti Disponibili**:

| Tool | File | Capability | Cost |
|------|------|------------|------|
| **Perplexity** | `PerplexityResearchTool` | Web research, recent news | ~$0.005/call |
| **Serper** | `WebSearchTool` | Google search | ~$0.002/call |
| **RAG** | `RagTool` | Company knowledge base | Free |

**Perplexity Capabilities**:
- ✅ Real-time web research
- ✅ Multi-source aggregation
- ✅ Timeframe filtering (last 7 days, yesterday, last month)
- ✅ Domain filtering
- ✅ Citation tracking

**Existing Research Patterns**:
```python
# From ResearchCompanyUseCase
research_result = await perplexity.research_with_retry(
    brand_name=session.brand_name,
    website=session.website,
    additional_context=additional_context,
)
```

---

### 4. ✅ Email Delivery System

**Componenti Disponibili**:

| Componente | Capability | Status |
|------------|------------|--------|
| **Brevo Adapter** | Transactional email | ✅ Production-ready |
| **HTML Templates** | Email formatting | ✅ Available |
| **Template Support** | Brevo templates | ✅ Configured |
| **Idempotency** | Session-based dedup | ✅ Implemented |
| **Retry Logic** | Exponential backoff | ✅ Implemented |

**Email Features**:
- ✅ HTML + Plain text fallback
- ✅ Custom headers (X-Session-Id, X-Content-Id)
- ✅ Tags for categorization
- ✅ Delivery tracking (message_id, timestamp)

---

### 5. ✅ Database & Persistence

**Existing Tables** (Supabase):

| Table | Purpose | Reusable |
|-------|---------|----------|
| `onboarding_sessions` | Session tracking | ⚠️ Parziale |
| `company_contexts` | RAG cache for companies | ✅ Sì |
| `clients` | Client profiles | ✅ Sì |
| `documents` | Knowledge base | ✅ Sì |
| `content_generations` | Generated content | ✅ Sì |
| `workflow_runs` | Workflow tracking | ✅ Sì |

**Existing Fields** (Riutilizzabili):
```sql
onboarding_sessions:
  - brand_name, website, user_email
  - snapshot (JSONB) → CompanySnapshot
  - metadata (JSONB) → Extensible

company_contexts:
  - company_name, website
  - company_snapshot (JSONB)
  - usage_count, last_used_at
```

---

### 6. ✅ Adaptive Cards System

**Componenti Disponibili**:

| Componente | File | Capability |
|------------|------|------------|
| **Card Storage** | `context_cards` table | Store dynamic cards |
| **Card Types** | Multiple types | Persona, Product, Trend, etc. |
| **Performance Tracking** | `card_performance_events` | Track usage & engagement |
| **Relationships** | `card_relationships` | Link related cards |

**Integration Opportunity**:
- ✅ Newsletter content → Create/Update Adaptive Cards
- ✅ Cards → Inform newsletter personalization
- ✅ Performance feedback → Improve content

---

## ❌ COSA MANCA - GAP ANALYSIS

### 1. ❌ User Subscription Management

**Missing Components**:
- ❌ **Newsletter Subscriptions Table**: Track who is subscribed
- ❌ **Subscription Preferences**: Frequency, topics, format
- ❌ **Opt-in/Opt-out Flow**: GDPR-compliant subscription management
- ❌ **Unsubscribe Tokens**: Secure unsubscribe links
- ❌ **Subscription Status**: Active, paused, cancelled

**Required Schema**:
```sql
newsletter_subscriptions:
  - subscription_id (UUID)
  - tenant_id (UUID) -- Multi-tenant
  - user_id (UUID)
  - user_email (TEXT)
  - company_snapshot_id (UUID) -- Link to company profile
  - status (TEXT) -- active, paused, cancelled
  - frequency (TEXT) -- weekly, biweekly, monthly
  - preferred_day (TEXT) -- monday, tuesday, etc.
  - preferred_time (TIME) -- 09:00, 14:00, etc.
  - topics_of_interest (TEXT[]) -- competitors, trends, news
  - created_at, updated_at
  - last_sent_at
  - unsubscribe_token (TEXT)
```

---

### 2. ❌ Competitor Tracking System

**Missing Components**:
- ❌ **Competitor Database**: Store competitor profiles
- ❌ **Competitor Research**: Automated competitor discovery
- ❌ **Competitor Monitoring**: Track competitor activities
- ❌ **Competitor News**: Aggregate competitor news/updates
- ❌ **Competitive Intelligence**: Analyze competitor strategies

**Required Schema**:
```sql
competitors:
  - competitor_id (UUID)
  - tenant_id (UUID)
  - company_id (UUID) -- Our client
  - competitor_name (TEXT)
  - competitor_website (TEXT)
  - competitor_industry (TEXT)
  - relationship_type (TEXT) -- direct, indirect, emerging
  - monitoring_enabled (BOOLEAN)
  - last_researched_at (TIMESTAMPTZ)
  - snapshot (JSONB) -- CompanySnapshot-like structure
  - created_at, updated_at

competitor_activities:
  - activity_id (UUID)
  - competitor_id (UUID)
  - activity_type (TEXT) -- product_launch, funding, news, hiring
  - title (TEXT)
  - description (TEXT)
  - source_url (TEXT)
  - published_at (TIMESTAMPTZ)
  - relevance_score (FLOAT) -- 0-1
  - created_at
```

---

### 3. ❌ Market Trend Analysis

**Missing Components**:
- ❌ **Trend Detection**: Identify emerging trends in user's industry
- ❌ **Trend Tracking**: Monitor trend evolution over time
- ❌ **Trend Relevance**: Score trends by relevance to user
- ❌ **Trend Aggregation**: Aggregate trends across sources

**Required Schema**:
```sql
market_trends:
  - trend_id (UUID)
  - industry (TEXT)
  - trend_name (TEXT)
  - trend_description (TEXT)
  - trend_category (TEXT) -- technology, regulation, consumer_behavior
  - first_detected_at (TIMESTAMPTZ)
  - momentum_score (FLOAT) -- 0-1 (growing, stable, declining)
  - sources (JSONB) -- Array of source URLs
  - keywords (TEXT[])
  - created_at, updated_at

user_trend_relevance:
  - relevance_id (UUID)
  - tenant_id (UUID)
  - trend_id (UUID)
  - relevance_score (FLOAT) -- 0-1
  - reason (TEXT) -- Why this trend is relevant
  - created_at
```

---

### 4. ❌ Newsletter Generation Pipeline

**Missing Components**:
- ❌ **Personalization Engine**: Combine user profile + competitors + trends
- ❌ **Content Curation**: Select most relevant content for each user
- ❌ **Newsletter Template**: User-specific newsletter structure
- ❌ **A/B Testing**: Test different content strategies
- ❌ **Content Deduplication**: Avoid sending same content twice

**Required Logic**:
```python
class NewsletterPersonalizationEngine:
    async def generate_personalized_newsletter(
        self,
        subscription: NewsletterSubscription,
        company_snapshot: CompanySnapshot,
        competitors: List[Competitor],
        trends: List[MarketTrend],
    ) -> PersonalizedNewsletter:
        """
        Generate personalized newsletter content.
        
        Steps:
        1. Research competitor activities (last 7 days)
        2. Identify relevant market trends
        3. Aggregate industry news
        4. Curate content based on user preferences
        5. Generate newsletter sections
        6. Apply brand voice
        """
```

---

### 5. ❌ Scheduling & Automation

**Missing Components**:
- ❌ **Cron Job System**: No background job scheduler
- ❌ **Job Queue**: No async job processing (Celery/ARQ/RQ)
- ❌ **Scheduled Sends**: No weekly newsletter automation
- ❌ **Batch Processing**: No bulk newsletter generation
- ❌ **Retry Logic**: No failed send retry mechanism

**Required Infrastructure**:
```python
# Option 1: Celery + Redis
@celery.task
def generate_weekly_newsletters():
    """Run every Monday at 9 AM"""
    subscriptions = get_active_subscriptions(day="monday")
    for sub in subscriptions:
        generate_and_send_newsletter.delay(sub.subscription_id)

# Option 2: APScheduler (simpler)
scheduler = AsyncIOScheduler()
scheduler.add_job(
    generate_weekly_newsletters,
    trigger="cron",
    day_of_week="mon",
    hour=9,
    minute=0,
)
```

---

### 6. ❌ Analytics & Feedback Loop

**Missing Components**:
- ❌ **Email Analytics**: Open rates, click rates, engagement
- ❌ **Content Performance**: Which sections perform best
- ❌ **User Feedback**: Explicit feedback collection
- ❌ **Personalization Improvement**: ML-based optimization
- ❌ **Churn Prediction**: Identify users at risk of unsubscribing

**Required Schema**:
```sql
newsletter_deliveries:
  - delivery_id (UUID)
  - subscription_id (UUID)
  - newsletter_id (UUID)
  - sent_at (TIMESTAMPTZ)
  - delivery_status (TEXT) -- sent, bounced, failed
  - brevo_message_id (TEXT)
  - opened_at (TIMESTAMPTZ)
  - clicked_at (TIMESTAMPTZ)
  - unsubscribed_at (TIMESTAMPTZ)

newsletter_engagement:
  - engagement_id (UUID)
  - delivery_id (UUID)
  - event_type (TEXT) -- open, click, forward, reply
  - event_data (JSONB)
  - created_at

newsletter_feedback:
  - feedback_id (UUID)
  - delivery_id (UUID)
  - rating (INTEGER) -- 1-5
  - feedback_text (TEXT)
  - created_at
```

---

## 🔄 INTEGRATION CON SISTEMI ESISTENTI

### 1. Onboarding Flow → Newsletter Subscription

**Current Flow**:
```
User completes onboarding → Views Adaptive Cards → Done
```

**New Flow**:
```
User completes onboarding → Views Adaptive Cards → 
  → Opt-in to Newsletter (modal/banner) →
  → Configure preferences (frequency, topics) →
  → Create subscription record →
  → Send welcome email →
  → Schedule first newsletter
```

**Integration Points**:
- ✅ Use existing `CompanySnapshot` for personalization
- ✅ Use existing `user_email` for delivery
- ✅ Extend `OnboardingSession` with `newsletter_opted_in` flag
- ✅ Create `NewsletterSubscription` after onboarding

---

### 2. Adaptive Cards → Newsletter Content

**Bidirectional Integration**:

**Cards → Newsletter**:
- ✅ Use Adaptive Cards as content source
- ✅ Persona Cards → Audience insights
- ✅ Product Cards → Product updates
- ✅ Trend Cards → Market trends
- ✅ Competitor Cards → Competitive intelligence

**Newsletter → Cards**:
- ✅ Newsletter content → Create new Adaptive Cards
- ✅ Competitor activities → Update Competitor Cards
- ✅ Market trends → Create/Update Trend Cards
- ✅ Performance data → Update Card metrics

---

### 3. Publishing Systems (HubSpot/LinkedIn) → Newsletter

**Content Repurposing**:
- ✅ Newsletter content → LinkedIn posts
- ✅ Newsletter content → HubSpot blog posts
- ✅ Newsletter sections → Social media snippets
- ✅ Trend analysis → Thought leadership content

**Cross-Channel Strategy**:
```
Weekly Newsletter (Email) →
  → LinkedIn Post (Monday)
  → HubSpot Blog (Wednesday)
  → Twitter Thread (Friday)
```

---

## 📈 SUCCESS METRICS & KPIs

### Retention Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Subscription Rate** | >40% of onboarded users | % users who opt-in after onboarding |
| **Open Rate** | >25% | % newsletters opened |
| **Click Rate** | >5% | % users who click links |
| **Engagement Rate** | >10% | % users who interact (open + click) |
| **Churn Rate** | <5% monthly | % users who unsubscribe |
| **Retention Lift** | +30% | Increase in 90-day retention vs non-subscribers |

### Content Quality Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Relevance Score** | >4/5 | User feedback rating |
| **Content Freshness** | 100% | % content from last 7 days |
| **Personalization Accuracy** | >80% | % content relevant to user's industry |
| **Competitor Coverage** | >3 competitors/newsletter | Avg competitors mentioned |
| **Trend Coverage** | >2 trends/newsletter | Avg trends mentioned |

### Operational Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Generation Time** | <5 min/newsletter | Avg time to generate |
| **Delivery Success** | >99% | % successfully delivered |
| **Cost per Newsletter** | <$0.10 | Avg cost (research + generation + delivery) |
| **Automation Rate** | 100% | % newsletters sent automatically |

---

## 🎯 NEXT STEPS

1. ✅ **Review this analysis** with team
2. ⏳ **Design complete architecture** (next document)
3. ⏳ **Create Linear roadmap** with tasks and estimates
4. ⏳ **Design database schema** for all new tables
5. ⏳ **Create code examples** for key components
6. ⏳ **Plan MVP scope** (what to build first)

---

**Status**: ✅ **ANALYSIS COMPLETE**  
**Last Updated**: 2025-10-25

