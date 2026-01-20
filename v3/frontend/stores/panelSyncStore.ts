/**
 * ZoneWise V3 - Panel Sync Store
 * Manages state synchronization between Map and Chat panels.
 */

import { create } from 'zustand';

interface Parcel {
  id: string;
  parcel_id: string;
  address: string;
  zone_code: string;
  zone_category: string;
  hbu_score: number;
  foreclosure_status?: string;
  coordinates: [number, number];
}

interface MapHighlight {
  parcel_id: string;
  style: 'primary' | 'secondary' | 'comparison';
  duration_ms?: number;
}

interface ChatContext {
  current_parcel?: string;
  current_address?: string;
  current_zone?: string;
  visible_parcels: string[];
  active_layers: string[];
  map_bounds?: [number, number, number, number];
}

interface SyncEvent {
  type: string;
  payload: Record<string, unknown>;
  timestamp: number;
}

interface PanelSyncState {
  // Selected parcel (shared between panels)
  selectedParcel: Parcel | null;
  setSelectedParcel: (parcel: Parcel | null) => void;

  // Map highlights from chat
  mapHighlights: MapHighlight[];
  setMapHighlights: (highlights: MapHighlight[]) => void;
  clearHighlights: () => void;

  // Chat context from map
  chatContext: ChatContext;
  setChatContext: (context: Partial<ChatContext>) => void;

  // Sync events queue
  eventQueue: SyncEvent[];
  enqueueEvent: (event: SyncEvent) => void;
  dequeueEvent: () => SyncEvent | undefined;
}

export const usePanelSyncStore = create<PanelSyncState>((set, get) => ({
  selectedParcel: null,
  setSelectedParcel: (parcel) => {
    set({ selectedParcel: parcel });
    // Auto-update chat context
    if (parcel) {
      get().setChatContext({
        current_parcel: parcel.id,
        current_address: parcel.address,
        current_zone: parcel.zone_code,
      });
    }
  },

  mapHighlights: [],
  setMapHighlights: (highlights) => set({ mapHighlights: highlights }),
  clearHighlights: () => set({ mapHighlights: [] }),

  chatContext: {
    visible_parcels: [],
    active_layers: ['zoning'],
  },
  setChatContext: (context) =>
    set((state) => ({
      chatContext: { ...state.chatContext, ...context },
    })),

  eventQueue: [],
  enqueueEvent: (event) =>
    set((state) => ({
      eventQueue: [...state.eventQueue, event],
    })),
  dequeueEvent: () => {
    const state = get();
    const [first, ...rest] = state.eventQueue;
    set({ eventQueue: rest });
    return first;
  },
}));
