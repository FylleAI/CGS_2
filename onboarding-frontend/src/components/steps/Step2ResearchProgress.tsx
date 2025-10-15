/**
 * Step2ResearchProgress Component
 * Animated research progress indicator
 */

import React, { useEffect, useState } from 'react';
import { Box, Typography, LinearProgress, Stack } from '@mui/material';
import { CheckCircle, HourglassEmpty } from '@mui/icons-material';
import { TypingIndicator } from '../common/TypingIndicator';

const RESEARCH_STEPS = [
  { label: 'Searching company information', duration: 2000 },
  { label: 'Analyzing industry data', duration: 2000 },
  { label: 'Synthesizing insights', duration: 2000 },
  { label: 'Generating questions', duration: 1500 },
];

export const Step2ResearchProgress: React.FC = () => {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const totalDuration = RESEARCH_STEPS.reduce((sum, step) => sum + step.duration, 0);
    let elapsed = 0;

    const interval = setInterval(() => {
      elapsed += 100;
      const newProgress = Math.min((elapsed / totalDuration) * 100, 100);
      setProgress(newProgress);

      // Update current step
      let cumulativeDuration = 0;
      for (let i = 0; i < RESEARCH_STEPS.length; i++) {
        cumulativeDuration += RESEARCH_STEPS[i].duration;
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
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 700 }}>
        🔍 Researching Your Company
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        This will take just a moment...
      </Typography>

      {/* Progress Bar */}
      <LinearProgress
        variant="determinate"
        value={progress}
        sx={{
          height: 8,
          borderRadius: 4,
          mb: 4,
          backgroundColor: 'grey.200',
          '& .MuiLinearProgress-bar': {
            background: 'linear-gradient(90deg, #00D084 0%, #00A869 100%)',
          },
        }}
      />

      {/* Steps */}
      <Stack spacing={2} sx={{ maxWidth: 400, mx: 'auto' }}>
        {RESEARCH_STEPS.map((step, index) => {
          const isCompleted = index < currentStepIndex;
          const isCurrent = index === currentStepIndex;

          return (
            <Box
              key={index}
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 2,
                p: 2,
                borderRadius: 2,
                backgroundColor: isCurrent ? 'primary.50' : 'transparent',
                transition: 'all 0.3s ease',
              }}
            >
              {isCompleted ? (
                <CheckCircle color="success" />
              ) : isCurrent ? (
                <HourglassEmpty color="primary" />
              ) : (
                <Box
                  sx={{
                    width: 24,
                    height: 24,
                    borderRadius: '50%',
                    border: '2px solid',
                    borderColor: 'grey.300',
                  }}
                />
              )}
              <Typography
                variant="body2"
                sx={{
                  flex: 1,
                  fontWeight: isCurrent ? 600 : 400,
                  color: isCompleted ? 'success.main' : isCurrent ? 'primary.main' : 'text.secondary',
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
      <Typography variant="caption" color="text.secondary" sx={{ mt: 4, display: 'block' }}>
        Powered by Perplexity AI & Gemini
      </Typography>
    </Box>
  );
};

export default Step2ResearchProgress;

