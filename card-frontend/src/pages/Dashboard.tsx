/**
 * Dashboard Page - Main card overview
 */

import React, { useState, useEffect } from 'react';
import {
  Container,
  Box,
  Typography,
  Tabs,
  Tab,
  Button,
  Alert,
  Switch,
  FormControlLabel,
  TextField,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import AddIcon from '@mui/icons-material/Add';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import toast from 'react-hot-toast';
import { CardGrid } from '../components/CardGrid';
import { useCards, useDeleteCard, useCardsByType } from '../hooks';
import { cardApi } from '../services/cardApi';
import type { CardType } from '../types/card';

const CARD_TYPES: CardType[] = ['product', 'persona', 'campaign', 'topic'];

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<CardType>('product');
  const [isSuperAdmin, setIsSuperAdmin] = useState(false);
  const [customTenantId, setCustomTenantId] = useState('');

  useEffect(() => {
    setIsSuperAdmin(cardApi.isSuperAdmin());
  }, []);

  const { data: allCards, isLoading, error } = useCards();
  const { mutate: deleteCard, isPending: isDeleting } = useDeleteCard();

  const handleSuperAdminToggle = (event: React.ChangeEvent<HTMLInputElement>) => {
    const enabled = event.target.checked;
    setIsSuperAdmin(enabled);
    cardApi.setSuperAdminMode(enabled);
    if (enabled) {
      toast.success('Super Admin mode enabled - viewing all profiles');
    } else {
      toast.success('Super Admin mode disabled');
    }
    // Refresh data
    window.location.reload();
  };

  const handleSetTenantId = () => {
    if (customTenantId.trim()) {
      localStorage.setItem('tenant_id', customTenantId);
      toast.success(`Tenant ID set to: ${customTenantId}`);
      window.location.reload();
    }
  };
  
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
            {isSuperAdmin && (
              <AdminPanelSettingsIcon sx={{ ml: 1, color: 'warning.main', verticalAlign: 'middle' }} />
            )}
          </Typography>
          <Typography variant="body2" color="textSecondary">
            {isSuperAdmin
              ? '🔓 Super Admin Mode - Viewing all profiles'
              : 'Manage your company cards: Product, Persona, Campaign, and Topics'
            }
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

      {/* Super Admin Controls */}
      <Box sx={{ mb: 4, p: 2, bgcolor: 'background.paper', border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <FormControlLabel
            control={
              <Switch
                checked={isSuperAdmin}
                onChange={handleSuperAdminToggle}
              />
            }
            label="Super Admin Mode (View All Profiles)"
          />
        </Box>

        {isSuperAdmin && (
          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
            <TextField
              size="small"
              placeholder="Enter tenant ID (email)"
              value={customTenantId}
              onChange={(e) => setCustomTenantId(e.target.value)}
              sx={{ flex: 1 }}
            />
            <Button
              variant="outlined"
              onClick={handleSetTenantId}
            >
              Set Tenant
            </Button>
          </Box>
        )}
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

