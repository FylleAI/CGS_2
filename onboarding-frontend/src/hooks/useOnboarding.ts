/**
 * useOnboarding Hook
 * Main hook for orchestrating onboarding flow
 */

import { useCallback } from 'react';
import { useMutation } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { useOnboardingStore } from '@/store/onboardingStore';
import { onboardingApi } from '@/services/api/onboardingApi';
import type {
  StartOnboardingRequest,
  SubmitAnswersRequest,
  OnboardingStep,
  QuestionResponse,
} from '@/types/onboarding';
import { TOAST_CONFIG } from '@/config/constants';
import { OnboardingGoal } from '@/types/onboarding';

// ============================================================================
// Analytics Generic Questions
// ============================================================================

const ANALYTICS_GENERIC_QUESTIONS: QuestionResponse[] = [
  {
    id: 'variable_1',
    question: 'What is your primary business objective?',
    reason: 'Understanding your main goal helps us provide targeted strategic insights and recommendations.',
    expected_response_type: 'text',
    required: true,
  },
  {
    id: 'variable_2',
    question: 'What is your target market?',
    reason: 'Knowing your audience allows us to analyze market positioning and competitive landscape effectively.',
    expected_response_type: 'text',
    required: true,
  },
  {
    id: 'variable_3',
    question: 'What is your biggest challenge?',
    reason: 'Identifying key challenges enables us to focus on actionable solutions and quick wins.',
    expected_response_type: 'text',
    required: true,
  },
  {
    id: 'variable_4',
    question: 'What makes you unique?',
    reason: 'Your unique value proposition is crucial for differentiation analysis and content strategy.',
    expected_response_type: 'text',
    required: true,
  },
];

// ============================================================================
// Hook
// ============================================================================

export const useOnboarding = () => {
  const {
    session,
    snapshot,
    questions,
    currentStep,
    isLoading,
    error,
    setSession,
    setSnapshot,
    setQuestions,
    setCurrentStep,
    setLoading,
    setError,
    reset,
  } = useOnboardingStore();

  // ============================================================================
  // Start Onboarding Mutation
  // ============================================================================

  const startOnboardingMutation = useMutation({
    mutationFn: (data: StartOnboardingRequest) => onboardingApi.startOnboarding(data),
    onMutate: () => {
      setLoading(true);
      setError(null);
      setCurrentStep(1); // Move to research progress step
    },
    onSuccess: (data, variables) => {
      // Extract goal from request
      const requestedGoal = variables.goal;

      // Store session data
      setSession({
        session_id: data.session_id,
        trace_id: data.trace_id,
        brand_name: variables.brand_name,
        goal: requestedGoal,
        state: data.state,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      });

      // Determine which questions to use
      const questionsToUse = requestedGoal === OnboardingGoal.COMPANY_ANALYTICS
        ? ANALYTICS_GENERIC_QUESTIONS
        : data.clarifying_questions;

      // Store snapshot summary (we'll get full snapshot later)
      if (data.snapshot_summary) {
        setSnapshot({
          version: '1.0',
          snapshot_id: data.session_id,
          generated_at: new Date().toISOString(),
          trace_id: data.trace_id,
          company: {
            name: data.snapshot_summary.company_name,
            description: data.snapshot_summary.description,
            industry: data.snapshot_summary.industry,
            key_offerings: [],
            differentiators: [],
            evidence: [],
          },
          audience: {
            primary: data.snapshot_summary.target_audience,
            pain_points: [],
          },
          voice: {
            tone: data.snapshot_summary.tone,
            style_guidelines: [],
          },
          insights: {},
          clarifying_questions: questionsToUse.map(q => ({
            ...q,
            expected_response_type: q.expected_response_type as any,
          })),
        });
      }

      // Store questions (generic for analytics, backend-generated for content)
      setQuestions(questionsToUse);

      // Move to snapshot review step
      setCurrentStep(2);
      setLoading(false);

      toast.success('Research completed successfully!', {
        duration: TOAST_CONFIG.SUCCESS_DURATION,
      });
    },
    onError: (err: any) => {
      setError({
        message: err.message || 'Failed to start onboarding',
        code: err.code,
        details: err.details,
      });
      setLoading(false);
      setCurrentStep(0); // Go back to input step

      toast.error(err.message || 'Failed to start onboarding', {
        duration: TOAST_CONFIG.ERROR_DURATION,
      });
    },
  });

  // ============================================================================
  // Submit Answers Mutation
  // ============================================================================

  const submitAnswersMutation = useMutation({
    mutationFn: ({ sessionId, data }: { sessionId: string; data: SubmitAnswersRequest }) =>
      onboardingApi.submitAnswers(sessionId, data),
    onMutate: () => {
      setLoading(true);
      setError(null);
      setCurrentStep(4); // Move to execution step
    },
    onSuccess: (data) => {
      // Update session with results
      setSession({
        ...session!,
        state: data.state,
        cgs_run_id: data.cgs_run_id,
        delivery_status: data.delivery_status,
        updated_at: new Date().toISOString(),
        metadata: {
          content_title: data.content_title,
          content_preview: data.content_preview,
          word_count: data.word_count,
          execution_metrics: data.execution_metrics,
        },
      });

      // Move to results step
      setCurrentStep(5);
      setLoading(false);

      toast.success('Content generated successfully!', {
        duration: TOAST_CONFIG.SUCCESS_DURATION,
      });
    },
    onError: (err: any) => {
      setError({
        message: err.message || 'Failed to generate content',
        code: err.code,
        details: err.details,
      });
      setLoading(false);
      setCurrentStep(3); // Go back to questions step

      toast.error(err.message || 'Failed to generate content', {
        duration: TOAST_CONFIG.ERROR_DURATION,
      });
    },
  });

  // ============================================================================
  // Actions
  // ============================================================================

  const startOnboarding = useCallback(
    (data: StartOnboardingRequest) => {
      startOnboardingMutation.mutate(data);
    },
    [startOnboardingMutation]
  );

  const submitAnswers = useCallback(
    (answers: Record<string, any>) => {
      if (!session?.session_id) {
        toast.error('No active session');
        return;
      }

      submitAnswersMutation.mutate({
        sessionId: session.session_id,
        data: { answers },
      });
    },
    [session, submitAnswersMutation]
  );

  const goToStep = useCallback(
    (step: OnboardingStep) => {
      setCurrentStep(step);
    },
    [setCurrentStep]
  );

  const resetOnboarding = useCallback(() => {
    reset();
    toast.success('Onboarding reset');
  }, [reset]);

  // ============================================================================
  // Return
  // ============================================================================

  return {
    // State
    session,
    snapshot,
    questions,
    currentStep,
    isLoading,
    error,

    // Actions
    startOnboarding,
    submitAnswers,
    goToStep,
    resetOnboarding,

    // Mutation states
    isStarting: startOnboardingMutation.isPending,
    isSubmitting: submitAnswersMutation.isPending,
  };
};

export default useOnboarding;

