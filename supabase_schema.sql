-- CGSRef Database Schema for Supabase
-- This file contains the complete database schema for the CGSRef application

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector"; -- For embeddings (if available)

-- =====================================================
-- CLIENTS TABLE
-- =====================================================
CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(200) NOT NULL,
    description TEXT,
    brand_voice TEXT,
    target_audience TEXT,
    industry VARCHAR(100),
    rag_enabled BOOLEAN DEFAULT true,
    knowledge_base_path TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id)
);

-- =====================================================
-- DOCUMENTS TABLE (Knowledge Base)
-- =====================================================
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    description TEXT,
    category VARCHAR(100),
    tags TEXT[] DEFAULT '{}',
    file_path TEXT, -- Path in Supabase Storage
    file_size INTEGER,
    file_type VARCHAR(50),
    metadata JSONB DEFAULT '{}',
    embedding VECTOR(1536), -- OpenAI embeddings dimension
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id)
);

-- =====================================================
-- WORKFLOWS TABLE
-- =====================================================
CREATE TABLE workflows (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    config JSONB NOT NULL DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id)
);

-- =====================================================
-- CONTENT GENERATIONS TABLE
-- =====================================================
CREATE TABLE content_generations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID REFERENCES clients(id),
    workflow_id UUID REFERENCES workflows(id),
    run_id UUID,
    title VARCHAR(500),
    content TEXT,
    content_type VARCHAR(50),
    content_format VARCHAR(50),
    topic TEXT NOT NULL,
    context TEXT,
    target_audience TEXT,
    parameters JSONB DEFAULT '{}',
    selected_documents UUID[] DEFAULT '{}',
    word_count INTEGER,
    generation_time_seconds NUMERIC(10,3),
    cost_usd NUMERIC(10,4),
    status VARCHAR(50) DEFAULT 'pending', -- pending, processing, completed, failed
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id)
);

-- =====================================================
-- API KEYS TABLE (for external services)
-- =====================================================
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_name VARCHAR(100) NOT NULL,
    key_name VARCHAR(100) NOT NULL,
    encrypted_key TEXT NOT NULL, -- Encrypted API key
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    UNIQUE(service_name, key_name)
);

-- =====================================================
-- USER PROFILES TABLE (extends auth.users)
-- =====================================================
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name VARCHAR(200),
    avatar_url TEXT,
    role VARCHAR(50) DEFAULT 'user', -- admin, user, viewer
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Documents indexes
CREATE INDEX idx_documents_client_id ON documents(client_id);
CREATE INDEX idx_documents_category ON documents(category);
CREATE INDEX idx_documents_tags ON documents USING GIN(tags);
CREATE INDEX idx_documents_created_at ON documents(created_at DESC);
CREATE INDEX idx_documents_search ON documents USING GIN(to_tsvector('english', title || ' ' || content));

-- Content generations indexes
CREATE INDEX idx_content_generations_client_id ON content_generations(client_id);
CREATE INDEX idx_content_generations_status ON content_generations(status);
CREATE INDEX idx_content_generations_created_at ON content_generations(created_at DESC);
CREATE INDEX idx_content_generations_created_by ON content_generations(created_by);
CREATE INDEX idx_content_generations_run_id ON content_generations(run_id);

-- Clients indexes
CREATE INDEX idx_clients_name ON clients(name);
CREATE INDEX idx_clients_created_by ON clients(created_by);

-- =====================================================
-- ROW LEVEL SECURITY POLICIES
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE workflows ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_generations ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

-- Clients policies
CREATE POLICY "Users can view all clients" ON clients FOR SELECT USING (true);
CREATE POLICY "Authenticated users can create clients" ON clients FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Users can update their own clients" ON clients FOR UPDATE USING (created_by = auth.uid());

-- Documents policies
CREATE POLICY "Users can view all documents" ON documents FOR SELECT USING (true);
CREATE POLICY "Authenticated users can create documents" ON documents FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Users can update their own documents" ON documents FOR UPDATE USING (created_by = auth.uid());

-- Content generations policies
CREATE POLICY "Users can view their own generations" ON content_generations FOR SELECT USING (created_by = auth.uid());
CREATE POLICY "Users can create their own generations" ON content_generations FOR INSERT WITH CHECK (created_by = auth.uid());
CREATE POLICY "Users can update their own generations" ON content_generations FOR UPDATE USING (created_by = auth.uid());

-- User profiles policies
CREATE POLICY "Users can view their own profile" ON user_profiles FOR SELECT USING (id = auth.uid());
CREATE POLICY "Users can update their own profile" ON user_profiles FOR UPDATE USING (id = auth.uid());
CREATE POLICY "Users can insert their own profile" ON user_profiles FOR INSERT WITH CHECK (id = auth.uid());

-- API keys policies (admin only)
CREATE POLICY "Only admins can manage API keys" ON api_keys FOR ALL USING (
    EXISTS (
        SELECT 1 FROM user_profiles
        WHERE id = auth.uid() AND role = 'admin'
    )
);

-- =====================================================
-- FUNCTIONS AND TRIGGERS
-- =====================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at trigger to all tables
CREATE TRIGGER update_clients_updated_at BEFORE UPDATE ON clients FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_workflows_updated_at BEFORE UPDATE ON workflows FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_content_generations_updated_at BEFORE UPDATE ON content_generations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_api_keys_updated_at BEFORE UPDATE ON api_keys FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to create user profile on signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.user_profiles (id, full_name, avatar_url)
    VALUES (NEW.id, NEW.raw_user_meta_data->>'full_name', NEW.raw_user_meta_data->>'avatar_url');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to create profile on user signup
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();


-- Similarity search function for RAG using pgvector
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

-- =====================================================
-- INITIAL DATA
-- =====================================================

-- Insert default client (Siebert)
INSERT INTO clients (name, display_name, description, brand_voice, target_audience, industry, rag_enabled) VALUES
('siebert', 'Siebert Financial', 'Financial services company focused on empowering individual investors', 'Professional yet accessible, empowering, educational, trustworthy', 'Gen Z and young professionals interested in financial literacy', 'Financial Services', true);

-- Insert default workflows
INSERT INTO workflows (name, display_name, description, category, config) VALUES
('enhanced_article', 'Enhanced Article', 'Comprehensive article with research, analysis, and expert insights', 'article', '{"tasks": ["research", "writing", "review"], "agents": ["researcher", "writer", "editor"]}'),
('newsletter_premium', 'Premium Newsletter', 'Premium newsletter with curated content and insights', 'newsletter', '{"tasks": ["curation", "writing", "formatting"], "agents": ["curator", "writer", "formatter"]}');
