import axios from 'axios';
import { API_BASE_URL } from '../config/api';
import {
  ClientProfile,
  WorkflowType,
  RAGContent,
  GenerationRequest,
  GenerationResponse,
  GeneratedImage,
  SystemInfo,
  ProvidersResponse
} from '../types';
import { frontendLogger, EventType } from './logger';

// Configure axios instance
const api = axios.create({
  baseURL: API_BASE_URL, // Use direct API URL
  timeout: 600000, // Increased to 10 minutes for complex workflows (Siebert, multi-agent)
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for enhanced logging
api.interceptors.request.use(
  (config) => {
    const requestId = frontendLogger.logApiRequest(
      config.method?.toUpperCase() || 'UNKNOWN',
      config.url || '',
      {
        headers: config.headers,
        data: config.data ? JSON.stringify(config.data).substring(0, 500) : undefined
      }
    );

    // Store request ID and start time for response logging
    (config as any).metadata = {
      requestId,
      startTime: Date.now()
    };

    return config;
  },
  (error) => {
    frontendLogger.error(EventType.API_ERROR, 'API Request setup failed', {
      error: error.message,
      stack: error.stack
    });
    return Promise.reject(error);
  }
);

// Response interceptor for enhanced logging and error handling
api.interceptors.response.use(
  (response) => {
    const metadata = (response.config as any).metadata;
    const duration = Date.now() - (metadata?.startTime || 0);

    frontendLogger.logApiResponse(
      metadata?.requestId || 'unknown',
      response.status,
      duration,
      {
        responseSize: JSON.stringify(response.data).length,
        contentType: response.headers['content-type']
      }
    );

    return response;
  },
  (error) => {
    const metadata = (error.config as any)?.metadata;
    const duration = Date.now() - (metadata?.startTime || 0);

    frontendLogger.logApiError(
      metadata?.requestId || 'unknown',
      error,
      duration
    );

    if (error.response?.status === 401) {
      frontendLogger.warn(EventType.USER_ACTION, 'Unauthorized access attempt', {
        url: error.config?.url,
        status: error.response.status
      });
    }

    return Promise.reject(error);
  }
);

export const apiService = {
  // System endpoints
  async getSystemInfo(): Promise<SystemInfo> {
    const response = await api.get<SystemInfo>('/api/v1/system/info');
    return response.data;
  },

  async getHealth(): Promise<any> {
    const response = await api.get('/health');
    return response.data;
  },

  // Provider endpoints
  async getAvailableProviders(): Promise<ProvidersResponse> {
    console.log('🔧 Fetching available LLM providers');
    try {
      const response = await api.get('/api/v1/content/providers');
      const data: any = response.data;

      // Keep models as objects { name, max_tokens } when provided by backend.
      // If backend returns strings for models (legacy), wrap into objects with a safe default max_tokens.
      const normalized: ProvidersResponse = {
        ...data,
        providers: (data?.providers ?? []).map((p: any) => ({
          ...p,
          models: Array.isArray(p?.models)
            ? p.models.map((m: any) =>
                typeof m === 'string'
                  ? { name: m, max_tokens: 4096 }
                  : { name: m?.name ?? String(m), max_tokens: m?.max_tokens ?? 4096 }
              )
            : [],
        })),
      };

      console.log('✅ Providers fetched successfully (normalized):', normalized);
      return normalized;
    } catch (error) {
      console.error('❌ CRITICAL: Error fetching providers - no fallback allowed:', error);
      throw new Error('Failed to fetch LLM providers - system cannot proceed without real provider data');
    }
  },

  // Client profiles endpoints
  async getClientProfiles(): Promise<ClientProfile[]> {
    // For now, return mock data - will be replaced with real API
    return [
      {
        id: 'siebert',
        name: 'siebert',
        displayName: 'Siebert Financial',
        description: 'Financial services company focused on empowering individual investors',
        brandVoice: 'Professional yet accessible, empowering, educational, trustworthy',
        targetAudience: 'Gen Z and young professionals interested in financial literacy',
        industry: 'Financial Services',
        ragEnabled: true,
        knowledgeBasePath: 'data/knowledge_base/siebert'
      },
      {
        id: 'default',
        name: 'default',
        displayName: 'Default Profile',
        description: 'General purpose content generation profile',
        brandVoice: 'Professional and informative',
        targetAudience: 'General audience',
        industry: 'General',
        ragEnabled: false
      }
    ];
  },

  // Workflow endpoints
  async getWorkflowTypes(): Promise<WorkflowType[]> {
    // Mock data for now - will be replaced with real API
    return [
      {
        id: 'enhanced_article',
        name: 'enhanced_article',
        displayName: 'Enhanced Article',
        description: 'Comprehensive article with research, analysis, and expert insights',
        category: 'article',
        requiredFields: [
          {
            id: 'topic',
            name: 'topic',
            label: 'Article Topic',
            type: 'text',
            required: true,
            placeholder: 'Enter the main topic for your article'
          },
          {
            id: 'target_word_count',
            name: 'target_word_count',
            label: 'Target Word Count',
            type: 'number',
            required: true,
            validation: { min: 500, max: 3000 }
          }
        ],
        optionalFields: [
          {
            id: 'tone',
            name: 'tone',
            label: 'Tone',
            type: 'select',
            required: false,
            options: [
              { value: 'professional', label: 'Professional' },
              { value: 'conversational', label: 'Conversational' },
              { value: 'academic', label: 'Academic' },
              { value: 'casual', label: 'Casual' }
            ]
          },
          {
            id: 'include_statistics',
            name: 'include_statistics',
            label: 'Include Statistics',
            type: 'boolean',
            required: false
          }
        ]
      },
      {
        id: 'enhanced_article_with_image',
        name: 'enhanced_article_with_image',
        displayName: 'Enhanced Article + Image',
        description: 'Enhanced article workflow with automated contextual image generation',
        category: 'article',
        requiredFields: [
          {
            id: 'topic',
            name: 'topic',
            label: 'Article Topic',
            type: 'text',
            required: true,
            placeholder: 'Enter the main topic for your article'
          },
          {
            id: 'target_word_count',
            name: 'target_word_count',
            label: 'Target Word Count',
            type: 'number',
            required: true,
            validation: { min: 500, max: 3000 }
          }
        ],
        optionalFields: [
          {
            id: 'tone',
            name: 'tone',
            label: 'Tone',
            type: 'select',
            required: false,
            options: [
              { value: 'professional', label: 'Professional' },
              { value: 'conversational', label: 'Conversational' },
              { value: 'academic', label: 'Academic' },
              { value: 'casual', label: 'Casual' }
            ]
          },
          {
            id: 'image_style',
            name: 'image_style',
            label: 'Image Style',
            type: 'select',
            required: false,
            options: [
              { value: 'professional', label: 'Professional' },
              { value: 'creative', label: 'Creative' },
              { value: 'minimalist', label: 'Minimalist' },
              { value: 'abstract', label: 'Abstract' },
              { value: 'realistic', label: 'Realistic' }
            ]
          },
          {
            id: 'image_provider',
            name: 'image_provider',
            label: 'Image Provider',
            type: 'select',
            required: false,
            options: [
              { value: 'openai', label: 'OpenAI DALL·E' },
              { value: 'gemini', label: 'Google Gemini (preview)' }
            ]
          }
        ]
      },
      {
        id: 'siebert_premium_newsletter',
        name: 'siebert_premium_newsletter',
        displayName: 'Siebert Premium Newsletter',
        description: 'Optimized Gen Z newsletter with Perplexity AI research and 8-section format',
        category: 'newsletter',
        requiredFields: [
          {
            id: 'topic',
            name: 'topic',
            label: 'Newsletter Topic',
            type: 'textarea',
            required: true,
            placeholder: 'Enter the main financial theme for this newsletter edition',
            validation: { min: 5, max: 200 }
          },
          {
            id: 'target_word_count',
            name: 'target_word_count',
            label: 'Target Word Count',
            type: 'number',
            required: true,
            placeholder: '1000',
            validation: { min: 800, max: 1200 }
          }
        ],
        optionalFields: [
          {
            id: 'target_audience',
            name: 'target_audience',
            label: 'Target Audience',
            type: 'select',
            required: false,
            options: [
              { value: 'Gen Z investors and young professionals', label: 'Gen Z Investors (Default)' },
              { value: 'Millennial professionals building wealth', label: 'Millennial Professionals' },
              { value: 'Mixed Gen Z and Millennial audience', label: 'Mixed Audience' }
            ]
          },
          {
            id: 'cultural_trends',
            name: 'cultural_trends',
            label: 'Cultural Trends',
            type: 'textarea',
            required: false,
            placeholder: 'TikTok trends, viral topics, current events, gaming references...'
          },
          {
            id: 'exclude_topics',
            name: 'exclude_topics',
            label: 'Topics to Exclude',
            type: 'text',
            required: false,
            placeholder: 'crypto day trading, get rich quick schemes, penny stocks'
          },
          {
            id: 'research_timeframe',
            name: 'research_timeframe',
            label: 'Research Timeframe',
            type: 'select',
            required: false,
            options: [
              { value: 'last 7 days', label: 'Last 7 days (Default)' },
              { value: 'yesterday', label: 'Yesterday' },
              { value: 'last month', label: 'Last month' }
            ]
          },
          {
            id: 'premium_sources',
            name: 'premium_sources',
            label: 'Premium Research Sources',
            type: 'textarea',
            required: false,
            placeholder: 'Custom premium sources (one per line). Leave empty to use Siebert defaults.'
          },
          {
            id: 'custom_instructions',
            name: 'custom_instructions',
            label: 'Custom Instructions',
            type: 'textarea',
            required: false,
            placeholder: 'Additional requirements or focus areas for this edition...'
          }
        ]
      },
      {
        id: 'premium_newsletter',
        name: 'premium_newsletter',
        displayName: 'Premium Newsletter',
        description: 'Advanced newsletter with premium source analysis and client-specific brand integration',
        category: 'newsletter',
        requiredFields: [
          {
            id: 'newsletter_topic',
            name: 'newsletter_topic',
            label: 'Newsletter Topic',
            type: 'textarea',
            required: true,
            placeholder: 'Enter the main theme for this newsletter edition',
            validation: { min: 5, max: 200 }
          },
          {
            id: 'premium_sources',
            name: 'premium_sources',
            label: 'Premium Sources URLs',
            type: 'text',
            required: true,
            placeholder: 'Enter premium source URLs (one per line, max 10)',
            validation: { min: 1, max: 10 }
          },
          {
            id: 'target_audience',
            name: 'target_audience',
            label: 'Target Audience',
            type: 'textarea',
            required: true,
            placeholder: 'Describe the specific target audience for this edition',
            validation: { min: 3, max: 500 }
          }
        ],
        optionalFields: [
          {
            id: 'target_word_count',
            name: 'target_word_count',
            label: 'Target Word Count',
            type: 'number',
            required: false,
            placeholder: '1200',
            validation: { min: 800, max: 2500 }
          },

          {
            id: 'exclude_topics',
            name: 'exclude_topics',
            label: 'Topics to Exclude',
            type: 'text',
            required: false,
            placeholder: 'Enter topics to exclude (comma-separated)'
          },
          {
            id: 'priority_sections',
            name: 'priority_sections',
            label: 'Priority Sections',
            type: 'text',
            required: false,
            placeholder: 'Enter priority sections (comma-separated)'
          },
          {
            id: 'custom_instructions',
            name: 'custom_instructions',
            label: 'Custom Instructions',
            type: 'textarea',
            required: false,
            placeholder: 'Any additional instructions for the newsletter generation'
          }
        ]
      }
    ];
  },

  // RAG content endpoints
  async getRAGContents(clientProfile: string): Promise<RAGContent[]> {
    try {
      console.log(`🔍 Fetching RAG contents for client: ${clientProfile}`);

      // Call real knowledge base API
      const response = await api.get(`/api/v1/knowledge-base/frontend/clients/${clientProfile}/documents`);

      console.log(`✅ Received ${response.data.length} documents from knowledge base`);

      // Transform backend format to frontend format
      const ragContents: RAGContent[] = response.data.map((doc: any) => ({
        id: doc.id,
        title: doc.title,
        content: doc.description, // Use description as preview content
        type: doc.category,
        clientProfile: clientProfile,
        tags: doc.tags,
        createdAt: doc.date + 'T00:00:00Z', // Convert date to ISO format
        score: 1.0 // Default score
      }));

      return ragContents;

    } catch (error) {
      console.error(`❌ CRITICAL: Error fetching RAG contents for ${clientProfile} - no fallback allowed:`, error);
      throw new Error(`Failed to fetch RAG contents for ${clientProfile} - system cannot proceed without real knowledge base data`);
    }
  },

  // Get specific RAG document content
  async getRAGDocumentContent(clientProfile: string, documentId: string): Promise<string> {
    try {
      console.log(`📄 Fetching document content: ${clientProfile}/${documentId}`);

      const response = await api.get(`/api/v1/knowledge-base/clients/${clientProfile}/documents/${documentId}`);

      console.log(`✅ Retrieved document content (${response.data.content.length} chars)`);

      return response.data.content;

    } catch (error) {
      console.error(`❌ Error fetching document content ${clientProfile}/${documentId}:`, error);
      throw error;
    }
  },


  // Upload a new RAG document for a client
  async uploadRAGDocument(
    clientProfile: string,
    params: { title: string; content: string; description?: string; tags?: string[] }
  ): Promise<any> {
    try {
      frontendLogger.info(EventType.USER_ACTION, 'Uploading RAG document', {
        clientProfile,
        title: params.title,
      });
      const response = await api.post(
        `/api/v1/knowledge-base/clients/${clientProfile}/documents`,
        params
      );
      frontendLogger.info(EventType.API_RESPONSE, 'RAG document uploaded', {
        clientProfile,
        title: params.title,
      });
      return response.data;
    } catch (error) {
      console.error('❌ Error uploading RAG document:', error);
      throw error;
    }
  },


  // Get available clients from knowledge base
  async getAvailableClients(): Promise<string[]> {
    try {
      console.log('📋 Fetching available clients from knowledge base');

      const response = await api.get('/api/v1/knowledge-base/clients');

      console.log(`✅ Found ${response.data.length} clients:`, response.data);

      return response.data;

    } catch (error) {
      console.error('❌ CRITICAL: Error fetching available clients - no fallback allowed:', error);
      throw new Error('Failed to fetch available clients - system cannot proceed without real client data');
    }
  },

  // Content generation endpoint
  async generateContent(request: GenerationRequest): Promise<GenerationResponse> {
    // Start workflow tracking
    const workflowId = frontendLogger.logWorkflowStart(request.workflowType, {
      clientProfile: request.clientProfile,
      parameters: request.parameters,
      ragContentIds: request.ragContentIds
    });

    const payload = {
      topic: request.parameters.topic || request.parameters.newsletter_topic,
      content_type: request.workflowType === 'newsletter_premium' ? 'newsletter' : 'article',
      content_format: 'markdown',
      client_profile: request.clientProfile,
      workflow_type: request.workflowType,
      selected_documents: request.ragContentIds || [], // Pass selected RAG content IDs
      // Provider selection
      provider: request.parameters.provider || 'openai',
      model: request.parameters.model || 'gpt-4o',
      temperature: request.parameters.temperature || 0.7,
      workflow_id: workflowId, // Include workflow ID for backend tracking
      ...request.parameters
    };

    frontendLogger.info(EventType.WORKFLOW_START, 'Content generation started', {
      workflowId,
      workflowType: request.workflowType,
      payload: { ...payload, selected_documents: payload.selected_documents.length }
    });

    try {
      const response = await api.post<any>('/api/v1/content/generate', payload, {
        timeout: 600000 // 10 minutes for complex workflows (Siebert multi-agent, Perplexity research)
      });

      // Extract workflow metrics from backend response
      const backendMetrics = response.data.workflow_metrics;
      const rawImage: any =
        response.data.generated_image ||
        response.data.generatedImage ||
        response.data.metadata?.generated_image;
      const imageMetadata: Record<string, any> | undefined =
        response.data.image_metadata ||
        response.data.imageMetadata ||
        response.data.metadata?.image_metadata;

      const normalisedImage: GeneratedImage | undefined = rawImage
        ? {
            ...rawImage,
            imageUrl: rawImage.image_url ?? rawImage.imageUrl ?? null,
            imageData: rawImage.image_data ?? rawImage.imageData ?? null,
            provider: rawImage.provider ?? imageMetadata?.provider,
            style: rawImage.style,
            size: rawImage.size,
            quality: rawImage.quality,
          }
        : undefined;

      // Transform backend response to frontend format
      const result: GenerationResponse = {
        contentId: response.data.content_id || response.data.contentId || 'unknown',
        title: response.data.title || 'Generated Content',
        body: response.data.content || response.data.body || '',
        contentType: response.data.content_type || response.data.contentType || 'article',
        wordCount: response.data.word_count || response.data.wordCount || 0,
        generationTime: response.data.generation_time_seconds || response.data.generationTime || 0,
        success: true,
        workflowMetrics: backendMetrics, // Include backend metrics in response
        generatedImage: normalisedImage,
        imageMetadata: imageMetadata || normalisedImage?.metadata || undefined,
      };

      // Log workflow completion
      frontendLogger.logWorkflowComplete(workflowId, result, backendMetrics);

      return result;

    } catch (error) {
      // Log workflow error
      frontendLogger.logWorkflowError(workflowId, error);
      throw error;
    }
  }
};

export default apiService;
