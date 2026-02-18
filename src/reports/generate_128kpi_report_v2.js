#!/usr/bin/env node
/**
 * ============================================================================
 * BIDDEED.AI / ZONEWISE 128-KPI PROPERTY REPORT GENERATOR
 * ============================================================================
 * Beats PropertyOnion (96 KPIs) + PropZone (74 KPIs)
 * 
 * Data Sources:
 *   fl_parcels        → 40+ property columns (FDOR Statewide Cadastral)
 *   parcel_zones      → zone_code linkage
 *   zoning_districts  → zone details + embedded DIMS JSON
 *   zone_standards    → dimensional standards (setbacks, FAR, height)
 *   permitted_uses    → allowed uses per zone
 *   Esri World Imagery → aerial photos
 *
 * Usage:
 *   node generate_128kpi_report.js --parcel "27 3702-88-A-3"
 *   node generate_128kpi_report.js --address "720 VERBENIA DR" --city "SATELLITE BEACH"
 *   node generate_128kpi_report.js --zip 32937 --limit 5
 */

const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        Header, Footer, AlignmentType, LevelFormat, ImageRun,
        HeadingLevel, BorderStyle, WidthType, ShadingType, PageNumber, PageBreak } = require('docx');
const fs = require('fs');
const { execSync } = require('child_process');

// =============================================================================
// CONFIGURATION
// =============================================================================
const SUPABASE_URL = 'https://mocerqjnksmhcjzxrewo.supabase.co';
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_KEY || 
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1vY2VycWpua3NtaGNqenhyZXdvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDUzMjUyNiwiZXhwIjoyMDgwMTA4NTI2fQ.fL255mO0V8-rrU0Il3L41cIdQXUau-HRQXiamTqp9nE';

const BREVARD_MILLAGE = 0.01812; // ~18.12 mills total Brevard avg
const INSURANCE_RATE_PER_SQFT = 1.25; // FL avg
const RENTAL_RATE_PER_SQFT = 1.15; // Brevard avg $/sqft/month
const CAP_RATE_AREA = 0.065; // 6.5% Brevard avg

const COLORS = {
  NAVY: '1E3A5F', GREEN_BG: 'E8F5E9', BLUE_BG: 'E3F2FD',
  RED_BG: 'FFEBEE', ORANGE_BG: 'FFF3E0', PURPLE_BG: 'F3E5F5',
  ALT_ROW: 'F5F7FA', WHITE: 'FFFFFF', LIGHT_GRAY: 'F0F0F0',
  BORDER: 'CCCCCC', DARK_TEXT: '333333'
};

// FDOR Code Maps
const DOR_USE_CODES = {
  '000': 'Vacant Residential', '001': 'Single Family', '002': 'Mobile Home',
  '003': 'Multi-Family (2-4)', '004': 'Condominium', '005': 'Cooperatives',
  '006': 'Retirement Homes', '007': 'Misc Residential', '008': 'Multi-Family (5+)',
  '009': 'Residential Common', '010': 'Vacant Commercial', '011': 'Stores/Retail',
  '012': 'Mixed Use', '014': 'Supermarket', '016': 'Community Shopping',
  '017': 'Office (1 story)', '018': 'Office (multi)', '019': 'Medical Office',
  '020': 'AC Warehouse', '021': 'Restaurant', '022': 'Gas Station',
  '023': 'Financial', '024': 'Insurance', '025': 'Repair Service',
  '027': 'Auto Sales', '028': 'Parking Lot', '029': 'Wholesale',
  '030': 'Florist/Greenhouse', '032': 'Dry Cleaners', '033': 'Hotel',
  '034': 'Motel', '039': 'Theaters', '040': 'Vacant Industrial',
  '041': 'Light Manufacturing', '048': 'Warehousing', '070': 'Church',
  '071': 'Private School', '072': 'Private Hospital', '073': 'Nursing Home',
  '080': 'Undefined Government', '081': 'Military', '082': 'Forest/Parks',
  '083': 'Public Schools', '084': 'Colleges', '085': 'Hospitals',
  '086': 'County', '087': 'State', '088': 'Federal', '089': 'Municipal',
  '091': 'Utility', '092': 'Mining', '093': 'Subsurface', '094': 'ROW',
  '095': 'Rivers/Lakes', '097': 'Outdoor Recreation', '099': 'Acreage'
};

const CONSTRUCTION_CLASS = {
  1: 'Superior/Fireproof', 2: 'Excellent/Masonry', 3: 'Good/Frame',
  4: 'Average', 5: 'Below Average', 6: 'Economy', 0: 'N/A'
};

const IMP_QUALITY = {
  1: 'Excellent', 2: 'Very Good', 3: 'Good',
  4: 'Average', 5: 'Below Average', 6: 'Poor', 0: 'N/A'
};

const FL_COUNTY_MAP = {
  11:'Alachua',12:'Baker',13:'Bay',14:'Bradford',15:'Brevard',16:'Broward',
  17:'Calhoun',18:'Charlotte',19:'Citrus',20:'Clay',21:'Collier',22:'Columbia',
  23:'Miami-Dade',24:'DeSoto',25:'Dixie',26:'Duval',27:'Escambia',28:'Flagler',
  29:'Franklin',30:'Gadsden',31:'Gilchrist',32:'Glades',33:'Gulf',34:'Hamilton',
  35:'Hardee',36:'Hendry',37:'Hernando',38:'Highlands',39:'Hillsborough',
  40:'Holmes',41:'Indian River',42:'Jackson',43:'Jefferson',44:'Lafayette',
  45:'Lake',46:'Lee',47:'Leon',48:'Levy',49:'Liberty',50:'Madison',51:'Manatee',
  52:'Marion',53:'Martin',54:'Monroe',55:'Nassau',56:'Okaloosa',57:'Okeechobee',
  58:'Orange',59:'Osceola',60:'Palm Beach',61:'Pasco',62:'Pinellas',63:'Polk',
  64:'Putnam',65:'Santa Rosa',66:'Sarasota',67:'Seminole',68:'St. Johns',
  69:'St. Lucie',70:'Sumter',71:'Suwannee',72:'Taylor',73:'Union',74:'Volusia',
  75:'Wakulla',76:'Walton',77:'Washington'
};

