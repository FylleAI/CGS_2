export enum CardType {
  PRODUCT = 'product',
  TARGET = 'target',
  CAMPAIGNS = 'campaigns',
  TOPIC = 'topic',
  BRAND_VOICE = 'brand_voice',
  COMPETITOR = 'competitor',
  PERFORMANCE = 'performance',
  FEEDBACK = 'feedback'
}

export interface BaseCard {
  id: string;
  type: CardType;
  title: string;
  createdAt: string;
  updatedAt: string;
  sessionId?: string;
}

export interface ProductCard extends BaseCard {
  type: CardType.PRODUCT;
  valueProposition: string;
  features: string[];
  differentiators: string[];
  useCases: string[];
  performanceMetrics: {
    metric: string;
    value: string;
  }[];
}

export interface TargetCard extends BaseCard {
  type: CardType.TARGET;
  icpName: string;
  description: string;
  painPoints: string[];
  goals: string[];
  preferredLanguage: string;
  communicationChannels: string[];
  demographics?: {
    ageRange?: string;
    location?: string;
    role?: string;
    industry?: string;
  };
}

export interface CampaignsCard extends BaseCard {
  type: CardType.CAMPAIGNS;
  objective: string;
  keyMessages: string[];
  tone: string;
  assets: {
    name: string;
    type: string;
    status: string;
  }[];
  results?: {
    metric: string;
    value: string;
    trend?: 'up' | 'down' | 'stable';
  }[];
  learnings: string[];
}

export interface TopicCard extends BaseCard {
  type: CardType.TOPIC;
  description: string;
  keywords: string[];
  angles: string[];
  relatedContent: {
    title: string;
    type: string;
    url?: string;
  }[];
  trends: {
    trend: string;
    relevance: 'high' | 'medium' | 'low';
  }[];
}

export interface BrandVoiceCard extends BaseCard {
  type: CardType.BRAND_VOICE;
  toneDescription: string;
  styleGuidelines: string[];
  dosExamples: string[];
  dontsExamples: string[];
  termsToUse: string[];
  termsToAvoid: string[];
}

export interface CompetitorCard extends BaseCard {
  type: CardType.COMPETITOR;
  competitorName: string;
  positioning: string;
  keyMessages: string[];
  strengths: string[];
  weaknesses: string[];
  differentiationOpportunities: string[];
}

export interface PerformanceCard extends BaseCard {
  type: CardType.PERFORMANCE;
  period: string;
  metrics: {
    channel: string;
    contentType: string;
    ctr?: number;
    engagement?: number;
    conversions?: number;
    impressions?: number;
  }[];
  topPerformingContent: {
    title: string;
    type: string;
    metric: string;
    value: string;
  }[];
  insights: string[];
}

export interface FeedbackCard extends BaseCard {
  type: CardType.FEEDBACK;
  source: 'customer_feedback' | 'team_feedback' | 'ab_test' | 'analytics' | 'other';
  summary: string;
  details: string;
  actionItems: string[];
  relatedCards?: string[];
  priority: 'high' | 'medium' | 'low';
}

export type Card = 
  | ProductCard 
  | TargetCard 
  | CampaignsCard 
  | TopicCard 
  | BrandVoiceCard 
  | CompetitorCard 
  | PerformanceCard 
  | FeedbackCard;

export interface CardsSnapshot {
  sessionId: string;
  generatedAt: string;
  cards: Card[];
}

export const CardTypeLabels: Record<CardType, string> = {
  [CardType.PRODUCT]: 'Prodotto/Servizio',
  [CardType.TARGET]: 'Target',
  [CardType.CAMPAIGNS]: 'Campagne',
  [CardType.TOPIC]: 'Topic',
  [CardType.BRAND_VOICE]: 'Brand Voice',
  [CardType.COMPETITOR]: 'Competitor',
  [CardType.PERFORMANCE]: 'Performance',
  [CardType.FEEDBACK]: 'Feedback'
};

export const CardTypeDescriptions: Record<CardType, string> = {
  [CardType.PRODUCT]: 'Value proposition, features, differenziatori, casi d\'uso e metriche',
  [CardType.TARGET]: 'Profilo ICP, pain points, obiettivi, linguaggio e canali',
  [CardType.CAMPAIGNS]: 'Obiettivi, messaggi chiave, tonalità, asset e risultati',
  [CardType.TOPIC]: 'Argomenti ricorrenti, keyword, angolazioni e trend',
  [CardType.BRAND_VOICE]: 'Linee guida stilistiche, tono, esempi do/don\'t',
  [CardType.COMPETITOR]: 'Posizionamento, messaging, gap e opportunità',
  [CardType.PERFORMANCE]: 'CTR, engagement, conversioni per contenuto e canale',
  [CardType.FEEDBACK]: 'Apprendimenti da clienti, team e A/B test'
};
