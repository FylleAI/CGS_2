/**
 * App Component
 * Main application component
 */

import React from 'react';
import { ThemeProvider, CssBaseline, Box } from '@mui/material';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { theme } from './config/theme';
import { Header } from './components/common/Header';
import { OnboardingWizard } from './pages/OnboardingPage';
import { useOnboardingStore } from './store/onboardingStore';

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
    mutations: {
      retry: 1,
    },
  },
});

function App() {
  const reset = useOnboardingStore((state) => state.reset);

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Box sx={{ minHeight: '100vh', backgroundColor: 'background.default' }}>
          <Header onReset={reset} />
          <OnboardingWizard />
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
                primary: '#00D084',
                secondary: '#fff',
              },
            },
            error: {
              iconTheme: {
                primary: '#EF4444',
                secondary: '#fff',
              },
            },
          }}
        />
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;

