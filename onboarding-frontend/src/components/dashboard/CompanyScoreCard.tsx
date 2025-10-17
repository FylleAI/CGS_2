/**
 * CompanyScoreCard Component
 * Displays company score with gauge chart (0-100)
 */

import React from 'react';
import { Card, CardContent, Typography, Box, Stack } from '@mui/material';
import { Gauge } from '@mui/x-charts/Gauge';
import { motion } from 'framer-motion';

interface CompanyScoreCardProps {
  score: number;
  label?: string;
  description?: string;
}

export const CompanyScoreCard: React.FC<CompanyScoreCardProps> = ({
  score,
  label = 'Company Score',
  description = 'Overall digital presence and content readiness',
}) => {
  // Determine color based on score
  const getScoreColor = (value: number): string => {
    if (value >= 80) return '#10b981'; // Green
    if (value >= 60) return '#3b82f6'; // Blue
    if (value >= 40) return '#f59e0b'; // Orange
    return '#ef4444'; // Red
  };

  const getScoreLabel = (value: number): string => {
    if (value >= 80) return 'Excellent';
    if (value >= 60) return 'Good';
    if (value >= 40) return 'Fair';
    return 'Needs Improvement';
  };

  const scoreColor = getScoreColor(score);
  const scoreLabel = getScoreLabel(score);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <Card
        sx={{
          height: '100%',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <CardContent>
          <Stack spacing={2} alignItems="center">
            {/* Title */}
            <Typography variant="h6" fontWeight={600} textAlign="center">
              {label}
            </Typography>

            {/* Gauge Chart */}
            <Box sx={{ position: 'relative', width: '100%', maxWidth: 200 }}>
              <Gauge
                value={score}
                valueMin={0}
                valueMax={100}
                startAngle={-110}
                endAngle={110}
                sx={{
                  width: '100%',
                  height: 180,
                  '& .MuiGauge-valueArc': {
                    fill: scoreColor,
                  },
                  '& .MuiGauge-referenceArc': {
                    fill: 'rgba(255, 255, 255, 0.2)',
                  },
                  '& .MuiGauge-valueText': {
                    fontSize: 40,
                    fontWeight: 700,
                    fill: 'white',
                  },
                }}
                text={({ value }) => `${value}`}
              />
            </Box>

            {/* Score Label */}
            <Box
              sx={{
                px: 2,
                py: 0.5,
                borderRadius: 2,
                bgcolor: scoreColor,
                color: 'white',
              }}
            >
              <Typography variant="body2" fontWeight={600}>
                {scoreLabel}
              </Typography>
            </Box>

            {/* Description */}
            <Typography
              variant="body2"
              textAlign="center"
              sx={{ opacity: 0.9, fontSize: '0.875rem' }}
            >
              {description}
            </Typography>
          </Stack>
        </CardContent>

        {/* Decorative circles */}
        <Box
          sx={{
            position: 'absolute',
            top: -50,
            right: -50,
            width: 150,
            height: 150,
            borderRadius: '50%',
            bgcolor: 'rgba(255, 255, 255, 0.1)',
          }}
        />
        <Box
          sx={{
            position: 'absolute',
            bottom: -30,
            left: -30,
            width: 100,
            height: 100,
            borderRadius: '50%',
            bgcolor: 'rgba(255, 255, 255, 0.1)',
          }}
        />
      </Card>
    </motion.div>
  );
};

export default CompanyScoreCard;

