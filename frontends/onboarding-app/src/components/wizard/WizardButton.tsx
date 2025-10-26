/**
 * WizardButton Component
 * Animated button with loading state
 */

import React from 'react';
import { Button, CircularProgress } from '@mui/material';
import { motion } from 'framer-motion';
import type { ButtonProps } from '@mui/material';

interface WizardButtonProps extends Omit<ButtonProps, 'component'> {
  loading?: boolean;
  icon?: React.ReactNode;
}

export const WizardButton: React.FC<WizardButtonProps> = ({
  children,
  loading = false,
  icon,
  disabled,
  ...props
}) => {
  return (
    <motion.div
      whileHover={{ scale: disabled || loading ? 1 : 1.02 }}
      whileTap={{ scale: disabled || loading ? 1 : 0.98 }}
    >
      <Button
        {...props}
        disabled={disabled || loading}
        endIcon={loading ? <CircularProgress size={20} color="inherit" /> : icon}
        sx={{
          py: 1.5,
          px: 4,
          fontSize: '1rem',
          fontWeight: 600,
          borderRadius: 3,
          textTransform: 'none',
          background: 'linear-gradient(135deg, #00D084 0%, #00A869 100%)',
          color: 'white',
          boxShadow: '0 4px 14px rgba(0, 208, 132, 0.3)',
          '&:hover': {
            background: 'linear-gradient(135deg, #00A869 0%, #00804E 100%)',
            boxShadow: '0 6px 20px rgba(0, 208, 132, 0.4)',
          },
          '&:disabled': {
            background: '#e0e0e0',
            color: '#9e9e9e',
            boxShadow: 'none',
          },
          ...props.sx,
        }}
      >
        {children}
      </Button>
    </motion.div>
  );
};

export default WizardButton;

