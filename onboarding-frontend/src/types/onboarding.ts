/**
 * Onboarding Types
 * TypeScript types matching the onboarding API contracts
 */

// ============================================================================
// Enums
// ============================================================================

export enum OnboardingGoal {
  // Analytics (NEW - Primary goal)
  COMPANY_ANALYTICS = 'company_analytics',

  // Social Media (Legacy - for content generation)
  LINKEDIN_POST = 'linkedin_post',
  LINKEDIN_ARTICLE = 'linkedin_article',

  // Email Marketing (Legacy - for content generation)
  NEWSLETTER = 'newsletter',
  NEWSLETTER_PREMIUM = 'newsletter_premium',

  // Content Marketing (Legacy - for content generation)
  BLOG_POST = 'blog_post',
  ARTICLE = 'article',
}

// Labels for UI display
export const GOAL_LABELS: Record<OnboardingGoal, string> = {
  [OnboardingGoal.COMPANY_ANALYTICS]: 'Company Analytics',
  [OnboardingGoal.LINKEDIN_POST]: 'LinkedIn Post',
  [OnboardingGoal.LINKEDIN_ARTICLE]: 'LinkedIn Article',
  [OnboardingGoal.NEWSLETTER]: 'Newsletter',
  [OnboardingGoal.NEWSLETTER_PREMIUM]: 'Premium Newsletter',
  [OnboardingGoal.BLOG_POST]: 'Blog Post',
  [OnboardingGoal.ARTICLE]: 'Article',
};

// Descriptions for UI display
export const GOAL_DESCRIPTIONS: Record<OnboardingGoal, string> = {
  [OnboardingGoal.COMPANY_ANALYTICS]: 'Comprehensive analytics report with insights, opportunities, and recommendations',
  [OnboardingGoal.LINKEDIN_POST]: 'Short, engaging post (200-400 words)',
  [OnboardingGoal.LINKEDIN_ARTICLE]: 'Long-form thought leadership (800-1500 words)',
  [OnboardingGoal.NEWSLETTER]: 'Curated newsletter (1000-1500 words)',
  [OnboardingGoal.NEWSLETTER_PREMIUM]: 'Premium newsletter with research',
  [OnboardingGoal.BLOG_POST]: 'SEO-optimized blog article (1200-2000 words)',
  [OnboardingGoal.ARTICLE]: 'Generic article',
};

export enum SessionState {
  CREATED = 'created',
  RESEARCHING = 'researching',
  SYNTHESIZING = 'synthesizing',
  AWAITING_USER = 'awaiting_user',
  PAYLOAD_READY = 'payload_ready',
  EXECUTING = 'executing',
  DELIVERING = 'delivering',
  DONE = 'done',
  FAILED = 'failed',
}

// ============================================================================
// Domain Models
// ============================================================================

export interface Evidence {
  source: string;
  snippet: string;
  url?: string;
}

export interface CompanyInfo {
  name: string;
  legal_name?: string;
  website?: string;
  industry?: string;
  headquarters?: string;
  size_range?: string;
  description: string;
  key_offerings: string[];
  differentiators: string[];
  evidence: Evidence[];
}

export interface AudienceInfo {
  primary: string;
  pain_points: string[];
  demographics?: string;
  psychographics?: string;
}

export interface VoiceInfo {
  tone: string;
  style_guidelines: string[];
  forbidden_phrases?: string[];
  preferred_phrases?: string[];
}

export interface InsightsInfo {
  market_position?: string;
  competitive_advantages?: string[];
  recent_developments?: string[];
  content_opportunities?: string[];
}

export interface ClarifyingQuestion {
  id: string;
  question: string;
  reason: string;
  expected_response_type: 'string' | 'number' | 'boolean' | 'select' | 'multiselect';
  options?: string[];
  required: boolean;
  default_value?: any;
}

export interface CompanySnapshot {
  version: string;
  snapshot_id: string;
  generated_at: string;
  trace_id?: string;
  company: CompanyInfo;
  audience: AudienceInfo;
  voice: VoiceInfo;
  insights: InsightsInfo;
  clarifying_questions: ClarifyingQuestion[];
  clarifying_answers?: Record<string, any>;
}

export interface OnboardingSession {
  session_id: string;
  trace_id: string;
  brand_name: string;
  website?: string;
  goal: OnboardingGoal;
  user_email: string;
  state: SessionState;
  created_at: string;
  updated_at: string;
  snapshot?: CompanySnapshot;
  cgs_run_id?: string;
  delivery_status?: string;
  error_message?: string;
  metadata?: Record<string, any>;
}

// ============================================================================
// API Request/Response Types
// ============================================================================

export interface StartOnboardingRequest {
  brand_name: string;
  website?: string;
  goal: OnboardingGoal;
  user_email: string;
  additional_context?: string;
}

