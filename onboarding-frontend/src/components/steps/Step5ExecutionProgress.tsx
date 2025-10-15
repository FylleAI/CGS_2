/**
 * Step5ExecutionProgress Component
 * Content generation progress indicator
 */

import React, { useEffect, useState } from 'react';
import { Box, Typography, LinearProgress, Stack, Chip } from '@mui/material';
import { CheckCircle, HourglassEmpty, AutoAwesome } from '@mui/icons-material';
import { TypingIndicator } from '../common/TypingIndicator';

const EXECUTION_STEPS = [
  { label: 'Building content payload', duration: 1500 },
  { label: 'Executing CGS workflow', duration: 3000 },
  { label: 'Generating content with AI', duration: 4000 },
  { label: 'Applying brand voice', duration: 2000 },
  { label: 'Finalizing content', duration: 1500 },
];

export const Step5ExecutionProgress: React.FC = () => {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const totalDuration = EXECUTION_STEPS.reduce((sum, step) => sum + step.duration, 0);
    let elapsed = 0;

    const interval = setInterval(() => {
      elapsed += 100;
      const newProgress = Math.min((elapsed / totalDuration) * 100, 100);
      setProgress(newProgress);

      // Update current step
      let cumulativeDuration = 0;
      for (let i = 0; i < EXECUTION_STEPS.length; i++) {
        cumulativeDuration += EXECUTION_STEPS[i].duration;
        if (elapsed < cumulativeDuration) {
          setCurrentStepIndex(i);
          break;
        }
      }

      if (elapsed >= totalDuration) {
        clearInterval(interval);
      }
    }, 100);

    return () => clearInterval(interval);
  }, []);

  return (
    <Box sx={{ textAlign: 'center', py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 2 }}>
        <AutoAwesome sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 700 }}>
          ⚙️ Generating Your Content
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 1 }}>
          Our AI is crafting personalized content for you
        </Typography>
        <Chip
          label="Estimated time: 2-3 minutes"
          size="small"
          color="info"
          variant="outlined"
        />
      </Box>

      {/* Progress Bar */}
      <LinearProgress
        variant="determinate"
        value={progress}
        sx={{
          height: 10,
          borderRadius: 5,
          mb: 4,
          mt: 3,
          backgroundColor: 'grey.200',
          '& .MuiLinearProgress-bar': {
            background: 'linear-gradient(90deg, #00D084 0%, #00A869 50%, #6366F1 100%)',
            borderRadius: 5,
          },
        }}
      />

      {/* Progress Percentage */}
      <Typography variant="h5" fontWeight={700} color="primary.main" sx={{ mb: 4 }}>
        {Math.round(progress)}%
      </Typography>

      {/* Steps */}
      <Stack spacing={2} sx={{ maxWidth: 500, mx: 'auto' }}>
        {EXECUTION_STEPS.map((step, index) => {
          const isCompleted = index < currentStepIndex;
          const isCurrent = index === currentStepIndex;

          return (
            <Box
              key={index}
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 2,
                p: 2.5,
                borderRadius: 3,
                backgroundColor: isCurrent
                  ? 'rgba(0, 208, 132, 0.1)'
                  : isCompleted
                  ? 'rgba(16, 185, 129, 0.05)'
                  : 'transparent',
                border: '1px solid',
                borderColor: isCurrent
                  ? 'primary.main'
                  : isCompleted
                  ? 'success.light'
                  : 'grey.200',
                transition: 'all 0.3s ease',
                transform: isCurrent ? 'scale(1.02)' : 'scale(1)',
              }}
            >
              {isCompleted ? (
                <CheckCircle sx={{ color: 'success.main', fontSize: 28 }} />
              ) : isCurrent ? (
                <HourglassEmpty sx={{ color: 'primary.main', fontSize: 28 }} />
              ) : (
                <Box
                  sx={{
                    width: 28,
                    height: 28,
                    borderRadius: '50%',
                    border: '2px solid',
                    borderColor: 'grey.300',
                  }}
                />
              )}
              <Typography
                variant="body1"
                sx={{
                  flex: 1,
                  fontWeight: isCurrent ? 600 : 400,
                  color: isCompleted
                    ? 'success.main'
                    : isCurrent
                    ? 'primary.main'
                    : 'text.secondary',
                }}
              >
                {step.label}
              </Typography>
              {isCurrent && <TypingIndicator />}
            </Box>
          );
        })}
      </Stack>

      {/* Footer */}
      <Box sx={{ mt: 4, p: 3, backgroundColor: 'grey.50', borderRadius: 2 }}>
        <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
          💡 Did you know?
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Our AI analyzes your company snapshot and applies your brand voice to create
          authentic, engaging content tailored to your audience.
        </Typography>
      </Box>
    </Box>
  );
};

export default Step5ExecutionProgress;

