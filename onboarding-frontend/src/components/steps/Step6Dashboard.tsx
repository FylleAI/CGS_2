/**
 * Step6Dashboard Component
 * Analytics dashboard with 8 card components
 */

import React from 'react';
import { Box, Grid, Stack, Typography, Button, CircularProgress } from '@mui/material';
import { motion } from 'framer-motion';
import RefreshIcon from '@mui/icons-material/Refresh';
import {
  CompanyScoreCard,
  ContentOpportunitiesCard,
  CompetitorCard,
  QuickWinsCard,
  OptimizationInsightsCard,
  ContentTypesChart,
  MetricsCard,
  FullReportCard,
} from '@/components/dashboard';
import type { AnalyticsData } from '@/types/onboarding';

interface Step6DashboardProps {
  analyticsData: AnalyticsData;
  companyName?: string;
  isLoading?: boolean;
  onReset?: () => void;
}

export const Step6Dashboard: React.FC<Step6DashboardProps> = ({
  analyticsData,
  companyName,
  isLoading = false,
  onReset,
}) => {
  if (isLoading) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: 400,
          gap: 2,
        }}
      >
        <CircularProgress size={60} />
        <Typography variant="h6" color="text.secondary">
          Generating Analytics Dashboard...
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ width: '100%', maxWidth: 1400, mx: 'auto' }}>
      <Stack spacing={3}>
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              mb: 2,
            }}
          >
            <Box>
              <Typography variant="h4" fontWeight={700} gutterBottom>
                Analytics Dashboard
              </Typography>
              {companyName && (
                <Typography variant="body1" color="text.secondary">
                  {companyName} • Strategic Insights & Recommendations
                </Typography>
              )}
            </Box>
            {onReset && (
              <Button
                variant="outlined"
                startIcon={<RefreshIcon />}
                onClick={onReset}
              >
                New Analysis
              </Button>
            )}
          </Box>
        </motion.div>

        {/* Dashboard Grid */}
        <Grid container spacing={3}>
          {/* Row 1: Score, Opportunities, Competitors */}
          <Grid item xs={12} md={4}>
            <CompanyScoreCard score={analyticsData.company_score} />
          </Grid>
          <Grid item xs={12} md={4}>
            <ContentOpportunitiesCard
              opportunities={analyticsData.content_opportunities}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <CompetitorCard competitors={analyticsData.competitors} />
          </Grid>

          {/* Row 2: Optimization Insights (Full Width) */}
          <Grid item xs={12}>
            <OptimizationInsightsCard
              insights={analyticsData.optimization_insights}
            />
          </Grid>

          {/* Row 3: Quick Wins, Content Types, Metrics */}
          <Grid item xs={12} md={4}>
            <QuickWinsCard quickWins={analyticsData.quick_wins} />
          </Grid>
          <Grid item xs={12} md={4}>
            <ContentTypesChart
              distribution={analyticsData.content_distribution}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <MetricsCard metrics={analyticsData.metrics} />
          </Grid>

          {/* Row 4: Full Report (Full Width) */}
          <Grid item xs={12}>
            <FullReportCard
              report={analyticsData.full_report}
              companyName={companyName}
            />
          </Grid>
        </Grid>

        {/* Footer Actions */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.4, delay: 0.8 }}
        >
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'center',
              gap: 2,
              pt: 2,
              pb: 4,
            }}
          >
            {onReset && (
              <Button
                variant="contained"
                size="large"
                startIcon={<RefreshIcon />}
                onClick={onReset}
              >
                Analyze Another Company
              </Button>
            )}
          </Box>
        </motion.div>
      </Stack>
    </Box>
  );
};

export default Step6Dashboard;

