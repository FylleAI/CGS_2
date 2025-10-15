/**
 * Onboarding Types
 * TypeScript types matching the onboarding API contracts
 */

// ============================================================================
// Enums
// ============================================================================

export enum OnboardingGoal {
  LINKEDIN_POST = 'linkedin_post',
  NEWSLETTER = 'newsletter',
  NEWSLETTER_PREMIUM = 'newsletter_premium',
  ARTICLE = 'article',
}

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
  user_email?: string;
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
  user_email?: string;
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