export interface SnapshotSummary {
  company_name: string;
  industry?: string;
  description: string;
  target_audience: string;
  tone: string;
  questions_count: number;
}

export interface QuestionResponse {
  id: string;
  question: string;
  reason: string;
  expected_response_type: string;
  options?: string[];
  required: boolean;
}

// Wizard-compatible question type
export interface Question {
  id: string;
  question: string;
  context?: string;
  type: 'text' | 'number' | 'boolean' | 'select' | 'enum' | 'multiselect';
  options?: Array<{
    value: string;
    label: string;
    description?: string;
  }>;
  required?: boolean;
}

export interface StartOnboardingResponse {
  session_id: string;
  trace_id: string;
  state: SessionState;
  snapshot_summary: SnapshotSummary;
  clarifying_questions: QuestionResponse[];
  message: string;
  next_action: string;
}

export interface SubmitAnswersRequest {
  answers: Record<string, any>;
}

export interface SubmitAnswersResponse {
  session_id: string;
  state: SessionState;
  content_title?: string;
  content_preview?: string;
  word_count?: number;
  delivery_status?: string;
  cgs_run_id?: string;
  execution_metrics?: {
    duration_seconds: number;
    [key: string]: any;
  };
  message: string;
}

export interface SessionStatusResponse {
  session_id: string;
  trace_id: string;
  brand_name: string;
  goal: OnboardingGoal;
  state: SessionState;
  created_at: string;
  updated_at: string;
  has_snapshot: boolean;
  snapshot_complete: boolean;
  cgs_run_id?: string;
  delivery_status?: string;
  error_message?: string;
}

export interface SessionDetailResponse {
  session: OnboardingSession;
  snapshot?: CompanySnapshot;
}

// ============================================================================
// UI State Types
// ============================================================================

export interface OnboardingFormData {
  brand_name: string;
  website: string;
  goal: OnboardingGoal;
  user_email: string;
  additional_context: string;
}

export interface AnswersFormData {
  [questionId: string]: any;
}

export interface OnboardingError {
  message: string;
  code?: string;
  details?: any;
}

export interface PollingState {
  isPolling: boolean;
  attempts: number;
  lastUpdate?: string;
}

// ============================================================================
// Helper Types
// ============================================================================

export type OnboardingStep = 0 | 1 | 2 | 3 | 4 | 5;

export interface StepConfig {
  index: OnboardingStep;
  label: string;
  description: string;
  canSkip: boolean;
  canGoBack: boolean;
}

export const STEP_CONFIGS: Record<OnboardingStep, StepConfig> = {
  0: {
    index: 0,
    label: 'Company Information',
    description: 'Tell us about your company',
    canSkip: false,
    canGoBack: false,
  },
  1: {
    index: 1,
    label: 'Research in Progress',
    description: 'Researching your company',
    canSkip: false,
    canGoBack: false,
  },
  2: {
    index: 2,
    label: 'Review Snapshot',
    description: 'Review company snapshot',
    canSkip: false,
    canGoBack: true,
  },
  3: {
    index: 3,
    label: 'Clarifying Questions',
    description: 'Answer a few questions',
    canSkip: false,
    canGoBack: true,
  },
  4: {
    index: 4,
    label: 'Generating Content',
    description: 'Creating your content',
    canSkip: false,
    canGoBack: false,
  },
  5: {
    index: 5,
    label: 'Results',
    description: 'Your content is ready',
    canSkip: false,
    canGoBack: false,
  },
};

// ============================================================================
// Analytics Dashboard Types
// ============================================================================

export interface ContentOpportunity {
  type: string;
  count: number;
  priority?: 'high' | 'medium' | 'low';
}

export interface Competitor {
  name: string;
  strength?: string;
  weakness?: string;
  threat_level?: 'high' | 'medium' | 'low';
}

export interface QuickWin {
  title: string;
  description?: string;
  impact?: 'high' | 'medium' | 'low';
  effort?: 'low' | 'medium' | 'high';
}

export interface OptimizationArea {
  score?: number;
  recommendations?: string[];
  strengths?: string[];
  weaknesses?: string[];
}

export interface OptimizationInsights {
  brand_voice?: OptimizationArea;
  seo?: OptimizationArea;
  messaging?: OptimizationArea;
  social_strategy?: OptimizationArea;
}

export interface ContentDistribution {
  [key: string]: number;
}

export interface AnalyticsData {
  company_score: number;
  content_opportunities: ContentOpportunity[];
  optimization_insights: OptimizationInsights;
  competitors: Competitor[];
  quick_wins: QuickWin[];
  content_distribution: ContentDistribution;
  metrics: Record<string, any>;
  full_report: string;
}
