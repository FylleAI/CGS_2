/**
 * OptimizationInsightsCard Component
 * Displays 4-section grid with optimization insights
 */

import React from 'react';
import { Card, CardContent, Typography, Box, Stack, Grid } from '@mui/material';
import { motion } from 'framer-motion';
import RecordVoiceOverIcon from '@mui/icons-material/RecordVoiceOver';
import SearchIcon from '@mui/icons-material/Search';
import MessageIcon from '@mui/icons-material/Message';
import ShareIcon from '@mui/icons-material/Share';

interface OptimizationArea {
  score?: number;
  recommendations?: string[];
  strengths?: string[];
  weaknesses?: string[];
}

interface OptimizationInsights {
  brand_voice?: OptimizationArea;
  seo?: OptimizationArea;
  messaging?: OptimizationArea;
  social_strategy?: OptimizationArea;
}

interface OptimizationInsightsCardProps {
  insights: OptimizationInsights;
}

const AREA_CONFIG = {
  brand_voice: {
    title: 'Brand Voice',
    icon: RecordVoiceOverIcon,
    color: '#8b5cf6',
  },
  seo: {
    title: 'SEO',
    icon: SearchIcon,
    color: '#3b82f6',
  },
  messaging: {
    title: 'Messaging',
    icon: MessageIcon,
    color: '#10b981',
  },
  social_strategy: {
    title: 'Social Strategy',
    icon: ShareIcon,
    color: '#f59e0b',
  },
};

export const OptimizationInsightsCard: React.FC<OptimizationInsightsCardProps> = ({
  insights,
}) => {
  const renderArea = (
    key: keyof OptimizationInsights,
    area: OptimizationArea | undefined,
    index: number
  ) => {
    const config = AREA_CONFIG[key];
    const Icon = config.icon;

    return (
      <Grid item xs={12} sm={6} key={key}>
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3, delay: 0.4 + index * 0.1 }}
        >
          <Box
            sx={{
              p: 2,
              borderRadius: 2,
              border: '2px solid',
              borderColor: config.color,
              bgcolor: 'background.paper',
              height: '100%',
              minHeight: 200,
            }}
          >
            <Stack spacing={1.5}>
              {/* Header */}
              <Box display="flex" alignItems="center" gap={1}>
                <Box
                  sx={{
                    width: 40,
                    height: 40,
                    borderRadius: 2,
                    bgcolor: config.color,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'white',
                  }}
                >
                  <Icon sx={{ fontSize: 24 }} />
                </Box>
                <Box flex={1}>
                  <Typography variant="subtitle1" fontWeight={600}>
                    {config.title}
                  </Typography>
                  {area?.score !== undefined && (
                    <Typography variant="caption" color="text.secondary">
                      Score: {area.score}/100
                    </Typography>
                  )}
                </Box>
              </Box>

              {/* Strengths */}
              {area?.strengths && area.strengths.length > 0 && (
                <Box>
                  <Typography variant="caption" fontWeight={600} color="success.main">
                    ✓ Strengths
                  </Typography>
                  <Stack spacing={0.5} mt={0.5}>
                    {area.strengths.slice(0, 2).map((strength, i) => (
                      <Typography
                        key={i}
                        variant="caption"
                        sx={{
                          display: 'block',
                          pl: 1,
                          borderLeft: '2px solid',
                          borderColor: 'success.light',
                        }}
                      >
                        {strength}
                      </Typography>
                    ))}
                  </Stack>
                </Box>
              )}

              {/* Recommendations */}
              {area?.recommendations && area.recommendations.length > 0 && (
                <Box>
                  <Typography variant="caption" fontWeight={600} color={config.color}>
                    → Recommendations
                  </Typography>
                  <Stack spacing={0.5} mt={0.5}>
                    {area.recommendations.slice(0, 3).map((rec, i) => (
                      <Typography
                        key={i}
                        variant="caption"
                        sx={{
                          display: 'block',
                          pl: 1,
                          borderLeft: '2px solid',
                          borderColor: config.color,
                        }}
                      >
                        {rec}
                      </Typography>
                    ))}
                  </Stack>
                </Box>
              )}

              {/* Weaknesses */}
              {area?.weaknesses && area.weaknesses.length > 0 && (
                <Box>
                  <Typography variant="caption" fontWeight={600} color="warning.main">
                    ⚠ Areas to Improve
                  </Typography>
                  <Stack spacing={0.5} mt={0.5}>
                    {area.weaknesses.slice(0, 2).map((weakness, i) => (
                      <Typography
                        key={i}
                        variant="caption"
                        sx={{
                          display: 'block',
                          pl: 1,
                          borderLeft: '2px solid',
                          borderColor: 'warning.light',
                        }}
                      >
                        {weakness}
                      </Typography>
                    ))}
                  </Stack>
                </Box>
              )}
            </Stack>
          </Box>
        </motion.div>
      </Grid>
    );
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.4 }}
    >
      <Card sx={{ height: '100%' }}>
        <CardContent>
          <Stack spacing={2}>
            {/* Header */}
            <Typography variant="h6" fontWeight={600}>
              Optimization Insights
            </Typography>

            {/* 4-Section Grid */}
            <Grid container spacing={2}>
              {renderArea('brand_voice', insights.brand_voice, 0)}
              {renderArea('seo', insights.seo, 1)}
              {renderArea('messaging', insights.messaging, 2)}
              {renderArea('social_strategy', insights.social_strategy, 3)}
            </Grid>
          </Stack>
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default OptimizationInsightsCard;

