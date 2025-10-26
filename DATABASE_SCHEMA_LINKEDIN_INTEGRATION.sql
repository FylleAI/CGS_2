-- ============================================================================
-- LinkedIn Integration - Database Schema
-- ============================================================================
-- Version: 1.0
-- Date: 2025-10-25
-- Description: Schema per LinkedIn OAuth credentials e publication tracking
-- ============================================================================

-- ============================================================================
-- TABLE 1: linkedin_credentials
-- ============================================================================
-- Stores OAuth credentials per LinkedIn accounts (member & organization)
-- Multi-tenant aware con encryption at rest per tokens

CREATE TABLE linkedin_credentials (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Multi-tenancy
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- LinkedIn Identity
    linkedin_person_urn VARCHAR(255) NOT NULL,  -- urn:li:person:ABC123
    linkedin_email VARCHAR(255),
    linkedin_name VARCHAR(255),
    linkedin_headline VARCHAR(500),
    linkedin_profile_url TEXT,
    
    -- Account Type
    account_type VARCHAR(50) NOT NULL DEFAULT 'member',  -- 'member' or 'organization'
    organization_urn VARCHAR(255),  -- urn:li:organization:123 (if account_type='organization')
    organization_name VARCHAR(255),
    
    -- OAuth Tokens (encrypted at rest)
    access_token TEXT NOT NULL,
    refresh_token TEXT NOT NULL,
    token_type VARCHAR(50) DEFAULT 'Bearer',
    
    -- Token Expiration
    access_token_expires_at TIMESTAMP NOT NULL,
    refresh_token_expires_at TIMESTAMP NOT NULL,
    
    -- Scopes
    scopes TEXT[] NOT NULL,  -- ['profile', 'email', 'w_member_social']
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    last_used_at TIMESTAMP,
    last_refresh_at TIMESTAMP,
    
    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT linkedin_credentials_tenant_person_unique UNIQUE(tenant_id, linkedin_person_urn),
    CONSTRAINT linkedin_credentials_account_type_check CHECK (account_type IN ('member', 'organization')),
    CONSTRAINT linkedin_credentials_scopes_not_empty CHECK (array_length(scopes, 1) > 0),
    CONSTRAINT linkedin_credentials_org_urn_check CHECK (
        (account_type = 'organization' AND organization_urn IS NOT NULL) OR
        (account_type = 'member' AND organization_urn IS NULL)
    )
);

-- Indexes
CREATE INDEX idx_linkedin_credentials_tenant ON linkedin_credentials(tenant_id);
CREATE INDEX idx_linkedin_credentials_user ON linkedin_credentials(user_id);
CREATE INDEX idx_linkedin_credentials_person_urn ON linkedin_credentials(linkedin_person_urn);
CREATE INDEX idx_linkedin_credentials_access_expires ON linkedin_credentials(access_token_expires_at) 
    WHERE is_active = true;
CREATE INDEX idx_linkedin_credentials_refresh_expires ON linkedin_credentials(refresh_token_expires_at) 
    WHERE is_active = true;
CREATE INDEX idx_linkedin_credentials_active ON linkedin_credentials(tenant_id, is_active);

-- Trigger: Update updated_at
CREATE TRIGGER linkedin_credentials_updated_at
    BEFORE UPDATE ON linkedin_credentials
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Comments
COMMENT ON TABLE linkedin_credentials IS 'Stores LinkedIn OAuth credentials for members and organizations';
COMMENT ON COLUMN linkedin_credentials.linkedin_person_urn IS 'LinkedIn person URN (urn:li:person:ABC123)';
COMMENT ON COLUMN linkedin_credentials.access_token IS 'Encrypted OAuth access token (60 days validity)';
COMMENT ON COLUMN linkedin_credentials.refresh_token IS 'Encrypted OAuth refresh token (365 days validity)';

-- ============================================================================
-- TABLE 2: linkedin_publications
-- ============================================================================
-- Tracks all LinkedIn post publications with status and metadata

