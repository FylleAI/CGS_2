/**
 * Onboarding Types for Fylle Onboarding v3
 */

export enum OnboardingGoal {
  COMPANY_SNAPSHOT = 'company_snapshot',
  CONTENT_GENERATION = 'content_generation',
}

export enum SessionState {
  CREATED = 'created',
  RESEARCHING = 'researching',
  SYNTHESIZING = 'synthesizing',
  QUESTIONS_READY = 'questions_ready',
  GENERATING_CARDS = 'generating_cards',
  DONE = 'done',
  ERROR = 'error',
}

export interface QuestionResponse {
  id: string;
  question: string;
  reason: string;
  expected_response_type: 'text' | 'select' | 'multiselect';
  options?: string[];
  required: boolean;
}

export interface SnapshotSummary {
  company_name: string;
  industry?: string;
  description: string;
  target_audience?: string;
  tone?: string;
  questions_count: number;
}

export interface StartOnboardingRequest {
  brand_name: string;
  website?: string;
  goal: OnboardingGoal;
  user_email: string;
  additional_context?: string;
}

export interface StartOnboardingResponse {
  session_id: string;
  user_id: string;
  trace_id: string;
  state: SessionState;
  snapshot_summary?: SnapshotSummary;
  clarifying_questions: QuestionResponse[];
  message: string;
  next_action: string;
}

export interface SubmitAnswersRequest {
  answers: Record<string, any>;
}

export interface SubmitAnswersResponse {
  session_id: string;
  user_id: string;
  state: SessionState;
  message: string;
  card_ids?: string[];
  cards_created?: number;
  redirect_url?: string;
}

export interface SessionStatusResponse {
  session_id: string;
  user_id: string;
  state: SessionState;
  brand_name: string;
  goal: OnboardingGoal;
  has_snapshot: boolean;
  snapshot_complete: boolean;
  error_message?: string;
}