// =============================================================================
// SUPABASE HELPERS
// =============================================================================
function supaFetch(path) {
  const url = `${SUPABASE_URL}${path}`;
  try {
    // Escape single quotes in URL for shell
    const safeUrl = url.replace(/'/g, "'\\''");
    const result = execSync(
      `curl -s '${safeUrl}' -H 'apikey: ${SUPABASE_KEY}' -H 'Authorization: Bearer ${SUPABASE_KEY}'`,
      { maxBuffer: 10 * 1024 * 1024, timeout: 30000 }
    );
    const text = result.toString().trim();
    if (!text) return [];
    return JSON.parse(text);
  } catch (e) {
    console.error(`  supaFetch error: ${e.message?.substring(0, 200)}`);
    return [];
  }
}

// =============================================================================
// FEMA NFHL FLOOD ZONE API (Free, no key required)
// =============================================================================
const FEMA_NFHL_URL = 'https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer';

function fetchFemaFloodZone(lat, lng) {
  try {
    // Layer 28 = Flood Hazard Zones (S_Fld_Haz_Ar)
    const floodUrl = `${FEMA_NFHL_URL}/28/query?geometry=${lng},${lat}&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=FLD_ZONE,ZONE_SUBTY,SFHA_TF,STATIC_BFE,DEPTH,VELOCITY,SOURCE_CIT,DFIRM_ID&returnGeometry=false&f=json`;
    const floodResult = execSync(`curl -s '${floodUrl}'`, { timeout: 15000 });
    const floodData = JSON.parse(floodResult.toString());
    const flood = floodData?.features?.[0]?.attributes || null;

    // Layer 3 = FIRM Panels
    const firmUrl = `${FEMA_NFHL_URL}/3/query?geometry=${lng},${lat}&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=FIRM_PAN,EFF_DATE,PANEL_TYP,DFIRM_ID&returnGeometry=false&f=json`;
    const firmResult = execSync(`curl -s '${firmUrl}'`, { timeout: 15000 });
    const firmData = JSON.parse(firmResult.toString());
    const firm = firmData?.features?.[0]?.attributes || null;

    if (!flood) return null;

    // Parse FEMA zone into risk tier
    const zone = flood.FLD_ZONE || 'Unknown';
    const sfha = flood.SFHA_TF === 'T';
    const bfe = flood.STATIC_BFE > -9000 ? flood.STATIC_BFE : null;
    const depth = flood.DEPTH > -9000 ? flood.DEPTH : null;
    const velocity = flood.VELOCITY > -9000 ? flood.VELOCITY : null;

    let riskTier, insuranceReq;
    if (['VE', 'V', 'V1-V30'].some(z => zone.startsWith(z))) {
      riskTier = 'EXTREME';
      insuranceReq = 'MANDATORY (Coastal High Velocity)';
    } else if (['AE', 'A', 'AH', 'AO', 'AR', 'A99'].some(z => zone.startsWith(z))) {
      riskTier = 'HIGH';
      insuranceReq = 'MANDATORY (100-Year Floodplain)';
    } else if (flood.ZONE_SUBTY?.includes('0.2 PCT')) {
      riskTier = 'MODERATE';
      insuranceReq = 'Recommended (500-Year Floodplain)';
    } else if (zone === 'X' || zone === 'C' || zone === 'B') {
      riskTier = 'LOW';
      insuranceReq = 'Optional (Minimal Flood Hazard)';
    } else if (zone === 'D') {
      riskTier = 'UNDETERMINED';
      insuranceReq = 'Recommended (Undetermined Risk)';
    } else {
      riskTier = 'UNKNOWN';
      insuranceReq = 'Check with insurer';
    }

    // Parse FIRM effective date
    let firmEffDate = null;
    if (firm?.EFF_DATE) {
      firmEffDate = new Date(firm.EFF_DATE).toISOString().split('T')[0];
    }

    return {
      zone, subtype: flood.ZONE_SUBTY || '', sfha, bfe, depth, velocity,
      riskTier, insuranceReq, dfirmId: flood.DFIRM_ID,
      firmPanel: firm?.FIRM_PAN || null, firmEffDate,
      sourceCitation: flood.SOURCE_CIT,
    };
  } catch (e) {
    console.error(`  FEMA API error: ${e.message?.substring(0, 100)}`);
    return null;
  }
}

// =============================================================================
// DATA FETCHERS
// =============================================================================
function fetchParcel(parcelId) {
  const encoded = encodeURIComponent(parcelId);
  const data = supaFetch(`/rest/v1/fl_parcels?select=*&parcel_id=eq.${encoded}&limit=1`);
  return data[0] || null;
}

function fetchParcelByAddress(address, city) {
  const addr = encodeURIComponent(`%${address}%`);
  let q = `/rest/v1/fl_parcels?select=*&phy_addr1=ilike.${addr}&co_no=eq.15&limit=1`;
  if (city) q += `&phy_city=ilike.${encodeURIComponent(`%${city}%`)}`;
  const data = supaFetch(q);
  return data[0] || null;
}

function fetchZoning(parcelId) {
  const encoded = encodeURIComponent(parcelId);
  const data = supaFetch(
    `/rest/v1/parcel_zones?select=*,zoning_districts!inner(*)&parcel_id=eq.${encoded}&limit=1`
  );
  return data[0] || null;
}

// Smart zone inference: DOR_UC → category → best-match zoning_district with DIMS
const DOR_TO_CATEGORY = {
  '000': 'residential', '001': 'residential', '002': 'residential', '003': 'residential',
  '004': 'residential', '005': 'residential', '006': 'residential', '007': 'residential',
  '008': 'residential', '009': 'residential',
  '010': 'commercial', '011': 'commercial', '012': 'mixed_use', '014': 'commercial',
  '016': 'commercial', '017': 'commercial', '018': 'commercial', '019': 'commercial',
  '020': 'industrial', '021': 'commercial', '022': 'commercial', '023': 'commercial',
  '024': 'commercial', '025': 'commercial', '027': 'commercial', '028': 'commercial',
  '029': 'commercial', '030': 'commercial', '033': 'commercial', '034': 'commercial',
  '040': 'industrial', '041': 'industrial', '048': 'industrial',
  '070': 'special', '071': 'special', '072': 'special', '073': 'special',
  '080': 'special', '081': 'special', '082': 'conservation', '083': 'special',
};

// Map DOR_UC to likely zone code prefix for residential
const DOR_TO_ZONE_HINT = {
  '001': 'R-1', '002': 'R-1', '003': 'R-2', '004': 'R-3', '008': 'R-3',
  '011': 'C-1', '017': 'C-1', '018': 'C-2', '041': 'I-1', '048': 'I-1',
};

function inferZoning(parcel) {
  // Find jurisdiction by city name — prefer exact match
  const cityName = parcel.phy_city;
  if (!cityName) return null;
  
  // Try exact match first, then fuzzy
  let jurisdictions = supaFetch(
    `/rest/v1/jurisdictions?select=id,name&county=eq.Brevard&name=eq.${encodeURIComponent(cityName.split(' ').map(w=>w.charAt(0)+w.slice(1).toLowerCase()).join(' '))}&limit=1`
  );
  if (!jurisdictions || !jurisdictions[0]) {
    jurisdictions = supaFetch(
      `/rest/v1/jurisdictions?select=id,name&county=eq.Brevard&name=ilike.${encodeURIComponent(`%${cityName}%`)}&limit=5`
    );
    // Pick shortest name match (most specific)
    if (jurisdictions && jurisdictions.length > 1) {
      jurisdictions.sort((a, b) => a.name.length - b.name.length);
    }
  }
  if (!jurisdictions || !jurisdictions[0]) return null;
  const jurId = jurisdictions[0].id;
  
  // Get all zones for this jurisdiction with DIMS
  const zones = supaFetch(
    `/rest/v1/zoning_districts?select=id,code,name,category,description&jurisdiction_id=eq.${jurId}`
  );
  if (!zones || zones.length === 0) return null;
  
  // Find best match based on DOR use code
  const dorUc = parcel.dor_uc || '001';
  const category = DOR_TO_CATEGORY[dorUc] || 'residential';
  const zoneHint = DOR_TO_ZONE_HINT[dorUc] || 'R-1';
  
  // Priority: exact code match → category match with DIMS → first category match
  let bestZone = zones.find(z => z.code === zoneHint && z.description?.includes('DIMS'));
  if (!bestZone) bestZone = zones.find(z => z.category === category && z.description?.includes('DIMS'));
  if (!bestZone) bestZone = zones.find(z => z.category === category);
  if (!bestZone) bestZone = zones[0];
  
  return {
    zone_code: bestZone.code,
    zone_name: bestZone.name,
    zoning_districts: bestZone,
    _inferred: true,
    _jurisdiction: jurisdictions[0].name,
  };
}

function fetchZoneStandards(districtId) {
  const data = supaFetch(
    `/rest/v1/zone_standards?select=*&zoning_district_id=eq.${districtId}&limit=1`
  );
  return data[0] || null;
}

function fetchPermittedUses(districtId) {
  const data = supaFetch(
    `/rest/v1/permitted_uses?select=*&zoning_district_id=eq.${districtId}&limit=20`
  );
  return data || [];
}

function fetchAreaStats(coNo, zipCode) {
  // Fetch area comparison data for market analysis KPIs
  const data = supaFetch(
    `/rest/v1/fl_parcels?select=jv,tot_lvg_ar,lnd_sqfoot,sale_prc1,sale_yr1&co_no=eq.${coNo}&phy_zipcd=eq.${zipCode}&jv=gt.0&tot_lvg_ar=gt.0&limit=200`
  );
  return data || [];
}

// =============================================================================
// DIMS JSON PARSER (embedded in zoning_districts.description)
// =============================================================================
function parseDimsJson(description) {
  if (!description) return null;
  const match = description.match(/<!--DIMS:(\{.*?\})-->/s);
  if (!match) return null;
  try { return JSON.parse(match[1]); } catch { return null; }
}

// =============================================================================
// 128 KPI COMPUTATION ENGINE
// =============================================================================
function compute128KPIs(parcel, zoning, standards, dims, uses, areaStats, fema) {
  const p = parcel;
  const z = zoning?.zoning_districts || {};
  const s = standards || {};
  const d = dims || {};
  
  // Parse address components
  const addrParts = (p.phy_addr1 || '').match(/^(\d+)\s+(.+)$/) || [];
  const streetNum = addrParts[1] || '';
  const streetName = addrParts[2] || p.phy_addr1 || '';
  
  // Computed values
  const buildingValue = Math.max(0, (p.jv || 0) - (p.lnd_val || 0));
  const pricePerSqft = p.tot_lvg_ar > 0 ? (p.jv / p.tot_lvg_ar) : 0;
  const landPricePerSqft = p.lnd_sqfoot > 0 ? (p.lnd_val / p.lnd_sqfoot) : 0;
  const improvementRatio = p.jv > 0 ? (buildingValue / p.jv) : 0;
  const appreciationSinceSale = p.sale_prc1 > 0 ? ((p.jv - p.sale_prc1) / p.sale_prc1 * 100) : null;
  const annualTax = Math.round(p.jv * BREVARD_MILLAGE);
  const insuranceEst = Math.round((p.tot_lvg_ar || 0) * INSURANCE_RATE_PER_SQFT);
  const monthlyRentEst = Math.round((p.tot_lvg_ar || 0) * RENTAL_RATE_PER_SQFT);
  const annualRentEst = monthlyRentEst * 12;
  const grossRentMult = annualRentEst > 0 ? (p.jv / annualRentEst).toFixed(1) : 'N/A';
  const capRate = p.jv > 0 ? ((annualRentEst - annualTax - insuranceEst) / p.jv * 100) : 0;
  const priceToRent = monthlyRentEst > 0 ? (p.jv / (monthlyRentEst * 12)).toFixed(1) : 'N/A';
  
  // Area stats computations
  const areaValues = areaStats.filter(a => a.jv > 0).map(a => a.jv);
  const areaMedianValue = areaValues.length > 0 ? areaValues.sort((a,b) => a-b)[Math.floor(areaValues.length/2)] : 0;
  const areaPPSqft = areaStats.filter(a => a.tot_lvg_ar > 0);
  const areaAvgPPSqft = areaPPSqft.length > 0 ? Math.round(areaPPSqft.reduce((s,a) => s + a.jv/a.tot_lvg_ar, 0) / areaPPSqft.length) : 0;
  const valueVsMedian = areaMedianValue > 0 ? ((p.jv - areaMedianValue) / areaMedianValue * 100).toFixed(1) : 'N/A';
  const recentSales = areaStats.filter(a => a.sale_yr1 >= 2023 && a.sale_prc1 > 0);
  
  // Zoning computations
  const maxFar = d.floor_area_ratio || s.max_far || null;
  const maxCoverage = d.coverage_pct || s.max_lot_coverage_pct || null;
  const maxBuildingArea = maxFar && p.lnd_sqfoot ? Math.round(p.lnd_sqfoot * maxFar) : null;
  const unusedRights = maxBuildingArea ? Math.max(0, maxBuildingArea - (p.tot_lvg_ar || 0)) : null;
  const farUtilization = maxFar && p.lnd_sqfoot && p.tot_lvg_ar ? 
    ((p.tot_lvg_ar / p.lnd_sqfoot / maxFar) * 100).toFixed(1) : null;

  // Risk scoring
  let riskScore = 50; // baseline
  if (p.eff_yr_blt > 0 && p.eff_yr_blt < 1970) riskScore += 10;
  if ((p.const_clas || 0) >= 5) riskScore += 10;
  if ((p.imp_qual || 0) >= 5) riskScore += 10;
  if (p.jv > areaMedianValue * 1.5) riskScore += 5;
  if (buildingValue < p.lnd_val * 0.3) riskScore += 5; // land > building = aging structure
  // FEMA flood risk adjustments
  if (fema) {
    if (fema.riskTier === 'EXTREME') riskScore += 20;
    else if (fema.riskTier === 'HIGH') riskScore += 15;
    else if (fema.riskTier === 'MODERATE') riskScore += 5;
    else if (fema.riskTier === 'LOW') riskScore -= 5;
  }
  riskScore = Math.min(100, Math.max(0, riskScore));

  // Opportunity scoring
  let oppScore = 50;
  if (appreciationSinceSale !== null && appreciationSinceSale > 20) oppScore += 10;
  if (pricePerSqft > 0 && pricePerSqft < areaAvgPPSqft * 0.85) oppScore += 15;
  if (unusedRights && unusedRights > p.tot_lvg_ar) oppScore += 10;
  if (p.av_hmstd > 0) oppScore -= 5; // homestead = harder to acquire
  oppScore = Math.min(100, Math.max(0, oppScore));

  // Investment grade
  const investGrade = oppScore >= 80 ? 'A+' : oppScore >= 70 ? 'A' : oppScore >= 60 ? 'B' : oppScore >= 40 ? 'C' : 'D';

  // Permitted uses summary
  const permittedList = uses.filter(u => u.use_type === 'permitted').map(u => u.use_description);
  const conditionalList = uses.filter(u => u.requires_special_permit).map(u => u.use_description);
  const isSTRAllowed = uses.some(u => u.is_short_term_rental);
  const isADUAllowed = uses.some(u => u.is_adu);
  const isMixedUse = uses.some(u => u.is_mixed_use);

  // =========================================================================
  // FULL 128 KPI OBJECT
  // =========================================================================
  return {
    _meta: {
      version: '2.0.0',
      generated: new Date().toISOString(),
      source: 'BidDeed.AI / ZoneWise 128-KPI Engine',
      parcel_id: p.parcel_id,
      county: FL_COUNTY_MAP[p.co_no] || `County ${p.co_no}`,
    },

    // ── SECTION 1: PROPERTY IDENTIFICATION (12 KPIs) ──────────────────────
    property_identification: {
      KPI_001: { name: 'Parcel ID', value: p.parcel_id, source: 'FDOR' },
      KPI_002: { name: 'County', value: FL_COUNTY_MAP[p.co_no] || `County ${p.co_no}`, source: 'FDOR' },
      KPI_003: { name: 'Full Address', value: `${p.phy_addr1}, ${p.phy_city}, FL ${p.phy_zipcd}`, source: 'FDOR' },
      KPI_004: { name: 'Street Number', value: streetNum, source: 'Parsed' },
      KPI_005: { name: 'Street Name', value: streetName, source: 'Parsed' },
      KPI_006: { name: 'City', value: p.phy_city, source: 'FDOR' },
      KPI_007: { name: 'State', value: 'FL', source: 'FDOR' },
      KPI_008: { name: 'ZIP Code', value: p.phy_zipcd, source: 'FDOR' },
      KPI_009: { name: 'Owner Name', value: p.own_name, source: 'FDOR' },
      KPI_010: { name: 'Owner Address', value: `${p.own_addr1 || ''}, ${p.own_city || ''}, ${p.own_state || ''} ${p.own_zipcd || ''}`.trim(), source: 'FDOR' },
      KPI_011: { name: 'Property Type', value: DOR_USE_CODES[p.dor_uc] || `Code ${p.dor_uc}`, source: 'FDOR DOR_UC' },
      KPI_012: { name: 'PA Use Code', value: p.pa_uc, source: 'FDOR PA_UC' },
    },

    // ── SECTION 2: PHYSICAL CHARACTERISTICS (13 KPIs) ─────────────────────
    physical_characteristics: {
      KPI_013: { name: 'Total Living Area', value: p.tot_lvg_ar, unit: 'sq ft', source: 'FDOR' },
      KPI_014: { name: 'Lot Size', value: p.lnd_sqfoot, unit: 'sq ft', source: 'FDOR' },
      KPI_015: { name: 'Lot Size (Acres)', value: p.lnd_sqfoot ? (p.lnd_sqfoot / 43560).toFixed(2) : 'N/A', unit: 'acres', source: 'Calculated' },
      KPI_016: { name: 'Year Built (Actual)', value: p.act_yr_blt || 'N/A', source: 'FDOR' },
      KPI_017: { name: 'Year Built (Effective)', value: p.eff_yr_blt || 'N/A', source: 'FDOR' },
      KPI_018: { name: 'Building Age', value: p.eff_yr_blt > 0 ? (2026 - p.eff_yr_blt) : 'N/A', unit: 'years', source: 'Calculated' },
      KPI_019: { name: 'Number of Buildings', value: p.no_buldng, source: 'FDOR' },
      KPI_020: { name: 'Residential Units', value: p.no_res_unt, source: 'FDOR' },
      KPI_021: { name: 'Construction Class', value: CONSTRUCTION_CLASS[p.const_clas] || 'N/A', source: 'FDOR' },
      KPI_022: { name: 'Improvement Quality', value: IMP_QUALITY[p.imp_qual] || 'N/A', source: 'FDOR' },
      KPI_023: { name: 'Special Features Value', value: p.spec_feat_ || 0, unit: '$', source: 'FDOR' },
      KPI_024: { name: 'Land Units', value: p.no_lnd_unt, source: 'FDOR' },
      KPI_025: { name: 'Aerial Photo', value: p.photo_url ? 'Available' : 'N/A', url: p.photo_url, source: 'Esri' },
    },

    // ── SECTION 3: FINANCIAL / VALUATION (20 KPIs) ────────────────────────
    financial_valuation: {
      KPI_026: { name: 'Just (Market) Value', value: p.jv, unit: '$', source: 'FDOR' },
      KPI_027: { name: 'Land Value', value: p.lnd_val, unit: '$', source: 'FDOR' },
      KPI_028: { name: 'Building Value', value: buildingValue, unit: '$', source: 'Calculated' },
      KPI_029: { name: 'Assessed Value (Homestead)', value: p.av_hmstd, unit: '$', source: 'FDOR' },
      KPI_030: { name: 'Assessed Value (Non-Hmstd)', value: p.av_non_hms, unit: '$', source: 'FDOR' },
      KPI_031: { name: 'Assessed Value (School)', value: p.av_sd, unit: '$', source: 'FDOR' },
      KPI_032: { name: 'Assessed Value (Non-School)', value: p.av_nsd, unit: '$', source: 'FDOR' },
      KPI_033: { name: 'Taxable Value (School)', value: p.tv_sd, unit: '$', source: 'FDOR' },
      KPI_034: { name: 'Taxable Value (Non-School)', value: p.tv_nsd, unit: '$', source: 'FDOR' },
      KPI_035: { name: 'Price Per Sq Ft', value: Math.round(pricePerSqft), unit: '$/sqft', source: 'Calculated' },
      KPI_036: { name: 'Land Price Per Sq Ft', value: Math.round(landPricePerSqft * 100) / 100, unit: '$/sqft', source: 'Calculated' },
      KPI_037: { name: 'Improvement Ratio', value: (improvementRatio * 100).toFixed(1), unit: '%', source: 'Calculated' },
      KPI_038: { name: 'Homestead Exemption', value: p.av_hmstd > 0 ? 'Yes' : 'No', source: 'FDOR' },
      KPI_039: { name: 'Special Features Value', value: p.spec_feat_ || 0, unit: '$', source: 'FDOR' },
      KPI_040: { name: 'Last Sale Price', value: p.sale_prc1 || 0, unit: '$', source: 'FDOR' },
      KPI_041: { name: 'Last Sale Year', value: p.sale_yr1 || 'N/A', source: 'FDOR' },
      KPI_042: { name: 'Last Sale Month', value: p.sale_mo1 || 'N/A', source: 'FDOR' },
      KPI_043: { name: 'Appreciation Since Sale', value: appreciationSinceSale !== null ? `${appreciationSinceSale.toFixed(1)}%` : 'N/A', source: 'Calculated' },
      KPI_044: { name: 'Annual Tax Estimate', value: annualTax, unit: '$', source: 'Calculated' },
      KPI_045: { name: 'Insurance Estimate', value: insuranceEst, unit: '$/yr', source: 'Calculated' },
    },

    // ── SECTION 4: MARKET ANALYSIS (18 KPIs) ──────────────────────────────
    market_analysis: {
      KPI_046: { name: 'Area Median Value', value: areaMedianValue, unit: '$', source: 'fl_parcels aggregate' },
      KPI_047: { name: 'Area Avg $/SqFt', value: areaAvgPPSqft, unit: '$/sqft', source: 'fl_parcels aggregate' },
      KPI_048: { name: 'Value vs Area Median', value: `${valueVsMedian}%`, source: 'Calculated' },
      KPI_049: { name: 'Properties in ZIP', value: areaStats.length, source: 'fl_parcels count' },
      KPI_050: { name: 'Recent Sales (2023+)', value: recentSales.length, source: 'fl_parcels filter' },
      KPI_051: { name: 'Median Recent Sale Price', value: recentSales.length > 0 ? recentSales.map(r=>r.sale_prc1).sort((a,b)=>a-b)[Math.floor(recentSales.length/2)] : 'N/A', unit: '$', source: 'Calculated' },
      KPI_052: { name: 'Area Residential Count', value: areaStats.length, source: 'fl_parcels' },
      KPI_053: { name: 'ZIP Code', value: p.phy_zipcd, source: 'FDOR' },
      KPI_054: { name: 'Neighborhood', value: p.phy_city, source: 'FDOR' },
      KPI_055: { name: 'County', value: FL_COUNTY_MAP[p.co_no], source: 'FDOR' },
      KPI_056: { name: 'Latitude', value: p.centroid_lat, source: 'FDOR Cadastral' },
      KPI_057: { name: 'Longitude', value: p.centroid_lng, source: 'FDOR Cadastral' },
      KPI_058: { name: 'Price Percentile (ZIP)', value: areaValues.length > 0 ? Math.round(areaValues.filter(v => v < p.jv).length / areaValues.length * 100) : 'N/A', unit: '%ile', source: 'Calculated' },
      KPI_059: { name: 'Value Tier', value: p.jv >= 500000 ? 'Premium' : p.jv >= 250000 ? 'Mid-Range' : p.jv >= 100000 ? 'Entry-Level' : 'Value', source: 'Calculated' },
      KPI_060: { name: 'Building-to-Land Ratio', value: p.lnd_val > 0 ? (buildingValue / p.lnd_val).toFixed(2) : 'N/A', source: 'Calculated' },
      KPI_061: { name: 'Effective Age Score', value: p.eff_yr_blt > 0 ? Math.max(0, 100 - (2026 - p.eff_yr_blt) * 2) : 'N/A', unit: '/100', source: 'Calculated' },
      KPI_062: { name: 'Property Size Class', value: (p.tot_lvg_ar||0) >= 3000 ? 'Large' : (p.tot_lvg_ar||0) >= 1500 ? 'Medium' : (p.tot_lvg_ar||0) >= 800 ? 'Small' : 'Micro', source: 'Calculated' },
      KPI_063: { name: 'Lot Size Class', value: (p.lnd_sqfoot||0) >= 43560 ? 'Acreage (1+ ac)' : (p.lnd_sqfoot||0) >= 10000 ? 'Large Lot' : (p.lnd_sqfoot||0) >= 5000 ? 'Standard' : 'Small', source: 'Calculated' },
    },

    // ── SECTION 5: ZONING & REGULATORY (20 KPIs) ─────────────────────────
    zoning_regulatory: {
      KPI_064: { name: 'Zone Code', value: zoning?.zone_code || p.zone_code || 'N/A', source: 'parcel_zones' },
      KPI_065: { name: 'Zone Name', value: z.name || 'N/A', source: 'zoning_districts' },
      KPI_066: { name: 'Zone Category', value: z.category || 'N/A', source: 'zoning_districts' },
      KPI_067: { name: 'Max Height', value: d.max_height_ft || s.max_height_ft || 'N/A', unit: 'ft', source: 'DIMS/Standards' },
      KPI_068: { name: 'Max Stories', value: d.max_stories || s.max_stories || 'N/A', source: 'DIMS/Standards' },
      KPI_069: { name: 'Max Lot Coverage', value: maxCoverage ? `${maxCoverage}%` : 'N/A', source: 'DIMS/Standards' },
      KPI_070: { name: 'Front Setback', value: d.setbacks_ft?.front || s.front_setback_ft || 'N/A', unit: 'ft', source: 'DIMS/Standards' },
      KPI_071: { name: 'Side Setback', value: d.setbacks_ft?.side || s.side_setback_ft || 'N/A', unit: 'ft', source: 'DIMS/Standards' },
      KPI_072: { name: 'Rear Setback', value: d.setbacks_ft?.rear || s.rear_setback_ft || 'N/A', unit: 'ft', source: 'DIMS/Standards' },
      KPI_073: { name: 'Corner Setback', value: d.setbacks_ft?.corner || s.corner_setback_ft || 'N/A', unit: 'ft', source: 'DIMS/Standards' },
      KPI_074: { name: 'Floor Area Ratio (FAR)', value: maxFar || 'N/A', source: 'DIMS/Standards' },
      KPI_075: { name: 'Max Density (DU/acre)', value: d.density_max_du_acre || s.max_density_du_acre || 'N/A', source: 'DIMS/Standards' },
      KPI_076: { name: 'Min Lot Size', value: d.min_lot_sqft || s.min_lot_sqft || 'N/A', unit: 'sq ft', source: 'DIMS/Standards' },
      KPI_077: { name: 'Min Lot Width', value: d.min_lot_width_ft || s.min_lot_width_ft || 'N/A', unit: 'ft', source: 'DIMS/Standards' },
      KPI_078: { name: 'Parking Required', value: d.parking_min || d.parking_min_per_1000sf || s.parking_per_unit || 'N/A', source: 'DIMS/Standards' },
      KPI_079: { name: 'Max Building Area', value: maxBuildingArea, unit: 'sq ft', source: 'Calculated' },
      KPI_080: { name: 'Unused Dev Rights', value: unusedRights, unit: 'sq ft', source: 'Calculated' },
      KPI_081: { name: 'FAR Utilization', value: farUtilization ? `${farUtilization}%` : 'N/A', source: 'Calculated' },
      KPI_082: { name: 'Expansion Potential', value: unusedRights && p.tot_lvg_ar > 0 ? `${Math.round(unusedRights/p.tot_lvg_ar*100)}%` : 'N/A', source: 'Calculated' },
      KPI_083: { name: 'Jurisdiction', value: zoning?.zoning_districts?.jurisdictions?.name || p.phy_city || 'N/A', source: 'parcel_zones' },
    },

    // ── SECTION 6: PERMITTED USES (8 KPIs) ────────────────────────────────
    permitted_uses: {
      KPI_084: { name: 'Permitted Uses Count', value: permittedList.length, source: 'permitted_uses' },
      KPI_085: { name: 'Top Permitted Uses', value: permittedList.slice(0, 5).join('; ') || 'N/A', source: 'permitted_uses' },
      KPI_086: { name: 'Conditional Uses Count', value: conditionalList.length, source: 'permitted_uses' },
      KPI_087: { name: 'Short-Term Rental', value: isSTRAllowed ? 'Allowed' : 'Not Listed', source: 'permitted_uses' },
      KPI_088: { name: 'ADU Allowed', value: isADUAllowed ? 'Yes' : 'Not Listed', source: 'permitted_uses' },
      KPI_089: { name: 'Mixed Use Allowed', value: isMixedUse ? 'Yes' : 'Not Listed', source: 'permitted_uses' },
      KPI_090: { name: 'Live Local Act Eligible', value: 'Check Required', source: 'State Law' },
      KPI_091: { name: 'Ordinance Source', value: d.source_url || s.source_url || 'N/A', source: 'DIMS/Standards' },
    },

    // ── SECTION 7: INVESTMENT METRICS (12 KPIs) ──────────────────────────
    investment_metrics: {
      KPI_092: { name: 'Monthly Rent Estimate', value: monthlyRentEst, unit: '$', source: 'Calculated' },
      KPI_093: { name: 'Annual Rent Estimate', value: annualRentEst, unit: '$', source: 'Calculated' },
      KPI_094: { name: 'Gross Rent Multiplier', value: grossRentMult, source: 'Calculated' },
      KPI_095: { name: 'Cap Rate Estimate', value: `${capRate.toFixed(1)}%`, source: 'Calculated' },
      KPI_096: { name: 'Price-to-Rent Ratio', value: priceToRent, source: 'Calculated' },
      KPI_097: { name: 'NOI Estimate', value: annualRentEst - annualTax - insuranceEst, unit: '$/yr', source: 'Calculated' },
      KPI_098: { name: 'Cash-on-Cash (25% down)', value: p.jv > 0 ? `${((annualRentEst - annualTax - insuranceEst - p.jv*0.75*0.065) / (p.jv*0.25) * 100).toFixed(1)}%` : 'N/A', source: 'Calculated' },
      KPI_099: { name: 'Annual Tax', value: annualTax, unit: '$', source: 'Calculated' },
      KPI_100: { name: 'Annual Insurance', value: insuranceEst, unit: '$', source: 'Calculated' },
      KPI_101: { name: 'Annual Expenses', value: annualTax + insuranceEst, unit: '$', source: 'Calculated' },
      KPI_102: { name: 'Expense Ratio', value: annualRentEst > 0 ? `${((annualTax + insuranceEst) / annualRentEst * 100).toFixed(1)}%` : 'N/A', source: 'Calculated' },
      KPI_103: { name: 'Break-Even Rent', value: Math.round((annualTax + insuranceEst + (p.jv * 0.75 * 0.065)) / 12), unit: '$/mo', source: 'Calculated' },
    },

    // ── SECTION 8: RISK ASSESSMENT (13 KPIs) ──────────────────────────────
    risk_assessment: {
      KPI_104: { name: 'Risk Score', value: riskScore, unit: '/100', source: 'Calculated' },
      KPI_105: { name: 'Risk Level', value: riskScore >= 70 ? 'HIGH' : riskScore >= 50 ? 'MODERATE' : 'LOW', source: 'Calculated' },
      KPI_106: { name: 'Building Age Risk', value: p.eff_yr_blt > 0 && p.eff_yr_blt < 1970 ? 'Pre-1970 (check lead/asbestos)' : p.eff_yr_blt < 1990 ? 'Aging (30+ years)' : 'Acceptable', source: 'Calculated' },
      KPI_107: { name: 'Construction Quality Risk', value: (p.const_clas||0) >= 5 ? 'Below Average' : 'Acceptable', source: 'FDOR' },
      KPI_108: { name: 'Improvement Quality Risk', value: (p.imp_qual||0) >= 5 ? 'Below Average/Poor' : 'Acceptable', source: 'FDOR' },
      KPI_109: { name: 'Over-Valued vs Area', value: p.jv > areaMedianValue * 1.5 ? 'Significantly Above Median' : 'Within Range', source: 'Calculated' },
      KPI_110: { name: 'Land > Building', value: buildingValue < p.lnd_val * 0.3 ? 'Yes (teardown candidate)' : 'No', source: 'Calculated' },
      KPI_111: { name: 'Homestead Protected', value: p.av_hmstd > 0 ? 'Yes (owner-occupied)' : 'No', source: 'FDOR' },
      KPI_112: { name: 'FEMA Flood Zone', value: fema ? fema.zone : 'Not queried', source: 'FEMA NFHL' },
      KPI_113: { name: 'Flood Zone Description', value: fema?.subtype || 'N/A', source: 'FEMA NFHL' },
      KPI_114: { name: 'Special Flood Hazard Area', value: fema ? (fema.sfha ? 'YES (SFHA)' : 'No') : 'N/A', source: 'FEMA NFHL' },
      KPI_115: { name: 'Base Flood Elevation', value: fema?.bfe ? `${fema.bfe} ft` : 'N/A', source: 'FEMA NFHL' },
      KPI_116: { name: 'Flood Insurance Required', value: fema?.insuranceReq || 'Check with insurer', source: 'FEMA NFHL' },
    },

    // ── SECTION 9: BIDDEED.AI SCORING (12 KPIs) ──────────────────────────
    biddeed_scoring: {
      KPI_117: { name: 'Opportunity Score', value: oppScore, unit: '/100', source: 'BidDeed.AI' },
      KPI_118: { name: 'Investment Grade', value: investGrade, source: 'BidDeed.AI' },
      KPI_119: { name: 'Recommendation', value: oppScore >= 70 ? 'REVIEW' : oppScore >= 50 ? 'MONITOR' : 'PASS', source: 'BidDeed.AI' },
      KPI_120: { name: 'Estimated ARV', value: Math.round(areaMedianValue * 1.05) || p.jv, unit: '$', source: 'BidDeed.AI' },
      KPI_121: { name: 'Max Bid (Shapira Formula)', value: Math.round(((areaMedianValue||p.jv) * 0.7) - 10000 - Math.min(25000, (areaMedianValue||p.jv)*0.15)), unit: '$', source: 'Shapira Formula' },
      KPI_122: { name: 'Estimated Repair Cost', value: p.eff_yr_blt > 0 && p.eff_yr_blt < 1990 ? Math.round(p.tot_lvg_ar * 25) : Math.round(p.tot_lvg_ar * 10), unit: '$', source: 'BidDeed.AI' },
      KPI_123: { name: 'Estimated Profit', value: null, unit: '$', note: 'Requires auction data', source: 'BidDeed.AI' },
      KPI_124: { name: 'Estimated ROI', value: null, note: 'Requires auction data', source: 'BidDeed.AI' },
      KPI_125: { name: 'Exit Strategy', value: monthlyRentEst > 2000 ? 'Rent (strong cashflow)' : 'Fix & Flip', source: 'BidDeed.AI' },
      KPI_126: { name: 'Time to Exit', value: monthlyRentEst > 2000 ? 'Hold (rental)' : '90-120 days', source: 'BidDeed.AI' },
      KPI_127: { name: 'Deal Quality Flags', value: [
        pricePerSqft < areaAvgPPSqft * 0.85 ? 'Below-market $/sqft' : null,
        unusedRights > (p.tot_lvg_ar||1) ? 'High expansion potential' : null,
        p.eff_yr_blt >= 2000 ? 'Modern construction' : null,
        p.av_hmstd === 0 ? 'Non-homestead (investor-friendly)' : null,
      ].filter(Boolean).join('; ') || 'None', source: 'BidDeed.AI' },
      KPI_128: { name: 'Data Confidence', value: [p.jv > 0, p.tot_lvg_ar > 0, p.eff_yr_blt > 0, p.centroid_lat, zoning?.zone_code].filter(Boolean).length >= 4 ? 'HIGH' : 'MODERATE', source: 'BidDeed.AI' },
    },
  };
}

// =============================================================================
// DOCX REPORT GENERATOR
// =============================================================================
const border = { style: BorderStyle.SINGLE, size: 1, color: COLORS.BORDER };
const borders = { top: border, bottom: border, left: border, right: border };
const cellMargins = { top: 60, bottom: 60, left: 100, right: 100 };
const TABLE_WIDTH = 9360; // US Letter - 1" margins
const COL_KPI = 600;
const COL_NAME = 3200;
const COL_VALUE = 3560;
const COL_SOURCE = 2000;

function headerCell(text) {
  return new TableCell({
    borders, margins: cellMargins,
    shading: { fill: COLORS.NAVY, type: ShadingType.CLEAR },
    children: [new Paragraph({ children: [new TextRun({ text, bold: true, color: 'FFFFFF', font: 'Arial', size: 18 })] })]
  });
}

function dataRow(kpiNum, kpi, rowIdx) {
  const val = kpi.value !== null && kpi.value !== undefined ? 
    (kpi.unit === '$' ? `$${Number(kpi.value).toLocaleString()}` : 
     kpi.unit ? `${kpi.value} ${kpi.unit}` : String(kpi.value)) : 'N/A';
  const bg = rowIdx % 2 === 0 ? COLORS.WHITE : COLORS.ALT_ROW;
  
  const makeCell = (text, width) => new TableCell({
    borders, margins: cellMargins, width: { size: width, type: WidthType.DXA },
    shading: { fill: bg, type: ShadingType.CLEAR },
    children: [new Paragraph({ children: [new TextRun({ text: String(text), font: 'Arial', size: 18, color: COLORS.DARK_TEXT })] })]
  });

  return new TableRow({ children: [
    makeCell(kpiNum, COL_KPI), makeCell(kpi.name, COL_NAME),
    makeCell(val, COL_VALUE), makeCell(kpi.source, COL_SOURCE)
  ]});
}

function sectionHeader(title, color) {
  return new Paragraph({
    spacing: { before: 300, after: 100 },
    shading: { fill: color, type: ShadingType.CLEAR },
    children: [new TextRun({ text: `  ${title}`, bold: true, font: 'Arial', size: 24, color: COLORS.NAVY })]
  });
}

function buildKPITable(section) {
  const entries = Object.entries(section);
  const rows = [
    new TableRow({ children: [
      headerCell('#'), headerCell('KPI Name'), headerCell('Value'), headerCell('Source')
    ]}),
    ...entries.map(([key, kpi], i) => dataRow(key.replace('KPI_', ''), kpi, i))
  ];
  return new Table({
    width: { size: TABLE_WIDTH, type: WidthType.DXA },
    columnWidths: [COL_KPI, COL_NAME, COL_VALUE, COL_SOURCE],
    rows
  });
}

async function generateDOCX(kpis, outputPath) {
  const addr = kpis.property_identification.KPI_003.value;
  const sections = [
    { title: 'PROPERTY IDENTIFICATION (12 KPIs)', data: kpis.property_identification, color: COLORS.BLUE_BG },
    { title: 'PHYSICAL CHARACTERISTICS (13 KPIs)', data: kpis.physical_characteristics, color: COLORS.GREEN_BG },
    { title: 'FINANCIAL / VALUATION (20 KPIs)', data: kpis.financial_valuation, color: COLORS.BLUE_BG },
    { title: 'MARKET ANALYSIS (18 KPIs)', data: kpis.market_analysis, color: COLORS.GREEN_BG },
    { title: 'ZONING & REGULATORY (20 KPIs)', data: kpis.zoning_regulatory, color: COLORS.ORANGE_BG },
    { title: 'PERMITTED USES (8 KPIs)', data: kpis.permitted_uses, color: COLORS.PURPLE_BG },
    { title: 'INVESTMENT METRICS (12 KPIs)', data: kpis.investment_metrics, color: COLORS.BLUE_BG },
    { title: 'RISK ASSESSMENT (13 KPIs)', data: kpis.risk_assessment, color: COLORS.RED_BG },
    { title: 'BIDDEED.AI SCORING (12 KPIs)', data: kpis.biddeed_scoring, color: COLORS.GREEN_BG },
  ];

  const children = [
    // Title
    new Paragraph({
      spacing: { after: 100 },
      children: [new TextRun({ text: 'BidDeed.AI / ZoneWise', font: 'Arial', size: 36, bold: true, color: COLORS.NAVY })]
    }),
    new Paragraph({
      spacing: { after: 50 },
      children: [new TextRun({ text: '128-KPI PROPERTY INTELLIGENCE REPORT', font: 'Arial', size: 28, bold: true, color: COLORS.NAVY })]
    }),
    new Paragraph({
      border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: COLORS.NAVY, space: 1 } },
      spacing: { after: 200 },
      children: [new TextRun({ text: addr, font: 'Arial', size: 22, color: '666666' })]
    }),
    // Summary bar
    new Paragraph({
      spacing: { after: 50 },
      children: [
        new TextRun({ text: `Grade: ${kpis.biddeed_scoring.KPI_118.value}  |  `, font: 'Arial', size: 20, bold: true }),
        new TextRun({ text: `Risk: ${kpis.risk_assessment.KPI_105.value}  |  `, font: 'Arial', size: 20 }),
        new TextRun({ text: `Value: $${Number(kpis.financial_valuation.KPI_026.value).toLocaleString()}  |  `, font: 'Arial', size: 20 }),
        new TextRun({ text: `Cap Rate: ${kpis.investment_metrics.KPI_095.value}  |  `, font: 'Arial', size: 20 }),
        new TextRun({ text: `Zone: ${kpis.zoning_regulatory.KPI_064.value}`, font: 'Arial', size: 20 }),
      ]
    }),
    new Paragraph({
      spacing: { after: 200 },
      children: [
        new TextRun({ text: `Generated: ${new Date().toLocaleDateString()} | 128 KPIs | Beats PropertyOnion (96) + PropZone (74)`, font: 'Arial', size: 16, color: '999999', italics: true }),
      ]
    }),
  ];

  // Add all sections
  for (const sec of sections) {
    children.push(sectionHeader(sec.title, sec.color));
    children.push(buildKPITable(sec.data));
  }

  // Footer disclaimer
  children.push(new Paragraph({ spacing: { before: 400 }, children: [
    new TextRun({ text: 'DISCLAIMER: This report is generated from public records (FL Department of Revenue, County Property Appraiser, Municipal Zoning). Estimates for rental income, insurance, and taxes are approximations. Verify all data before making investment decisions. Not financial or legal advice.', font: 'Arial', size: 14, color: '999999', italics: true })
  ]}));

  const doc = new Document({
    styles: {
      default: { document: { run: { font: 'Arial', size: 20 } } },
    },
    sections: [{
      properties: {
        page: {
          size: { width: 12240, height: 15840 },
          margin: { top: 720, right: 720, bottom: 720, left: 720 }
        }
      },
      headers: {
        default: new Header({
          children: [new Paragraph({
            alignment: AlignmentType.RIGHT,
            children: [new TextRun({ text: 'BidDeed.AI | 128-KPI Report', font: 'Arial', size: 14, color: '999999' })]
          })]
        })
      },
      footers: {
        default: new Footer({
          children: [new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [
              new TextRun({ text: 'Page ', font: 'Arial', size: 14, color: '999999' }),
              new TextRun({ children: [PageNumber.CURRENT], font: 'Arial', size: 14, color: '999999' }),
              new TextRun({ text: ' | Proprietary - Everest Capital USA', font: 'Arial', size: 14, color: '999999' }),
            ]
          })]
        })
      },
      children
    }]
  });

  const buffer = await Packer.toBuffer(doc);
  fs.writeFileSync(outputPath, buffer);
  return outputPath;
}

