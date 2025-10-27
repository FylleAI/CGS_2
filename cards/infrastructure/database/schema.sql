-- ============================================================================
-- Cards API Database Schema
-- ============================================================================
-- Version: 1.0.0
-- Created: 2025-10-27
-- Description: PostgreSQL schema for Cards API with Row-Level Security (RLS)
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- TABLE: cards
-- ============================================================================
-- Stores all cards (company, audience, voice, insight)
-- with multi-tenant isolation via RLS
-- ============================================================================

CREATE TABLE IF NOT EXISTS cards (
    -- Primary key
    card_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Multi-tenancy
    tenant_id UUID NOT NULL,
    
    -- Card metadata
    card_type VARCHAR(50) NOT NULL CHECK (card_type IN ('company', 'audience', 'voice', 'insight')),
    
    -- Card content (JSONB for flexibility)
    content JSONB NOT NULL,
    
    -- Content hash for deduplication
    content_hash VARCHAR(64) NOT NULL,
    
    -- Source tracking
    source_session_id UUID,
    created_by VARCHAR(255) NOT NULL,
    
    -- Soft delete
    is_active BOOLEAN NOT NULL DEFAULT true,
    deleted_at TIMESTAMP WITH TIME ZONE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_cards_tenant_id ON cards(tenant_id) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_cards_card_type ON cards(card_type) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_cards_content_hash ON cards(content_hash);
CREATE INDEX IF NOT EXISTS idx_cards_source_session ON cards(source_session_id) WHERE source_session_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_cards_created_at ON cards(created_at DESC);

-- GIN index for JSONB content search
CREATE INDEX IF NOT EXISTS idx_cards_content_gin ON cards USING GIN (content);

-- Unique constraint for deduplication (per tenant)
CREATE UNIQUE INDEX IF NOT EXISTS idx_cards_unique_content 
    ON cards(tenant_id, card_type, content_hash) 
    WHERE is_active = true;

-- ============================================================================
-- TABLE: idempotency_store
-- ============================================================================
-- Stores idempotency keys and cached responses for safe retries
-- ============================================================================

CREATE TABLE IF NOT EXISTS idempotency_store (
    -- Primary key
    idempotency_key VARCHAR(255) PRIMARY KEY,
    
    -- Multi-tenancy
    tenant_id UUID NOT NULL,
    
    -- Cached response
    response_payload JSONB NOT NULL,
    
    -- Expiration
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Index for cleanup of expired entries
CREATE INDEX IF NOT EXISTS idx_idempotency_expires_at ON idempotency_store(expires_at);
CREATE INDEX IF NOT EXISTS idx_idempotency_tenant_id ON idempotency_store(tenant_id);

-- ============================================================================
-- TABLE: card_usage
-- ============================================================================
-- Tracks card usage in workflows for analytics
-- ============================================================================

CREATE TABLE IF NOT EXISTS card_usage (
    -- Primary key
    usage_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Foreign key to cards
    card_id UUID NOT NULL REFERENCES cards(card_id) ON DELETE CASCADE,
    
    -- Multi-tenancy
    tenant_id UUID NOT NULL,
    
    -- Workflow context
    workflow_id UUID,
    workflow_type VARCHAR(100),
    
    -- Timestamp
    used_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes for analytics queries
CREATE INDEX IF NOT EXISTS idx_usage_card_id ON card_usage(card_id);
CREATE INDEX IF NOT EXISTS idx_usage_tenant_id ON card_usage(tenant_id);
CREATE INDEX IF NOT EXISTS idx_usage_workflow_id ON card_usage(workflow_id) WHERE workflow_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_usage_used_at ON card_usage(used_at DESC);
CREATE INDEX IF NOT EXISTS idx_usage_workflow_type ON card_usage(workflow_type) WHERE workflow_type IS NOT NULL;

-- ============================================================================
-- ROW-LEVEL SECURITY (RLS)
-- ============================================================================
-- Enforce multi-tenant isolation at the database level
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE cards ENABLE ROW LEVEL SECURITY;
ALTER TABLE idempotency_store ENABLE ROW LEVEL SECURITY;
ALTER TABLE card_usage ENABLE ROW LEVEL SECURITY;

-- RLS Policy for cards table
-- Only allow access to rows where tenant_id matches the session variable
CREATE POLICY cards_tenant_isolation ON cards
    USING (tenant_id = current_setting('app.current_tenant_id', true)::UUID);

-- RLS Policy for idempotency_store table
CREATE POLICY idempotency_tenant_isolation ON idempotency_store
    USING (tenant_id = current_setting('app.current_tenant_id', true)::UUID);

-- RLS Policy for card_usage table
CREATE POLICY usage_tenant_isolation ON card_usage
    USING (tenant_id = current_setting('app.current_tenant_id', true)::UUID);

-- ============================================================================
-- TRIGGERS
-- ============================================================================
-- Automatically update updated_at timestamp
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for cards table
DROP TRIGGER IF EXISTS update_cards_updated_at ON cards;
CREATE TRIGGER update_cards_updated_at
    BEFORE UPDATE ON cards
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- CLEANUP FUNCTIONS
-- ============================================================================
-- Functions to clean up expired data
-- ============================================================================

-- Function to delete expired idempotency entries
CREATE OR REPLACE FUNCTION cleanup_expired_idempotency()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM idempotency_store
    WHERE expires_at < NOW();
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- COMMENTS
-- ============================================================================
-- Add table and column comments for documentation
-- ============================================================================

COMMENT ON TABLE cards IS 'Stores all cards (company, audience, voice, insight) with multi-tenant isolation';
COMMENT ON COLUMN cards.card_id IS 'Unique identifier for the card';
COMMENT ON COLUMN cards.tenant_id IS 'Tenant identifier for multi-tenant isolation';
COMMENT ON COLUMN cards.card_type IS 'Type of card: company, audience, voice, or insight';
COMMENT ON COLUMN cards.content IS 'Card content stored as JSONB for flexibility';
COMMENT ON COLUMN cards.content_hash IS 'SHA-256 hash of content for deduplication';
COMMENT ON COLUMN cards.source_session_id IS 'Optional reference to the onboarding session that created this card';
COMMENT ON COLUMN cards.is_active IS 'Soft delete flag - false means deleted';

COMMENT ON TABLE idempotency_store IS 'Stores idempotency keys and cached responses for safe retries';
COMMENT ON COLUMN idempotency_store.idempotency_key IS 'Unique idempotency key from client';
COMMENT ON COLUMN idempotency_store.response_payload IS 'Cached response to return on replay';
COMMENT ON COLUMN idempotency_store.expires_at IS 'Expiration timestamp - entries are deleted after this time';

COMMENT ON TABLE card_usage IS 'Tracks card usage in workflows for analytics';
COMMENT ON COLUMN card_usage.card_id IS 'Reference to the card that was used';
COMMENT ON COLUMN card_usage.workflow_id IS 'Unique identifier for the workflow execution';
COMMENT ON COLUMN card_usage.workflow_type IS 'Type of workflow (e.g., premium_newsletter, blog_post)';

-- ============================================================================
-- GRANTS
-- ============================================================================
-- Grant permissions (adjust based on your user setup)
-- ============================================================================

-- Grant all privileges to the application user
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_app_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_app_user;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================

