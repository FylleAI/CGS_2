import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { AppState, ClientProfile, WorkflowType, RAGContent } from '../types';

interface AppStore extends AppState {
  // Actions
  setSelectedClient: (client: ClientProfile | null) => void;
  setSelectedWorkflow: (workflow: WorkflowType | null) => void;
  setAvailableClients: (clients: ClientProfile[]) => void;
  setAvailableWorkflows: (workflows: WorkflowType[]) => void;
  setRAGContents: (contents: RAGContent[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  resetState: () => void;
}

const initialState: AppState = {
  selectedClient: null,
  selectedWorkflow: null,
  availableClients: [],
  availableWorkflows: [],
  ragContents: [],
  isLoading: false,
  error: null,
};

export const useAppStore = create<AppStore>()(
  devtools(
    (set, get) => ({
      ...initialState,

      setSelectedClient: (client) => {
        set({ selectedClient: client });
        // Reset workflow when client changes
        if (client?.name !== get().selectedClient?.name) {
          set({ selectedWorkflow: null });
        }
      },

      setSelectedWorkflow: (workflow) => {
        set({ selectedWorkflow: workflow });
      },

      setAvailableClients: (clients) => {
        set({ availableClients: clients });
      },

      setAvailableWorkflows: (workflows) => {
        set({ availableWorkflows: workflows });
      },

      setRAGContents: (contents) => {
        set({ ragContents: contents });
      },

      setLoading: (loading) => {
        set({ isLoading: loading });
      },

      setError: (error) => {
        set({ error });
      },

      resetState: () => {
        set(initialState);
      },
    }),
    {
      name: 'cgsref-store',
    }
  )
);
