import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Checkbox,
  FormControlLabel,
  Chip,
  Grid,
  TextField,
  InputAdornment,
  Skeleton,
  Alert,
  Collapse,
  IconButton,
  Badge,
} from '@mui/material';
import {
  Search as SearchIcon,
  Storage as StorageIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Description as DescriptionIcon,
  DateRange as DateRangeIcon,
} from '@mui/icons-material';
import { useQuery } from 'react-query';
import { format } from 'date-fns';

import { RAGContent } from '../types';
import apiService from '../services/api';

interface RAGContentSelectorProps {
  clientProfile: string;
  selectedContents: string[];
  onSelectionChange: (selectedIds: string[]) => void;
}

const RAGContentSelector: React.FC<RAGContentSelectorProps> = ({
  clientProfile,
  selectedContents,
  onSelectionChange,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [isExpanded, setIsExpanded] = useState(false);

  // Load RAG contents for the client
  const {
    data: ragContents = [],
    isLoading,
    error,
  } = useQuery(
    ['ragContents', clientProfile],
    () => apiService.getRAGContents(clientProfile),
    {
      enabled: !!clientProfile,
      retry: 1,
    }
  );

  // Get all unique tags
  const allTags = React.useMemo(() => {
    const tags = new Set<string>();
    ragContents.forEach(content => {
      content.tags.forEach(tag => tags.add(tag));
    });
    return Array.from(tags).sort();
  }, [ragContents]);

  // Filter contents based on search and tags
  const filteredContents = React.useMemo(() => {
    return ragContents.filter(content => {
      const matchesSearch = searchQuery === '' || 
        content.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        content.content.toLowerCase().includes(searchQuery.toLowerCase());
      
      const matchesTags = selectedTags.length === 0 ||
        selectedTags.some(tag => content.tags.includes(tag));
      
      return matchesSearch && matchesTags;
    });
  }, [ragContents, searchQuery, selectedTags]);

  const handleContentToggle = (contentId: string) => {
    const newSelection = selectedContents.includes(contentId)
      ? selectedContents.filter(id => id !== contentId)
      : [...selectedContents, contentId];
    
    onSelectionChange(newSelection);
  };

  const handleTagToggle = (tag: string) => {
    setSelectedTags(prev => 
      prev.includes(tag)
        ? prev.filter(t => t !== tag)
        : [...prev, tag]
    );
  };

  const handleSelectAll = () => {
    const allIds = filteredContents.map(content => content.id);
    onSelectionChange(allIds);
  };

  const handleClearAll = () => {
    onSelectionChange([]);
  };

  if (error) {
    return (
      <Alert severity="error">
        Failed to load knowledge base content for {clientProfile}
      </Alert>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <StorageIcon color="primary" />
          <Typography variant="h6">
            Knowledge Base Content
          </Typography>
          <Badge badgeContent={selectedContents.length} color="primary">
            <Chip size="small" label={`${ragContents.length} available`} />
          </Badge>
        </Box>
        
        <IconButton
          onClick={() => setIsExpanded(!isExpanded)}
          size="small"
        >
          {isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
        </IconButton>
      </Box>

      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Select relevant content from your knowledge base to enhance the article generation.
        Selected content will be used by the RAG specialist for context and insights.
      </Typography>

      <Collapse in={isExpanded}>
        <Box sx={{ mb: 3 }}>
          {/* Search and Filters */}
          <Grid container spacing={2} sx={{ mb: 2 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                size="small"
                placeholder="Search content..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon />
                    </InputAdornment>
                  ),
                }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                <Typography variant="caption">Filter by tags:</Typography>
                <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                  {allTags.slice(0, 5).map(tag => (
                    <Chip
                      key={tag}
                      label={tag}
                      size="small"
                      clickable
                      color={selectedTags.includes(tag) ? 'primary' : 'default'}
                      onClick={() => handleTagToggle(tag)}
                    />
                  ))}
                </Box>
              </Box>
            </Grid>
          </Grid>

          {/* Selection Actions */}
          <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
            <Chip
              label="Select All"
              size="small"
              clickable
              onClick={handleSelectAll}
              color="primary"
              variant="outlined"
            />
            <Chip
              label="Clear All"
              size="small"
              clickable
              onClick={handleClearAll}
              variant="outlined"
            />
          </Box>

          {/* Content List */}
          {isLoading ? (
            <Grid container spacing={2}>
              {[1, 2, 3].map(i => (
                <Grid item xs={12} md={6} key={i}>
                  <Card>
                    <CardContent>
                      <Skeleton variant="text" width="80%" height={24} />
                      <Skeleton variant="text" width="100%" height={20} />
                      <Skeleton variant="text" width="60%" height={20} />
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          ) : filteredContents.length === 0 ? (
            <Alert severity="info">
              {ragContents.length === 0 
                ? `No knowledge base content found for ${clientProfile}`
                : 'No content matches your search criteria'
              }
            </Alert>
          ) : (
            <Grid container spacing={2}>
              {filteredContents.map(content => (
                <Grid item xs={12} md={6} key={content.id}>
                  <Card 
                    sx={{ 
                      cursor: 'pointer',
                      border: selectedContents.includes(content.id) ? 2 : 1,
                      borderColor: selectedContents.includes(content.id) ? 'primary.main' : 'divider',
                      '&:hover': {
                        borderColor: 'primary.light',
                        boxShadow: 2,
                      }
                    }}
                    onClick={() => handleContentToggle(content.id)}
                  >
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
                        <FormControlLabel
                          control={
                            <Checkbox
                              checked={selectedContents.includes(content.id)}
                              onChange={() => handleContentToggle(content.id)}
                            />
                          }
                          label=""
                          sx={{ m: 0 }}
                        />
                        
                        <Box sx={{ flex: 1 }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                            <DescriptionIcon fontSize="small" color="action" />
                            <Typography variant="subtitle2" noWrap>
                              {content.title}
                            </Typography>
                          </Box>
                          
                          <Typography 
                            variant="body2" 
                            color="text.secondary" 
                            sx={{ 
                              mb: 1,
                              display: '-webkit-box',
                              WebkitLineClamp: 2,
                              WebkitBoxOrient: 'vertical',
                              overflow: 'hidden',
                            }}
                          >
                            {content.content}
                          </Typography>

                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                            <DateRangeIcon fontSize="small" color="action" />
                            <Typography variant="caption">
                              {format(new Date(content.createdAt), 'MMM dd, yyyy')}
                            </Typography>
                            <Chip size="small" label={content.type} variant="outlined" />
                          </Box>

                          <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                            {content.tags.slice(0, 3).map(tag => (
                              <Chip
                                key={tag}
                                label={tag}
                                size="small"
                                variant="outlined"
                                color="primary"
                              />
                            ))}
                            {content.tags.length > 3 && (
                              <Chip
                                label={`+${content.tags.length - 3}`}
                                size="small"
                                variant="outlined"
                              />
                            )}
                          </Box>
                        </Box>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
        </Box>
      </Collapse>

      {/* Summary */}
      {selectedContents.length > 0 && (
        <Box sx={{ mt: 2, p: 2, backgroundColor: 'primary.50', borderRadius: 1 }}>
          <Typography variant="subtitle2" color="primary.main">
            Selected: {selectedContents.length} content{selectedContents.length !== 1 ? 's' : ''}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            These will be used by the RAG specialist to enhance your article with relevant context and insights.
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default RAGContentSelector;
