/**
 * Step3SnapshotReview Component
 * Minimal wizard-style snapshot review
 */

import React from 'react';
import { Box, Typography, Stack, Avatar, Chip } from '@mui/material';
import { motion } from 'framer-motion';
import { WizardButton } from '../wizard/WizardButton';
import type { CompanySnapshot } from '@/types/onboarding';

interface Step3SnapshotReviewProps {
  snapshot: CompanySnapshot;
  onContinue: () => void;
  isLoading?: boolean;
}

export const Step3SnapshotReview: React.FC<Step3SnapshotReviewProps> = ({
  snapshot,
  onContinue,
  isLoading = false,
}) => {
  return (
    <Box
      sx={{
        width: '100%',
        maxWidth: 600,
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
              width: 80,
              height: 80,
              fontSize: '2.5rem',
              background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
            }}
          >
            ✅
          </Avatar>
        </motion.div>

        {/* Header */}
        <Box sx={{ textAlign: 'center' }}>
          <Typography variant="h4" gutterBottom sx={{ fontWeight: 700 }}>
            Research Complete!
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Here's what we learned about {snapshot.company.name}
          </Typography>
        </Box>

        {/* Snapshot Summary Cards */}
        <Box
          sx={{
            width: '100%',
            p: 3,
            borderRadius: 3,
            backgroundColor: 'rgba(0, 208, 132, 0.05)',
            border: '1px solid rgba(0, 208, 132, 0.2)',
          }}
        >
          <Stack spacing={3}>
            {/* Company Overview */}
            <Box>
              <Typography
                variant="subtitle2"
                sx={{ fontWeight: 700, color: '#00D084', mb: 1 }}
              >
                🏢 Company
              </Typography>
              <Typography variant="body1" sx={{ fontWeight: 600, mb: 0.5 }}>
                {snapshot.company.name}
              </Typography>
              {snapshot.company.industry && (
                <Chip
                  label={snapshot.company.industry}
                  size="small"
                  sx={{
                    bgcolor: 'rgba(0, 208, 132, 0.1)',
                    color: '#00D084',
                    fontWeight: 600,
                    mb: 1,
                  }}
                />
              )}
              <Typography variant="body2" color="text.secondary">
                {snapshot.company.description}
              </Typography>
            </Box>

            {/* Target Audience */}
            <Box>
              <Typography
                variant="subtitle2"
                sx={{ fontWeight: 700, color: '#00D084', mb: 1 }}
              >
                👥 Target Audience
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {snapshot.audience.primary}
              </Typography>
            </Box>

            {/* Brand Voice */}
            <Box>
              <Typography
                variant="subtitle2"
                sx={{ fontWeight: 700, color: '#00D084', mb: 1 }}
              >
                🎨 Brand Voice
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {snapshot.voice.tone}
              </Typography>
            </Box>

            {/* Key Offerings */}
            {snapshot.company.key_offerings.length > 0 && (
              <Box>
                <Typography
                  variant="subtitle2"
                  sx={{ fontWeight: 700, color: '#00D084', mb: 1 }}
                >
                  ✨ Key Offerings
                </Typography>
                <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                  {snapshot.company.key_offerings.slice(0, 3).map((offering, index) => (
                    <Chip
                      key={index}
                      label={offering}
                      size="small"
                      variant="outlined"
                      sx={{ borderColor: 'rgba(0, 208, 132, 0.3)' }}
                    />
                  ))}
                  {snapshot.company.key_offerings.length > 3 && (
                    <Chip
                      label={`+${snapshot.company.key_offerings.length - 3} more`}
                      size="small"
                      variant="outlined"
                      sx={{ borderColor: 'rgba(0, 208, 132, 0.3)' }}
                    />
                  )}
                </Stack>
              </Box>
            )}
          </Stack>
        </Box>

        {/* Next Step Info */}
        <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center' }}>
          Next, we'll ask a few clarifying questions to tailor the content
        </Typography>

        {/* Continue Button */}
        <WizardButton onClick={onContinue} loading={isLoading} size="large">
          Continue to Questions
        </WizardButton>
      </Stack>
    </Box>
  );
};

export default Step3SnapshotReview;

