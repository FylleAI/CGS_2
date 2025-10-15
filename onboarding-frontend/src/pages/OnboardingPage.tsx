/**
 * OnboardingPage Component
 * Main onboarding wizard orchestrator
 */

import React from 'react';
import { ConversationalContainer } from '../components/onboarding/ConversationalContainer';
import { Step1CompanyInput } from '../components/steps/Step1CompanyInput';
import { Step2ResearchProgress } from '../components/steps/Step2ResearchProgress';
import { Step3SnapshotReview } from '../components/steps/Step3SnapshotReview';
import { Step4QuestionsForm } from '../components/steps/Step4QuestionsForm';
import { Step5ExecutionProgress } from '../components/steps/Step5ExecutionProgress';
import { Step6Results } from '../components/steps/Step6Results';
import { useOnboarding } from '../hooks/useOnboarding';
import { useOnboardingStore } from '../store/onboardingStore';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { Box, Typography, Button } from '@mui/material';
import type { OnboardingFormData } from '../types/onboarding';

export const OnboardingWizard: React.FC = () => {
  const {
    currentStep,
    isLoading,
    error,
    startOnboarding,
    submitAnswers,
    resetOnboarding,
    snapshot,
    questions,
    session,
  } = useOnboarding();

  const handleCompanySubmit = (data: Partial<OnboardingFormData>) => {
    startOnboarding({
      brand_name: data.brand_name!,
      website: data.website || undefined,
      goal: data.goal!,
      user_email: data.user_email || undefined,
      additional_context: data.additional_context || undefined,
    });
  };

  const handleAnswersSubmit = (answers: Record<string, any>) => {
    submitAnswers(answers);
  };

  const renderStep = () => {
    switch (currentStep) {
      case 0:
        return (
          <Step1CompanyInput
            onSubmit={handleCompanySubmit}
            isLoading={isLoading}
          />
        );

      case 1:
        return <Step2ResearchProgress />;

      case 2:
        return snapshot ? (
          <Step3SnapshotReview
            snapshot={snapshot}
            onContinue={() => useOnboardingStore.getState().nextStep()}
            isLoading={isLoading}
          />
        ) : (
          <LoadingSpinner message="Loading snapshot..." />
        );

      case 3:
        return questions.length > 0 ? (
          <Step4QuestionsForm
            questions={questions}
            onSubmit={handleAnswersSubmit}
            isLoading={isLoading}
          />
        ) : (
          <LoadingSpinner message="Loading questions..." />
        );

      case 4:
        return <Step5ExecutionProgress />;

      case 5:
        return session ? (
          <Step6Results
            session={session}
            onStartNew={resetOnboarding}
          />
        ) : (
          <LoadingSpinner message="Loading results..." />
        );

      default:
        return <LoadingSpinner />;
    }
  };

  return (
    <ConversationalContainer currentStep={currentStep}>
      {error ? (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="h5" color="error" gutterBottom>
            ❌ Error
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            {error.message}
          </Typography>
          <Button variant="contained" onClick={resetOnboarding}>
            Try Again
          </Button>
        </Box>
      ) : (
        renderStep()
      )}
    </ConversationalContainer>
  );
};

export default OnboardingWizard;

