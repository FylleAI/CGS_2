/**
 * Cards Page for Fylle Onboarding v3
 * Displays user's cards with Packs section below
 */

import { useState, useMemo } from 'react';
import { useLocation } from 'wouter';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Loader2, Pencil, MoreHorizontal } from 'lucide-react';
import { useCards } from '@/hooks/useCards';
import { CardType, CardTypeLabels, CardTypeDescriptions } from '@shared/types/cards';
import type { Card as CardData } from '@shared/types/cards';
import { DEFAULT_PACKS } from '@shared/types/packs';

const fylleLogo = '/assets/fylle-logotipo-green.png';

function getQueryParam(name: string): string | null {
  if (typeof window === 'undefined') return null;
  const params = new URLSearchParams(window.location.search);
  return params.get(name);
}

const cardVariants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 }
};

export default function CardsPage() {
  const [, navigate] = useLocation();
  const userId = getQueryParam('user_id');
  
  const { cards, isLoading, isError, selectedCardId, setSelectedCardId, getCardsByType } = useCards({ userId });
  
  const [viewMode, setViewMode] = useState<'types' | 'type-list' | 'detail'>('types');
  const [selectedType, setSelectedType] = useState<CardType | null>(null);

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
    } else if (viewMode === 'type-list') {
      setViewMode('types');
      setSelectedType(null);
    }
  };

  const getCardSummary = (card: CardData): string => {
    switch (card.type) {
      case CardType.PRODUCT:
        return (card as any).valueProposition || '';
      case CardType.TARGET:
        return (card as any).description || '';
      case CardType.BRAND_VOICE:
        return (card as any).toneDescription || '';
      default:
        return '';
    }
  };

  const cardTypes = Object.values(CardType);
  const typesWithCards = cardTypes.filter(type => getCardsByType(type).length > 0);
  const firstCardsPerType = typesWithCards
    .map(type => getCardsByType(type)[0])
    .filter((card): card is CardData => card !== undefined);

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

  if (isError || cards.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-neutral-100">
        <Card className="bg-white border-neutral-200 shadow-sm rounded-3xl max-w-md">
          <CardContent className="pt-10 pb-8 px-8 text-center">
            <h2 className="text-xl font-semibold text-neutral-900 mb-2">Nessuna card trovata</h2>
            <p className="text-neutral-500 mb-6">Completa l'onboarding per generare le tue cards</p>
            <Button
              onClick={() => navigate('/onboarding')}
              className="bg-neutral-900 text-white hover:bg-neutral-800 rounded-xl"
            >
              Vai all'Onboarding
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const renderCardGrid = (cardsToRender: CardData[]) => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {cardsToRender.map((card) => {
        const summary = getCardSummary(card);
        const typeLabel = CardTypeLabels[card.type];
        const typeDescription = CardTypeDescriptions[card.type];
        
        return (
          <Card 
            key={card.id}
            className="bg-white border-0 shadow-sm rounded-2xl cursor-pointer hover:shadow-md transition-shadow"
          >
            <CardContent className="p-5">
              <div className="flex justify-between items-start mb-2">
                <div>
                  <h3 className="text-lg font-bold text-neutral-900">{typeLabel}</h3>
                  <p className="text-sm text-neutral-400">{typeDescription}</p>
                </div>
                <button className="w-8 h-8 flex items-center justify-center rounded-full bg-neutral-100 hover:bg-neutral-200">
                  <MoreHorizontal className="w-4 h-4 text-neutral-600" />
                </button>
              </div>
              
              <p className="text-neutral-700 text-sm leading-relaxed mb-4">
                {summary || <span className="text-neutral-300">Add Text...</span>}
              </p>
              
              <div className="flex justify-end">
                <button
                  onClick={() => handleTypeClick(card.type)}
                  className="w-10 h-10 flex items-center justify-center rounded-full bg-neutral-900 hover:bg-neutral-800"
                >
                  <Pencil className="w-4 h-4 text-white" />
                </button>
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );

  const renderPacksSection = () => (
    <div className="mt-12">
      <h2 className="text-2xl font-bold text-neutral-900 mb-6">Content Packs</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {DEFAULT_PACKS.map((pack) => (
          <Card 
            key={pack.id}
            className="bg-white border-0 shadow-sm rounded-2xl cursor-pointer hover:shadow-md transition-shadow"
            onClick={() => navigate(`/packs?pack_id=${pack.id}&user_id=${userId}`)}
          >
            <CardContent className="p-6">
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 bg-neutral-100 rounded-xl flex items-center justify-center text-2xl">
                  {pack.icon}
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-neutral-900">{pack.displayName}</h3>
                  <p className="text-sm text-neutral-500">{pack.description}</p>
                </div>
                <Button className="bg-neutral-900 hover:bg-neutral-800 rounded-xl">
                  Attiva
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );

  return (
    <div className="min-h-screen py-12 px-6 bg-neutral-100">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-8">
          <img src={fylleLogo} alt="Fylle" className="h-11 mx-auto" />
        </div>

        <AnimatePresence mode="wait">
          {viewMode === 'types' && (
            <motion.div
              key="types"
              variants={cardVariants}
              initial="initial"
              animate="animate"
              exit="exit"
            >
              {renderCardGrid(firstCardsPerType)}
              {renderPacksSection()}
            </motion.div>
          )}

          {viewMode === 'type-list' && selectedType && (
            <motion.div
              key="type-list"
              variants={cardVariants}
              initial="initial"
              animate="animate"
              exit="exit"
            >
              <button onClick={handleBack} className="text-sm text-neutral-500 hover:text-neutral-700 mb-4">
                ← Torna alle tipologie
              </button>
              <h2 className="text-2xl font-bold text-neutral-900 mb-6">{CardTypeLabels[selectedType]}</h2>
              {renderCardGrid(getCardsByType(selectedType))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
