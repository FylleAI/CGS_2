/**
 * Step5ExecutionProgress Component
 * Minimal wizard-style content generation progress
 */

import React, { useEffect, useState } from 'react';
import { Box, Typography, LinearProgress, Stack, Avatar } from '@mui/material';
import { motion } from 'framer-motion';

const EXECUTION_STEPS = [
  { label: 'Building content payload', emoji: '📦' },
  { label: 'Executing CGS workflow', emoji: '⚙️' },
  { label: 'Generating content with AI', emoji: '✨' },
  { label: 'Applying brand voice', emoji: '🎨' },
  { label: 'Finalizing content', emoji: '🎯' },
];

export const Step5ExecutionProgress: React.FC = () => {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const stepDuration = 2500; // 2.5 seconds per step
    const totalDuration = EXECUTION_STEPS.length * stepDuration;

    const interval = setInterval(() => {
      setProgress((prev) => {
        const newProgress = Math.min(prev + (100 / totalDuration) * 100, 100);

        // Update current step based on progress
        const newStepIndex = Math.min(
          Math.floor((newProgress / 100) * EXECUTION_STEPS.length),
          EXECUTION_STEPS.length - 1
        );
        setCurrentStepIndex(newStepIndex);

        if (newProgress >= 100) {
          clearInterval(interval);
        }

        return newProgress;
      });
    }, 100);

    return () => clearInterval(interval);
  }, []);

  const currentStep = EXECUTION_STEPS[currentStepIndex];
  const isComplete = progress >= 100;

  return (
    <Box
      sx={{
        width: '100%',
        maxWidth: 500,
        mx: 'auto',
        px: 3,
        textAlign: 'center',
      }}
    >
      <Stack spacing={4} alignItems="center">
        {/* Animated Icon */}
        <motion.div
          key={currentStepIndex}
          initial={{ scale: 0, rotate: -180 }}
          animate={{ scale: 1, rotate: 0 }}
          transition={{ type: 'spring', stiffness: 200, damping: 15 }}
        >
          <Avatar
            sx={{
              width: 80,
              height: 80,
              fontSize: '2.5rem',
              background: 'linear-gradient(135deg, #00D084 0%, #00A869 100%)',
            }}
          >
            {isComplete ? '🎉' : currentStep.emoji}
          </Avatar>
        </motion.div>

        {/* Current Step Text */}
        <motion.div
          key={`text-${currentStepIndex}`}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <Typography
            variant="h5"
            sx={{
              fontWeight: 700,
              color: 'text.primary',
              mb: 1,
            }}
          >
            {isComplete ? 'Content Generated!' : currentStep.label}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {isComplete
              ? 'Your content is ready!'
              : 'Our AI is crafting personalized content for you...'}
          </Typography>
        </motion.div>

        {/* Progress Bar */}
        <Box sx={{ width: '100%' }}>
          <LinearProgress
            variant="determinate"
            value={progress}
            sx={{
              height: 8,
              borderRadius: 4,
              backgroundColor: 'rgba(0, 208, 132, 0.1)',
              '& .MuiLinearProgress-bar': {
                background: 'linear-gradient(90deg, #00D084 0%, #00A869 100%)',
                borderRadius: 4,
              },
            }}
          />
          <Typography
            variant="caption"
            color="text.secondary"
            sx={{ display: 'block', mt: 1 }}
          >
            {Math.round(progress)}%
          </Typography>
        </Box>

        {/* Step Indicators */}
        <Stack direction="row" spacing={1}>
          {EXECUTION_STEPS.map((step, index) => (
            <Box
              key={index}
              sx={{
                width: 12,
                height: 12,
                borderRadius: '50%',
                backgroundColor:
                  index <= currentStepIndex
                    ? '#00D084'
                    : 'rgba(0, 208, 132, 0.2)',
                transition: 'all 0.3s ease',
              }}
            />
          ))}
        </Stack>
      </Stack>
    </Box>
  );
};

export default Step5ExecutionProgress;

