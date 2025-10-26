import React from 'react';
import { Users, Target, AlertCircle, CheckCircle2 } from 'lucide-react';
import { FylleCard, CardHeader, CardContent, CardFooter, Chip, Section } from './FylleCard';
import { CompanySnapshot } from '../../types/onboarding';

interface AudienceIntelligenceCardProps {
  snapshot: CompanySnapshot;
}

export const AudienceIntelligenceCard: React.FC<AudienceIntelligenceCardProps> = ({ snapshot }) => {
  const { audience } = snapshot;

  return (
    <FylleCard category="audience" className="h-full">
      <CardHeader
        icon={Users}
        title="Audience Intelligence"
        subtitle="Who you're reaching"
        category="audience"
      />

      <CardContent className="space-y-4">
        {/* Primary & Secondary Audience */}
        <Section title="Target Audience" icon={Target}>
          <div className="space-y-2">
            {/* Primary */}
            <div>
              <span className="text-xs font-medium text-gray-500">Primary</span>
              <div className="mt-1">
                <Chip variant="primary" className="text-base">
                  👤 {audience.primary}
                </Chip>
              </div>
            </div>

            {/* Secondary */}
            {audience.secondary && audience.secondary.length > 0 && (
              <div>
                <span className="text-xs font-medium text-gray-500">Secondary</span>
                <div className="mt-1 flex flex-wrap gap-2">
                  {audience.secondary.slice(0, 3).map((sec, idx) => (
                    <Chip key={idx} variant="secondary" className="text-xs">
                      {sec}
                    </Chip>
                  ))}
                </div>
              </div>
            )}
          </div>
        </Section>

        {/* Pain Points */}
        {audience.pain_points && audience.pain_points.length > 0 && (
          <Section title="Pain Points" icon={AlertCircle}>
            <ul className="space-y-2">
              {audience.pain_points.slice(0, 3).map((pain, idx) => (
                <li key={idx} className="flex items-start gap-2 text-sm text-gray-700">
                  <AlertCircle className="mt-0.5 h-4 w-4 flex-shrink-0 text-red-500" />
                  <span className="leading-relaxed">{pain}</span>
                </li>
              ))}
            </ul>
          </Section>
        )}

        {/* Desired Outcomes */}
        {audience.desired_outcomes && audience.desired_outcomes.length > 0 && (
          <Section title="Desired Outcomes" icon={CheckCircle2}>
            <ul className="space-y-2">
              {audience.desired_outcomes.slice(0, 3).map((outcome, idx) => (
                <li key={idx} className="flex items-start gap-2 text-sm text-gray-700">
                  <CheckCircle2 className="mt-0.5 h-4 w-4 flex-shrink-0 text-emerald-500" />
                  <span className="leading-relaxed">{outcome}</span>
                </li>
              ))}
            </ul>
          </Section>
        )}
      </CardContent>

      <CardFooter>
        <div className="text-xs text-gray-500">
          🧠 AI understanding based on market research
        </div>
      </CardFooter>
    </FylleCard>
  );
};

