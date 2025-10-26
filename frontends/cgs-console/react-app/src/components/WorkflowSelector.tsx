import React from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  Skeleton,
  Radio,
  FormControlLabel,
  RadioGroup,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import {
  Article as ArticleIcon,
  Email as EmailIcon,
  AutoAwesome as AutoAwesomeIcon,
} from '@mui/icons-material';

import { useAppStore } from '../store/appStore';
import { WorkflowType } from '../types';

interface WorkflowSelectorProps {
  loading?: boolean;
}

const getWorkflowIcon = (category: string) => {
  switch (category) {
    case 'article':
      return <ArticleIcon />;
    case 'newsletter':
      return <EmailIcon />;
    default:
      return <AutoAwesomeIcon />;
  }
};

const getWorkflowColor = (category: string) => {
  switch (category) {
    case 'article':
      return 'primary';
    case 'newsletter':
      return 'secondary';
    default:
      return 'default';
  }
};

const WorkflowSelector: React.FC<WorkflowSelectorProps> = ({ loading = false }) => {
  const { 
    availableWorkflows, 
    selectedWorkflow, 
    setSelectedWorkflow 
  } = useAppStore();

  const handleWorkflowSelect = (workflow: WorkflowType) => {
    setSelectedWorkflow(workflow);
  };

  if (loading) {
    return (
      <Grid container spacing={2}>
        {[1, 2].map((i) => (
          <Grid item xs={12} sm={6} key={i}>
            <Card>
              <CardContent>
                <Skeleton variant="text" width="60%" height={24} />
                <Skeleton variant="text" width="100%" height={20} />
                <Skeleton variant="text" width="80%" height={20} />
                <Box sx={{ mt: 2 }}>
                  <Skeleton variant="rectangular" width={80} height={24} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    );
  }

  return (
    <Box>
      <RadioGroup
        value={selectedWorkflow?.id || ''}
        onChange={(e) => {
          const workflow = availableWorkflows.find(w => w.id === e.target.value);
          if (workflow) handleWorkflowSelect(workflow);
        }}
      >
        <Grid container spacing={2}>
          {availableWorkflows.map((workflow) => (
            <Grid item xs={12} sm={6} key={workflow.id}>
              <Card 
                sx={{ 
                  cursor: 'pointer',
                  border: selectedWorkflow?.id === workflow.id ? 2 : 1,
                  borderColor: selectedWorkflow?.id === workflow.id ? 'primary.main' : 'divider',
                  '&:hover': {
                    borderColor: 'primary.light',
                    boxShadow: 2,
                  }
                }}
                onClick={() => handleWorkflowSelect(workflow)}
              >
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
                    <FormControlLabel
                      value={workflow.id}
                      control={<Radio />}
                      label=""
                      sx={{ m: 0 }}
                    />
                    <Box sx={{ flex: 1 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                        {getWorkflowIcon(workflow.category)}
                        <Typography variant="h6">
                          {workflow.displayName}
                        </Typography>
                      </Box>
                      
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        {workflow.description}
                      </Typography>

                      <Box sx={{ mb: 2 }}>
                        <Chip
                          size="small"
                          label={workflow.category}
                          color={getWorkflowColor(workflow.category) as any}
                          variant="outlined"
                        />
                      </Box>

                      <Typography variant="caption" color="text.secondary">
                        Required fields: {workflow.requiredFields.length} | 
                        Optional fields: {workflow.optionalFields.length}
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </RadioGroup>

      {selectedWorkflow && (
        <Box sx={{ mt: 3, p: 2, backgroundColor: 'primary.50', borderRadius: 2 }}>
          <Typography variant="subtitle2" color="primary.main" gutterBottom>
            Selected: {selectedWorkflow.displayName}
          </Typography>
          
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <Typography variant="caption" color="text.secondary" display="block">
                Required Fields:
              </Typography>
              <List dense sx={{ py: 0 }}>
                {selectedWorkflow.requiredFields.map((field) => (
                  <ListItem key={field.id} sx={{ py: 0, px: 0 }}>
                    <ListItemText 
                      primary={field.label}
                      primaryTypographyProps={{ variant: 'body2' }}
                    />
                  </ListItem>
                ))}
              </List>
            </Grid>
            
            {selectedWorkflow.optionalFields.length > 0 && (
              <Grid item xs={12} sm={6}>
                <Typography variant="caption" color="text.secondary" display="block">
                  Optional Fields:
                </Typography>
                <List dense sx={{ py: 0 }}>
                  {selectedWorkflow.optionalFields.map((field) => (
                    <ListItem key={field.id} sx={{ py: 0, px: 0 }}>
                      <ListItemText 
                        primary={field.label}
                        primaryTypographyProps={{ variant: 'body2' }}
                      />
                    </ListItem>
                  ))}
                </List>
              </Grid>
            )}
          </Grid>
        </Box>
      )}
    </Box>
  );
};

export default WorkflowSelector;
