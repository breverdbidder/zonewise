/**
 * ZoneWise V3 - MapPanel Component
 * Main map display with Mapbox GL, parcel selection, and zoning layers.
 */

'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

import { usePanelSyncStore } from '@/stores/panelSyncStore';
import { ParcelPopup } from './ParcelPopup';
import { ChoroplethLayer } from './ChoroplethLayer';

const MAPBOX_TOKEN = process.env.NEXT_PUBLIC_MAPBOX_TOKEN || '';
const BREVARD_BOUNDS: [[number, number], [number, number]] = [[-81.0, 27.8], [-80.2, 28.8]];
const BREVARD_CENTER: [number, number] = [-80.6077, 28.3922];

interface MapPanelProps {
  className?: string;
  onParcelSelect?: (parcelId: string) => void;
  onViewportChange?: (viewport: MapViewport) => void;
}

interface MapViewport {
  center: [number, number];
  zoom: number;
  bounds?: [[number, number], [number, number]];
}

export function MapPanel({ className = '', onParcelSelect, onViewportChange }: MapPanelProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const [mapLoaded, setMapLoaded] = useState(false);
  const [popupData, setPopupData] = useState<any>(null);
  const [popupPosition, setPopupPosition] = useState<{ x: number; y: number } | null>(null);

  const { selectedParcelId, setSelectedParcelId, mapViewport, setMapViewport, activeLayers, zoneFilter } = usePanelSyncStore();

  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    mapboxgl.accessToken = MAPBOX_TOKEN;

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/light-v11',
      center: mapViewport?.center || BREVARD_CENTER,
      zoom: mapViewport?.zoom || 10,
      maxBounds: BREVARD_BOUNDS,
      minZoom: 8,
      maxZoom: 18
    });

    const mapInstance = map.current;
    mapInstance.addControl(new mapboxgl.NavigationControl(), 'top-right');
    mapInstance.addControl(new mapboxgl.ScaleControl(), 'bottom-left');

    mapInstance.on('load', () => {
      setMapLoaded(true);
      
      // Add sources
      mapInstance.addSource('parcels', { type: 'geojson', data: { type: 'FeatureCollection', features: [] } });
      mapInstance.addSource('zoning', { type: 'geojson', data: { type: 'FeatureCollection', features: [] } });

      // Add layers
      mapInstance.addLayer({ id: 'zoning-fill', type: 'fill', source: 'zoning', paint: { 'fill-color': ['get', 'color'], 'fill-opacity': 0.5 } });
      mapInstance.addLayer({ id: 'zoning-outline', type: 'line', source: 'zoning', paint: { 'line-color': '#666666', 'line-width': 1 } });
      mapInstance.addLayer({ id: 'parcels-fill', type: 'fill', source: 'parcels', paint: { 'fill-color': 'transparent', 'fill-opacity': 0.3 } });
      mapInstance.addLayer({ id: 'parcels-outline', type: 'line', source: 'parcels', paint: { 'line-color': '#94a3b8', 'line-width': 1 } });
    });

    mapInstance.on('moveend', () => {
      const center = mapInstance.getCenter();
      const bounds = mapInstance.getBounds();
      const viewport: MapViewport = {
        center: [center.lng, center.lat],
        zoom: mapInstance.getZoom(),
        bounds: [[bounds.getSouthWest().lng, bounds.getSouthWest().lat], [bounds.getNorthEast().lng, bounds.getNorthEast().lat]]
      };
      setMapViewport(viewport);
      onViewportChange?.(viewport);
    });

    mapInstance.on('click', 'parcels-fill', (e) => {
      if (!e.features?.length) return;
      const feature = e.features[0];
      const parcelId = feature.properties?.parcel_id;
      if (parcelId) {
        setSelectedParcelId(parcelId);
        onParcelSelect?.(parcelId);
        setPopupData(feature.properties);
        setPopupPosition({ x: e.point.x, y: e.point.y });
      }
    });

    mapInstance.on('mouseenter', 'parcels-fill', () => { mapInstance.getCanvas().style.cursor = 'pointer'; });
    mapInstance.on('mouseleave', 'parcels-fill', () => { mapInstance.getCanvas().style.cursor = ''; });

    return () => { mapInstance.remove(); map.current = null; };
  }, []);

  useEffect(() => {
    if (!map.current || !mapLoaded || !mapViewport?.bounds) return;
    const [sw, ne] = mapViewport.bounds;
    fetch(`/api/v1/map/parcels?min_lng=${sw[0]}&min_lat=${sw[1]}&max_lng=${ne[0]}&max_lat=${ne[1]}`)
      .then(r => r.ok ? r.json() : null)
      .then(data => {
        if (data?.features) {
          (map.current?.getSource('parcels') as mapboxgl.GeoJSONSource)?.setData(data);
        }
      });
  }, [mapViewport?.bounds, mapLoaded]);

  const closePopup = useCallback(() => { setPopupData(null); setPopupPosition(null); }, []);

  return (
    <div className={`relative w-full h-full ${className}`}>
      <div ref={mapContainer} className="absolute inset-0 w-full h-full" />
      {!mapLoaded && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-100">
          <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
        </div>
      )}
      {mapLoaded && map.current && <ChoroplethLayer map={map.current} visible={activeLayers.includes('zoning')} zoneFilter={zoneFilter} />}
      {popupData && popupPosition && (
        <ParcelPopup data={popupData} position={popupPosition} onClose={closePopup} onAnalyze={(id) => { onParcelSelect?.(id); closePopup(); }} />
      )}
      <div className="absolute bottom-0 right-0 text-xs text-gray-500 bg-white/80 px-2 py-1">ZoneWise V3</div>
    </div>
  );
}

export default MapPanel;
