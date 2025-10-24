/**
 * API Client
 * Axios instance with interceptors for logging and error handling
 */

import axios, { AxiosError, AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { API_CONFIG } from '@/config/api';
import { FEATURE_FLAGS } from '@/config/constants';

// ============================================================================
// Axios Instance
// ============================================================================

export const createApiClient = (baseURL: string): AxiosInstance => {
  const client = axios.create({
    baseURL,
    timeout: API_CONFIG.TIMEOUT,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Request Interceptor
  client.interceptors.request.use(
    (config) => {
      const requestId = generateRequestId();
      
      // Add request ID to headers
      config.headers['X-Request-ID'] = requestId;
      
      // Log request in debug mode
      if (FEATURE_FLAGS.ENABLE_DEBUG_MODE) {
        console.log(`[API Request ${requestId}]`, {
          method: config.method?.toUpperCase(),
          url: config.url,
          data: config.data,
        });
      }
      
      // Store metadata for response logging
      (config as any).metadata = {
        requestId,
        startTime: Date.now(),
      };
      
      return config;
    },
    (error) => {
      console.error('[API Request Error]', error);
      return Promise.reject(error);
    }
  );

  // Response Interceptor
  client.interceptors.response.use(
    (response: AxiosResponse) => {
      const metadata = (response.config as any).metadata;
      const duration = Date.now() - (metadata?.startTime || 0);
      
      // Log response in debug mode
      if (FEATURE_FLAGS.ENABLE_DEBUG_MODE) {
        console.log(`[API Response ${metadata?.requestId}]`, {
          status: response.status,
          duration: `${duration}ms`,
          data: response.data,
        });
      }
      
      return response;
    },
    async (error: AxiosError) => {
      const metadata = (error.config as any)?.metadata;
      const duration = Date.now() - (metadata?.startTime || 0);
      
      // Log error
      console.error(`[API Error ${metadata?.requestId}]`, {
        status: error.response?.status,
        duration: `${duration}ms`,
        message: error.message,
        data: error.response?.data,
      });
      
      // Handle specific error cases
      if (error.response) {
        // Server responded with error status
        const errorData = error.response.data as any;
        
        throw {
          message: errorData?.detail || errorData?.message || 'An error occurred',
          code: error.response.status.toString(),
          details: errorData,
        };
      } else if (error.request) {
        // Request made but no response
        throw {
          message: 'No response from server. Please check your connection.',
          code: 'NETWORK_ERROR',
          details: error.message,
        };
      } else {
        // Error in request setup
        throw {
          message: error.message || 'An unexpected error occurred',
          code: 'REQUEST_ERROR',
          details: error,
        };
      }
    }
  );

  return client;
};

// ============================================================================
// API Clients
// ============================================================================

export const onboardingApiClient = createApiClient(API_CONFIG.ONBOARDING_BASE_URL);
export const cgsApiClient = createApiClient(API_CONFIG.CGS_BASE_URL);

// ============================================================================
// Retry Logic
// ============================================================================

export const retryRequest = async <T>(
  requestFn: () => Promise<T>,
  maxAttempts: number = API_CONFIG.RETRY_ATTEMPTS,
  delay: number = API_CONFIG.RETRY_DELAY
): Promise<T> => {
  let lastError: any;
  
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await requestFn();
    } catch (error) {
      lastError = error;
      
      if (attempt < maxAttempts) {
        // Wait before retrying (exponential backoff)
        const waitTime = delay * Math.pow(2, attempt - 1);
        await new Promise(resolve => setTimeout(resolve, waitTime));
        
        if (FEATURE_FLAGS.ENABLE_DEBUG_MODE) {
          console.log(`[Retry] Attempt ${attempt + 1}/${maxAttempts} after ${waitTime}ms`);
        }
      }
    }
  }
  
  throw lastError;
};

// ============================================================================
// Utilities
// ============================================================================

function generateRequestId(): string {
  return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

export default {
  onboardingApiClient,
  cgsApiClient,
  retryRequest,
};

