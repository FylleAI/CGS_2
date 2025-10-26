import React, { useState } from 'react';
import { Lightbulb, Newspaper, MessageCircle, TrendingUp } from 'lucide-react';
import { FylleCard, CardHeader, CardContent, CardFooter, Section, ConfidenceBadge } from './FylleCard';
import { CompanySnapshot } from '../../types/onboarding';

interface StrategicInsightsCardProps {
  snapshot: CompanySnapshot;
}

export const StrategicInsightsCard: React.FC<StrategicInsightsCardProps> = ({ snapshot }) => {
  const { insights, company } = snapshot;
  const [activeTab, setActiveTab] = useState<'news' | 'messages'>('news');

  return (
    <FylleCard category="insight" className="h-full">
      <CardHeader
        icon={Lightbulb}
        title="Strategic Insights"
        subtitle="Context & intelligence"
        category="insight"
      />

      <CardContent className="space-y-4">
        {/* Tabs */}
        <div className="flex gap-2 border-b border-gray-200">
          <button
            onClick={() => setActiveTab('news')}
            className={`
              pb-2 px-3 text-sm font-medium transition-all
              ${activeTab === 'news'
                ? 'border-b-2 border-amber-500 text-amber-700'
                : 'text-gray-500 hover:text-gray-700'
              }
            `}
          >
            <div className="flex items-center gap-1.5">
              <Newspaper className="h-4 w-4" />
              News
            </div>
          </button>
          <button
            onClick={() => setActiveTab('messages')}
            className={`
              pb-2 px-3 text-sm font-medium transition-all
              ${activeTab === 'messages'
                ? 'border-b-2 border-amber-500 text-amber-700'
                : 'text-gray-500 hover:text-gray-700'
              }
            `}
          >
            <div className="flex items-center gap-1.5">
              <MessageCircle className="h-4 w-4" />
              Messages
            </div>
          </button>
        </div>

        {/* Tab Content */}
        <div className="min-h-[200px]">
          {activeTab === 'news' && (
            <div className="space-y-3">
              {insights.recent_news && insights.recent_news.length > 0 ? (
                insights.recent_news.slice(0, 2).map((news, idx) => (
                  <div
                    key={idx}
                    className="rounded-lg border border-amber-200/50 bg-amber-50/30 p-3"
                  >
                    <div className="flex items-start gap-2">
                      <TrendingUp className="mt-0.5 h-4 w-4 flex-shrink-0 text-amber-600" />
                      <p className="text-sm leading-relaxed text-gray-700">{news}</p>
                    </div>
                  </div>
                ))
              ) : (
                <div className="flex h-[200px] items-center justify-center text-sm text-gray-500">
                  No recent news available
                </div>
              )}
            </div>
          )}

          {activeTab === 'messages' && (
            <div className="space-y-3">
              {insights.key_messages && insights.key_messages.length > 0 ? (
                <ul className="space-y-2">
                  {insights.key_messages.slice(0, 3).map((message, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-sm text-gray-700">
                      <span className="mt-1 flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full bg-amber-100 text-xs font-semibold text-amber-700">
                        {idx + 1}
                      </span>
                      <span className="leading-relaxed">{message}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="flex h-[200px] items-center justify-center text-sm text-gray-500">
                  No key messages available
                </div>
              )}
            </div>
          )}
        </div>

        {/* Evidence Section */}
        {company.evidence && company.evidence.length > 0 && (
          <Section title="Evidence" className="pt-2 border-t border-gray-200">
            <div className="space-y-2">
              {company.evidence.slice(0, 2).map((evidence, idx) => (
                <div key={idx} className="rounded-lg bg-gray-50 p-3">
                  <p className="text-xs leading-relaxed text-gray-600 mb-2">
                    "{evidence.excerpt.slice(0, 120)}..."
                  </p>
                  <ConfidenceBadge
                    confidence={evidence.confidence}
                    source={evidence.source}
                  />
                </div>
              ))}
            </div>
          </Section>
        )}
      </CardContent>

      <CardFooter>
        <button className="w-full rounded-lg border border-amber-200 bg-amber-50 px-4 py-2 text-sm font-medium text-amber-700 transition-all hover:bg-amber-100 hover:border-amber-300">
          Generate Content Plan
        </button>
      </CardFooter>
    </FylleCard>
  );
};