// =============================================================================
// MAIN
// =============================================================================
async function main() {
  const args = process.argv.slice(2);
  let parcelId = null, address = null, city = null, zipCode = null;
  
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--parcel' && args[i+1]) { parcelId = args[++i]; }
    else if (args[i] === '--address' && args[i+1]) { address = args[++i]; }
    else if (args[i] === '--city' && args[i+1]) { city = args[++i]; }
    else if (args[i] === '--zip' && args[i+1]) { zipCode = args[++i]; }
  }

  if (!parcelId && !address) {
    // Default: demo with a Satellite Beach property
    parcelId = '27 3702-88-A-3';
  }

  console.log('='  .repeat(60));
  console.log('  BIDDEED.AI 128-KPI REPORT GENERATOR');
  console.log('=' .repeat(60));
  
  // 1. Fetch parcel
  console.log('\n[1/5] Fetching parcel data...');
  const parcel = parcelId ? fetchParcel(parcelId) : fetchParcelByAddress(address, city);
  if (!parcel) { console.error('ERROR: Parcel not found'); process.exit(1); }
  console.log(`  Found: ${parcel.phy_addr1}, ${parcel.phy_city} (JV: $${(parcel.jv||0).toLocaleString()})`);

  // 2. Fetch zoning
  console.log('[2/5] Fetching zoning data...');
  let zoning = fetchZoning(parcel.parcel_id);
  if (!zoning) {
    console.log('  No direct zone match, inferring from DOR use code + city...');
    zoning = inferZoning(parcel);
  }
  const dims = zoning?.zoning_districts ? parseDimsJson(zoning.zoning_districts.description) : null;
  console.log(`  Zone: ${zoning?.zone_code || 'N/A'}${zoning?._inferred ? ' (inferred)' : ''} | DIMS: ${dims ? 'YES' : 'NO'}${zoning?._jurisdiction ? ` | Jurisdiction: ${zoning._jurisdiction}` : ''}`);

  // 3. Fetch standards & uses
  console.log('[3/5] Fetching zone standards & permitted uses...');
  const districtId = zoning?.zoning_districts?.id;
  const standards = districtId ? fetchZoneStandards(districtId) : null;
  const uses = districtId ? fetchPermittedUses(districtId) : [];
  console.log(`  Standards: ${standards ? 'YES' : 'NO'} | Uses: ${uses.length}`);

  // 4. Fetch area stats
  console.log('[4/6] Fetching area market stats...');
  const areaStats = fetchAreaStats(parcel.co_no, parcel.phy_zipcd);
  console.log(`  Area comparables: ${areaStats.length} properties in ZIP ${parcel.phy_zipcd}`);

  // 5. Fetch FEMA flood zone data
  console.log('[5/6] Querying FEMA NFHL flood zone...');
  let fema = null;
  if (parcel.centroid_lat && parcel.centroid_lng) {
    fema = fetchFemaFloodZone(parcel.centroid_lat, parcel.centroid_lng);
    if (fema) {
      console.log(`  Zone: ${fema.zone} | ${fema.subtype}`);
      console.log(`  SFHA: ${fema.sfha ? 'YES' : 'No'} | Risk: ${fema.riskTier} | BFE: ${fema.bfe || 'N/A'} ft`);
      console.log(`  FIRM Panel: ${fema.firmPanel || 'N/A'} | Effective: ${fema.firmEffDate || 'N/A'}`);
      console.log(`  Insurance: ${fema.insuranceReq}`);
    } else {
      console.log('  FEMA data not available for this location');
    }
  } else {
    console.log('  No coordinates available — skipping FEMA lookup');
  }

  // 6. Compute 128 KPIs
  console.log('[6/6] Computing 128 KPIs...');
  const kpis = compute128KPIs(parcel, zoning, standards, dims, uses, areaStats, fema);

  // Count populated KPIs
  let populated = 0, total = 0;
  for (const section of Object.values(kpis)) {
    if (typeof section !== 'object' || section === null) continue;
    for (const [key, kpi] of Object.entries(section)) {
      if (!key.startsWith('KPI_')) continue;
      total++;
      if (kpi.value !== null && kpi.value !== undefined && kpi.value !== 'N/A' && kpi.value !== '') populated++;
    }
  }
  console.log(`\n  KPIs: ${populated}/${total} populated (${Math.round(populated/total*100)}%)\n`);

  // Generate DOCX
  const safeName = (parcel.phy_addr1 || 'property').replace(/[^a-zA-Z0-9]/g, '_').substring(0, 40);
  const outputPath = `/home/claude/${safeName}_128KPI.docx`;
  await generateDOCX(kpis, outputPath);
  console.log(`  DOCX: ${outputPath}`);

  // Also save JSON
  const jsonPath = `/home/claude/${safeName}_128KPI.json`;
  fs.writeFileSync(jsonPath, JSON.stringify(kpis, null, 2));
  console.log(`  JSON: ${jsonPath}`);

  console.log('\n' + '='.repeat(60));
  console.log('  DONE - 128 KPIs COMPUTED & REPORT GENERATED');
  console.log('='.repeat(60));
}

main().catch(e => { console.error('FATAL:', e); process.exit(1); });
