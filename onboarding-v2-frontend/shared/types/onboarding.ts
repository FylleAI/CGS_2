/**
 * Onboarding Types - Mapped from Python backend models
 * 
 * These types match the FastAPI backend at Onboarding/onboarding/
 * Domain models: domain/models.py
 * API models: api/models.py
 */

// ============================================================================
// ENUMS
// ============================================================================

export enum OnboardingGoal {
  COMPANY_SNAPSHOT = "company_snapshot",
  CONTENT_GENERATION = "content_generation"
}

export enum SessionState {
  CREATED = "created",
  RESEARCHING = "researching",
  SYNTHESIZING = "synthesizing",
  AWAITING_USER = "awaiting_user",
  PAYLOAD_READY = "payload_ready",
  EXECUTING = "executing",
  DELIVERING = "delivering",
  DONE = "done",
  FAILED = "failed"
}

// ============================================================================
// DOMAIN MODELS
// ============================================================================

export interface Evidence {
  source: string;
  excerpt: string;
  confidence?: number;
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
  primary?: string;
  secondary: string[];
  pain_points: string[];
  desired_outcomes: string[];
}

export interface VoiceInfo {
  tone?: string;
  style_guidelines: string[];
  forbidden_phrases: string[];
  cta_preferences: string[];
}

export interface InsightsInfo {
  positioning?: string;
  key_messages: string[];
  recent_news: string[];
  competitors: string[];
}

export interface ClarifyingQuestion {
  id: string;
  question: string;
  reason: string;
  expected_response_type: "string" | "select" | "boolean" | "number";
  options?: string[];
  required: boolean;
}

export interface SourceMetadata {
  tool: string;
  timestamp: string;
  cost_usd?: number;
  token_usage?: number;
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
  clarifying_answers: Record<string, any>;
  source_metadata: SourceMetadata[];
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
  cgs_payload?: Record<string, any>;
  cgs_run_id?: string;
  cgs_response?: Record<string, any>;
  company_context_id?: string;
  delivery_status?: string;
  delivery_message_id?: string;
  delivery_timestamp?: string;
  error_message?: string;
  metadata: Record<string, any>;
}

// ============================================================================
// API REQUEST MODELS
// ============================================================================

export interface StartOnboardingRequest {
  brand_name: string;
  website?: string;
  goal: OnboardingGoal;
  user_email: string;
  additional_context?: string;
}

export interface SubmitAnswersRequest {
  answers: Record<string, any>;
}

export interface ExecuteWorkflowRequest {
  dry_run?: boolean;
  requested_provider?: string;
}

// ============================================================================
// API RESPONSE MODELS
// ============================================================================

export interface QuestionResponse {
  id: string;
  question: string;
  reason: string;
  expected_response_type: string;
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

export interface StartOnboardingResponse {
  session_id: string;
  trace_id: string;
  state: SessionState;
  snapshot_summary?: SnapshotSummary;
  clarifying_questions: QuestionResponse[];
  message: string;
  next_action: string;
}

export interface SubmitAnswersResponse {
  session_id: string;
  state: SessionState;
  message: string;
  snapshot?: CompanySnapshot;
  card_ids?: string[];
  cards_created?: number;
  partial?: boolean;
  cards_service_url?: string;
  content_title?: string;
  content_preview?: string;
  word_count?: number;
  delivery_status?: string;
  workflow_metrics?: Record<string, any>;
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
  cgs_response?: Record<string, any>;
  delivery_status?: string;
  delivery_message_id?: string;
  error_message?: string;
  metadata: Record<string, any>;
}

export interface HealthCheckResponse {
  status: string;
  version: string;
  services: Record<string, boolean>;
  cgs_healthy: boolean;
}

export interface ErrorResponse {
  error: string;
  detail?: string;
  session_id?: string;
}
