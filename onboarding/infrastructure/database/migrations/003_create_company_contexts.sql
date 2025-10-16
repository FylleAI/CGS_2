-- Migration 003: Create company_contexts table for RAG system
-- Purpose: Store company snapshots for reuse across sessions
-- Author: Onboarding Team
-- Date: 2025-10-16

-- ============================================================================
-- TABLE: company_contexts
-- ============================================================================

CREATE TABLE IF NOT EXISTS company_contexts (
    -- Primary key
    context_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Company identification
    company_name TEXT NOT NULL,           -- Normalized name for matching (lowercase, no spaces/dashes)
    company_display_name TEXT NOT NULL,   -- Original name for display
    website TEXT,                         -- Company website
    
    -- Versioning
    version INTEGER NOT NULL DEFAULT 1,   -- Version number (increments on refresh)
    is_active BOOLEAN NOT NULL DEFAULT true,  -- Only one active version per company
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Rich Context (JSONB)
    company_snapshot JSONB NOT NULL,      -- Full CompanySnapshot object
    
    -- Metadata for RAG retrieval
    industry TEXT,                        -- Extracted from snapshot.company.industry
    primary_audience TEXT,                -- Extracted from snapshot.audience.primary
    key_offerings TEXT[],                 -- Array of key offerings
    tags TEXT[],                          -- Tags for categorization/search
    
    -- Usage tracking
    usage_count INTEGER NOT NULL DEFAULT 0,
    last_used_at TIMESTAMPTZ,
    
    -- Source tracking
    source_session_id UUID,               -- First session that created this context
    
    -- Constraints
    CONSTRAINT unique_company_version UNIQUE (company_name, version),
    CONSTRAINT check_version_positive CHECK (version > 0),
    CONSTRAINT check_usage_count_non_negative CHECK (usage_count >= 0)
);

-- ============================================================================
-- INDEXES
-- ============================================================================

-- Index for RAG lookup (most common query)
CREATE INDEX IF NOT EXISTS idx_company_contexts_name_active 
ON company_contexts(company_name) 
WHERE is_active = true;

-- Index for industry filtering
CREATE INDEX IF NOT EXISTS idx_company_contexts_industry 
ON company_contexts(industry) 
WHERE is_active = true;

-- Index for recent contexts
CREATE INDEX IF NOT EXISTS idx_company_contexts_updated 
ON company_contexts(updated_at DESC);

-- GIN index for tags array search
CREATE INDEX IF NOT EXISTS idx_company_contexts_tags 
ON company_contexts USING GIN(tags);

-- GIN index for full-text search on company info
CREATE INDEX IF NOT EXISTS idx_company_contexts_fts 
ON company_contexts USING GIN(
    to_tsvector('english', 
        company_display_name || ' ' || 
        COALESCE(industry, '') || ' ' || 
        COALESCE(primary_audience, '')
    )
);

-- ============================================================================
-- TRIGGER: Update updated_at timestamp
-- ============================================================================

CREATE OR REPLACE FUNCTION update_company_contexts_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_company_contexts_updated_at
    BEFORE UPDATE ON company_contexts
    FOR EACH ROW
    EXECUTE FUNCTION update_company_contexts_updated_at();

-- ============================================================================
-- ALTER: Add company_context_id to onboarding_sessions
-- ============================================================================

-- Add foreign key reference to company_contexts
ALTER TABLE onboarding_sessions 
ADD COLUMN IF NOT EXISTS company_context_id UUID REFERENCES company_contexts(context_id);

-- Index for joins
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_context 
ON onboarding_sessions(company_context_id);

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE company_contexts IS 'Stores company snapshots for RAG-based reuse across onboarding sessions';
COMMENT ON COLUMN company_contexts.context_id IS 'Unique identifier for this context';
COMMENT ON COLUMN company_contexts.company_name IS 'Normalized company name for matching (lowercase, no spaces/dashes)';
COMMENT ON COLUMN company_contexts.company_display_name IS 'Original company name for display purposes';
COMMENT ON COLUMN company_contexts.version IS 'Version number, increments when context is refreshed';
COMMENT ON COLUMN company_contexts.is_active IS 'Only one active version per company at a time';
COMMENT ON COLUMN company_contexts.company_snapshot IS 'Full CompanySnapshot object as JSONB';
COMMENT ON COLUMN company_contexts.usage_count IS 'Number of times this context has been reused';
COMMENT ON COLUMN company_contexts.last_used_at IS 'Timestamp of last usage';
COMMENT ON COLUMN company_contexts.source_session_id IS 'Session ID that originally created this context';

-- ============================================================================
-- SAMPLE QUERIES (for reference)
-- ============================================================================

-- Find active context for a company
-- SELECT * FROM company_contexts 
-- WHERE company_name = 'peterlegwood' 
-- AND is_active = true 
-- ORDER BY version DESC 
-- LIMIT 1;

-- List all contexts for a company (all versions)
-- SELECT context_id, version, is_active, usage_count, created_at 
-- FROM company_contexts 
-- WHERE company_name = 'peterlegwood' 
-- ORDER BY version DESC;

-- Find contexts by industry
-- SELECT company_display_name, industry, usage_count, last_used_at 
-- FROM company_contexts 
-- WHERE industry = 'Therapeutic Footwear' 
-- AND is_active = true;

-- Find most used contexts
-- SELECT company_display_name, industry, usage_count, last_used_at 
-- FROM company_contexts 
-- WHERE is_active = true 
-- ORDER BY usage_count DESC 
-- LIMIT 10;

-- Full-text search
-- SELECT company_display_name, industry, primary_audience 
-- FROM company_contexts 
-- WHERE to_tsvector('english', company_display_name || ' ' || COALESCE(industry, '')) 
--       @@ to_tsquery('english', 'footwear');

-- ============================================================================
-- ROLLBACK (if needed)
-- ============================================================================

-- To rollback this migration:
-- DROP TRIGGER IF EXISTS trigger_update_company_contexts_updated_at ON company_contexts;
-- DROP FUNCTION IF EXISTS update_company_contexts_updated_at();
-- ALTER TABLE onboarding_sessions DROP COLUMN IF EXISTS company_context_id;
-- DROP INDEX IF EXISTS idx_onboarding_sessions_context;
-- DROP INDEX IF EXISTS idx_company_contexts_fts;
-- DROP INDEX IF EXISTS idx_company_contexts_tags;
-- DROP INDEX IF EXISTS idx_company_contexts_updated;
-- DROP INDEX IF EXISTS idx_company_contexts_industry;
-- DROP INDEX IF EXISTS idx_company_contexts_name_active;
-- DROP TABLE IF EXISTS company_contexts;

