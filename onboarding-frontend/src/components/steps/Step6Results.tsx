/**
 * Step6Results Component
 * Conditional rendering: Analytics Dashboard or Content Preview
 */

import React from 'react';
import { Box, Typography, Stack, Avatar, Chip, IconButton, Tooltip } from '@mui/material';
import { motion } from 'framer-motion';
import { ContentCopy, Download } from '@mui/icons-material';
import toast from 'react-hot-toast';
import { WizardButton } from '../wizard/WizardButton';
import { Step6Dashboard } from './Step6Dashboard';
import type { OnboardingSession, AnalyticsData } from '@/types/onboarding';
import { OnboardingGoal } from '@/types/onboarding';

interface Step6ResultsProps {
  session: OnboardingSession;
  onStartNew: () => void;
}

export const Step6Results: React.FC<Step6ResultsProps> = ({
  session,
  onStartNew,
}) => {
  // Check if this is an analytics session
  const isAnalytics = session.goal === OnboardingGoal.COMPANY_ANALYTICS;

  // Extract analytics data from cgs_response if available
  const analyticsData: AnalyticsData | null = React.useMemo(() => {
    if (!isAnalytics || !session.cgs_response) return null;

    const content = session.cgs_response.content;
    if (!content || !content.analytics_data) return null;

    return content.analytics_data as AnalyticsData;
  }, [isAnalytics, session.cgs_response]);

  // If analytics goal, render dashboard
  if (isAnalytics && analyticsData) {
    return (
      <Step6Dashboard
        analyticsData={analyticsData}
        companyName={session.brand_name}
        onReset={onStartNew}
      />
    );
  }

  // Otherwise, render content preview (legacy)
  const metadata = session.metadata || {};
  const contentTitle = metadata.content_title || 'Content Generated';
  const contentPreview = metadata.content_preview || session.cgs_response?.content?.body || 'Your content is ready!';
  const wordCount = metadata.word_count || 0;

  const handleCopyContent = () => {
    navigator.clipboard.writeText(contentPreview);
    toast.success('Content copied to clipboard!');
  };

  const handleDownload = () => {
    const blob = new Blob([contentPreview], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${contentTitle.replace(/\s+/g, '_')}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success('Content downloaded!');
  };

  return (
    <Box
      sx={{
        width: '100%',
        maxWidth: 700,
        mx: 'auto',
        px: 3,
      }}
    >
      <Stack spacing={4} alignItems="center">
        {/* Success Icon */}
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', stiffness: 200, damping: 15 }}
        >
          <Avatar
            sx={{
              width: 100,
              height: 100,
              fontSize: '3rem',
              background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
            }}
          >
            🎉
          </Avatar>
        </motion.div>

        {/* Header */}
        <Box sx={{ textAlign: 'center' }}>
          <Typography variant="h3" gutterBottom sx={{ fontWeight: 700 }}>
            Success!
          </Typography>
          <Typography variant="h6" color="text.secondary">
            Your content is ready
          </Typography>
        </Box>

        {/* Content Preview */}
        <Box
          sx={{
            width: '100%',
            p: 3,
            borderRadius: 3,
            backgroundColor: 'rgba(16, 185, 129, 0.05)',
            border: '1px solid rgba(16, 185, 129, 0.2)',
          }}
        >
          <Stack spacing={2}>
            {/* Title and Actions */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="h6" fontWeight={600}>
                {contentTitle}
              </Typography>
              <Stack direction="row" spacing={1}>
                <Tooltip title="Copy to clipboard">
                  <IconButton size="small" onClick={handleCopyContent} color="primary">
                    <ContentCopy fontSize="small" />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Download">
                  <IconButton size="small" onClick={handleDownload} color="primary">
                    <Download fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Stack>
            </Box>

            {/* Content */}
            <Box
              sx={{
                maxHeight: 300,
                overflowY: 'auto',
                p: 2,
                backgroundColor: 'white',
                borderRadius: 2,
                border: '1px solid rgba(0, 0, 0, 0.1)',
              }}
            >
              <Typography
                variant="body2"
                component="pre"
                sx={{
                  whiteSpace: 'pre-wrap',
                  m: 0,
                  fontFamily: 'inherit',
                  lineHeight: 1.6,
                }}
              >
                {contentPreview}
              </Typography>
            </Box>

            {/* Metadata */}
            <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
              {wordCount > 0 && (
                <Chip
                  label={`${wordCount} words`}
                  size="small"
                  sx={{
                    bgcolor: 'rgba(16, 185, 129, 0.1)',
                    color: '#059669',
                    fontWeight: 600,
                  }}
                />
              )}
              <Chip
                label={session.brand_name}
                size="small"
                sx={{
                  bgcolor: 'rgba(16, 185, 129, 0.1)',
                  color: '#059669',
                  fontWeight: 600,
                }}
              />
              <Chip
                label={session.goal.replace('_', ' ')}
                size="small"
                sx={{
                  bgcolor: 'rgba(16, 185, 129, 0.1)',
                  color: '#059669',
                  fontWeight: 600,
                }}
              />
            </Stack>
          </Stack>
        </Box>

        {/* Actions */}
        <Stack spacing={2} sx={{ width: '100%', maxWidth: 400 }}>
          <WizardButton onClick={onStartNew} size="large">
            Start New Onboarding
          </WizardButton>

          <Stack direction="row" spacing={2}>
            <WizardButton
              onClick={handleCopyContent}
              size="medium"
              sx={{
                flex: 1,
                background: 'transparent',
                color: '#00D084',
                border: '2px solid #00D084',
                '&:hover': {
                  background: 'rgba(0, 208, 132, 0.1)',
                },
              }}
            >
              Copy
            </WizardButton>
            <WizardButton
              onClick={handleDownload}
              size="medium"
              sx={{
                flex: 1,
                background: 'transparent',
                color: '#00D084',
                border: '2px solid #00D084',
                '&:hover': {
                  background: 'rgba(0, 208, 132, 0.1)',
                },
              }}
            >
              Download
            </WizardButton>
          </Stack>
        </Stack>

        {/* Thank You Message */}
        <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center' }}>
          ✨ Thank you for using Fylle AI Onboarding!
        </Typography>
      </Stack>
    </Box>
  );
};

export default Step6Results;

