-- Tracking tables for workflow runs and agent logs

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- WORKFLOW RUNS
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
-- AGENT EXECUTIONS
-- =====================================================
CREATE TABLE IF NOT EXISTS agent_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id UUID REFERENCES workflow_runs(id) ON DELETE CASCADE,
    agent_name VARCHAR(200),
    step_number INT,
    status VARCHAR(50) DEFAULT 'completed',
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds NUMERIC(10,3),
    tokens_used BIGINT,
    cost_usd NUMERIC(12,4),
    thoughts TEXT,
    input_data JSONB DEFAULT '{}',
    output_data JSONB DEFAULT '{}'
);

-- =====================================================
-- RUN LOGS
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

-- Optional indexes
CREATE INDEX IF NOT EXISTS idx_workflow_runs_started_at ON workflow_runs(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_agent_executions_run_id ON agent_executions(run_id);
CREATE INDEX IF NOT EXISTS idx_run_logs_run_id ON run_logs(run_id);

-- =====================================================
-- RUN DOCUMENTS (RAG usage)
-- =====================================================
CREATE TABLE IF NOT EXISTS run_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id UUID REFERENCES workflow_runs(id) ON DELETE CASCADE,
    client_name VARCHAR(100),
    document_path TEXT,
    source_url TEXT,
    retrieved_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_run_documents_run_id ON run_documents(run_id);

