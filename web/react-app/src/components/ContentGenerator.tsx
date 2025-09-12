import React, { useEffect, useState } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Stepper,
  Step,
  StepLabel,
  Paper,
} from '@mui/material';
import { useQuery } from 'react-query';
import toast from 'react-hot-toast';

import { useAppStore } from '../store/appStore';
import { GenerationResponse } from '../types';
import apiService from '../services/api';
import ClientSelector from './ClientSelector';
import WorkflowSelector from './WorkflowSelector';
import WorkflowForm from './WorkflowForm';
import GenerationResults from './GenerationResults';
import RAGUploader from './RAGUploader';

const steps = [
  'Select Client',
  'Choose Workflow',
  'Configure Parameters',
  'Generate Content'
];

const ContentGenerator: React.FC = () => {
  const {
    selectedClient,
    selectedWorkflow,
    setAvailableClients,
    setAvailableWorkflows,
    setError,
    error
  } = useAppStore();

  // Generation state
  const [generationResult, setGenerationResult] = useState<GenerationResponse | undefined>();
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationProgress, setGenerationProgress] = useState(0);

  // Load clients
  const { data: clients, isLoading: loadingClients } = useQuery(
    'clients',
    apiService.getClientProfiles,
    {
      onSuccess: (data) => {
        setAvailableClients(data);
      },
      onError: (error: any) => {
        console.error('Failed to load clients:', error);
        setError('Failed to load client profiles');
        toast.error('Failed to load client profiles');
      }
    }
  );

  // Load workflows
  const { data: workflows, isLoading: loadingWorkflows } = useQuery(
    'workflows',
    apiService.getWorkflowTypes,
    {
      onSuccess: (data) => {
        setAvailableWorkflows(data);
      },
      onError: (error: any) => {
        console.error('Failed to load workflows:', error);
        setError('Failed to load workflow types');
        toast.error('Failed to load workflow types');
      }
    }
  );

  // Determine current step
  const getCurrentStep = () => {
    if (!selectedClient) return 0;
    if (!selectedWorkflow) return 1;
    return 2;
  };

  const currentStep = getCurrentStep();

  // Generation handlers
  const handleGenerationStart = () => {
    setIsGenerating(true);
    setGenerationProgress(0);
    setGenerationResult(undefined);
  };

  const handleGenerationComplete = (result: GenerationResponse) => {
    setIsGenerating(false);
    setGenerationProgress(100);
    setGenerationResult(result);
  };

  const handleSaveContent = (result: GenerationResponse, filename: string) => {
    // Here you could implement saving to backend or local storage
    console.log('Saving content:', { result, filename });
    toast.success(`Content saved as ${filename}`);
  };

  return (
    <Box>
      {/* Progress Stepper */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Stepper activeStep={currentStep} alternativeLabel>
          {steps.map((label, index) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
      </Paper>

      {/* Main Content */}
      <Grid container spacing={4}>
        {/* Left Column - Configuration */}
        <Grid item xs={12} lg={8}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            {/* Client Selection */}
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  1. Select Client Profile
                </Typography>
                <ClientSelector loading={loadingClients} />
              </CardContent>
            </Card>

            {/* Knowledge Base Uploader */}
            {selectedClient && (
              <RAGUploader />
            )}

            {/* Workflow Selection */}
            {selectedClient && (
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    2. Choose Workflow Type
                  </Typography>
                  <WorkflowSelector loading={loadingWorkflows} />
                </CardContent>
              </Card>
            )}

            {/* Workflow Configuration */}
            {selectedClient && selectedWorkflow && (
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    3. Configure Parameters
                  </Typography>
                  <WorkflowForm
                    onGenerationStart={handleGenerationStart}
                    onGenerationComplete={handleGenerationComplete}
                  />
                </CardContent>
              </Card>
            )}
          </Box>
        </Grid>

        {/* Right Column - Info & Results */}
        <Grid item xs={12} lg={4}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            {/* Selected Configuration Summary */}
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Configuration Summary
                </Typography>
                
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Client Profile
                  </Typography>
                  <Typography variant="body2">
                    {selectedClient?.displayName || 'Not selected'}
                  </Typography>
                </Box>

                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Workflow Type
                  </Typography>
                  <Typography variant="body2">
                    {selectedWorkflow?.displayName || 'Not selected'}
                  </Typography>
                </Box>

                {selectedWorkflow && (
                  <Box>
                    <Typography variant="subtitle2" color="text.secondary">
                      Description
                    </Typography>
                    <Typography variant="body2">
                      {selectedWorkflow.description}
                    </Typography>
                  </Box>
                )}
              </CardContent>
            </Card>

            {/* Generation Results */}
            <GenerationResults
              result={generationResult}
              isGenerating={isGenerating}
              progress={generationProgress}
              onSave={handleSaveContent}
            />
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ContentGenerator;
