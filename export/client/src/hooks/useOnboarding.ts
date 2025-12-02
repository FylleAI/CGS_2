import { useState, useEffect, useCallback } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useToast } from '@/hooks/use-toast';
import { queryClient } from '@/lib/queryClient';
import type {
  StartOnboardingRequest,
  StartOnboardingResponse,
  SubmitAnswersResponse,
  SessionStatusResponse,
  SessionDetailResponse,
  HealthCheckResponse,
} from '@shared/types/onboarding';
import { SessionState } from '@shared/types/onboarding';

// ============================================
// CONFIGURATION
// ============================================
// Set to false to use real backend API
const USE_MOCKS = false;

// API Base URL - configure based on environment
const API_BASE_URL = import.meta.env.VITE_ONBOARDING_API_URL || 'http://localhost:8001';

// Mock configuration (for development without backend)
const MOCKS_BASE_PATH = '/mocks/onboarding';
const MOCK_DELAY = 800;

// Helper to simulate API delay
const mockDelay = (ms: number = MOCK_DELAY) => new Promise(resolve => setTimeout(resolve, ms));

// Helper to fetch mock JSON
async function fetchMock<T>(path: string): Promise<T> {
  await mockDelay();
  const response = await fetch(`${MOCKS_BASE_PATH}/${path}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch mock: ${path}`);
  }
  return response.json();
}
// ============================================

const ASYNC_STATES = [
  SessionState.RESEARCHING,
  SessionState.SYNTHESIZING,
  SessionState.EXECUTING,
  SessionState.DELIVERING,
];

const FINAL_STATES = [
  SessionState.AWAITING_USER,
  SessionState.DONE,
  SessionState.FAILED,
];

const RESEARCH_STATES = [SessionState.RESEARCHING, SessionState.SYNTHESIZING];
const EXECUTE_STATES = [SessionState.EXECUTING, SessionState.DELIVERING];

function getPollingInterval(state?: SessionState): number | false {
  if (!state) return false;
  if (FINAL_STATES.includes(state)) return false;
  if (RESEARCH_STATES.includes(state)) return 3000;
  if (EXECUTE_STATES.includes(state)) return 5000;
  return false;
}

