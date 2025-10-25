/**
 * API Configuration
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const CARD_API_URL = import.meta.env.VITE_CARD_API_URL || `${API_BASE_URL}/api/v1/cards`;

export const API_CONFIG = {
  BASE_URL: API_BASE_URL,
  CARD_API_URL: CARD_API_URL,
  TIMEOUT: 30000, // 30 seconds
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000, // 1 second
} as const;

export const CARD_ENDPOINTS = {
  // List cards
  LIST: `${CARD_API_URL}`,
  
  // Get single card
  GET: (id: string) => `${CARD_API_URL}/${id}`,
  
  // Create card
  CREATE: `${CARD_API_URL}`,
  
  // Update card
  UPDATE: (id: string) => `${CARD_API_URL}/${id}`,
  
  // Delete card
  DELETE: (id: string) => `${CARD_API_URL}/${id}`,
  
  // Relationships
  RELATIONSHIPS: `${CARD_API_URL}/relationships`,
  CREATE_RELATIONSHIP: `${CARD_API_URL}/relationships`,
  DELETE_RELATIONSHIP: (id: string) => `${CARD_API_URL}/relationships/${id}`,
  
  // Context
  CONTEXT_ALL: `${CARD_API_URL}/context/all`,
  CONTEXT_RAG: `${CARD_API_URL}/context/rag-text`,
} as const;

