/**
 * WizardInput Component
 * Minimal styled input field
 */

import React from 'react';
import { TextField } from '@mui/material';
import { motion } from 'framer-motion';
import type { TextFieldProps } from '@mui/material';

export const WizardInput: React.FC<TextFieldProps> = (props) => {
  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
    >
      <TextField
        {...props}
        variant="outlined"
        fullWidth
        sx={{
          '& .MuiOutlinedInput-root': {
            borderRadius: 3,
            backgroundColor: '#f8f9fa',
            transition: 'all 0.3s ease',
            '& fieldset': {
              borderColor: 'transparent',
            },
            '&:hover': {
              backgroundColor: '#f0f1f3',
              '& fieldset': {
                borderColor: '#00D084',
              },
            },
            '&.Mui-focused': {
              backgroundColor: 'white',
              boxShadow: '0 0 0 3px rgba(0, 208, 132, 0.1)',
              '& fieldset': {
                borderColor: '#00D084',
                borderWidth: 2,
              },
            },
          },
          '& .MuiInputLabel-root': {
            fontWeight: 500,
            '&.Mui-focused': {
              color: '#00D084',
            },
          },
          ...props.sx,
        }}
      />
    </motion.div>
  );
};

export default WizardInput;

