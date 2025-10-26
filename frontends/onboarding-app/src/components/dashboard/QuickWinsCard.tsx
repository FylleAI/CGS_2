/**
 * QuickWinsCard Component
 * Displays actionable quick wins with interactive checklist
 */

import React, { useState } from 'react';
import { Card, CardContent, Typography, Box, Stack, Checkbox, Chip } from '@mui/material';
import { motion } from 'framer-motion';
import FlashOnIcon from '@mui/icons-material/FlashOn';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';

interface QuickWin {
  title: string;
  description?: string;
  impact?: 'high' | 'medium' | 'low';
  effort?: 'low' | 'medium' | 'high';
}

interface QuickWinsCardProps {
  quickWins: QuickWin[];
}

export const QuickWinsCard: React.FC<QuickWinsCardProps> = ({ quickWins }) => {
  const [checkedItems, setCheckedItems] = useState<Set<number>>(new Set());

  const handleToggle = (index: number) => {
    setCheckedItems((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(index)) {
        newSet.delete(index);
      } else {
        newSet.add(index);
      }
      return newSet;
    });
  };

  const getImpactColor = (impact?: string) => {
    switch (impact) {
      case 'high':
        return '#10b981';
      case 'medium':
        return '#3b82f6';
      case 'low':
        return '#6b7280';
      default:
        return '#6b7280';
    }
  };

  const getEffortColor = (effort?: string) => {
    switch (effort) {
      case 'low':
        return '#10b981';
      case 'medium':
        return '#f59e0b';
      case 'high':
        return '#ef4444';
      default:
        return '#6b7280';
    }
  };

  const completionRate = quickWins.length > 0
    ? Math.round((checkedItems.size / quickWins.length) * 100)
    : 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.3 }}
    >
      <Card sx={{ height: '100%' }}>
        <CardContent>
          <Stack spacing={2}>
            {/* Header */}
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box display="flex" alignItems="center" gap={1}>
                <FlashOnIcon sx={{ fontSize: 28, color: '#f59e0b' }} />
                <Typography variant="h6" fontWeight={600}>
                  Quick Wins
                </Typography>
              </Box>
              <Chip
                icon={<CheckCircleIcon />}
                label={`${completionRate}% Complete`}
                color={completionRate === 100 ? 'success' : 'default'}
                size="small"
                sx={{ fontWeight: 600 }}
              />
            </Box>

            {/* Progress Bar */}
            <Box>
              <Box
                sx={{
                  width: '100%',
                  height: 8,
                  borderRadius: 4,
                  bgcolor: 'grey.200',
                  overflow: 'hidden',
                }}
              >
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${completionRate}%` }}
                  transition={{ duration: 0.5, delay: 0.5 }}
                  style={{
                    height: '100%',
                    background: 'linear-gradient(90deg, #10b981 0%, #3b82f6 100%)',
                  }}
                />
              </Box>
              <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
                {checkedItems.size} of {quickWins.length} completed
              </Typography>
            </Box>

            {/* Quick Wins List */}
            <Stack spacing={1.5} sx={{ maxHeight: 400, overflowY: 'auto' }}>
              {quickWins.map((win, index) => {
                const isChecked = checkedItems.has(index);

                return (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3, delay: 0.4 + index * 0.1 }}
                  >
                    <Box
                      sx={{
                        p: 1.5,
                        borderRadius: 2,
                        border: '1px solid',
                        borderColor: isChecked ? 'success.main' : 'grey.300',
                        bgcolor: isChecked ? 'success.50' : 'background.paper',
                        cursor: 'pointer',
                        transition: 'all 0.2s',
                        '&:hover': {
                          borderColor: 'primary.main',
                          boxShadow: 1,
                        },
                      }}
                      onClick={() => handleToggle(index)}
                    >
                      <Box display="flex" gap={1.5}>
                        <Checkbox
                          checked={isChecked}
                          onChange={() => handleToggle(index)}
                          sx={{ p: 0 }}
                        />
                        <Box flex={1}>
                          <Typography
                            variant="body2"
                            fontWeight={600}
                            sx={{
                              textDecoration: isChecked ? 'line-through' : 'none',
                              color: isChecked ? 'text.secondary' : 'text.primary',
                            }}
                          >
                            {win.title}
                          </Typography>
                          {win.description && (
                            <Typography
                              variant="caption"
                              color="text.secondary"
                              sx={{ display: 'block', mt: 0.5 }}
                            >
                              {win.description}
                            </Typography>
                          )}
                          {/* Impact & Effort Tags */}
                          <Box display="flex" gap={0.5} mt={1}>
                            {win.impact && (
                              <Chip
                                label={`${win.impact} impact`}
                                size="small"
                                sx={{
                                  height: 20,
                                  fontSize: '0.65rem',
                                  bgcolor: getImpactColor(win.impact),
                                  color: 'white',
                                  fontWeight: 600,
                                }}
                              />
                            )}
                            {win.effort && (
                              <Chip
                                label={`${win.effort} effort`}
                                size="small"
                                sx={{
                                  height: 20,
                                  fontSize: '0.65rem',
                                  bgcolor: getEffortColor(win.effort),
                                  color: 'white',
                                  fontWeight: 600,
                                }}
                              />
                            )}
                          </Box>
                        </Box>
                      </Box>
                    </Box>
                  </motion.div>
                );
              })}
            </Stack>
          </Stack>
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default QuickWinsCard;

