/**
 * Header Component
 */

import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box, Container } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import AddIcon from '@mui/icons-material/Add';

export const Header: React.FC = () => {
  const navigate = useNavigate();

  return (
    <AppBar position="sticky" elevation={1}>
      <Container maxWidth="lg">
        <Toolbar disableGutters>
          <Typography
            variant="h6"
            component="div"
            sx={{
              flexGrow: 1,
              fontWeight: 700,
              cursor: 'pointer',
            }}
            onClick={() => navigate('/')}
          >
            📇 Card Manager
          </Typography>

          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              color="inherit"
              onClick={() => navigate('/')}
            >
              Dashboard
            </Button>
            <Button
              color="inherit"
              onClick={() => navigate('/relationships')}
            >
              Relationships
            </Button>
            <Button
              color="inherit"
              startIcon={<AddIcon />}
              onClick={() => navigate('/cards/new')}
              variant="outlined"
              sx={{ borderColor: 'rgba(255,255,255,0.5)', color: 'white' }}
            >
              New Card
            </Button>
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
};

