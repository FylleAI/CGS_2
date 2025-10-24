import React from 'react';
import { MessageSquare, Mic, MousePointerClick, Shield } from 'lucide-react';
import { FylleCard, CardHeader, CardContent, CardFooter, Chip, Section } from './FylleCard';
import { CompanySnapshot } from '../../types/onboarding';

interface VoiceDNACardProps {
  snapshot: CompanySnapshot;
}

export const VoiceDNACard: React.FC<VoiceDNACardProps> = ({ snapshot }) => {
  const { voice } = snapshot;

  // Capitalize tone
  const formattedTone = voice.tone
    .split(' ')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');

  // Get tone color
  const getToneColor = (tone: string) => {
    const lowerTone = tone.toLowerCase();
    if (lowerTone.includes('professional')) return 'from-blue-500/10 to-blue-600/5';
    if (lowerTone.includes('friendly')) return 'from-green-500/10 to-green-600/5';
    if (lowerTone.includes('casual')) return 'from-orange-500/10 to-orange-600/5';
    if (lowerTone.includes('formal')) return 'from-gray-500/10 to-gray-600/5';
    return 'from-purple-500/10 to-purple-600/5';
  };

  return (
    <FylleCard category="voice" className="h-full">
      <CardHeader
        icon={MessageSquare}
        title="Voice DNA"
        subtitle="How you communicate"
        category="voice"
      />

      <CardContent className="space-y-4">
        {/* Tone */}
        <div>
          <div className="text-sm font-medium text-gray-700 mb-2">Brand Tone</div>
          <div
            className={`rounded-lg bg-gradient-to-r ${getToneColor(voice.tone)} border border-purple-200/50 p-4 text-center`}
          >
            <div className="flex items-center justify-center gap-2">
              <Mic className="h-5 w-5 text-purple-600" />
              <span className="text-lg font-semibold text-purple-900">{formattedTone}</span>
            </div>
          </div>
        </div>

        {/* Style Guidelines */}
        {voice.style_guidelines && voice.style_guidelines.length > 0 && (
          <Section title="Style Guidelines" icon={Shield}>
            <ul className="space-y-2">
              {voice.style_guidelines.slice(0, 3).map((guideline, idx) => (
                <li key={idx} className="flex items-start gap-2 text-sm text-gray-700">
                  <span className="mt-1 flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full bg-purple-100 text-xs font-semibold text-purple-700">
                    ✓
                  </span>
                  <span className="leading-relaxed">{guideline}</span>
                </li>
              ))}
            </ul>
          </Section>
        )}

        {/* CTA Preferences */}
        {voice.cta_preferences && voice.cta_preferences.length > 0 && (
          <Section title="Preferred CTAs" icon={MousePointerClick}>
            <div className="flex flex-wrap gap-2">
              {voice.cta_preferences.slice(0, 3).map((cta, idx) => (
                <button
                  key={idx}
                  className="rounded-lg border border-purple-200 bg-purple-50 px-3 py-1.5 text-xs font-medium text-purple-700 transition-all hover:bg-purple-100 hover:border-purple-300"
                >
                  {cta}
                </button>
              ))}
            </div>
          </Section>
        )}

        {/* Forbidden Phrases (if any) */}
        {voice.forbidden_phrases && voice.forbidden_phrases.length > 0 ? (
          <div className="rounded-lg border border-red-200 bg-red-50 p-3">
            <div className="text-xs font-medium text-red-700 mb-1">Avoid These Phrases</div>
            <div className="flex flex-wrap gap-1">
              {voice.forbidden_phrases.map((phrase, idx) => (
                <span key={idx} className="text-xs text-red-600">
                  "{phrase}"
                  {idx < voice.forbidden_phrases.length - 1 && ', '}
                </span>
              ))}
            </div>
          </div>
        ) : (
          <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-center">
            <span className="text-xs font-medium text-emerald-700">
              ✓ No content restrictions detected
            </span>
          </div>
        )}
      </CardContent>

      <CardFooter>
        <div className="text-xs text-gray-500">
          🎨 Voice profile analyzed from brand communications
        </div>
      </CardFooter>
    </FylleCard>
  );
};

