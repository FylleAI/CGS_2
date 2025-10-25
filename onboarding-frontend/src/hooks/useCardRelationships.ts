/**
 * useCardRelationships Hook
 * Custom hook for managing card relationships
 */

import { useCallback, useState } from 'react';
import { cardApi } from '../services/cardApi';
import { CardRelationship, CreateRelationshipRequest } from '../types/card';

interface UseCardRelationshipsState {
  relationships: CardRelationship[];
  isLoading: boolean;
  error: string | null;
}

interface UseCardRelationshipsActions {
  getRelationships: (cardId: string, tenantId: string) => Promise<CardRelationship[]>;
  createRelationship: (
    sourceCardId: string,
    tenantId: string,
    request: CreateRelationshipRequest
  ) => Promise<CardRelationship>;
  deleteRelationship: (
    sourceCardId: string,
    targetCardId: string,
    tenantId: string
  ) => Promise<void>;
  clearError: () => void;
  reset: () => void;
}

export function useCardRelationships(): UseCardRelationshipsState & UseCardRelationshipsActions {
  const [state, setState] = useState<UseCardRelationshipsState>({
    relationships: [],
    isLoading: false,
    error: null,
  });

  const getRelationships = useCallback(
    async (cardId: string, tenantId: string): Promise<CardRelationship[]> => {
      setState((prev) => ({ ...prev, isLoading: true, error: null }));
      try {
        const relationships = await cardApi.getRelationships(cardId, tenantId);
        setState((prev) => ({ ...prev, relationships, isLoading: false }));
        return relationships;
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        setState((prev) => ({ ...prev, isLoading: false, error: errorMessage }));
        throw error;
      }
    },
    []
  );

  const createRelationship = useCallback(
    async (
      sourceCardId: string,
      tenantId: string,
      request: CreateRelationshipRequest
    ): Promise<CardRelationship> => {
      setState((prev) => ({ ...prev, isLoading: true, error: null }));
      try {
        const relationship = await cardApi.createRelationship(sourceCardId, tenantId, request);
        setState((prev) => ({
          ...prev,
          relationships: [...prev.relationships, relationship],
          isLoading: false,
        }));
        return relationship;
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        setState((prev) => ({ ...prev, isLoading: false, error: errorMessage }));
        throw error;
      }
    },
    []
  );

  const deleteRelationship = useCallback(
    async (sourceCardId: string, targetCardId: string, tenantId: string): Promise<void> => {
      setState((prev) => ({ ...prev, isLoading: true, error: null }));
      try {
        await cardApi.deleteRelationship(sourceCardId, targetCardId, tenantId);
        setState((prev) => ({
          ...prev,
          relationships: prev.relationships.filter(
            (rel) => !(rel.source_card_id === sourceCardId && rel.target_card_id === targetCardId)
          ),
          isLoading: false,
        }));
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
      relationships: [],
      isLoading: false,
      error: null,
    });
  }, []);

  return {
    ...state,
    getRelationships,
    createRelationship,
    deleteRelationship,
    clearError,
    reset,
  };
}

