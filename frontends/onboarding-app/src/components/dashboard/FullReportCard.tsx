/**
 * FullReportCard Component
 * Displays full analytics report with expandable markdown viewer
 */

import React, { useState } from 'react';
import { Card, CardContent, Typography, Box, Stack, Button, Collapse, IconButton } from '@mui/material';
import { motion } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import DescriptionIcon from '@mui/icons-material/Description';
import DownloadIcon from '@mui/icons-material/Download';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import toast from 'react-hot-toast';

interface FullReportCardProps {
  report: string;
  companyName?: string;
}

export const FullReportCard: React.FC<FullReportCardProps> = ({ report, companyName }) => {
  const [expanded, setExpanded] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(report);
      toast.success('Report copied to clipboard!');
    } catch (err) {
      toast.error('Failed to copy report');
    }
  };

  const handleDownload = () => {
    const blob = new Blob([report], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${companyName || 'company'}-analytics-report.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success('Report downloaded!');
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.7 }}
    >
      <Card sx={{ height: '100%' }}>
        <CardContent>
          <Stack spacing={2}>
            {/* Header */}
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box display="flex" alignItems="center" gap={1}>
                <DescriptionIcon sx={{ fontSize: 28, color: 'primary.main' }} />
                <Typography variant="h6" fontWeight={600}>
                  Full Analytics Report
                </Typography>
              </Box>

              {/* Action Buttons */}
              <Box display="flex" gap={1}>
                <IconButton
                  size="small"
                  onClick={handleCopy}
                  sx={{
                    bgcolor: 'grey.100',
                    '&:hover': { bgcolor: 'grey.200' },
                  }}
                >
                  <ContentCopyIcon fontSize="small" />
                </IconButton>
                <IconButton
                  size="small"
                  onClick={handleDownload}
                  sx={{
                    bgcolor: 'grey.100',
                    '&:hover': { bgcolor: 'grey.200' },
                  }}
                >
                  <DownloadIcon fontSize="small" />
                </IconButton>
                <IconButton
                  size="small"
                  onClick={() => setExpanded(!expanded)}
                  sx={{
                    bgcolor: 'primary.main',
                    color: 'white',
                    '&:hover': { bgcolor: 'primary.dark' },
                  }}
                >
                  {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                </IconButton>
              </Box>
            </Box>

            {/* Preview (first 200 chars) */}
            {!expanded && (
              <Box
                sx={{
                  p: 2,
                  borderRadius: 2,
                  bgcolor: 'grey.50',
                  border: '1px solid',
                  borderColor: 'grey.200',
                }}
              >
                <Typography variant="body2" color="text.secondary">
                  {report.slice(0, 200)}...
                </Typography>
                <Button
                  size="small"
                  onClick={() => setExpanded(true)}
                  sx={{ mt: 1 }}
                  endIcon={<ExpandMoreIcon />}
                >
                  Read Full Report
                </Button>
              </Box>
            )}

            {/* Full Report (Expandable) */}
            <Collapse in={expanded}>
              <Box
                sx={{
                  p: 3,
                  borderRadius: 2,
                  bgcolor: 'grey.50',
                  border: '1px solid',
                  borderColor: 'grey.200',
                  maxHeight: 600,
                  overflowY: 'auto',
                  '& h1': {
                    fontSize: '1.5rem',
                    fontWeight: 700,
                    mt: 2,
                    mb: 1,
                    color: 'primary.main',
                  },
                  '& h2': {
                    fontSize: '1.25rem',
                    fontWeight: 600,
                    mt: 2,
                    mb: 1,
                    color: 'text.primary',
                  },
                  '& h3': {
                    fontSize: '1.1rem',
                    fontWeight: 600,
                    mt: 1.5,
                    mb: 0.5,
                    color: 'text.primary',
                  },
                  '& p': {
                    fontSize: '0.95rem',
                    lineHeight: 1.7,
                    mb: 1,
                    color: 'text.secondary',
                  },
                  '& ul, & ol': {
                    pl: 3,
                    mb: 1,
                  },
                  '& li': {
                    fontSize: '0.9rem',
                    lineHeight: 1.6,
                    mb: 0.5,
                    color: 'text.secondary',
                  },
                  '& code': {
                    px: 1,
                    py: 0.5,
                    borderRadius: 1,
                    bgcolor: 'grey.200',
                    fontSize: '0.85rem',
                    fontFamily: 'monospace',
                  },
                  '& pre': {
                    p: 2,
                    borderRadius: 2,
                    bgcolor: 'grey.900',
                    color: 'grey.100',
                    overflow: 'auto',
                    '& code': {
                      bgcolor: 'transparent',
                      color: 'inherit',
                    },
                  },
                  '& blockquote': {
                    pl: 2,
                    borderLeft: '4px solid',
                    borderColor: 'primary.main',
                    fontStyle: 'italic',
                    color: 'text.secondary',
                  },
                  '& hr': {
                    my: 2,
                    borderColor: 'grey.300',
                  },
                  '& a': {
                    color: 'primary.main',
                    textDecoration: 'none',
                    '&:hover': {
                      textDecoration: 'underline',
                    },
                  },
                }}
              >
                <ReactMarkdown>{report}</ReactMarkdown>
              </Box>

              <Button
                fullWidth
                size="small"
                onClick={() => setExpanded(false)}
                sx={{ mt: 1 }}
                endIcon={<ExpandLessIcon />}
              >
                Collapse Report
              </Button>
            </Collapse>
          </Stack>
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default FullReportCard;

