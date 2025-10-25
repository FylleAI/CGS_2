/**
 * CardEditor Component
 * Generic card editor component that dispatches to specific editors
 */

import React, { useEffect, useState } from 'react';
import { CardResponse, CardType, CreateCardRequest, UpdateCardRequest } from '../types/card';
import { useCard } from '../hooks';
import CampaignCardEditor from './CampaignCardEditor';
import PersonaCardEditor from './PersonaCardEditor';
import ProductCardEditor from './ProductCardEditor';
import TopicCardEditor from './TopicCardEditor';

interface CardEditorProps {
  tenantId: string;
  cardId?: string;
  cardType: CardType;
  onSave?: (card: CardResponse) => void;
  onCancel?: () => void;
}

const CardEditor: React.FC<CardEditorProps> = ({
  tenantId,
  cardId,
  cardType,
  onSave,
  onCancel,
}) => {
  const { card, isLoading, error, getCard, createCard, updateCard, clearError } = useCard();
  const [isEditing, setIsEditing] = useState(!cardId);

  useEffect(() => {
    if (cardId) {
      getCard(cardId, tenantId).catch((err) => {
        console.error('Failed to load card:', err);
      });
    }
  }, [cardId, tenantId, getCard]);

  const handleSave = async (request: CreateCardRequest | UpdateCardRequest) => {
    try {
      let savedCard: CardResponse;

      if (cardId) {
        savedCard = await updateCard(cardId, tenantId, request as UpdateCardRequest);
      } else {
        savedCard = await createCard(tenantId, request as CreateCardRequest);
      }

      setIsEditing(false);
      onSave?.(savedCard);
    } catch (err) {
      console.error('Failed to save card:', err);
    }
  };

  const handleCancel = () => {
    setIsEditing(false);
    onCancel?.();
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-gray-500">Loading card...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
        <div className="text-red-800 font-semibold">Error</div>
        <div className="text-red-700 text-sm mt-1">{error}</div>
        <button
          onClick={clearError}
          className="mt-3 px-3 py-1 bg-red-200 hover:bg-red-300 text-red-800 rounded text-sm"
        >
          Dismiss
        </button>
      </div>
    );
  }

  if (!isEditing && card) {
    return (
      <div className="p-4 border rounded-lg bg-gray-50">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h3 className="text-lg font-semibold">{card.title}</h3>
            <p className="text-sm text-gray-600">Version {card.version}</p>
          </div>
          <button
            onClick={() => setIsEditing(true)}
            className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded"
          >
            Edit
          </button>
        </div>
        <div className="text-sm text-gray-700">
          <p>Type: {card.card_type}</p>
          <p>Created: {new Date(card.created_at).toLocaleDateString()}</p>
          {card.notes && <p className="mt-2 italic text-gray-600">{card.notes}</p>}
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 border rounded-lg">
      {cardType === CardType.PRODUCT && (
        <ProductCardEditor
          card={card as any}
          onSave={handleSave}
          onCancel={handleCancel}
        />
      )}
      {cardType === CardType.PERSONA && (
        <PersonaCardEditor
          card={card as any}
          onSave={handleSave}
          onCancel={handleCancel}
        />
      )}
      {cardType === CardType.CAMPAIGN && (
        <CampaignCardEditor
          card={card as any}
          onSave={handleSave}
          onCancel={handleCancel}
        />
      )}
      {cardType === CardType.TOPIC && (
        <TopicCardEditor
          card={card as any}
          onSave={handleSave}
          onCancel={handleCancel}
        />
      )}
    </div>
  );
};

export default CardEditor;

