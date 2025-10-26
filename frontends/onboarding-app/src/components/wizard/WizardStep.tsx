/**
 * WizardStep Component
 * Single step container with title and content
 */

import React from 'react';
import { Box, Typography, Avatar } from '@mui/material';
import { motion } from 'framer-motion';

interface WizardStepProps {
  title: string;
  subtitle?: string;
  icon?: React.ReactNode;
  children: React.ReactNode;
  centered?: boolean;
}

export const WizardStep: React.FC<WizardStepProps> = ({
  title,
  subtitle,
  icon,
  children,
  centered = false,
}) => {
  return (
    <Box sx={{ textAlign: centered ? 'center' : 'left' }}>
      {/* Icon/Avatar */}
      {icon && (
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.1, type: 'spring', stiffness: 200 }}
        >
          <Box sx={{ display: 'flex', justifyContent: centered ? 'center' : 'flex-start', mb: 3 }}>
            <Avatar
              sx={{
                width: 64,
                height: 64,
                background: 'linear-gradient(135deg, #00D084 0%, #00A869 100%)',
                fontSize: '2rem',
              }}
            >
              {icon}
            </Avatar>
          </Box>
        </motion.div>
      )}

      {/* Title */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <Typography
          variant="h4"
          sx={{
            fontWeight: 700,
            mb: 1,
            color: '#1a1a1a',
            fontSize: { xs: '1.75rem', sm: '2rem' },
          }}
        >
          {title}
        </Typography>
      </motion.div>

      {/* Subtitle */}
      {subtitle && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          <Typography
            variant="body1"
            sx={{
              color: 'text.secondary',
              mb: 4,
              fontSize: '1rem',
              lineHeight: 1.6,
            }}
          >
            {subtitle}
          </Typography>
        </motion.div>
      )}

      {/* Content */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        {children}
      </motion.div>
    </Box>
  );
};

export default WizardStep;

