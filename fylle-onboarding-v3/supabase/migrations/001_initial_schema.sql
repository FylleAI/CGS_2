-- Fylle Onboarding v3 - Initial Schema
-- Run this migration in Supabase SQL Editor

-- =============================================================================
-- USERS TABLE
-- =============================================================================
-- Created when user enters email during onboarding

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    brand_name VARCHAR(255),
    website VARCHAR(500),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Trigger to update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- CARDS TABLE
-- =============================================================================
-- Stores all 8 card types for each user

CREATE TABLE IF NOT EXISTS cards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL CHECK (type IN (
        'product', 'target', 'campaigns', 'topic', 
        'brand_voice', 'competitor', 'performance', 'feedback'
    )),
    title VARCHAR(255) NOT NULL,
    data JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TRIGGER update_cards_updated_at
    BEFORE UPDATE ON cards
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Index for fast user card lookups
CREATE INDEX idx_cards_user_id ON cards(user_id);
CREATE INDEX idx_cards_type ON cards(type);

-- =============================================================================
-- PACKS TABLE
-- =============================================================================
-- Content generation pack types (Newsletter, Blog Post, etc.)

CREATE TABLE IF NOT EXISTS packs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    icon VARCHAR(10),
    prompt_template_key VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert default packs
INSERT INTO packs (name, display_name, description, icon, prompt_template_key, is_active) VALUES
    ('newsletter', 'Newsletter Pack', 'Genera brief per newsletter professionali', '📧', 'brief.newsletter', TRUE),
    ('blog_post', 'Blog Post Pack', 'Genera brief per articoli di blog', '📝', 'brief.blog_post', TRUE)
ON CONFLICT (name) DO NOTHING;

-- =============================================================================
-- BRIEFS TABLE
-- =============================================================================
-- Generated briefs for each user/pack combination

CREATE TABLE IF NOT EXISTS briefs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    pack_id UUID NOT NULL REFERENCES packs(id),
    title VARCHAR(255),
    content JSONB NOT NULL DEFAULT '{}',
    answers JSONB DEFAULT '{}',
    context_snapshot JSONB DEFAULT '{}',
    llm_provider VARCHAR(50),
    llm_model VARCHAR(100),
    generation_time_ms INT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_briefs_user_id ON briefs(user_id);
CREATE INDEX idx_briefs_pack_id ON briefs(pack_id);
CREATE INDEX idx_briefs_created_at ON briefs(created_at DESC);

-- =============================================================================
-- PROMPTS TABLE
-- =============================================================================
-- Dynamic prompt templates with YAML fallback

CREATE TABLE IF NOT EXISTS prompts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key VARCHAR(100) UNIQUE NOT NULL,
    template TEXT NOT NULL,
    variables JSONB DEFAULT '[]',
    description TEXT,
    version INT DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TRIGGER update_prompts_updated_at
    BEFORE UPDATE ON prompts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE INDEX idx_prompts_key ON prompts(key);
CREATE INDEX idx_prompts_active ON prompts(is_active) WHERE is_active = TRUE;

-- =============================================================================
-- ONBOARDING SESSIONS TABLE
-- =============================================================================
-- Tracks onboarding progress

CREATE TABLE IF NOT EXISTS onboarding_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    state VARCHAR(50) NOT NULL DEFAULT 'created' CHECK (state IN (
        'created', 'researching', 'synthesizing', 'questions_ready',
        'generating_cards', 'done', 'error'
    )),
    snapshot JSONB DEFAULT '{}',
    clarifying_questions JSONB DEFAULT '[]',
    answers JSONB DEFAULT '{}',
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TRIGGER update_onboarding_sessions_updated_at
    BEFORE UPDATE ON onboarding_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE INDEX idx_onboarding_sessions_user_id ON onboarding_sessions(user_id);
CREATE INDEX idx_onboarding_sessions_state ON onboarding_sessions(state);

-- =============================================================================
-- LLM USAGE TRACKING TABLE
-- =============================================================================
-- Track API calls and costs

CREATE TABLE IF NOT EXISTS llm_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    provider VARCHAR(50) NOT NULL,
    model VARCHAR(100) NOT NULL,
    prompt_tokens INT DEFAULT 0,
    completion_tokens INT DEFAULT 0,
    total_tokens INT DEFAULT 0,
    cost_usd DECIMAL(10, 6) DEFAULT 0,
    operation VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_llm_usage_user_id ON llm_usage(user_id);
CREATE INDEX idx_llm_usage_provider ON llm_usage(provider);
CREATE INDEX idx_llm_usage_created_at ON llm_usage(created_at DESC);

-- =============================================================================
-- ROW LEVEL SECURITY (RLS)
-- =============================================================================
-- Enable RLS on all tables

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE cards ENABLE ROW LEVEL SECURITY;
ALTER TABLE briefs ENABLE ROW LEVEL SECURITY;
ALTER TABLE onboarding_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE llm_usage ENABLE ROW LEVEL SECURITY;

-- Service role can do everything (for backend)
CREATE POLICY "Service role full access on users" ON users
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access on cards" ON cards
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access on briefs" ON briefs
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access on onboarding_sessions" ON onboarding_sessions
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access on llm_usage" ON llm_usage
    FOR ALL USING (auth.role() = 'service_role');

-- Packs are public read
CREATE POLICY "Public read access on packs" ON packs
    FOR SELECT USING (TRUE);

-- Prompts are public read (for debugging, can restrict later)
CREATE POLICY "Public read access on prompts" ON prompts
    FOR SELECT USING (TRUE);
