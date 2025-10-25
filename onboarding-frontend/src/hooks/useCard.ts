/**
 * useCard Hook
 * Custom hook for managing card state and operations
 */

import { useCallback, useState } from 'react';
import { cardApi } from '../services/cardApi';
import { AnyCard, CardResponse, CardType, CreateCardRequest, UpdateCardRequest } from '../types/card';

interface UseCardState {
  card: CardResponse | null;
  isLoading: boolean;
  error: string | null;
  isDirty: boolean;
}

interface UseCardActions {
  createCard: (tenantId: string, request: CreateCardRequest) => Promise<CardResponse>;
  getCard: (cardId: string, tenantId: string) => Promise<CardResponse>;
  updateCard: (cardId: string, tenantId: string, request: UpdateCardRequest) => Promise<CardResponse>;
  deleteCard: (cardId: string, tenantId: string) => Promise<void>;
  clearError: () => void;
  reset: () => void;
}

export function useCard(): UseCardState & UseCardActions {
  const [state, setState] = useState<UseCardState>({
    card: null,
    isLoading: false,
    error: null,
    isDirty: false,
  });

  const createCard = useCallback(
    async (tenantId: string, request: CreateCardRequest): Promise<CardResponse> => {
      setState((prev) => ({ ...prev, isLoading: true, error: null }));
      try {
        const card = await cardApi.createCard(tenantId, request);
        setState((prev) => ({ ...prev, card, isLoading: false, isDirty: false }));
        return card;
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        setState((prev) => ({ ...prev, isLoading: false, error: errorMessage }));
        throw error;
      }
    },
    []
  );

  const getCard = useCallback(
    async (cardId: string, tenantId: string): Promise<CardResponse> => {
      setState((prev) => ({ ...prev, isLoading: true, error: null }));
      try {
        const card = await cardApi.getCard(cardId, tenantId);
        setState((prev) => ({ ...prev, card, isLoading: false }));
        return card;
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        setState((prev) => ({ ...prev, isLoading: false, error: errorMessage }));
        throw error;
      }
    },
    []
  );

  const updateCard = useCallback(
    async (cardId: string, tenantId: string, request: UpdateCardRequest): Promise<CardResponse> => {
      setState((prev) => ({ ...prev, isLoading: true, error: null }));
      try {
        const card = await cardApi.updateCard(cardId, tenantId, request);
        setState((prev) => ({ ...prev, card, isLoading: false, isDirty: false }));
        return card;
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        setState((prev) => ({ ...prev, isLoading: false, error: errorMessage }));
        throw error;
      }
    },
    []
  );

  const deleteCard = useCallback(
    async (cardId: string, tenantId: string): Promise<void> => {
      setState((prev) => ({ ...prev, isLoading: true, error: null }));
      try {
        await cardApi.deleteCard(cardId, tenantId);
        setState((prev) => ({ ...prev, card: null, isLoading: false }));
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        setState((prev) => ({ ...prev, isLoading: false, error: errorMessage }));
        throw error;
      }
    },
    []
  );

  const clearError = useCallback(() => {
    setState((prev) => ({ ...prev, error: null }));
  }, []);

  const reset = useCallback(() => {
    setState({
      card: null,
      isLoading: false,
      error: null,
      isDirty: false,
    });
  }, []);

  return {
    ...state,
    createCard,
    getCard,
    updateCard,
    deleteCard,
    clearError,
    reset,
  };
}

