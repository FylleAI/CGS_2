-- ============================================================================
-- Migration 004: Adaptive Knowledge Base - Context Cards System
-- Purpose: Create granular, multi-tenant, evolving knowledge cards
-- Author: Fylle Team
-- Date: 2025-10-25
-- ============================================================================

-- ============================================================================
-- TABLE: context_cards (Core Knowledge Units)
-- ============================================================================

CREATE TABLE IF NOT EXISTS context_cards (
    -- Identity
    card_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,  -- Multi-tenant support
    
    -- Card Type (Atomic & Complete)
    card_type TEXT NOT NULL CHECK (card_type IN (
        'product',      -- Product/Service card
        'persona',      -- Target audience/ICP card
        'campaign',     -- Campaign/Project card
        'topic',        -- Topic/Theme card
        'brand_voice',  -- Brand voice guidelines card
        'competitor',   -- Competitor analysis card
        'performance',  -- Performance metrics card
        'insight'       -- AI-generated insight card
    )),
    
    -- Metadata
    title TEXT NOT NULL,
    description TEXT,
    category TEXT,  -- For grouping (e.g., 'marketing', 'sales', 'product')
    tags TEXT[] DEFAULT '{}',
    
    -- Content (JSONB for flexibility - structure varies by card_type)
    content JSONB NOT NULL,
    
    -- Versioning (Evolutionary)
    version INTEGER NOT NULL DEFAULT 1,
    is_active BOOLEAN NOT NULL DEFAULT true,
    parent_card_id UUID REFERENCES context_cards(card_id),  -- Previous version
    
    -- Lifecycle
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by TEXT NOT NULL,  -- 'user:{user_id}', 'agent:{agent_name}', 'automation:{job_name}'
    updated_by TEXT,
    
    -- Performance Metrics (Measurable)
    metrics JSONB DEFAULT '{}'::jsonb,  -- {ctr, engagement_rate, conversion_rate, etc.}
    
    -- Quality Signals
    confidence_score FLOAT DEFAULT 0.8 CHECK (confidence_score >= 0 AND confidence_score <= 1),
    quality_score FLOAT CHECK (quality_score IS NULL OR (quality_score >= 0 AND quality_score <= 1)),
    
    -- Usage Tracking
    usage_count INTEGER DEFAULT 0 CHECK (usage_count >= 0),
    last_used_at TIMESTAMPTZ,
    
    -- Source Tracking
    source_session_id UUID,  -- Onboarding session that created this
    source_workflow_id UUID, -- Workflow run that created this
    
    -- Constraints
    CONSTRAINT unique_card_version UNIQUE (card_id, version)
);

-- ============================================================================
-- TABLE: card_relationships (Linkable)
-- ============================================================================

CREATE TABLE IF NOT EXISTS card_relationships (
    relationship_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Cards
    source_card_id UUID NOT NULL REFERENCES context_cards(card_id) ON DELETE CASCADE,
    target_card_id UUID NOT NULL REFERENCES context_cards(card_id) ON DELETE CASCADE,
    
    -- Relationship Type
    relationship_type TEXT NOT NULL CHECK (relationship_type IN (
        'references',    -- Source references target
        'supports',      -- Source supports/validates target
        'contradicts',   -- Source contradicts target
        'extends',       -- Source extends/builds on target
        'derived_from',  -- Source was derived from target (e.g., insight from data)
        'replaces',      -- Source replaces target (deprecation)
        'requires'       -- Source requires target (dependency)
    )),
    
    -- Relationship Strength (0-1)
    strength FLOAT DEFAULT 1.0 CHECK (strength >= 0 AND strength <= 1),
    
    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Constraints
    CONSTRAINT unique_relationship UNIQUE (source_card_id, target_card_id, relationship_type),
    CONSTRAINT no_self_reference CHECK (source_card_id != target_card_id)
);

-- ============================================================================
-- TABLE: card_feedback (Evolutionary)
-- ============================================================================

