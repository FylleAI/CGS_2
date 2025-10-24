/**
 * WizardContainer Component
 * Minimal wizard container with smooth transitions
 */

import React from 'react';
import { Box, Container, Paper, LinearProgress } from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';

interface WizardContainerProps {
  children: React.ReactNode;
  currentStep: number;
  totalSteps: number;
  showProgress?: boolean;
}

export const WizardContainer: React.FC<WizardContainerProps> = ({
  children,
  currentStep,
  totalSteps,
  showProgress = true,
}) => {
  const progress = ((currentStep + 1) / totalSteps) * 100;

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
        py: 4,
      }}
    >
      <Container maxWidth="md">
        {/* Progress Bar */}
        {showProgress && (
          <Box sx={{ mb: 3 }}>
            <LinearProgress
              variant="determinate"
              value={progress}
              sx={{
                height: 6,
                borderRadius: 3,
                backgroundColor: 'rgba(0, 208, 132, 0.1)',
                '& .MuiLinearProgress-bar': {
                  borderRadius: 3,
                  background: 'linear-gradient(90deg, #00D084 0%, #00A869 100%)',
                },
              }}
            />
          </Box>
        )}

        {/* Main Content Card */}
        <Paper
          elevation={0}
          sx={{
            borderRadius: 4,
            overflow: 'hidden',
            backgroundColor: 'white',
            boxShadow: '0 20px 60px rgba(0, 0, 0, 0.08)',
          }}
        >
          <AnimatePresence mode="wait">
            <motion.div
              key={currentStep}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3, ease: 'easeInOut' }}
            >
              <Box sx={{ p: { xs: 3, sm: 5 } }}>
                {children}
              </Box>
            </motion.div>
          </AnimatePresence>
        </Paper>
      </Container>
    </Box>
  );
};

export default WizardContainer;

