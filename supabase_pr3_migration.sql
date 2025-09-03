-- Migration script for PR #3: Enhanced Supabase Tracking
-- This script creates the missing tables and updates existing ones

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- WORKFLOW RUNS (ensure it exists)
-- =====================================================
CREATE TABLE IF NOT EXISTS workflow_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_name VARCHAR(100),
    workflow_name VARCHAR(200),
    topic TEXT,
    status VARCHAR(50) DEFAULT 'running', -- running, completed, failed
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds NUMERIC(10,3),
    total_cost_usd NUMERIC(12,4),
    total_tokens BIGINT,
    error_message TEXT
);

-- =====================================================
-- RUN LOGS (ensure it exists)
-- =====================================================
CREATE TABLE IF NOT EXISTS run_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id UUID REFERENCES workflow_runs(id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    level VARCHAR(20) DEFAULT 'INFO',
    message TEXT,
    agent_name VARCHAR(200),
    metadata JSONB DEFAULT '{}'
);

-- =====================================================
-- RUN DOCUMENTS (NEW in PR #3) - RAG usage tracking
-- =====================================================
CREATE TABLE IF NOT EXISTS run_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id UUID REFERENCES workflow_runs(id) ON DELETE CASCADE,
    client_name VARCHAR(100),
    document_path TEXT,
    source_url TEXT,
    retrieved_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- CONTENT GENERATIONS (ensure it exists with correct schema)
-- =====================================================
CREATE TABLE IF NOT EXISTS content_generations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id UUID, -- Link to workflow_runs
    title VARCHAR(500),
    content TEXT,
    topic TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_workflow_runs_started_at ON workflow_runs(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_run_logs_run_id ON run_logs(run_id);
CREATE INDEX IF NOT EXISTS idx_run_documents_run_id ON run_documents(run_id);
CREATE INDEX IF NOT EXISTS idx_content_generations_run_id ON content_generations(run_id);
CREATE INDEX IF NOT EXISTS idx_content_generations_created_at ON content_generations(created_at DESC);

-- =====================================================
-- VERIFY TABLES EXIST
-- =====================================================
-- This query will show all the tables we just created
SELECT 
    table_name,
    table_type
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('workflow_runs', 'run_logs', 'run_documents', 'content_generations')
ORDER BY table_name;
