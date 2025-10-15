/**
 * Step6Results Component
 * Display generated content results
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
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  CheckCircle,
  ContentCopy,
  Download,
  Email,
  Refresh,
  Visibility,
} from '@mui/icons-material';
import toast from 'react-hot-toast';
import type { OnboardingSession } from '@/types/onboarding';

interface Step6ResultsProps {
  session: OnboardingSession;
  onStartNew: () => void;
}

export const Step6Results: React.FC<Step6ResultsProps> = ({
  session,
  onStartNew,
}) => {
  const metadata = session.metadata || {};
  const contentTitle = metadata.content_title || 'Content Generated';
  const contentPreview = metadata.content_preview || 'Your content is ready!';
  const wordCount = metadata.word_count || 0;
  const executionMetrics = metadata.execution_metrics || {};

  const handleCopyContent = () => {
    navigator.clipboard.writeText(contentPreview);
    toast.success('Content copied to clipboard!');
  };

  const handleDownload = () => {
    const blob = new Blob([contentPreview], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${contentTitle.replace(/\s+/g, '_')}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success('Content downloaded!');
  };

  return (
    <Box>
      {/* Success Header */}
      <Box sx={{ textAlign: 'center', mb: 4 }}>
        <CheckCircle sx={{ fontSize: 80, color: 'success.main', mb: 2 }} />
        <Typography variant="h3" gutterBottom sx={{ fontWeight: 700 }}>
          🎉 Success!
        </Typography>
        <Typography variant="h6" color="text.secondary" gutterBottom>
          Your content is ready
        </Typography>
        <Stack direction="row" spacing={1} justifyContent="center" sx={{ mt: 2 }}>
          <Chip
            icon={<CheckCircle />}
            label="Content Generated"
            color="success"
            variant="filled"
          />
          {session.delivery_status === 'sent' && (
            <Chip
              icon={<Email />}
              label="Email Sent"
              color="info"
              variant="outlined"
            />
          )}
        </Stack>
      </Box>

      {/* Content Preview */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 2 }}>
            <Typography variant="h5" fontWeight={600}>
              {contentTitle}
            </Typography>
            <Stack direction="row" spacing={1}>
              <Tooltip title="Copy to clipboard">
                <IconButton size="small" onClick={handleCopyContent} color="primary">
                  <ContentCopy />
                </IconButton>
              </Tooltip>
              <Tooltip title="Download">
                <IconButton size="small" onClick={handleDownload} color="primary">
                  <Download />
                </IconButton>
              </Tooltip>
            </Stack>
          </Box>

          <Divider sx={{ my: 2 }} />

          <Box
            sx={{
              maxHeight: 300,
              overflowY: 'auto',
              p: 2,
              backgroundColor: 'grey.50',
              borderRadius: 2,
              fontFamily: 'monospace',
              fontSize: '0.875rem',
              lineHeight: 1.6,
            }}
          >
            <Typography variant="body2" component="pre" sx={{ whiteSpace: 'pre-wrap', m: 0 }}>
              {contentPreview}
            </Typography>
          </Box>

          {/* Metadata */}
          <Stack direction="row" spacing={2} sx={{ mt: 2 }}>
            {wordCount > 0 && (
              <Chip
                label={`${wordCount} words`}
                size="small"
                variant="outlined"
              />
            )}
            {executionMetrics.duration_seconds && (
              <Chip
                label={`Generated in ${Math.round(executionMetrics.duration_seconds)}s`}
                size="small"
                variant="outlined"
              />
            )}
          </Stack>
        </CardContent>
      </Card>

      {/* Session Info */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" fontWeight={600} gutterBottom>
            Session Details
          </Typography>
          <Stack spacing={1}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="body2" color="text.secondary">
                Session ID:
              </Typography>
              <Typography variant="body2" fontFamily="monospace">
                {session.session_id.substring(0, 8)}...
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="body2" color="text.secondary">
                Company:
              </Typography>
              <Typography variant="body2" fontWeight={600}>
                {session.brand_name}
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="body2" color="text.secondary">
                Goal:
              </Typography>
              <Typography variant="body2">
                {session.goal.replace('_', ' ').toUpperCase()}
              </Typography>
            </Box>
            {session.cgs_run_id && (
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2" color="text.secondary">
                  CGS Run ID:
                </Typography>
                <Typography variant="body2" fontFamily="monospace">
                  {session.cgs_run_id.substring(0, 8)}...
                </Typography>
              </Box>
            )}
          </Stack>
        </CardContent>
      </Card>

      {/* Actions */}
      <Stack spacing={2}>
        <Button
          variant="contained"
          size="large"
          startIcon={<Refresh />}
          onClick={onStartNew}
          fullWidth
          sx={{
            py: 1.5,
            fontSize: '1rem',
            fontWeight: 600,
            background: 'linear-gradient(135deg, #00D084 0%, #00A869 100%)',
            '&:hover': {
              background: 'linear-gradient(135deg, #00A869 0%, #00804E 100%)',
            },
          }}
        >
          Start New Onboarding
        </Button>

        <Stack direction="row" spacing={2}>
          <Button
            variant="outlined"
            size="medium"
            startIcon={<ContentCopy />}
            onClick={handleCopyContent}
            fullWidth
          >
            Copy Content
          </Button>
          <Button
            variant="outlined"
            size="medium"
            startIcon={<Download />}
            onClick={handleDownload}
            fullWidth
          >
            Download
          </Button>
        </Stack>
      </Stack>

      {/* Footer */}
      <Box sx={{ mt: 4, p: 3, backgroundColor: 'success.50', borderRadius: 2, textAlign: 'center' }}>
        <Typography variant="body2" color="success.dark" fontWeight={600}>
          ✨ Thank you for using Fylle AI Onboarding!
        </Typography>
        <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 1 }}>
          Your content has been generated and is ready to use.
        </Typography>
      </Box>
    </Box>
  );
};

export default Step6Results;

