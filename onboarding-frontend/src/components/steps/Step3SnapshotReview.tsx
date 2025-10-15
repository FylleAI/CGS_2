/**
 * Step3SnapshotReview Component
 * Review company snapshot before proceeding
 */

import React from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Chip,
  Stack,
  Divider,
} from '@mui/material';
import {
  Business,
  People,
  RecordVoiceOver,
  Lightbulb,
  ArrowForward,
} from '@mui/icons-material';
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
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 700 }}>
          ✅ Research Complete!
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Here's what we learned about your company
        </Typography>
      </Box>

      {/* Company Info */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <Business color="primary" />
            <Typography variant="h6" fontWeight={600}>
              Company Overview
            </Typography>
          </Box>
          <Typography variant="h5" gutterBottom>
            {snapshot.company.name}
          </Typography>
          {snapshot.company.industry && (
            <Chip
              label={snapshot.company.industry}
              size="small"
              color="primary"
              variant="outlined"
              sx={{ mb: 2 }}
            />
          )}
          <Typography variant="body2" color="text.secondary" paragraph>
            {snapshot.company.description}
          </Typography>

          {snapshot.company.key_offerings.length > 0 && (
            <>
              <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                Key Offerings:
              </Typography>
              <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap sx={{ mb: 2 }}>
                {snapshot.company.key_offerings.map((offering, index) => (
                  <Chip key={index} label={offering} size="small" />
                ))}
              </Stack>
            </>
          )}

          {snapshot.company.differentiators.length > 0 && (
            <>
              <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                Differentiators:
              </Typography>
              <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                {snapshot.company.differentiators.map((diff, index) => (
                  <Chip key={index} label={diff} size="small" color="success" variant="outlined" />
                ))}
              </Stack>
            </>
          )}
        </CardContent>
      </Card>

      {/* Audience */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <People color="primary" />
            <Typography variant="h6" fontWeight={600}>
              Target Audience
            </Typography>
          </Box>
          <Typography variant="body2" color="text.secondary" paragraph>
            {snapshot.audience.primary}
          </Typography>

          {snapshot.audience.pain_points.length > 0 && (
            <>
              <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                Pain Points:
              </Typography>
              <ul style={{ margin: 0, paddingLeft: 20 }}>
                {snapshot.audience.pain_points.map((point, index) => (
                  <li key={index}>
                    <Typography variant="body2" color="text.secondary">
                      {point}
                    </Typography>
                  </li>
                ))}
              </ul>
            </>
          )}
        </CardContent>
      </Card>

      {/* Voice & Tone */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <RecordVoiceOver color="primary" />
            <Typography variant="h6" fontWeight={600}>
              Brand Voice
            </Typography>
          </Box>
          <Typography variant="body2" color="text.secondary" paragraph>
            <strong>Tone:</strong> {snapshot.voice.tone}
          </Typography>

          {snapshot.voice.style_guidelines.length > 0 && (
            <>
              <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                Style Guidelines:
              </Typography>
              <ul style={{ margin: 0, paddingLeft: 20 }}>
                {snapshot.voice.style_guidelines.map((guideline, index) => (
                  <li key={index}>
                    <Typography variant="body2" color="text.secondary">
                      {guideline}
                    </Typography>
                  </li>
                ))}
              </ul>
            </>
          )}
        </CardContent>
      </Card>

      {/* Insights (if available) */}
      {snapshot.insights && Object.keys(snapshot.insights).length > 0 && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <Lightbulb color="primary" />
              <Typography variant="h6" fontWeight={600}>
                Insights
              </Typography>
            </Box>
            {snapshot.insights.market_position && (
              <Typography variant="body2" color="text.secondary" paragraph>
                <strong>Market Position:</strong> {snapshot.insights.market_position}
              </Typography>
            )}
          </CardContent>
        </Card>
      )}

      <Divider sx={{ my: 3 }} />

      {/* Continue Button */}
      <Box sx={{ textAlign: 'center' }}>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Next, we'll ask a few clarifying questions to tailor the content
        </Typography>
        <Button
          variant="contained"
          size="large"
          onClick={onContinue}
          disabled={isLoading}
          endIcon={<ArrowForward />}
          sx={{
            px: 4,
            py: 1.5,
            fontSize: '1rem',
            fontWeight: 600,
          }}
        >
          Continue to Questions
        </Button>
      </Box>
    </Box>
  );
};

export default Step3SnapshotReview;

