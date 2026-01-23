/**
 * Cards Hook for Fylle Onboarding v3
 */

import { useState, useMemo } from 'react';
import { useApiQuery, useApiMutation, apiRequest, invalidateQueries } from '@/lib/api-client';
import { useToast } from '@/hooks/use-toast';
import type { Card, CardType, CardsSnapshot } from '@shared/types/cards';

interface UseCardsOptions {
  userId?: string | null;
}

export function useCards({ userId }: UseCardsOptions = {}) {
  const { toast } = useToast();
  const [selectedCardId, setSelectedCardId] = useState<string | null>(null);

  const {
    data: cardsData,
    isLoading,
    isError,
    refetch,
  } = useApiQuery<CardsSnapshot>(
    ['cards', userId || 'anonymous'],
    `/api/v1/cards${userId ? `?user_id=${userId}` : ''}`,
    {
      enabled: !!userId,
    }
  );

  const cards = useMemo(() => cardsData?.cards || [], [cardsData]);

  const selectedCard = useMemo(
    () => cards.find((card) => card.id === selectedCardId) || null,
    [cards, selectedCardId]
  );

  const getCardsByType = (type: CardType): Card[] => {
    return cards.filter((card) => card.type === type);
  };

  const updateCard = useApiMutation(
    async (card: Card) => {
      return apiRequest<Card>(`/api/v1/cards/${card.id}`, {
        method: 'PUT',
        body: JSON.stringify(card),
      });
    },
    {
      onSuccess: () => {
        invalidateQueries(['cards', userId || 'anonymous']);
        toast({
          title: 'Card aggiornata',
          description: 'Le modifiche sono state salvate.',
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
    cards,
    isLoading,
    isError,
    refetch,
    selectedCardId,
    selectedCard,
    setSelectedCardId,
    getCardsByType,
    updateCard,
  };
}
