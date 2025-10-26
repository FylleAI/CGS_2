/**
 * Hook to manage card relationships
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { cardApi } from '../services/cardApi';
import type { CreateRelationshipRequest } from '../types/card';

export function useCardRelationships(cardId: string | undefined) {
  return useQuery({
    queryKey: ['relationships', cardId],
    queryFn: () => {
      if (!cardId) throw new Error('Card ID is required');
      return cardApi.getRelationships(cardId);
    },
    enabled: !!cardId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useCreateRelationship() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: CreateRelationshipRequest) =>
      cardApi.createRelationship(request),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['relationships'] });
    },
  });
}

export function useDeleteRelationship() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (relationshipId: string) =>
      cardApi.deleteRelationship(relationshipId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['relationships'] });
    },
  });
}

export function useContextAll() {
  return useQuery({
    queryKey: ['context-all'],
    queryFn: () => cardApi.getContextAll(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useRagContextText() {
  return useQuery({
    queryKey: ['rag-context'],
    queryFn: () => cardApi.getRagContextText(),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

