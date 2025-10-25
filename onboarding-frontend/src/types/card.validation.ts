/**
 * Card Service Validation Schemas
 * Zod schemas for client-side validation
 */

import { z } from 'zod';

// ============================================================================
// Enum Schemas
// ============================================================================

export const CardTypeSchema = z.enum(['product', 'persona', 'campaign', 'topic']);

export const RelationshipTypeSchema = z.enum([
  'targets',
  'promoted_in',
  'is_target_of',
  'discusses',
  'links_to',
  'derives_from',
  'supports',
]);

// ============================================================================
// Content Schemas
// ============================================================================

export const ProductContentSchema = z.object({
  value_proposition: z.string().min(1, 'Value proposition is required'),
  features: z.array(z.string()).default([]),
  differentiators: z.array(z.string()).default([]),
  use_cases: z.array(z.string()).default([]),
  target_market: z.string().default(''),
});

export const PersonaContentSchema = z.object({
  icp_profile: z.string().min(1, 'ICP profile is required'),
  pain_points: z.array(z.string()).default([]),
  goals: z.array(z.string()).default([]),
  preferred_language: z.string().default(''),
  communication_channels: z.array(z.string()).default([]),
  demographics: z.record(z.any()).optional(),
  psychographics: z.record(z.any()).optional(),
});

export const CampaignContentSchema = z.object({
  objective: z.string().min(1, 'Objective is required'),
  key_messages: z.array(z.string()).default([]),
  tone: z.string().default(''),
  target_personas: z.array(z.string()).default([]),
  assets_produced: z.array(z.string()).default([]),
  results: z.string().optional(),
  learnings: z.string().optional(),
});

export const TopicContentSchema = z.object({
  keywords: z.array(z.string()).default([]),
  angles: z.array(z.string()).default([]),
  related_content: z.array(z.string()).default([]),
  trend_status: z.enum(['emerging', 'stable', 'declining']).default('stable'),
  frequency: z.string().default(''),
  audience_interest: z.string().default(''),
});

// ============================================================================
// Request Schemas
// ============================================================================

export const CreateCardRequestSchema = z.object({
  card_type: CardTypeSchema,
  title: z.string().min(1, 'Title is required').max(500),
  content: z.record(z.any()),
  metrics: z.record(z.any()).optional(),
  notes: z.string().max(2000).optional(),
});

export const UpdateCardRequestSchema = z.object({
  title: z.string().min(1).max(500).optional(),
  content: z.record(z.any()).optional(),
  metrics: z.record(z.any()).optional(),
  notes: z.string().max(2000).optional(),
});

export const CreateRelationshipRequestSchema = z.object({
  target_card_id: z.string().uuid('Invalid target card ID'),
  relationship_type: RelationshipTypeSchema,
  strength: z.number().min(0).max(1).default(1.0),
});

// ============================================================================
// Response Schemas
// ============================================================================

export const CardRelationshipSchema = z.object({
  id: z.string().uuid(),
  source_card_id: z.string().uuid(),
  target_card_id: z.string().uuid(),
  relationship_type: RelationshipTypeSchema,
  strength: z.number().min(0).max(1),
  created_at: z.string().datetime(),
});

export const BaseCardSchema = z.object({
  id: z.string().uuid(),
  tenant_id: z.string().uuid(),
  card_type: CardTypeSchema,
  title: z.string(),
  content: z.record(z.any()),
  metrics: z.record(z.any()),
  notes: z.string(),
  version: z.number().int().positive(),
  is_active: z.boolean(),
  created_by: z.string().uuid().optional(),
  updated_by: z.string().uuid().optional(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});

export const CardResponseSchema = BaseCardSchema.extend({
  relationships: z.array(CardRelationshipSchema).default([]),
});

export const CardsContextResponseSchema = z.object({
  product: z.array(CardResponseSchema).default([]),
  persona: z.array(CardResponseSchema).default([]),
  campaign: z.array(CardResponseSchema).default([]),
  topic: z.array(CardResponseSchema).default([]),
});

export const RagContextResponseSchema = z.object({
  context: z.string(),
});

// ============================================================================
// Snapshot Schemas
// ============================================================================

export const CompanyInfoSchema = z.object({
  company_name: z.string().min(1),
  value_proposition: z.string().min(1),
  features: z.array(z.string()).default([]),
  differentiators: z.array(z.string()).default([]),
  use_cases: z.array(z.string()).default([]),
  target_market: z.string().default(''),
  conversion_rate: z.number().optional(),
  avg_deal_size: z.number().optional(),
});

export const AudienceInfoSchema = z.object({
  persona_name: z.string().min(1),
  icp_profile: z.string().min(1),
  pain_points: z.array(z.string()).default([]),
  goals: z.array(z.string()).default([]),
  preferred_language: z.string().default(''),
  communication_channels: z.array(z.string()).default([]),
  demographics: z.record(z.any()).optional(),
  psychographics: z.record(z.any()).optional(),
});

export const GoalInfoSchema = z.object({
  campaign_name: z.string().min(1),
  objective: z.string().min(1),
  key_messages: z.array(z.string()).default([]),
  tone: z.string().default(''),
  assets_produced: z.array(z.string()).default([]),
  reach: z.number().optional(),
  conversions: z.number().optional(),
  roi: z.number().optional(),
});

export const InsightsInfoSchema = z.object({
  topic_name: z.string().min(1),
  keywords: z.array(z.string()).default([]),
  angles: z.array(z.string()).default([]),
  related_content: z.array(z.string()).default([]),
  trend_status: z.enum(['emerging', 'stable', 'declining']).default('stable'),
  frequency: z.string().default(''),
  audience_interest: z.string().default(''),
  search_volume: z.number().optional(),
  trend_score: z.number().optional(),
});

export const CompanySnapshotSchema = z.object({
  company_info: CompanyInfoSchema,
  audience_info: AudienceInfoSchema,
  goal: GoalInfoSchema,
  insights: InsightsInfoSchema,
});

// ============================================================================
// Type Exports
// ============================================================================

export type CreateCardRequest = z.infer<typeof CreateCardRequestSchema>;
export type UpdateCardRequest = z.infer<typeof UpdateCardRequestSchema>;
export type CardResponse = z.infer<typeof CardResponseSchema>;
export type CreateRelationshipRequest = z.infer<typeof CreateRelationshipRequestSchema>;
export type CompanySnapshot = z.infer<typeof CompanySnapshotSchema>;

