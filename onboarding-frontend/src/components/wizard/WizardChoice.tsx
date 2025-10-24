/**
 * WizardChoice Component
 * Interactive choice cards for selections
 */

import React from 'react';
import { Box, Typography, Paper } from '@mui/material';
import { motion } from 'framer-motion';
import { Check as CheckIcon } from '@mui/icons-material';

interface WizardChoiceProps {
  label: string;
  description?: string;
  icon?: React.ReactNode;
  selected?: boolean;
  onClick?: () => void;
  disabled?: boolean;
}

export const WizardChoice: React.FC<WizardChoiceProps> = ({
  label,
  description,
  icon,
  selected = false,
  onClick,
  disabled = false,
}) => {
  return (
    <motion.div
      whileHover={{ scale: disabled ? 1 : 1.02 }}
      whileTap={{ scale: disabled ? 1 : 0.98 }}
    >
      <Paper
        onClick={disabled ? undefined : onClick}
        elevation={0}
        sx={{
          p: 3,
          borderRadius: 3,
          cursor: disabled ? 'not-allowed' : 'pointer',
          border: '2px solid',
          borderColor: selected ? '#00D084' : 'transparent',
          backgroundColor: selected ? 'rgba(0, 208, 132, 0.05)' : '#f8f9fa',
          transition: 'all 0.3s ease',
          position: 'relative',
          opacity: disabled ? 0.5 : 1,
          '&:hover': {
            borderColor: disabled ? 'transparent' : selected ? '#00D084' : '#e0e0e0',
            backgroundColor: disabled ? '#f8f9fa' : selected ? 'rgba(0, 208, 132, 0.08)' : '#f0f1f3',
          },
        }}
      >
        {/* Check Icon */}
        {selected && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', stiffness: 300 }}
          >
            <Box
              sx={{
                position: 'absolute',
                top: 12,
                right: 12,
                width: 28,
                height: 28,
                borderRadius: '50%',
                backgroundColor: '#00D084',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <CheckIcon sx={{ fontSize: 18, color: 'white' }} />
            </Box>
          </motion.div>
        )}

        {/* Icon */}
        {icon && (
          <Box sx={{ fontSize: '2rem', mb: 1.5 }}>
            {icon}
          </Box>
        )}

        {/* Label */}
        <Typography
          variant="h6"
          sx={{
            fontWeight: 600,
            mb: description ? 0.5 : 0,
            color: selected ? '#00D084' : '#1a1a1a',
          }}
        >
          {label}
        </Typography>

        {/* Description */}
        {description && (
          <Typography
            variant="body2"
            sx={{
              color: 'text.secondary',
              lineHeight: 1.5,
            }}
          >
            {description}
          </Typography>
        )}
      </Paper>
    </motion.div>
  );
};

export default WizardChoice;

