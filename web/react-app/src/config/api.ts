// API Configuration
if (!process.env.REACT_APP_API_URL) {
  throw new Error('REACT_APP_API_URL is not defined');
}
export const API_BASE_URL = process.env.REACT_APP_API_URL as string;

export const API_ENDPOINTS = {
  BASE: API_BASE_URL,
  HEALTH: `${API_BASE_URL}/health`,
  SYSTEM_INFO: `${API_BASE_URL}/api/v1/system/info`,
  PROVIDERS: `${API_BASE_URL}/api/v1/content/providers`,
  GENERATE: `${API_BASE_URL}/api/v1/content/generate`,
  KNOWLEDGE_BASE: `${API_BASE_URL}/api/v1/knowledge-base`,
  LOGS: `${API_BASE_URL}/api/v1/logs`
};