CREATE TABLE linkedin_publications (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Multi-tenancy
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    credential_id UUID NOT NULL REFERENCES linkedin_credentials(id) ON DELETE CASCADE,
    
    -- Content Reference
    content_id UUID REFERENCES contents(id) ON DELETE SET NULL,
    
    -- LinkedIn Post Info
    linkedin_post_urn VARCHAR(255),  -- urn:li:share:123 or urn:li:ugcPost:123
    linkedin_post_url TEXT,
    linkedin_post_id VARCHAR(255),  -- Extracted from URN
    
    -- Post Content
    post_type VARCHAR(50) NOT NULL,  -- 'text', 'image', 'video', 'article', 'multi_image', 'document'
    commentary TEXT NOT NULL,
    visibility VARCHAR(50) DEFAULT 'PUBLIC',  -- 'PUBLIC', 'CONNECTIONS'
    
    -- Media
    media_urns TEXT[],  -- ['urn:li:image:123', 'urn:li:video:456']
    media_count INTEGER DEFAULT 0,
    
    -- Article (for link posts)
    article_url TEXT,
    article_title VARCHAR(500),
    article_description TEXT,
    
    -- Status
    status VARCHAR(50) NOT NULL DEFAULT 'pending',  
    -- 'pending', 'publishing', 'published', 'failed', 'deleted', 'scheduled'
    
    error_code VARCHAR(100),
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    
    -- Timestamps
    published_at TIMESTAMP,
    scheduled_for TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT linkedin_publications_status_check CHECK (
        status IN ('pending', 'publishing', 'published', 'failed', 'deleted', 'scheduled')
    ),
    CONSTRAINT linkedin_publications_post_type_check CHECK (
        post_type IN ('text', 'image', 'video', 'article', 'multi_image', 'document', 'poll')
    ),
    CONSTRAINT linkedin_publications_retry_check CHECK (retry_count <= max_retries),
    CONSTRAINT linkedin_publications_media_count_check CHECK (media_count >= 0 AND media_count <= 9),
    CONSTRAINT linkedin_publications_scheduled_check CHECK (
        (status = 'scheduled' AND scheduled_for IS NOT NULL AND scheduled_for > NOW()) OR
        (status != 'scheduled')
    )
);

-- Indexes
CREATE INDEX idx_linkedin_publications_tenant ON linkedin_publications(tenant_id);
CREATE INDEX idx_linkedin_publications_credential ON linkedin_publications(credential_id);
CREATE INDEX idx_linkedin_publications_content ON linkedin_publications(content_id);
CREATE INDEX idx_linkedin_publications_status ON linkedin_publications(status);
CREATE INDEX idx_linkedin_publications_post_urn ON linkedin_publications(linkedin_post_urn);
CREATE INDEX idx_linkedin_publications_scheduled ON linkedin_publications(scheduled_for) 
    WHERE status = 'scheduled' AND scheduled_for IS NOT NULL;
CREATE INDEX idx_linkedin_publications_failed ON linkedin_publications(tenant_id, status, retry_count)
    WHERE status = 'failed' AND retry_count < max_retries;
CREATE INDEX idx_linkedin_publications_created_at ON linkedin_publications(created_at DESC);

-- Trigger: Update updated_at
CREATE TRIGGER linkedin_publications_updated_at
    BEFORE UPDATE ON linkedin_publications
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger: Update media_count
CREATE OR REPLACE FUNCTION update_linkedin_publication_media_count()
RETURNS TRIGGER AS $$
BEGIN
    NEW.media_count := COALESCE(array_length(NEW.media_urns, 1), 0);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER linkedin_publications_media_count
    BEFORE INSERT OR UPDATE OF media_urns ON linkedin_publications
    FOR EACH ROW
    EXECUTE FUNCTION update_linkedin_publication_media_count();

-- Comments
COMMENT ON TABLE linkedin_publications IS 'Tracks all LinkedIn post publications';
COMMENT ON COLUMN linkedin_publications.linkedin_post_urn IS 'LinkedIn post URN returned by API';
COMMENT ON COLUMN linkedin_publications.status IS 'Publication status: pending, publishing, published, failed, deleted, scheduled';
COMMENT ON COLUMN linkedin_publications.retry_count IS 'Number of retry attempts for failed publications';

-- ============================================================================
-- TABLE 3: linkedin_publication_events
-- ============================================================================
-- Event sourcing for publication lifecycle

