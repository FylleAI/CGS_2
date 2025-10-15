/**
 * Step1CompanyInput Component
 * Company information input with conversational UI
 */

import React from 'react';
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import {
  Box,
  Typography,
  TextField,
  Button,
  MenuItem,
  Chip,
  Stack,
  InputAdornment,
} from '@mui/material';
import {
  Business as BusinessIcon,
  Language as WebIcon,
  Email as EmailIcon,
  Send as SendIcon,
} from '@mui/icons-material';
import { GOAL_OPTIONS, SUGGESTION_CHIPS } from '@/config/constants';
import type { OnboardingFormData, OnboardingGoal } from '@/types/onboarding';

// ============================================================================
// Validation Schema
// ============================================================================

const schema = yup.object().shape({
  brand_name: yup.string().required('Company name is required').min(2, 'Too short'),
  website: yup.string().url('Must be a valid URL').nullable(),
  goal: yup.string().required('Please select a goal').oneOf(['linkedin_post', 'newsletter', 'newsletter_premium', 'article']),
  user_email: yup.string().email('Must be a valid email').nullable(),
  additional_context: yup.string().nullable(),
});

// ============================================================================
// Component
// ============================================================================

interface Step1CompanyInputProps {
  onSubmit: (data: Partial<OnboardingFormData>) => void;
  isLoading?: boolean;
}

export const Step1CompanyInput: React.FC<Step1CompanyInputProps> = ({
  onSubmit,
  isLoading = false,
}) => {
  const {
    control,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm({
    resolver: yupResolver(schema),
    defaultValues: {
      brand_name: '',
      website: '',
      goal: 'linkedin_post' as OnboardingGoal,
      user_email: '',
      additional_context: '',
    },
  });

  const handleChipClick = (value: string) => {
    setValue('brand_name', value);
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 700 }}>
          👋 Welcome to Fylle AI
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Let's get started by learning about your company
        </Typography>
      </Box>

      {/* Suggestion Chips */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
          Quick suggestions:
        </Typography>
        <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
          {SUGGESTION_CHIPS.map((chip) => (
            <Chip
              key={chip.value}
              label={`${chip.icon} ${chip.label}`}
              onClick={() => handleChipClick(chip.value)}
              sx={{
                cursor: 'pointer',
                '&:hover': {
                  backgroundColor: 'primary.light',
                  color: 'white',
                },
              }}
            />
          ))}
        </Stack>
      </Box>

      {/* Form */}
      <form onSubmit={handleSubmit(onSubmit)}>
        <Stack spacing={3}>
          {/* Company Name */}
          <Controller
            name="brand_name"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Company Name"
                placeholder="e.g., Acme Corp"
                required
                fullWidth
                error={!!errors.brand_name}
                helperText={errors.brand_name?.message}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <BusinessIcon color="primary" />
                    </InputAdornment>
                  ),
                }}
              />
            )}
          />

          {/* Website */}
          <Controller
            name="website"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Website (Optional)"
                placeholder="https://example.com"
                fullWidth
                error={!!errors.website}
                helperText={errors.website?.message}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <WebIcon color="action" />
                    </InputAdornment>
                  ),
                }}
              />
            )}
          />

          {/* Goal */}
          <Controller
            name="goal"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                select
                label="What would you like to create?"
                required
                fullWidth
                error={!!errors.goal}
                helperText={errors.goal?.message}
              >
                {GOAL_OPTIONS.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.icon} {option.label}
                  </MenuItem>
                ))}
              </TextField>
            )}
          />

          {/* Email */}
          <Controller
            name="user_email"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Email (Optional)"
                placeholder="your@email.com"
                type="email"
                fullWidth
                error={!!errors.user_email}
                helperText={errors.user_email?.message || 'We\'ll send the results here'}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <EmailIcon color="action" />
                    </InputAdornment>
                  ),
                }}
              />
            )}
          />

          {/* Additional Context */}
          <Controller
            name="additional_context"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Additional Context (Optional)"
                placeholder="Tell us more about your company or specific requirements..."
                multiline
                rows={3}
                fullWidth
              />
            )}
          />

          {/* Submit Button */}
          <Button
            type="submit"
            variant="contained"
            size="large"
            disabled={isLoading}
            endIcon={<SendIcon />}
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
            {isLoading ? 'Starting Research...' : 'Start Research'}
          </Button>
        </Stack>
      </form>
    </Box>
  );
};

export default Step1CompanyInput;

