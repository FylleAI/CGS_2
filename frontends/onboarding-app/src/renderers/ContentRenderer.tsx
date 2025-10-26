/**
 * Content Renderer
 * Registers content preview renderer with the registry
 */

import { rendererRegistry } from './RendererRegistry';
import { ContentPreview } from '@/components/steps/ContentPreview';
import type { OnboardingSession } from '@/types/onboarding';

/**
 * Extract content data from session.
 */
const extractContentData = (session: OnboardingSession): {
  contentTitle: string;
  contentPreview: string;
  wordCount: number;
} => {
  const metadata = session.metadata || {};
  const contentTitle = metadata.content_title || 'Content Generated';
  const contentPreview = metadata.content_preview || session.cgs_response?.content?.body || 'Your content is ready!';
  const wordCount = metadata.word_count || 0;

  return {
    contentTitle,
    contentPreview,
    wordCount,
  };
};

// Register content preview renderer (fallback for unknown display types)
rendererRegistry.register(
  'content_preview',
  ContentPreview,
  extractContentData
);

