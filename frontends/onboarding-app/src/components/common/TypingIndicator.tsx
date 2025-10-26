/**
 * TypingIndicator Component
 * Animated typing indicator for conversational UI
 */

import React from 'react';
import { Box, keyframes } from '@mui/material';

const bounce = keyframes`
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-8px);
  }
`;

export const TypingIndicator: React.FC = () => {
  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        gap: 0.5,
        px: 2,
        py: 1.5,
        backgroundColor: 'grey.100',
        borderRadius: 3,
        width: 'fit-content',
      }}
    >
      {[0, 1, 2].map((i) => (
        <Box
          key={i}
          sx={{
            width: 8,
            height: 8,
            borderRadius: '50%',
            backgroundColor: 'grey.400',
            animation: `${bounce} 1.4s infinite ease-in-out`,
            animationDelay: `${i * 0.16}s`,
          }}
        />
      ))}
    </Box>
  );
};

export default TypingIndicator;

