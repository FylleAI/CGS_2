import React, { useState, useEffect } from 'react';
import {
  Box,
  TextField,
  Button,
  Grid,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
  Chip,
  Alert,
  CircularProgress,
  Divider,
  Paper,
} from '@mui/material';
import {
  Send as SendIcon,
  AutoAwesome as AutoAwesomeIcon,
  Article as ArticleIcon,
  Email as EmailIcon,
} from '@mui/icons-material';
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import toast from 'react-hot-toast';

import { useAppStore } from '../store/appStore';
import { GenerationRequest } from '../types';
import apiService from '../services/api';
import RAGContentSelector from './RAGContentSelector';
import ProviderSelector from './ProviderSelector';

// Enhanced Article Schema - Adattato dal workflow originale
const enhancedArticleSchema = yup.object({
  topic: yup
    .string()
    .required('Topic is required')
    .min(3, 'Topic must be at least 3 characters')
    .max(200, 'Topic must be less than 200 characters'),
  target_word_count: yup
    .number()
    .required('Word count is required')
    .min(300, 'Minimum 300 words')
    .max(5000, 'Maximum 5000 words'),
  target: yup
    .string()
    .required('Target audience is required')
    .min(3, 'Target must be at least 3 characters')
    .max(500, 'Target must be less than 500 characters'),
  // Campi opzionali per migliorare il workflow
  tone: yup.string().optional(),
  include_statistics: yup.boolean().optional(),
  include_examples: yup.boolean().optional(),
  context: yup.string().optional(),
});

// Newsletter Premium Schema
const newsletterPremiumSchema = yup.object({
  newsletter_topic: yup
    .string()
    .required('Newsletter topic is required')
    .min(3, 'Topic must be at least 3 characters')
    .max(200, 'Topic must be less than 200 characters'),
  target_word_count: yup
    .number()
    .required('Word count is required')
    .min(400, 'Minimum 400 words')
    .max(2000, 'Maximum 2000 words'),
  target: yup
    .string()
    .required('Target audience is required')
    .min(3, 'Target must be at least 3 characters'),
  edition_number: yup
    .number()
    .required('Edition number is required')
    .min(1, 'Edition must be at least 1'),
  featured_sections: yup.array().of(yup.string()).optional(),
  context: yup.string().optional(),
});

// Premium Newsletter Schema
const premiumNewsletterSchema = yup.object({
  newsletter_topic: yup
    .string()
    .required('Newsletter topic is required')
    .min(5, 'Topic must be at least 5 characters')
    .max(200, 'Topic must be less than 200 characters'),
  premium_sources: yup
    .string()
    .required('At least one premium source is required')
    .test('valid-urls', 'Please enter valid URLs', function(value) {
      if (!value) return false;
      const urls = value.split('\n').filter(url => url.trim());
      if (urls.length === 0) return false;
      if (urls.length > 10) return this.createError({ message: 'Maximum 10 sources allowed' });

      for (const url of urls) {
        if (!url.trim().match(/^https?:\/\/.+/)) {
          return this.createError({ message: `Invalid URL: ${url.trim()}` });
        }
      }
      return true;
    }),
  target_audience: yup
    .string()
    .required('Target audience is required')
    .min(3, 'Target audience must be at least 3 characters')
    .max(500, 'Target audience must be less than 500 characters'),
  target_word_count: yup
    .number()
    .optional()
    .min(800, 'Minimum 800 words')
    .max(2500, 'Maximum 2500 words'),
  edition_number: yup
    .number()
    .optional()
    .min(1, 'Edition must be at least 1'),
  exclude_topics: yup
    .string()
    .optional(),
  priority_sections: yup
    .string()
    .optional(),
  custom_instructions: yup
    .string()
    .optional()
    .max(1000, 'Instructions must be less than 1000 characters')
});

// Form data types
type EnhancedArticleFormData = {
  topic: string;
  target_word_count: number;
  target: string;
  tone?: string;
  include_statistics?: boolean;
  include_examples?: boolean;
  context?: string;
};

