/**
 * Card Grid Component - Display multiple cards
 */

import React from 'react';
import { Grid, Box, Typography, CircularProgress, Alert } from '@mui/material';
import { CardCard } from './CardCard';
import type { BaseCard } from '../types/card';

interface CardGridProps {
  cards: BaseCard[];
  isLoading?: boolean;
  error?: Error | null;
  onDelete?: (cardId: string) => void;
  onEdit?: (cardId: string) => void;
  emptyMessage?: string;
}

export const CardGrid: React.FC<CardGridProps> = ({
  cards,
  isLoading = false,
  error = null,
  onDelete,
  onEdit,
  emptyMessage = 'No cards found',
}) => {
  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error">
        Error loading cards: {error.message}
      </Alert>
    );
  }

  if (!cards || cards.length === 0) {
    return (
      <Box sx={{ textAlign: 'center', py: 4 }}>
        <Typography color="textSecondary">
          {emptyMessage}
        </Typography>
      </Box>
    );
  }

  return (
    <Grid container spacing={3}>
      {cards.map((card) => (
        <Grid item xs={12} sm={6} md={4} lg={3} key={card.id}>
          <CardCard
            card={card}
            onDelete={onDelete}
            onEdit={onEdit}
          />
        </Grid>
      ))}
    </Grid>
  );
};

