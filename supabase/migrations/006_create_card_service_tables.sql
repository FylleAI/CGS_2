-- Migration: Create Card Service Tables
-- Date: 2025-10-25
-- Description: Create context_cards and card_relationships tables for Card Service V1

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- Table: context_cards
-- Description: Stores atomic cards (Product, Persona, Campaign, Topic)
-- ============================================================================
CREATE TABLE IF NOT EXISTS context_cards (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id UUID NOT NULL,
  card_type VARCHAR(50) NOT NULL,
  title VARCHAR(500) NOT NULL,
  content JSONB NOT NULL,
  metrics JSONB DEFAULT '{}',
  notes TEXT DEFAULT '',
  version INT DEFAULT 1,
  is_active BOOLEAN DEFAULT true,
  created_by UUID,
  updated_by UUID,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),

  -- Constraints
  CONSTRAINT valid_card_type CHECK (card_type IN ('product', 'persona', 'campaign', 'topic'))
);

-- Indexes for context_cards
CREATE INDEX IF NOT EXISTS idx_cards_tenant_id ON context_cards(tenant_id);
CREATE INDEX IF NOT EXISTS idx_cards_tenant_type ON context_cards(tenant_id, card_type);
CREATE INDEX IF NOT EXISTS idx_cards_active ON context_cards(is_active);
CREATE INDEX IF NOT EXISTS idx_cards_created_at ON context_cards(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_cards_updated_at ON context_cards(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_cards_content ON context_cards USING GIN(content);

-- Partial unique index: Only one active card per type per tenant
CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_active_card_per_type
ON context_cards(tenant_id, card_type)
WHERE is_active = true;

-- ============================================================================
-- Table: card_relationships
-- Description: Stores relationships between cards
-- ============================================================================
CREATE TABLE IF NOT EXISTS card_relationships (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  source_card_id UUID NOT NULL REFERENCES context_cards(id) ON DELETE CASCADE,
  target_card_id UUID NOT NULL REFERENCES context_cards(id) ON DELETE CASCADE,
  relationship_type VARCHAR(50) NOT NULL,
  strength FLOAT DEFAULT 1.0 CHECK (strength >= 0.0 AND strength <= 1.0),
  created_at TIMESTAMPTZ DEFAULT NOW(),

  -- Constraints
  CONSTRAINT no_self_reference CHECK (source_card_id != target_card_id),
  CONSTRAINT valid_relationship_type CHECK (relationship_type IN (
    'targets',
    'promoted_in',
    'is_target_of',
    'discusses',
    'links_to',
    'derives_from',
    'supports'
  ))
);

-- Indexes for card_relationships
CREATE INDEX IF NOT EXISTS idx_relationships_source ON card_relationships(source_card_id);
CREATE INDEX IF NOT EXISTS idx_relationships_target ON card_relationships(target_card_id);
CREATE INDEX IF NOT EXISTS idx_relationships_type ON card_relationships(relationship_type);
CREATE INDEX IF NOT EXISTS idx_relationships_source_target ON card_relationships(source_card_id, target_card_id);

-- ============================================================================
-- Row Level Security (RLS) Policies
-- ============================================================================

-- Enable RLS on context_cards
ALTER TABLE context_cards ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see cards from their tenant
CREATE POLICY "Users can view their tenant's cards"
ON context_cards
FOR SELECT
USING (tenant_id = auth.uid()::uuid);

-- Policy: Users can only insert cards for their tenant
CREATE POLICY "Users can create cards for their tenant"
ON context_cards
FOR INSERT
WITH CHECK (tenant_id = auth.uid()::uuid);

-- Policy: Users can only update cards from their tenant
CREATE POLICY "Users can update their tenant's cards"
ON context_cards
FOR UPDATE
USING (tenant_id = auth.uid()::uuid)
WITH CHECK (tenant_id = auth.uid()::uuid);

-- Policy: Users can only delete cards from their tenant
CREATE POLICY "Users can delete their tenant's cards"
ON context_cards
FOR DELETE
USING (tenant_id = auth.uid()::uuid);

-- Enable RLS on card_relationships
ALTER TABLE card_relationships ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see relationships for their tenant's cards
CREATE POLICY "Users can view their tenant's relationships"
ON card_relationships
FOR SELECT
USING (
  source_card_id IN (
    SELECT id FROM context_cards WHERE tenant_id = auth.uid()::uuid
  )
);

-- Policy: Users can only create relationships for their tenant's cards
CREATE POLICY "Users can create relationships for their tenant's cards"
ON card_relationships
FOR INSERT
WITH CHECK (
  source_card_id IN (
    SELECT id FROM context_cards WHERE tenant_id = auth.uid()::uuid
  )
  AND target_card_id IN (
    SELECT id FROM context_cards WHERE tenant_id = auth.uid()::uuid
  )
);

-- Policy: Users can only delete relationships for their tenant's cards
CREATE POLICY "Users can delete their tenant's relationships"
ON card_relationships
FOR DELETE
USING (
  source_card_id IN (
    SELECT id FROM context_cards WHERE tenant_id = auth.uid()::uuid
  )
);

-- ============================================================================
-- Triggers for updated_at
-- ============================================================================

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for context_cards
CREATE TRIGGER update_context_cards_updated_at
BEFORE UPDATE ON context_cards
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Comments for documentation
-- ============================================================================

COMMENT ON TABLE context_cards IS 'Stores atomic cards: Product, Persona, Campaign, Topic';
COMMENT ON COLUMN context_cards.id IS 'Unique identifier for the card';
COMMENT ON COLUMN context_cards.tenant_id IS 'Tenant identifier (user email or organization ID)';
COMMENT ON COLUMN context_cards.card_type IS 'Type of card: product, persona, campaign, topic';
COMMENT ON COLUMN context_cards.title IS 'Card title';
COMMENT ON COLUMN context_cards.content IS 'Card content as JSONB (flexible schema per type)';
COMMENT ON COLUMN context_cards.metrics IS 'Card metrics as JSONB';
COMMENT ON COLUMN context_cards.notes IS 'User notes about the card';
COMMENT ON COLUMN context_cards.version IS 'Version number for tracking changes';
COMMENT ON COLUMN context_cards.is_active IS 'Soft delete flag';
COMMENT ON COLUMN context_cards.created_by IS 'User who created the card';
COMMENT ON COLUMN context_cards.updated_by IS 'User who last updated the card';

COMMENT ON TABLE card_relationships IS 'Stores relationships between cards';
COMMENT ON COLUMN card_relationships.id IS 'Unique identifier for the relationship';
COMMENT ON COLUMN card_relationships.source_card_id IS 'Source card ID';
COMMENT ON COLUMN card_relationships.target_card_id IS 'Target card ID';
COMMENT ON COLUMN card_relationships.relationship_type IS 'Type of relationship';
COMMENT ON COLUMN card_relationships.strength IS 'Strength of relationship (0.0 to 1.0)';