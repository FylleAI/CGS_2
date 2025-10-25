/**
 * Card Component - Display single card
 */

import React from 'react';
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  Button,
  Chip,
  Box,
  Stack,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import type { BaseCard } from '../types/card';

interface CardCardProps {
  card: BaseCard;
  onDelete?: (cardId: string) => void;
  onEdit?: (cardId: string) => void;
}

const CARD_TYPE_COLORS: Record<string, 'primary' | 'secondary' | 'success' | 'warning'> = {
  product: 'primary',
  persona: 'secondary',
  campaign: 'success',
  topic: 'warning',
};

export const CardCard: React.FC<CardCardProps> = ({ card, onDelete, onEdit }) => {
  const navigate = useNavigate();

  const handleView = () => {
    navigate(`/cards/${card.id}`);
  };

  const handleEdit = () => {
    if (onEdit) {
      onEdit(card.id);
    } else {
      navigate(`/cards/${card.id}/edit`);
    }
  };

  const handleDelete = () => {
    if (onDelete && window.confirm('Are you sure you want to delete this card?')) {
      onDelete(card.id);
    }
  };

  return (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardContent sx={{ flexGrow: 1 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 1 }}>
          <Typography variant="h6" component="div" sx={{ flex: 1 }}>
            {card.title}
          </Typography>
          <Chip
            label={card.card_type.toUpperCase()}
            color={CARD_TYPE_COLORS[card.card_type] || 'default'}
            size="small"
            variant="outlined"
          />
        </Box>

        <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
          {card.notes || 'No description'}
        </Typography>

        <Stack direction="row" spacing={1} sx={{ flexWrap: 'wrap', gap: 1 }}>
          {card.metrics && Object.entries(card.metrics).slice(0, 3).map(([key, value]) => (
            <Chip
              key={key}
              label={`${key}: ${value}`}
              size="small"
              variant="outlined"
            />
          ))}
        </Stack>

        <Typography variant="caption" color="textSecondary" sx={{ display: 'block', mt: 2 }}>
          v{card.version} • {new Date(card.created_at).toLocaleDateString()}
        </Typography>
      </CardContent>

      <CardActions sx={{ justifyContent: 'flex-end', gap: 1 }}>
        <Button
          size="small"
          startIcon={<OpenInNewIcon />}
          onClick={handleView}
        >
          View
        </Button>
        <Button
          size="small"
          startIcon={<EditIcon />}
          onClick={handleEdit}
          color="primary"
        >
          Edit
        </Button>
        <Button
          size="small"
          startIcon={<DeleteIcon />}
          onClick={handleDelete}
          color="error"
        >
          Delete
        </Button>
      </CardActions>
    </Card>
  );
};

