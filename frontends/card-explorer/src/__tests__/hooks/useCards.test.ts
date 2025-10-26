/**
 * Tests for useCards hook
 */

import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useCards, useCreateCard, useUpdateCard, useDeleteCard } from '../../hooks/useCards';
import * as cardApi from '../../services/cardApi';

// Mock the API
jest.mock('../../services/cardApi');

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe('useCards', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should fetch cards successfully', async () => {
    const mockCards = [
      {
        id: 'card-1',
        card_type: 'product',
        title: 'Test Product',
        content: { product_name: 'Test' },
        is_active: true,
        version: 1,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
    ];

    (cardApi.cardApi.listCards as jest.Mock).mockResolvedValue(mockCards);

    const { result } = renderHook(() => useCards(), { wrapper: createWrapper() });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual(mockCards);
  });

  it('should handle fetch error', async () => {
    const error = new Error('Failed to fetch cards');
    (cardApi.cardApi.listCards as jest.Mock).mockRejectedValue(error);

    const { result } = renderHook(() => useCards(), { wrapper: createWrapper() });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error).toBeDefined();
  });

  it('should return loading state initially', () => {
    (cardApi.cardApi.listCards as jest.Mock).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );

    const { result } = renderHook(() => useCards(), { wrapper: createWrapper() });

    expect(result.current.isLoading).toBe(true);
  });
});

describe('useCreateCard', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should create card successfully', async () => {
    const newCard = {
      card_type: 'product',
      title: 'New Product',
      content: { product_name: 'New' },
    };

    const createdCard = {
      id: 'card-1',
      ...newCard,
      is_active: true,
      version: 1,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    (cardApi.cardApi.createCard as jest.Mock).mockResolvedValue(createdCard);

    const { result } = renderHook(() => useCreateCard(), { wrapper: createWrapper() });

    result.current.mutate(newCard as any);

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual(createdCard);
  });

  it('should handle creation error', async () => {
    const error = new Error('Failed to create card');
    (cardApi.cardApi.createCard as jest.Mock).mockRejectedValue(error);

    const { result } = renderHook(() => useCreateCard(), { wrapper: createWrapper() });

    result.current.mutate({} as any);

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });
  });
});

describe('useUpdateCard', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should update card successfully', async () => {
    const cardId = 'card-1';
    const updates = { title: 'Updated Title' };

    const updatedCard = {
      id: cardId,
      card_type: 'product',
      title: 'Updated Title',
      content: { product_name: 'Test' },
      is_active: true,
      version: 2,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    (cardApi.cardApi.updateCard as jest.Mock).mockResolvedValue(updatedCard);

    const { result } = renderHook(() => useUpdateCard(), { wrapper: createWrapper() });

    result.current.mutate({ cardId, ...updates } as any);

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual(updatedCard);
  });
});

describe('useDeleteCard', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should delete card successfully', async () => {
    const cardId = 'card-1';

    (cardApi.cardApi.deleteCard as jest.Mock).mockResolvedValue({ success: true });

    const { result } = renderHook(() => useDeleteCard(), { wrapper: createWrapper() });

    result.current.mutate(cardId);

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });
  });

  it('should handle deletion error', async () => {
    const error = new Error('Failed to delete card');
    (cardApi.cardApi.deleteCard as jest.Mock).mockRejectedValue(error);

    const { result } = renderHook(() => useDeleteCard(), { wrapper: createWrapper() });

    result.current.mutate('card-1');

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });
  });
});

