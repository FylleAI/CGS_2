/**
 * Card Service API Client
 * HTTP client for Card Service endpoints
 */

import { CardResponse, CardType, CreateCardRequest, CreateRelationshipRequest, RelationshipResponse, UpdateCardRequest } from '../types/card';

const API_BASE_URL = import.meta.env.VITE_CGS_API_URL || 'http://localhost:8000';
const CARD_API_BASE = `${API_BASE_URL}/api/v1/cards`;

// ============================================================================
// Card CRUD Operations
// ============================================================================

export const cardApi = {
  /**
   * Create a new card
   */
  async createCard(tenantId: string, request: CreateCardRequest): Promise<CardResponse> {
    const response = await fetch(`${CARD_API_BASE}?tenant_id=${tenantId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create card');
    }

    return response.json();
  },

  /**
   * Get all cards for a tenant
   */
  async listCards(tenantId: string, cardType?: CardType): Promise<CardResponse[]> {
    const params = new URLSearchParams({ tenant_id: tenantId });
    if (cardType) {
      params.append('card_type', cardType);
    }

    const response = await fetch(`${CARD_API_BASE}?${params}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to list cards');
    }

    return response.json();
  },

  /**
   * Get a specific card by ID
   */
  async getCard(cardId: string, tenantId: string): Promise<CardResponse> {
    const response = await fetch(`${CARD_API_BASE}/${cardId}?tenant_id=${tenantId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get card');
    }

    return response.json();
  },

  /**
   * Update a card
   */
  async updateCard(
    cardId: string,
    tenantId: string,
    request: UpdateCardRequest
  ): Promise<CardResponse> {
    const response = await fetch(`${CARD_API_BASE}/${cardId}?tenant_id=${tenantId}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update card');
    }

    return response.json();
  },

  /**
   * Delete a card (soft delete)
   */
  async deleteCard(cardId: string, tenantId: string): Promise<void> {
    const response = await fetch(`${CARD_API_BASE}/${cardId}?tenant_id=${tenantId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete card');
    }
  },

  // ============================================================================
  // Relationship Operations
  // ============================================================================

  /**
   * Create a relationship between two cards
   */
  async createRelationship(
    sourceCardId: string,
    tenantId: string,
    request: CreateRelationshipRequest
  ): Promise<RelationshipResponse> {
    const response = await fetch(
      `${CARD_API_BASE}/${sourceCardId}/relationships?tenant_id=${tenantId}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create relationship');
    }

    return response.json();
  },

  /**
   * Get all relationships for a card
   */
  async getRelationships(cardId: string, tenantId: string): Promise<RelationshipResponse[]> {
    const response = await fetch(
      `${CARD_API_BASE}/${cardId}/relationships?tenant_id=${tenantId}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get relationships');
    }

    return response.json();
  },

  /**
   * Delete a relationship
   */
  async deleteRelationship(
    sourceCardId: string,
    targetCardId: string,
    tenantId: string
  ): Promise<void> {
    const response = await fetch(
      `${CARD_API_BASE}/${sourceCardId}/relationships/${targetCardId}?tenant_id=${tenantId}`,
      {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete relationship');
    }
  },

  // ============================================================================
  // Integration Operations
  // ============================================================================

  /**
   * Create cards from CompanySnapshot (Onboarding integration)
   */
  async createCardsFromSnapshot(tenantId: string, snapshot: any): Promise<CardResponse[]> {
    const response = await fetch(
      `${CARD_API_BASE}/onboarding/create-from-snapshot?tenant_id=${tenantId}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(snapshot),
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create cards from snapshot');
    }

    return response.json();
  },

  /**
   * Get all cards for context (CGS integration)
   */
  async getAllCardsForContext(tenantId: string): Promise<Record<string, CardResponse[]>> {
    const response = await fetch(`${CARD_API_BASE}/context/all?tenant_id=${tenantId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get cards for context');
    }

    return response.json();
  },

  /**
   * Get RAG context text (CGS integration)
   */
  async getRagContextText(tenantId: string): Promise<string> {
    const response = await fetch(`${CARD_API_BASE}/context/rag-text?tenant_id=${tenantId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get RAG context');
    }

    const data = await response.json();
    return data.context;
  },

  /**
   * Get cards by type (CGS integration)
   */
  async getCardsByType(tenantId: string, cardTypes?: CardType[]): Promise<Record<string, CardResponse[]>> {
    const params = new URLSearchParams({ tenant_id: tenantId });
    if (cardTypes) {
      cardTypes.forEach((type) => params.append('card_types', type));
    }

    const response = await fetch(`${CARD_API_BASE}/context/by-type?${params}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get cards by type');
    }

    return response.json();
  },
};

