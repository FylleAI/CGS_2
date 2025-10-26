/**
 * MetricsCard Component
 * Displays key metrics in a grid layout
 */

import React from 'react';
import { Card, CardContent, Typography, Box, Stack, Grid } from '@mui/material';
import { motion } from 'framer-motion';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import RemoveIcon from '@mui/icons-material/Remove';

interface Metric {
  label: string;
  value: string | number;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  icon?: React.ReactNode;
}

interface MetricsCardProps {
  metrics: Record<string, any>;
}

export const MetricsCard: React.FC<MetricsCardProps> = ({ metrics }) => {
  // Convert metrics object to array of Metric items
  const metricItems: Metric[] = Object.entries(metrics).map(([key, value]) => {
    // Handle different value types
    if (typeof value === 'object' && value !== null) {
      return {
        label: formatLabel(key),
        value: value.value || value.count || JSON.stringify(value),
        trend: value.trend,
        trendValue: value.trendValue,
      };
    }
    return {
      label: formatLabel(key),
      value: value,
    };
  });

  function formatLabel(key: string): string {
    return key
      .replace(/_/g, ' ')
      .replace(/\b\w/g, (char) => char.toUpperCase());
  }

  const getTrendIcon = (trend?: string) => {
    switch (trend) {
      case 'up':
        return <TrendingUpIcon sx={{ fontSize: 16, color: 'success.main' }} />;
      case 'down':
        return <TrendingDownIcon sx={{ fontSize: 16, color: 'error.main' }} />;
      case 'neutral':
        return <RemoveIcon sx={{ fontSize: 16, color: 'text.secondary' }} />;
      default:
        return null;
    }
  };

  const getTrendColor = (trend?: string) => {
    switch (trend) {
      case 'up':
        return 'success.main';
      case 'down':
        return 'error.main';
      default:
        return 'text.secondary';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.6 }}
    >
      <Card sx={{ height: '100%' }}>
        <CardContent>
          <Stack spacing={2}>
            {/* Header */}
            <Typography variant="h6" fontWeight={600}>
              Key Metrics
            </Typography>

            {/* Metrics Grid */}
            <Grid container spacing={2}>
              {metricItems.map((metric, index) => (
                <Grid item xs={6} sm={4} md={3} key={index}>
                  <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.3, delay: 0.7 + index * 0.05 }}
                  >
                    <Box
                      sx={{
                        p: 2,
                        borderRadius: 2,
                        bgcolor: 'grey.50',
                        border: '1px solid',
                        borderColor: 'grey.200',
                        height: '100%',
                        transition: 'all 0.2s',
                        '&:hover': {
                          borderColor: 'primary.main',
                          boxShadow: 1,
                        },
                      }}
                    >
                      <Stack spacing={0.5}>
                        {/* Label */}
                        <Typography
                          variant="caption"
                          color="text.secondary"
                          fontWeight={500}
                          sx={{ fontSize: '0.7rem' }}
                        >
                          {metric.label}
                        </Typography>

                        {/* Value */}
                        <Typography variant="h6" fontWeight={700} color="primary">
                          {metric.value}
                        </Typography>

                        {/* Trend */}
                        {metric.trend && (
                          <Box display="flex" alignItems="center" gap={0.5}>
                            {getTrendIcon(metric.trend)}
                            {metric.trendValue && (
                              <Typography
                                variant="caption"
                                color={getTrendColor(metric.trend)}
                                fontWeight={600}
                              >
                                {metric.trendValue}
                              </Typography>
                            )}
                          </Box>
                        )}
                      </Stack>
                    </Box>
                  </motion.div>
                </Grid>
              ))}
            </Grid>

            {/* Empty State */}
            {metricItems.length === 0 && (
              <Box
                sx={{
                  p: 4,
                  textAlign: 'center',
                  color: 'text.secondary',
                }}
              >
                <Typography variant="body2">No metrics available</Typography>
              </Box>
            )}
          </Stack>
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default MetricsCard;

