'use client';

import { useState, useCallback, useEffect } from 'react';
import { cn } from '@/lib/utils';
import { MapPanel } from '@/components/map/MapPanel';
import { ChatPanel } from '@/components/chat/ChatPanel';
import { usePanelSyncStore } from '@/stores/panelSyncStore';
import { useMediaQuery } from '@/hooks/useMediaQuery';

interface SplitScreenProps {
  defaultMapWidth?: number;
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
  const [activePanel, setActivePanel] = useState<'map' | 'chat'>('map');
  
  const isMobile = useMediaQuery('(max-width: 768px)');
  const isTablet = useMediaQuery('(min-width: 768px) and (max-width: 1200px)');
  
  // Panel sync store
  const {
    selectedParcel,
    setSelectedParcel,
    mapHighlights,
    setMapHighlights,
    chatContext,
    setChatContext,
  } = usePanelSyncStore();

  // Handle drag resize
  const handleMouseDown = useCallback(() => {
    setIsDragging(true);
  }, []);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  const handleMouseMove = useCallback(
    (e: MouseEvent) => {
      if (!isDragging) return;
      const newWidth = (e.clientX / window.innerWidth) * 100;
      setMapWidth(Math.min(maxMapWidth, Math.max(minMapWidth, newWidth)));
    },
    [isDragging, minMapWidth, maxMapWidth]
  );

  useEffect(() => {
    if (isDragging) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
    }
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, handleMouseMove, handleMouseUp]);

  // Map -> Chat: When parcel is selected on map
  const handleParcelSelect = useCallback(
    (parcel: any) => {
      setSelectedParcel(parcel);
      setChatContext({
        current_parcel: parcel.id,
        current_address: parcel.address,
        current_zone: parcel.zone_code,
      });
    },
    [setSelectedParcel, setChatContext]
  );

  // Chat -> Map: When AI suggests map actions
  const handleMapAction = useCallback(
    (action: any) => {
      if (action.type === 'highlight') {
        setMapHighlights(action.payload.parcels);
      }
      // Handle other action types (zoom, filter, layer)
    },
    [setMapHighlights]
  );

  // Mobile: Tab-based layout
  if (isMobile) {
    return (
      <div className="flex flex-col h-screen">
        {/* Tab buttons */}
        <div className="flex border-b bg-background">
          <button
            onClick={() => setActivePanel('map')}
            className={cn(
              'flex-1 py-3 text-sm font-medium transition-colors',
              activePanel === 'map'
                ? 'border-b-2 border-primary text-primary'
                : 'text-muted-foreground hover:text-foreground'
            )}
          >
            🗺️ Map
          </button>
          <button
            onClick={() => setActivePanel('chat')}
            className={cn(
              'flex-1 py-3 text-sm font-medium transition-colors',
              activePanel === 'chat'
                ? 'border-b-2 border-primary text-primary'
                : 'text-muted-foreground hover:text-foreground'
            )}
          >
            💬 AI Chat
          </button>
        </div>

        {/* Active panel */}
        <div className="flex-1 overflow-hidden">
          {activePanel === 'map' ? (
            <MapPanel
              onParcelSelect={handleParcelSelect}
              highlights={mapHighlights}
              className="h-full"
            />
          ) : (
            <ChatPanel
              selectedParcel={selectedParcel}
              context={chatContext}
              onMapAction={handleMapAction}
              className="h-full"
            />
          )}
        </div>
      </div>
    );
  }

  // Desktop/Tablet: Split-screen layout
  const actualMapWidth = isTablet ? 50 : mapWidth;

  return (
    <div className="flex h-screen w-full overflow-hidden">
      {/* Map Panel */}
      <div
        className="relative h-full overflow-hidden"
        style={{ width: `${actualMapWidth}%` }}
      >
        <MapPanel
          onParcelSelect={handleParcelSelect}
          highlights={mapHighlights}
          className="h-full w-full"
        />
      </div>

      {/* Resizer (desktop only) */}
      {!isTablet && (
        <div
          className={cn(
            'w-1 cursor-col-resize bg-border hover:bg-primary/50 transition-colors flex-shrink-0',
            isDragging && 'bg-primary'
          )}
          onMouseDown={handleMouseDown}
        />
      )}

      {/* Chat Panel */}
      <div
        className="relative h-full overflow-hidden flex-1"
        style={{ width: isTablet ? '50%' : `${100 - actualMapWidth}%` }}
      >
        <ChatPanel
          selectedParcel={selectedParcel}
          context={chatContext}
          onMapAction={handleMapAction}
          className="h-full w-full"
        />
      </div>
    </div>
  );
}

export default SplitScreen;
