import React, { useState } from 'react';
import { Card, CardContent, Typography, TextField, Button, Stack } from '@mui/material';
import toast from 'react-hot-toast';
import apiService from '../services/api';
import { useAppStore } from '../store/appStore';

const RAGUploader: React.FC = () => {
  const { selectedClient } = useAppStore();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [tags, setTags] = useState('');
  const [content, setContent] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleFileSelected = async (file?: File | null) => {
    try {
      if (!file) return;
      const isText = file.type.startsWith('text') || /(\.md|\.txt)$/i.test(file.name);
      if (!isText) {
        toast.error('Supportiamo solo file .md o .txt per ora');
        return;
      }
      const text = await file.text();
      setContent(text);
      if (!title) setTitle(file.name.replace(/\.(md|txt)$/i, ''));
      if (!description) setDescription(text.slice(0, 200));
      toast.success('File caricato nel form');
    } catch (e) {
      toast.error('Impossibile leggere il file');
    }
  };

  const handleSubmit = async () => {
    if (!selectedClient?.name) {
      toast.error('Select a client first');
      return;
    }
    if (!title.trim() || !content.trim()) {
      toast.error('Title and content are required');
      return;
    }

    try {
      setSubmitting(true);
      const payload: any = {
        title: title.trim(),
        content,
      };
      if (description.trim()) payload.description = description.trim();
      const tagList = tags
        .split(',')
        .map((t) => t.trim())
        .filter((t) => !!t);
      if (tagList.length) payload.tags = tagList;

      await apiService.uploadRAGDocument(selectedClient.name, payload);
      toast.success('Document uploaded');
      setTitle('');
      setDescription('');
      setTags('');
      setContent('');
    } catch (e: any) {
      // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
      toast.error(e?.response?.data?.detail || 'Upload failed');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Upload Knowledge Base Document
        </Typography>
        <Stack spacing={2}>
          <TextField
            label="Title (without .md)"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            fullWidth
          />
          <TextField
            label="Description (optional)"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            fullWidth
          />
          <TextField
            label="Tags (comma separated, optional)"
            value={tags}
            onChange={(e) => setTags(e.target.value)}
            fullWidth
          />

          <Button variant="outlined" component="label">
            Seleziona file (.md o .txt)
            <input
              type="file"
              hidden
              accept=".md,.txt,text/markdown,text/plain"
              onChange={(e) => handleFileSelected(e.target.files?.[0] ?? null)}
            />
          </Button>

          <TextField
            label="Content (Markdown)"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            fullWidth
            multiline
            minRows={6}
            placeholder="Incolla qui il contenuto oppure seleziona un file sopra"
          />
          <Button variant="contained" onClick={handleSubmit} disabled={submitting}>
            {submitting ? 'Uploading…' : 'Upload'}
          </Button>
        </Stack>
      </CardContent>
    </Card>
  );
};

export default RAGUploader;

