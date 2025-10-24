/**
 * ConversationalContainer Component
 * Main container for conversational onboarding interface
 */

import React from 'react';
import { Box, Container, Paper, Stepper, Step, StepLabel } from '@mui/material';
import { STEP_LABELS } from '@/config/constants';
import type { OnboardingStep } from '@/types/onboarding';

interface ConversationalContainerProps {
  currentStep: OnboardingStep;
  children: React.ReactNode;
}

export const ConversationalContainer: React.FC<ConversationalContainerProps> = ({
  currentStep,
  children,
}) => {
  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
        py: 4,
      }}
    >
      <Container maxWidth="md">
        {/* Progress Stepper */}
        <Paper
          elevation={0}
          sx={{
            p: 3,
            mb: 3,
            borderRadius: 3,
            backgroundColor: 'rgba(255, 255, 255, 0.9)',
            backdropFilter: 'blur(10px)',
          }}
        >
          <Stepper activeStep={currentStep} alternativeLabel>
            {STEP_LABELS.map((label, index) => (
              <Step key={index}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>
        </Paper>

        {/* Main Content */}
        <Paper
          elevation={3}
          sx={{
            p: 4,
            borderRadius: 4,
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(255, 255, 255, 0.3)',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
            minHeight: 500,
          }}
        >
          {children}
        </Paper>
      </Container>
    </Box>
  );
};

export default ConversationalContainer;

