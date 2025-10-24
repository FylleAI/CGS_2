/**
 * CompanySnapshotRenderer
 * Registers company snapshot card renderer with the registry
 * Now uses the new OnboardingResultsGrid (2x2 card layout)
 */

import React from 'react';
import { rendererRegistry } from './RendererRegistry';
import { OnboardingResultsGrid } from '../components/cards/OnboardingResultsGrid';
import type { OnboardingSession, CompanySnapshot } from '../types/onboarding';

/**
 * Extract company snapshot from session.
 * CGS returns company_snapshot in content.metadata, or we use session.snapshot as fallback.
 */
const extractCompanySnapshot = (session: OnboardingSession): CompanySnapshot | null => {
  let snapshot: CompanySnapshot | undefined;

  // 1. Try to get snapshot from CGS response content.metadata (primary location)
  const contentMetadata = session.cgs_response?.content?.metadata;
  snapshot = contentMetadata?.company_snapshot;

  // 2. Fallback to root-level metadata (in case backend structure differs)
  if (!snapshot) {
    const rootMetadata = session.cgs_response?.metadata;
    snapshot = rootMetadata?.company_snapshot;
  }

  // 3. Fallback to session.snapshot (original snapshot from research phase)
  if (!snapshot) {
    snapshot = session.snapshot;
  }

  if (!snapshot) {
    console.warn('⚠️ CompanySnapshotRenderer: No snapshot found in session');
    return null;
  }

  return snapshot;
};

/**
 * Wrapper component for OnboardingResultsGrid to match renderer interface.
 */
const CompanySnapshotCardRenderer: React.FC<{
  session: OnboardingSession;
  data: CompanySnapshot | null;
  onStartNew?: () => void;
}> = ({ data, onStartNew }) => {
  if (!data) {
    return (
      <div className="bg-white border border-gray-200 rounded-2xl shadow-sm p-6 max-w-3xl mx-auto">
        <div className="text-center text-gray-500 py-8">
          <p className="text-lg font-semibold mb-2">No Company Snapshot Available</p>
          <p className="text-sm">The company snapshot could not be loaded.</p>
        </div>
      </div>
    );
  }

  return <OnboardingResultsGrid snapshot={data} onStartNew={onStartNew} />;
};

// Register company snapshot renderer
rendererRegistry.register(
  'company_snapshot',
  CompanySnapshotCardRenderer,
  extractCompanySnapshot
);

