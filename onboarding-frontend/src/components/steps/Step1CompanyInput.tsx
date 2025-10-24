/**
 * Step1CompanyInput Component
 * Sequential wizard-style questions (like Step4)
 */

import React, { useState } from 'react';
import { Box, Stack, Typography, Chip, Grid } from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';
import { WizardInput } from '../wizard/WizardInput';
import { WizardChoice } from '../wizard/WizardChoice';
import { WizardButton } from '../wizard/WizardButton';
import { GOAL_OPTIONS } from '@/config/constants';
import type { OnboardingFormData, OnboardingGoal } from '@/types/onboarding';

// ============================================================================
// Question Definitions
// ============================================================================

interface Question {
  id: keyof OnboardingFormData;
  question: string;
  type: 'text' | 'url' | 'email' | 'textarea' | 'choice';
  placeholder?: string;
  required?: boolean;
  helperText?: string;
}

const QUESTIONS: Question[] = [
  {
    id: 'brand_name',
    question: "What's your brand name?",
    type: 'text',
    placeholder: 'e.g., Acme Corp',
    required: true,
  },
  {
    id: 'website',
    question: "What's your website?",
    type: 'url',
    placeholder: 'https://example.com',
    required: false,
    helperText: 'Optional - helps us understand your brand better',
  },
  {
    id: 'goal',
    question: 'What would you like to get?',
    type: 'choice',
    required: true,
    helperText: '💡 Recommended: Start with Company Analytics to get strategic insights',
  },
  {
    id: 'user_email',
    question: "What's your email address?",
    type: 'email',
    placeholder: 'your.email@example.com',
    required: true,
    helperText: "We'll send your content to this email",
  },
  {
    id: 'additional_context',
    question: 'Any additional context you want to share?',
    type: 'textarea',
    placeholder: 'Tell us more about your company, target audience, tone of voice...',
    required: false,
    helperText: 'Optional - but helps us create better content',
  },
];

// ============================================================================
// Component
// ============================================================================

interface Step1CompanyInputProps {
  onSubmit: (data: Partial<OnboardingFormData>) => void;
  isLoading?: boolean;
}

export const Step1CompanyInput: React.FC<Step1CompanyInputProps> = ({
  onSubmit,
  isLoading = false,
}) => {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<Partial<OnboardingFormData>>({});
  const [inputValue, setInputValue] = useState('');
  const [inputError, setInputError] = useState('');

  const currentQuestion = QUESTIONS[currentQuestionIndex];
  const isLastQuestion = currentQuestionIndex === QUESTIONS.length - 1;

  // ============================================================================
  // Validation
  // ============================================================================

  const validateInput = (value: string, question: Question): string => {
    if (question.required && !value.trim()) {
      return 'This field is required';
    }

    if (question.type === 'url' && value.trim()) {
      try {
        new URL(value);
      } catch {
        return 'Please enter a valid URL';
      }
    }

    if (question.type === 'email' && value.trim()) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(value)) {
        return 'Please enter a valid email';
      }
    }

    return '';
  };

  // ============================================================================
  // Handlers
  // ============================================================================

  const handleNext = () => {
    // Validate current input
    const error = validateInput(inputValue, currentQuestion);
    if (error) {
      setInputError(error);
      return;
    }

    // Save answer
    const newAnswers = { ...answers, [currentQuestion.id]: inputValue };
    setAnswers(newAnswers);

    // Move to next question or submit
    if (isLastQuestion) {
      onSubmit(newAnswers);
    } else {
      setCurrentQuestionIndex((prev) => prev + 1);
      setInputValue('');
      setInputError('');
    }
  };

  const handleChoiceSelect = (value: OnboardingGoal) => {
    const newAnswers = { ...answers, [currentQuestion.id]: value };
    setAnswers(newAnswers);

    // Auto-advance after choice selection
    setTimeout(() => {
      if (isLastQuestion) {
        onSubmit(newAnswers);
      } else {
        setCurrentQuestionIndex((prev) => prev + 1);
        setInputValue('');
        setInputError('');
      }
    }, 300);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && currentQuestion.type !== 'textarea') {
      e.preventDefault();
      handleNext();
    }
  };

  // ============================================================================
  // Render Question
  // ============================================================================

  const renderQuestion = () => {
    if (currentQuestion.type === 'choice') {
      return (
        <Stack spacing={2}>
          {/* Helper text for goal selection */}
          {currentQuestion.helperText && (
            <Typography
              variant="body2"
              sx={{
                color: 'primary.main',
                fontWeight: 500,
                textAlign: 'center',
                mb: 1,
              }}
            >
              {currentQuestion.helperText}
            </Typography>
          )}

          <Grid container spacing={2}>
            {GOAL_OPTIONS.map((option) => {
              const isRecommended = option.value === 'company_snapshot';

              return (
                <Grid item xs={12} sm={6} key={option.value}>
                  <Box sx={{ position: 'relative' }}>
                    {/* Recommended badge */}
                    {isRecommended && (
                      <Chip
                        label="Recommended"
                        size="small"
                        color="primary"
                        sx={{
                          position: 'absolute',
                          top: -8,
                          right: 8,
                          zIndex: 1,
                          fontWeight: 600,
                          fontSize: '0.7rem',
                        }}
                      />
                    )}

                    <WizardChoice
                      label={option.label}
                      description={option.description}
                      icon={option.icon}
                      selected={false}
                      onClick={() => handleChoiceSelect(option.value as OnboardingGoal)}
                    />
                  </Box>
                </Grid>
              );
            })}
          </Grid>
        </Stack>
      );
    }

    return (
      <Stack spacing={3}>
        <WizardInput
          value={inputValue}
          onChange={(e) => {
            setInputValue(e.target.value);
            setInputError('');
          }}
          onKeyPress={handleKeyPress}
          placeholder={currentQuestion.placeholder}
          error={!!inputError}
          helperText={inputError || currentQuestion.helperText}
          multiline={currentQuestion.type === 'textarea'}
          rows={currentQuestion.type === 'textarea' ? 4 : 1}
          autoFocus
          fullWidth
        />

        <Box sx={{ display: 'flex', justifyContent: 'center' }}>
          <WizardButton onClick={handleNext} loading={isLoading} size="large">
            {isLastQuestion ? 'Start Research' : 'Continue'}
          </WizardButton>
        </Box>
      </Stack>
    );
  };

  // ============================================================================
  // Render
  // ============================================================================

  return (
    <Box
      sx={{
        width: '100%',
        maxWidth: 600,
        mx: 'auto',
        px: 3,
      }}
    >
      <AnimatePresence mode="wait">
        <motion.div
          key={currentQuestionIndex}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.3 }}
        >
          <Stack spacing={4} alignItems="center">
            {/* Question Counter */}
            <Chip
              label={`Question ${currentQuestionIndex + 1} of ${QUESTIONS.length}`}
              size="small"
              sx={{
                bgcolor: 'rgba(0, 208, 132, 0.1)',
                color: '#00D084',
                fontWeight: 600,
              }}
            />

            {/* Question Text */}
            <Typography
              variant="h4"
              sx={{
                fontWeight: 700,
                textAlign: 'center',
                color: 'text.primary',
              }}
            >
              {currentQuestion.question}
            </Typography>

            {/* Question Input/Choices */}
            <Box sx={{ width: '100%' }}>{renderQuestion()}</Box>
          </Stack>
        </motion.div>
      </AnimatePresence>
    </Box>
  );
};

export default Step1CompanyInput;

