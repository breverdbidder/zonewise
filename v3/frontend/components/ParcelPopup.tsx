/**
 * ZoneWise V3 - ParcelPopup Component
 * Property details popup on map click.
 */

'use client';

import { X, MapPin, Home, DollarSign, Layers } from 'lucide-react';

interface ParcelPopupProps {
  data: {
    parcel_id: string;
    address?: string;
    zone_code?: string;
    lot_size_sqft?: number;
    assessed_value?: number;
    year_built?: number;
  };
  position: { x: number; y: number };
  onClose: () => void;
  onAnalyze: (parcelId: string) => void;
}

export function ParcelPopup({ data, position, onClose, onAnalyze }: ParcelPopupProps) {
  const formatCurrency = (value?: number) => 
    value ? `$${value.toLocaleString()}` : 'N/A';
  
  const formatSqft = (value?: number) => 
    value ? `${value.toLocaleString()} sq ft` : 'N/A';

  return (
    <div
      className="absolute z-50 bg-white rounded-lg shadow-xl border border-gray-200 w-72"
      style={{
        left: Math.min(position.x, window.innerWidth - 300),
        top: Math.min(position.y, window.innerHeight - 300),
        transform: 'translate(-50%, -100%) translateY(-10px)'
      }}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 border-b bg-gray-50 rounded-t-lg">
        <span className="font-medium text-sm text-gray-900 truncate">{data.parcel_id}</span>
        <button onClick={onClose} className="p-1 hover:bg-gray-200 rounded transition-colors">
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Content */}
      <div className="p-3 space-y-2">
        {data.address && (
          <div className="flex items-start gap-2">
            <MapPin className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" />
            <span className="text-sm text-gray-600">{data.address}</span>
          </div>
        )}

        <div className="grid grid-cols-2 gap-2 text-sm">
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-blue-500" />
            <span className="font-medium">{data.zone_code || 'N/A'}</span>
          </div>
          
          <div className="flex items-center gap-2">
            <Home className="w-4 h-4 text-green-500" />
            <span>{formatSqft(data.lot_size_sqft)}</span>
          </div>
        </div>

        <div className="flex items-center gap-2 text-sm">
          <DollarSign className="w-4 h-4 text-yellow-600" />
          <span>Assessed: {formatCurrency(data.assessed_value)}</span>
        </div>

        {data.year_built && (
          <div className="text-xs text-gray-500">
            Built: {data.year_built}
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="px-3 pb-3">
        <button
          onClick={() => onAnalyze(data.parcel_id)}
          className="w-full py-2 bg-blue-500 text-white text-sm font-medium rounded-lg hover:bg-blue-600 transition-colors"
        >
          Analyze This Parcel
        </button>
      </div>

      {/* Arrow */}
      <div className="absolute left-1/2 bottom-0 transform -translate-x-1/2 translate-y-full">
        <div className="w-0 h-0 border-l-8 border-r-8 border-t-8 border-l-transparent border-r-transparent border-t-white" />
      </div>
    </div>
  );
}

export default ParcelPopup;
