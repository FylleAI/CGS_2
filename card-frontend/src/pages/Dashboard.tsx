/**
 * Dashboard Page - Main card overview
 */

import React, { useState } from 'react';
import {
  Container,
  Box,
  Typography,
  Tabs,
  Tab,
  Button,
  Alert,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import AddIcon from '@mui/icons-material/Add';
import toast from 'react-hot-toast';
import { CardGrid } from '../components/CardGrid';
import { useCards, useDeleteCard, useCardsByType } from '../hooks';
import type { CardType } from '../types/card';

const CARD_TYPES: CardType[] = ['product', 'persona', 'campaign', 'topic'];

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<CardType>('product');
  
  const { data: allCards, isLoading, error } = useCards();
  const { mutate: deleteCard, isPending: isDeleting } = useDeleteCard();
  
  const cardsByType = allCards?.filter(card => card.card_type === activeTab) || [];

  const handleDelete = (cardId: string) => {
    deleteCard(cardId, {
      onSuccess: () => {
        toast.success('Card deleted successfully');
      },
      onError: (err) => {
        toast.error(`Failed to delete card: ${err.message}`);
      },
    });
  };

  const handleEdit = (cardId: string) => {
    navigate(`/cards/${cardId}/edit`);
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" component="h1" sx={{ fontWeight: 700, mb: 1 }}>
            📇 Card Dashboard
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Manage your company cards: Product, Persona, Campaign, and Topics
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => navigate('/cards/new')}
        >
          New Card
        </Button>
      </Box>

      {/* Stats */}
      {allCards && (
        <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: 2, mb: 4 }}>
          {CARD_TYPES.map(type => (
            <Box
              key={type}
              sx={{
                p: 2,
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 1,
                textAlign: 'center',
              }}
            >
              <Typography variant="h6" sx={{ fontWeight: 700 }}>
                {allCards.filter(c => c.card_type === type).length}
              </Typography>
              <Typography variant="caption" color="textSecondary">
                {type.charAt(0).toUpperCase() + type.slice(1)}
              </Typography>
            </Box>
          ))}
        </Box>
      )}

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={(_, value) => setActiveTab(value)}
          aria-label="card types"
        >
          {CARD_TYPES.map(type => (
            <Tab
              key={type}
              label={type.charAt(0).toUpperCase() + type.slice(1)}
              value={type}
            />
          ))}
        </Tabs>
      </Box>

      {/* Cards Grid */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          Error loading cards: {error.message}
        </Alert>
      )}

      <CardGrid
        cards={cardsByType}
        isLoading={isLoading || isDeleting}
        error={error}
        onDelete={handleDelete}
        onEdit={handleEdit}
        emptyMessage={`No ${activeTab} cards yet. Create one to get started!`}
      />
    </Container>
  );
};

