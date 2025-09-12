-- Agent tracking schema fixes for Supabase
-- Safe, idempotent migration to align with current backend tracker usage
-- Run this in Supabase SQL editor on your project (schema: public)

-- 1) Ensure required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2) Create workflow_runs table if missing
CREATE TABLE IF NOT EXISTS public.workflow_runs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  client_name TEXT NOT NULL,
  workflow_name TEXT NOT NULL,
  topic TEXT,
  status TEXT DEFAULT 'running',
  started_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  error_message TEXT,
  total_cost_usd NUMERIC(10,4),
  total_tokens INTEGER,
  agent_executor TEXT
);

-- 3) Create run_logs table if missing (tracker orders by timestamp)
CREATE TABLE IF NOT EXISTS public.run_logs (
  id BIGSERIAL PRIMARY KEY,
  run_id UUID NOT NULL,
  level TEXT NOT NULL,
  message TEXT NOT NULL,
  agent_name TEXT,
  metadata JSONB,
  timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Relax/extend the level constraint to include agent reasoning and tooling signals
ALTER TABLE IF EXISTS public.run_logs DROP CONSTRAINT IF EXISTS run_logs_level_check;
ALTER TABLE IF EXISTS public.run_logs
  ADD CONSTRAINT run_logs_level_check
  CHECK (level IN ('INFO','DEBUG','WARN','WARNING','ERROR','THINK','LLM','TOOL','START','END'));

-- 4) Create agent_executions table if missing
CREATE TABLE IF NOT EXISTS public.agent_executions (
  id BIGSERIAL PRIMARY KEY,
  run_id UUID NOT NULL,
  agent_name TEXT NOT NULL,
  step_number INTEGER DEFAULT 0,
  status TEXT DEFAULT 'completed',
  completed_at TIMESTAMPTZ DEFAULT NOW(),
  input_data JSONB,
  output_data JSONB,
  thoughts TEXT,
  tokens_used INTEGER,
  cost_usd NUMERIC(10,4),
  provider_name TEXT,
  model_name TEXT,
  duration_seconds NUMERIC(10,3)
);

-- Ensure duration_seconds supports fractional seconds (avoid 22P02 on inserts)
ALTER TABLE IF EXISTS public.agent_executions
  ALTER COLUMN duration_seconds TYPE NUMERIC(10,3)
  USING duration_seconds::NUMERIC;

-- Ensure provider/model columns exist (for accurate evaluation)
ALTER TABLE IF EXISTS public.agent_executions
  ADD COLUMN IF NOT EXISTS provider_name TEXT;
ALTER TABLE IF EXISTS public.agent_executions
  ADD COLUMN IF NOT EXISTS model_name TEXT;

-- 5) Create run_documents table if missing
CREATE TABLE IF NOT EXISTS public.run_documents (
  id BIGSERIAL PRIMARY KEY,
  run_id UUID NOT NULL,
  client_name TEXT NOT NULL,
  document_path TEXT NOT NULL,
  source_url TEXT,
  agent_name TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Ensure agent_name exists (backend may send it)
ALTER TABLE IF EXISTS public.run_documents
  ADD COLUMN IF NOT EXISTS agent_name TEXT;

-- 6) Create run_document_chunks table if missing
CREATE TABLE IF NOT EXISTS public.run_document_chunks (
  id BIGSERIAL PRIMARY KEY,
  run_id UUID NOT NULL,
  agent_name TEXT NOT NULL,
  document_id TEXT NOT NULL,
  chunk_text TEXT NOT NULL,
  similarity_score NUMERIC(10,6),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7) Helpful indexes
CREATE INDEX IF NOT EXISTS idx_workflow_runs_started_at ON public.workflow_runs(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_workflow_runs_status ON public.workflow_runs(status);
CREATE INDEX IF NOT EXISTS idx_run_logs_run_id ON public.run_logs(run_id);
CREATE INDEX IF NOT EXISTS idx_agent_exec_run_id ON public.agent_executions(run_id);
CREATE INDEX IF NOT EXISTS idx_run_docs_run_id ON public.run_documents(run_id);
CREATE INDEX IF NOT EXISTS idx_run_doc_chunks_run_id ON public.run_document_chunks(run_id);


-- 8) Referential integrity: Foreign Keys with ON DELETE CASCADE
ALTER TABLE IF EXISTS public.run_logs DROP CONSTRAINT IF EXISTS fk_run_logs_run;
ALTER TABLE IF EXISTS public.run_logs
  ADD CONSTRAINT fk_run_logs_run FOREIGN KEY (run_id)
  REFERENCES public.workflow_runs(id) ON DELETE CASCADE;

ALTER TABLE IF EXISTS public.agent_executions DROP CONSTRAINT IF EXISTS fk_agent_exec_run;
ALTER TABLE IF EXISTS public.agent_executions
  ADD CONSTRAINT fk_agent_exec_run FOREIGN KEY (run_id)
  REFERENCES public.workflow_runs(id) ON DELETE CASCADE;

ALTER TABLE IF EXISTS public.run_documents DROP CONSTRAINT IF EXISTS fk_run_docs_run;
ALTER TABLE IF EXISTS public.run_documents
  ADD CONSTRAINT fk_run_docs_run FOREIGN KEY (run_id)
  REFERENCES public.workflow_runs(id) ON DELETE CASCADE;

ALTER TABLE IF EXISTS public.run_document_chunks DROP CONSTRAINT IF EXISTS fk_run_chunks_run;
ALTER TABLE IF EXISTS public.run_document_chunks
  ADD CONSTRAINT fk_run_chunks_run FOREIGN KEY (run_id)
  REFERENCES public.workflow_runs(id) ON DELETE CASCADE;

-- 9) Composite indexes for frequent queries
CREATE INDEX IF NOT EXISTS idx_run_logs_run_ts ON public.run_logs(run_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_agent_exec_run_step ON public.agent_executions(run_id, step_number);

-- Note on RLS:
-- If RLS is enabled on these tables in your project, ensure appropriate INSERT/SELECT policies are in place
-- for the backend role you are using (anon/service_role). This script does not alter RLS policies.

