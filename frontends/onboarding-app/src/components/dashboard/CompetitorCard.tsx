/**
 * CompetitorCard Component
 * Displays competitor analysis with avatars and insights
 */

import React from 'react';
import { Card, CardContent, Typography, Box, Stack, Avatar, Chip } from '@mui/material';
import { motion } from 'framer-motion';
import BusinessIcon from '@mui/icons-material/Business';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';

interface Competitor {
  name: string;
  strength?: string;
  weakness?: string;
  threat_level?: 'high' | 'medium' | 'low';
}

interface CompetitorCardProps {
  competitors: Competitor[];
}

export const CompetitorCard: React.FC<CompetitorCardProps> = ({ competitors }) => {
  const getThreatColor = (level?: string) => {
    switch (level) {
      case 'high':
        return '#ef4444';
      case 'medium':
        return '#f59e0b';
      case 'low':
        return '#10b981';
      default:
        return '#6b7280';
    }
  };

  const getInitials = (name: string): string => {
    return name
      .split(' ')
      .map((word) => word[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.2 }}
    >
      <Card
        sx={{
          height: '100%',
          background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
          color: 'white',
        }}
      >
        <CardContent>
          <Stack spacing={2}>
            {/* Header */}
            <Box display="flex" alignItems="center" gap={1}>
              <BusinessIcon sx={{ fontSize: 28 }} />
              <Typography variant="h6" fontWeight={600}>
                Competitor Intelligence
              </Typography>
            </Box>

            {/* Competitor Count */}
            <Box
              sx={{
                p: 1.5,
                borderRadius: 2,
                bgcolor: 'rgba(255, 255, 255, 0.15)',
                textAlign: 'center',
              }}
            >
              <Typography variant="h4" fontWeight={700}>
                {competitors.length}
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>
                Key Competitors Analyzed
              </Typography>
            </Box>

            {/* Competitor List */}
            <Stack spacing={1.5} sx={{ maxHeight: 300, overflowY: 'auto' }}>
              {competitors.map((competitor, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: 0.3 + index * 0.1 }}
                >
                  <Box
                    sx={{
                      p: 1.5,
                      borderRadius: 2,
                      bgcolor: 'rgba(255, 255, 255, 0.15)',
                      backdropFilter: 'blur(10px)',
                    }}
                  >
                    <Box display="flex" alignItems="center" gap={1.5} mb={1}>
                      <Avatar
                        sx={{
                          bgcolor: getThreatColor(competitor.threat_level),
                          width: 40,
                          height: 40,
                          fontWeight: 700,
                        }}
                      >
                        {getInitials(competitor.name)}
                      </Avatar>
                      <Box flex={1}>
                        <Typography variant="body1" fontWeight={600}>
                          {competitor.name}
                        </Typography>
                        {competitor.threat_level && (
                          <Chip
                            label={`${competitor.threat_level} threat`}
                            size="small"
                            sx={{
                              mt: 0.5,
                              height: 20,
                              fontSize: '0.7rem',
                              bgcolor: getThreatColor(competitor.threat_level),
                              color: 'white',
                              fontWeight: 600,
                            }}
                          />
                        )}
                      </Box>
                    </Box>

                    {/* Strength/Weakness */}
                    {(competitor.strength || competitor.weakness) && (
                      <Stack spacing={0.5} sx={{ fontSize: '0.8rem', opacity: 0.95 }}>
                        {competitor.strength && (
                          <Box display="flex" gap={0.5}>
                            <TrendingUpIcon sx={{ fontSize: 16 }} />
                            <Typography variant="caption">
                              <strong>Strength:</strong> {competitor.strength}
                            </Typography>
                          </Box>
                        )}
                        {competitor.weakness && (
                          <Typography variant="caption">
                            <strong>Weakness:</strong> {competitor.weakness}
                          </Typography>
                        )}
                      </Stack>
                    )}
                  </Box>
                </motion.div>
              ))}
            </Stack>
          </Stack>
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default CompetitorCard;

