import React from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  Skeleton,
  Radio,
  FormControlLabel,
  RadioGroup,
} from '@mui/material';
import {
  Business as BusinessIcon,
  Psychology as PsychologyIcon,
  Storage as StorageIcon,
} from '@mui/icons-material';

import { useAppStore } from '../store/appStore';
import { ClientProfile } from '../types';

interface ClientSelectorProps {
  loading?: boolean;
}

const ClientSelector: React.FC<ClientSelectorProps> = ({ loading = false }) => {
  const { 
    availableClients, 
    selectedClient, 
    setSelectedClient 
  } = useAppStore();

  const handleClientSelect = (client: ClientProfile) => {
    setSelectedClient(client);
  };

  if (loading) {
    return (
      <Grid container spacing={2}>
        {[1, 2].map((i) => (
          <Grid item xs={12} sm={6} key={i}>
            <Card>
              <CardContent>
                <Skeleton variant="text" width="60%" height={24} />
                <Skeleton variant="text" width="100%" height={20} />
                <Skeleton variant="text" width="80%" height={20} />
                <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                  <Skeleton variant="rectangular" width={60} height={24} />
                  <Skeleton variant="rectangular" width={80} height={24} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    );
  }

  return (
    <Box>
      <RadioGroup
        value={selectedClient?.id || ''}
        onChange={(e) => {
          const client = availableClients.find(c => c.id === e.target.value);
          if (client) handleClientSelect(client);
        }}
      >
        <Grid container spacing={2}>
          {availableClients.map((client) => (
            <Grid item xs={12} sm={6} key={client.id}>
              <Card 
                sx={{ 
                  cursor: 'pointer',
                  border: selectedClient?.id === client.id ? 2 : 1,
                  borderColor: selectedClient?.id === client.id ? 'primary.main' : 'divider',
                  '&:hover': {
                    borderColor: 'primary.light',
                    boxShadow: 2,
                  }
                }}
                onClick={() => handleClientSelect(client)}
              >
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
                    <FormControlLabel
                      value={client.id}
                      control={<Radio />}
                      label=""
                      sx={{ m: 0 }}
                    />
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="h6" gutterBottom>
                        {client.displayName}
                      </Typography>
                      
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        {client.description}
                      </Typography>

                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                        <BusinessIcon fontSize="small" color="action" />
                        <Typography variant="caption">
                          {client.industry}
                        </Typography>
                      </Box>

                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                        <PsychologyIcon fontSize="small" color="action" />
                        <Typography variant="caption">
                          {client.targetAudience}
                        </Typography>
                      </Box>

                      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                        <Chip
                          size="small"
                          label={client.ragEnabled ? 'RAG Enabled' : 'RAG Disabled'}
                          color={client.ragEnabled ? 'success' : 'default'}
                          icon={<StorageIcon />}
                        />
                        {client.ragEnabled && (
                          <Chip
                            size="small"
                            label="Knowledge Base"
                            variant="outlined"
                            color="primary"
                          />
                        )}
                      </Box>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </RadioGroup>

      {selectedClient && (
        <Box sx={{ mt: 3, p: 2, backgroundColor: 'primary.50', borderRadius: 2 }}>
          <Typography variant="subtitle2" color="primary.main" gutterBottom>
            Selected: {selectedClient.displayName}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Brand Voice: {selectedClient.brandVoice}
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default ClientSelector;
