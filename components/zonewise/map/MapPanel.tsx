'use client';

import { useEffect, useRef, useState } from 'react';
import { Layers, ZoomIn, ZoomOut, Locate, Info } from 'lucide-react';

interface MapPanelProps {
  selectedParcel: string | null;
  onParcelClick: (parcelId: string) => void;
}

interface ParcelInfo {
  id: string;
  address: string;
  owner: string;
  zoningCode: string;
  acreage: number;
  justValue: number;
}

export function MapPanel({ selectedParcel, onParcelClick }: MapPanelProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const mapRef = useRef<any>(null);
  const [mapLoaded, setMapLoaded] = useState(false);
  const [hoveredParcel, setHoveredParcel] = useState<ParcelInfo | null>(null);
  const [layers, setLayers] = useState({
    zoning: true,
    parcels: true,
    aerial: false,
  });

  useEffect(() => {
    if (!mapContainer.current || mapRef.current) return;

    // Initialize Mapbox
    const initMap = async () => {
      const mapboxgl = (await import('mapbox-gl')).default;
      
      // @ts-ignore
      mapboxgl.accessToken = process.env.NEXT_PUBLIC_MAPBOX_TOKEN;

      const map = new mapboxgl.Map({
        container: mapContainer.current!,
        style: 'mapbox://styles/mapbox/light-v11',
        center: [-80.6081, 28.0836], // Brevard County center
        zoom: 10,
      });

      map.on('load', () => {
        setMapLoaded(true);
        
        // Add zoning districts layer (choropleth)
        map.addSource('zoning-districts', {
          type: 'geojson',
          data: '/api/geojson/zoning',
        });

        map.addLayer({
          id: 'zoning-fill',
          type: 'fill',
          source: 'zoning-districts',
          paint: {
            'fill-color': [
              'match',
              ['get', 'category'],
              'residential', '#4CAF50',
              'commercial', '#2196F3',
              'industrial', '#9C27B0',
              'agricultural', '#FF9800',
              'mixed-use', '#E91E63',
              '#9E9E9E', // default
            ],
            'fill-opacity': 0.4,
          },
        });

        map.addLayer({
          id: 'zoning-outline',
          type: 'line',
          source: 'zoning-districts',
          paint: {
            'line-color': '#333',
            'line-width': 1,
          },
        });

        // Add parcels layer
        map.addSource('parcels', {
          type: 'geojson',
          data: '/api/geojson/parcels',
        });

        map.addLayer({
          id: 'parcels-fill',
          type: 'fill',
          source: 'parcels',
          paint: {
            'fill-color': '#627BC1',
            'fill-opacity': 0.1,
          },
        });

        map.addLayer({
          id: 'parcels-outline',
          type: 'line',
          source: 'parcels',
          paint: {
            'line-color': '#627BC1',
            'line-width': 0.5,
          },
        });

        // Click handler for parcels
        map.on('click', 'parcels-fill', (e: any) => {
          if (e.features && e.features.length > 0) {
            const feature = e.features[0];
            onParcelClick(feature.properties.id);
          }
        });

        // Hover handler for parcels
        map.on('mousemove', 'parcels-fill', (e: any) => {
          if (e.features && e.features.length > 0) {
            map.getCanvas().style.cursor = 'pointer';
            const props = e.features[0].properties;
            setHoveredParcel({
              id: props.id,
              address: props.address,
              owner: props.owner,
              zoningCode: props.zoning_code,
              acreage: props.acreage,
              justValue: props.just_value,
            });
          }
        });

        map.on('mouseleave', 'parcels-fill', () => {
          map.getCanvas().style.cursor = '';
          setHoveredParcel(null);
        });
      });

      mapRef.current = map;
    };

    initMap();

    return () => {
      mapRef.current?.remove();
    };
  }, [onParcelClick]);

  // Fly to selected parcel
  useEffect(() => {
    if (!selectedParcel || !mapRef.current || !mapLoaded) return;

    const fetchAndFlyTo = async () => {
      try {
        const response = await fetch(`/api/parcels/${selectedParcel}`);
        const parcel = await response.json();
        
        if (parcel.geometry?.coordinates) {
          mapRef.current.flyTo({
            center: parcel.geometry.coordinates[0][0], // First point of polygon
            zoom: 17,
            duration: 1500,
          });
        }
      } catch (error) {
        console.error('Failed to fetch parcel:', error);
      }
    };

    fetchAndFlyTo();
  }, [selectedParcel, mapLoaded]);

  // Toggle layer visibility
  const toggleLayer = (layerId: string) => {
    if (!mapRef.current || !mapLoaded) return;

    const map = mapRef.current;
    const layerIds: Record<string, string[]> = {
      zoning: ['zoning-fill', 'zoning-outline'],
      parcels: ['parcels-fill', 'parcels-outline'],
    };

    const ids = layerIds[layerId] || [];
    const newVisibility = !layers[layerId as keyof typeof layers];

    ids.forEach((id) => {
      map.setLayoutProperty(id, 'visibility', newVisibility ? 'visible' : 'none');
    });

    setLayers((prev) => ({ ...prev, [layerId]: newVisibility }));
  };

  return (
    <div className="relative h-full">
      {/* Map Container */}
      <div ref={mapContainer} className="h-full w-full" />

      {/* Loading Overlay */}
      {!mapLoaded && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-100">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2" />
            <p className="text-gray-600">Loading map...</p>
          </div>
        </div>
      )}

      {/* Layer Controls */}
      <div className="absolute top-4 right-4 bg-white rounded-lg shadow-lg p-2">
        <div className="flex flex-col gap-1">
          <button
            onClick={() => toggleLayer('zoning')}
            className={`flex items-center gap-2 px-3 py-2 rounded text-sm ${
              layers.zoning ? 'bg-blue-100 text-blue-700' : 'hover:bg-gray-100'
            }`}
          >
            <Layers className="h-4 w-4" />
            Zoning
          </button>
          <button
            onClick={() => toggleLayer('parcels')}
            className={`flex items-center gap-2 px-3 py-2 rounded text-sm ${
              layers.parcels ? 'bg-blue-100 text-blue-700' : 'hover:bg-gray-100'
            }`}
          >
            <Layers className="h-4 w-4" />
            Parcels
          </button>
        </div>
      </div>

      {/* Zoom Controls */}
      <div className="absolute bottom-24 right-4 bg-white rounded-lg shadow-lg">
        <button
          onClick={() => mapRef.current?.zoomIn()}
          className="p-2 hover:bg-gray-100 rounded-t-lg border-b"
        >
          <ZoomIn className="h-5 w-5" />
        </button>
        <button
          onClick={() => mapRef.current?.zoomOut()}
          className="p-2 hover:bg-gray-100"
        >
          <ZoomOut className="h-5 w-5" />
        </button>
        <button
          onClick={() => {
            navigator.geolocation.getCurrentPosition((pos) => {
              mapRef.current?.flyTo({
                center: [pos.coords.longitude, pos.coords.latitude],
                zoom: 14,
              });
            });
          }}
          className="p-2 hover:bg-gray-100 rounded-b-lg border-t"
        >
          <Locate className="h-5 w-5" />
        </button>
      </div>

      {/* Hovered Parcel Info */}
      {hoveredParcel && (
        <div className="absolute bottom-4 left-4 bg-white rounded-lg shadow-lg p-3 max-w-xs">
          <div className="flex items-start gap-2">
            <Info className="h-4 w-4 text-blue-600 mt-0.5" />
            <div className="text-sm">
              <p className="font-medium">{hoveredParcel.address}</p>
              <p className="text-gray-600">
                Zoning: <span className="font-medium">{hoveredParcel.zoningCode}</span>
              </p>
              <p className="text-gray-600">
                {hoveredParcel.acreage?.toFixed(2)} acres
              </p>
              <p className="text-gray-600">
                Value: ${hoveredParcel.justValue?.toLocaleString()}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Legend */}
      <div className="absolute bottom-4 right-4 bg-white rounded-lg shadow-lg p-3">
        <p className="text-xs font-medium mb-2">Zoning Categories</p>
        <div className="space-y-1 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-4 h-3 rounded" style={{ backgroundColor: '#4CAF50' }} />
            <span>Residential</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-3 rounded" style={{ backgroundColor: '#2196F3' }} />
            <span>Commercial</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-3 rounded" style={{ backgroundColor: '#9C27B0' }} />
            <span>Industrial</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-3 rounded" style={{ backgroundColor: '#FF9800' }} />
            <span>Agricultural</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-3 rounded" style={{ backgroundColor: '#E91E63' }} />
            <span>Mixed-Use</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default MapPanel;
