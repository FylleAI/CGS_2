-- Supabase schema for onboarding service
-- Run this SQL in your Supabase SQL editor to create the required table

-- Create onboarding_sessions table
CREATE TABLE IF NOT EXISTS onboarding_sessions (
    -- Primary key
    session_id UUID PRIMARY KEY,
    
    -- Tracking
    trace_id TEXT NOT NULL,
    
    -- Input
    brand_name TEXT NOT NULL,
    website TEXT,
    goal TEXT NOT NULL,
    user_email TEXT,
    
    -- State
    state TEXT NOT NULL DEFAULT 'created',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Artifacts
    snapshot JSONB,
    cgs_payload JSONB,
    cgs_run_id UUID,
    cgs_response JSONB,
    
    -- Delivery
    delivery_status TEXT,
    delivery_message_id TEXT,
    delivery_timestamp TIMESTAMPTZ,
    
    -- Error handling
    error_message TEXT,
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_brand_name 
    ON onboarding_sessions(brand_name);

CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_state 
    ON onboarding_sessions(state);

CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_created_at 
    ON onboarding_sessions(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_trace_id 
    ON onboarding_sessions(trace_id);

CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_user_email 
    ON onboarding_sessions(user_email);

-- Create index for JSONB queries
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_snapshot 
    ON onboarding_sessions USING GIN (snapshot);

-- Add updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_onboarding_sessions_updated_at
    BEFORE UPDATE ON onboarding_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Add comments
COMMENT ON TABLE onboarding_sessions IS 'Onboarding sessions tracking complete workflow state';
COMMENT ON COLUMN onboarding_sessions.session_id IS 'Unique session identifier';
COMMENT ON COLUMN onboarding_sessions.trace_id IS 'Trace ID for correlation across services';
COMMENT ON COLUMN onboarding_sessions.brand_name IS 'Company/brand name being onboarded';
COMMENT ON COLUMN onboarding_sessions.goal IS 'Content generation goal: linkedin_post, newsletter, article';
COMMENT ON COLUMN onboarding_sessions.state IS 'Session state: created, researching, synthesizing, awaiting_user, payload_ready, executing, delivering, done, failed';
COMMENT ON COLUMN onboarding_sessions.snapshot IS 'Company snapshot JSON (CompanySnapshot v1.0)';
COMMENT ON COLUMN onboarding_sessions.cgs_payload IS 'CGS payload JSON (CgsPayload v1.0)';
COMMENT ON COLUMN onboarding_sessions.cgs_run_id IS 'CGS workflow run ID';
COMMENT ON COLUMN onboarding_sessions.cgs_response IS 'CGS response JSON (ResultEnvelope v1.0)';

-- Optional: Create view for active sessions
CREATE OR REPLACE VIEW active_onboarding_sessions AS
SELECT 
    session_id,
    trace_id,
    brand_name,
    goal,
    state,
    created_at,
    updated_at,
    delivery_status,
    error_message
FROM onboarding_sessions
WHERE state NOT IN ('done', 'failed')
ORDER BY created_at DESC;

-- Optional: Create view for session statistics
CREATE OR REPLACE VIEW onboarding_session_stats AS
SELECT 
    state,
    goal,
    COUNT(*) as count,
    AVG(EXTRACT(EPOCH FROM (updated_at - created_at))) as avg_duration_seconds,
    COUNT(CASE WHEN delivery_status = 'sent' THEN 1 END) as delivered_count,
    COUNT(CASE WHEN error_message IS NOT NULL THEN 1 END) as error_count
FROM onboarding_sessions
GROUP BY state, goal;

-- Grant permissions (adjust as needed for your setup)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON onboarding_sessions TO authenticated;
-- GRANT SELECT ON active_onboarding_sessions TO authenticated;
-- GRANT SELECT ON onboarding_session_stats TO authenticated;

