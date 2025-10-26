import React, { useState, useEffect } from 'react';
import {
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Typography,
  Chip,
  Alert,
  CircularProgress,
  Grid,
  Paper,
  Tooltip,
  IconButton,
} from '@mui/material';
import {
  Psychology as PsychologyIcon,
  Refresh as RefreshIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { useQuery } from 'react-query';
import { Controller, Control } from 'react-hook-form';
import toast from 'react-hot-toast';

import apiService from '../services/api';
import { ProviderInfo, ModelInfo } from '../types';

interface ProviderSelectorProps {
  control: Control<any>;
  selectedProvider?: string;
  selectedModel?: string;
  selectedTokens?: number;
  onProviderChange?: (provider: string) => void;
  onModelChange?: (model: string) => void;
  onTokensChange?: (tokens: number) => void;
}

const ProviderSelector: React.FC<ProviderSelectorProps> = ({
  control,
  selectedProvider,
  selectedModel,
  selectedTokens,
  onProviderChange,
  onModelChange,
  onTokensChange,
}) => {
  const [currentProvider, setCurrentProvider] = useState<string>(selectedProvider || '');
  const [availableModels, setAvailableModels] = useState<ModelInfo[]>([]);
  const [selectedModelInfo, setSelectedModelInfo] = useState<ModelInfo | undefined>(undefined);


  // Generate discrete token options up to the model limit using canonical steps
  const getTokenOptions = (limit: number): number[] => {
    if (!limit || limit <= 0) return [];
    const candidates = [256, 512, 1024, 1536, 2048, 3072, 4096, 6144, 8192, 12000, 16000, 24000, 32000, 48000, 64000, 96000, 128000, 200000];
    const options = candidates.filter(v => v <= limit);
    if (!options.includes(limit)) options.push(limit);
    // Ensure ascending unique values
    return Array.from(new Set(options)).sort((a, b) => a - b);
  };

  // Fetch available providers
  const {
    data: providersData,
    isLoading: loadingProviders,
    error: providersError,
    refetch: refetchProviders,
  } = useQuery(
    'providers',
    apiService.getAvailableProviders,
    {
      onSuccess: (data) => {
        console.log('✅ Providers loaded:', data);
        // Set default provider if none selected
        if (!currentProvider && data.default_provider) {
          setCurrentProvider(data.default_provider);
          onProviderChange?.(data.default_provider);
        }
      },
      onError: (error: any) => {
        console.error('❌ Failed to load providers:', error);
        toast.error('Failed to load LLM providers');
      },
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
    }
  );

  // Update available models when provider changes
  useEffect(() => {
    if (providersData && currentProvider) {
      const provider = providersData.providers.find(p => p.name === currentProvider);
      if (provider) {
        setAvailableModels(provider.models);
        const info = provider.models.find(m => m.name === (selectedModel || provider.default_model));
        setSelectedModelInfo(info);
        // Auto-select default model if no model is selected
        if (!selectedModel && provider.default_model) {
          onModelChange?.(provider.default_model);
        }
        if (info) {
          onTokensChange?.(info.max_tokens);
        }
      }
    }
  }, [currentProvider, providersData, selectedModel, onModelChange, onTokensChange]);

  // Update selected model info when model changes
  useEffect(() => {
    if (availableModels && selectedModel) {
      const info = availableModels.find(m => m.name === selectedModel);
      setSelectedModelInfo(info);
      if (info) {
        onTokensChange?.(info.max_tokens);
      }
    }
  }, [selectedModel, availableModels, onTokensChange]);

  const handleProviderChange = (provider: string) => {
    setCurrentProvider(provider);
    onProviderChange?.(provider);

    // Reset model selection when provider changes
    const providerInfo = providersData?.providers.find(p => p.name === provider);
    if (providerInfo && providerInfo.default_model) {
      onModelChange?.(providerInfo.default_model);
    }
  };

  const getProviderIcon = (providerName: string) => {
    switch (providerName) {
      case 'openai':
        return '🤖';
      case 'anthropic':
        return '🧠';
      case 'deepseek':
        return '🔍';
      default:
        return '⚡';
    }
  };

  const getProviderDisplayName = (providerName: string) => {
    switch (providerName) {
      case 'openai':
        return 'OpenAI';
      case 'anthropic':
        return 'Anthropic';
      case 'deepseek':
        return 'DeepSeek';
      default:
        return providerName.charAt(0).toUpperCase() + providerName.slice(1);
    }
  };

  if (loadingProviders) {
    return (
      <Paper sx={{ p: 2, textAlign: 'center' }}>
        <CircularProgress size={24} />
        <Typography variant="body2" sx={{ mt: 1 }}>
          Loading LLM providers...
        </Typography>
      </Paper>
    );
  }

  if (providersError || !providersData) {
    return (
      <Alert
        severity="error"
        action={
          <IconButton size="small" onClick={() => refetchProviders()}>
            <RefreshIcon />
          </IconButton>
        }
      >
        Failed to load LLM providers. Click refresh to try again.
      </Alert>
    );
  }

  return (
    <Box>
      {/* Provider Selection Header */}
      <Paper sx={{ p: 2, mb: 3, backgroundColor: 'info.50' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <PsychologyIcon color="info" />
          <Typography variant="h6" color="info.main">
            LLM Provider Selection
          </Typography>
          <Tooltip title="Refresh providers">
            <IconButton size="small" onClick={() => refetchProviders()}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>
        <Typography variant="body2" color="text.secondary">
          Choose the AI provider and model for content generation
        </Typography>
      </Paper>

      <Grid container spacing={3}>
        {/* Provider Selection */}
        <Grid item xs={12} sm={4}>
          <Controller
            name="provider"
            control={control}
            defaultValue={providersData.default_provider}
            render={({ field }) => (
              <FormControl fullWidth>
                <InputLabel>LLM Provider *</InputLabel>
                <Select
                  {...field}
                  value={currentProvider || field.value}
                  label="LLM Provider *"
                  onChange={(e) => {
                    field.onChange(e);
                    handleProviderChange(e.target.value as string);
                  }}
                >
                  {providersData.providers.map((provider: ProviderInfo) => (
                    <MenuItem
                      key={provider.name}
                      value={provider.name}
                      disabled={!provider.available}
                    >
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
                        <span>{getProviderIcon(provider.name)}</span>
                        <Typography>{getProviderDisplayName(provider.name)}</Typography>
                        {provider.available ? (
                          <CheckCircleIcon color="success" sx={{ ml: 'auto', fontSize: 16 }} />
                        ) : (
                          <ErrorIcon color="error" sx={{ ml: 'auto', fontSize: 16 }} />
                        )}
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            )}
          />
        </Grid>

        {/* Model Selection */}
        <Grid item xs={12} sm={4}>
          <Controller
            name="model"
            control={control}
            defaultValue={providersData.providers.find(p => p.name === (currentProvider || providersData.default_provider))?.default_model || ''}
            render={({ field }) => (
              <FormControl fullWidth disabled={!currentProvider || availableModels.length === 0}>
                <InputLabel>Model *</InputLabel>
                <Select
                  {...field}
                  value={selectedModel || field.value}
                  label="Model *"
                  onChange={(e) => {
                    field.onChange(e);
                    onModelChange?.(e.target.value as string);
                  }}
                >
                  {availableModels.map((model: ModelInfo) => (
                    <MenuItem key={model.name} value={model.name}>
                      <Typography>{model.name}</Typography>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            )}
          />
        </Grid>

        {/* Token Limit Selection */}
        <Grid item xs={12} sm={4}>
          <Controller
            name="max_tokens"
            control={control}
            defaultValue={selectedTokens || selectedModelInfo?.max_tokens || 4096}
            render={({ field }) => (
              <FormControl fullWidth disabled={!selectedModelInfo}>
                <InputLabel>Max Tokens *</InputLabel>
                <Select
                  {...field}
                  value={selectedTokens ?? field.value}
                  label="Max Tokens *"
                  onChange={(e) => {
                    field.onChange(e);
                    onTokensChange?.(Number(e.target.value));
                  }}
                >
                  {selectedModelInfo && getTokenOptions(selectedModelInfo.max_tokens).map((value) => (
                    <MenuItem key={value} value={value}>
                      {value}
                    </MenuItem>
                  ))}
                </Select>
                {selectedModelInfo && (
                  <>
                    <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
                      Max output tokens: {selectedModelInfo.max_tokens} tokens
                    </Typography>
                    {selectedModelInfo.context_window ? (
                      <Typography variant="caption" color="text.secondary">
                        Context window: {selectedModelInfo.context_window} tokens
                      </Typography>
                    ) : null}
                  </>
                )}
              </FormControl>
            )}
          />
        </Grid>

        {/* Provider Info */}
        {currentProvider && (
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', alignItems: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                Available models:
              </Typography>
              {availableModels.map((model) => (
                <Chip
                  key={model.name}
                  label={model.name}
                  size="small"
                  variant={selectedModel === model.name ? "filled" : "outlined"}
                  color={selectedModel === model.name ? "primary" : "default"}
                />
              ))}
            </Box>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default ProviderSelector;
