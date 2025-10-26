-- ============================================================================
-- Migration 004: HubSpot Integration - Native Content Publishing
-- Purpose: Enable native publishing of generated content to HubSpot
-- Author: Fylle Team
-- Date: 2025-10-25
-- ============================================================================

-- ============================================================================
-- TABLE: hubspot_credentials (Multi-Tenant Credential Management)
-- ============================================================================

CREATE TABLE IF NOT EXISTS hubspot_credentials (
    -- Identity
    credential_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,  -- Multi-tenant support
    
    -- HubSpot Portal
    portal_id TEXT NOT NULL,  -- HubSpot portal/account ID
    portal_name TEXT,  -- Human-readable portal name
    
    -- Authentication
    auth_type TEXT NOT NULL CHECK (auth_type IN ('private_app', 'oauth')),
    access_token TEXT NOT NULL,  -- Encrypted at application level
    refresh_token TEXT,  -- For OAuth only
    token_expires_at TIMESTAMPTZ,  -- For OAuth (6 hours)
    scopes TEXT[] DEFAULT '{}',  -- OAuth scopes granted
    
    -- Status
    is_active BOOLEAN NOT NULL DEFAULT true,
    last_used_at TIMESTAMPTZ,
    
    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by TEXT NOT NULL,  -- user:{id} or system
    
    -- Constraints
    CONSTRAINT unique_tenant_portal UNIQUE (tenant_id, portal_id)
);

-- ============================================================================
-- TABLE: content_publications (Publication Tracking)
-- ============================================================================

