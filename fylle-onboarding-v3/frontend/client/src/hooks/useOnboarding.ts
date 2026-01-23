/**
 * Onboarding Hook for Fylle Onboarding v3
 */

import { useState } from 'react';
import { useApiMutation, apiRequest } from '@/lib/api-client';
import { useToast } from '@/hooks/use-toast';
import type {
  StartOnboardingRequest,
  StartOnboardingResponse,
  SubmitAnswersRequest,
  SubmitAnswersResponse,
  SessionStatusResponse,
} from '@shared/types/onboarding';

export function useOnboarding() {
  const { toast } = useToast();
  const [userId, setUserId] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);

  const startOnboarding = useApiMutation(
    async (data: StartOnboardingRequest) => {
      const response = await apiRequest<StartOnboardingResponse>(
        '/api/v1/onboarding/start',
        {
          method: 'POST',
          body: JSON.stringify(data),
        }
      );
      setUserId(response.user_id);
      setSessionId(response.session_id);
      return response;
    },
    {
      onSuccess: (data) => {
        toast({
          title: 'Onboarding avviato',
          description: `${data.clarifying_questions.length} domande pronte.`,
        });
      },
      onError: (error) => {
        toast({
          title: 'Errore',
          description: error.message,
          variant: 'destructive',
        });
      },
    }
  );

  const submitAnswers = useApiMutation(
    async ({ sessionId, answers }: { sessionId: string; answers: Record<string, any> }) => {
      return apiRequest<SubmitAnswersResponse>(
        `/api/v1/onboarding/${sessionId}/answers`,
        {
          method: 'POST',
          body: JSON.stringify({ answers }),
        }
      );
    },
    {
      onSuccess: (data) => {
        toast({
          title: 'Cards generate',
          description: `${data.cards_created} cards create con successo.`,
        });
      },
      onError: (error) => {
        toast({
          title: 'Errore',
          description: error.message,
          variant: 'destructive',
        });
      },
    }
  );

  const getSessionStatus = async (sessionId: string): Promise<SessionStatusResponse> => {
    return apiRequest<SessionStatusResponse>(`/api/v1/onboarding/${sessionId}/status`);
  };

  const clearSession = () => {
    setUserId(null);
    setSessionId(null);
  };

  return {
    userId,
    sessionId,
    setUserId,
    setSessionId,
    startOnboarding,
    submitAnswers,
    getSessionStatus,
    clearSession,
  };
}
