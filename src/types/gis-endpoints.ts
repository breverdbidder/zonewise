/**
 * ZoneWise GIS Endpoint Types V2.0
 * Generated: 2026-01-23
 */

export type GISStatus =
  | 'WORKING'
  | 'TEMPORARY_OUTAGE'
  | 'SERVER_DOWN'
  | 'TILE_ONLY'
  | 'PDF_ONLY'
  | 'MANUAL_DATA'
  | 'NOT_FOUND';

export type DataSource =
  | 'FEATURE_SERVICE'
  | 'MAP_SERVICE'
  | 'TILE_SERVICE'
  | 'PDF_MAP'
  | 'ELAWS_EMBEDDED'
  | null;

export type FallbackStrategy =
  | 'BCPAO_PARCEL_OVERLAY'
  | 'ELAWS_MUNICODE'
  | 'SUPABASE_ZONING_DISTRICTS'
  | 'CONTACT_CITY_GIS'
  | 'MANUAL_DIGITIZATION'
  | 'COUNTY_OVERLAY';

export interface RateLimitConfig {
  requests_per_minute: number;
  max_records: number;
}

export interface QueryParams {
  where: string;
  outFields: string;
  returnGeometry: boolean;
  f: 'geojson' | 'json' | 'pjson';
}

export interface GISEndpoint {
  jurisdiction: string;
  jurisdiction_id: number;
  status: GISStatus;
  data_source: DataSource;
  parcels: number;
  url: string | null;
  alternate_viewer?: string;
  zone_field: string | null;
  geometry_type: string | null;
  spatial_reference: number | null;
  rate_limit: RateLimitConfig | null;
  query_params: QueryParams | null;
  fallback_strategy: FallbackStrategy;
  contact?: string;
  last_verified: string;
  outage_since?: string;
  notes: string;
}

export interface CatalogMetadata {
  version: string;
  created: string;
  last_updated: string;
  description: string;
  maintainer: string;
}

export interface PriorityAction {
  jurisdiction_id: number;
  action: string;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
}

export interface CoverageSummary {
  api_accessible_parcels: number;
  total_known_parcels: number;
  api_coverage_percent: number;
  with_fallback_coverage_percent: number;
}

export interface FallbackStrategyDef {
  description: string;
  implementation: string;
}

export interface GISCatalog {
  metadata: CatalogMetadata;
  endpoints: Record<string, GISEndpoint>;
  summary: {
    by_status: Record<GISStatus, string[]>;
    coverage: CoverageSummary;
    priority_actions: PriorityAction[];
  };
  fallback_strategies: Record<FallbackStrategy, FallbackStrategyDef>;
}

// Jurisdiction ID to name mapping (compile-time safe)
export const JURISDICTION_IDS = {
  MELBOURNE: 1,
  PALM_BAY: 2,
  INDIAN_HARBOUR_BEACH: 3,
  TITUSVILLE: 4,
  COCOA: 5,
  SATELLITE_BEACH: 6,
  COCOA_BEACH: 7,
  ROCKLEDGE: 8,
  WEST_MELBOURNE: 9,
  CAPE_CANAVERAL: 10,
  INDIALANTIC: 11,
  MELBOURNE_BEACH: 12,
  UNINCORPORATED: 13,
  MALABAR: 14,
  GRANT_VALKARIA: 15,
  PALM_SHORES: 16,
  MELBOURNE_VILLAGE: 17,
} as const;

export type JurisdictionId = typeof JURISDICTION_IDS[keyof typeof JURISDICTION_IDS];

// Helper to check if endpoint is queryable
export function isQueryable(endpoint: GISEndpoint): boolean {
  return (
    endpoint.status === 'WORKING' &&
    endpoint.url !== null &&
    endpoint.query_params !== null
  );
}

// Helper to get working endpoints
export function getWorkingEndpoints(catalog: GISCatalog): GISEndpoint[] {
  return Object.values(catalog.endpoints).filter(
    (e) => e.status === 'WORKING'
  );
}
