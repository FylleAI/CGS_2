-- RAG similarity search function and indexes (pgvector) for Supabase
-- Safe, idempotent migration to enable public.match_documents used by the backend
-- Run this in Supabase SQL editor on your project (schema: public)

-- 1) Ensure required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector"; -- pgvector for embeddings

-- 2) Ensure documents table has the embedding column with correct dimension
--    If the column already exists with a different type, adjust manually as needed.
ALTER TABLE IF EXISTS public.documents
  ADD COLUMN IF NOT EXISTS embedding VECTOR(1536);

-- Helpful indexes (optional but recommended)
-- Index on client_id for faster filtering
CREATE INDEX IF NOT EXISTS idx_documents_client_id ON public.documents(client_id);

-- Vector index for fast ANN search (requires pgvector >= 0.4.0)
-- Note: IVFFLAT index requires ANALYZE after creation and is most effective on larger datasets.
CREATE INDEX IF NOT EXISTS idx_documents_embedding
  ON public.documents USING ivfflat (embedding vector_l2_ops)
  WITH (lists = 100);

-- 3) Create/replace the similarity search function
--    This function is called by the backend via Supabase RPC: match_documents
CREATE OR REPLACE FUNCTION public.match_documents(
    query_embedding vector(1536),
    match_count integer,
    client_name text
)
RETURNS TABLE (
    id uuid,
    title text,
    content text,
    file_path text,
    similarity float
)
LANGUAGE sql STABLE
AS $$
  SELECT d.id,
         d.title,
         d.content,
         d.file_path,
         1 - (d.embedding <=> query_embedding) AS similarity
  FROM public.documents d
  JOIN public.clients c ON c.id = d.client_id
  WHERE c.name = client_name
    AND d.embedding IS NOT NULL
  ORDER BY d.embedding <=> query_embedding
  LIMIT LEAST(match_count, 50);
$$;

-- 4) Permissions: allow anon/authenticated to execute the RPC function
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
    GRANT EXECUTE ON FUNCTION public.match_documents(vector(1536), integer, text) TO anon;
  END IF;
  IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
    GRANT EXECUTE ON FUNCTION public.match_documents(vector(1536), integer, text) TO authenticated;
  END IF;
END$$;

-- 5) Analyze to improve IVFFLAT performance (optional)
ANALYZE public.documents;
