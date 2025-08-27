// API Configuration
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  BASE: API_BASE_URL,
  HEALTH: `${API_BASE_URL}/health`,
  SYSTEM_INFO: `${API_BASE_URL}/api/v1/system/info`,
  PROVIDERS: `${API_BASE_URL}/api/v1/content/providers`,
  GENERATE: `${API_BASE_URL}/api/v1/content/generate`,
  KNOWLEDGE_BASE: `${API_BASE_URL}/api/v1/knowledge-base`,
  LOGS: `${API_BASE_URL}/api/v1/logs`
};