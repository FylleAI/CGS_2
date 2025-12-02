/**
 * Step6Results Component
 *
 * NEW: Shows generated cards from cards_output
 * Uses CardsDebugView for minimal/debug visualization
 */

import React from 'react';
import { Box, Typography } from '@mui/material';
import { CardsDebugView } from '../cards/CardsDebugView';
import type { OnboardingSession } from '@/types/onboarding';

interface Step6ResultsProps {
  session: OnboardingSession;
  onStartNew: () => void;
}

export const Step6Results: React.FC<Step6ResultsProps> = ({
  session,
  onStartNew,
}) => {
  // NEW: Get cards_output from session metadata
  const cardsOutput = session.metadata?.cards_output || null;

  console.log('🎴 Step6Results: cards_output =', cardsOutput);
  console.log('🎴 Step6Results: session.metadata =', session.metadata);

  // If no cards_output, show error with debug info
  if (!cardsOutput) {
    return (
      <Box sx={{ p: 4, maxWidth: 800, mx: 'auto' }}>
        <Typography variant="h5" sx={{ fontWeight: 700, mb: 2 }}>
          ⚠️ No Cards Generated
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
          The session completed but no cards_output was found in metadata.
        </Typography>

        {/* Debug info */}
        <Box sx={{
          p: 2,
          backgroundColor: '#f5f5f5',
          borderRadius: 1,
          fontFamily: 'monospace',
          fontSize: '0.8rem',
          overflow: 'auto'
        }}>
          <strong>Session ID:</strong> {session.session_id}<br/>
          <strong>State:</strong> {session.state}<br/>
          <strong>Metadata keys:</strong> {session.metadata ? Object.keys(session.metadata).join(', ') : 'none'}<br/>
          <pre>{JSON.stringify(session.metadata, null, 2)}</pre>
        </Box>

        <Box sx={{ textAlign: 'center', mt: 4 }}>
          <button
            onClick={onStartNew}
            style={{
              padding: '12px 32px',
              fontSize: '1rem',
              fontWeight: 600,
              backgroundColor: '#1976d2',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
            }}
          >
            Start New Onboarding
          </button>
        </Box>
      </Box>
    );
  }

  // Render cards using debug view
  return <CardsDebugView cardsOutput={cardsOutput} onStartNew={onStartNew} />;
};

export default Step6Results;

