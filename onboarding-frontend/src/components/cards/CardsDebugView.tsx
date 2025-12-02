/**
 * CardsDebugView - Minimal UI to visualize generated cards
 * 
 * Purpose: Debug/QA view to inspect card data quality
 * Shows all cards in a readable JSON-like format
 */

import React from 'react';
import { Box, Typography, Paper, Chip, Divider, Stack } from '@mui/material';

// Card type colors for visual distinction
const CARD_TYPE_COLORS: Record<string, string> = {
  product: '#4CAF50',
  target: '#2196F3',
  brand_voice: '#9C27B0',
  topic: '#FF9800',
  campaigns: '#E91E63',
  performance: '#00BCD4',
  competitor: '#F44336',
  feedback: '#795548',
};

interface Card {
  id: string;
  type: string;
  title: string;
  sessionId: string;
  [key: string]: any;
}

interface CardsOutput {
  sessionId: string;
  generatedAt: string;
  cards: Card[];
}

interface CardsDebugViewProps {
  cardsOutput: CardsOutput | null;
  onStartNew?: () => void;
}

// Render a single field with label
const Field: React.FC<{ label: string; value: any }> = ({ label, value }) => {
  if (value === null || value === undefined) return null;
  
  const renderValue = () => {
    if (Array.isArray(value)) {
      if (value.length === 0) return <em style={{ color: '#999' }}>empty array</em>;
      return (
        <Stack direction="row" flexWrap="wrap" gap={0.5} sx={{ mt: 0.5 }}>
          {value.map((item, i) => (
            <Chip 
              key={i} 
              label={typeof item === 'object' ? JSON.stringify(item) : String(item)} 
              size="small" 
              variant="outlined"
              sx={{ fontSize: '0.75rem' }}
            />
          ))}
        </Stack>
      );
    }
    if (typeof value === 'object') {
      return <pre style={{ margin: 0, fontSize: '0.75rem', whiteSpace: 'pre-wrap' }}>{JSON.stringify(value, null, 2)}</pre>;
    }
    return <span>{String(value)}</span>;
  };

  return (
    <Box sx={{ mb: 1 }}>
      <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>
        {label}:
      </Typography>
      <Box sx={{ ml: 1 }}>{renderValue()}</Box>
    </Box>
  );
};

// Render a single card
const CardView: React.FC<{ card: Card; index: number }> = ({ card, index }) => {
  const color = CARD_TYPE_COLORS[card.type] || '#666';
  
  // Fields to skip (already shown in header)
  const skipFields = ['id', 'type', 'title', 'sessionId'];
  
  return (
    <Paper 
      elevation={2} 
      sx={{ 
        p: 2, 
        mb: 2, 
        borderLeft: `4px solid ${color}`,
        backgroundColor: '#fafafa'
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
        <Chip 
          label={card.type.toUpperCase()} 
          size="small" 
          sx={{ backgroundColor: color, color: 'white', fontWeight: 700 }}
        />
        <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
          {card.title}
        </Typography>
        <Typography variant="caption" color="text.secondary" sx={{ ml: 'auto' }}>
          #{index + 1} | {card.id}
        </Typography>
      </Box>
      
      <Divider sx={{ my: 1 }} />
      
      {Object.entries(card)
        .filter(([key]) => !skipFields.includes(key))
        .map(([key, value]) => (
          <Field key={key} label={key} value={value} />
        ))}
    </Paper>
  );
};

export const CardsDebugView: React.FC<CardsDebugViewProps> = ({ cardsOutput, onStartNew }) => {
  if (!cardsOutput) {
    return (
      <Box sx={{ p: 4, textAlign: 'center' }}>
        <Typography variant="h6" color="error">⚠️ No cards_output available</Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          The API response did not include cards data
        </Typography>
      </Box>
    );
  }

  const { sessionId, generatedAt, cards } = cardsOutput;

  return (
    <Box sx={{ p: 3, maxWidth: 900, mx: 'auto' }}>
      {/* Header */}
      <Paper sx={{ p: 2, mb: 3, backgroundColor: '#e3f2fd' }}>
        <Typography variant="h5" sx={{ fontWeight: 700, mb: 1 }}>
          🎴 Generated Cards ({cards.length})
        </Typography>
        <Typography variant="body2" color="text.secondary">
          <strong>Session:</strong> {sessionId}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          <strong>Generated:</strong> {new Date(generatedAt).toLocaleString()}
        </Typography>
      </Paper>

      {/* Cards */}
      {cards.map((card, index) => (
        <CardView key={card.id} card={card} index={index} />
      ))}

      {/* Start New Button */}
      {onStartNew && (
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
      )}
    </Box>
  );
};

export default CardsDebugView;

