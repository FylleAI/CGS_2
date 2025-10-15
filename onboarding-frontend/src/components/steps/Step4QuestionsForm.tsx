/**
 * Step4QuestionsForm Component
 * Chat-based conversational interface for clarifying questions
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  Chip,
  Stack,
  Paper,
  Fade,
  Slide,
  IconButton,
  Avatar,
} from '@mui/material';
import { Send, SmartToy, Person, CheckCircle } from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import type { QuestionResponse } from '@/types/onboarding';

interface Step4QuestionsFormProps {
  questions: QuestionResponse[];
  onSubmit: (answers: Record<string, any>) => void;
  isLoading?: boolean;
}

interface ChatMessage {
  id: string;
  type: 'bot' | 'user';
  content: string;
  timestamp: Date;
  questionId?: string;
}

export const Step4QuestionsForm: React.FC<Step4QuestionsFormProps> = ({
  questions,
  onSubmit,
  isLoading = false,
}) => {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, any>>({});
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const currentQuestion = questions[currentQuestionIndex];
  const isLastQuestion = currentQuestionIndex === questions.length - 1;
  const allQuestionsAnswered = currentQuestionIndex >= questions.length;

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Show first question on mount
  useEffect(() => {
    if (questions.length > 0 && messages.length === 0) {
      setTimeout(() => {
        addBotMessage(currentQuestion);
      }, 500);
    }
  }, [questions]);

  // Focus input when question changes
  useEffect(() => {
    if (!allQuestionsAnswered) {
      inputRef.current?.focus();
    }
  }, [currentQuestionIndex, allQuestionsAnswered]);

  const addBotMessage = (question: QuestionResponse) => {
    setIsTyping(true);
    setTimeout(() => {
      setIsTyping(false);
      setMessages((prev) => [
        ...prev,
        {
          id: `bot-${question.id}`,
          type: 'bot',
          content: question.question,
          timestamp: new Date(),
          questionId: question.id,
        },
      ]);
    }, 800);
  };

  const addUserMessage = (content: string, questionId: string) => {
    setMessages((prev) => [
      ...prev,
      {
        id: `user-${questionId}`,
        type: 'user',
        content,
        timestamp: new Date(),
        questionId,
      },
    ]);
  };

  const handleAnswer = (value: any) => {
    const displayValue = typeof value === 'boolean' ? (value ? 'Yes' : 'No') : String(value);

    // Add user message
    addUserMessage(displayValue, currentQuestion.id);

    // Save answer
    const newAnswers = { ...answers, [currentQuestion.id]: value };
    setAnswers(newAnswers);

    // Clear input
    setInputValue('');

    // Move to next question or submit
    if (isLastQuestion) {
      // All questions answered, submit after a delay
      setTimeout(() => {
        setCurrentQuestionIndex(questions.length);
        setTimeout(() => {
          onSubmit(newAnswers);
        }, 1000);
      }, 500);
    } else {
      // Show next question
      setTimeout(() => {
        setCurrentQuestionIndex((prev) => prev + 1);
        addBotMessage(questions[currentQuestionIndex + 1]);
      }, 1000);
    }
  };

  const handleTextSubmit = () => {
    if (!inputValue.trim()) return;
    handleAnswer(inputValue);
  };

  const handleChipClick = (value: string) => {
    handleAnswer(value);
  };

  return (
    <Box
      sx={{
        height: '70vh',
        display: 'flex',
        flexDirection: 'column',
        maxWidth: '800px',
        margin: '0 auto',
      }}
    >
      {/* Chat Header */}
      <Paper
        elevation={0}
        sx={{
          p: 2,
          borderRadius: '16px 16px 0 0',
          background: 'linear-gradient(135deg, #00D084 0%, #00A869 100%)',
          color: 'white',
        }}
      >
        <Stack direction="row" alignItems="center" spacing={2}>
          <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)' }}>
            <SmartToy />
          </Avatar>
          <Box>
            <Typography variant="h6" fontWeight={600}>
              Fylle AI Assistant
            </Typography>
            <Typography variant="caption" sx={{ opacity: 0.9 }}>
              {allQuestionsAnswered
                ? 'All questions answered!'
                : `Question ${currentQuestionIndex + 1} of ${questions.length}`}
            </Typography>
          </Box>
        </Stack>
      </Paper>

      {/* Messages Container */}
      <Paper
        elevation={0}
        sx={{
          flex: 1,
          overflowY: 'auto',
          p: 3,
          backgroundColor: '#F8F9FA',
          borderRadius: 0,
        }}
      >
        <Stack spacing={2}>
          <AnimatePresence>
            {messages.map((message, index) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
              >
                <Box
                  sx={{
                    display: 'flex',
                    justifyContent: message.type === 'bot' ? 'flex-start' : 'flex-end',
                    mb: 1,
                  }}
                >
                  <Box
                    sx={{
                      maxWidth: '70%',
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: 1,
                      flexDirection: message.type === 'bot' ? 'row' : 'row-reverse',
                    }}
                  >
                    <Avatar
                      sx={{
                        width: 32,
                        height: 32,
                        bgcolor: message.type === 'bot' ? '#00D084' : '#1976d2',
                      }}
                    >
                      {message.type === 'bot' ? <SmartToy fontSize="small" /> : <Person fontSize="small" />}
                    </Avatar>
                    <Paper
                      elevation={0}
                      sx={{
                        p: 2,
                        borderRadius: 2,
                        backgroundColor: message.type === 'bot' ? 'white' : '#00D084',
                        color: message.type === 'bot' ? 'text.primary' : 'white',
                      }}
                    >
                      <Typography variant="body1">{message.content}</Typography>
                      {message.type === 'bot' && message.questionId && (
                        <Typography variant="caption" sx={{ display: 'block', mt: 1, opacity: 0.7 }}>
                          {questions.find((q) => q.id === message.questionId)?.reason}
                        </Typography>
                      )}
                    </Paper>
                  </Box>
                </Box>
              </motion.div>
            ))}
          </AnimatePresence>

          {/* Typing Indicator */}
          {isTyping && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Avatar sx={{ width: 32, height: 32, bgcolor: '#00D084' }}>
                  <SmartToy fontSize="small" />
                </Avatar>
                <Paper elevation={0} sx={{ p: 2, borderRadius: 2 }}>
                  <Stack direction="row" spacing={0.5}>
                    <Box
                      component={motion.div}
                      animate={{ y: [0, -5, 0] }}
                      transition={{ repeat: Infinity, duration: 0.6, delay: 0 }}
                      sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: '#00D084' }}
                    />
                    <Box
                      component={motion.div}
                      animate={{ y: [0, -5, 0] }}
                      transition={{ repeat: Infinity, duration: 0.6, delay: 0.2 }}
                      sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: '#00D084' }}
                    />
                    <Box
                      component={motion.div}
                      animate={{ y: [0, -5, 0] }}
                      transition={{ repeat: Infinity, duration: 0.6, delay: 0.4 }}
                      sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: '#00D084' }}
                    />
                  </Stack>
                </Paper>
              </Box>
            </motion.div>
          )}

          {/* Completion Message */}
          {allQuestionsAnswered && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5 }}
            >
              <Paper
                elevation={0}
                sx={{
                  p: 3,
                  textAlign: 'center',
                  background: 'linear-gradient(135deg, #00D084 0%, #00A869 100%)',
                  color: 'white',
                  borderRadius: 2,
                }}
              >
                <CheckCircle sx={{ fontSize: 48, mb: 1 }} />
                <Typography variant="h6" fontWeight={600}>
                  Perfect! Generating your content...
                </Typography>
              </Paper>
            </motion.div>
          )}

          <div ref={messagesEndRef} />
        </Stack>
      </Paper>

      {/* Input Area */}
      {!allQuestionsAnswered && currentQuestion && (
        <Paper
          elevation={0}
          sx={{
            p: 2,
            borderRadius: '0 0 16px 16px',
            borderTop: '1px solid',
            borderColor: 'divider',
          }}
        >
          {/* Quick Reply Chips for select/boolean */}
          {(currentQuestion.expected_response_type === 'select' ||
            currentQuestion.expected_response_type === 'boolean') && (
            <Box sx={{ mb: 2 }}>
              <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                {currentQuestion.expected_response_type === 'boolean' ? (
                  <>
                    <Chip
                      label="Yes"
                      onClick={() => handleAnswer(true)}
                      sx={{
                        px: 2,
                        py: 2.5,
                        fontSize: '0.95rem',
                        fontWeight: 500,
                        borderRadius: 3,
                        cursor: 'pointer',
                        transition: 'all 0.2s',
                        '&:hover': {
                          backgroundColor: '#00D084',
                          color: 'white',
                          transform: 'translateY(-2px)',
                        },
                      }}
                    />
                    <Chip
                      label="No"
                      onClick={() => handleAnswer(false)}
                      sx={{
                        px: 2,
                        py: 2.5,
                        fontSize: '0.95rem',
                        fontWeight: 500,
                        borderRadius: 3,
                        cursor: 'pointer',
                        transition: 'all 0.2s',
                        '&:hover': {
                          backgroundColor: '#00D084',
                          color: 'white',
                          transform: 'translateY(-2px)',
                        },
                      }}
                    />
                  </>
                ) : (
                  currentQuestion.options?.map((option) => (
                    <Chip
                      key={option}
                      label={option}
                      onClick={() => handleChipClick(option)}
                      sx={{
                        px: 2,
                        py: 2.5,
                        fontSize: '0.95rem',
                        fontWeight: 500,
                        borderRadius: 3,
                        cursor: 'pointer',
                        transition: 'all 0.2s',
                        '&:hover': {
                          backgroundColor: '#00D084',
                          color: 'white',
                          transform: 'translateY(-2px)',
                        },
                      }}
                    />
                  ))
                )}
              </Stack>
            </Box>
          )}

          {/* Text Input for string/number */}
          {(currentQuestion.expected_response_type === 'string' ||
            currentQuestion.expected_response_type === 'number') && (
            <Stack direction="row" spacing={1}>
              <TextField
                inputRef={inputRef}
                fullWidth
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleTextSubmit();
                  }
                }}
                placeholder="Type your answer..."
                type={currentQuestion.expected_response_type === 'number' ? 'number' : 'text'}
                multiline={currentQuestion.expected_response_type === 'string'}
                rows={currentQuestion.expected_response_type === 'string' ? 2 : 1}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 3,
                    backgroundColor: 'white',
                  },
                }}
              />
              <IconButton
                onClick={handleTextSubmit}
                disabled={!inputValue.trim()}
                sx={{
                  backgroundColor: '#00D084',
                  color: 'white',
                  '&:hover': {
                    backgroundColor: '#00A869',
                  },
                  '&:disabled': {
                    backgroundColor: 'grey.300',
                  },
                }}
              >
                <Send />
              </IconButton>
            </Stack>
          )}
        </Paper>
      )}
    </Box>
  );
};

export default Step4QuestionsForm;

