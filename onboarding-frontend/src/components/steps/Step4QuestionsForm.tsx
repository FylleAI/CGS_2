/**
 * Step4QuestionsForm Component
 * Wizard-based questions interface (one question at a time, no chat history)
 */

import React, { useState, useMemo } from 'react';
import { Box } from '@mui/material';
import { WizardQuestion } from '../wizard/WizardQuestion';
import type { QuestionResponse, Question } from '@/types/onboarding';

interface Step4QuestionsFormProps {
  questions: QuestionResponse[];
  onSubmit: (answers: Record<string, any>) => void;
  isLoading?: boolean;
}

// Convert QuestionResponse to wizard-compatible Question
const convertToWizardQuestion = (q: QuestionResponse): Question => ({
  id: q.id,
  question: q.question,
  context: q.reason,
  type: q.expected_response_type as Question['type'],
  options: q.options?.map((opt) => ({
    value: opt,
    label: opt,
  })),
  required: q.required,
});

export const Step4QuestionsForm: React.FC<Step4QuestionsFormProps> = ({
  questions,
  onSubmit,
  isLoading = false,
}) => {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, any>>({});

  // Convert questions to wizard format
  const wizardQuestions = useMemo(
    () => questions.map(convertToWizardQuestion),
    [questions]
  );

  const currentQuestion = wizardQuestions[currentQuestionIndex];

  const handleAnswer = (value: any) => {
    // Save answer
    const newAnswers = { ...answers, [currentQuestion.id]: value };
    setAnswers(newAnswers);

    // Move to next question or submit
    if (currentQuestionIndex === wizardQuestions.length - 1) {
      // Last question - submit all answers
      onSubmit(newAnswers);
    } else {
      // Move to next question
      setCurrentQuestionIndex((prev) => prev + 1);
    }
  };

  if (wizardQuestions.length === 0) {
    return null;
  }

  return (
    <Box>
      <WizardQuestion
        question={currentQuestion}
        currentIndex={currentQuestionIndex}
        totalQuestions={wizardQuestions.length}
        onAnswer={handleAnswer}
        isLoading={isLoading}
      />
    </Box>
  );
};

export default Step4QuestionsForm;

