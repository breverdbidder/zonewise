'use client';

import { useState } from 'react';
import { ChatPanel } from '@/components/zonewise/chat/ChatPanel';
import { MapPanel } from '@/components/zonewise/map/MapPanel';
import { ArtifactPanel } from '@/components/zonewise/ArtifactPanel';

export default function ResearchPage() {
  const [sessionId] = useState(() => crypto.randomUUID());
  const [selectedParcel, setSelectedParcel] = useState<string | null>(null);
  const [artifact, setArtifact] = useState<any | null>(null);
  const [showArtifact, setShowArtifact] = useState(false);

  const handleArtifact = (newArtifact: any) => {
    setArtifact(newArtifact);
    setShowArtifact(true);
  };

  return (
    <div className="flex h-screen">
      {/* Chat Panel - 40% */}
      <div className="w-2/5 border-r flex flex-col">
        <ChatPanel
          sessionId={sessionId}
          onParcelSelect={setSelectedParcel}
          onArtifact={handleArtifact}
        />
      </div>

      {/* Map/Artifact Panel - 60% */}
      <div className="w-3/5 relative">
        {showArtifact && artifact ? (
          <ArtifactPanel
            artifact={artifact}
            onClose={() => setShowArtifact(false)}
          />
        ) : (
          <MapPanel
            selectedParcel={selectedParcel}
            onParcelClick={setSelectedParcel}
          />
        )}
      </div>
    </div>
  );
}
