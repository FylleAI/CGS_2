/**
 * UI Store
 * Zustand store for UI state (modals, toasts, etc.)
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

// ============================================================================
// Store Interface
// ============================================================================

interface UIState {
  // Modal state
  isModalOpen: boolean;
  modalContent: React.ReactNode | null;
  
  // Sidebar state
  isSidebarOpen: boolean;
  
  // Theme
  isDarkMode: boolean;
  
  // Actions
  openModal: (content: React.ReactNode) => void;
  closeModal: () => void;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  toggleDarkMode: () => void;
}

// ============================================================================
// Store
// ============================================================================

export const useUIStore = create<UIState>()(
  devtools(
    (set) => ({
      // Initial state
      isModalOpen: false,
      modalContent: null,
      isSidebarOpen: false,
      isDarkMode: false,
      
      // Actions
      openModal: (content) =>
        set({
          isModalOpen: true,
          modalContent: content,
        }),
      
      closeModal: () =>
        set({
          isModalOpen: false,
          modalContent: null,
        }),
      
      toggleSidebar: () =>
        set((state) => ({
          isSidebarOpen: !state.isSidebarOpen,
        })),
      
      setSidebarOpen: (open) =>
        set({ isSidebarOpen: open }),
      
      toggleDarkMode: () =>
        set((state) => ({
          isDarkMode: !state.isDarkMode,
        })),
    }),
    { name: 'UIStore' }
  )
);

export default useUIStore;

