import React from "react";
import type { CompanySnapshotCardData } from "@/types/onboarding";

/**
 * CompanySnapshotCard - Presentational Component
 *
 * Displays company snapshot data in a beautiful card format.
 * This is a pure UI component with no business logic.
 *
 * @param data - Normalized company snapshot data
 */

interface CompanySnapshotCardProps {
  data: CompanySnapshotCardData | null;
  onGenerateBrief?: () => void;
  onCompareCompetitors?: () => void;
}

export default function CompanySnapshotCard({ 
  data, 
  onGenerateBrief, 
  onCompareCompetitors 
}: CompanySnapshotCardProps) {
  if (!data) {
    return (
      <div className="bg-white border border-gray-200 rounded-2xl shadow-sm p-6 max-w-3xl mx-auto">
        <p className="text-center text-gray-500">No company snapshot available</p>
      </div>
    );
  }

  return (
    <div className="bg-white border border-gray-200 rounded-2xl shadow-sm p-6 max-w-3xl mx-auto">
      {/* Header */}
      <header className="mb-4">
        <h2 className="text-2xl font-bold text-gray-900">{data.name}</h2>
        <p className="text-sm text-gray-600">{data.industry}</p>
        {data.website && (
          <a
            href={data.website}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 text-sm underline hover:text-blue-800"
          >
            {data.website.replace(/^https?:\/\//, "")}
          </a>
        )}
      </header>

      {/* Overview */}
      {data.description && (
        <section className="mb-4">
          <h3 className="text-lg font-semibold text-gray-800 mb-1">Overview</h3>
          <p className="text-gray-700 text-sm">{data.description}</p>
        </section>
      )}

      {/* Voice & Audience */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div>
          <h4 className="font-semibold text-gray-800 mb-1">Voice & Tone</h4>
          <p className="text-sm text-gray-700 mb-1">
            Tone: <span className="font-medium">{data.voiceTone}</span>
          </p>
          {data.voiceStyle.length > 0 && (
            <ul className="text-sm text-gray-700 list-disc ml-4">
              {data.voiceStyle.map((style, i) => (
                <li key={i}>{style}</li>
              ))}
            </ul>
          )}
        </div>

        <div>
          <h4 className="font-semibold text-gray-800 mb-1">Audience</h4>
          <p className="text-sm text-gray-700 mb-1">
            Primary: <span className="font-medium">{data.primaryAudience}</span>
          </p>
          {data.painPoints.length > 0 && (
            <>
              <p className="text-sm text-gray-700 font-medium mt-2">Pain Points:</p>
              <ul className="text-sm text-gray-700 list-disc ml-4">
                {data.painPoints.map((p, i) => (
                  <li key={i}>{p}</li>
                ))}
              </ul>
            </>
          )}
        </div>
      </section>

      {/* Positioning */}
      {data.positioning && (
        <section className="mb-4">
          <h4 className="font-semibold text-gray-800 mb-1">Positioning</h4>
          <p className="text-sm text-gray-700">{data.positioning}</p>
        </section>
      )}

      {/* Differentiators */}
      {data.differentiators.length > 0 && (
        <section className="mb-4">
          <h4 className="font-semibold text-gray-800 mb-1">Key Differentiators</h4>
          <ul className="text-sm text-gray-700 list-disc ml-4">
            {data.differentiators.map((diff, i) => (
              <li key={i}>{diff}</li>
            ))}
          </ul>
        </section>
      )}

      {/* Recent Highlights */}
      {data.recentNews.length > 0 && (
        <section className="mb-4">
          <h4 className="font-semibold text-gray-800 mb-1">Recent Highlights</h4>
          <ul className="text-sm text-gray-700 list-disc ml-4">
            {data.recentNews.map((n, i) => (
              <li key={i}>{n}</li>
            ))}
          </ul>
        </section>
      )}

      {/* AI Summary */}
      {data.aiSummary && (
        <section className="mb-6 bg-gray-50 rounded-xl p-4">
          <h4 className="font-semibold text-gray-800 mb-1">Fylle Insight</h4>
          <p className="italic text-gray-700 text-sm">"{data.aiSummary}"</p>
        </section>
      )}

      {/* CTAs */}
      <div className="flex gap-3">
        <button 
          onClick={onGenerateBrief}
          className="bg-blue-600 text-white text-sm px-4 py-2 rounded-xl hover:bg-blue-700 transition-colors"
        >
          Generate AI Brief
        </button>
        <button 
          onClick={onCompareCompetitors}
          className="bg-gray-100 text-gray-800 text-sm px-4 py-2 rounded-xl hover:bg-gray-200 transition-colors"
        >
          Compare with Competitors
        </button>
      </div>
    </div>
  );
}

