/**
 * Packs Hook for Fylle Onboarding v3
 */

import { useApiQuery, useApiMutation, apiRequest } from '@/lib/api-client';
import { useToast } from '@/hooks/use-toast';
import type {
  Pack,
  StartBriefResponse,
  SubmitBriefAnswersResponse,
  BriefDocument,
} from '@shared/types/packs';

interface UsePacksOptions {
  userId?: string | null;
}

export function usePacks({ userId }: UsePacksOptions = {}) {
  const { toast } = useToast();

  // Fetch available packs
  const {
    data: packs,
    isLoading: packsLoading,
  } = useApiQuery<Pack[]>(
    ['packs'],
    '/api/v1/packs',
    {
      staleTime: 10 * 60 * 1000, // 10 minutes
    }
  );

  // Fetch user's briefs
  const {
    data: briefs,
    isLoading: briefsLoading,
    refetch: refetchBriefs,
  } = useApiQuery<BriefDocument[]>(
    ['briefs', userId || 'anonymous'],
    `/api/v1/briefs${userId ? `?user_id=${userId}` : ''}`,
    {
      enabled: !!userId,
    }
  );

  // Start brief generation
  const startBrief = useApiMutation(
    async (packId: string) => {
      return apiRequest<StartBriefResponse>('/api/v1/briefs/start', {
        method: 'POST',
        body: JSON.stringify({ pack_id: packId }),
      });
    },
    {
      onSuccess: (data) => {
        toast({
          title: 'Brief avviato',
          description: `Rispondi a ${data.questions.length} domande.`,
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

  // Submit brief answers
  const submitBriefAnswers = useApiMutation(
    async ({ briefSessionId, answers }: { briefSessionId: string; answers: Record<string, string> }) => {
      return apiRequest<SubmitBriefAnswersResponse>(`/api/v1/briefs/${briefSessionId}/answers`, {
        method: 'POST',
        body: JSON.stringify({ answers }),
      });
    },
    {
      onSuccess: () => {
        refetchBriefs();
        toast({
          title: 'Brief generato',
          description: 'Il tuo brief è pronto.',
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

  return {
    packs: packs || [],
    briefs: briefs || [],
    packsLoading,
    briefsLoading,
    startBrief,
    submitBriefAnswers,
    refetchBriefs,
  };
}
