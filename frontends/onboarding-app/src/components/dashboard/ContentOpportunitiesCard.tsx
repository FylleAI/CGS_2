/**
 * ContentOpportunitiesCard Component
 * Displays number of content opportunities with breakdown
 */

import React from 'react';
import { Card, CardContent, Typography, Box, Stack, Chip } from '@mui/material';
import { motion } from 'framer-motion';
import LightbulbIcon from '@mui/icons-material/Lightbulb';

interface ContentOpportunity {
  type: string;
  count: number;
  priority?: 'high' | 'medium' | 'low';
}

interface ContentOpportunitiesCardProps {
  opportunities: ContentOpportunity[];
  totalCount?: number;
}

export const ContentOpportunitiesCard: React.FC<ContentOpportunitiesCardProps> = ({
  opportunities,
  totalCount,
}) => {
  const total = totalCount || opportunities.reduce((sum, opp) => sum + opp.count, 0);

  const getPriorityColor = (priority?: string) => {
    switch (priority) {
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'info';
      default:
        return 'default';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.1 }}
    >
      <Card
        sx={{
          height: '100%',
          background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
          color: 'white',
        }}
      >
        <CardContent>
          <Stack spacing={2}>
            {/* Header */}
            <Box display="flex" alignItems="center" gap={1}>
              <LightbulbIcon sx={{ fontSize: 28 }} />
              <Typography variant="h6" fontWeight={600}>
                Content Opportunities
              </Typography>
            </Box>

            {/* Total Count */}
            <Box textAlign="center" py={2}>
              <Typography variant="h2" fontWeight={700}>
                {total}
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>
                Opportunities Identified
              </Typography>
            </Box>

            {/* Breakdown */}
            <Stack spacing={1.5}>
              {opportunities.map((opp, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: 0.2 + index * 0.1 }}
                >
                  <Box
                    sx={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      p: 1.5,
                      borderRadius: 2,
                      bgcolor: 'rgba(255, 255, 255, 0.15)',
                      backdropFilter: 'blur(10px)',
                    }}
                  >
                    <Box display="flex" alignItems="center" gap={1}>
                      <Typography variant="body2" fontWeight={500}>
                        {opp.type}
                      </Typography>
                      {opp.priority && (
                        <Chip
                          label={opp.priority}
                          size="small"
                          color={getPriorityColor(opp.priority) as any}
                          sx={{
                            height: 20,
                            fontSize: '0.7rem',
                            fontWeight: 600,
                          }}
                        />
                      )}
                    </Box>
                    <Box
                      sx={{
                        minWidth: 32,
                        height: 32,
                        borderRadius: '50%',
                        bgcolor: 'rgba(255, 255, 255, 0.3)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                    >
                      <Typography variant="body2" fontWeight={700}>
                        {opp.count}
                      </Typography>
                    </Box>
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

export default ContentOpportunitiesCard;