CREATE TABLE IF NOT EXISTS card_feedback (
    feedback_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    card_id UUID NOT NULL REFERENCES context_cards(card_id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL,
    
    -- Feedback Source
    source_type TEXT NOT NULL CHECK (source_type IN (
        'user_edit',        -- User manually edited card
        'user_rating',      -- User rated card (thumbs up/down)
        'user_suggestion',  -- User suggested improvement
        'performance_data', -- Performance metrics updated
        'ab_test',          -- A/B test result
        'agent_update',     -- Agent updated card
        'automation'        -- Automated update
    )),
    source_id TEXT,  -- User ID, agent name, job name, etc.
    
    -- Feedback Content
    feedback_type TEXT NOT NULL CHECK (feedback_type IN (
        'correction',      -- Factual correction
        'enhancement',     -- Improvement suggestion
        'validation',      -- Positive validation
        'metric_update',   -- Performance metric update
        'quality_issue'    -- Quality problem reported
    )),
    feedback_data JSONB NOT NULL,  -- Structured feedback data
    
    -- Impact Tracking
    applied BOOLEAN DEFAULT false,
    applied_at TIMESTAMPTZ,
    applied_by TEXT,
    impact_score FLOAT CHECK (impact_score IS NULL OR (impact_score >= 0 AND impact_score <= 1)),
    
    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- ============================================================================
-- TABLE: card_performance_events (Measurable)
-- ============================================================================

CREATE TABLE IF NOT EXISTS card_performance_events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    card_id UUID NOT NULL REFERENCES context_cards(card_id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL,
    
    -- Event Details
    event_type TEXT NOT NULL CHECK (event_type IN (
        'content_generated',  -- Content was generated using this card
        'content_published',  -- Content was published
        'engagement',         -- User engaged with content
        'conversion',         -- Conversion event
        'view',              -- Card was viewed
        'edit',              -- Card was edited
        'share'              -- Card was shared
    )),
    event_data JSONB NOT NULL,  -- {channel, content_type, content_id, etc.}
    
    -- Performance Metrics
    ctr FLOAT CHECK (ctr IS NULL OR (ctr >= 0 AND ctr <= 1)),
    engagement_rate FLOAT CHECK (engagement_rate IS NULL OR (engagement_rate >= 0 AND engagement_rate <= 1)),
    conversion_rate FLOAT CHECK (conversion_rate IS NULL OR (conversion_rate >= 0 AND conversion_rate <= 1)),
    
    -- Context
    workflow_run_id UUID,
    content_id UUID,
    
    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- ============================================================================
-- INDEXES
-- ============================================================================

-- context_cards indexes
CREATE INDEX IF NOT EXISTS idx_cards_tenant_type 
ON context_cards(tenant_id, card_type) 
WHERE is_active = true;

CREATE INDEX IF NOT EXISTS idx_cards_category 
ON context_cards(category) 
WHERE is_active = true;

CREATE INDEX IF NOT EXISTS idx_cards_tags 
ON context_cards USING GIN(tags);

CREATE INDEX IF NOT EXISTS idx_cards_updated 
ON context_cards(updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_cards_quality 
ON context_cards(quality_score DESC NULLS LAST) 
WHERE is_active = true;

CREATE INDEX IF NOT EXISTS idx_cards_usage 
ON context_cards(usage_count DESC) 
WHERE is_active = true;

-- Full-text search on card content
CREATE INDEX IF NOT EXISTS idx_cards_fts 
ON context_cards USING GIN(
    to_tsvector('english', 
        title || ' ' || 
        COALESCE(description, '') || ' ' || 
        COALESCE(category, '')
    )
);

-- card_relationships indexes
CREATE INDEX IF NOT EXISTS idx_relationships_source 
ON card_relationships(source_card_id);

CREATE INDEX IF NOT EXISTS idx_relationships_target 
ON card_relationships(target_card_id);

CREATE INDEX IF NOT EXISTS idx_relationships_type 
ON card_relationships(relationship_type);

-- card_feedback indexes
CREATE INDEX IF NOT EXISTS idx_feedback_card 
ON card_feedback(card_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_feedback_pending 
ON card_feedback(tenant_id, created_at DESC) 
WHERE applied = false;

CREATE INDEX IF NOT EXISTS idx_feedback_source 
ON card_feedback(source_type, source_id);

-- card_performance_events indexes
CREATE INDEX IF NOT EXISTS idx_performance_card 
ON card_performance_events(card_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_performance_tenant 
ON card_performance_events(tenant_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_performance_type 
ON card_performance_events(event_type, created_at DESC);

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to normalize card title for matching
CREATE OR REPLACE FUNCTION normalize_card_title(title TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN LOWER(REGEXP_REPLACE(title, '[^a-zA-Z0-9]', '', 'g'));
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to calculate quality score
CREATE OR REPLACE FUNCTION calculate_quality_score(
    p_card_id UUID,
    p_performance_weight FLOAT DEFAULT 0.6,
    p_feedback_weight FLOAT DEFAULT 0.3,
    p_confidence_weight FLOAT DEFAULT 0.1
)
RETURNS FLOAT AS $$
DECLARE
    v_performance_score FLOAT;
    v_feedback_score FLOAT;
    v_confidence_score FLOAT;
    v_quality_score FLOAT;
BEGIN
    -- Get average performance metrics (last 30 days)
    SELECT AVG(COALESCE(engagement_rate, 0))
    INTO v_performance_score
    FROM card_performance_events
    WHERE card_id = p_card_id
    AND created_at > NOW() - INTERVAL '30 days';
    
    -- Get feedback sentiment score
    SELECT 
        CASE 
            WHEN COUNT(*) = 0 THEN 0.5
            ELSE (
                COUNT(*) FILTER (WHERE feedback_type = 'validation') * 1.0 +
                COUNT(*) FILTER (WHERE feedback_type = 'enhancement') * 0.7 +
                COUNT(*) FILTER (WHERE feedback_type = 'correction') * 0.3 +
                COUNT(*) FILTER (WHERE feedback_type = 'quality_issue') * 0.0
            ) / COUNT(*)
        END
    INTO v_feedback_score
    FROM card_feedback
    WHERE card_id = p_card_id
    AND created_at > NOW() - INTERVAL '30 days';
    
    -- Get confidence score
    SELECT confidence_score
    INTO v_confidence_score
    FROM context_cards
    WHERE card_id = p_card_id;
    
    -- Calculate weighted average
    v_quality_score := 
        COALESCE(v_performance_score, 0.5) * p_performance_weight +
        COALESCE(v_feedback_score, 0.5) * p_feedback_weight +
        COALESCE(v_confidence_score, 0.8) * p_confidence_weight;
    
    RETURN v_quality_score;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_cards_updated_at
BEFORE UPDATE ON context_cards
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VIEWS
-- ============================================================================

-- View for active cards with computed metrics
CREATE OR REPLACE VIEW v_active_cards AS
SELECT 
    c.*,
    COUNT(DISTINCT r.relationship_id) as relationship_count,
    COUNT(DISTINCT f.feedback_id) as feedback_count,
    COUNT(DISTINCT p.event_id) as performance_event_count
FROM context_cards c
LEFT JOIN card_relationships r ON c.card_id = r.source_card_id OR c.card_id = r.target_card_id
LEFT JOIN card_feedback f ON c.card_id = f.card_id
LEFT JOIN card_performance_events p ON c.card_id = p.card_id
WHERE c.is_active = true
GROUP BY c.card_id;

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE context_cards IS 'Atomic knowledge units that evolve with data, feedback, and performance';
COMMENT ON COLUMN context_cards.card_type IS 'Type of knowledge: product, persona, campaign, topic, brand_voice, competitor, performance, insight';
COMMENT ON COLUMN context_cards.content IS 'JSONB content structure varies by card_type';
COMMENT ON COLUMN context_cards.metrics IS 'Performance metrics: {ctr, engagement_rate, conversion_rate, etc.}';
COMMENT ON COLUMN context_cards.quality_score IS 'Computed quality score (0-1) based on performance + feedback + confidence';
COMMENT ON COLUMN context_cards.created_by IS 'Format: user:{id}, agent:{name}, automation:{job}';

COMMENT ON TABLE card_relationships IS 'Links between cards forming a knowledge graph';
COMMENT ON COLUMN card_relationships.relationship_type IS 'Type: references, supports, contradicts, extends, derived_from, replaces, requires';
COMMENT ON COLUMN card_relationships.strength IS 'Relationship strength (0-1)';

COMMENT ON TABLE card_feedback IS 'Feedback from users, agents, and automation for card evolution';
COMMENT ON COLUMN card_feedback.source_type IS 'Source: user_edit, user_rating, performance_data, ab_test, agent_update, automation';
COMMENT ON COLUMN card_feedback.feedback_type IS 'Type: correction, enhancement, validation, metric_update, quality_issue';

COMMENT ON TABLE card_performance_events IS 'Time-series performance events for cards';
COMMENT ON COLUMN card_performance_events.event_type IS 'Event: content_generated, content_published, engagement, conversion, view, edit, share';

-- ============================================================================
-- SAMPLE QUERIES (for reference)
-- ============================================================================

-- Find all active cards for a tenant by type
-- SELECT * FROM context_cards 
-- WHERE tenant_id = 'xxx' 
-- AND card_type = 'persona' 
-- AND is_active = true 
-- ORDER BY quality_score DESC NULLS LAST;

-- Get related cards
-- SELECT c.* 
-- FROM context_cards c
-- JOIN card_relationships r ON c.card_id = r.target_card_id
-- WHERE r.source_card_id = 'xxx'
-- AND r.relationship_type = 'references';

-- Get pending feedback for a tenant
-- SELECT * FROM card_feedback
-- WHERE tenant_id = 'xxx'
-- AND applied = false
-- ORDER BY created_at DESC;

-- Get top performing cards
-- SELECT c.card_id, c.title, AVG(p.engagement_rate) as avg_engagement
-- FROM context_cards c
-- JOIN card_performance_events p ON c.card_id = p.card_id
-- WHERE c.tenant_id = 'xxx'
-- AND p.created_at > NOW() - INTERVAL '30 days'
-- GROUP BY c.card_id, c.title
-- ORDER BY avg_engagement DESC
-- LIMIT 10;

