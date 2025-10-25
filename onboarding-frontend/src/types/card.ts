/**
 * Card Service Types
 * TypeScript types for Card Service domain models
 */

export enum CardType {
  PRODUCT = 'product',
  PERSONA = 'persona',
  CAMPAIGN = 'campaign',
  TOPIC = 'topic',
}

export enum RelationshipType {
  TARGETS = 'targets',
  PROMOTED_IN = 'promoted_in',
  IS_TARGET_OF = 'is_target_of',
  DISCUSSES = 'discusses',
  LINKS_TO = 'links_to',
  DERIVES_FROM = 'derives_from',
  SUPPORTS = 'supports',
}

// ============================================================================
// Card Content Types
// ============================================================================

export interface ProductContent {
  value_proposition: string;
  features: string[];
  differentiators: string[];
  use_cases: string[];
  target_market: string;
}

export interface PersonaContent {
  icp_profile: string;
  pain_points: string[];
  goals: string[];
  preferred_language: string;
  communication_channels: string[];
  demographics?: Record<string, any>;
  psychographics?: Record<string, any>;
}

export interface CampaignContent {
  objective: string;
  key_messages: string[];
  tone: string;
  target_personas: string[];
  assets_produced: string[];
  results?: string;
  learnings?: string;
}

export interface TopicContent {
  keywords: string[];
  angles: string[];
  related_content: string[];
  trend_status: 'emerging' | 'stable' | 'declining';
  frequency: string;
  audience_interest: string;
}

export type CardContent = ProductContent | PersonaContent | CampaignContent | TopicContent;

// ============================================================================
// Base Card Types
// ============================================================================

export interface BaseCard {
  id: string;
  tenant_id: string;
  card_type: CardType;
  title: string;
  content: Record<string, any>;
  metrics: Record<string, any>;
  notes: string;
  version: number;
  is_active: boolean;
  created_by?: string;
  updated_by?: string;
  created_at: string;
  updated_at: string;
}

export interface ProductCard extends BaseCard {
  card_type: CardType.PRODUCT;
  content: ProductContent;
}

export interface PersonaCard extends BaseCard {
  card_type: CardType.PERSONA;
  content: PersonaContent;
}

export interface CampaignCard extends BaseCard {
  card_type: CardType.CAMPAIGN;
  content: CampaignContent;
}

export interface TopicCard extends BaseCard {
  card_type: CardType.TOPIC;
  content: TopicContent;
}

export type AnyCard = ProductCard | PersonaCard | CampaignCard | TopicCard;

// ============================================================================
// Relationship Types
// ============================================================================

export interface CardRelationship {
  id: string;
  source_card_id: string;
  target_card_id: string;
  relationship_type: RelationshipType;
  strength: number;
  created_at: string;
}

// ============================================================================
// API Request/Response Types
// ============================================================================

export interface CreateCardRequest {
  card_type: CardType;
  title: string;
  content: Record<string, any>;
  metrics?: Record<string, any>;
  notes?: string;
}

export interface UpdateCardRequest {
  title?: string;
  content?: Record<string, any>;
  metrics?: Record<string, any>;
  notes?: string;
}

export interface CardResponse extends BaseCard {
  relationships: CardRelationship[];
}

export interface CreateRelationshipRequest {
  target_card_id: string;
  relationship_type: RelationshipType;
  strength?: number;
}

export interface RelationshipResponse extends CardRelationship {}

// ============================================================================
// Context Types (for CGS integration)
// ============================================================================

export interface CardsContextResponse {
  product: CardResponse[];
  persona: CardResponse[];
  campaign: CardResponse[];
  topic: CardResponse[];
}

export interface RagContextResponse {
  context: string;
}

// ============================================================================
// Snapshot Types (for Onboarding integration)
// ============================================================================

export interface CompanyInfo {
  company_name: string;
  value_proposition: string;
  features: string[];
  differentiators: string[];
  use_cases: string[];
  target_market: string;
  conversion_rate?: number;
  avg_deal_size?: number;
}

export interface AudienceInfo {
  persona_name: string;
  icp_profile: string;
  pain_points: string[];
  goals: string[];
  preferred_language: string;
  communication_channels: string[];
  demographics?: Record<string, any>;
  psychographics?: Record<string, any>;
}

export interface GoalInfo {
  campaign_name: string;
  objective: string;
  key_messages: string[];
  tone: string;
  assets_produced: string[];
  reach?: number;
  conversions?: number;
  roi?: number;
}

export interface InsightsInfo {
  topic_name: string;
  keywords: string[];
  angles: string[];
  related_content: string[];
  trend_status: 'emerging' | 'stable' | 'declining';
  frequency: string;
  audience_interest: string;
  search_volume?: number;
  trend_score?: number;
}

export interface CompanySnapshot {
  company_info: CompanyInfo;
  audience_info: AudienceInfo;
  goal: GoalInfo;
  insights: InsightsInfo;
}

// ============================================================================
// UI State Types
// ============================================================================

export interface CardEditorState {
  card: AnyCard | null;
  isLoading: boolean;
  error: string | null;
  isDirty: boolean;
}

export interface CardListState {
  cards: CardResponse[];
  isLoading: boolean;
  error: string | null;
  filter?: CardType;
}

export interface RelationshipEditorState {
  relationships: CardRelationship[];
  isLoading: boolean;
  error: string | null;
}

