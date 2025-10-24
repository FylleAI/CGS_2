import React from 'react';
import { motion } from 'framer-motion';
import { CompanySnapshot } from '../../types/onboarding';
import { CompanySnapshotCardV2 } from './CompanySnapshotCardV2';
import { AudienceIntelligenceCard } from './AudienceIntelligenceCard';
import { VoiceDNACard } from './VoiceDNACard';
import { StrategicInsightsCard } from './StrategicInsightsCard';

interface OnboardingResultsGridProps {
  snapshot: CompanySnapshot;
  onStartNew?: () => void;
}

export const OnboardingResultsGrid: React.FC<OnboardingResultsGridProps> = ({
  snapshot,
  onStartNew,
}) => {
  return (
    <div className="w-full max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="mb-8 text-center"
      >
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Welcome, {snapshot.company.name}! 🎉
        </h1>
        <p className="text-gray-600">
          Fylle has analyzed your company and created a personalized profile.
        </p>
      </motion.div>

      {/* Grid 2x2 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        {/* Card 1: Company Snapshot */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3, delay: 0.1 }}
        >
          <CompanySnapshotCardV2 snapshot={snapshot} />
        </motion.div>

        {/* Card 2: Audience Intelligence */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3, delay: 0.2 }}
        >
          <AudienceIntelligenceCard snapshot={snapshot} />
        </motion.div>

        {/* Card 3: Voice DNA */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3, delay: 0.3 }}
        >
          <VoiceDNACard snapshot={snapshot} />
        </motion.div>

        {/* Card 4: Strategic Insights */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3, delay: 0.4 }}
        >
          <StrategicInsightsCard snapshot={snapshot} />
        </motion.div>
      </div>

      {/* Primary CTA */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.5 }}
        className="flex flex-col items-center gap-4"
      >
        <button className="rounded-xl bg-gradient-to-r from-emerald-500 to-emerald-600 px-8 py-4 text-lg font-semibold text-white shadow-lg shadow-emerald-500/30 transition-all hover:shadow-xl hover:shadow-emerald-500/40 hover:scale-105">
          🚀 Build Your Knowledge Base
        </button>
        {onStartNew && (
          <button
            onClick={onStartNew}
            className="text-sm text-gray-500 hover:text-gray-700 transition-colors"
          >
            Start a new onboarding
          </button>
        )}
      </motion.div>

      {/* Footer Info */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.3, delay: 0.6 }}
        className="mt-8 text-center text-xs text-gray-500"
      >
        <p>
          Generated on {new Date(snapshot.generated_at).toLocaleDateString('en-US', {
            month: 'long',
            day: 'numeric',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
          })}
        </p>
        <p className="mt-1">
          Trace ID: <code className="font-mono text-gray-400">{snapshot.trace_id}</code>
        </p>
      </motion.div>
    </div>
  );
};

