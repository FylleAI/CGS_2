/**
 * Onboarding API Service
 * API calls for onboarding flow
 */

import { onboardingApiClient, retryRequest } from './client';
import { API_ENDPOINTS } from '@/config/api';
import type {
  StartOnboardingRequest,
  StartOnboardingResponse,
  SubmitAnswersRequest,
  SubmitAnswersResponse,
  SessionStatusResponse,
  SessionDetailResponse,
} from '@/types/onboarding';

// ============================================================================
// Onboarding API
// ============================================================================

export const onboardingApi = {
  /**
   * Start onboarding process
   * POST /api/v1/onboarding/start
   */
  startOnboarding: async (data: StartOnboardingRequest): Promise<StartOnboardingResponse> => {
    const response = await retryRequest(() =>
      onboardingApiClient.post<StartOnboardingResponse>(
        API_ENDPOINTS.ONBOARDING.START,
        data
      )
    );
    return response.data;
  },

  /**
   * Submit answers to clarifying questions
   * POST /api/v1/onboarding/{session_id}/answers
   */
  submitAnswers: async (
    sessionId: string,
    data: SubmitAnswersRequest
  ): Promise<SubmitAnswersResponse> => {
    const response = await retryRequest(() =>
      onboardingApiClient.post<SubmitAnswersResponse>(
        API_ENDPOINTS.ONBOARDING.SUBMIT_ANSWERS(sessionId),
        data
      )
    );
    return response.data;
  },

  /**
   * Get session status
   * GET /api/v1/onboarding/{session_id}/status
   */
  getSessionStatus: async (sessionId: string): Promise<SessionStatusResponse> => {
    const response = await onboardingApiClient.get<SessionStatusResponse>(
      API_ENDPOINTS.ONBOARDING.GET_STATUS(sessionId)
    );
    return response.data;
  },

  /**
   * Get session details (includes full snapshot)
   * GET /api/v1/onboarding/{session_id}
   */
  getSessionDetails: async (sessionId: string): Promise<SessionDetailResponse> => {
    const response = await onboardingApiClient.get<SessionDetailResponse>(
      API_ENDPOINTS.ONBOARDING.GET_DETAILS(sessionId)
    );
    return response.data;
  },

  /**
   * Health check
   * GET /health
   */
  healthCheck: async (): Promise<{ status: string }> => {
    const response = await onboardingApiClient.get<{ status: string }>(
      API_ENDPOINTS.HEALTH.ONBOARDING
    );
    return response.data;
  },
};

export default onboardingApi;

