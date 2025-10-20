/**
 * Analytics Renderer
 * Registers analytics dashboard renderer with the registry
 */

import { rendererRegistry } from './RendererRegistry';
import { Step6Dashboard } from '@/components/steps/Step6Dashboard';
import type { OnboardingSession, AnalyticsData } from '@/types/onboarding';

/**
 * Extract analytics data from session.
 */
const extractAnalyticsData = (session: OnboardingSession): {
  analyticsData: AnalyticsData | null;
  companyName: string;
} => {
  const content = session.cgs_response?.content;
  
  if (!content || !content.analytics_data) {
    return {
      analyticsData: null,
      companyName: session.brand_name,
    };
  }

  return {
    analyticsData: content.analytics_data as AnalyticsData,
    companyName: session.brand_name,
  };
};

/**
 * Wrapper component for Step6Dashboard to match renderer interface.
 */
const AnalyticsDashboardRenderer: React.FC<{
  session: OnboardingSession;
  data: ReturnType<typeof extractAnalyticsData>;
  onStartNew: () => void;
}> = ({ data, onStartNew }) => {
  if (!data.analyticsData) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <p>❌ Analytics data not available</p>
      </div>
    );
  }

  return (
    <Step6Dashboard
      analyticsData={data.analyticsData}
      companyName={data.companyName}
      onReset={onStartNew}
    />
  );
};

// Register analytics dashboard renderer
rendererRegistry.register(
  'analytics_dashboard',
  AnalyticsDashboardRenderer,
  extractAnalyticsData
);

console.log('📊 Analytics renderer registered');

