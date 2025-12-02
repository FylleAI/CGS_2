import { useState } from 'react';
import { useLocation } from 'wouter';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Loader2, MoreHorizontal, Pencil } from 'lucide-react';
import { useCards } from '@/hooks/useCards';
import { CardType, CardTypeLabels, CardTypeDescriptions } from '@shared/types/cards';
const fylleLogo = '/assets/fylle-logotipo-green.png';
import type { 
  Card as CardData, 
  ProductCard, 
  TargetCard, 
  CampaignsCard, 
  TopicCard, 
  BrandVoiceCard, 
  CompetitorCard, 
  PerformanceCard, 
  FeedbackCard 
} from '@shared/types/cards';

type ViewMode = 'types' | 'type-list' | 'detail';

const cardVariants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 }
};

export default function CardsPage() {
  const [, navigate] = useLocation();
  const { 
    cards, 
    isLoading, 
    isError,
    selectedCardId,
    selectedCard,
    setSelectedCardId,
    updateCard,
    getCardsByType
  } = useCards();

  const [viewMode, setViewMode] = useState<ViewMode>('types');
  const [selectedType, setSelectedType] = useState<CardType | null>(null);
  const [editingField, setEditingField] = useState<string | null>(null);
  const [editValue, setEditValue] = useState<string>('');

  const handleTypeClick = (type: CardType) => {
    setSelectedType(type);
    setViewMode('type-list');
  };

  const handleCardClick = (cardId: string) => {
    setSelectedCardId(cardId);
    setViewMode('detail');
  };

  const handleBack = () => {
    if (viewMode === 'detail') {
      setViewMode('type-list');
      setSelectedCardId(null);
      setEditingField(null);
    } else if (viewMode === 'type-list') {
      setViewMode('types');
      setSelectedType(null);
    }
  };

  const handleStartEdit = (field: string, value: string) => {
    setEditingField(field);
    setEditValue(value);
  };

  const handleSaveEdit = (card: CardData, field: string) => {
    if (!card) return;
    
    const updatedCard = { ...card, [field]: editValue };
    updateCard.mutate(updatedCard as CardData);
    setEditingField(null);
  };

  const handleCancelEdit = () => {
    setEditingField(null);
    setEditValue('');
  };

  const cardTypes = Object.values(CardType);

  const getCardSummary = (card: CardData): string => {
    switch (card.type) {
      case CardType.PRODUCT:
        return (card as ProductCard).valueProposition || '';
      case CardType.TARGET:
        return (card as TargetCard).description || '';
      case CardType.CAMPAIGNS:
        return (card as CampaignsCard).keyMessages[0] || '';
      case CardType.TOPIC:
        return (card as TopicCard).description || '';
      case CardType.BRAND_VOICE:
        return (card as BrandVoiceCard).toneDescription || '';
      case CardType.COMPETITOR:
        return (card as CompetitorCard).positioning || '';
      case CardType.PERFORMANCE:
        return (card as PerformanceCard).period || '';
      case CardType.FEEDBACK:
        return (card as FeedbackCard).summary || '';
      default:
        return '';
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-neutral-100">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-neutral-400" />
          <p className="text-neutral-500 text-sm">Caricamento cards...</p>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-neutral-100">
        <Card className="bg-white border-neutral-200 shadow-sm rounded-3xl max-w-md">
          <CardContent className="pt-10 pb-8 px-8 text-center">
            <h2 className="text-xl font-semibold text-neutral-900 mb-2">Errore</h2>
            <p className="text-neutral-500 mb-6">Impossibile caricare le cards</p>
            <Button
              onClick={() => navigate('/onboarding')}
              className="bg-neutral-900 text-white hover:bg-neutral-800 rounded-xl"
              data-testid="button-go-onboarding"
            >
              Vai all'Onboarding
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const renderEditableField = (
    card: CardData,
    field: string,
    value: string,
    label: string,
    multiline: boolean = false
  ) => {
    const isEditing = editingField === field;

    if (isEditing) {
      return (
        <div className="space-y-2">
          <label className="text-xs text-neutral-400 uppercase tracking-wide">{label}</label>
          {multiline ? (
            <Textarea
              value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
              className="bg-neutral-50 border-neutral-200 text-neutral-900 focus:border-neutral-300 focus-visible:ring-0 focus-visible:ring-offset-0 rounded-xl resize-none"
              rows={4}
              autoFocus
              data-testid={`textarea-edit-${field}`}
            />
          ) : (
            <Input
              value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
              className="bg-neutral-50 border-neutral-200 text-neutral-900 focus:border-neutral-300 focus-visible:ring-0 focus-visible:ring-offset-0 rounded-xl"
              autoFocus
              data-testid={`input-edit-${field}`}
            />
          )}
          <div className="flex gap-2">
            <Button
              size="sm"
              onClick={() => handleSaveEdit(card, field)}
              className="bg-neutral-900 text-white hover:bg-neutral-800 rounded-lg text-xs"
              data-testid={`button-save-${field}`}
            >
              Salva
            </Button>
            <Button
              size="sm"
              variant="ghost"
              onClick={handleCancelEdit}
              className="text-neutral-500 hover:text-neutral-700 rounded-lg text-xs"
              data-testid={`button-cancel-${field}`}
            >
              Annulla
            </Button>
          </div>
        </div>
      );
    }

    return (
      <div 
        className="group cursor-pointer hover:bg-neutral-50 rounded-lg p-2 -m-2 transition-colors"
        onClick={() => handleStartEdit(field, value)}
        data-testid={`field-${field}`}
      >
        <label className="text-xs text-neutral-400 uppercase tracking-wide">{label}</label>
        <p className="text-neutral-900 mt-1" data-testid={`text-${field}`}>{value || <span className="text-neutral-300 italic">Clicca per aggiungere</span>}</p>
      </div>
    );
  };

  const renderListField = (
    card: CardData,
    field: string,
    items: string[],
    label: string
  ) => {
    return (
      <div className="space-y-2" data-testid={`list-${field}`}>
        <label className="text-xs text-neutral-400 uppercase tracking-wide">{label}</label>
        <ul className="space-y-1">
          {items.map((item, idx) => (
            <li key={idx} className="text-neutral-700 text-sm flex items-start" data-testid={`list-item-${field}-${idx}`}>
              <span className="text-neutral-300 mr-2">•</span>
              {item}
            </li>
          ))}
        </ul>
      </div>
    );
  };

  const renderProductCard = (card: ProductCard) => (
    <div className="space-y-6">
      {renderEditableField(card, 'valueProposition', card.valueProposition, 'Value Proposition', true)}
      {renderListField(card, 'features', card.features, 'Features')}
      {renderListField(card, 'differentiators', card.differentiators, 'Differenziatori')}
      {renderListField(card, 'useCases', card.useCases, 'Casi d\'uso')}
      
      <div className="space-y-2">
        <label className="text-xs text-neutral-400 uppercase tracking-wide">Metriche</label>
        <div className="grid grid-cols-3 gap-3">
          {card.performanceMetrics.map((metric, idx) => (
            <div key={idx} className="bg-neutral-50 rounded-xl p-3 text-center">
              <p className="text-lg font-semibold text-neutral-900">{metric.value}</p>
              <p className="text-xs text-neutral-500">{metric.metric}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderTargetCard = (card: TargetCard) => (
    <div className="space-y-6">
      {renderEditableField(card, 'icpName', card.icpName, 'Nome ICP')}
      {renderEditableField(card, 'description', card.description, 'Descrizione', true)}
      {renderListField(card, 'painPoints', card.painPoints, 'Pain Points')}
      {renderListField(card, 'goals', card.goals, 'Obiettivi')}
      {renderEditableField(card, 'preferredLanguage', card.preferredLanguage, 'Linguaggio preferito')}
      {renderListField(card, 'communicationChannels', card.communicationChannels, 'Canali')}
      
      {card.demographics && (
        <div className="space-y-2">
          <label className="text-xs text-neutral-400 uppercase tracking-wide">Demographics</label>
          <div className="grid grid-cols-2 gap-3">
            {card.demographics.ageRange && (
              <div className="bg-neutral-50 rounded-xl p-3">
                <p className="text-xs text-neutral-500">Età</p>
                <p className="text-neutral-900">{card.demographics.ageRange}</p>
              </div>
            )}
            {card.demographics.location && (
              <div className="bg-neutral-50 rounded-xl p-3">
                <p className="text-xs text-neutral-500">Location</p>
                <p className="text-neutral-900">{card.demographics.location}</p>
              </div>
            )}
            {card.demographics.role && (
              <div className="bg-neutral-50 rounded-xl p-3">
                <p className="text-xs text-neutral-500">Ruolo</p>
                <p className="text-neutral-900">{card.demographics.role}</p>
              </div>
            )}
            {card.demographics.industry && (
              <div className="bg-neutral-50 rounded-xl p-3">
                <p className="text-xs text-neutral-500">Industry</p>
                <p className="text-neutral-900">{card.demographics.industry}</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );

  const renderCampaignsCard = (card: CampaignsCard) => (
    <div className="space-y-6">
      {renderEditableField(card, 'objective', card.objective, 'Obiettivo', true)}
      {renderListField(card, 'keyMessages', card.keyMessages, 'Messaggi chiave')}
      {renderEditableField(card, 'tone', card.tone, 'Tono')}
      
      <div className="space-y-2">
        <label className="text-xs text-neutral-400 uppercase tracking-wide">Asset</label>
        <div className="space-y-2">
          {card.assets.map((asset, idx) => (
            <div key={idx} className="flex items-center justify-between bg-neutral-50 rounded-xl p-3">
              <div>
                <p className="text-neutral-900 text-sm">{asset.name}</p>
                <p className="text-xs text-neutral-500">{asset.type}</p>
              </div>
              <span className={`text-xs px-2 py-1 rounded-full ${
                asset.status === 'completato' ? 'bg-green-100 text-green-700' :
                asset.status === 'in produzione' ? 'bg-yellow-100 text-yellow-700' :
                asset.status === 'draft' ? 'bg-neutral-100 text-neutral-600' :
                'bg-blue-100 text-blue-700'
              }`}>
                {asset.status}
              </span>
            </div>
          ))}
        </div>
      </div>

      {card.results && card.results.length > 0 && (
        <div className="space-y-2">
          <label className="text-xs text-neutral-400 uppercase tracking-wide">Risultati</label>
          <div className="grid grid-cols-3 gap-3">
            {card.results.map((result, idx) => (
              <div key={idx} className="bg-neutral-50 rounded-xl p-3 text-center">
                <p className="text-lg font-semibold text-neutral-900">{result.value}</p>
                <p className="text-xs text-neutral-500">{result.metric}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {renderListField(card, 'learnings', card.learnings, 'Apprendimenti')}
    </div>
  );

  const renderTopicCard = (card: TopicCard) => (
    <div className="space-y-6">
      {renderEditableField(card, 'description', card.description, 'Descrizione', true)}
      
      <div className="space-y-2">
        <label className="text-xs text-neutral-400 uppercase tracking-wide">Keywords</label>
        <div className="flex flex-wrap gap-2">
          {card.keywords.map((keyword, idx) => (
            <span key={idx} className="bg-neutral-100 text-neutral-700 text-sm px-3 py-1 rounded-full">
              {keyword}
            </span>
          ))}
        </div>
      </div>

      {renderListField(card, 'angles', card.angles, 'Angolazioni')}

      <div className="space-y-2">
        <label className="text-xs text-neutral-400 uppercase tracking-wide">Contenuti correlati</label>
        <div className="space-y-2">
          {card.relatedContent.map((content, idx) => (
            <div key={idx} className="bg-neutral-50 rounded-xl p-3">
              <p className="text-neutral-900 text-sm">{content.title}</p>
              <p className="text-xs text-neutral-500">{content.type}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="space-y-2">
        <label className="text-xs text-neutral-400 uppercase tracking-wide">Trend</label>
        <div className="space-y-2">
          {card.trends.map((trend, idx) => (
            <div key={idx} className="flex items-center justify-between bg-neutral-50 rounded-xl p-3">
              <p className="text-neutral-700 text-sm">{trend.trend}</p>
              <span className={`text-xs px-2 py-1 rounded-full ${
                trend.relevance === 'high' ? 'bg-green-100 text-green-700' :
                trend.relevance === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                'bg-neutral-100 text-neutral-600'
              }`}>
                {trend.relevance}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderBrandVoiceCard = (card: BrandVoiceCard) => (
    <div className="space-y-6">
      {renderEditableField(card, 'toneDescription', card.toneDescription, 'Descrizione tono', true)}
      {renderListField(card, 'styleGuidelines', card.styleGuidelines, 'Linee guida stilistiche')}
      
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <label className="text-xs text-neutral-400 uppercase tracking-wide">Do ✓</label>
          <div className="space-y-2">
            {card.dosExamples.map((example, idx) => (
              <div key={idx} className="bg-green-50 border border-green-100 rounded-xl p-3">
                <p className="text-green-800 text-sm">"{example}"</p>
              </div>
            ))}
          </div>
        </div>
        <div className="space-y-2">
          <label className="text-xs text-neutral-400 uppercase tracking-wide">Don't ✗</label>
          <div className="space-y-2">
            {card.dontsExamples.map((example, idx) => (
              <div key={idx} className="bg-red-50 border border-red-100 rounded-xl p-3">
                <p className="text-red-800 text-sm">"{example}"</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <label className="text-xs text-neutral-400 uppercase tracking-wide">Termini da usare</label>
          <div className="flex flex-wrap gap-2">
            {card.termsToUse.map((term, idx) => (
              <span key={idx} className="bg-green-100 text-green-700 text-sm px-3 py-1 rounded-full">
                {term}
              </span>
            ))}
          </div>
        </div>
        <div className="space-y-2">
          <label className="text-xs text-neutral-400 uppercase tracking-wide">Termini da evitare</label>
          <div className="flex flex-wrap gap-2">
            {card.termsToAvoid.map((term, idx) => (
              <span key={idx} className="bg-red-100 text-red-700 text-sm px-3 py-1 rounded-full line-through">
                {term}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  const renderCompetitorCard = (card: CompetitorCard) => (
    <div className="space-y-6">
      {renderEditableField(card, 'competitorName', card.competitorName, 'Competitor')}
      {renderEditableField(card, 'positioning', card.positioning, 'Posizionamento', true)}
      {renderListField(card, 'keyMessages', card.keyMessages, 'Messaggi chiave')}
      
      <div className="grid grid-cols-2 gap-4">
        <div>
          {renderListField(card, 'strengths', card.strengths, 'Punti di forza')}
        </div>
        <div>
          {renderListField(card, 'weaknesses', card.weaknesses, 'Punti deboli')}
        </div>
      </div>

      {renderListField(card, 'differentiationOpportunities', card.differentiationOpportunities, 'Opportunità di differenziazione')}
    </div>
  );

  const renderPerformanceCard = (card: PerformanceCard) => (
    <div className="space-y-6">
      {renderEditableField(card, 'period', card.period, 'Periodo')}
      
      <div className="space-y-2">
        <label className="text-xs text-neutral-400 uppercase tracking-wide">Metriche per canale</label>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-neutral-100">
                <th className="text-left py-2 text-neutral-500 font-medium">Canale</th>
                <th className="text-left py-2 text-neutral-500 font-medium">Tipo</th>
                <th className="text-right py-2 text-neutral-500 font-medium">CTR</th>
                <th className="text-right py-2 text-neutral-500 font-medium">Engagement</th>
              </tr>
            </thead>
            <tbody>
              {card.metrics.map((metric, idx) => (
                <tr key={idx} className="border-b border-neutral-50">
                  <td className="py-2 text-neutral-900">{metric.channel}</td>
                  <td className="py-2 text-neutral-600">{metric.contentType}</td>
                  <td className="py-2 text-right text-neutral-900">{metric.ctr ? `${metric.ctr}%` : '-'}</td>
                  <td className="py-2 text-right text-neutral-900">{metric.engagement ? `${metric.engagement}%` : '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="space-y-2">
        <label className="text-xs text-neutral-400 uppercase tracking-wide">Top contenuti</label>
        <div className="space-y-2">
          {card.topPerformingContent.map((content, idx) => (
            <div key={idx} className="bg-neutral-50 rounded-xl p-3 flex justify-between items-center">
              <div>
                <p className="text-neutral-900 text-sm">{content.title}</p>
                <p className="text-xs text-neutral-500">{content.type}</p>
              </div>
              <div className="text-right">
                <p className="text-neutral-900 font-medium">{content.value}</p>
                <p className="text-xs text-neutral-500">{content.metric}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {renderListField(card, 'insights', card.insights, 'Insights')}
    </div>
  );

  const renderFeedbackCard = (card: FeedbackCard) => (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <span className={`text-xs px-2 py-1 rounded-full ${
          card.priority === 'high' ? 'bg-red-100 text-red-700' :
          card.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
          'bg-neutral-100 text-neutral-600'
        }`}>
          Priorità {card.priority}
        </span>
        <span className="text-xs text-neutral-500">
          {card.source === 'customer_feedback' ? 'Feedback cliente' :
           card.source === 'team_feedback' ? 'Feedback team' :
           card.source === 'ab_test' ? 'A/B Test' :
           card.source === 'analytics' ? 'Analytics' : 'Altro'}
        </span>
      </div>

      {renderEditableField(card, 'summary', card.summary, 'Sommario', true)}
      {renderEditableField(card, 'details', card.details, 'Dettagli', true)}
      {renderListField(card, 'actionItems', card.actionItems, 'Azioni')}
    </div>
  );

  const renderCardDetail = (card: CardData) => {
    switch (card.type) {
      case CardType.PRODUCT:
        return renderProductCard(card as ProductCard);
      case CardType.TARGET:
        return renderTargetCard(card as TargetCard);
      case CardType.CAMPAIGNS:
        return renderCampaignsCard(card as CampaignsCard);
      case CardType.TOPIC:
        return renderTopicCard(card as TopicCard);
      case CardType.BRAND_VOICE:
        return renderBrandVoiceCard(card as BrandVoiceCard);
      case CardType.COMPETITOR:
        return renderCompetitorCard(card as CompetitorCard);
      case CardType.PERFORMANCE:
        return renderPerformanceCard(card as PerformanceCard);
      case CardType.FEEDBACK:
        return renderFeedbackCard(card as FeedbackCard);
      default:
        return null;
    }
  };

  const getFirstCardByType = (type: CardType): CardData | undefined => {
    return cards.find(card => card.type === type);
  };

  const renderCardGrid = (cardsToRender: CardData[], showTypeAsTitle: boolean = true) => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {cardsToRender.map((card) => {
        const summary = getCardSummary(card);
        const typeLabel = CardTypeLabels[card.type];
        const typeDescription = CardTypeDescriptions[card.type];
        
        return (
          <Card 
            key={card.id}
            className="bg-white border-0 shadow-sm rounded-2xl cursor-pointer hover:shadow-md transition-shadow relative min-h-[200px] flex flex-col"
            data-testid={`card-item-${card.id}`}
          >
            <CardContent className="p-5 flex flex-col flex-1">
              <div className="flex justify-between items-start mb-2">
                <div className="flex-1">
                  <h3 className="text-lg font-bold text-neutral-900">
                    {showTypeAsTitle ? typeLabel : card.title}
                  </h3>
                  <p className="text-sm text-neutral-400 mt-0.5">
                    {showTypeAsTitle ? typeDescription : typeLabel}
                  </p>
                </div>
                <button
                  className="w-8 h-8 flex items-center justify-center rounded-full bg-neutral-100 hover:bg-neutral-200 transition-colors"
                  onClick={(e) => {
                    e.stopPropagation();
                  }}
                  data-testid={`button-menu-${card.id}`}
                >
                  <MoreHorizontal className="w-4 h-4 text-neutral-600" />
                </button>
              </div>
              
              <div className="flex-1 flex flex-col justify-end">
                <p className="text-neutral-700 text-sm leading-relaxed mb-4">
                  {summary || <span className="text-neutral-300">Add Text...</span>}
                </p>
                
                <div className="flex justify-end">
                  <button
                    className="w-10 h-10 flex items-center justify-center rounded-full bg-neutral-900 hover:bg-neutral-800 transition-colors"
                    onClick={(e) => {
                      e.stopPropagation();
                      if (showTypeAsTitle) {
                        handleTypeClick(card.type);
                      } else {
                        handleCardClick(card.id);
                      }
                    }}
                    data-testid={`button-edit-${card.id}`}
                  >
                    <Pencil className="w-4 h-4 text-white" />
                  </button>
                </div>
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );

  const typesWithCards = cardTypes.filter(type => getCardsByType(type).length > 0);
  const firstCardsPerType = typesWithCards
    .map(type => getFirstCardByType(type))
    .filter((card): card is CardData => card !== undefined);

  return (
    <div className="min-h-screen py-12 px-6 bg-neutral-100">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-8">
          <img 
            src={fylleLogo} 
            alt="Fylle" 
            className="h-11 mx-auto"
            data-testid="img-fylle-logo"
          />
        </div>
        
        <AnimatePresence mode="wait">
          {viewMode === 'types' && (
            <motion.div
              key="types"
              variants={cardVariants}
              initial="initial"
              animate="animate"
              exit="exit"
              transition={{ duration: 0.25, ease: 'easeOut' }}
            >
              {renderCardGrid(firstCardsPerType, true)}

              <div className="mt-8 flex justify-end">
                <Button
                  className="bg-neutral-900 text-white hover:bg-neutral-800 rounded-xl px-6"
                  onClick={() => navigate('/onboarding')}
                  data-testid="button-new-onboarding"
                >
                  Add area
                </Button>
              </div>
            </motion.div>
          )}

          {viewMode === 'type-list' && selectedType && (
            <motion.div
              key="type-list"
              variants={cardVariants}
              initial="initial"
              animate="animate"
              exit="exit"
              transition={{ duration: 0.25, ease: 'easeOut' }}
            >
              <div className="mb-6">
                <button
                  onClick={handleBack}
                  className="text-sm text-neutral-500 hover:text-neutral-700 mb-4"
                  data-testid="button-back-to-types"
                >
                  ← Torna alle tipologie
                </button>
                <h2 className="text-2xl font-bold text-neutral-900">
                  {CardTypeLabels[selectedType]}
                </h2>
                <p className="text-neutral-500 mt-1">
                  {CardTypeDescriptions[selectedType]}
                </p>
              </div>

              {renderCardGrid(getCardsByType(selectedType), false)}

              <div className="mt-8 flex justify-end">
                <Button
                  className="bg-neutral-900 text-white hover:bg-neutral-800 rounded-xl px-6"
                  onClick={() => navigate('/onboarding')}
                  data-testid="button-add-card"
                >
                  Aggiungi {CardTypeLabels[selectedType]}
                </Button>
              </div>
            </motion.div>
          )}

          {viewMode === 'detail' && selectedCard && (
            <motion.div
              key="detail"
              variants={cardVariants}
              initial="initial"
              animate="animate"
              exit="exit"
              transition={{ duration: 0.25, ease: 'easeOut' }}
            >
              <Card className="bg-white border-neutral-200 shadow-sm rounded-3xl" data-testid="card-detail">
                <CardContent className="pt-8 pb-8 px-8">
                  <div className="mb-6">
                    <p className="text-xs text-neutral-400 uppercase tracking-wide mb-1">
                      {CardTypeLabels[selectedCard.type]}
                    </p>
                    <h2 className="text-xl font-semibold text-neutral-900">
                      {selectedCard.title}
                    </h2>
                  </div>

                  <div className="border-t border-neutral-100 pt-6">
                    {renderCardDetail(selectedCard)}
                  </div>

                  <div className="flex gap-3 mt-8 pt-6 border-t border-neutral-100">
                    <Button
                      variant="ghost"
                      className="flex-1 h-11 text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900 rounded-xl"
                      onClick={handleBack}
                      data-testid="button-back-to-list"
                    >
                      Indietro
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
