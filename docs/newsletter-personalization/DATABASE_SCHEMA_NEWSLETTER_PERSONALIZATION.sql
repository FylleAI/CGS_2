-- ============================================================================
-- Newsletter Personalization - Database Schema
-- ============================================================================
-- Version: 1.0
-- Date: 2025-10-25
-- Description: Complete database schema for personalized weekly newsletter system
-- ============================================================================

-- ============================================================================
-- 1. SUBSCRIPTION MANAGEMENT
-- ============================================================================

-- Newsletter Subscriptions
CREATE TABLE IF NOT EXISTS newsletter_subscriptions (
    subscription_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    user_id UUID,  -- Optional: link to auth.users if available
    user_email TEXT NOT NULL,
    company_snapshot_id UUID REFERENCES company_contexts(context_id) ON DELETE SET NULL,
    
    -- Subscription Status
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'paused', 'cancelled')),
    
    -- Delivery Preferences
    frequency TEXT NOT NULL DEFAULT 'weekly' CHECK (frequency IN ('weekly', 'biweekly', 'monthly')),
    preferred_day TEXT NOT NULL DEFAULT 'monday' CHECK (preferred_day IN ('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday')),
    preferred_time TIME NOT NULL DEFAULT '09:00:00',
    
    -- Content Preferences (JSONB for flexibility)
    preferences JSONB DEFAULT '{
        "include_competitors": true,
        "include_trends": true,
        "include_news": true,
        "include_insights": true,
        "max_competitors": 5,
        "max_trends": 3,
        "content_length": "medium",
        "format": "html"
    }'::jsonb,
    
    -- Topics of Interest
    topics_of_interest TEXT[] DEFAULT ARRAY[]::TEXT[],
    
    -- Unsubscribe
    unsubscribe_token TEXT UNIQUE NOT NULL,
    unsubscribed_at TIMESTAMPTZ,
    unsubscribe_reason TEXT,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_sent_at TIMESTAMPTZ,
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Indexes
CREATE INDEX idx_newsletter_subscriptions_tenant ON newsletter_subscriptions(tenant_id);
CREATE INDEX idx_newsletter_subscriptions_email ON newsletter_subscriptions(user_email);
CREATE INDEX idx_newsletter_subscriptions_status ON newsletter_subscriptions(status);
CREATE INDEX idx_newsletter_subscriptions_day ON newsletter_subscriptions(preferred_day) WHERE status = 'active';
CREATE INDEX idx_newsletter_subscriptions_company ON newsletter_subscriptions(company_snapshot_id);

-- Updated timestamp trigger
CREATE OR REPLACE FUNCTION update_newsletter_subscriptions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_newsletter_subscriptions_updated_at
    BEFORE UPDATE ON newsletter_subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_newsletter_subscriptions_updated_at();

-- ============================================================================
-- 2. COMPETITOR TRACKING
-- ============================================================================

-- Competitors
CREATE TABLE IF NOT EXISTS competitors (
    competitor_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    company_id UUID REFERENCES company_contexts(context_id) ON DELETE CASCADE,
    
    -- Competitor Info
    competitor_name TEXT NOT NULL,
    competitor_website TEXT,
    competitor_industry TEXT,
    competitor_description TEXT,
    
    -- Relationship
    relationship_type TEXT DEFAULT 'direct' CHECK (relationship_type IN ('direct', 'indirect', 'emerging', 'adjacent')),
    
    -- Monitoring
    monitoring_enabled BOOLEAN DEFAULT true,
    last_researched_at TIMESTAMPTZ,
    research_frequency_days INTEGER DEFAULT 7,
    
    -- Snapshot (CompanySnapshot-like structure)
    snapshot JSONB DEFAULT '{}'::jsonb,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,
    
    UNIQUE(tenant_id, company_id, competitor_name)
);

