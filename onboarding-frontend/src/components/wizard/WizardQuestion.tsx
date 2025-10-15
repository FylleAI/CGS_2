/**
 * WizardQuestion Component
 * Single question display with answer input (no chat history)
 */

import React, { useState } from 'react';
import { Box, Stack, Chip } from '@mui/material';
import { WizardStep } from './WizardStep';
import { WizardInput } from './WizardInput';
import { WizardChoice } from './WizardChoice';
import { WizardButton } from './WizardButton';
import { ArrowForward as NextIcon } from '@mui/icons-material';
import type { Question } from '@/types/onboarding';

interface WizardQuestionProps {
  question: Question;
  currentIndex: number;
  totalQuestions: number;
  onAnswer: (answer: any) => void;
  isLoading?: boolean;
}

export const WizardQuestion: React.FC<WizardQuestionProps> = ({
  question,
  currentIndex,
  totalQuestions,
  onAnswer,
  isLoading = false,
}) => {
  const [answer, setAnswer] = useState<any>('');

  const handleSubmit = () => {
    if (!answer || (typeof answer === 'string' && !answer.trim())) return;
    onAnswer(answer);
    setAnswer(''); // Reset for next question
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey && question.type === 'text') {
      e.preventDefault();
      handleSubmit();
    }
  };

  const renderInput = () => {
    switch (question.type) {
      case 'select':
      case 'enum':
        return (
          <Stack spacing={2}>
            {question.options?.map((option) => (
              <WizardChoice
                key={option.value}
                label={option.label}
                description={option.description}
                selected={answer === option.value}
                onClick={() => setAnswer(option.value)}
              />
            ))}
          </Stack>
        );

      case 'boolean':
        return (
          <Stack direction="row" spacing={2}>
            <Box sx={{ flex: 1 }}>
              <WizardChoice
                label="Yes"
                icon="✓"
                selected={answer === true}
                onClick={() => setAnswer(true)}
              />
            </Box>
            <Box sx={{ flex: 1 }}>
              <WizardChoice
                label="No"
                icon="✗"
                selected={answer === false}
                onClick={() => setAnswer(false)}
              />
            </Box>
          </Stack>
        );

      case 'multiselect':
        return (
          <Stack spacing={2}>
            {question.options?.map((option) => {
              const isSelected = Array.isArray(answer) && answer.includes(option.value);
              return (
                <WizardChoice
                  key={option.value}
                  label={option.label}
                  description={option.description}
                  selected={isSelected}
                  onClick={() => {
                    const current = Array.isArray(answer) ? answer : [];
                    if (isSelected) {
                      setAnswer(current.filter((v) => v !== option.value));
                    } else {
                      setAnswer([...current, option.value]);
                    }
                  }}
                />
              );
            })}
          </Stack>
        );

      case 'number':
        return (
          <WizardInput
            type="number"
            value={answer}
            onChange={(e) => setAnswer(Number(e.target.value))}
            onKeyPress={handleKeyPress}
            placeholder="Enter a number..."
            autoFocus
          />
        );

      case 'text':
      default:
        return (
          <WizardInput
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your answer..."
            multiline={question.type === 'text'}
            rows={question.type === 'text' ? 4 : 1}
            autoFocus
          />
        );
    }
  };

  const canSubmit = () => {
    if (question.type === 'multiselect') {
      return Array.isArray(answer) && answer.length > 0;
    }
    if (question.type === 'boolean') {
      return answer === true || answer === false;
    }
    if (typeof answer === 'string') {
      return answer.trim().length > 0;
    }
    return answer !== '' && answer !== null && answer !== undefined;
  };

  return (
    <WizardStep
      title={question.question}
      subtitle={question.context}
      icon="💬"
    >
      <Stack spacing={4}>
        {/* Question Counter */}
        <Box sx={{ display: 'flex', justifyContent: 'center' }}>
          <Chip
            label={`Question ${currentIndex + 1} of ${totalQuestions}`}
            size="small"
            sx={{
              backgroundColor: 'rgba(0, 208, 132, 0.1)',
              color: '#00D084',
              fontWeight: 600,
            }}
          />
        </Box>

        {/* Input */}
        {renderInput()}

        {/* Submit Button */}
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
          <WizardButton
            onClick={handleSubmit}
            disabled={!canSubmit()}
            loading={isLoading}
            icon={<NextIcon />}
          >
            {currentIndex === totalQuestions - 1 ? 'Complete' : 'Next'}
          </WizardButton>
        </Box>
      </Stack>
    </WizardStep>
  );
};

export default WizardQuestion;

