/**
 * ZoneWise V3 - Panel Sync Store
 * Zustand store for synchronizing state between MapPanel and ChatPanel.
 */

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

interface MapViewport {
  center: [number, number];
  zoom: number;
  bounds?: [[number, number], [number, number]];
}

interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

interface PanelSyncState {
  // Map State
  selectedParcelId: string | null;
  mapViewport: MapViewport | null;
  activeLayers: string[];
  zoneFilter: string[];
  
  // Chat State
  conversationHistory: Message[];
  lastQuery: string | null;
  
  // Session
  sessionId: string | null;
  
  // Actions
  setSelectedParcelId: (id: string | null) => void;
  setMapViewport: (viewport: MapViewport) => void;
  setActiveLayers: (layers: string[]) => void;
  toggleLayer: (layer: string) => void;
  setZoneFilter: (zones: string[]) => void;
  setConversationHistory: (messages: Message[]) => void;
  addMessage: (message: Message) => void;
  setLastQuery: (query: string | null) => void;
  setSessionId: (id: string) => void;
  reset: () => void;
}

const initialState = {
  selectedParcelId: null,
  mapViewport: null,
  activeLayers: ['parcels', 'zoning'],
  zoneFilter: [],
  conversationHistory: [],
  lastQuery: null,
  sessionId: null,
};

export const usePanelSyncStore = create<PanelSyncState>()(
  persist(
    (set, get) => ({
      ...initialState,

      setSelectedParcelId: (id) => set({ selectedParcelId: id }),

      setMapViewport: (viewport) => set({ mapViewport: viewport }),

      setActiveLayers: (layers) => set({ activeLayers: layers }),

      toggleLayer: (layer) => {
        const current = get().activeLayers;
        if (current.includes(layer)) {
          set({ activeLayers: current.filter(l => l !== layer) });
        } else {
          set({ activeLayers: [...current, layer] });
        }
      },

      setZoneFilter: (zones) => set({ zoneFilter: zones }),

      setConversationHistory: (messages) => set({ conversationHistory: messages }),

      addMessage: (message) => {
        const current = get().conversationHistory;
        set({ conversationHistory: [...current.slice(-50), message] }); // Keep last 50
      },

      setLastQuery: (query) => set({ lastQuery: query }),

      setSessionId: (id) => set({ sessionId: id }),

      reset: () => set(initialState),
    }),
    {
      name: 'zonewise-panel-sync',
      storage: createJSONStorage(() => sessionStorage),
      partialize: (state) => ({
        selectedParcelId: state.selectedParcelId,
        mapViewport: state.mapViewport,
        activeLayers: state.activeLayers,
        sessionId: state.sessionId,
      }),
    }
  )
);

// Selector hooks for performance
export const useSelectedParcel = () => usePanelSyncStore((s) => s.selectedParcelId);
export const useMapViewport = () => usePanelSyncStore((s) => s.mapViewport);
export const useActiveLayers = () => usePanelSyncStore((s) => s.activeLayers);
export const useConversationHistory = () => usePanelSyncStore((s) => s.conversationHistory);

export default usePanelSyncStore;