type NewsletterPremiumFormData = {
  newsletter_topic: string;
  target_word_count: number;
  target: string;
  edition_number: number;
  featured_sections?: string[];
  context?: string;
};

type PremiumNewsletterFormData = {
  newsletter_topic: string;
  premium_sources: string;
  target_audience: string;
  target_word_count?: number;
  edition_number?: number;
  exclude_topics?: string;
  priority_sections?: string;
  custom_instructions?: string;
};

type WorkflowFormData = EnhancedArticleFormData | NewsletterPremiumFormData | PremiumNewsletterFormData;

interface WorkflowFormProps {
  onGenerationStart?: () => void;
  onGenerationComplete?: (result: any) => void;
}

const WorkflowForm: React.FC<WorkflowFormProps> = ({
  onGenerationStart,
  onGenerationComplete,
}) => {
  const { selectedClient, selectedWorkflow } = useAppStore();
  const [isGenerating, setIsGenerating] = useState(false);
  const [selectedRAGContents, setSelectedRAGContents] = useState<string[]>([]);
  const [selectedProvider, setSelectedProvider] = useState<string>('openai');
  const [selectedModel, setSelectedModel] = useState<string>('gpt-4o');

  // Determine schema based on workflow
  const getValidationSchema = () => {
    if (selectedWorkflow?.id === 'enhanced_article') {
      return enhancedArticleSchema;
    } else if (selectedWorkflow?.id === 'newsletter_premium') {
      return newsletterPremiumSchema;
    } else if (selectedWorkflow?.id === 'premium_newsletter') {
      return premiumNewsletterSchema;
    }
    return yup.object({});
  };

  const {
    control,
    handleSubmit,
    formState: { errors, isValid },
    reset,
    watch,
  } = useForm<any>({
    resolver: yupResolver(getValidationSchema()),
    mode: 'onChange',
    defaultValues: getDefaultValues(),
  });

  function getDefaultValues() {
    const baseDefaults = {
      provider: selectedProvider,
      model: selectedModel,
      temperature: 0.7,
    };

    if (selectedWorkflow?.id === 'enhanced_article') {
      return {
        ...baseDefaults,
        topic: '',
        target_word_count: 800,
        target: selectedClient?.targetAudience || '',
        tone: 'professional',
        include_statistics: true,
        include_examples: true,
        context: '',
      };
    } else if (selectedWorkflow?.id === 'newsletter_premium') {
      return {
        ...baseDefaults,
        newsletter_topic: '',
        target_word_count: 600,
        target: selectedClient?.targetAudience || '',
        edition_number: 1,
        featured_sections: [],
        context: '',
      };
    } else if (selectedWorkflow?.id === 'premium_newsletter') {
      return {
        ...baseDefaults,
        newsletter_topic: '',
        premium_sources: '',
        target_audience: selectedClient?.targetAudience || '',
        target_word_count: 1200,
        edition_number: 1,
        exclude_topics: '',
        priority_sections: '',
        custom_instructions: '',
      };
    }
    return baseDefaults;
  }

  // Reset form when workflow changes
  useEffect(() => {
    reset(getDefaultValues());
  }, [selectedWorkflow, selectedClient, reset]);

  const onSubmit = async (data: any) => {
    if (!selectedClient || !selectedWorkflow) {
      toast.error('Please select client and workflow');
      return;
    }

    setIsGenerating(true);
    onGenerationStart?.();

    try {
      const request: GenerationRequest = {
        clientProfile: selectedClient.name,
        workflowType: selectedWorkflow.id,
        parameters: {
          ...data,
          client_name: selectedClient.displayName,
          brand_voice: selectedClient.brandVoice,
        },
        ragContentIds: selectedRAGContents,
      };

      console.log('Sending generation request:', request);
      const result = await apiService.generateContent(request);
      
      if (result.success) {
        toast.success('Content generated successfully!');
        onGenerationComplete?.(result);
      } else {
        toast.error(result.errorMessage || 'Generation failed');
      }
    } catch (error: any) {
      console.error('Generation error:', error);
      toast.error(error.message || 'Failed to generate content');
    } finally {
      setIsGenerating(false);
    }
  };

  if (!selectedWorkflow) {
    return (
      <Alert severity="info">
        Please select a workflow to configure parameters.
      </Alert>
    );
  }

  const renderEnhancedArticleForm = () => (
    <Box>
      {/* Workflow Info */}
      <Paper sx={{ p: 2, mb: 3, backgroundColor: 'primary.50' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <ArticleIcon color="primary" />
          <Typography variant="h6" color="primary.main">
            Enhanced Article Creation
          </Typography>
        </Box>
        <Typography variant="body2" color="text.secondary">
          Workflow ottimizzato con setting iniziale, ricerca web e creazione contenuto finale
        </Typography>
      </Paper>

      <Grid container spacing={3}>
        {/* Topic - Campo principale */}
        <Grid item xs={12}>
          <Controller
            name="topic"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                fullWidth
                label="Article Topic *"
                placeholder="Enter the main topic for your enhanced article"
                error={!!errors.topic}
                helperText={errors.topic?.message as string || "This will be used for RAG research and web search"}
                variant="outlined"
                multiline
                rows={2}
              />
            )}
          />
        </Grid>

        {/* Numero parole e Target */}
        <Grid item xs={12} sm={6}>
          <Controller
            name="target_word_count"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                fullWidth
                type="number"
                label="Target Word Count *"
                error={!!errors.target_word_count}
                helperText={errors.target_word_count?.message as string || "Recommended: 800-1500 words"}
                InputProps={{ inputProps: { min: 300, max: 5000 } }}
              />
            )}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <Controller
            name="target"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                fullWidth
                label="Target Audience *"
                placeholder="Describe your target audience"
                error={!!errors.target}
                helperText={errors.target?.message as string || "Will be used to tailor content tone and examples"}
                multiline
                rows={2}
              />
            )}
          />
        </Grid>

        {/* Context aggiuntivo */}
        <Grid item xs={12}>
          <Controller
            name="context"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                fullWidth
                label="Additional Context (Optional)"
                placeholder="Any additional context or specific requirements for the article"
                multiline
                rows={3}
                helperText="This context will be used by the RAG specialist to create a comprehensive brief"
              />
            )}
          />
        </Grid>

        {/* Impostazioni avanzate */}
        <Grid item xs={12}>
          <Typography variant="subtitle2" gutterBottom>
            Advanced Settings
          </Typography>
        </Grid>

        <Grid item xs={12} sm={6}>
          <Controller
            name="tone"
            control={control}
            render={({ field }) => (
              <FormControl fullWidth>
                <InputLabel>Tone</InputLabel>
                <Select {...field} label="Tone">
                  <MenuItem value="professional">Professional</MenuItem>
                  <MenuItem value="conversational">Conversational</MenuItem>
                  <MenuItem value="academic">Academic</MenuItem>
                  <MenuItem value="casual">Casual</MenuItem>
                </Select>
              </FormControl>
            )}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            <Controller
              name="include_statistics"
              control={control}
              render={({ field }) => (
                <FormControlLabel
                  control={<Switch {...field} checked={field.value} />}
                  label="Include Statistics & Data"
                />
              )}
            />
            <Controller
              name="include_examples"
              control={control}
              render={({ field }) => (
                <FormControlLabel
                  control={<Switch {...field} checked={field.value} />}
                  label="Include Real Examples"
                />
              )}
            />
          </Box>
        </Grid>
      </Grid>
    </Box>
  );

  const renderNewsletterPremiumForm = () => (
    <Box>
      {/* Workflow Info */}
      <Paper sx={{ p: 2, mb: 3, backgroundColor: 'secondary.50' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <EmailIcon color="secondary" />
          <Typography variant="h6" color="secondary.main">
            Newsletter Premium
          </Typography>
        </Box>
        <Typography variant="body2" color="text.secondary">
          Premium newsletter with curated content and insights
        </Typography>
      </Paper>

      <Grid container spacing={3}>
        {/* Newsletter Topic */}
        <Grid item xs={12}>
          <Controller
            name="newsletter_topic"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                fullWidth
                label="Newsletter Topic *"
                placeholder="Main theme for this newsletter edition"
                error={!!errors.newsletter_topic}
                helperText={errors.newsletter_topic?.message as string}
                multiline
                rows={2}
              />
            )}
          />
        </Grid>

        {/* Word Count, Target, Edition */}
        <Grid item xs={12} sm={4}>
          <Controller
            name="target_word_count"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                fullWidth
                type="number"
                label="Target Word Count *"
                error={!!errors.target_word_count}
                helperText={errors.target_word_count?.message as string}
                InputProps={{ inputProps: { min: 400, max: 2000 } }}
              />
            )}
          />
        </Grid>

        <Grid item xs={12} sm={4}>
          <Controller
            name="target"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                fullWidth
                label="Target Audience *"
                error={!!errors.target}
                helperText={errors.target?.message as string}
              />
            )}
          />
        </Grid>

        <Grid item xs={12} sm={4}>
          <Controller
            name="edition_number"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                fullWidth
                type="number"
                label="Edition Number *"
                error={!!errors.edition_number}
                helperText={errors.edition_number?.message as string}
                InputProps={{ inputProps: { min: 1 } }}
              />
            )}
          />
        </Grid>

        {/* Context */}
        <Grid item xs={12}>
          <Controller
            name="context"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                fullWidth
                label="Additional Context (Optional)"
                placeholder="Any specific requirements or themes for this newsletter"
                multiline
                rows={3}
              />
            )}
          />
        </Grid>

        {/* Featured Sections */}
        <Grid item xs={12}>
          <Controller
            name="featured_sections"
            control={control}
            render={({ field }) => (
              <FormControl fullWidth>
                <InputLabel>Featured Sections</InputLabel>
                <Select
                  {...field}
                  multiple
                  label="Featured Sections"
                  renderValue={(selected: unknown) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {Array.isArray(selected) && (selected as string[]).map((value: string) => (
                        <Chip key={value} label={value.replace('_', ' ')} size="small" />
                      ))}
                    </Box>
                  )}
                >
                  <MenuItem value="market_analysis">Market Analysis</MenuItem>
                  <MenuItem value="expert_insights">Expert Insights</MenuItem>
                  <MenuItem value="trending_topics">Trending Topics</MenuItem>
                  <MenuItem value="educational_content">Educational Content</MenuItem>
                </Select>
              </FormControl>
            )}
          />
        </Grid>
      </Grid>
    </Box>
  );

  const renderPremiumNewsletterForm = () => (
    <Box>
      {/* Workflow Info Header */}
      <Paper sx={{ p: 2, mb: 3, backgroundColor: 'secondary.50' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <EmailIcon color="secondary" />
          <Typography variant="h6" color="secondary.main">
            Premium Newsletter
          </Typography>
        </Box>
        <Typography variant="body2" color="text.secondary">
          Advanced newsletter with premium source analysis and client-specific brand integration
        </Typography>
      </Paper>

      <Grid container spacing={3}>
        {/* Newsletter Topic */}
        <Grid item xs={12}>
          <Controller
            name="newsletter_topic"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                fullWidth
                label="Newsletter Topic *"
                placeholder="Enter the main theme for this newsletter edition"
                error={!!errors.newsletter_topic}
                helperText={errors.newsletter_topic?.message as string}
                multiline
                rows={2}
              />
            )}
          />
        </Grid>

        {/* Premium Sources URLs */}
        <Grid item xs={12}>
          <Controller
            name="premium_sources"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                fullWidth
                label="Premium Sources URLs *"
                placeholder="Enter premium source URLs (one per line, max 10)"
                error={!!errors.premium_sources}
                helperText={errors.premium_sources?.message as string || "Enter one URL per line. Maximum 10 sources allowed."}
                multiline
                rows={6}
              />
            )}
          />
        </Grid>

        {/* Target Audience */}
        <Grid item xs={12}>
          <Controller
            name="target_audience"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                fullWidth
                label="Target Audience *"
                placeholder="Describe the specific target audience for this edition"
                error={!!errors.target_audience}
                helperText={errors.target_audience?.message as string}
                multiline
                rows={3}
              />
            )}
          />
        </Grid>

        {/* Word Count & Edition Number */}
        <Grid item xs={12} sm={6}>
          <Controller
            name="target_word_count"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                fullWidth
                type="number"
                label="Target Word Count"
                placeholder="1200"
                error={!!errors.target_word_count}
                helperText={errors.target_word_count?.message as string}
                InputProps={{ inputProps: { min: 800, max: 2500 } }}
              />
            )}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <Controller
            name="edition_number"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                fullWidth
                type="number"
                label="Edition Number"
                placeholder="1"
                error={!!errors.edition_number}
                helperText={errors.edition_number?.message as string}
                InputProps={{ inputProps: { min: 1 } }}
              />
            )}
          />
        </Grid>

        {/* Exclude Topics */}
        <Grid item xs={12} sm={6}>
          <Controller
            name="exclude_topics"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                fullWidth
                label="Topics to Exclude"
                placeholder="Enter topics to exclude (comma-separated)"
                error={!!errors.exclude_topics}
                helperText={errors.exclude_topics?.message as string}
              />
            )}
          />
        </Grid>

        {/* Priority Sections */}
        <Grid item xs={12} sm={6}>
          <Controller
            name="priority_sections"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                fullWidth
                label="Priority Sections"
                placeholder="Enter priority sections (comma-separated)"
                error={!!errors.priority_sections}
                helperText={errors.priority_sections?.message as string}
              />
            )}
          />
        </Grid>

        {/* Custom Instructions */}
        <Grid item xs={12}>
          <Controller
            name="custom_instructions"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                fullWidth
                label="Custom Instructions"
                placeholder="Any additional instructions for the newsletter generation"
                error={!!errors.custom_instructions}
                helperText={errors.custom_instructions?.message as string}
                multiline
                rows={3}
              />
            )}
          />
        </Grid>
      </Grid>
    </Box>
  );

  return (
    <Box component="form" onSubmit={handleSubmit(onSubmit)}>
      {/* Workflow-specific form */}
      {selectedWorkflow.id === 'enhanced_article' && renderEnhancedArticleForm()}
      {selectedWorkflow.id === 'newsletter_premium' && renderNewsletterPremiumForm()}
      {selectedWorkflow.id === 'premium_newsletter' && renderPremiumNewsletterForm()}

      {/* Provider Selection */}
      <Divider sx={{ my: 4 }} />
      <ProviderSelector
        control={control}
        selectedProvider={selectedProvider}
        selectedModel={selectedModel}
        onProviderChange={setSelectedProvider}
        onModelChange={setSelectedModel}
      />

      {/* RAG Content Selection */}
      {selectedClient?.ragEnabled && (
        <>
          <Divider sx={{ my: 4 }} />
          <RAGContentSelector
            clientProfile={selectedClient.name}
            selectedContents={selectedRAGContents}
            onSelectionChange={setSelectedRAGContents}
          />
        </>
      )}

      {/* Submit Button */}
      <Box sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
        <Button
          type="submit"
          variant="contained"
          size="large"
          disabled={!isValid || isGenerating}
          startIcon={
            isGenerating ? (
              <CircularProgress size={20} />
            ) : (
              <AutoAwesomeIcon />
            )
          }
          sx={{ minWidth: 200, py: 1.5 }}
        >
          {isGenerating ? 'Generating Content...' : 'Generate Content'}
        </Button>
      </Box>

      {/* Form Debug Info (solo in development) */}
      {process.env.NODE_ENV === 'development' && (
        <Box sx={{ mt: 2, p: 2, backgroundColor: 'grey.100', borderRadius: 1 }}>
          <Typography variant="caption" display="block">
            Form Valid: {isValid ? '✅' : '❌'} | 
            Selected RAG: {selectedRAGContents.length} | 
            Workflow: {selectedWorkflow.id}
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default WorkflowForm;
