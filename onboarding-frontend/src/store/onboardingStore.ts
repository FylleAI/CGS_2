/**
 * Onboarding Store
 * Zustand store for onboarding flow state management
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import type {
  OnboardingSession,
  CompanySnapshot,
  OnboardingStep,
  OnboardingError,
  PollingState,
  QuestionResponse,
} from '@/types/onboarding';

// ============================================================================
// Store Interface
// ============================================================================

interface OnboardingState {
  // Session data
  session: OnboardingSession | null;
  snapshot: CompanySnapshot | null;
  questions: QuestionResponse[];
  
  // UI state
  currentStep: OnboardingStep;
  isLoading: boolean;
  error: OnboardingError | null;
  
  // Polling state
  polling: PollingState;
  
  // Actions
  setSession: (session: OnboardingSession | null) => void;
  setSnapshot: (snapshot: CompanySnapshot | null) => void;
  setQuestions: (questions: QuestionResponse[]) => void;
  setCurrentStep: (step: OnboardingStep) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: OnboardingError | null) => void;
  setPolling: (polling: Partial<PollingState>) => void;
  
  // Complex actions
  nextStep: () => void;
  previousStep: () => void;
  reset: () => void;
  updateSessionState: (updates: Partial<OnboardingSession>) => void;
}

// ============================================================================
// Initial State
// ============================================================================

const initialState = {
  session: null,
  snapshot: null,
  questions: [],
  currentStep: 0 as OnboardingStep,
  isLoading: false,
  error: null,
  polling: {
    isPolling: false,
    attempts: 0,
  },
};

// ============================================================================
// Store
// ============================================================================

export const useOnboardingStore = create<OnboardingState>()(
  devtools(
    (set, get) => ({
      ...initialState,
      
      // Simple setters
      setSession: (session) => set({ session }),
      
      setSnapshot: (snapshot) => set({ snapshot }),
      
      setQuestions: (questions) => set({ questions }),
      
      setCurrentStep: (step) => set({ currentStep: step }),
      
      setLoading: (loading) => set({ isLoading: loading }),
      
      setError: (error) => set({ error }),
      
      setPolling: (polling) =>
        set((state) => ({
          polling: { ...state.polling, ...polling },
        })),
      
      // Complex actions
      nextStep: () =>
        set((state) => ({
          currentStep: Math.min(5, state.currentStep + 1) as OnboardingStep,
        })),
      
      previousStep: () =>
        set((state) => ({
          currentStep: Math.max(0, state.currentStep - 1) as OnboardingStep,
        })),
      
      reset: () => set(initialState),
      
      updateSessionState: (updates) =>
        set((state) => ({
          session: state.session
            ? { ...state.session, ...updates }
            : null,
        })),
    }),
    { name: 'OnboardingStore' }
  )
);

// ============================================================================
// Selectors
// ============================================================================

export const selectSession = (state: OnboardingState) => state.session;
export const selectSnapshot = (state: OnboardingState) => state.snapshot;
export const selectQuestions = (state: OnboardingState) => state.questions;
export const selectCurrentStep = (state: OnboardingState) => state.currentStep;
export const selectIsLoading = (state: OnboardingState) => state.isLoading;
export const selectError = (state: OnboardingState) => state.error;
export const selectPolling = (state: OnboardingState) => state.polling;

// Computed selectors
export const selectSessionId = (state: OnboardingState) => state.session?.session_id;
export const selectSessionState = (state: OnboardingState) => state.session?.state;
export const selectHasSnapshot = (state: OnboardingState) => !!state.snapshot;
export const selectHasQuestions = (state: OnboardingState) => state.questions.length > 0;

export default useOnboardingStore;

