/**
 * OnboardingPage Component
 * Main onboarding wizard orchestrator
 */

import React from 'react';
import { WizardContainer } from '../components/wizard/WizardContainer';
import { Step1CompanyInput } from '../components/steps/Step1CompanyInput';
import { Step2ResearchProgress } from '../components/steps/Step2ResearchProgress';
import { Step3SnapshotReview } from '../components/steps/Step3SnapshotReview';
import { Step4QuestionsForm } from '../components/steps/Step4QuestionsForm';
import { Step5ExecutionProgress } from '../components/steps/Step5ExecutionProgress';
import { Step6Results } from '../components/steps/Step6Results';
import { useOnboarding } from '../hooks/useOnboarding';
import { useOnboardingStore } from '../store/onboardingStore';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { Box, Typography } from '@mui/material';
import { WizardButton } from '../components/wizard/WizardButton';
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
      user_email: data.user_email!,
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
    <WizardContainer currentStep={currentStep} totalSteps={6}>
      {error ? (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="h4" gutterBottom sx={{ fontWeight: 700 }}>
            ❌ Oops!
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
            {error.message}
          </Typography>
          <WizardButton onClick={resetOnboarding}>
            Try Again
          </WizardButton>
        </Box>
      ) : (
        renderStep()
      )}
    </WizardContainer>
  );
};

export default OnboardingWizard;

