/**
 * Step6Results Component
 * Metadata-driven rendering using Renderer Registry
 */

import React from 'react';
import { Box, Typography } from '@mui/material';
import { rendererRegistry } from '@/renderers/RendererRegistry';
import type { OnboardingSession } from '@/types/onboarding';

// Import renderers to auto-register them
import '@/renderers/AnalyticsRenderer';
import '@/renderers/ContentRenderer';

interface Step6ResultsProps {
  session: OnboardingSession;
  onStartNew: () => void;
}

export const Step6Results: React.FC<Step6ResultsProps> = ({
  session,
  onStartNew,
}) => {
  // Get display_type from CGS response (metadata-driven!)
  const displayType = session.cgs_response?.content?.display_type || 'content_preview';

  console.log(`🎨 Rendering with display_type: ${displayType}`);

  // Get renderer from registry
  const renderer = rendererRegistry.getRenderer(displayType);

  // Fallback if renderer not found
  if (!renderer) {
    console.warn(`⚠️ No renderer found for display_type: ${displayType}, using fallback`);

    const fallbackRenderer = rendererRegistry.getRenderer('content_preview');

    if (!fallbackRenderer) {
      return (
        <Box sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" color="error">
            ❌ Error: No renderer available
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            Display type: {displayType}
          </Typography>
        </Box>
      );
    }

    // Use fallback
    const fallbackData = fallbackRenderer.dataExtractor(session);
    const FallbackComponent = fallbackRenderer.component;
    return <FallbackComponent session={session} data={fallbackData} onStartNew={onStartNew} />;
  }

  // Extract data and render
  const data = renderer.dataExtractor(session);
  const RendererComponent = renderer.component;

  return <RendererComponent session={session} data={data} onStartNew={onStartNew} />;
};

export default Step6Results;

