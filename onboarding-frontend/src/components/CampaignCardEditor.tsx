/**
 * CampaignCardEditor Component
 * Editor for Campaign cards
 */

import React, { useState } from 'react';
import { CampaignCard, CampaignContent, CreateCardRequest, UpdateCardRequest, CardType } from '../types/card';

interface CampaignCardEditorProps {
  card?: CampaignCard;
  onSave: (request: CreateCardRequest | UpdateCardRequest) => Promise<void>;
  onCancel: () => void;
}

const CampaignCardEditor: React.FC<CampaignCardEditorProps> = ({ card, onSave, onCancel }) => {
  const [formData, setFormData] = useState<CampaignContent>(
    card?.content || {
      objective: '',
      key_messages: [],
      tone: '',
      target_personas: [],
      assets_produced: [],
      results: '',
      learnings: '',
    }
  );

  const [title, setTitle] = useState(card?.title || '');
  const [notes, setNotes] = useState(card?.notes || '');
  const [isSaving, setIsSaving] = useState(false);

  const handleArrayFieldChange = (field: keyof CampaignContent, index: number, value: string) => {
    const arr = [...(formData[field] as string[])];
    arr[index] = value;
    setFormData((prev) => ({ ...prev, [field]: arr }));
  };

  const handleAddArrayItem = (field: keyof CampaignContent) => {
    setFormData((prev) => ({
      ...prev,
      [field]: [...(prev[field] as string[]), ''],
    }));
  };

  const handleRemoveArrayItem = (field: keyof CampaignContent, index: number) => {
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
            card_type: CardType.CAMPAIGN,
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
        <label className="block text-sm font-medium text-gray-700 mb-1">Campaign Name</label>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Campaign name"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Objective</label>
        <textarea
          value={formData.objective}
          onChange={(e) => setFormData((prev) => ({ ...prev, objective: e.target.value }))}
          required
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="What is the campaign objective?"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Key Messages</label>
        {formData.key_messages.map((msg, idx) => (
          <div key={idx} className="flex gap-2 mb-2">
            <input
              type="text"
              value={msg}
              onChange={(e) => handleArrayFieldChange('key_messages', idx, e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Key message"
            />
            <button
              type="button"
              onClick={() => handleRemoveArrayItem('key_messages', idx)}
              className="px-3 py-2 bg-red-100 hover:bg-red-200 text-red-700 rounded"
            >
              Remove
            </button>
          </div>
        ))}
        <button
          type="button"
          onClick={() => handleAddArrayItem('key_messages')}
          className="px-3 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded text-sm"
        >
          + Add Message
        </button>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Tone</label>
        <input
          type="text"
          value={formData.tone}
          onChange={(e) => setFormData((prev) => ({ ...prev, tone: e.target.value }))}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="e.g., Professional, Casual, Humorous"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Target Personas</label>
        {formData.target_personas.map((persona, idx) => (
          <div key={idx} className="flex gap-2 mb-2">
            <input
              type="text"
              value={persona}
              onChange={(e) => handleArrayFieldChange('target_personas', idx, e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Target persona"
            />
            <button
              type="button"
              onClick={() => handleRemoveArrayItem('target_personas', idx)}
              className="px-3 py-2 bg-red-100 hover:bg-red-200 text-red-700 rounded"
            >
              Remove
            </button>
          </div>
        ))}
        <button
          type="button"
          onClick={() => handleAddArrayItem('target_personas')}
          className="px-3 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded text-sm"
        >
          + Add Persona
        </button>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Assets Produced</label>
        {formData.assets_produced.map((asset, idx) => (
          <div key={idx} className="flex gap-2 mb-2">
            <input
              type="text"
              value={asset}
              onChange={(e) => handleArrayFieldChange('assets_produced', idx, e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Asset type"
            />
            <button
              type="button"
              onClick={() => handleRemoveArrayItem('assets_produced', idx)}
              className="px-3 py-2 bg-red-100 hover:bg-red-200 text-red-700 rounded"
            >
              Remove
            </button>
          </div>
        ))}
        <button
          type="button"
          onClick={() => handleAddArrayItem('assets_produced')}
          className="px-3 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded text-sm"
        >
          + Add Asset
        </button>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Results</label>
        <textarea
          value={formData.results || ''}
          onChange={(e) => setFormData((prev) => ({ ...prev, results: e.target.value }))}
          rows={2}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Campaign results"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Learnings</label>
        <textarea
          value={formData.learnings || ''}
          onChange={(e) => setFormData((prev) => ({ ...prev, learnings: e.target.value }))}
          rows={2}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Key learnings"
        />
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

export default CampaignCardEditor;

