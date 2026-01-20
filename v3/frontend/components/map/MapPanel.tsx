'use client';

import { useRef, useEffect, useState, useCallback } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Layers, ZoomIn, ZoomOut, Locate, Map } from 'lucide-react';

// Map configuration
const MAP_CONFIG = {
  style: 'mapbox://styles/mapbox/light-v11',
  center: [-80.7, 28.1] as [number, number], // Brevard County
  zoom: 9,
  minZoom: 5,
  maxZoom: 18,
};

// Choropleth color scales
const ZONING_COLORS: Record<string, string> = {
  'residential-sf': '#90CAF9',
  'residential-mf': '#1E88E5',
  'commercial': '#F57C00',
  'industrial': '#7B1FA2',
  'agricultural': '#66BB6A',
  'mixed-use': '#26A69A',
  'pud': '#AB47BC',
  'unknown': '#E0E0E0',
};

const HBU_COLORS = [
  { threshold: 0, color: '#D32F2F', label: 'Skip (0-40)' },
  { threshold: 40, color: '#F57C00', label: 'Review (40-60)' },
  { threshold: 60, color: '#FBC02D', label: 'Consider (60-75)' },
  { threshold: 75, color: '#388E3C', label: 'Bid (75-90)' },
  { threshold: 90, color: '#1B5E20', label: 'Strong Bid (90+)' },
];

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

interface MapPanelProps {
  onParcelSelect: (parcel: Parcel) => void;
  highlights?: string[];
  className?: string;
}