CREATE TABLE IF NOT EXISTS content_publications (
    -- Identity
    publication_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id UUID NOT NULL,  -- FK to content (from CGS or onboarding)
    tenant_id UUID NOT NULL,
    
    -- Platform
    platform TEXT NOT NULL CHECK (platform IN (
        'hubspot_blog',
        'hubspot_social_linkedin',
        'hubspot_social_twitter',
        'hubspot_social_facebook',
        'hubspot_email',
        'hubspot_landing_page'
    )),
    
    -- HubSpot IDs
    credential_id UUID NOT NULL REFERENCES hubspot_credentials(credential_id),
    platform_content_id TEXT,  -- HubSpot blog post ID, broadcast ID, email ID, etc.
    platform_url TEXT,  -- Published URL (e.g., https://blog.company.com/post-slug)
    
    -- Status
    status TEXT NOT NULL CHECK (status IN (
        'pending',      -- Waiting to be published
        'publishing',   -- Currently being published
        'published',    -- Successfully published
        'failed',       -- Publication failed
        'scheduled',    -- Scheduled for future publication
        'cancelled'     -- Cancelled by user
    )) DEFAULT 'pending',
    
    -- Scheduling
    scheduled_at TIMESTAMPTZ,  -- When to publish (for scheduled publications)
    published_at TIMESTAMPTZ,  -- When actually published
    
    -- Error Handling
    error_message TEXT,
    error_code TEXT,
    retry_count INTEGER DEFAULT 0 CHECK (retry_count >= 0),
    max_retries INTEGER DEFAULT 5,
    last_retry_at TIMESTAMPTZ,
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,  -- Platform-specific metadata
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT check_scheduled_at CHECK (
        (status = 'scheduled' AND scheduled_at IS NOT NULL) OR
        (status != 'scheduled')
    )
);

-- ============================================================================
-- TABLE: publication_metadata (SEO & Content Metadata)
-- ============================================================================

CREATE TABLE IF NOT EXISTS publication_metadata (
    -- Identity
    metadata_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    publication_id UUID NOT NULL REFERENCES content_publications(publication_id) ON DELETE CASCADE,
    
    -- SEO Metadata
    meta_title TEXT,  -- SEO title (may differ from content title)
    meta_description TEXT,  -- SEO description (150-160 chars)
    canonical_url TEXT,  -- Canonical URL for SEO
    
    -- Content Metadata
    featured_image_url TEXT,  -- Featured image URL
    featured_image_alt_text TEXT,  -- Alt text for accessibility
    tags TEXT[] DEFAULT '{}',  -- Content tags
    categories TEXT[] DEFAULT '{}',  -- Content categories
    
    -- HubSpot-Specific
    blog_id TEXT,  -- HubSpot blog/content group ID (for blog posts)
    author_id TEXT,  -- HubSpot author ID
    campaign_id TEXT,  -- HubSpot campaign ID
    
    -- Social Media Specific
    social_channel_guid TEXT,  -- HubSpot social channel GUID
    social_message TEXT,  -- Social media message (may differ from content)
    social_link_url TEXT,  -- Link to include in social post
    social_photo_url TEXT,  -- Photo to include in social post
    
    -- Email Specific
    email_subject TEXT,  -- Email subject line
    email_from_name TEXT,  -- From name
    email_reply_to TEXT,  -- Reply-to email
    
    -- Custom Fields
    custom_fields JSONB DEFAULT '{}'::jsonb,  -- Platform-specific custom fields
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- TABLE: publication_events (Audit Log)
-- ============================================================================

CREATE TABLE IF NOT EXISTS publication_events (
    -- Identity
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    publication_id UUID NOT NULL REFERENCES content_publications(publication_id) ON DELETE CASCADE,
    
    -- Event Details
    event_type TEXT NOT NULL CHECK (event_type IN (
        'created',          -- Publication record created
        'publishing',       -- Started publishing
        'published',        -- Successfully published
        'failed',           -- Publication failed
        'retrying',         -- Retrying after failure
        'scheduled',        -- Scheduled for future
        'cancelled',        -- Cancelled by user
        'updated',          -- Metadata updated
        'deleted'           -- Publication deleted
    )),
    
    -- Event Data
    event_data JSONB NOT NULL DEFAULT '{}'::jsonb,  -- Event-specific data
    
    -- Context
    triggered_by TEXT,  -- user:{id}, system, scheduler, retry_worker
    
    -- Timestamp
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- TABLE: publication_performance (Performance Metrics from HubSpot)
-- ============================================================================

CREATE TABLE IF NOT EXISTS publication_performance (
    -- Identity
    performance_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    publication_id UUID NOT NULL REFERENCES content_publications(publication_id) ON DELETE CASCADE,
    
    -- Metrics (Blog Posts)
    views INTEGER,
    unique_views INTEGER,
    time_on_page_seconds INTEGER,
    bounce_rate FLOAT CHECK (bounce_rate IS NULL OR (bounce_rate >= 0 AND bounce_rate <= 1)),
    
    -- Metrics (Social Media)
    impressions INTEGER,
    clicks INTEGER,
    likes INTEGER,
    shares INTEGER,
    comments INTEGER,
    engagement_rate FLOAT CHECK (engagement_rate IS NULL OR (engagement_rate >= 0 AND engagement_rate <= 1)),
    
    -- Metrics (Email)
    sent INTEGER,
    delivered INTEGER,
    opened INTEGER,
    clicked INTEGER,
    unsubscribed INTEGER,
    open_rate FLOAT CHECK (open_rate IS NULL OR (open_rate >= 0 AND open_rate <= 1)),
    click_rate FLOAT CHECK (click_rate IS NULL OR (click_rate >= 0 AND click_rate <= 1)),
    
    -- Calculated Metrics
    ctr FLOAT CHECK (ctr IS NULL OR (ctr >= 0 AND ctr <= 1)),  -- Click-through rate
    conversion_rate FLOAT CHECK (conversion_rate IS NULL OR (conversion_rate >= 0 AND conversion_rate <= 1)),
    
    -- Metadata
    synced_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),  -- When metrics were synced from HubSpot
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- INDEXES
-- ============================================================================

-- hubspot_credentials indexes
CREATE INDEX IF NOT EXISTS idx_credentials_tenant 
ON hubspot_credentials(tenant_id) 
WHERE is_active = true;

CREATE INDEX IF NOT EXISTS idx_credentials_portal 
ON hubspot_credentials(portal_id);

CREATE INDEX IF NOT EXISTS idx_credentials_expires 
ON hubspot_credentials(token_expires_at) 
WHERE auth_type = 'oauth' AND is_active = true;

-- content_publications indexes
CREATE INDEX IF NOT EXISTS idx_publications_content 
ON content_publications(content_id);

CREATE INDEX IF NOT EXISTS idx_publications_tenant 
ON content_publications(tenant_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_publications_status 
ON content_publications(status, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_publications_platform 
ON content_publications(platform, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_publications_scheduled 
ON content_publications(scheduled_at) 
WHERE status = 'scheduled';

CREATE INDEX IF NOT EXISTS idx_publications_failed 
ON content_publications(retry_count, last_retry_at) 
WHERE status = 'failed';

CREATE INDEX IF NOT EXISTS idx_publications_credential 
ON content_publications(credential_id);

-- publication_metadata indexes
CREATE INDEX IF NOT EXISTS idx_metadata_publication 
ON publication_metadata(publication_id);

CREATE INDEX IF NOT EXISTS idx_metadata_tags 
ON publication_metadata USING GIN(tags);

-- publication_events indexes
CREATE INDEX IF NOT EXISTS idx_events_publication 
ON publication_events(publication_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_events_type 
ON publication_events(event_type, created_at DESC);

-- publication_performance indexes
CREATE INDEX IF NOT EXISTS idx_performance_publication 
ON publication_performance(publication_id);

CREATE INDEX IF NOT EXISTS idx_performance_synced 
ON publication_performance(synced_at DESC);

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for hubspot_credentials
CREATE TRIGGER update_credentials_updated_at
BEFORE UPDATE ON hubspot_credentials
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Trigger for content_publications
CREATE TRIGGER update_publications_updated_at
BEFORE UPDATE ON content_publications
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Trigger for publication_metadata
CREATE TRIGGER update_metadata_updated_at
BEFORE UPDATE ON publication_metadata
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Function to create publication event on status change
CREATE OR REPLACE FUNCTION create_publication_event()
RETURNS TRIGGER AS $$
BEGIN
    -- Only create event if status changed
    IF (TG_OP = 'UPDATE' AND OLD.status != NEW.status) OR TG_OP = 'INSERT' THEN
        INSERT INTO publication_events (
            publication_id,
            event_type,
            event_data,
            triggered_by
        ) VALUES (
            NEW.publication_id,
            NEW.status,
            jsonb_build_object(
                'old_status', CASE WHEN TG_OP = 'UPDATE' THEN OLD.status ELSE NULL END,
                'new_status', NEW.status,
                'retry_count', NEW.retry_count,
                'error_message', NEW.error_message
            ),
            'system'
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for automatic event creation
CREATE TRIGGER auto_create_publication_event
AFTER INSERT OR UPDATE ON content_publications
FOR EACH ROW
EXECUTE FUNCTION create_publication_event();

-- ============================================================================
-- VIEWS
-- ============================================================================

-- View for active publications with metadata
CREATE OR REPLACE VIEW v_publications_with_metadata AS
SELECT 
    p.*,
    m.meta_description,
    m.featured_image_url,
    m.tags,
    m.blog_id,
    m.author_id,
    c.portal_id,
    c.portal_name,
    perf.views,
    perf.clicks,
    perf.ctr,
    perf.engagement_rate
FROM content_publications p
LEFT JOIN publication_metadata m ON p.publication_id = m.publication_id
LEFT JOIN hubspot_credentials c ON p.credential_id = c.credential_id
LEFT JOIN LATERAL (
    SELECT * FROM publication_performance
    WHERE publication_id = p.publication_id
    ORDER BY synced_at DESC
    LIMIT 1
) perf ON true;

-- View for pending/scheduled publications
CREATE OR REPLACE VIEW v_pending_publications AS
SELECT 
    p.*,
    m.meta_description,
    m.featured_image_url,
    c.portal_id
FROM content_publications p
LEFT JOIN publication_metadata m ON p.publication_id = m.publication_id
LEFT JOIN hubspot_credentials c ON p.credential_id = c.credential_id
WHERE p.status IN ('pending', 'scheduled')
ORDER BY COALESCE(p.scheduled_at, p.created_at) ASC;

-- View for failed publications needing retry
CREATE OR REPLACE VIEW v_failed_publications AS
SELECT 
    p.*,
    c.portal_id,
    c.is_active as credential_active
FROM content_publications p
LEFT JOIN hubspot_credentials c ON p.credential_id = c.credential_id
WHERE p.status = 'failed'
AND p.retry_count < p.max_retries
ORDER BY p.last_retry_at ASC NULLS FIRST;

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE hubspot_credentials IS 'HubSpot API credentials per tenant (Private App or OAuth)';
COMMENT ON COLUMN hubspot_credentials.access_token IS 'Encrypted at application level before storage';
COMMENT ON COLUMN hubspot_credentials.auth_type IS 'private_app: Simple token, oauth: Full OAuth 2.0 flow';

COMMENT ON TABLE content_publications IS 'Tracks all content publications to HubSpot platforms';
COMMENT ON COLUMN content_publications.platform IS 'HubSpot platform: blog, social (LinkedIn/Twitter/Facebook), email, landing page';
COMMENT ON COLUMN content_publications.status IS 'Publication lifecycle: pending → publishing → published (or failed)';

COMMENT ON TABLE publication_metadata IS 'SEO and content metadata for HubSpot publications';
COMMENT ON COLUMN publication_metadata.meta_description IS 'SEO meta description (150-160 characters recommended)';

COMMENT ON TABLE publication_events IS 'Audit log of all publication state changes';
COMMENT ON TABLE publication_performance IS 'Performance metrics synced from HubSpot Analytics API';

-- ============================================================================
-- SAMPLE QUERIES (for reference)
-- ============================================================================

-- Get active credential for tenant
-- SELECT * FROM hubspot_credentials 
-- WHERE tenant_id = 'xxx' AND is_active = true 
-- LIMIT 1;

-- Get all publications for content
-- SELECT * FROM v_publications_with_metadata 
-- WHERE content_id = 'xxx' 
-- ORDER BY created_at DESC;

-- Get pending publications due for publishing
-- SELECT * FROM v_pending_publications 
-- WHERE status = 'scheduled' 
-- AND scheduled_at <= NOW();

-- Get failed publications to retry
-- SELECT * FROM v_failed_publications 
-- LIMIT 100;

-- Get publication performance
-- SELECT 
--     p.publication_id,
--     p.platform,
--     p.published_at,
--     perf.views,
--     perf.clicks,
--     perf.ctr
-- FROM content_publications p
-- JOIN publication_performance perf ON p.publication_id = perf.publication_id
-- WHERE p.tenant_id = 'xxx'
-- ORDER BY perf.views DESC
-- LIMIT 10;

-- ============================================================================
-- ROLLBACK SCRIPT
-- ============================================================================

-- To rollback this migration, run:
-- DROP VIEW IF EXISTS v_failed_publications;
-- DROP VIEW IF EXISTS v_pending_publications;
-- DROP VIEW IF EXISTS v_publications_with_metadata;
-- DROP TRIGGER IF EXISTS auto_create_publication_event ON content_publications;
-- DROP TRIGGER IF EXISTS update_metadata_updated_at ON publication_metadata;
-- DROP TRIGGER IF EXISTS update_publications_updated_at ON content_publications;
-- DROP TRIGGER IF EXISTS update_credentials_updated_at ON hubspot_credentials;
-- DROP FUNCTION IF EXISTS create_publication_event();
-- DROP FUNCTION IF EXISTS update_updated_at_column();
-- DROP TABLE IF EXISTS publication_performance;
-- DROP TABLE IF EXISTS publication_events;
-- DROP TABLE IF EXISTS publication_metadata;
-- DROP TABLE IF EXISTS content_publications;
-- DROP TABLE IF EXISTS hubspot_credentials;