export function useOnboarding() {
  const { toast } = useToast();
  const [sessionId, setSessionId] = useState<string | null>(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('onboarding_session_id');
    }
    return null;
  });

  useEffect(() => {
    if (sessionId) {
      localStorage.setItem('onboarding_session_id', sessionId);
    } else {
      localStorage.removeItem('onboarding_session_id');
    }
  }, [sessionId]);

  const clearSession = useCallback(() => {
    setSessionId(null);
    localStorage.removeItem('onboarding_session_id');
  }, []);

  // ============================================
  // START ONBOARDING MUTATION
  // ============================================
  const startOnboarding = useMutation({
    mutationFn: async (_data: StartOnboardingRequest): Promise<StartOnboardingResponse> => {
      if (USE_MOCKS) {
        return fetchMock<StartOnboardingResponse>('start.json');
      }
      // Real API call
      const response = await fetch(`${API_BASE_URL}/api/v1/onboarding/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(_data),
      });
      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || 'Failed to start onboarding');
      }
      return response.json();
    },
    onSuccess: (data) => {
      setSessionId(data.session_id);
      toast({
        title: 'Onboarding avviato',
        description: `Ricerca completata per ${data.snapshot_summary?.company_name || 'la tua azienda'}. Rispondi alle domande.`,
      });
    },
    onError: (error) => {
      toast({
        title: 'Errore avvio onboarding',
        description: error instanceof Error ? error.message : 'Impossibile avviare la sessione',
        variant: 'destructive',
      });
    },
  });

  // ============================================
  // SUBMIT ANSWERS MUTATION
  // ============================================
  const submitAnswers = useMutation({
    mutationFn: async ({
      sessionId: _sessionId,
      answers: _answers
    }: {
      sessionId: string;
      answers: Record<string, any>
    }): Promise<SubmitAnswersResponse> => {
      if (USE_MOCKS) {
        return fetchMock<SubmitAnswersResponse>('submit.json');
      }
      // Real API call
      const response = await fetch(`${API_BASE_URL}/api/v1/onboarding/${_sessionId}/answers`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ answers: _answers }),
      });
      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || 'Failed to submit answers');
      }
      return response.json();
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['/api/v1/onboarding', variables.sessionId] });
      queryClient.invalidateQueries({ queryKey: ['/api/v1/onboarding', variables.sessionId, 'status'] });

      // Save cards_output to query cache for useCards to consume
      if (data.cards_output) {
        console.log('💾 Saving cards to cache:', data.cards_output);
        console.log(`   Cards count: ${data.cards_output.cards?.length || 0}`);
        queryClient.setQueryData(['cards', 'snapshot'], data.cards_output);
        // Also save session_id for reference
        localStorage.setItem('cards_session_id', variables.sessionId);
      } else {
        console.warn('⚠️ No cards_output in response:', data);
      }

      toast({
        title: 'Risposte inviate',
        description: data.message || `${data.cards_created || 0} cards create con successo!`,
      });
    },
    onError: (error) => {
      toast({
        title: 'Errore invio risposte',
        description: error instanceof Error ? error.message : 'Impossibile inviare le risposte',
        variant: 'destructive',
      });
    },
  });

  // ============================================
  // SESSION STATUS QUERY (with polling)
  // ============================================
  const useSessionStatus = (sessionIdParam: string | null, options?: { enabled?: boolean }) => {
    return useQuery<SessionStatusResponse>({
      queryKey: ['/api/v1/onboarding', sessionIdParam, 'status'],
      queryFn: async () => {
        if (!sessionIdParam) throw new Error('No session ID');
        if (USE_MOCKS) {
          return fetchMock<SessionStatusResponse>('status.json');
        }
        const response = await fetch(`${API_BASE_URL}/api/v1/onboarding/${sessionIdParam}/status`);
        if (!response.ok) throw new Error('Failed to fetch status');
        return response.json();
      },
      enabled: !!sessionIdParam && (options?.enabled !== false),
      refetchInterval: (query) => {
        const state = query.state.data?.state as SessionState | undefined;
        return getPollingInterval(state);
      },
      staleTime: 1000,
    });
  };

  // ============================================
  // SESSION DETAILS QUERY
  // ============================================
  const useSessionDetails = (sessionIdParam: string | null, options?: { enabled?: boolean }) => {
    return useQuery<SessionDetailResponse>({
      queryKey: ['/api/v1/onboarding', sessionIdParam, 'details'],
      queryFn: async () => {
        if (!sessionIdParam) throw new Error('No session ID');
        if (USE_MOCKS) {
          return fetchMock<SessionDetailResponse>('details.json');
        }
        const response = await fetch(`${API_BASE_URL}/api/v1/onboarding/${sessionIdParam}`);
        if (!response.ok) throw new Error('Failed to fetch details');
        return response.json();
      },
      enabled: !!sessionIdParam && (options?.enabled !== false),
    });
  };

  // ============================================
  // HEALTH CHECK QUERY
  // ============================================
  const useHealthCheck = () => {
    return useQuery<HealthCheckResponse>({
      queryKey: ['/api/v1/onboarding/health'],
      queryFn: async () => {
        if (USE_MOCKS) {
          return fetchMock<HealthCheckResponse>('health.json');
        }
        const response = await fetch(`${API_BASE_URL}/api/v1/onboarding/health`);
        if (!response.ok) throw new Error('Health check failed');
        return response.json();
      },
      staleTime: 60000,
    });
  };

  return {
    sessionId,
    setSessionId,
    clearSession,
    startOnboarding,
    submitAnswers,
    useSessionStatus,
    useSessionDetails,
    useHealthCheck,
    isPollingState: (state?: SessionState) => state ? ASYNC_STATES.includes(state) : false,
    isFinalState: (state?: SessionState) => state ? FINAL_STATES.includes(state) : false,
  };
}
