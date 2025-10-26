/**
 * ProductCardEditor Component
 * Editor for Product cards
 */

import React, { useState } from 'react';
import { ProductCard, ProductContent, CreateCardRequest, UpdateCardRequest, CardType } from '../types/card';

interface ProductCardEditorProps {
  card?: ProductCard;
  onSave: (request: CreateCardRequest | UpdateCardRequest) => Promise<void>;
  onCancel: () => void;
}

const ProductCardEditor: React.FC<ProductCardEditorProps> = ({ card, onSave, onCancel }) => {
  const [formData, setFormData] = useState<ProductContent>(
    card?.content || {
      value_proposition: '',
      features: [],
      differentiators: [],
      use_cases: [],
      target_market: '',
    }
  );

  const [title, setTitle] = useState(card?.title || '');
  const [notes, setNotes] = useState(card?.notes || '');
  const [isSaving, setIsSaving] = useState(false);

  const handleArrayFieldChange = (field: keyof ProductContent, index: number, value: string) => {
    const arr = [...(formData[field] as string[])];
    arr[index] = value;
    setFormData((prev) => ({ ...prev, [field]: arr }));
  };

  const handleAddArrayItem = (field: keyof ProductContent) => {
    setFormData((prev) => ({
      ...prev,
      [field]: [...(prev[field] as string[]), ''],
    }));
  };

  const handleRemoveArrayItem = (field: keyof ProductContent, index: number) => {
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
            card_type: CardType.PRODUCT,
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
        <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Product name"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Value Proposition</label>
        <textarea
          value={formData.value_proposition}
          onChange={(e) => setFormData((prev) => ({ ...prev, value_proposition: e.target.value }))}
          required
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="What makes your product unique?"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Features</label>
        {formData.features.map((feature, idx) => (
          <div key={idx} className="flex gap-2 mb-2">
            <input
              type="text"
              value={feature}
              onChange={(e) => handleArrayFieldChange('features', idx, e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Feature"
            />
            <button
              type="button"
              onClick={() => handleRemoveArrayItem('features', idx)}
              className="px-3 py-2 bg-red-100 hover:bg-red-200 text-red-700 rounded"
            >
              Remove
            </button>
          </div>
        ))}
        <button
          type="button"
          onClick={() => handleAddArrayItem('features')}
          className="px-3 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded text-sm"
        >
          + Add Feature
        </button>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Differentiators</label>
        {formData.differentiators.map((diff, idx) => (
          <div key={idx} className="flex gap-2 mb-2">
            <input
              type="text"
              value={diff}
              onChange={(e) => handleArrayFieldChange('differentiators', idx, e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Differentiator"
            />
            <button
              type="button"
              onClick={() => handleRemoveArrayItem('differentiators', idx)}
              className="px-3 py-2 bg-red-100 hover:bg-red-200 text-red-700 rounded"
            >
              Remove
            </button>
          </div>
        ))}
        <button
          type="button"
          onClick={() => handleAddArrayItem('differentiators')}
          className="px-3 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded text-sm"
        >
          + Add Differentiator
        </button>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Use Cases</label>
        {formData.use_cases.map((useCase, idx) => (
          <div key={idx} className="flex gap-2 mb-2">
            <input
              type="text"
              value={useCase}
              onChange={(e) => handleArrayFieldChange('use_cases', idx, e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Use case"
            />
            <button
              type="button"
              onClick={() => handleRemoveArrayItem('use_cases', idx)}
              className="px-3 py-2 bg-red-100 hover:bg-red-200 text-red-700 rounded"
            >
              Remove
            </button>
          </div>
        ))}
        <button
          type="button"
          onClick={() => handleAddArrayItem('use_cases')}
          className="px-3 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded text-sm"
        >
          + Add Use Case
        </button>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Target Market</label>
        <input
          type="text"
          value={formData.target_market}
          onChange={(e) => setFormData((prev) => ({ ...prev, target_market: e.target.value }))}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Who is your target market?"
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

export default ProductCardEditor;

