// Base Types for CGSRef Frontend

export interface ClientProfile {
  id: string;
  name: string;
  displayName: string;
  description: string;
  brandVoice: string;
  targetAudience: string;
  industry: string;
  ragEnabled: boolean;
  knowledgeBasePath?: string;
}

export interface WorkflowType {
  id: string;
  name: string;
  displayName: string;
  description: string;
  category: 'article' | 'newsletter' | 'social' | 'custom';
  requiredFields: WorkflowField[];
  optionalFields: WorkflowField[];
}

export interface WorkflowField {
  id: string;
  name: string;
  label: string;
  type: 'text' | 'textarea' | 'select' | 'number' | 'boolean' | 'multiselect' | 'rag-content';
  required: boolean;
  placeholder?: string;
  options?: { value: string; label: string }[];
  validation?: {
    min?: number;
    max?: number;
    pattern?: string;
  };
}

export interface RAGContent {
  id: string;
  title: string;
  content: string;
  type: string;
  clientProfile: string;
  tags: string[];
  createdAt: string;
  score?: number;
}

export interface GenerationRequest {
  clientProfile: string;
  workflowType: string;
  parameters: Record<string, any>;
  ragContentIds?: string[];
}

export interface ProviderInfo {
  name: string;
  available: boolean;
  models: string[];
  default_model: string;
}

export interface ProvidersResponse {
  providers: ProviderInfo[];
  default_provider: string;
}

export interface GenerationResponse {
  contentId: string;
  title: string;
  body: string;
  contentType: string;
  wordCount: number;
  generationTime: number;
  success: boolean;
  errorMessage?: string;
}

export interface AppState {
  selectedClient: ClientProfile | null;
  selectedWorkflow: WorkflowType | null;
  availableClients: ClientProfile[];
  availableWorkflows: WorkflowType[];
  ragContents: RAGContent[];
  isLoading: boolean;
  error: string | null;
}

// API Response Types
export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
}

export interface SystemInfo {
  appName: string;
  version: string;
  environment: string;
  providers: Record<string, boolean>;
}
