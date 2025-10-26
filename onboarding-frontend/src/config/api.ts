/**
 * API Configuration
 * Centralized API endpoints and configuration
 */

// Validate environment variables
const ONBOARDING_API_URL = import.meta.env.VITE_ONBOARDING_API_URL;
const CGS_API_URL = import.meta.env.VITE_CGS_API_URL;

if (!ONBOARDING_API_URL) {
  throw new Error('VITE_ONBOARDING_API_URL is not defined in environment variables');
}

export const API_CONFIG = {
  ONBOARDING_BASE_URL: ONBOARDING_API_URL,
  CGS_BASE_URL: CGS_API_URL || 'http://localhost:8000',
  TIMEOUT: 120000, // 2 minutes
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000, // 1 second
} as const;

export const API_ENDPOINTS = {
  // Onboarding endpoints (updated for new API v1)
  ONBOARDING: {
    START: '/api/v1/onboarding/sessions',
    SUBMIT_ANSWERS: (sessionId: string) => `/api/v1/onboarding/sessions/${sessionId}/answers`,
    GET_STATUS: (sessionId: string) => `/api/v1/onboarding/sessions/${sessionId}/status`,
    GET_DETAILS: (sessionId: string) => `/api/v1/onboarding/sessions/${sessionId}`,
  },

  // Health checks
  HEALTH: {
    ONBOARDING: '/health',
    CGS: '/health',
  },
} as const;

export default API_CONFIG;

