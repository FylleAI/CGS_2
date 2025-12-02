import { useState, useEffect, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiRequest, useApiMutation, invalidateQueries } from '@/lib/api-client';
import { useToast } from '@/hooks/use-toast';
import type {
  StartOnboardingRequest,
  StartOnboardingResponse,
  SubmitAnswersResponse,
  SessionStatusResponse,
  SessionDetailResponse,
  HealthCheckResponse,
} from '@shared/types/onboarding';
import { SessionState } from '@shared/types/onboarding';

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

  const startOnboarding = useApiMutation(
    async (data: StartOnboardingRequest) => {
      return apiRequest<StartOnboardingResponse>('/api/v1/onboarding/start', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },
    {
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
    }
  );

  const submitAnswers = useApiMutation(
    async ({ 
      sessionId, 
      answers 
    }: { 
      sessionId: string; 
      answers: Record<string, any> 
    }) => {
      return apiRequest<SubmitAnswersResponse>(
        `/api/v1/onboarding/${sessionId}/answers`,
        {
          method: 'POST',
          body: JSON.stringify({ answers }),
        }
      );
    },
    {
      onSuccess: (data, variables) => {
        invalidateQueries([`/api/v1/onboarding/${variables.sessionId}`]);
        invalidateQueries([`/api/v1/onboarding/${variables.sessionId}/status`]);
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
    }
  );

  const useSessionStatus = (sessionIdParam: string | null, options?: { enabled?: boolean }) => {
    return useQuery<SessionStatusResponse>({
      queryKey: ['/api/v1/onboarding', sessionIdParam, 'status'],
      queryFn: async () => {
        if (!sessionIdParam) throw new Error('No session ID');
        return apiRequest<SessionStatusResponse>(`/api/v1/onboarding/${sessionIdParam}/status`);
      },
      enabled: !!sessionIdParam && (options?.enabled !== false),
      refetchInterval: (query) => {
        const state = query.state.data?.state as SessionState | undefined;
        return getPollingInterval(state);
      },
      staleTime: 1000,
    });
  };

  const useSessionDetails = (sessionIdParam: string | null, options?: { enabled?: boolean }) => {
    return useQuery<SessionDetailResponse>({
      queryKey: ['/api/v1/onboarding', sessionIdParam, 'details'],
      queryFn: async () => {
        if (!sessionIdParam) throw new Error('No session ID');
        return apiRequest<SessionDetailResponse>(`/api/v1/onboarding/${sessionIdParam}`);
      },
      enabled: !!sessionIdParam && (options?.enabled !== false),
    });
  };

  const useHealthCheck = () => {
    return useQuery<HealthCheckResponse>({
      queryKey: ['/api/v1/onboarding/health'],
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
