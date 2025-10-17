/**
 * ContentTypesChart Component
 * Displays content distribution with bar/pie chart
 */

import React, { useState } from 'react';
import { Card, CardContent, Typography, Box, Stack, ToggleButtonGroup, ToggleButton } from '@mui/material';
import { BarChart } from '@mui/x-charts/BarChart';
import { PieChart } from '@mui/x-charts/PieChart';
import { motion } from 'framer-motion';
import BarChartIcon from '@mui/icons-material/BarChart';
import PieChartIcon from '@mui/icons-material/PieChart';

interface ContentDistribution {
  [key: string]: number;
}

interface ContentTypesChartProps {
  distribution: ContentDistribution;
}

export const ContentTypesChart: React.FC<ContentTypesChartProps> = ({ distribution }) => {
  const [chartType, setChartType] = useState<'bar' | 'pie'>('bar');

  // Prepare data for charts
  const contentTypes = Object.keys(distribution);
  const values = Object.values(distribution);

  const barData = contentTypes.map((type, index) => ({
    type,
    value: values[index],
  }));

  const pieData = contentTypes.map((type, index) => ({
    id: index,
    value: values[index],
    label: type,
  }));

  const colors = [
    '#8b5cf6',
    '#3b82f6',
    '#10b981',
    '#f59e0b',
    '#ef4444',
    '#ec4899',
    '#06b6d4',
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.5 }}
    >
      <Card sx={{ height: '100%' }}>
        <CardContent>
          <Stack spacing={2}>
            {/* Header with Chart Type Toggle */}
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Typography variant="h6" fontWeight={600}>
                Content Distribution
              </Typography>
              <ToggleButtonGroup
                value={chartType}
                exclusive
                onChange={(_, newType) => newType && setChartType(newType)}
                size="small"
              >
                <ToggleButton value="bar" aria-label="bar chart">
                  <BarChartIcon fontSize="small" />
                </ToggleButton>
                <ToggleButton value="pie" aria-label="pie chart">
                  <PieChartIcon fontSize="small" />
                </ToggleButton>
              </ToggleButtonGroup>
            </Box>

            {/* Chart */}
            <Box sx={{ width: '100%', height: 300 }}>
              {chartType === 'bar' ? (
                <BarChart
                  dataset={barData}
                  xAxis={[
                    {
                      scaleType: 'band',
                      dataKey: 'type',
                      tickLabelStyle: {
                        angle: -45,
                        textAnchor: 'end',
                        fontSize: 11,
                      },
                    },
                  ]}
                  series={[
                    {
                      dataKey: 'value',
                      label: 'Opportunities',
                      color: '#8b5cf6',
                    },
                  ]}
                  height={300}
                  margin={{ top: 20, right: 20, bottom: 80, left: 40 }}
                />
              ) : (
                <PieChart
                  series={[
                    {
                      data: pieData,
                      highlightScope: { faded: 'global', highlighted: 'item' },
                      faded: { innerRadius: 30, additionalRadius: -30, color: 'gray' },
                      innerRadius: 30,
                      outerRadius: 100,
                      paddingAngle: 2,
                      cornerRadius: 5,
                    },
                  ]}
                  colors={colors}
                  height={300}
                  slotProps={{
                    legend: {
                      direction: 'column',
                      position: { vertical: 'middle', horizontal: 'right' },
                      padding: 0,
                      itemMarkWidth: 12,
                      itemMarkHeight: 12,
                      markGap: 5,
                      itemGap: 8,
                      labelStyle: {
                        fontSize: 11,
                      },
                    },
                  }}
                />
              )}
            </Box>

            {/* Summary Stats */}
            <Box
              sx={{
                p: 1.5,
                borderRadius: 2,
                bgcolor: 'grey.100',
                display: 'flex',
                justifyContent: 'space-around',
              }}
            >
              <Box textAlign="center">
                <Typography variant="h6" fontWeight={700} color="primary">
                  {contentTypes.length}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Content Types
                </Typography>
              </Box>
              <Box textAlign="center">
                <Typography variant="h6" fontWeight={700} color="primary">
                  {values.reduce((sum, val) => sum + val, 0)}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Total Opportunities
                </Typography>
              </Box>
            </Box>
          </Stack>
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default ContentTypesChart;

