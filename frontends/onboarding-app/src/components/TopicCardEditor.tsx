/**
 * TopicCardEditor Component
 * Editor for Topic cards
 */

import React, { useState } from 'react';
import { TopicCard, TopicContent, CreateCardRequest, UpdateCardRequest, CardType } from '../types/card';

interface TopicCardEditorProps {
  card?: TopicCard;
  onSave: (request: CreateCardRequest | UpdateCardRequest) => Promise<void>;
  onCancel: () => void;
}

const TopicCardEditor: React.FC<TopicCardEditorProps> = ({ card, onSave, onCancel }) => {
  const [formData, setFormData] = useState<TopicContent>(
    card?.content || {
      keywords: [],
      angles: [],
      related_content: [],
      trend_status: 'stable',
      frequency: '',
      audience_interest: '',
    }
  );

  const [title, setTitle] = useState(card?.title || '');
  const [notes, setNotes] = useState(card?.notes || '');
  const [isSaving, setIsSaving] = useState(false);

  const handleArrayFieldChange = (field: keyof TopicContent, index: number, value: string) => {
    const arr = [...(formData[field] as string[])];
    arr[index] = value;
    setFormData((prev) => ({ ...prev, [field]: arr }));
  };

  const handleAddArrayItem = (field: keyof TopicContent) => {
    setFormData((prev) => ({
      ...prev,
      [field]: [...(prev[field] as string[]), ''],
    }));
  };

  const handleRemoveArrayItem = (field: keyof TopicContent, index: number) => {
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
            card_type: CardType.TOPIC,
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
        <label className="block text-sm font-medium text-gray-700 mb-1">Topic Name</label>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Topic name"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Keywords</label>
        {formData.keywords.map((keyword, idx) => (
          <div key={idx} className="flex gap-2 mb-2">
            <input
              type="text"
              value={keyword}
              onChange={(e) => handleArrayFieldChange('keywords', idx, e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Keyword"
            />
            <button
              type="button"
              onClick={() => handleRemoveArrayItem('keywords', idx)}
              className="px-3 py-2 bg-red-100 hover:bg-red-200 text-red-700 rounded"
            >
              Remove
            </button>
          </div>
        ))}
        <button
          type="button"
          onClick={() => handleAddArrayItem('keywords')}
          className="px-3 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded text-sm"
        >
          + Add Keyword
        </button>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Angles</label>
        {formData.angles.map((angle, idx) => (
          <div key={idx} className="flex gap-2 mb-2">
            <input
              type="text"
              value={angle}
              onChange={(e) => handleArrayFieldChange('angles', idx, e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Angle"
            />
            <button
              type="button"
              onClick={() => handleRemoveArrayItem('angles', idx)}
              className="px-3 py-2 bg-red-100 hover:bg-red-200 text-red-700 rounded"
            >
              Remove
            </button>
          </div>
        ))}
        <button
          type="button"
          onClick={() => handleAddArrayItem('angles')}
          className="px-3 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded text-sm"
        >
          + Add Angle
        </button>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Related Content</label>
        {formData.related_content.map((content, idx) => (
          <div key={idx} className="flex gap-2 mb-2">
            <input
              type="text"
              value={content}
              onChange={(e) => handleArrayFieldChange('related_content', idx, e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Related content"
            />
            <button
              type="button"
              onClick={() => handleRemoveArrayItem('related_content', idx)}
              className="px-3 py-2 bg-red-100 hover:bg-red-200 text-red-700 rounded"
            >
              Remove
            </button>
          </div>
        ))}
        <button
          type="button"
          onClick={() => handleAddArrayItem('related_content')}
          className="px-3 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded text-sm"
        >
          + Add Content
        </button>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Trend Status</label>
        <select
          value={formData.trend_status}
          onChange={(e) =>
            setFormData((prev) => ({
              ...prev,
              trend_status: e.target.value as 'emerging' | 'stable' | 'declining',
            }))
          }
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="emerging">Emerging</option>
          <option value="stable">Stable</option>
          <option value="declining">Declining</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Frequency</label>
        <input
          type="text"
          value={formData.frequency}
          onChange={(e) => setFormData((prev) => ({ ...prev, frequency: e.target.value }))}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="e.g., Weekly, Monthly, Quarterly"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Audience Interest</label>
        <input
          type="text"
          value={formData.audience_interest}
          onChange={(e) => setFormData((prev) => ({ ...prev, audience_interest: e.target.value }))}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="e.g., High, Medium, Low"
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

export default TopicCardEditor;

