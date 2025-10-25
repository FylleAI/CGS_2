/**
 * useCardList Hook
 * Custom hook for managing card list state and operations
 */

import { useCallback, useState } from 'react';
import { cardApi } from '../services/cardApi';
import { CardResponse, CardType } from '../types/card';

interface UseCardListState {
  cards: CardResponse[];
  isLoading: boolean;
  error: string | null;
  filter?: CardType;
}

interface UseCardListActions {
  listCards: (tenantId: string, cardType?: CardType) => Promise<CardResponse[]>;
  setFilter: (cardType?: CardType) => void;
  clearError: () => void;
  reset: () => void;
}

export function useCardList(): UseCardListState & UseCardListActions {
  const [state, setState] = useState<UseCardListState>({
    cards: [],
    isLoading: false,
    error: null,
    filter: undefined,
  });

  const listCards = useCallback(
    async (tenantId: string, cardType?: CardType): Promise<CardResponse[]> => {
      setState((prev) => ({ ...prev, isLoading: true, error: null, filter: cardType }));
      try {
        const cards = await cardApi.listCards(tenantId, cardType);
        setState((prev) => ({ ...prev, cards, isLoading: false }));
        return cards;
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        setState((prev) => ({ ...prev, isLoading: false, error: errorMessage }));
        throw error;
      }
    },
    []
  );

  const setFilter = useCallback((cardType?: CardType) => {
    setState((prev) => ({ ...prev, filter: cardType }));
  }, []);

  const clearError = useCallback(() => {
    setState((prev) => ({ ...prev, error: null }));
  }, []);

  const reset = useCallback(() => {
    setState({
      cards: [],
      isLoading: false,
      error: null,
      filter: undefined,
    });
  }, []);

  return {
    ...state,
    listCards,
    setFilter,
    clearError,
    reset,
  };
}

