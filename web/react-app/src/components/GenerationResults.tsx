import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  LinearProgress,
  Alert,
  Divider,
  IconButton,
  Collapse,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Download as DownloadIcon,
  Visibility as VisibilityIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Timer as TimerIcon,
  TextFields as TextFieldsIcon,
  Save as SaveIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';

import { GenerationResponse } from '../types';
import WorkflowMetrics from './WorkflowMetrics';

interface GenerationResultsProps {
  result?: GenerationResponse;
  isGenerating?: boolean;
  progress?: number;
  onSave?: (result: GenerationResponse, filename: string) => void;
}

const GenerationResults: React.FC<GenerationResultsProps> = ({
  result,
  isGenerating = false,
  progress = 0,
  onSave,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [previewOpen, setPreviewOpen] = useState(false);
  const [saveDialogOpen, setSaveDialogOpen] = useState(false);
  const [filename, setFilename] = useState('');

  const imageSource = React.useMemo(() => {
    if (!result?.generatedImage) return null;
    const { imageUrl, imageData } = result.generatedImage;
    if (imageUrl) {
      return imageUrl;
    }
    if (imageData) {
      const trimmed = imageData.trim();
      if (trimmed.startsWith('data:')) {
        return trimmed;
      }
      return `data:image/png;base64,${trimmed}`;
    }
    return null;
  }, [result]);

  React.useEffect(() => {
    if (result) {
      setIsExpanded(true);
      // Generate default filename
      const timestamp = format(new Date(), 'yyyy-MM-dd_HH-mm');
      const title = result.title?.replace(/[^a-zA-Z0-9]/g, '_').substring(0, 30) || 'content';
      setFilename(`${title}_${timestamp}.md`);
    }
  }, [result]);

  const handleSave = () => {
    if (result && filename && onSave) {
      onSave(result, filename);
      setSaveDialogOpen(false);
    }
  };

  const handleDownload = () => {
    if (!result) return;
    
    const content = `# ${result.title}\n\n${result.body}`;
    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename || 'content.md';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  if (!isGenerating && !result) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Generation Results
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Results will appear here after content generation.
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Box>
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="h6">
              Generation Results
            </Typography>
            {result && (
              <IconButton
                onClick={() => setIsExpanded(!isExpanded)}
                size="small"
              >
                {isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              </IconButton>
            )}
          </Box>

          {/* Generation Progress */}
          {isGenerating && (
            <Box sx={{ mb: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <TimerIcon fontSize="small" color="primary" />
                <Typography variant="body2">
                  Generating content...
                </Typography>
              </Box>
              <LinearProgress 
                variant={progress > 0 ? "determinate" : "indeterminate"}
                value={progress}
                sx={{ mb: 1 }}
              />
              <Typography variant="caption" color="text.secondary">
                Complex workflows (Siebert Premium Newsletter) may take 3-6 minutes due to multi-agent processing and Perplexity research
              </Typography>
            </Box>
          )}

          {/* Generation Result */}
          {result && (
            <Box>
              {/* Status */}
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                {result.success ? (
                  <CheckCircleIcon color="success" />
                ) : (
                  <ErrorIcon color="error" />
                )}
                <Typography variant="body1" fontWeight="medium">
                  {result.success ? 'Generation Completed' : 'Generation Failed'}
                </Typography>
              </Box>

              {result.success ? (
                <>
                  {/* Quick Stats */}
                  <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
                    <Chip
                      icon={<TextFieldsIcon />}
                      label={`${result.wordCount} words`}
                      size="small"
                      color="primary"
                    />
                    <Chip
                      icon={<TimerIcon />}
                      label={`${result.generationTime}s`}
                      size="small"
                      color="secondary"
                    />
                    <Chip
                      label={result.contentType}
                      size="small"
                      variant="outlined"
                    />
                  </Box>

                  {imageSource && (
                    <Box
                      sx={{
                        mb: 2,
                        p: 2,
                        border: 1,
                        borderColor: 'grey.200',
                        borderRadius: 2,
                        backgroundColor: 'grey.50',
                      }}
                    >
                      <Typography variant="subtitle2" gutterBottom>
                        Generated Image
                      </Typography>
                      <Box
                        component="img"
                        src={imageSource}
                        alt="AI generated visual"
                        sx={{
                          maxWidth: '100%',
                          borderRadius: 1,
                          border: 1,
                          borderColor: 'grey.200',
                        }}
                      />
                      <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 1 }}>
                        Provider: {result.generatedImage?.provider || result.imageMetadata?.provider || 'unknown'}
                      </Typography>
                    </Box>
                  )}

                  {/* Actions */}
                  <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                    <Button
                      size="small"
                      startIcon={<VisibilityIcon />}
                      onClick={() => setPreviewOpen(true)}
                    >
                      Preview
                    </Button>
                    <Button
                      size="small"
                      startIcon={<DownloadIcon />}
                      onClick={handleDownload}
                    >
                      Download
                    </Button>
                    {onSave && (
                      <Button
                        size="small"
                        startIcon={<SaveIcon />}
                        onClick={() => setSaveDialogOpen(true)}
                      >
                        Save
                      </Button>
                    )}
                  </Box>

                  {/* Workflow Metrics */}
                  {result.workflowMetrics && (
                    <Box sx={{ mb: 2 }}>
                      <WorkflowMetrics metrics={result.workflowMetrics} />
                    </Box>
                  )}

                  {/* Content Preview */}
                  <Collapse in={isExpanded}>
                    <Divider sx={{ mb: 2 }} />
                    <Typography variant="subtitle2" gutterBottom>
                      Content Preview
                    </Typography>
                    <Box
                      sx={{
                        maxHeight: 300,
                        overflow: 'auto',
                        p: 2,
                        backgroundColor: 'grey.50',
                        borderRadius: 1,
                        border: 1,
                        borderColor: 'grey.200',
                      }}
                    >
                      <Typography variant="h6" gutterBottom>
                        {result.title}
                      </Typography>
                      <Typography
                        variant="body2"
                        sx={{
                          whiteSpace: 'pre-wrap',
                          fontFamily: 'monospace',
                          fontSize: '0.875rem',
                        }}
                      >
                        {result.body.substring(0, 500)}
                        {result.body.length > 500 && '...'}
                      </Typography>
                    </Box>
                  </Collapse>
                </>
              ) : (
                <Alert severity="error" sx={{ mt: 1 }}>
                  {result.errorMessage || 'An error occurred during generation'}
                </Alert>
              )}
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Full Preview Dialog */}
      <Dialog
        open={previewOpen}
        onClose={() => setPreviewOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Content Preview
        </DialogTitle>
        <DialogContent>
          {result && (
            <Box>
              <Typography variant="h5" gutterBottom>
                {result.title}
              </Typography>
              <Typography
                variant="body1"
                sx={{
                  whiteSpace: 'pre-wrap',
                  lineHeight: 1.6,
                }}
              >
                {result.body}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPreviewOpen(false)}>
            Close
          </Button>
          <Button onClick={handleDownload} variant="contained">
            Download
          </Button>
        </DialogActions>
      </Dialog>

      {/* Save Dialog */}
      <Dialog
        open={saveDialogOpen}
        onClose={() => setSaveDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Save Content
        </DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Filename"
            value={filename}
            onChange={(e) => setFilename(e.target.value)}
            helperText="Enter a filename for your content"
            sx={{ mt: 1 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSaveDialogOpen(false)}>
            Cancel
          </Button>
          <Button 
            onClick={handleSave} 
            variant="contained"
            disabled={!filename.trim()}
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default GenerationResults;
