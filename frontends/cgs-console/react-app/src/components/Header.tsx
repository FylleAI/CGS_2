import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  AutoAwesome as AutoAwesomeIcon,
  Settings as SettingsIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { useQuery } from 'react-query';
import apiService from '../services/api';

const Header: React.FC = () => {
  const { data: systemInfo } = useQuery(
    'systemInfo',
    apiService.getSystemInfo,
    {
      retry: false,
      refetchOnMount: false,
    }
  );

  return (
    <AppBar position="static" elevation={0} sx={{ backgroundColor: 'white', color: 'text.primary' }}>
      <Toolbar sx={{ justifyContent: 'space-between' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <AutoAwesomeIcon sx={{ fontSize: 32, color: 'primary.main' }} />
          <Box>
            <Typography variant="h5" component="h1" sx={{ fontWeight: 700, color: 'primary.main' }}>
              CGSRef
            </Typography>
            <Typography variant="caption" sx={{ color: 'text.secondary' }}>
              Clean Content Generation System
            </Typography>
          </Box>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          {systemInfo && (
            <>
              <Chip
                label={`v${systemInfo.version}`}
                size="small"
                variant="outlined"
                color="primary"
              />
              <Chip
                label={systemInfo.environment}
                size="small"
                color={systemInfo.environment === 'production' ? 'success' : 'warning'}
              />
            </>
          )}
          
          <Tooltip title="System Information">
            <IconButton size="small">
              <InfoIcon />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Settings">
            <IconButton size="small">
              <SettingsIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
