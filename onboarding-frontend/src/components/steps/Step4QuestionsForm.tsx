/**
 * Step4QuestionsForm Component
 * Dynamic form for clarifying questions
 */

import React from 'react';
import { useForm, Controller } from 'react-hook-form';
import {
  Box,
  Typography,
  TextField,
  Button,
  Radio,
  RadioGroup,
  FormControlLabel,
  FormControl,
  FormLabel,
  Checkbox,
  FormGroup,
  MenuItem,
  Stack,
  Card,
  CardContent,
} from '@mui/material';
import { Send } from '@mui/icons-material';
import type { QuestionResponse } from '@/types/onboarding';

interface Step4QuestionsFormProps {
  questions: QuestionResponse[];
  onSubmit: (answers: Record<string, any>) => void;
  isLoading?: boolean;
}

export const Step4QuestionsForm: React.FC<Step4QuestionsFormProps> = ({
  questions,
  onSubmit,
  isLoading = false,
}) => {
  const { control, handleSubmit, formState: { errors } } = useForm({
    defaultValues: questions.reduce((acc, q) => ({
      ...acc,
      [q.id]: q.expected_response_type === 'boolean' ? false : '',
    }), {}),
  });

  const renderQuestionInput = (question: QuestionResponse) => {
    switch (question.expected_response_type) {
      case 'boolean':
        return (
          <Controller
            name={question.id}
            control={control}
            rules={{ required: question.required }}
            render={({ field }) => (
              <FormControl component="fieldset">
                <RadioGroup {...field} row>
                  <FormControlLabel value="true" control={<Radio />} label="Yes" />
                  <FormControlLabel value="false" control={<Radio />} label="No" />
                </RadioGroup>
              </FormControl>
            )}
          />
        );

      case 'select':
        return (
          <Controller
            name={question.id}
            control={control}
            rules={{ required: question.required }}
            render={({ field }) => (
              <TextField
                {...field}
                select
                fullWidth
                error={!!errors[question.id]}
                helperText={errors[question.id] ? 'This field is required' : ''}
              >
                {question.options?.map((option) => (
                  <MenuItem key={option} value={option}>
                    {option}
                  </MenuItem>
                ))}
              </TextField>
            )}
          />
        );

      case 'multiselect':
        return (
          <Controller
            name={question.id}
            control={control}
            rules={{ required: question.required }}
            render={({ field }) => (
              <FormGroup>
                {question.options?.map((option) => (
                  <FormControlLabel
                    key={option}
                    control={
                      <Checkbox
                        checked={field.value?.includes(option) || false}
                        onChange={(e) => {
                          const currentValue = field.value || [];
                          if (e.target.checked) {
                            field.onChange([...currentValue, option]);
                          } else {
                            field.onChange(currentValue.filter((v: string) => v !== option));
                          }
                        }}
                      />
                    }
                    label={option}
                  />
                ))}
              </FormGroup>
            )}
          />
        );

      case 'number':
        return (
          <Controller
            name={question.id}
            control={control}
            rules={{ required: question.required }}
            render={({ field }) => (
              <TextField
                {...field}
                type="number"
                fullWidth
                error={!!errors[question.id]}
                helperText={errors[question.id] ? 'This field is required' : ''}
              />
            )}
          />
        );

      default: // string
        return (
          <Controller
            name={question.id}
            control={control}
            rules={{ required: question.required }}
            render={({ field }) => (
              <TextField
                {...field}
                fullWidth
                multiline
                rows={3}
                error={!!errors[question.id]}
                helperText={errors[question.id] ? 'This field is required' : ''}
              />
            )}
          />
        );
    }
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 700 }}>
          📝 A Few Questions
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Help us tailor the content to your specific needs
        </Typography>
      </Box>

      {/* Form */}
      <form onSubmit={handleSubmit(onSubmit)}>
        <Stack spacing={3}>
          {questions.map((question, index) => (
            <Card key={question.id} elevation={0} sx={{ backgroundColor: 'grey.50' }}>
              <CardContent>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="h6" gutterBottom>
                    Question {index + 1}
                    {question.required && (
                      <Typography component="span" color="error.main">
                        {' '}*
                      </Typography>
                    )}
                  </Typography>
                  <Typography variant="body1" fontWeight={600} gutterBottom>
                    {question.question}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {question.reason}
                  </Typography>
                </Box>

                {renderQuestionInput(question)}
              </CardContent>
            </Card>
          ))}

          {/* Submit Button */}
          <Button
            type="submit"
            variant="contained"
            size="large"
            disabled={isLoading}
            endIcon={<Send />}
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
            {isLoading ? 'Generating Content...' : 'Generate Content'}
          </Button>
        </Stack>
      </form>

      {/* Footer */}
      <Typography variant="caption" color="text.secondary" sx={{ mt: 3, display: 'block', textAlign: 'center' }}>
        Your answers will be used to create personalized content
      </Typography>
    </Box>
  );
};

export default Step4QuestionsForm;

