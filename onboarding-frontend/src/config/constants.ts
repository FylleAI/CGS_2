/**
 * Application Constants
 * Centralized configuration values
 */

export const POLLING_CONFIG = {
  INTERVAL: Number(import.meta.env.VITE_POLLING_INTERVAL) || 3000, // 3 seconds
  MAX_ATTEMPTS: Number(import.meta.env.VITE_MAX_POLLING_ATTEMPTS) || 40, // 2 minutes max
  BACKOFF_MULTIPLIER: 1.5, // Exponential backoff
} as const;

export const FEATURE_FLAGS = {
  ENABLE_DASHBOARD: import.meta.env.VITE_ENABLE_DASHBOARD === 'true',
  ENABLE_DEBUG_MODE: import.meta.env.VITE_ENABLE_DEBUG_MODE === 'true',
} as const;

export const ONBOARDING_STEPS = {
  COMPANY_INPUT: 0,
  RESEARCH_PROGRESS: 1,
  SNAPSHOT_REVIEW: 2,
  QUESTIONS: 3,
  EXECUTION: 4,
  RESULTS: 5,
} as const;

export const STEP_LABELS = [
  'Company Information',
  'Research in Progress',
  'Review Snapshot',
  'Clarifying Questions',
  'Generating Content',
  'Results',
] as const;

export const GOAL_OPTIONS = [
  {
    value: 'company_analytics',
    label: 'Company Analytics',
    icon: '📊',
    description: 'Comprehensive analytics report with insights and recommendations'
  },
  {
    value: 'linkedin_post',
    label: 'LinkedIn Post',
    icon: '💼',
    description: 'Short, engaging post (200-400 words)'
  },
  {
    value: 'linkedin_article',
    label: 'LinkedIn Article',
    icon: '📄',
    description: 'Long-form thought leadership (800-1500 words)'
  },
  {
    value: 'newsletter',
    label: 'Newsletter',
    icon: '📧',
    description: 'Curated newsletter (1000-1500 words)'
  },
  {
    value: 'newsletter_premium',
    label: 'Premium Newsletter',
    icon: '⭐',
    description: 'Premium newsletter with research'
  },
  {
    value: 'blog_post',
    label: 'Blog Post',
    icon: '✍️',
    description: 'SEO-optimized blog article (1200-2000 words)'
  },
  {
    value: 'article',
    label: 'Article',
    icon: '📝',
    description: 'Generic article'
  },
] as const;

export const SUGGESTION_CHIPS = [
  { label: 'Tech Startup', icon: '🚀', value: 'tech startup' },
  { label: 'E-commerce', icon: '🛒', value: 'e-commerce business' },
  { label: 'SaaS Company', icon: '☁️', value: 'saas company' },
  { label: 'Consulting Firm', icon: '💡', value: 'consulting firm' },
  { label: 'Marketing Agency', icon: '📱', value: 'marketing agency' },
  { label: 'Real Estate', icon: '🏢', value: 'real estate company' },
] as const;

export const ANIMATION_DURATIONS = {
  FAST: 200,
  NORMAL: 300,
  SLOW: 500,
} as const;

export const TOAST_CONFIG = {
  DURATION: 4000,
  SUCCESS_DURATION: 3000,
  ERROR_DURATION: 6000,
} as const;

export default {
  POLLING_CONFIG,
  FEATURE_FLAGS,
  ONBOARDING_STEPS,
  STEP_LABELS,
  GOAL_OPTIONS,
  SUGGESTION_CHIPS,
  ANIMATION_DURATIONS,
  TOAST_CONFIG,
};

