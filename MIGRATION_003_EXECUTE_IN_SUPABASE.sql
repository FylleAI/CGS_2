-- ============================================================================
-- MIGRATION 003: Create company_contexts table for RAG system
-- ============================================================================
-- 
-- INSTRUCTIONS:
-- 1. Go to Supabase Dashboard: https://iimymnlepgilbuoxnkqa.supabase.co
-- 2. Navigate to: SQL Editor
-- 3. Create a new query
-- 4. Copy and paste this ENTIRE file
-- 5. Click "Run" or press Ctrl+Enter
-- 6. Verify success (should see "Success. No rows returned")
--
-- ============================================================================

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
-- VERIFICATION QUERIES
-- ============================================================================

-- Check table was created
SELECT 'company_contexts table created' AS status, COUNT(*) AS record_count 
FROM company_contexts;

-- Check column was added to onboarding_sessions
SELECT 'company_context_id column added' AS status, 
       COUNT(*) AS sessions_with_context 
FROM onboarding_sessions 
WHERE company_context_id IS NOT NULL;

-- List all indexes on company_contexts
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'company_contexts' 
ORDER BY indexname;

-- ============================================================================
-- SUCCESS MESSAGE
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '✅ Migration 003 completed successfully!';
    RAISE NOTICE '   - company_contexts table created';
    RAISE NOTICE '   - Indexes created';
    RAISE NOTICE '   - Trigger created';
    RAISE NOTICE '   - company_context_id column added to onboarding_sessions';
    RAISE NOTICE '';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '   1. Verify tables in Supabase Table Editor';
    RAISE NOTICE '   2. Run: python scripts/run_migration_003.py --verify';
    RAISE NOTICE '   3. Proceed with Step 2: Repository implementation';
END $$;

