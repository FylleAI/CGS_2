/**
 * PersonaCardEditor Component
 * Editor for Persona cards
 */

import React, { useState } from 'react';
import { PersonaCard, PersonaContent, CreateCardRequest, UpdateCardRequest, CardType } from '../types/card';

interface PersonaCardEditorProps {
  card?: PersonaCard;
  onSave: (request: CreateCardRequest | UpdateCardRequest) => Promise<void>;
  onCancel: () => void;
}

const PersonaCardEditor: React.FC<PersonaCardEditorProps> = ({ card, onSave, onCancel }) => {
  const [formData, setFormData] = useState<PersonaContent>(
    card?.content || {
      icp_profile: '',
      pain_points: [],
      goals: [],
      preferred_language: '',
      communication_channels: [],
    }
  );

  const [title, setTitle] = useState(card?.title || '');
  const [notes, setNotes] = useState(card?.notes || '');
  const [isSaving, setIsSaving] = useState(false);

  const handleArrayFieldChange = (field: keyof PersonaContent, index: number, value: string) => {
    const arr = [...(formData[field] as string[])];
    arr[index] = value;
    setFormData((prev) => ({ ...prev, [field]: arr }));
  };

  const handleAddArrayItem = (field: keyof PersonaContent) => {
    setFormData((prev) => ({
      ...prev,
      [field]: [...(prev[field] as string[]), ''],
    }));
  };

  const handleRemoveArrayItem = (field: keyof PersonaContent, index: number) => {
    const arr = [...(formData[field] as string[])];
    arr.splice(index, 1);
    setFormData((prev) => ({ ...prev, [field]: arr }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);

    try {
      const request = card
        ? {
            title,
            content: formData,
            notes,
          }
        : {
            card_type: CardType.PERSONA,
            title,
            content: formData,
            notes,
          };

      await onSave(request);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Persona Name</label>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="e.g., Marketing Manager, CTO"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">ICP Profile</label>
        <textarea
          value={formData.icp_profile}
          onChange={(e) => setFormData((prev) => ({ ...prev, icp_profile: e.target.value }))}
          required
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Ideal Customer Profile description"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Pain Points</label>
        {formData.pain_points.map((point, idx) => (
          <div key={idx} className="flex gap-2 mb-2">
            <input
              type="text"
              value={point}
              onChange={(e) => handleArrayFieldChange('pain_points', idx, e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Pain point"
            />
            <button
              type="button"
              onClick={() => handleRemoveArrayItem('pain_points', idx)}
              className="px-3 py-2 bg-red-100 hover:bg-red-200 text-red-700 rounded"
            >
              Remove
            </button>
          </div>
        ))}
        <button
          type="button"
          onClick={() => handleAddArrayItem('pain_points')}
          className="px-3 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded text-sm"
        >
          + Add Pain Point
        </button>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Goals</label>
        {formData.goals.map((goal, idx) => (
          <div key={idx} className="flex gap-2 mb-2">
            <input
              type="text"
              value={goal}
              onChange={(e) => handleArrayFieldChange('goals', idx, e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Goal"
            />
            <button
              type="button"
              onClick={() => handleRemoveArrayItem('goals', idx)}
              className="px-3 py-2 bg-red-100 hover:bg-red-200 text-red-700 rounded"
            >
              Remove
            </button>
          </div>
        ))}
        <button
          type="button"
          onClick={() => handleAddArrayItem('goals')}
          className="px-3 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded text-sm"
        >
          + Add Goal
        </button>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Preferred Language</label>
        <input
          type="text"
          value={formData.preferred_language}
          onChange={(e) => setFormData((prev) => ({ ...prev, preferred_language: e.target.value }))}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="e.g., English, Spanish"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Communication Channels</label>
        {formData.communication_channels.map((channel, idx) => (
          <div key={idx} className="flex gap-2 mb-2">
            <input
              type="text"
              value={channel}
              onChange={(e) => handleArrayFieldChange('communication_channels', idx, e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., Email, LinkedIn, Twitter"
            />
            <button
              type="button"
              onClick={() => handleRemoveArrayItem('communication_channels', idx)}
              className="px-3 py-2 bg-red-100 hover:bg-red-200 text-red-700 rounded"
            >
              Remove
            </button>
          </div>
        ))}
        <button
          type="button"
          onClick={() => handleAddArrayItem('communication_channels')}
          className="px-3 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded text-sm"
        >
          + Add Channel
        </button>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          rows={2}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Additional notes"
        />
      </div>

      <div className="flex gap-3 justify-end">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={isSaving}
          className="px-4 py-2 bg-blue-500 hover:bg-blue-600 disabled:bg-blue-300 text-white rounded-lg"
        >
          {isSaving ? 'Saving...' : 'Save'}
        </button>
      </div>
    </form>
  );
};

export default PersonaCardEditor;

