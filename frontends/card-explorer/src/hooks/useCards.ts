/**
 * Hook to fetch all cards
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { cardApi } from '../services/cardApi';
import type { BaseCard, CreateCardRequest, UpdateCardRequest } from '../types/card';

const CARDS_QUERY_KEY = ['cards'];

export function useCards() {
  return useQuery({
    queryKey: CARDS_QUERY_KEY,
    queryFn: () => cardApi.listCards(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useCreateCard() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: CreateCardRequest) => cardApi.createCard(request),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: CARDS_QUERY_KEY });
    },
  });
}

export function useUpdateCard() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ cardId, request }: { cardId: string; request: UpdateCardRequest }) =>
      cardApi.updateCard(cardId, request),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: CARDS_QUERY_KEY });
    },
  });
}

export function useDeleteCard() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (cardId: string) => cardApi.deleteCard(cardId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: CARDS_QUERY_KEY });
    },
  });
}

export function useCardsByType(cardType: string) {
  const { data: cards, ...rest } = useCards();

  return {
    data: cards?.filter((card) => card.card_type === cardType) || [],
    ...rest,
  };
}

