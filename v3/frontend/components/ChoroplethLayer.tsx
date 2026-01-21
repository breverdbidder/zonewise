/**
 * ZoneWise V3 - ChoroplethLayer Component
 * Zoning visualization layer with color-coded districts.
 */

'use client';

import { useEffect, useState, useCallback } from 'react';
import type mapboxgl from 'mapbox-gl';

// Zone colors
const ZONE_COLORS: Record<string, string> = {
  'RS-1': '#90EE90', 'RS-2': '#98FB98', 'RS-3': '#7CFC00', 'RS-4': '#32CD32', 'RS-5': '#228B22', 'RS-6': '#006400',
  'RM-4': '#FFD700', 'RM-8': '#FFA500', 'RM-12': '#FF8C00', 'RM-15': '#FF6347',
  'BU-1': '#4169E1', 'BU-1-A': '#0000CD', 'BU-2': '#00008B',
  'IU-1': '#808080', 'IU-2': '#696969', 'IU-3': '#505050',
  'AU': '#8B4513', 'AA': '#A0522D', 'AE': '#CD853F',
  'PUD': '#DDA0DD', 'PIP': '#BA55D3', 'RVP': '#9932CC'
};

interface ChoroplethLayerProps {
  map: mapboxgl.Map;
  visible: boolean;
  zoneFilter?: string[];
  opacity?: number;
}

export function ChoroplethLayer({ map, visible, zoneFilter = [], opacity = 0.5 }: ChoroplethLayerProps) {
  const [zoningData, setZoningData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  // Load zoning data
  useEffect(() => {
    if (!visible) return;
    
    const loadZoning = async () => {
      setLoading(true);
      try {
        const response = await fetch('/api/v1/map/zoning');
        if (response.ok) {
          const data = await response.json();
          setZoningData(data);
        }
      } catch (error) {
        console.error('Failed to load zoning data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadZoning();
  }, [visible]);

  // Update map source when data changes
  useEffect(() => {
    if (!map || !zoningData) return;

    const source = map.getSource('zoning') as mapboxgl.GeoJSONSource;
    if (source) {
      // Add colors to features
      const coloredFeatures = zoningData.features.map((feature: any) => ({
        ...feature,
        properties: {
          ...feature.properties,
          color: ZONE_COLORS[feature.properties.zone_code] || '#808080'
        }
      }));

      source.setData({
        type: 'FeatureCollection',
        features: coloredFeatures
      });
    }
  }, [map, zoningData]);

  // Update visibility
  useEffect(() => {
    if (!map) return;

    const layers = ['zoning-fill', 'zoning-outline'];
    layers.forEach(layerId => {
      if (map.getLayer(layerId)) {
        map.setLayoutProperty(layerId, 'visibility', visible ? 'visible' : 'none');
      }
    });
  }, [map, visible]);

  // Update opacity
  useEffect(() => {
    if (!map || !map.getLayer('zoning-fill')) return;
    map.setPaintProperty('zoning-fill', 'fill-opacity', opacity);
  }, [map, opacity]);

  // Apply zone filter
  useEffect(() => {
    if (!map || !map.getLayer('zoning-fill')) return;

    if (zoneFilter.length > 0) {
      const filter = ['in', ['get', 'zone_code'], ['literal', zoneFilter]];
      map.setFilter('zoning-fill', filter);
      map.setFilter('zoning-outline', filter);
    } else {
      map.setFilter('zoning-fill', null);
      map.setFilter('zoning-outline', null);
    }
  }, [map, zoneFilter]);

  return null; // This is a map layer control, no DOM rendering
}

// Legend component for external use
export function ZoningLegend({ zones = Object.keys(ZONE_COLORS).slice(0, 8) }) {
  return (
    <div className="bg-white rounded-lg shadow-lg p-3 text-xs">
      <div className="font-semibold mb-2">Zoning Districts</div>
      <div className="grid grid-cols-2 gap-1">
        {zones.map(zone => (
          <div key={zone} className="flex items-center gap-2">
            <div className="w-3 h-3 rounded" style={{ backgroundColor: ZONE_COLORS[zone] }} />
            <span>{zone}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ChoroplethLayer;
