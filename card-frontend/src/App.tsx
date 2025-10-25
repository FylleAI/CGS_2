/**
 * Main App Component
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, CssBaseline, Box } from '@mui/material';
import { QueryClientProvider, QueryClient } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { theme } from './config/theme';
import { Header } from './components/Header';
import { Dashboard } from './pages/Dashboard';
import { CardDetail } from './pages/CardDetail';

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000,
    },
    mutations: {
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <Box sx={{ minHeight: '100vh', backgroundColor: 'background.default' }}>
            <Header />
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/cards/:cardId" element={<CardDetail />} />
              {/* TODO: Add more routes */}
              {/* <Route path="/cards/new" element={<CardEditor />} /> */}
              {/* <Route path="/cards/:cardId/edit" element={<CardEditor />} /> */}
              {/* <Route path="/relationships" element={<RelationshipsView />} /> */}
            </Routes>
          </Box>

          {/* Toast Notifications */}
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
                borderRadius: '10px',
              },
              success: {
                iconTheme: {
                  primary: '#10b981',
                  secondary: '#fff',
                },
              },
              error: {
                iconTheme: {
                  primary: '#ef4444',
                  secondary: '#fff',
                },
              },
            }}
          />
        </Router>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;

