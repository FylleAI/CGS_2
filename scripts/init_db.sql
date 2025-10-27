-- Database initialization script for local development
-- This script creates the Cards API schema in PostgreSQL

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- TABLE: cards
-- ============================================================================

CREATE TABLE IF NOT EXISTS cards (
    card_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL,
    card_type VARCHAR(50) NOT NULL CHECK (card_type IN ('company', 'audience', 'voice', 'insight')),
    content JSONB NOT NULL,
    content_hash VARCHAR(64) NOT NULL,
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(255) DEFAULT 'system',
    
    -- Constraints
    CONSTRAINT cards_tenant_type_hash_unique UNIQUE (tenant_id, card_type, content_hash)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_cards_tenant_id ON cards(tenant_id);
CREATE INDEX IF NOT EXISTS idx_cards_card_type ON cards(card_type);
CREATE INDEX IF NOT EXISTS idx_cards_tenant_type ON cards(tenant_id, card_type);
CREATE INDEX IF NOT EXISTS idx_cards_content_hash ON cards(content_hash);
CREATE INDEX IF NOT EXISTS idx_cards_content_gin ON cards USING GIN (content);
CREATE INDEX IF NOT EXISTS idx_cards_is_active ON cards(is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_cards_created_at ON cards(created_at DESC);

-- ============================================================================
-- TABLE: idempotency_store
-- ============================================================================

CREATE TABLE IF NOT EXISTS idempotency_store (
    idempotency_key VARCHAR(255) NOT NULL,
    tenant_id UUID NOT NULL,
    response_payload JSONB NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    PRIMARY KEY (idempotency_key, tenant_id),
    CONSTRAINT idempotency_store_key_tenant_unique UNIQUE (idempotency_key, tenant_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_idempotency_tenant_id ON idempotency_store(tenant_id);
CREATE INDEX IF NOT EXISTS idx_idempotency_expires_at ON idempotency_store(expires_at);

-- ============================================================================
-- TABLE: card_usage
-- ============================================================================

CREATE TABLE IF NOT EXISTS card_usage (
    usage_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    card_id UUID NOT NULL REFERENCES cards(card_id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL,
    workflow_id VARCHAR(255) NOT NULL,
    workflow_type VARCHAR(100) NOT NULL,
    session_id VARCHAR(255),
    used_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT card_usage_workflow_card_unique UNIQUE (workflow_id, card_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_card_usage_card_id ON card_usage(card_id);
CREATE INDEX IF NOT EXISTS idx_card_usage_tenant_id ON card_usage(tenant_id);
CREATE INDEX IF NOT EXISTS idx_card_usage_workflow_id ON card_usage(workflow_id);
CREATE INDEX IF NOT EXISTS idx_card_usage_workflow_type ON card_usage(workflow_type);
CREATE INDEX IF NOT EXISTS idx_card_usage_used_at ON card_usage(used_at DESC);

-- ============================================================================
-- TRIGGERS: Auto-update updated_at
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
DROP TRIGGER IF EXISTS cards_updated_at_trigger ON cards;
CREATE TRIGGER cards_updated_at_trigger
    BEFORE UPDATE ON cards
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for idempotency_store table
DROP TRIGGER IF EXISTS idempotency_store_updated_at_trigger ON idempotency_store;
CREATE TRIGGER idempotency_store_updated_at_trigger
    BEFORE UPDATE ON idempotency_store
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- ROW-LEVEL SECURITY (RLS) - Optional for local dev
-- ============================================================================

-- Enable RLS on tables (optional for local dev, required for production)
-- ALTER TABLE cards ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE idempotency_store ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE card_usage ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (optional for local dev)
-- CREATE POLICY cards_tenant_isolation ON cards
--     USING (tenant_id::text = current_setting('app.current_tenant_id', TRUE));

-- CREATE POLICY idempotency_tenant_isolation ON idempotency_store
--     USING (tenant_id::text = current_setting('app.current_tenant_id', TRUE));

-- CREATE POLICY card_usage_tenant_isolation ON card_usage
--     USING (tenant_id::text = current_setting('app.current_tenant_id', TRUE));

-- ============================================================================
-- CLEANUP: Expired idempotency entries
-- ============================================================================

-- Function to clean up expired idempotency entries
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
-- SAMPLE DATA (for local development)
-- ============================================================================

-- Insert sample tenant
DO $$
BEGIN
    -- Sample tenant ID
    INSERT INTO cards (
        tenant_id,
        card_type,
        content,
        content_hash,
        created_by
    )
    VALUES
        (
            '123e4567-e89b-12d3-a456-426614174000',
            'company',
            '{"name": "Sample Company", "domain": "sample.com", "industry": "Technology"}'::jsonb,
            encode(sha256('{"domain":"sample.com","industry":"Technology","name":"Sample Company"}'::bytea), 'hex'),
            'init_script'
        )
    ON CONFLICT (tenant_id, card_type, content_hash) DO NOTHING;
    
    RAISE NOTICE '✅ Database initialized successfully';
    RAISE NOTICE '📊 Sample data inserted for tenant: 123e4567-e89b-12d3-a456-426614174000';
END $$;

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- Verify tables
SELECT 
    'Tables created' as status,
    (SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'cards') as cards_table,
    (SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'idempotency_store') as idempotency_table,
    (SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'card_usage') as usage_table;

-- Verify indexes
SELECT 
    'Indexes created' as status,
    COUNT(*) as index_count
FROM pg_indexes
WHERE tablename IN ('cards', 'idempotency_store', 'card_usage');

-- Verify sample data
SELECT 
    'Sample data' as status,
    COUNT(*) as card_count
FROM cards
WHERE tenant_id = '123e4567-e89b-12d3-a456-426614174000';