export function MapPanel({ onParcelSelect, highlights = [], className }: MapPanelProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [activeLayers, setActiveLayers] = useState<string[]>(['zoning']);
  const [currentZoom, setCurrentZoom] = useState(MAP_CONFIG.zoom);
  const [selectedParcelId, setSelectedParcelId] = useState<string | null>(null);

  // Initialize map
  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    mapboxgl.accessToken = process.env.NEXT_PUBLIC_MAPBOX_TOKEN || '';

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: MAP_CONFIG.style,
      center: MAP_CONFIG.center,
      zoom: MAP_CONFIG.zoom,
      minZoom: MAP_CONFIG.minZoom,
      maxZoom: MAP_CONFIG.maxZoom,
    });

    map.current.addControl(new mapboxgl.NavigationControl(), 'top-right');
    map.current.addControl(new mapboxgl.ScaleControl(), 'bottom-left');

    map.current.on('load', () => {
      setLoaded(true);
      addMapLayers();
    });

    map.current.on('zoom', () => {
      setCurrentZoom(map.current?.getZoom() || MAP_CONFIG.zoom);
    });

    return () => {
      map.current?.remove();
      map.current = null;
    };
  }, []);

  // Add map layers
  const addMapLayers = useCallback(() => {
    if (!map.current) return;

    // Add zoning districts source (placeholder - will be loaded from API)
    map.current.addSource('zoning-districts', {
      type: 'geojson',
      data: {
        type: 'FeatureCollection',
        features: [],
      },
    });

    // Zoning layer
    map.current.addLayer({
      id: 'zoning-layer',
      type: 'fill',
      source: 'zoning-districts',
      paint: {
        'fill-color': [
          'match',
          ['get', 'zone_category'],
          'residential-sf', ZONING_COLORS['residential-sf'],
          'residential-mf', ZONING_COLORS['residential-mf'],
          'commercial', ZONING_COLORS['commercial'],
          'industrial', ZONING_COLORS['industrial'],
          'agricultural', ZONING_COLORS['agricultural'],
          'mixed-use', ZONING_COLORS['mixed-use'],
          'pud', ZONING_COLORS['pud'],
          ZONING_COLORS['unknown'],
        ],
        'fill-opacity': 0.6,
      },
    });

    // Add parcels source
    map.current.addSource('parcels', {
      type: 'geojson',
      data: {
        type: 'FeatureCollection',
        features: [],
      },
    });

    // Parcels layer (visible at higher zoom)
    map.current.addLayer({
      id: 'parcels-layer',
      type: 'fill',
      source: 'parcels',
      minzoom: 13,
      paint: {
        'fill-color': [
          'case',
          ['boolean', ['feature-state', 'selected'], false],
          '#1E3A5F',
          ['boolean', ['feature-state', 'highlighted'], false],
          '#F57C00',
          '#E3F2FD',
        ],
        'fill-opacity': [
          'case',
          ['boolean', ['feature-state', 'selected'], false],
          0.8,
          ['boolean', ['feature-state', 'highlighted'], false],
          0.7,
          0.4,
        ],
        'fill-outline-color': '#1E3A5F',
      },
    });

    // Click handler for parcels
    map.current.on('click', 'parcels-layer', (e) => {
      if (!e.features?.length) return;

      const feature = e.features[0];
      const parcel: Parcel = {
        id: feature.properties?.id || '',
        parcel_id: feature.properties?.parcel_id || '',
        address: feature.properties?.address || '',
        zone_code: feature.properties?.zone_code || '',
        zone_category: feature.properties?.zone_category || '',
        hbu_score: feature.properties?.hbu_score || 0,
        foreclosure_status: feature.properties?.foreclosure_status,
        coordinates: (feature.geometry as any).coordinates[0][0],
      };

      setSelectedParcelId(parcel.id);
      onParcelSelect(parcel);

      // Show popup
      new mapboxgl.Popup()
        .setLngLat(e.lngLat)
        .setHTML(`
          <div class="p-2">
            <h3 class="font-semibold text-sm">${parcel.address}</h3>
            <p class="text-xs text-gray-600">Zone: ${parcel.zone_code}</p>
            <p class="text-xs text-gray-600">HBU Score: ${parcel.hbu_score}</p>
          </div>
        `)
        .addTo(map.current!);
    });

    // Cursor change on hover
    map.current.on('mouseenter', 'parcels-layer', () => {
      if (map.current) map.current.getCanvas().style.cursor = 'pointer';
    });
    map.current.on('mouseleave', 'parcels-layer', () => {
      if (map.current) map.current.getCanvas().style.cursor = '';
    });
  }, [onParcelSelect]);

  // Handle highlights from chat
  useEffect(() => {
    if (!map.current || !loaded) return;

    const source = map.current.getSource('parcels') as mapboxgl.GeoJSONSource;
    if (!source) return;

    // Reset all highlights, then set new ones
    // This would typically involve setting feature-state
    highlights.forEach((parcelId) => {
      map.current?.setFeatureState(
        { source: 'parcels', id: parcelId },
        { highlighted: true }
      );
    });
  }, [highlights, loaded]);

  // Layer toggle
  const toggleLayer = useCallback(
    (layerId: string) => {
      if (!map.current) return;

      const isActive = activeLayers.includes(layerId);
      if (isActive) {
        setActiveLayers(activeLayers.filter((l) => l !== layerId));
        map.current.setLayoutProperty(`${layerId}-layer`, 'visibility', 'none');
      } else {
        setActiveLayers([...activeLayers, layerId]);
        map.current.setLayoutProperty(`${layerId}-layer`, 'visibility', 'visible');
      }
    },
    [activeLayers]
  );

  // Zoom controls
  const handleZoomIn = () => map.current?.zoomIn();
  const handleZoomOut = () => map.current?.zoomOut();
  const handleLocate = () => {
    navigator.geolocation.getCurrentPosition((pos) => {
      map.current?.flyTo({
        center: [pos.coords.longitude, pos.coords.latitude],
        zoom: 14,
      });
    });
  };

  return (
    <div className={cn('relative', className)}>
      {/* Map container */}
      <div ref={mapContainer} className="absolute inset-0" />

      {/* Layer controls */}
      <div className="absolute top-4 left-4 z-10 bg-background/90 backdrop-blur rounded-lg p-2 shadow-lg">
        <div className="flex items-center gap-2 mb-2">
          <Layers className="w-4 h-4" />
          <span className="text-sm font-medium">Layers</span>
        </div>
        <div className="space-y-1">
          {[
            { id: 'zoning', label: 'Zoning', color: '#1E88E5' },
            { id: 'foreclosures', label: 'Foreclosures', color: '#EF5350' },
            { id: 'hbu', label: 'HBU Scores', color: '#388E3C' },
          ].map((layer) => (
            <button
              key={layer.id}
              onClick={() => toggleLayer(layer.id)}
              className={cn(
                'flex items-center gap-2 w-full px-2 py-1 rounded text-sm transition-colors',
                activeLayers.includes(layer.id)
                  ? 'bg-primary/10 text-primary'
                  : 'hover:bg-muted'
              )}
            >
              <span
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: layer.color }}
              />
              {layer.label}
            </button>
          ))}
        </div>
      </div>

      {/* Zoom level indicator */}
      <div className="absolute bottom-4 left-4 z-10">
        <Badge variant="secondary" className="bg-background/90 backdrop-blur">
          <Map className="w-3 h-3 mr-1" />
          Zoom: {currentZoom.toFixed(1)}
        </Badge>
      </div>

      {/* Custom zoom controls */}
      <div className="absolute bottom-4 right-4 z-10 flex flex-col gap-1">
        <Button size="icon" variant="secondary" onClick={handleZoomIn}>
          <ZoomIn className="w-4 h-4" />
        </Button>
        <Button size="icon" variant="secondary" onClick={handleZoomOut}>
          <ZoomOut className="w-4 h-4" />
        </Button>
        <Button size="icon" variant="secondary" onClick={handleLocate}>
          <Locate className="w-4 h-4" />
        </Button>
      </div>

      {/* Legend */}
      {activeLayers.includes('zoning') && (
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 z-10 bg-background/90 backdrop-blur rounded-lg p-2 shadow-lg">
          <div className="flex items-center gap-3 text-xs">
            {Object.entries(ZONING_COLORS).slice(0, 6).map(([key, color]) => (
              <div key={key} className="flex items-center gap-1">
                <span
                  className="w-3 h-3 rounded"
                  style={{ backgroundColor: color }}
                />
                <span className="capitalize">{key.replace('-', ' ')}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default MapPanel;
