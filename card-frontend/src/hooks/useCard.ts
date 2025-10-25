/**
 * Hook to fetch single card
 */

import { useQuery } from '@tanstack/react-query';
import { cardApi } from '../services/cardApi';

export function useCard(cardId: string | undefined) {
  return useQuery({
    queryKey: ['card', cardId],
    queryFn: () => {
      if (!cardId) throw new Error('Card ID is required');
      return cardApi.getCard(cardId);
    },
    enabled: !!cardId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

