/**
 * ZoneWise V3 - SplitScreen Component
 * 60/40 split layout with resizable panels.
 */

'use client';

import { useState, useRef, useCallback, useEffect } from 'react';
import { GripVertical } from 'lucide-react';

import { MapPanel } from './MapPanel';
import { ChatPanel } from './ChatPanel';
import { usePanelSyncStore } from '@/stores/panelSyncStore';

interface SplitScreenProps {
  defaultSplit?: number; // 0-100, percentage for left panel
  minLeft?: number;
  minRight?: number;
}

export function SplitScreen({ 
  defaultSplit = 60, 
  minLeft = 30, 
  minRight = 25 
}: SplitScreenProps) {
  const [split, setSplit] = useState(defaultSplit);
  const [isDragging, setIsDragging] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const { setSelectedParcelId, setLastQuery } = usePanelSyncStore();

  // Handle parcel selection from map
  const handleParcelSelect = useCallback((parcelId: string) => {
    setSelectedParcelId(parcelId);
    setLastQuery(`Analyze parcel ${parcelId}`);
  }, [setSelectedParcelId, setLastQuery]);

  // Handle chat message
  const handleSendMessage = useCallback(async (message: string, context: any) => {
    const response = await fetch('/api/v1/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, context })
    });

    if (!response.ok) throw new Error('Chat API error');
    
    const data = await response.json();
    return data.response;
  }, []);

  // Drag handling
  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!isDragging || !containerRef.current) return;

    const rect = containerRef.current.getBoundingClientRect();
    const newSplit = ((e.clientX - rect.left) / rect.width) * 100;
    
    // Clamp to min/max
    const clampedSplit = Math.max(minLeft, Math.min(100 - minRight, newSplit));
    setSplit(clampedSplit);
  }, [isDragging, minLeft, minRight]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  // Add/remove event listeners
  useEffect(() => {
    if (isDragging) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
    }

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
  }, [isDragging, handleMouseMove, handleMouseUp]);

  return (
    <div ref={containerRef} className="flex h-screen w-full overflow-hidden bg-gray-50">
      {/* Left Panel - Map */}
      <div 
        className="relative overflow-hidden"
        style={{ width: `${split}%` }}
      >
        <MapPanel 
          onParcelSelect={handleParcelSelect}
          className="h-full"
        />
      </div>

      {/* Divider */}
      <div
        className={`relative w-1 bg-gray-200 hover:bg-blue-400 transition-colors cursor-col-resize flex items-center justify-center ${
          isDragging ? 'bg-blue-500' : ''
        }`}
        onMouseDown={handleMouseDown}
      >
        <div className="absolute inset-y-0 -left-2 -right-2" /> {/* Larger hit area */}
        <GripVertical className="w-4 h-4 text-gray-400" />
      </div>

      {/* Right Panel - Chat */}
      <div 
        className="relative overflow-hidden border-l border-gray-200"
        style={{ width: `${100 - split}%` }}
      >
        <ChatPanel 
          onSendMessage={handleSendMessage}
          className="h-full"
        />
      </div>
    </div>
  );
}

export default SplitScreen;