-- Competitor Activities
CREATE TABLE IF NOT EXISTS competitor_activities (
    activity_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    competitor_id UUID REFERENCES competitors(competitor_id) ON DELETE CASCADE,
    
    -- Activity Info
    activity_type TEXT NOT NULL CHECK (activity_type IN ('product_launch', 'funding', 'news', 'hiring', 'partnership', 'acquisition', 'other')),
    title TEXT NOT NULL,
    description TEXT,
    source_url TEXT,
    published_at TIMESTAMPTZ,
    
    -- Relevance
    relevance_score FLOAT CHECK (relevance_score >= 0 AND relevance_score <= 1),
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Indexes
CREATE INDEX idx_competitors_tenant ON competitors(tenant_id);
CREATE INDEX idx_competitors_company ON competitors(company_id);
CREATE INDEX idx_competitors_monitoring ON competitors(monitoring_enabled) WHERE monitoring_enabled = true;
CREATE INDEX idx_competitor_activities_competitor ON competitor_activities(competitor_id);
CREATE INDEX idx_competitor_activities_published ON competitor_activities(published_at DESC);
CREATE INDEX idx_competitor_activities_type ON competitor_activities(activity_type);

-- ============================================================================
-- 3. MARKET TRENDS
-- ============================================================================

-- Market Trends
CREATE TABLE IF NOT EXISTS market_trends (
    trend_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Trend Info
    industry TEXT NOT NULL,
    trend_name TEXT NOT NULL,
    trend_description TEXT,
    trend_category TEXT CHECK (trend_category IN ('technology', 'regulation', 'consumer_behavior', 'economic', 'competitive', 'other')),
    
    -- Detection
    first_detected_at TIMESTAMPTZ DEFAULT NOW(),
    last_updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Momentum (0-1: growing, stable, declining)
    momentum_score FLOAT CHECK (momentum_score >= 0 AND momentum_score <= 1),
    momentum_direction TEXT CHECK (momentum_direction IN ('growing', 'stable', 'declining')),
    
    -- Sources
    sources JSONB DEFAULT '[]'::jsonb,  -- Array of {url, title, published_at}
    keywords TEXT[] DEFAULT ARRAY[]::TEXT[],
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,
    
    UNIQUE(industry, trend_name)
);

-- User Trend Relevance (many-to-many)
CREATE TABLE IF NOT EXISTS user_trend_relevance (
    relevance_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    subscription_id UUID REFERENCES newsletter_subscriptions(subscription_id) ON DELETE CASCADE,
    trend_id UUID REFERENCES market_trends(trend_id) ON DELETE CASCADE,
    
    -- Relevance
    relevance_score FLOAT NOT NULL CHECK (relevance_score >= 0 AND relevance_score <= 1),
    reason TEXT,  -- Why this trend is relevant
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(subscription_id, trend_id)
);

-- Indexes
CREATE INDEX idx_market_trends_industry ON market_trends(industry);
CREATE INDEX idx_market_trends_category ON market_trends(trend_category);
CREATE INDEX idx_market_trends_momentum ON market_trends(momentum_score DESC);
CREATE INDEX idx_user_trend_relevance_subscription ON user_trend_relevance(subscription_id);
CREATE INDEX idx_user_trend_relevance_trend ON user_trend_relevance(trend_id);
CREATE INDEX idx_user_trend_relevance_score ON user_trend_relevance(relevance_score DESC);

-- ============================================================================
-- 4. NEWSLETTER CONTENT
-- ============================================================================

-- Newsletter Editions
CREATE TABLE IF NOT EXISTS newsletter_editions (
    edition_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    subscription_id UUID REFERENCES newsletter_subscriptions(subscription_id) ON DELETE CASCADE,
    
    -- Edition Info
    edition_date DATE NOT NULL,
    edition_number INTEGER,  -- Sequential number per subscription
    
    -- Content
    content JSONB NOT NULL,  -- Full newsletter content structure
    html_content TEXT,  -- Rendered HTML
    plain_text_content TEXT,  -- Plain text version
    
    -- Generation
    workflow_run_id UUID,  -- Link to workflow_runs table
    generation_status TEXT DEFAULT 'pending' CHECK (generation_status IN ('pending', 'generating', 'completed', 'failed')),
    generated_at TIMESTAMPTZ,
    generation_duration_ms INTEGER,
    generation_cost_usd NUMERIC(10, 6),
    
    -- Delivery
    delivery_status TEXT DEFAULT 'pending' CHECK (delivery_status IN ('pending', 'scheduled', 'sent', 'failed', 'cancelled')),
    scheduled_for TIMESTAMPTZ,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,
    
    UNIQUE(subscription_id, edition_date)
);

-- Indexes
CREATE INDEX idx_newsletter_editions_tenant ON newsletter_editions(tenant_id);
CREATE INDEX idx_newsletter_editions_subscription ON newsletter_editions(subscription_id);
CREATE INDEX idx_newsletter_editions_date ON newsletter_editions(edition_date DESC);
CREATE INDEX idx_newsletter_editions_status ON newsletter_editions(delivery_status);
CREATE INDEX idx_newsletter_editions_scheduled ON newsletter_editions(scheduled_for) WHERE delivery_status = 'scheduled';

-- ============================================================================
-- 5. DELIVERY & ANALYTICS
-- ============================================================================

-- Newsletter Deliveries
CREATE TABLE IF NOT EXISTS newsletter_deliveries (
    delivery_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    edition_id UUID REFERENCES newsletter_editions(edition_id) ON DELETE CASCADE,
    subscription_id UUID REFERENCES newsletter_subscriptions(subscription_id) ON DELETE CASCADE,
    
    -- Delivery Info
    sent_at TIMESTAMPTZ,
    delivery_status TEXT NOT NULL CHECK (delivery_status IN ('sent', 'bounced', 'failed', 'spam')),
    brevo_message_id TEXT,
    
    -- Engagement
    opened_at TIMESTAMPTZ,
    first_click_at TIMESTAMPTZ,
    click_count INTEGER DEFAULT 0,
    
    -- Unsubscribe
    unsubscribed_at TIMESTAMPTZ,
    
    -- Error Info
    error_message TEXT,
    bounce_type TEXT,  -- hard, soft, spam
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Newsletter Engagement Events
CREATE TABLE IF NOT EXISTS newsletter_engagement (
    engagement_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    delivery_id UUID REFERENCES newsletter_deliveries(delivery_id) ON DELETE CASCADE,
    
    -- Event Info
    event_type TEXT NOT NULL CHECK (event_type IN ('open', 'click', 'forward', 'reply', 'print')),
    event_data JSONB DEFAULT '{}'::jsonb,  -- {link_url, section, etc.}
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Newsletter Feedback
CREATE TABLE IF NOT EXISTS newsletter_feedback (
    feedback_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    delivery_id UUID REFERENCES newsletter_deliveries(delivery_id) ON DELETE CASCADE,
    
    -- Feedback
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    feedback_text TEXT,
    feedback_category TEXT,  -- too_long, not_relevant, too_frequent, etc.
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_newsletter_deliveries_edition ON newsletter_deliveries(edition_id);
CREATE INDEX idx_newsletter_deliveries_subscription ON newsletter_deliveries(subscription_id);
CREATE INDEX idx_newsletter_deliveries_sent ON newsletter_deliveries(sent_at DESC);
CREATE INDEX idx_newsletter_deliveries_opened ON newsletter_deliveries(opened_at) WHERE opened_at IS NOT NULL;
CREATE INDEX idx_newsletter_engagement_delivery ON newsletter_engagement(delivery_id);
CREATE INDEX idx_newsletter_engagement_type ON newsletter_engagement(event_type);
CREATE INDEX idx_newsletter_feedback_delivery ON newsletter_feedback(delivery_id);
CREATE INDEX idx_newsletter_feedback_rating ON newsletter_feedback(rating);

-- ============================================================================
-- 6. JOB SCHEDULING
-- ============================================================================

-- Newsletter Jobs
CREATE TABLE IF NOT EXISTS newsletter_jobs (
    job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subscription_id UUID REFERENCES newsletter_subscriptions(subscription_id) ON DELETE CASCADE,
    edition_id UUID REFERENCES newsletter_editions(edition_id) ON DELETE SET NULL,
    
    -- Job Info
    job_type TEXT NOT NULL CHECK (job_type IN ('generate', 'send', 'research_competitors', 'identify_trends')),
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    
    -- Scheduling
    scheduled_at TIMESTAMPTZ NOT NULL,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    
    -- Execution
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    error_message TEXT,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Indexes
CREATE INDEX idx_newsletter_jobs_subscription ON newsletter_jobs(subscription_id);
CREATE INDEX idx_newsletter_jobs_status ON newsletter_jobs(status);
CREATE INDEX idx_newsletter_jobs_scheduled ON newsletter_jobs(scheduled_at) WHERE status = 'pending';
CREATE INDEX idx_newsletter_jobs_type ON newsletter_jobs(job_type);

-- ============================================================================
-- 7. VIEWS
-- ============================================================================

-- Active Subscriptions View
CREATE OR REPLACE VIEW active_subscriptions AS
SELECT 
    s.*,
    c.company_name,
    c.company_display_name,
    c.industry
FROM newsletter_subscriptions s
LEFT JOIN company_contexts c ON s.company_snapshot_id = c.context_id
WHERE s.status = 'active';

-- Newsletter Performance View
CREATE OR REPLACE VIEW newsletter_performance AS
SELECT 
    e.edition_id,
    e.subscription_id,
    e.edition_date,
    d.delivery_status,
    d.sent_at,
    d.opened_at,
    d.click_count,
    CASE WHEN d.opened_at IS NOT NULL THEN 1 ELSE 0 END AS opened,
    CASE WHEN d.first_click_at IS NOT NULL THEN 1 ELSE 0 END AS clicked,
    f.rating AS feedback_rating,
    e.generation_cost_usd
FROM newsletter_editions e
LEFT JOIN newsletter_deliveries d ON e.edition_id = d.edition_id
LEFT JOIN newsletter_feedback f ON d.delivery_id = f.delivery_id;

-- Subscription Engagement Metrics View
CREATE OR REPLACE VIEW subscription_engagement_metrics AS
SELECT 
    s.subscription_id,
    s.user_email,
    s.status,
    COUNT(DISTINCT e.edition_id) AS total_newsletters_sent,
    COUNT(DISTINCT CASE WHEN d.opened_at IS NOT NULL THEN e.edition_id END) AS newsletters_opened,
    COUNT(DISTINCT CASE WHEN d.first_click_at IS NOT NULL THEN e.edition_id END) AS newsletters_clicked,
    ROUND(
        COUNT(DISTINCT CASE WHEN d.opened_at IS NOT NULL THEN e.edition_id END)::NUMERIC / 
        NULLIF(COUNT(DISTINCT e.edition_id), 0) * 100, 
        2
    ) AS open_rate_pct,
    ROUND(
        COUNT(DISTINCT CASE WHEN d.first_click_at IS NOT NULL THEN e.edition_id END)::NUMERIC / 
        NULLIF(COUNT(DISTINCT e.edition_id), 0) * 100, 
        2
    ) AS click_rate_pct,
    AVG(f.rating) AS avg_rating,
    MAX(d.sent_at) AS last_newsletter_sent_at
FROM newsletter_subscriptions s
LEFT JOIN newsletter_editions e ON s.subscription_id = e.subscription_id
LEFT JOIN newsletter_deliveries d ON e.edition_id = d.edition_id
LEFT JOIN newsletter_feedback f ON d.delivery_id = f.delivery_id
GROUP BY s.subscription_id, s.user_email, s.status;

-- ============================================================================
-- 8. FUNCTIONS
-- ============================================================================

-- Function: Get Active Subscriptions for Day
CREATE OR REPLACE FUNCTION get_active_subscriptions_for_day(day_name TEXT)
RETURNS TABLE (
    subscription_id UUID,
    user_email TEXT,
    company_snapshot_id UUID,
    preferences JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.subscription_id,
        s.user_email,
        s.company_snapshot_id,
        s.preferences
    FROM newsletter_subscriptions s
    WHERE s.status = 'active'
      AND s.preferred_day = day_name
      AND (s.last_sent_at IS NULL OR s.last_sent_at < NOW() - INTERVAL '6 days');
END;
$$ LANGUAGE plpgsql;

-- Function: Calculate Engagement Score
CREATE OR REPLACE FUNCTION calculate_engagement_score(sub_id UUID)
RETURNS NUMERIC AS $$
DECLARE
    score NUMERIC := 0;
    open_rate NUMERIC;
    click_rate NUMERIC;
    avg_rating NUMERIC;
BEGIN
    SELECT 
        open_rate_pct / 100.0,
        click_rate_pct / 100.0,
        COALESCE(avg_rating / 5.0, 0)
    INTO open_rate, click_rate, avg_rating
    FROM subscription_engagement_metrics
    WHERE subscription_id = sub_id;
    
    -- Weighted score: 40% open rate, 40% click rate, 20% rating
    score := (COALESCE(open_rate, 0) * 0.4) + 
             (COALESCE(click_rate, 0) * 0.4) + 
             (COALESCE(avg_rating, 0) * 0.2);
    
    RETURN ROUND(score, 3);
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 9. SAMPLE QUERIES
-- ============================================================================

-- Get subscriptions due for newsletter today (Monday)
-- SELECT * FROM get_active_subscriptions_for_day('monday');

-- Get engagement metrics for all subscriptions
-- SELECT * FROM subscription_engagement_metrics ORDER BY open_rate_pct DESC;

-- Get top performing newsletters
-- SELECT * FROM newsletter_performance WHERE opened = 1 ORDER BY click_count DESC LIMIT 10;

-- Identify churn risk (no opens in last 3 newsletters)
-- SELECT s.subscription_id, s.user_email
-- FROM newsletter_subscriptions s
-- WHERE s.status = 'active'
--   AND NOT EXISTS (
--       SELECT 1 FROM newsletter_deliveries d
--       JOIN newsletter_editions e ON d.edition_id = e.edition_id
--       WHERE e.subscription_id = s.subscription_id
--         AND d.opened_at IS NOT NULL
--         AND d.sent_at > NOW() - INTERVAL '21 days'
--   );

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================

