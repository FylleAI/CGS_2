/**
 * Card Types and Interfaces
 */

export type CardType = 'product' | 'persona' | 'campaign' | 'topic';

export type RelationshipType = 
  | 'targets'
  | 'promoted_in'
  | 'is_target_of'
  | 'discusses';

export interface ProductContent {
  name: string;
  description: string;
  features?: string[];
  pricing?: string;
  target_market?: string;
}

export interface PersonaContent {
  name: string;
  role: string;
  industry?: string;
  pain_points?: string[];
  goals?: string[];
  demographics?: Record<string, any>;
}

export interface CampaignContent {
  name: string;
  objective: string;
  channels?: string[];
  budget?: string;
  timeline?: string;
  kpis?: string[];
}

export interface TopicContent {
  title: string;
  description: string;
  keywords?: string[];
  subtopics?: string[];
  content_types?: string[];
}

export type CardContent = 
  | ProductContent 
  | PersonaContent 
  | CampaignContent 
  | TopicContent;

export interface BaseCard {
  id: string;
  tenant_id: string;
  card_type: CardType;
  title: string;
  content: CardContent;
  metrics?: Record<string, any>;
  notes?: string;
  is_active: boolean;
  version: number;
  created_at: string;
  updated_at: string;
  created_by?: string;
}

export interface CardRelationship {
  id: string;
  source_card_id: string;
  target_card_id: string;
  relationship_type: RelationshipType;
  strength: number; // 0.0 to 1.0
  metadata?: Record<string, any>;
  created_at: string;
}

export interface CardResponse {
  card: BaseCard;
  relationships: CardRelationship[];
}

export interface CreateCardRequest {
  card_type: CardType;
  title: string;
  content: CardContent;
  notes?: string;
}

export interface UpdateCardRequest {
  title?: string;
  content?: Partial<CardContent>;
  notes?: string;
}

export interface CreateRelationshipRequest {
  source_card_id: string;
  target_card_id: string;
  relationship_type: RelationshipType;
  strength?: number;
}

