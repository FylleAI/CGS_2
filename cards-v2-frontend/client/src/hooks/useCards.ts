import { useState, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useToast } from '@/hooks/use-toast';
import type { Card, CardsSnapshot, CardType } from '@shared/types/cards';

const MOCKS_BASE_PATH = '/mocks/cards';

export function useCards() {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [selectedCardId, setSelectedCardId] = useState<string | null>(null);

  const cardsQuery = useQuery<CardsSnapshot>({
    queryKey: ['cards', 'snapshot'],
    queryFn: async () => {
      const response = await fetch(`${MOCKS_BASE_PATH}/snapshot.json`);
      if (!response.ok) {
        throw new Error('Failed to fetch cards');
      }
      return response.json();
    },
    staleTime: 1000 * 60 * 5,
  });

  const getCardsByType = useCallback((type: CardType): Card[] => {
    if (!cardsQuery.data?.cards) return [];
    return cardsQuery.data.cards.filter(card => card.type === type);
  }, [cardsQuery.data]);

  const getCardById = useCallback((id: string): Card | undefined => {
    if (!cardsQuery.data?.cards) return undefined;
    return cardsQuery.data.cards.find(card => card.id === id);
  }, [cardsQuery.data]);

  const selectedCard = selectedCardId ? getCardById(selectedCardId) : null;

  const updateCard = useMutation({
    mutationFn: async (updatedCard: Card) => {
      await new Promise(resolve => setTimeout(resolve, 300));
      return updatedCard;
    },
    onMutate: async (updatedCard) => {
      await queryClient.cancelQueries({ queryKey: ['cards', 'snapshot'] });
      
      const previousData = queryClient.getQueryData<CardsSnapshot>(['cards', 'snapshot']);
      
      if (previousData) {
        queryClient.setQueryData<CardsSnapshot>(['cards', 'snapshot'], {
          ...previousData,
          cards: previousData.cards.map(card => 
            card.id === updatedCard.id 
              ? { ...updatedCard, updatedAt: new Date().toISOString() }
              : card
          ),
        });
      }
      
      return { previousData };
    },
    onSuccess: (data) => {
      toast({
        title: 'Card aggiornata',
        description: `"${data.title}" salvata con successo`,
      });
    },
    onError: (error, _, context) => {
      if (context?.previousData) {
        queryClient.setQueryData(['cards', 'snapshot'], context.previousData);
      }
      toast({
        title: 'Errore',
        description: 'Impossibile salvare le modifiche',
        variant: 'destructive',
      });
    },
  });

  const deleteCard = useMutation({
    mutationFn: async (cardId: string) => {
      await new Promise(resolve => setTimeout(resolve, 300));
      return cardId;
    },
    onMutate: async (cardId) => {
      await queryClient.cancelQueries({ queryKey: ['cards', 'snapshot'] });
      
      const previousData = queryClient.getQueryData<CardsSnapshot>(['cards', 'snapshot']);
      
      if (previousData) {
        queryClient.setQueryData<CardsSnapshot>(['cards', 'snapshot'], {
          ...previousData,
          cards: previousData.cards.filter(card => card.id !== cardId),
        });
      }
      
      if (selectedCardId === cardId) {
        setSelectedCardId(null);
      }
      
      return { previousData };
    },
    onSuccess: () => {
      toast({
        title: 'Card eliminata',
        description: 'La card è stata rimossa',
      });
    },
    onError: (error, _, context) => {
      if (context?.previousData) {
        queryClient.setQueryData(['cards', 'snapshot'], context.previousData);
      }
      toast({
        title: 'Errore',
        description: 'Impossibile eliminare la card',
        variant: 'destructive',
      });
    },
  });

  return {
    cards: cardsQuery.data?.cards || [],
    isLoading: cardsQuery.isLoading,
    isError: cardsQuery.isError,
    error: cardsQuery.error,
    sessionId: cardsQuery.data?.sessionId,
    generatedAt: cardsQuery.data?.generatedAt,
    
    getCardsByType,
    getCardById,
    
    selectedCardId,
    selectedCard,
    setSelectedCardId,
    
    updateCard,
    deleteCard,
    
    refetch: cardsQuery.refetch,
  };
}

export type UseCardsReturn = ReturnType<typeof useCards>;