CREATE TABLE linkedin_publication_events (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Foreign Keys
    publication_id UUID NOT NULL REFERENCES linkedin_publications(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Event Details
    event_type VARCHAR(50) NOT NULL,  
    -- 'created', 'publishing', 'published', 'failed', 'retry', 'deleted'
    
    event_data JSONB,  -- Additional event metadata
    
    -- Status Transition
    previous_status VARCHAR(50),
    new_status VARCHAR(50),
    
    -- Error Info (if applicable)
    error_code VARCHAR(100),
    error_message TEXT,
    
    -- Timestamp
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT linkedin_publication_events_type_check CHECK (
        event_type IN ('created', 'publishing', 'published', 'failed', 'retry', 'deleted', 'scheduled')
    )
);

-- Indexes
CREATE INDEX idx_linkedin_publication_events_publication ON linkedin_publication_events(publication_id);
CREATE INDEX idx_linkedin_publication_events_tenant ON linkedin_publication_events(tenant_id);
CREATE INDEX idx_linkedin_publication_events_type ON linkedin_publication_events(event_type);
CREATE INDEX idx_linkedin_publication_events_created_at ON linkedin_publication_events(created_at DESC);

-- Comments
COMMENT ON TABLE linkedin_publication_events IS 'Event sourcing for LinkedIn publication lifecycle';

-- ============================================================================
-- TABLE 4: linkedin_publication_performance
-- ============================================================================
-- Tracks performance metrics for published posts

CREATE TABLE linkedin_publication_performance (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Foreign Keys
    publication_id UUID NOT NULL REFERENCES linkedin_publications(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Engagement Metrics
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    
    -- Calculated Metrics
    engagement_rate DECIMAL(5, 2) DEFAULT 0.00,  -- (likes + comments + shares) / impressions * 100
    click_through_rate DECIMAL(5, 2) DEFAULT 0.00,  -- clicks / impressions * 100
    
    -- Timestamps
    fetched_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT linkedin_publication_performance_metrics_positive CHECK (
        impressions >= 0 AND clicks >= 0 AND likes >= 0 AND comments >= 0 AND shares >= 0
    ),
    CONSTRAINT linkedin_publication_performance_rates_valid CHECK (
        engagement_rate >= 0 AND engagement_rate <= 100 AND
        click_through_rate >= 0 AND click_through_rate <= 100
    )
);

-- Indexes
CREATE INDEX idx_linkedin_publication_performance_publication ON linkedin_publication_performance(publication_id);
CREATE INDEX idx_linkedin_publication_performance_tenant ON linkedin_publication_performance(tenant_id);
CREATE INDEX idx_linkedin_publication_performance_engagement ON linkedin_publication_performance(engagement_rate DESC);
CREATE INDEX idx_linkedin_publication_performance_fetched_at ON linkedin_publication_performance(fetched_at DESC);

-- Trigger: Update updated_at
CREATE TRIGGER linkedin_publication_performance_updated_at
    BEFORE UPDATE ON linkedin_publication_performance
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger: Calculate engagement metrics
CREATE OR REPLACE FUNCTION calculate_linkedin_engagement_metrics()
RETURNS TRIGGER AS $$
BEGIN
    -- Calculate engagement rate
    IF NEW.impressions > 0 THEN
        NEW.engagement_rate := ROUND(
            ((NEW.likes + NEW.comments + NEW.shares)::DECIMAL / NEW.impressions * 100)::NUMERIC, 
            2
        );
        NEW.click_through_rate := ROUND(
            (NEW.clicks::DECIMAL / NEW.impressions * 100)::NUMERIC, 
            2
        );
    ELSE
        NEW.engagement_rate := 0.00;
        NEW.click_through_rate := 0.00;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER linkedin_publication_performance_calculate_metrics
    BEFORE INSERT OR UPDATE ON linkedin_publication_performance
    FOR EACH ROW
    EXECUTE FUNCTION calculate_linkedin_engagement_metrics();

-- Comments
COMMENT ON TABLE linkedin_publication_performance IS 'Tracks performance metrics for LinkedIn posts';
COMMENT ON COLUMN linkedin_publication_performance.engagement_rate IS 'Calculated as (likes + comments + shares) / impressions * 100';

-- ============================================================================
-- VIEWS
-- ============================================================================

-- View: Active LinkedIn Credentials
CREATE OR REPLACE VIEW v_active_linkedin_credentials AS
SELECT 
    c.id,
    c.tenant_id,
    c.user_id,
    c.linkedin_person_urn,
    c.linkedin_email,
    c.linkedin_name,
    c.account_type,
    c.organization_name,
    c.scopes,
    c.access_token_expires_at,
    c.refresh_token_expires_at,
    c.last_used_at,
    CASE 
        WHEN c.access_token_expires_at < NOW() THEN 'expired'
        WHEN c.access_token_expires_at < NOW() + INTERVAL '7 days' THEN 'expiring_soon'
        ELSE 'valid'
    END AS token_status
FROM linkedin_credentials c
WHERE c.is_active = true;

COMMENT ON VIEW v_active_linkedin_credentials IS 'Active LinkedIn credentials with token status';

-- View: LinkedIn Publication Summary
CREATE OR REPLACE VIEW v_linkedin_publication_summary AS
SELECT 
    p.id,
    p.tenant_id,
    p.credential_id,
    p.content_id,
    p.linkedin_post_urn,
    p.linkedin_post_url,
    p.post_type,
    p.status,
    p.published_at,
    p.scheduled_for,
    c.linkedin_name AS author_name,
    c.account_type,
    perf.impressions,
    perf.likes,
    perf.comments,
    perf.shares,
    perf.engagement_rate
FROM linkedin_publications p
LEFT JOIN linkedin_credentials c ON p.credential_id = c.id
LEFT JOIN linkedin_publication_performance perf ON p.id = perf.publication_id;

COMMENT ON VIEW v_linkedin_publication_summary IS 'LinkedIn publications with author and performance data';

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function: Get credentials needing refresh
CREATE OR REPLACE FUNCTION get_linkedin_credentials_needing_refresh(days_before INTEGER DEFAULT 7)
RETURNS TABLE (
    credential_id UUID,
    tenant_id UUID,
    linkedin_person_urn VARCHAR,
    access_token_expires_at TIMESTAMP,
    days_until_expiration INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id,
        c.tenant_id,
        c.linkedin_person_urn,
        c.access_token_expires_at,
        EXTRACT(DAY FROM (c.access_token_expires_at - NOW()))::INTEGER
    FROM linkedin_credentials c
    WHERE c.is_active = true
      AND c.access_token_expires_at < NOW() + (days_before || ' days')::INTERVAL
      AND c.access_token_expires_at > NOW()
    ORDER BY c.access_token_expires_at ASC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_linkedin_credentials_needing_refresh IS 'Returns credentials that need token refresh within specified days';

-- Function: Get scheduled publications ready to publish
CREATE OR REPLACE FUNCTION get_linkedin_scheduled_publications_ready()
RETURNS TABLE (
    publication_id UUID,
    tenant_id UUID,
    credential_id UUID,
    scheduled_for TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id,
        p.tenant_id,
        p.credential_id,
        p.scheduled_for
    FROM linkedin_publications p
    WHERE p.status = 'scheduled'
      AND p.scheduled_for <= NOW()
    ORDER BY p.scheduled_for ASC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_linkedin_scheduled_publications_ready IS 'Returns scheduled publications ready to be published';

-- ============================================================================
-- SAMPLE QUERIES
-- ============================================================================

-- Query 1: Get all publications for a tenant
-- SELECT * FROM v_linkedin_publication_summary WHERE tenant_id = 'xxx' ORDER BY created_at DESC;

-- Query 2: Get credentials expiring soon
-- SELECT * FROM get_linkedin_credentials_needing_refresh(7);

-- Query 3: Get scheduled publications ready to publish
-- SELECT * FROM get_linkedin_scheduled_publications_ready();

-- Query 4: Get publication success rate by tenant
-- SELECT 
--     tenant_id,
--     COUNT(*) AS total_publications,
--     COUNT(*) FILTER (WHERE status = 'published') AS successful,
--     COUNT(*) FILTER (WHERE status = 'failed') AS failed,
--     ROUND(COUNT(*) FILTER (WHERE status = 'published')::DECIMAL / COUNT(*) * 100, 2) AS success_rate
-- FROM linkedin_publications
-- GROUP BY tenant_id;

-- ============================================================================
-- ROLLBACK SCRIPT
-- ============================================================================

-- DROP VIEW IF EXISTS v_linkedin_publication_summary CASCADE;
-- DROP VIEW IF EXISTS v_active_linkedin_credentials CASCADE;
-- DROP FUNCTION IF EXISTS get_linkedin_credentials_needing_refresh(INTEGER) CASCADE;
-- DROP FUNCTION IF EXISTS get_linkedin_scheduled_publications_ready() CASCADE;
-- DROP FUNCTION IF EXISTS calculate_linkedin_engagement_metrics() CASCADE;
-- DROP FUNCTION IF EXISTS update_linkedin_publication_media_count() CASCADE;
-- DROP TABLE IF EXISTS linkedin_publication_performance CASCADE;
-- DROP TABLE IF EXISTS linkedin_publication_events CASCADE;
-- DROP TABLE IF EXISTS linkedin_publications CASCADE;
-- DROP TABLE IF EXISTS linkedin_credentials CASCADE;

