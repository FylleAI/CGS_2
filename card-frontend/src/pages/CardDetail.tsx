/**
 * Card Detail Page
 */

import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Chip,
  Stack,
  CircularProgress,
  Alert,
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import toast from 'react-hot-toast';
import { useCard, useDeleteCard } from '../hooks';

export const CardDetail: React.FC = () => {
  const { cardId } = useParams<{ cardId: string }>();
  const navigate = useNavigate();
  const { data: card, isLoading, error } = useCard(cardId);
  const { mutate: deleteCard } = useDeleteCard();

  if (isLoading) {
    return (
      <Container sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
        <CircularProgress />
      </Container>
    );
  }

  if (error || !card) {
    return (
      <Container sx={{ py: 4 }}>
        <Alert severity="error">
          {error?.message || 'Card not found'}
        </Alert>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/')}
          sx={{ mt: 2 }}
        >
          Back to Dashboard
        </Button>
      </Container>
    );
  }

  const handleDelete = () => {
    if (window.confirm('Are you sure you want to delete this card?')) {
      deleteCard(card.id, {
        onSuccess: () => {
          toast.success('Card deleted successfully');
          navigate('/');
        },
        onError: (err) => {
          toast.error(`Failed to delete card: ${err.message}`);
        },
      });
    }
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/')}
        >
          Back
        </Button>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<EditIcon />}
            onClick={() => navigate(`/cards/${card.id}/edit`)}
          >
            Edit
          </Button>
          <Button
            variant="outlined"
            color="error"
            startIcon={<DeleteIcon />}
            onClick={handleDelete}
          >
            Delete
          </Button>
        </Box>
      </Box>

      {/* Card Content */}
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 2 }}>
            <Typography variant="h4" component="h1" sx={{ fontWeight: 700 }}>
              {card.title}
            </Typography>
            <Chip
              label={card.card_type.toUpperCase()}
              color="primary"
              variant="outlined"
            />
          </Box>

          {card.notes && (
            <Typography variant="body1" sx={{ mb: 3, color: 'textSecondary' }}>
              {card.notes}
            </Typography>
          )}

          {/* Content Details */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
              Details
            </Typography>
            <Stack spacing={2}>
              {Object.entries(card.content).map(([key, value]) => (
                <Box key={key}>
                  <Typography variant="caption" color="textSecondary" sx={{ textTransform: 'capitalize' }}>
                    {key.replace(/_/g, ' ')}
                  </Typography>
                  <Typography variant="body2">
                    {typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value)}
                  </Typography>
                </Box>
              ))}
            </Stack>
          </Box>

          {/* Metadata */}
          <Box sx={{ pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
            <Typography variant="caption" color="textSecondary">
              Version {card.version} • Created {new Date(card.created_at).toLocaleDateString()}
            </Typography>
          </Box>
        </CardContent>
      </Card>
    </Container>
  );
};

