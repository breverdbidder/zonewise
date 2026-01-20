# ZoneWise Product Requirements Specification (PRS) V3.0
## Technical Implementation for Split-Screen AI Platform

**Product:** ZoneWise  
**Version:** 3.0.0  
**Date:** January 20, 2026  
**Author:** Claude AI Architect  
**Status:** Technical Specification - Ready for Implementation

---

# CHANGELOG V3.0

| Component | V2.0 | V3.0 | Impact |
|-----------|------|------|--------|
| Frontend Framework | React + Vite | **Next.js 15 + ShadCNBlocks** | Unified stack |
| UI Library | Custom components | **ShadCNBlocks Premium ($149)** | 959+ components |
| Map Provider | Basic Mapbox | **Mapbox GL JS + PostGIS** | Reventure.app parity |
| Agent Framework | LangGraph | **OpenManus Multi-Agent** | Parallel execution |
| Layout | Chat-only | **Split-Screen (60/40)** | Visual + conversational |
| Data Layers | Single layer | **7 choropleth layers** | Rich visualization |

---

# TABLE OF CONTENTS

1. [System Architecture](#1-system-architecture)
2. [Frontend Specifications](#2-frontend-specifications)
3. [Split-Screen Implementation](#3-split-screen-implementation)
4. [Mapbox Integration](#4-mapbox-integration)
5. [NLP Chatbot Specifications](#5-nlp-chatbot-specifications)
6. [OpenManus Agent System](#6-openmanus-agent-system)
7. [Database Schema](#7-database-schema)
8. [API Specifications](#8-api-specifications)
9. [Data Pipeline](#9-data-pipeline)
10. [Deployment Architecture](#10-deployment-architecture)
11. [Testing Specifications](#11-testing-specifications)
12. [Performance Requirements](#12-performance-requirements)

---

# 1. SYSTEM ARCHITECTURE

## 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE LAYER                             │
│  ┌─────────────────────────────┐   ┌─────────────────────────────────┐  │
│  │   MAP PANEL (60%)           │   │   CHAT PANEL (40%)              │  │
│  │   • Mapbox GL JS            │   │   • ShadCNBlocks Chat UI        │  │
│  │   • Choropleth layers       │   │   • Message history             │  │
│  │   • Parcel selection        │   │   • Suggested actions           │  │
│  │   • Geographic drill-down   │   │   • Voice input (optional)      │  │
│  └─────────────────────────────┘   └─────────────────────────────────┘  │
│                    ShadCNBlocks Premium + Next.js 15                     │
│                    Hosting: Cloudflare Pages (Global CDN)                │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓ WebSocket + REST
┌─────────────────────────────────────────────────────────────────────────┐
│                         API GATEWAY LAYER                                │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │   FastAPI Server (Python 3.11+)                                 │    │
│  │   • /api/v1/chat - Chat endpoint                                │    │
│  │   • /api/v1/map - Map data endpoint                             │    │
│  │   • /api/v1/parcels - Parcel queries                            │    │
│  │   • /api/v1/analysis - HBU/CMA/ML                               │    │
│  │   • /ws/chat - WebSocket for real-time chat                     │    │
│  │   Hosting: Render.com (Auto-scaling Docker)                     │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                      OPENMANUS ORCHESTRATION LAYER                       │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │   Coordinator Agent (Claude Sonnet 4.5)                         │    │
│  │   ├── Zoning Agent (Gemini 2.5 Flash) - Zone lookup             │    │
│  │   ├── CMA Agent (Gemini 2.5 Flash) - Comparables                │    │
│  │   ├── HBU Agent (Claude Sonnet 4.5) - Best use analysis         │    │
│  │   ├── ML Agent (XGBoost local) - Price prediction               │    │
│  │   ├── Browser Agent (Playwright) - Web scraping                 │    │
│  │   └── Reporter Agent (Claude Sonnet 4.5) - Response synthesis   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                         DATABASE LAYER                                   │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │   Supabase PostgreSQL + PostGIS + pgvector                      │    │
│  │   • fl_parcels (10M rows, geometry)                             │    │
│  │   • fl_zoning_districts (GIS polygons)                          │    │
│  │   • chatbot_conversations, chatbot_messages                     │    │
│  │   • map_sessions, user_preferences                              │    │
│  │   • embeddings (pgvector for RAG)                               │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                         DATA SOURCES                                     │
│  • BCPAO API (parcels, FREE)           • Zillow CSVs (FREE)             │
│  • Census TigerLine (ZIP boundaries)   • Firecrawl (ordinances)         │
│  • Municode/AmLegal (zoning codes)     • RealForeclose (auctions)       │
└─────────────────────────────────────────────────────────────────────────┘
```

## 1.2 Technology Stack Summary

| Layer | Technology | Version | Purpose |
|-------|------------|---------|---------|
| **Frontend** | Next.js | 15.x | React framework, App Router |
| **UI Library** | ShadCNBlocks Premium | Latest | 959+ components, Zippay/Admin templates |
| **Styling** | Tailwind CSS | 4.x | Utility-first CSS |
| **Maps** | Mapbox GL JS | 3.x | Interactive choropleth maps |
| **State** | Zustand | 4.x | Client state management |
| **Backend** | FastAPI | 0.110+ | Async Python API |
| **Agents** | OpenManus | Latest | Multi-agent orchestration |
| **LLM Primary** | Gemini 2.5 Flash | Latest | 90% FREE tier |
| **LLM Complex** | Claude Sonnet 4.5 | Latest | Complex reasoning |
| **ML** | XGBoost | 2.x | Price prediction |
| **Database** | Supabase PostgreSQL | 15+ | PostGIS + pgvector |
| **Hosting** | Cloudflare Pages | - | Frontend CDN |
| **API Hosting** | Render.com | - | Auto-scaling containers |

---

# 2. FRONTEND SPECIFICATIONS

## 2.1 ShadCNBlocks Integration

### Template Mapping

| ZoneWise Feature | ShadCNBlocks Component | Template |
|------------------|------------------------|----------|
| Landing Page | Hero, Features, Pricing | **Zippay** |
| Dashboard Shell | Sidebar, Header, Layout | **Admin Dashboard** |
| Chat Interface | Chat bubbles, Input, Actions | **Custom + Blocks** |
| Data Tables | DataTable, Filters, Pagination | **Admin Dashboard** |
| Charts | Area, Bar, Line (Recharts) | **Admin Dashboard** |
| Forms | Input, Select, DatePicker | **Core Components** |
| Modals | Dialog, Sheet, Drawer | **Core Components** |

### Project Initialization

```bash
# Initialize Next.js with ShadCNBlocks
npx create-next-app@latest zonewise --typescript --tailwind --eslint --app

# Initialize shadcn/ui with Lyra style (professional boxy look)
npx shadcn init --style lyra --base-color slate --css-variables

# Install ShadCNBlocks components via CLI
npx shadcn add sidebar command dialog sheet data-table

# Install additional dependencies
npm install @mapbox/mapbox-gl-geocoder mapbox-gl react-map-gl
npm install zustand @tanstack/react-query axios
npm install recharts lucide-react
```

### Directory Structure

```
zonewise-frontend/
├── app/
│   ├── (marketing)/
│   │   ├── page.tsx              # Landing page (Zippay template)
│   │   ├── pricing/page.tsx      # Pricing page
│   │   └── features/page.tsx     # Features page
│   ├── (dashboard)/
│   │   ├── layout.tsx            # Split-screen layout
│   │   ├── page.tsx              # Main dashboard (map + chat)
│   │   ├── parcels/page.tsx      # Parcel data table
│   │   ├── analysis/page.tsx     # Analysis history
│   │   └── settings/page.tsx     # User settings
│   └── api/
│       ├── chat/route.ts         # Chat API proxy
│       └── map/route.ts          # Map data proxy
├── components/
│   ├── map/
│   │   ├── MapPanel.tsx          # Main map container
│   │   ├── MapControls.tsx       # Layer toggles, zoom
│   │   ├── ParcelPopup.tsx       # Parcel info popup
│   │   ├── ChoroplethLegend.tsx  # Color scale legend
│   │   └── GeographicNav.tsx     # State→County→ZIP nav
│   ├── chat/
│   │   ├── ChatPanel.tsx         # Main chat container
│   │   ├── MessageList.tsx       # Conversation history
│   │   ├── MessageInput.tsx      # User input
│   │   ├── SuggestedActions.tsx  # Quick action buttons
│   │   └── TypingIndicator.tsx   # AI thinking state
│   ├── ui/                       # ShadCNBlocks components
│   └── shared/
│       ├── SplitScreen.tsx       # Split-screen layout
│       └── PanelSync.tsx         # Map-chat synchronization
├── hooks/
│   ├── useMapState.ts            # Map state management
│   ├── useChatSession.ts         # Chat state management
│   ├── usePanelSync.ts           # Bidirectional sync
│   └── useParcelSelection.ts     # Selected parcel state
├── stores/
│   ├── mapStore.ts               # Zustand map store
│   └── chatStore.ts              # Zustand chat store
├── lib/
│   ├── mapbox.ts                 # Mapbox configuration
│   ├── api.ts                    # API client
│   └── utils.ts                  # Utility functions
└── styles/
    └── globals.css               # Tailwind + custom styles
```

## 2.2 Component Specifications

### SplitScreen Component

```typescript
// components/shared/SplitScreen.tsx
'use client';

import { useState, useCallback } from 'react';
import { cn } from '@/lib/utils';
import { MapPanel } from '@/components/map/MapPanel';
import { ChatPanel } from '@/components/chat/ChatPanel';
import { usePanelSync } from '@/hooks/usePanelSync';

interface SplitScreenProps {
  defaultMapWidth?: number; // Percentage 0-100
  minMapWidth?: number;
  maxMapWidth?: number;
}

export function SplitScreen({
  defaultMapWidth = 60,
  minMapWidth = 40,
  maxMapWidth = 75,
}: SplitScreenProps) {
  const [mapWidth, setMapWidth] = useState(defaultMapWidth);
  const [isDragging, setIsDragging] = useState(false);
  
  // Bidirectional sync hook
  const { 
    selectedParcel, 
    setSelectedParcel,
    mapHighlights,
    setMapHighlights,
    chatContext,
    setChatContext,
  } = usePanelSync();

  const handleDragStart = useCallback(() => setIsDragging(true), []);
  const handleDragEnd = useCallback(() => setIsDragging(false), []);
  
  const handleDrag = useCallback((e: MouseEvent) => {
    if (!isDragging) return;
    const newWidth = (e.clientX / window.innerWidth) * 100;
    setMapWidth(Math.min(maxMapWidth, Math.max(minMapWidth, newWidth)));
  }, [isDragging, minMapWidth, maxMapWidth]);

  return (
    <div className="flex h-screen w-full overflow-hidden">
      {/* Map Panel */}
      <div 
        className="relative h-full overflow-hidden"
        style={{ width: `${mapWidth}%` }}
      >
        <MapPanel
          onParcelSelect={setSelectedParcel}
          highlights={mapHighlights}
          onContextChange={setChatContext}
        />
      </div>
      
      {/* Resizer */}
      <div
        className={cn(
          "w-1 cursor-col-resize bg-border hover:bg-primary/50 transition-colors",
          isDragging && "bg-primary"
        )}
        onMouseDown={handleDragStart}
      />
      
      {/* Chat Panel */}
      <div 
        className="relative h-full overflow-hidden"
        style={{ width: `${100 - mapWidth}%` }}
      >
        <ChatPanel
          selectedParcel={selectedParcel}
          context={chatContext}
          onMapAction={setMapHighlights}
        />
      </div>
    </div>
  );
}
```

### Responsive Behavior

```typescript
// hooks/useResponsiveLayout.ts
import { useMediaQuery } from '@/hooks/useMediaQuery';

export function useResponsiveLayout() {
  const isDesktop = useMediaQuery('(min-width: 1200px)');
  const isTablet = useMediaQuery('(min-width: 768px)');
  const isMobile = useMediaQuery('(max-width: 767px)');
  
  if (isMobile) {
    return {
      layout: 'stacked',
      mapWidth: 100,
      chatWidth: 100,
      showTabs: true,
    };
  }
  
  if (isTablet) {
    return {
      layout: 'side-by-side',
      mapWidth: 50,
      chatWidth: 50,
      showTabs: false,
    };
  }
  
  return {
    layout: 'side-by-side',
    mapWidth: 60,
    chatWidth: 40,
    showTabs: false,
  };
}
```

---

# 3. SPLIT-SCREEN IMPLEMENTATION

## 3.1 Panel Synchronization Protocol

### Map → Chat Events

```typescript
// Event: Parcel selected on map
interface ParcelSelectedEvent {
  type: 'PARCEL_SELECTED';
  payload: {
    parcel_id: string;
    address: string;
    zone_code: string;
    coordinates: [number, number];
    properties: ParcelProperties;
  };
}

// Event: Region changed (zoom/pan)
interface RegionChangedEvent {
  type: 'REGION_CHANGED';
  payload: {
    bounds: [number, number, number, number]; // [west, south, east, north]
    zoom: number;
    visible_parcels: string[];
    geography: {
      state?: string;
      metro?: string;
      county?: string;
      zip?: string;
    };
  };
}

// Event: Layer toggled
interface LayerToggledEvent {
  type: 'LAYER_TOGGLED';
  payload: {
    layer_id: string;
    visible: boolean;
    active_layers: string[];
  };
}
```

### Chat → Map Events

```typescript
// Event: Highlight parcels from AI response
interface HighlightParcelsEvent {
  type: 'HIGHLIGHT_PARCELS';
  payload: {
    parcel_ids: string[];
    zoom_to: boolean;
    highlight_style: 'primary' | 'secondary' | 'comparison';
    duration_ms?: number; // Auto-clear after duration
  };
}

// Event: Zoom to location from AI response
interface ZoomToLocationEvent {
  type: 'ZOOM_TO_LOCATION';
  payload: {
    coordinates: [number, number];
    zoom: number;
    animate: boolean;
  };
}

// Event: Filter map by criteria
interface FilterMapEvent {
  type: 'FILTER_MAP';
  payload: {
    zone_codes?: string[];
    min_hbu_score?: number;
    max_price?: number;
    has_foreclosure?: boolean;
  };
}

// Event: Show specific layer
interface ShowLayerEvent {
  type: 'SHOW_LAYER';
  payload: {
    layer_id: string;
    solo: boolean; // Hide other layers
  };
}
```

## 3.2 State Management

```typescript
// stores/panelSyncStore.ts
import { create } from 'zustand';

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
    geography: {},
    visible_parcels: [],
    active_layers: ['zoning'],
  },
  setChatContext: (context) => set((state) => ({
    chatContext: { ...state.chatContext, ...context },
  })),
  
  eventQueue: [],
  enqueueEvent: (event) => set((state) => ({
    eventQueue: [...state.eventQueue, event],
  })),
  dequeueEvent: () => {
    const state = get();
    const [first, ...rest] = state.eventQueue;
    set({ eventQueue: rest });
    return first;
  },
}));
```

---

# 4. MAPBOX INTEGRATION

## 4.1 Map Configuration

```typescript
// lib/mapbox.ts
import mapboxgl from 'mapbox-gl';

// Mapbox access token
mapboxgl.accessToken = process.env.NEXT_PUBLIC_MAPBOX_TOKEN!;

// Default map configuration
export const MAP_CONFIG = {
  style: 'mapbox://styles/mapbox/light-v11', // Base style
  center: [-80.7, 28.1] as [number, number], // Brevard County center
  zoom: 9,
  minZoom: 5,
  maxZoom: 18,
  bounds: [
    [-87.6, 24.5], // Southwest Florida
    [-79.8, 31.0], // Northeast Florida
  ] as [[number, number], [number, number]],
};

// Zoom level to geography mapping
export const ZOOM_GEOGRAPHY = {
  5: 'state',
  7: 'metro',
  9: 'county',
  11: 'zip',
  13: 'parcel',
} as const;

// Layer IDs
export const LAYER_IDS = {
  ZONING: 'zoning-layer',
  FORECLOSURES: 'foreclosure-layer',
  HOME_VALUES: 'home-values-layer',
  INVENTORY: 'inventory-layer',
  HBU_SCORES: 'hbu-scores-layer',
  PARCELS: 'parcels-layer',
  SELECTED: 'selected-parcel-layer',
};
```

## 4.2 Choropleth Layer Specifications

### Zoning Choropleth

```typescript
// Zoning layer with color by zone category
export const ZONING_LAYER: mapboxgl.LayerSpecification = {
  id: LAYER_IDS.ZONING,
  type: 'fill',
  source: 'zoning-districts',
  paint: {
    'fill-color': [
      'match',
      ['get', 'zone_category'],
      'residential-sf', '#90CAF9',    // Light blue - Single Family
      'residential-mf', '#1E88E5',    // Blue - Multi Family
      'commercial', '#F57C00',        // Orange - Commercial
      'industrial', '#7B1FA2',        // Purple - Industrial
      'agricultural', '#66BB6A',      // Green - Agricultural
      'mixed-use', '#26A69A',         // Teal - Mixed Use
      'pud', '#AB47BC',               // Light Purple - PUD
      '#E0E0E0'                       // Gray - Unknown
    ],
    'fill-opacity': [
      'case',
      ['boolean', ['feature-state', 'hover'], false],
      0.8,
      0.6
    ],
    'fill-outline-color': '#FFFFFF',
  },
};

// Zoning legend configuration
export const ZONING_LEGEND = [
  { color: '#90CAF9', label: 'Residential SF', zone_category: 'residential-sf' },
  { color: '#1E88E5', label: 'Residential MF', zone_category: 'residential-mf' },
  { color: '#F57C00', label: 'Commercial', zone_category: 'commercial' },
  { color: '#7B1FA2', label: 'Industrial', zone_category: 'industrial' },
  { color: '#66BB6A', label: 'Agricultural', zone_category: 'agricultural' },
  { color: '#26A69A', label: 'Mixed Use', zone_category: 'mixed-use' },
  { color: '#AB47BC', label: 'PUD', zone_category: 'pud' },
];
```

### HBU Score Choropleth

```typescript
// HBU Score layer with gradient
export const HBU_LAYER: mapboxgl.LayerSpecification = {
  id: LAYER_IDS.HBU_SCORES,
  type: 'fill',
  source: 'parcels',
  paint: {
    'fill-color': [
      'interpolate',
      ['linear'],
      ['get', 'hbu_score'],
      0, '#D32F2F',    // Red - Skip (0-40)
      40, '#F57C00',   // Orange - Review (40-60)
      60, '#FBC02D',   // Yellow - Consider (60-75)
      75, '#388E3C',   // Green - Bid (75-90)
      90, '#1B5E20',   // Dark Green - Strong Bid (90+)
    ],
    'fill-opacity': 0.7,
  },
};

export const HBU_LEGEND = [
  { color: '#D32F2F', label: 'Skip (0-40)', min: 0, max: 40 },
  { color: '#F57C00', label: 'Review (40-60)', min: 40, max: 60 },
  { color: '#FBC02D', label: 'Consider (60-75)', min: 60, max: 75 },
  { color: '#388E3C', label: 'Bid (75-90)', min: 75, max: 90 },
  { color: '#1B5E20', label: 'Strong Bid (90+)', min: 90, max: 100 },
];
```

### Foreclosure Layer

```typescript
// Foreclosure status layer
export const FORECLOSURE_LAYER: mapboxgl.LayerSpecification = {
  id: LAYER_IDS.FORECLOSURES,
  type: 'circle',
  source: 'foreclosures',
  paint: {
    'circle-radius': [
      'interpolate',
      ['linear'],
      ['zoom'],
      9, 4,
      13, 8,
      16, 12,
    ],
    'circle-color': [
      'match',
      ['get', 'status'],
      'lis_pendens', '#FFF59D',    // Yellow - Filed
      'scheduled', '#FFB74D',      // Orange - Scheduled
      'active', '#EF5350',         // Red - Active
      'cancelled', '#90A4AE',      // Gray - Cancelled
      '#E0E0E0'
    ],
    'circle-stroke-width': 2,
    'circle-stroke-color': '#FFFFFF',
  },
};
```

## 4.3 Geographic Hierarchy Implementation

```typescript
// components/map/GeographicNav.tsx
interface GeographyLevel {
  type: 'state' | 'metro' | 'county' | 'zip';
  id: string;
  name: string;
  bounds?: mapboxgl.LngLatBounds;
}

export function GeographicNav() {
  const [hierarchy, setHierarchy] = useState<GeographyLevel[]>([
    { type: 'state', id: 'FL', name: 'Florida' }
  ]);
  
  const drillDown = async (level: GeographyLevel) => {
    const children = await fetchGeographyChildren(level);
    // Update map to show children
    // Update breadcrumb
  };
  
  return (
    <div className="absolute top-4 left-4 z-10 bg-background/90 rounded-lg p-2">
      <Breadcrumb>
        {hierarchy.map((level, i) => (
          <BreadcrumbItem key={level.id}>
            <BreadcrumbLink onClick={() => zoomToLevel(level)}>
              {level.name}
            </BreadcrumbLink>
            {i < hierarchy.length - 1 && <BreadcrumbSeparator />}
          </BreadcrumbItem>
        ))}
      </Breadcrumb>
      
      {/* Children list */}
      <div className="mt-2 max-h-60 overflow-auto">
        {children.map((child) => (
          <Button
            key={child.id}
            variant="ghost"
            size="sm"
            onClick={() => drillDown(child)}
          >
            {child.name}
          </Button>
        ))}
      </div>
    </div>
  );
}
```

## 4.4 Parcel Selection & Popup

```typescript
// components/map/ParcelPopup.tsx
interface ParcelPopupProps {
  parcel: Parcel;
  onAskAI: (parcel: Parcel) => void;
  onShowDetails: (parcel: Parcel) => void;
}

export function ParcelPopup({ parcel, onAskAI, onShowDetails }: ParcelPopupProps) {
  return (
    <div className="min-w-[250px] p-0">
      <div className="p-3 border-b">
        <h3 className="font-semibold text-sm">{parcel.address}</h3>
        <p className="text-xs text-muted-foreground">{parcel.city}, FL {parcel.zip}</p>
      </div>
      
      <div className="p-3 space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-muted-foreground">Zoning</span>
          <Badge variant="outline">{parcel.zone_code}</Badge>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-muted-foreground">Lot Size</span>
          <span>{parcel.lot_sqft.toLocaleString()} sqft</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-muted-foreground">HBU Score</span>
          <Badge className={getHbuColor(parcel.hbu_score)}>
            {parcel.hbu_score}/100
          </Badge>
        </div>
        {parcel.foreclosure_status && (
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Foreclosure</span>
            <Badge variant="destructive">{parcel.foreclosure_status}</Badge>
          </div>
        )}
      </div>
      
      <div className="p-3 border-t flex gap-2">
        <Button size="sm" className="flex-1" onClick={() => onAskAI(parcel)}>
          <MessageSquare className="w-4 h-4 mr-1" />
          Ask AI
        </Button>
        <Button size="sm" variant="outline" onClick={() => onShowDetails(parcel)}>
          <Info className="w-4 h-4" />
        </Button>
      </div>
    </div>
  );
}
```

---

# 5. NLP CHATBOT SPECIFICATIONS

## 5.1 Chat Interface Components

```typescript
// components/chat/ChatPanel.tsx
interface ChatPanelProps {
  selectedParcel?: Parcel;
  context: ChatContext;
  onMapAction: (action: MapAction) => void;
}

export function ChatPanel({ selectedParcel, context, onMapAction }: ChatPanelProps) {
  const { messages, sendMessage, isLoading } = useChatSession();
  const [input, setInput] = useState('');
  
  // Auto-populate input when parcel selected
  useEffect(() => {
    if (selectedParcel) {
      setInput(`Tell me about ${selectedParcel.address}`);
    }
  }, [selectedParcel]);
  
  const handleSend = async () => {
    const response = await sendMessage(input, {
      ...context,
      selected_parcel: selectedParcel?.id,
    });
    
    // Process map actions from AI response
    if (response.map_actions) {
      response.map_actions.forEach(onMapAction);
    }
    
    setInput('');
  };
  
  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b flex items-center justify-between">
        <div>
          <h2 className="font-semibold">AI Zoning Expert</h2>
          {selectedParcel && (
            <p className="text-sm text-muted-foreground">
              Analyzing {selectedParcel.address}
            </p>
          )}
        </div>
        <Button variant="ghost" size="icon">
          <Settings className="w-4 h-4" />
        </Button>
      </div>
      
      {/* Messages */}
      <ScrollArea className="flex-1 p-4">
        <MessageList messages={messages} onMapAction={onMapAction} />
        {isLoading && <TypingIndicator />}
      </ScrollArea>
      
      {/* Suggested Actions */}
      {messages.length > 0 && (
        <SuggestedActions
          suggestions={messages[messages.length - 1].suggestions}
          onSelect={setInput}
        />
      )}
      
      {/* Input */}
      <div className="p-4 border-t">
        <MessageInput
          value={input}
          onChange={setInput}
          onSend={handleSend}
          disabled={isLoading}
          placeholder={selectedParcel 
            ? `Ask about ${selectedParcel.address}...` 
            : "Ask about any property or zoning question..."
          }
        />
      </div>
    </div>
  );
}
```

## 5.2 Message Types & Rendering

```typescript
// types/chat.ts
interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  
  // AI-specific fields
  intent?: string;
  confidence?: number;
  entities?: Record<string, string>;
  sources?: Source[];
  
  // Map integration
  map_actions?: MapAction[];
  referenced_parcels?: string[];
  
  // Interactive elements
  suggestions?: string[];
  actions?: ActionButton[];
  
  // Rich content
  charts?: ChartData[];
  tables?: TableData[];
  images?: string[];
}

// Action button in AI response
interface ActionButton {
  label: string;
  type: 'map' | 'report' | 'compare' | 'save' | 'link';
  payload: Record<string, unknown>;
}

// Map action from AI
interface MapAction {
  type: 'highlight' | 'zoom' | 'filter' | 'layer';
  payload: Record<string, unknown>;
}
```

## 5.3 Intent Classification System

```typescript
// Intent types for zoning chatbot
export const INTENTS = {
  // Core zoning intents
  FEASIBILITY_CHECK: 'feasibility_check',      // "Can I build X?"
  ZONING_LOOKUP: 'zoning_lookup',              // "What's the zoning for X?"
  ALLOWED_USES: 'allowed_uses',                // "What can I build here?"
  DIMENSIONAL_STANDARDS: 'dimensional_standards', // "What are the setbacks?"
  
  // Analysis intents
  HBU_ANALYSIS: 'hbu_analysis',                // "What's the best use?"
  CMA_REQUEST: 'cma_request',                  // "What are the comps?"
  VALUE_ESTIMATE: 'value_estimate',            // "What's it worth?"
  
  // Map intents
  GEOGRAPHIC_SEARCH: 'geographic_search',      // "Show me R-2 zones in X"
  PARCEL_COMPARISON: 'parcel_comparison',      // "Compare these properties"
  AREA_ANALYSIS: 'area_analysis',              // "Analyze this ZIP code"
  
  // Report intents
  REPORT_REQUEST: 'report_request',            // "Generate a report"
  EXPORT_DATA: 'export_data',                  // "Export this data"
  
  // Educational intents
  DEFINITION: 'definition',                    // "What does FAR mean?"
  PROCESS_EXPLANATION: 'process_explanation',  // "How do I get a permit?"
  
  // Meta intents
  GREETING: 'greeting',
  CLARIFICATION: 'clarification',
  FEEDBACK: 'feedback',
} as const;

// Entity extraction schema
export const ENTITIES = {
  ADDRESS: 'address',
  PARCEL_ID: 'parcel_id',
  ZONE_CODE: 'zone_code',
  USE_TYPE: 'use_type',
  GEOGRAPHY: 'geography',         // State, county, city, ZIP
  METRIC: 'metric',               // Price, size, score
  TIME_PERIOD: 'time_period',     // Historical range
  COMPARISON_TYPE: 'comparison_type',
} as const;
```

---

# 6. OPENMANUS AGENT SYSTEM

## 6.1 Agent Configuration

```python
# agents/config.py
from dataclasses import dataclass
from enum import Enum

class AgentModel(Enum):
    GEMINI_FLASH = "gemini-2.5-flash"
    CLAUDE_SONNET = "claude-sonnet-4-5-20250514"
    XGBOOST_LOCAL = "xgboost-local"

@dataclass
class AgentConfig:
    name: str
    model: AgentModel
    temperature: float
    max_tokens: int
    tools: list[str]
    system_prompt: str

AGENT_CONFIGS = {
    "coordinator": AgentConfig(
        name="Coordinator",
        model=AgentModel.CLAUDE_SONNET,
        temperature=0.3,
        max_tokens=2000,
        tools=["task_decomposition", "agent_dispatch"],
        system_prompt="""You are the ZoneWise Coordinator Agent. Your job is to:
1. Analyze user queries and map context
2. Decompose complex queries into sub-tasks
3. Assign tasks to specialized agents
4. Aggregate and synthesize results
Always consider the current map state when planning responses."""
    ),
    
    "zoning": AgentConfig(
        name="Zoning Agent",
        model=AgentModel.GEMINI_FLASH,
        temperature=0.1,
        max_tokens=1500,
        tools=["zone_lookup", "rule_search", "ordinance_query"],
        system_prompt="""You are the ZoneWise Zoning Agent. Your job is to:
1. Look up zoning codes for parcels
2. Retrieve allowed uses and dimensional standards
3. Explain zoning rules in plain language
Be precise with setbacks, FAR, and density limits."""
    ),
    
    "cma": AgentConfig(
        name="CMA Agent",
        model=AgentModel.GEMINI_FLASH,
        temperature=0.2,
        max_tokens=2000,
        tools=["comp_search", "price_analysis", "market_trends"],
        system_prompt="""You are the ZoneWise CMA Agent. Your job is to:
1. Find comparable properties (5-10 comps)
2. Adjust for differences
3. Estimate market value
Use the most recent sales within 6 months when possible."""
    ),
    
    "hbu": AgentConfig(
        name="HBU Agent",
        model=AgentModel.CLAUDE_SONNET,
        temperature=0.3,
        max_tokens=2500,
        tools=["zoning_query", "market_query", "feasibility_calc"],
        system_prompt="""You are the ZoneWise HBU (Highest and Best Use) Agent. Your job is to:
1. Analyze all legally permissible uses
2. Evaluate physical suitability
3. Assess financial feasibility
4. Determine maximum productivity
Score HBU from 0-100 with detailed reasoning."""
    ),
    
    "ml": AgentConfig(
        name="ML Agent",
        model=AgentModel.XGBOOST_LOCAL,
        temperature=0.0,
        max_tokens=500,
        tools=["price_prediction", "probability_prediction"],
        system_prompt="N/A - Local ML model"
    ),
    
    "reporter": AgentConfig(
        name="Reporter Agent",
        model=AgentModel.CLAUDE_SONNET,
        temperature=0.4,
        max_tokens=3000,
        tools=["response_format", "map_action_create", "suggestion_generate"],
        system_prompt="""You are the ZoneWise Reporter Agent. Your job is to:
1. Synthesize results from all agents
2. Generate natural language responses
3. Create map actions (highlights, zooms, filters)
4. Suggest follow-up questions
Always make responses actionable with clear next steps."""
    ),
}
```

## 6.2 Agent Orchestration Flow

```python
# agents/orchestrator.py
import asyncio
from typing import Any
from langgraph.graph import StateGraph, END

class ZoneWiseOrchestrator:
    def __init__(self):
        self.agents = self._initialize_agents()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build LangGraph workflow for multi-agent orchestration"""
        workflow = StateGraph(OrchestratorState)
        
        # Add nodes
        workflow.add_node("coordinator", self.coordinator_node)
        workflow.add_node("zoning", self.zoning_node)
        workflow.add_node("cma", self.cma_node)
        workflow.add_node("hbu", self.hbu_node)
        workflow.add_node("ml", self.ml_node)
        workflow.add_node("reporter", self.reporter_node)
        
        # Set entry point
        workflow.set_entry_point("coordinator")
        
        # Add conditional edges (parallel execution)
        workflow.add_conditional_edges(
            "coordinator",
            self.route_to_agents,
            {
                "zoning_only": "zoning",
                "full_analysis": "parallel_execution",
                "simple_response": "reporter",
            }
        )
        
        # Parallel execution node
        workflow.add_node("parallel_execution", self.parallel_execution_node)
        
        # All paths lead to reporter
        workflow.add_edge("zoning", "reporter")
        workflow.add_edge("parallel_execution", "reporter")
        workflow.add_edge("reporter", END)
        
        return workflow.compile()
    
    async def parallel_execution_node(self, state: OrchestratorState) -> OrchestratorState:
        """Execute multiple agents in parallel"""
        tasks = state.get("pending_tasks", [])
        
        results = await asyncio.gather(
            self.zoning_node(state) if "zoning" in tasks else asyncio.sleep(0),
            self.cma_node(state) if "cma" in tasks else asyncio.sleep(0),
            self.hbu_node(state) if "hbu" in tasks else asyncio.sleep(0),
            self.ml_node(state) if "ml" in tasks else asyncio.sleep(0),
        )
        
        return {
            **state,
            "agent_results": {
                "zoning": results[0] if "zoning" in tasks else None,
                "cma": results[1] if "cma" in tasks else None,
                "hbu": results[2] if "hbu" in tasks else None,
                "ml": results[3] if "ml" in tasks else None,
            }
        }
    
    async def process_query(
        self, 
        query: str, 
        context: dict[str, Any]
    ) -> ChatResponse:
        """Main entry point for processing user queries"""
        initial_state = {
            "user_query": query,
            "map_context": context.get("map_context", {}),
            "selected_parcel": context.get("selected_parcel"),
            "conversation_history": context.get("history", []),
            "agent_results": {},
            "pending_tasks": [],
        }
        
        final_state = await self.graph.ainvoke(initial_state)
        
        return ChatResponse(
            content=final_state["response"],
            intent=final_state["detected_intent"],
            entities=final_state["extracted_entities"],
            map_actions=final_state.get("map_actions", []),
            suggestions=final_state.get("suggestions", []),
            sources=final_state.get("sources", []),
        )
```

## 6.3 Individual Agent Implementations

```python
# agents/zoning_agent.py
class ZoningAgent:
    """Agent specialized in zoning lookups and rule interpretation"""
    
    async def execute(self, state: dict) -> dict:
        parcel_id = state.get("selected_parcel")
        query = state.get("user_query")
        
        # Step 1: Get parcel zoning
        zoning = await self.lookup_zoning(parcel_id)
        
        # Step 2: Get dimensional standards
        standards = await self.get_dimensional_standards(zoning.zone_code)
        
        # Step 3: Get allowed uses
        uses = await self.get_allowed_uses(zoning.zone_code)
        
        # Step 4: Check for any overlays or special districts
        overlays = await self.check_overlays(parcel_id)
        
        return {
            "zoning_code": zoning.zone_code,
            "zone_name": zoning.zone_name,
            "jurisdiction": zoning.jurisdiction,
            "dimensional_standards": {
                "min_lot_size": standards.min_lot_size,
                "min_lot_width": standards.min_lot_width,
                "setbacks": {
                    "front": standards.front_setback,
                    "side": standards.side_setback,
                    "rear": standards.rear_setback,
                },
                "max_height": standards.max_height,
                "max_far": standards.max_far,
                "max_lot_coverage": standards.max_lot_coverage,
                "max_density": standards.max_density,
            },
            "allowed_uses": {
                "by_right": uses.by_right,
                "conditional": uses.conditional,
                "prohibited": uses.prohibited,
            },
            "overlays": overlays,
        }
```

---

# 7. DATABASE SCHEMA

## 7.1 Core Tables

```sql
-- Enable PostGIS and pgvector
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================
-- PARCEL & ZONING TABLES
-- ============================================

-- Florida parcels (10M+ rows)
CREATE TABLE fl_parcels (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parcel_id VARCHAR(50) UNIQUE NOT NULL,
    county_fips VARCHAR(5) NOT NULL,
    
    -- Location
    address VARCHAR(255),
    city VARCHAR(100),
    zip VARCHAR(10),
    latitude DECIMAL(10, 7),
    longitude DECIMAL(10, 7),
    geometry GEOMETRY(POLYGON, 4326),
    
    -- Zoning
    zone_code VARCHAR(20),
    zone_name VARCHAR(100),
    zone_category VARCHAR(50), -- residential-sf, commercial, etc.
    jurisdiction VARCHAR(100),
    
    -- Property details
    lot_sqft INTEGER,
    building_sqft INTEGER,
    year_built INTEGER,
    bedrooms INTEGER,
    bathrooms DECIMAL(3,1),
    
    -- Values
    assessed_value DECIMAL(12, 2),
    market_value DECIMAL(12, 2),
    last_sale_price DECIMAL(12, 2),
    last_sale_date DATE,
    
    -- Analysis scores
    hbu_score DECIMAL(5, 2),
    ml_predicted_value DECIMAL(12, 2),
    ml_confidence DECIMAL(5, 4),
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    data_source VARCHAR(50)
);

-- Spatial index for fast geographic queries
CREATE INDEX idx_parcels_geometry ON fl_parcels USING GIST(geometry);
CREATE INDEX idx_parcels_county ON fl_parcels(county_fips);
CREATE INDEX idx_parcels_zip ON fl_parcels(zip);
CREATE INDEX idx_parcels_zone ON fl_parcels(zone_code);

-- Zoning districts (polygon boundaries)
CREATE TABLE fl_zoning_districts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    zone_code VARCHAR(20) NOT NULL,
    zone_name VARCHAR(100),
    zone_category VARCHAR(50),
    jurisdiction VARCHAR(100),
    county_fips VARCHAR(5),
    geometry GEOMETRY(MULTIPOLYGON, 4326),
    
    -- Dimensional standards (denormalized for fast lookup)
    min_lot_size INTEGER,
    max_density DECIMAL(6, 2),
    max_height INTEGER,
    max_far DECIMAL(4, 2),
    front_setback INTEGER,
    side_setback INTEGER,
    rear_setback INTEGER,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_zoning_geometry ON fl_zoning_districts USING GIST(geometry);

-- ============================================
-- CHATBOT TABLES
-- ============================================

-- Chat conversations
CREATE TABLE chatbot_conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id),
    session_id VARCHAR(100) NOT NULL,
    
    -- Context
    current_parcel_id UUID REFERENCES fl_parcels(id),
    map_bounds GEOMETRY(POLYGON, 4326),
    active_layers TEXT[],
    
    -- Metadata
    message_count INTEGER DEFAULT 0,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_message_at TIMESTAMP WITH TIME ZONE,
    ended_at TIMESTAMP WITH TIME ZONE
);

-- Chat messages
CREATE TABLE chatbot_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES chatbot_conversations(id) ON DELETE CASCADE,
    
    -- Content
    role VARCHAR(20) NOT NULL, -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    
    -- AI analysis
    intent VARCHAR(50),
    intent_confidence DECIMAL(5, 4),
    entities JSONB,
    
    -- Map integration
    map_actions JSONB,
    referenced_parcels UUID[],
    
    -- Response metadata
    model_used VARCHAR(50),
    tokens_used INTEGER,
    response_time_ms INTEGER,
    
    -- Rich content
    suggestions TEXT[],
    action_buttons JSONB,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation ON chatbot_messages(conversation_id);
CREATE INDEX idx_messages_created ON chatbot_messages(created_at DESC);

-- ============================================
-- MAP SESSION TABLES
-- ============================================

-- Map sessions (track user map interactions)
CREATE TABLE map_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id),
    conversation_id UUID REFERENCES chatbot_conversations(id),
    
    -- Current view
    center_lat DECIMAL(10, 7),
    center_lng DECIMAL(10, 7),
    zoom_level DECIMAL(4, 2),
    bounds GEOMETRY(POLYGON, 4326),
    
    -- Active state
    active_layers TEXT[],
    selected_parcel_id UUID REFERENCES fl_parcels(id),
    highlighted_parcels UUID[],
    active_filters JSONB,
    
    -- Geography navigation
    current_state VARCHAR(2),
    current_metro VARCHAR(100),
    current_county VARCHAR(100),
    current_zip VARCHAR(10),
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- FORECLOSURE INTEGRATION (from BidDeed.AI)
-- ============================================

CREATE TABLE fl_foreclosure_auctions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parcel_id UUID REFERENCES fl_parcels(id),
    case_number VARCHAR(50),
    
    -- Status
    status VARCHAR(30), -- lis_pendens, scheduled, active, sold, cancelled
    auction_date DATE,
    auction_time TIME,
    
    -- Financials
    judgment_amount DECIMAL(12, 2),
    opening_bid DECIMAL(12, 2),
    final_bid DECIMAL(12, 2),
    
    -- ML predictions
    ml_win_probability DECIMAL(5, 4),
    ml_predicted_price DECIMAL(12, 2),
    
    -- Coordinates for map display
    latitude DECIMAL(10, 7),
    longitude DECIMAL(10, 7),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_foreclosures_parcel ON fl_foreclosure_auctions(parcel_id);
CREATE INDEX idx_foreclosures_status ON fl_foreclosure_auctions(status);
CREATE INDEX idx_foreclosures_date ON fl_foreclosure_auctions(auction_date);
```

## 7.2 Views & Functions

```sql
-- View: Parcels with full zoning info for map display
CREATE VIEW v_parcels_map AS
SELECT 
    p.id,
    p.parcel_id,
    p.address,
    p.city,
    p.zip,
    p.latitude,
    p.longitude,
    ST_AsGeoJSON(p.geometry) as geojson,
    p.zone_code,
    p.zone_category,
    p.lot_sqft,
    p.assessed_value,
    p.hbu_score,
    f.status as foreclosure_status,
    f.auction_date,
    f.judgment_amount
FROM fl_parcels p
LEFT JOIN fl_foreclosure_auctions f ON p.id = f.parcel_id AND f.status IN ('scheduled', 'active');

-- Function: Get parcels in bounding box
CREATE FUNCTION get_parcels_in_bounds(
    west DECIMAL,
    south DECIMAL,
    east DECIMAL,
    north DECIMAL,
    layer_filter TEXT DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    parcel_id VARCHAR,
    address VARCHAR,
    zone_code VARCHAR,
    zone_category VARCHAR,
    hbu_score DECIMAL,
    foreclosure_status VARCHAR,
    geojson TEXT
)
LANGUAGE sql
AS $$
    SELECT 
        p.id,
        p.parcel_id,
        p.address,
        p.zone_code,
        p.zone_category,
        p.hbu_score,
        f.status as foreclosure_status,
        ST_AsGeoJSON(p.geometry) as geojson
    FROM fl_parcels p
    LEFT JOIN fl_foreclosure_auctions f ON p.id = f.parcel_id
    WHERE ST_Intersects(
        p.geometry,
        ST_MakeEnvelope(west, south, east, north, 4326)
    )
    AND (layer_filter IS NULL OR p.zone_category = layer_filter)
    LIMIT 5000;
$$;

-- Function: Get choropleth data by ZIP
CREATE FUNCTION get_zip_choropleth(metric TEXT)
RETURNS TABLE (
    zip VARCHAR,
    value DECIMAL,
    geometry TEXT
)
LANGUAGE sql
AS $$
    SELECT 
        z.zip,
        CASE metric
            WHEN 'hbu_avg' THEN AVG(p.hbu_score)
            WHEN 'value_avg' THEN AVG(p.assessed_value)
            WHEN 'foreclosure_count' THEN COUNT(f.id)::DECIMAL
        END as value,
        ST_AsGeoJSON(ST_Union(p.geometry)) as geometry
    FROM fl_parcels p
    LEFT JOIN fl_foreclosure_auctions f ON p.id = f.parcel_id
    JOIN (SELECT DISTINCT zip FROM fl_parcels) z ON p.zip = z.zip
    GROUP BY z.zip;
$$;
```

---

# 8. API SPECIFICATIONS

## 8.1 REST API Endpoints

```yaml
openapi: 3.0.3
info:
  title: ZoneWise API V3
  version: 3.0.0
  description: Split-screen zoning intelligence API with map and chat integration

paths:
  /api/v1/chat:
    post:
      summary: Send chat message
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: User message
                session_id:
                  type: string
                context:
                  type: object
                  properties:
                    selected_parcel:
                      type: string
                    map_bounds:
                      type: array
                      items:
                        type: number
                    active_layers:
                      type: array
                      items:
                        type: string
      responses:
        200:
          description: AI response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ChatResponse'

  /api/v1/parcels/bounds:
    get:
      summary: Get parcels within bounds
      parameters:
        - name: west
          in: query
          schema:
            type: number
        - name: south
          in: query
          schema:
            type: number
        - name: east
          in: query
          schema:
            type: number
        - name: north
          in: query
          schema:
            type: number
        - name: layers
          in: query
          schema:
            type: array
            items:
              type: string
      responses:
        200:
          description: GeoJSON FeatureCollection
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/GeoJSONFeatureCollection'

  /api/v1/parcels/{parcel_id}:
    get:
      summary: Get single parcel details
      parameters:
        - name: parcel_id
          in: path
          required: true
          schema:
            type: string
      responses:
        200:
          description: Parcel details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ParcelDetail'

  /api/v1/analysis/hbu:
    post:
      summary: Run HBU analysis
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                parcel_id:
                  type: string
                include_cma:
                  type: boolean
                include_ml:
                  type: boolean
      responses:
        200:
          description: HBU analysis result
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HBUAnalysis'

  /api/v1/choropleth/{layer}:
    get:
      summary: Get choropleth data for layer
      parameters:
        - name: layer
          in: path
          required: true
          schema:
            type: string
            enum: [zoning, hbu, foreclosures, values, inventory]
        - name: geography
          in: query
          schema:
            type: string
            enum: [state, metro, county, zip]
      responses:
        200:
          description: Choropleth GeoJSON
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/GeoJSONFeatureCollection'

components:
  schemas:
    ChatResponse:
      type: object
      properties:
        id:
          type: string
        content:
          type: string
        intent:
          type: string
        confidence:
          type: number
        entities:
          type: object
        map_actions:
          type: array
          items:
            $ref: '#/components/schemas/MapAction'
        suggestions:
          type: array
          items:
            type: string
        sources:
          type: array
          items:
            $ref: '#/components/schemas/Source'

    MapAction:
      type: object
      properties:
        type:
          type: string
          enum: [highlight, zoom, filter, layer]
        payload:
          type: object

    ParcelDetail:
      type: object
      properties:
        id:
          type: string
        parcel_id:
          type: string
        address:
          type: string
        zoning:
          $ref: '#/components/schemas/ZoningInfo'
        values:
          $ref: '#/components/schemas/ValueInfo'
        analysis:
          $ref: '#/components/schemas/AnalysisInfo'
        foreclosure:
          $ref: '#/components/schemas/ForeclosureInfo'
```

## 8.2 WebSocket Protocol

```typescript
// WebSocket message types for real-time chat
interface WSMessage {
  type: 'chat' | 'map_event' | 'typing' | 'error';
  payload: unknown;
  timestamp: number;
}

// Client → Server
interface WSChatMessage {
  type: 'chat';
  payload: {
    message: string;
    context: ChatContext;
  };
}

// Server → Client
interface WSChatResponse {
  type: 'chat';
  payload: {
    id: string;
    content: string;
    map_actions: MapAction[];
    suggestions: string[];
    is_complete: boolean; // For streaming
  };
}

// Server → Client (streaming)
interface WSStreamChunk {
  type: 'stream_chunk';
  payload: {
    message_id: string;
    chunk: string;
    is_final: boolean;
  };
}
```

---

# 9. DATA PIPELINE

## 9.1 Daily Data Refresh

```yaml
# .github/workflows/daily_data_refresh.yml
name: Daily Data Refresh

on:
  schedule:
    - cron: '0 4 * * *'  # 11 PM EST / 4 AM UTC
  workflow_dispatch:

jobs:
  refresh-parcels:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Refresh BCPAO parcels
        run: python scripts/refresh_bcpao.py
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
      
      - name: Refresh Zillow data
        run: python scripts/refresh_zillow.py
      
      - name: Update HBU scores
        run: python scripts/calculate_hbu.py
      
      - name: Refresh foreclosure auctions
        run: python scripts/refresh_foreclosures.py

  refresh-zoning:
    runs-on: ubuntu-latest
    steps:
      - name: Scrape ordinance updates
        run: python scripts/scrape_ordinances.py
        env:
          FIRECRAWL_API_KEY: ${{ secrets.FIRECRAWL_API_KEY }}
      
      - name: Update zoning districts
        run: python scripts/update_zoning_districts.py
```

## 9.2 Data Source Integration

| Source | Frequency | Method | Data |
|--------|-----------|--------|------|
| BCPAO API | Daily | REST API | Parcels, owners, values |
| Zillow CSVs | Weekly | HTTP download | ZHVI, ZORI, inventory |
| Census TigerLine | Annually | FTP download | ZIP/county boundaries |
| Firecrawl | Daily | API scraping | Ordinance changes |
| RealForeclose | Daily | Selenium | Auction schedules |

---

# 10. DEPLOYMENT ARCHITECTURE

## 10.1 Infrastructure

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         CLOUDFLARE                                       │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │   Cloudflare Pages (Frontend)                                   │    │
│  │   • Global CDN (200+ edge locations)                            │    │
│  │   • Auto-deploy from GitHub                                     │    │
│  │   • SSL/TLS termination                                         │    │
│  │   • DDoS protection                                             │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │   Cloudflare Workers (Edge Functions)                           │    │
│  │   • Map tile caching                                            │    │
│  │   • API rate limiting                                           │    │
│  │   • Geographic routing                                          │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                         RENDER.COM                                       │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │   API Server (Docker)                                           │    │
│  │   • FastAPI application                                         │    │
│  │   • Auto-scaling (0-10 instances)                               │    │
│  │   • Health checks                                               │    │
│  │   • Environment: $25/mo (Starter)                               │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                         SUPABASE                                         │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │   PostgreSQL + PostGIS + pgvector                               │    │
│  │   • 8GB database                                                │    │
│  │   • Point-in-time recovery                                      │    │
│  │   • Read replicas (if needed)                                   │    │
│  │   • Environment: $25/mo (Pro)                                   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
```

## 10.2 Cost Summary

| Component | Monthly Cost | Notes |
|-----------|--------------|-------|
| Cloudflare Pages | FREE | Unlimited sites |
| Cloudflare Workers | FREE | 100K requests/day |
| Render.com Starter | $25 | Auto-scaling API |
| Supabase Pro | $25 | 8GB PostgreSQL |
| Mapbox GL JS | FREE | 50K map loads/mo |
| LLM APIs | ~$50 | 90% FREE tier |
| **TOTAL** | **~$100/month** | |

---

# 11. TESTING SPECIFICATIONS

## 11.1 Test Categories

| Category | Framework | Coverage Target |
|----------|-----------|-----------------|
| Unit Tests | Vitest + pytest | 80% |
| Component Tests | React Testing Library | 70% |
| Integration Tests | Playwright | Key flows |
| E2E Tests | Playwright | Critical paths |
| Performance Tests | k6 | Load testing |

## 11.2 Critical Test Scenarios

```typescript
// E2E Test: Split-screen map-chat interaction
test('parcel selection updates chat context', async ({ page }) => {
  await page.goto('/dashboard');
  
  // Click on a parcel
  await page.click('[data-testid="parcel-marker-123"]');
  
  // Verify chat context updated
  await expect(page.locator('[data-testid="chat-context"]'))
    .toContainText('123 Main St');
  
  // Verify AI response references parcel
  await page.fill('[data-testid="chat-input"]', 'What can I build here?');
  await page.click('[data-testid="send-button"]');
  
  await expect(page.locator('[data-testid="ai-response"]'))
    .toContainText('R-2');
});

test('AI response triggers map highlight', async ({ page }) => {
  await page.goto('/dashboard');
  
  // Ask for properties
  await page.fill('[data-testid="chat-input"]', 
    'Show me R-2 properties in Satellite Beach');
  await page.click('[data-testid="send-button"]');
  
  // Verify map highlights appear
  await expect(page.locator('[data-testid="highlighted-parcels"]'))
    .toHaveCount({ min: 1 });
});
```

---

# 12. PERFORMANCE REQUIREMENTS

## 12.1 Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Map Load (initial) | <2s | Time to interactive |
| Map Pan/Zoom | 60fps | Frame rate |
| Layer Toggle | <200ms | Click to render |
| Parcel Click | <100ms | Click to popup |
| Chat Response | <3s | Query to response |
| Chat Streaming | <500ms | First token |
| API Latency (p95) | <200ms | Server response |
| Database Query (p95) | <100ms | PostGIS queries |

## 12.2 Optimization Strategies

| Component | Strategy |
|-----------|----------|
| Map Tiles | Cloudflare edge caching |
| Parcels | Vector tiles at zoom 13+ |
| API | Response compression (gzip) |
| Database | Spatial indexes, query optimization |
| Chat | WebSocket streaming, response caching |
| Frontend | Code splitting, lazy loading |

---

*ZoneWise PRS V3.0*  
*Technical Implementation Specification*  
*January 20, 2026*
