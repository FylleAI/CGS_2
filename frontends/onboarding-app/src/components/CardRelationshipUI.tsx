/**
 * CardRelationshipUI Component
 * Visualize and manage relationships between cards
 */

import React, { useEffect, useState } from 'react';
import { CardRelationship, CardResponse, CreateRelationshipRequest, RelationshipType } from '../types/card';
import { useCardRelationships } from '../hooks';

interface CardRelationshipUIProps {
  sourceCard: CardResponse;
  tenantId: string;
  allCards: CardResponse[];
  onRelationshipCreated?: (relationship: CardRelationship) => void;
  onRelationshipDeleted?: (relationship: CardRelationship) => void;
}

const CardRelationshipUI: React.FC<CardRelationshipUIProps> = ({
  sourceCard,
  tenantId,
  allCards,
  onRelationshipCreated,
  onRelationshipDeleted,
}) => {
  const { relationships, isLoading, error, getRelationships, createRelationship, deleteRelationship, clearError } =
    useCardRelationships();

  const [showForm, setShowForm] = useState(false);
  const [selectedTargetId, setSelectedTargetId] = useState('');
  const [selectedRelationType, setSelectedRelationType] = useState<RelationshipType>(RelationshipType.LINKS_TO);
  const [strength, setStrength] = useState(1.0);

  useEffect(() => {
    getRelationships(sourceCard.id, tenantId).catch((err) => {
      console.error('Failed to load relationships:', err);
    });
  }, [sourceCard.id, tenantId, getRelationships]);

  const handleCreateRelationship = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedTargetId) {
      alert('Please select a target card');
      return;
    }

    try {
      const request: CreateRelationshipRequest = {
        target_card_id: selectedTargetId,
        relationship_type: selectedRelationType,
        strength,
      };

      const relationship = await createRelationship(sourceCard.id, tenantId, request);
      onRelationshipCreated?.(relationship);
      setShowForm(false);
      setSelectedTargetId('');
      setSelectedRelationType(RelationshipType.LINKS_TO);
      setStrength(1.0);
    } catch (err) {
      console.error('Failed to create relationship:', err);
    }
  };

  const handleDeleteRelationship = async (relationship: CardRelationship) => {
    if (!window.confirm('Delete this relationship?')) {
      return;
    }

    try {
      await deleteRelationship(sourceCard.id, relationship.target_card_id, tenantId);
      onRelationshipDeleted?.(relationship);
    } catch (err) {
      console.error('Failed to delete relationship:', err);
    }
  };

  const getTargetCardTitle = (cardId: string) => {
    return allCards.find((c) => c.id === cardId)?.title || 'Unknown Card';
  };

  const availableTargets = allCards.filter((c) => c.id !== sourceCard.id);

  return (
    <div className="p-4 border rounded-lg bg-gray-50">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">Relationships</h3>
        <button
          onClick={() => setShowForm(!showForm)}
          className="px-3 py-1 bg-blue-500 hover:bg-blue-600 text-white rounded text-sm"
        >
          {showForm ? 'Cancel' : '+ Add Relationship'}
        </button>
      </div>

      {error && (
        <div className="p-3 mb-4 bg-red-50 border border-red-200 rounded">
          <div className="text-red-800 text-sm">{error}</div>
          <button
            onClick={clearError}
            className="mt-2 text-xs text-red-600 hover:text-red-800 underline"
          >
            Dismiss
          </button>
        </div>
      )}

      {showForm && (
        <form onSubmit={handleCreateRelationship} className="p-4 mb-4 bg-white border rounded-lg space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Target Card</label>
            <select
              value={selectedTargetId}
              onChange={(e) => setSelectedTargetId(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select a card...</option>
              {availableTargets.map((card) => (
                <option key={card.id} value={card.id}>
                  {card.title} ({card.card_type})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Relationship Type</label>
            <select
              value={selectedRelationType}
              onChange={(e) => setSelectedRelationType(e.target.value as RelationshipType)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={RelationshipType.TARGETS}>Targets</option>
              <option value={RelationshipType.PROMOTED_IN}>Promoted In</option>
              <option value={RelationshipType.IS_TARGET_OF}>Is Target Of</option>
              <option value={RelationshipType.DISCUSSES}>Discusses</option>
              <option value={RelationshipType.LINKS_TO}>Links To</option>
              <option value={RelationshipType.DERIVES_FROM}>Derives From</option>
              <option value={RelationshipType.SUPPORTS}>Supports</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Strength: {strength.toFixed(1)}
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={strength}
              onChange={(e) => setStrength(parseFloat(e.target.value))}
              className="w-full"
            />
          </div>

          <div className="flex gap-2 justify-end">
            <button
              type="button"
              onClick={() => setShowForm(false)}
              className="px-3 py-2 border border-gray-300 rounded hover:bg-gray-50 text-sm"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-3 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded text-sm"
            >
              Create
            </button>
          </div>
        </form>
      )}

      {isLoading ? (
        <div className="text-gray-500 text-sm">Loading relationships...</div>
      ) : relationships.length === 0 ? (
        <div className="text-gray-500 text-sm italic">No relationships yet</div>
      ) : (
        <div className="space-y-2">
          {relationships.map((rel) => (
            <div key={rel.id} className="p-3 bg-white border rounded flex justify-between items-start">
              <div className="flex-1">
                <div className="font-medium text-sm">
                  {getTargetCardTitle(rel.target_card_id)}
                </div>
                <div className="text-xs text-gray-600 mt-1">
                  <span className="inline-block bg-blue-100 text-blue-800 px-2 py-1 rounded mr-2">
                    {rel.relationship_type}
                  </span>
                  <span className="text-gray-500">Strength: {rel.strength.toFixed(1)}</span>
                </div>
              </div>
              <button
                onClick={() => handleDeleteRelationship(rel)}
                className="px-2 py-1 bg-red-100 hover:bg-red-200 text-red-700 rounded text-xs"
              >
                Delete
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CardRelationshipUI;

