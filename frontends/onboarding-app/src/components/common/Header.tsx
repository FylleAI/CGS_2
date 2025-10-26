/**
 * Header Component
 * Application header with Fylle branding
 */

import React from 'react';
import { AppBar, Toolbar, Box, Typography, IconButton, Tooltip } from '@mui/material';
import { AutoAwesome as SparklesIcon, Refresh as RefreshIcon } from '@mui/icons-material';
import logoGreen from '@/assets/logos/fylle-logotipo-green.png';

interface HeaderProps {
  onReset?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onReset }) => {
  return (
    <AppBar
      position="static"
      elevation={0}
      sx={{
        backgroundColor: 'white',
        borderBottom: '1px solid',
        borderColor: 'divider',
      }}
    >
      <Toolbar sx={{ justifyContent: 'space-between', py: 1 }}>
        {/* Logo and Title */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <img
            src={logoGreen}
            alt="Fylle AI"
            style={{ height: 32, width: 'auto' }}
          />
          <Box>
            <Typography
              variant="h6"
              component="h1"
              sx={{
                fontWeight: 700,
                color: 'primary.main',
                lineHeight: 1.2,
              }}
            >
              Onboarding Assistant
            </Typography>
            <Typography
              variant="caption"
              sx={{
                color: 'text.secondary',
                display: 'block',
                lineHeight: 1,
              }}
            >
              Powered by AI
            </Typography>
          </Box>
        </Box>

        {/* Actions */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {onReset && (
            <Tooltip title="Start Over">
              <IconButton onClick={onReset} size="small" color="primary">
                <RefreshIcon />
              </IconButton>
            </Tooltip>
          )}
          <SparklesIcon sx={{ color: 'primary.main', fontSize: 28 }} />
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;

