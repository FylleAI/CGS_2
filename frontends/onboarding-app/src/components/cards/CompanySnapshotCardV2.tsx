import React, { useState } from 'react';
import { Building2, ExternalLink, Sparkles, TrendingUp } from 'lucide-react';
import { FylleCard, CardHeader, CardContent, CardFooter, Chip, Section } from './FylleCard';
import { CompanySnapshot } from '../../types/onboarding';

interface CompanySnapshotCardV2Props {
  snapshot: CompanySnapshot;
}

export const CompanySnapshotCardV2: React.FC<CompanySnapshotCardV2Props> = ({ snapshot }) => {
  const [isHovered, setIsHovered] = useState(false);

  // Calculate average confidence from evidence
  const avgConfidence =
    snapshot.company.evidence && snapshot.company.evidence.length > 0
      ? snapshot.company.evidence.reduce((sum, e) => sum + e.confidence, 0) /
        snapshot.company.evidence.length
      : 0.8;

  // Truncate description to 240-280 chars
  const truncateText = (text: string, maxLength: number = 280) => {
    if (text.length <= maxLength) return text;
    return text.slice(0, maxLength).trim() + '...';
  };

  return (
    <FylleCard
      category="company"
      className="h-full"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <CardHeader
        icon={Building2}
        title={snapshot.company.name}
        subtitle={snapshot.company.industry || 'Industry not specified'}
        confidence={avgConfidence}
        category="company"
      />

      <CardContent className="space-y-4">
        {/* Description */}
        <div>
          <p className="text-sm leading-relaxed text-gray-700">
            {truncateText(snapshot.company.description)}
          </p>
          {snapshot.company.website && (
            <a
              href={snapshot.company.website}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-2 inline-flex items-center gap-1 text-xs text-emerald-600 hover:text-emerald-700"
            >
              <ExternalLink className="h-3 w-3" />
              {snapshot.company.website.replace(/^https?:\/\//, '')}
            </a>
          )}
        </div>

        {/* Key Offerings */}
        {snapshot.company.key_offerings && snapshot.company.key_offerings.length > 0 && (
          <Section title="Key Offerings" icon={Sparkles}>
            <div className="flex flex-wrap gap-2">
              {snapshot.company.key_offerings.slice(0, 4).map((offering, idx) => (
                <Chip key={idx} variant="primary">
                  {offering}
                </Chip>
              ))}
            </div>
          </Section>
        )}

        {/* Differentiators */}
        {snapshot.company.differentiators && snapshot.company.differentiators.length > 0 && (
          <Section title="Differentiators" icon={TrendingUp}>
            <ul className="space-y-2">
              {snapshot.company.differentiators.slice(0, 3).map((diff, idx) => (
                <li key={idx} className="flex items-start gap-2 text-sm text-gray-700">
                  <span className="mt-1 flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full bg-emerald-100 text-xs font-semibold text-emerald-700">
                    {idx + 1}
                  </span>
                  <span className="leading-relaxed">{diff}</span>
                </li>
              ))}
            </ul>
          </Section>
        )}
      </CardContent>

      <CardFooter className="flex items-center justify-between">
        <div className="text-xs text-gray-500">
          Updated {new Date(snapshot.generated_at).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
          })}
        </div>
        <button
          className={`
            rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-xs font-medium text-emerald-700
            transition-all duration-200 hover:bg-emerald-100 hover:border-emerald-300
            ${isHovered ? 'opacity-100' : 'opacity-70'}
          `}
        >
          Refine Details
        </button>
      </CardFooter>
    </FylleCard>
  );
};

