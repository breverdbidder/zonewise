# ZoneWise Supabase Integration - Complete Schema & Prompt Engineering
## Including zonewize Skill Integration

**Created:** January 13, 2026  
**Version:** 2.0.0 (with zonewize skill)  
**Ecosystem:** ZoneWise Agentic AI Platform  

---

## CRITICAL ARCHITECTURE NOTE

**ZoneWise uses a SEPARATE Supabase instance from BidDeed.AI:**

```
BidDeed.AI:  mocerqjnksmhcjzxrewo.supabase.co
ZoneWise:    [NEW INSTANCE - zonewise.supabase.co]
```

**Why Separate?**
- Different data models (zoning vs foreclosures)
- Different access patterns (on-demand vs batch)
- Different scaling requirements
- Cleaner separation of concerns

---

## Complete Database Schema

### **1. Core Tables**

#### **properties**
```sql
-- Property master data
CREATE TABLE properties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    parcel_id TEXT UNIQUE NOT NULL,
    address TEXT NOT NULL,
    jurisdiction TEXT NOT NULL REFERENCES jurisdictions(id),
    property_type TEXT NOT NULL, -- residential, commercial, industrial, mixed_use
    zoning_district TEXT NOT NULL,
    lot_size_sqft INTEGER,
    building_sqft INTEGER,
    year_built INTEGER,
    front_setback NUMERIC(10,2),
    side_setback NUMERIC(10,2),
    rear_setback NUMERIC(10,2),
    building_height NUMERIC(10,2),
    current_use TEXT,
    owner_name TEXT,
    owner_address TEXT,
    latitude NUMERIC(10,6),
    longitude NUMERIC(10,6),
    geometry GEOMETRY(POINT, 4326), -- PostGIS for spatial queries
    bcpao_account TEXT, -- Brevard County Property Appraiser account
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_properties_jurisdiction ON properties(jurisdiction);
CREATE INDEX idx_properties_zoning_district ON properties(zoning_district);
CREATE INDEX idx_properties_parcel_id ON properties(parcel_id);
CREATE INDEX idx_properties_geometry ON properties USING GIST(geometry);
CREATE INDEX idx_properties_address_fts ON properties USING GIN(to_tsvector('english', address));
```

#### **jurisdictions**
```sql
-- 17 Brevard County jurisdictions
CREATE TABLE jurisdictions (
    id TEXT PRIMARY KEY, -- e.g., "indian_harbour_beach"
    full_name TEXT NOT NULL UNIQUE,
    abbreviation TEXT NOT NULL,
    ordinance_url TEXT NOT NULL,
    zoning_map_url TEXT,
    contact_email TEXT,
    contact_phone TEXT,
    office_hours TEXT,
    parser_version TEXT NOT NULL DEFAULT 'municode_v2',
    population INTEGER,
    area_sqmi NUMERIC(10,2),
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert 17 Brevard jurisdictions
INSERT INTO jurisdictions (id, full_name, abbreviation, ordinance_url, contact_email, contact_phone) VALUES
('indian_harbour_beach', 'Indian Harbour Beach', 'IHB', 'https://library.municode.com/fl/indian_harbour_beach', 'planning@ihb-fl.gov', '(321) 773-2200'),
('melbourne', 'City of Melbourne', 'MEL', 'https://library.municode.com/fl/melbourne', 'planning@melbourneflorida.org', '(321) 608-7500'),
('palm_bay', 'City of Palm Bay', 'PB', 'https://library.municode.com/fl/palm_bay', 'planning@palmbayflorida.org', '(321) 952-3410'),
('cocoa', 'City of Cocoa', 'COC', 'https://library.municode.com/fl/cocoa', 'planning@cocoafl.org', '(321) 433-8600'),
('cocoa_beach', 'City of Cocoa Beach', 'CB', 'https://library.municode.com/fl/cocoa_beach', 'planning@cityofcocoabeach.com', '(321) 868-3258'),
('rockledge', 'City of Rockledge', 'ROC', 'https://library.municode.com/fl/rockledge', 'planning@cityofrockledge.org', '(321) 690-3978'),
('titusville', 'City of Titusville', 'TIT', 'https://library.municode.com/fl/titusville', 'planning@titusville.com', '(321) 567-3774'),
('satellite_beach', 'City of Satellite Beach', 'SAT', 'https://library.municode.com/fl/satellite_beach', 'planning@satellitebeach.org', '(321) 773-4407'),
('west_melbourne', 'City of West Melbourne', 'WM', 'https://library.municode.com/fl/west_melbourne', 'planning@westmelbourne.org', '(321) 837-7774'),
('cape_canaveral', 'City of Cape Canaveral', 'CC', 'https://library.municode.com/fl/cape_canaveral', 'planning@cityofcapecanaveral.org', '(321) 868-1220'),
('malabar', 'Town of Malabar', 'MAL', 'https://library.municode.com/fl/malabar', 'planning@malabarflorida.org', '(321) 727-7764'),
('grant_valkaria', 'Town of Grant-Valkaria', 'GV', 'https://library.municode.com/fl/grant-valkaria', 'planning@grantfl.us', '(321) 723-8696'),
('indialantic', 'Town of Indialantic', 'IND', 'https://library.municode.com/fl/indialantic', 'planning@indialantic.com', '(321) 723-2242'),
('melbourne_beach', 'Town of Melbourne Beach', 'MB', 'https://library.municode.com/fl/melbourne_beach', 'planning@melbournebeachfl.org', '(321) 724-5860'),
('melbourne_village', 'Town of Melbourne Village', 'MV', 'https://library.municode.com/fl/melbourne_village', 'planning@melbournevillage-fl.gov', '(321) 723-5462'),
('palm_shores', 'Town of Palm Shores', 'PS', 'https://library.municode.com/fl/palm_shores', 'planning@palmshores.com', '(321) 984-4420'),
('brevard_county_unincorporated', 'Brevard County (Unincorporated)', 'BC', 'https://library.municode.com/fl/brevard_county', 'planning@brevardfl.gov', '(321) 633-2069');
```

#### **zoning_districts**
```sql
-- Master list of all zoning districts across all jurisdictions
CREATE TABLE zoning_districts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    jurisdiction_id TEXT NOT NULL REFERENCES jurisdictions(id),
    district_code TEXT NOT NULL, -- e.g., "R-1", "C-2", "I-1"
    district_name TEXT, -- e.g., "Single Family Residential"
    description TEXT,
    allowed_uses JSONB, -- Array of permitted uses
    dimensional_requirements JSONB, -- {min_lot_size, setbacks, height_limit, etc.}
    special_conditions JSONB, -- Overlay districts, special regulations
    ordinance_section TEXT, -- Reference to ordinance section
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(jurisdiction_id, district_code)
);

-- Index
CREATE INDEX idx_zoning_districts_jurisdiction ON zoning_districts(jurisdiction_id);
CREATE INDEX idx_zoning_districts_code ON zoning_districts(district_code);
```

---

### **2. zonewize Skill Tables**

#### **ordinance_cache**
```sql
-- Cache for scraped ordinances (7-day TTL)
CREATE TABLE ordinance_cache (
    jurisdiction_id TEXT PRIMARY KEY REFERENCES jurisdictions(id),
    content TEXT NOT NULL, -- Full HTML/text content from Firecrawl
    content_hash TEXT, -- MD5 hash to detect changes
    scraped_at TIMESTAMPTZ NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL, -- scraped_at + 7 days
    firecrawl_cost_usd NUMERIC(10,4),
    correlation_id UUID,
    metadata JSONB, -- {url, status_code, scrape_duration_ms, etc.}
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Automatically set expires_at
CREATE OR REPLACE FUNCTION set_ordinance_expiry()
RETURNS TRIGGER AS $$
BEGIN
    NEW.expires_at := NEW.scraped_at + INTERVAL '7 days';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_ordinance_expiry_trigger
BEFORE INSERT OR UPDATE ON ordinance_cache
FOR EACH ROW
EXECUTE FUNCTION set_ordinance_expiry();

-- Index
CREATE INDEX idx_ordinance_cache_expires ON ordinance_cache(expires_at);
```

#### **compliance_analyses**
```sql
-- Results from zonewize skill analyses
CREATE TABLE compliance_analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID NOT NULL REFERENCES properties(id),
    correlation_id UUID NOT NULL,
    
    -- Analysis results
    compliance_status TEXT NOT NULL, -- COMPLIANT, NON_COMPLIANT, UNKNOWN, MANUAL_REVIEW
    confidence_score INTEGER NOT NULL CHECK (confidence_score >= 0 AND confidence_score <= 100),
    zoning_district TEXT NOT NULL,
    allowed_uses JSONB,
    violations JSONB, -- Array of violation objects
    requires_variance BOOLEAN,
    ordinance_sections JSONB,
    
    -- Data provenance
    data_source TEXT NOT NULL, -- firecrawl_fresh, firecrawl_cache, firecrawl_cache_expired, manual_review
    cache_hit BOOLEAN NOT NULL,
    ordinance_last_updated TIMESTAMPTZ,
    
    -- Performance metrics
    execution_time_ms NUMERIC(10,2),
    cost_usd NUMERIC(10,4),
    
    -- Metadata
    analyzed_by TEXT DEFAULT 'zonewize_v1.0.0',
    analyzed_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Optional: user-provided context
    current_use TEXT,
    proposed_use TEXT,
    notes TEXT
);

-- Indexes
CREATE INDEX idx_compliance_analyses_property ON compliance_analyses(property_id);
CREATE INDEX idx_compliance_analyses_correlation ON compliance_analyses(correlation_id);
CREATE INDEX idx_compliance_analyses_status ON compliance_analyses(compliance_status);
CREATE INDEX idx_compliance_analyses_date ON compliance_analyses(analyzed_at DESC);
```

#### **violations**
```sql
-- Detailed violation records (normalized from compliance_analyses.violations JSONB)
CREATE TABLE violations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id UUID NOT NULL REFERENCES compliance_analyses(id) ON DELETE CASCADE,
    violation_type TEXT NOT NULL, -- use, setback, height, lot_size, parking, etc.
    description TEXT NOT NULL,
    severity TEXT NOT NULL, -- CRITICAL, MAJOR, MINOR
    code_reference TEXT,
    current_value TEXT,
    required_value TEXT,
    estimated_fix_cost NUMERIC(10,2), -- Optional: cost to remedy
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index
CREATE INDEX idx_violations_analysis ON violations(analysis_id);
CREATE INDEX idx_violations_type ON violations(violation_type);
CREATE INDEX idx_violations_severity ON violations(severity);
```

---

### **3. Observability Tables**

#### **zonewise_metrics**
```sql
-- Performance and business metrics for all ZoneWise operations
CREATE TABLE zonewise_metrics (
    id BIGSERIAL PRIMARY KEY,
    metric_name TEXT NOT NULL,
    value NUMERIC NOT NULL,
    labels JSONB, -- {skill, stage, jurisdiction, status, etc.}
    correlation_id UUID,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_zonewise_metrics_name ON zonewise_metrics(metric_name);
CREATE INDEX idx_zonewise_metrics_timestamp ON zonewise_metrics(timestamp DESC);
CREATE INDEX idx_zonewise_metrics_correlation ON zonewise_metrics(correlation_id);
CREATE INDEX idx_zonewise_metrics_labels ON zonewise_metrics USING GIN(labels);

-- Partition by month for performance
CREATE TABLE zonewise_metrics_2026_01 PARTITION OF zonewise_metrics
FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
```

**Key Metrics Tracked:**
```
zonewize_execution_ms           -- Execution time per analysis
zonewize_compliance_rate        -- % of properties compliant
zonewize_cache_hit_rate         -- % of cache hits
zonewize_firecrawl_cost_usd     -- Cost per Firecrawl call
zonewize_confidence_score       -- Average confidence score
zonewize_manual_review_rate     -- % requiring manual review
zonewize_violation_count        -- # violations found
```

#### **zonewise_errors**
```sql
-- Error tracking for debugging and monitoring
CREATE TABLE zonewise_errors (
    id BIGSERIAL PRIMARY KEY,
    error_type TEXT NOT NULL,
    error_message TEXT,
    skill_name TEXT,
    stage TEXT, -- Which stage in pipeline failed
    context JSONB, -- {property_id, jurisdiction, stack_trace, etc.}
    correlation_id UUID,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_zonewise_errors_type ON zonewise_errors(error_type);
CREATE INDEX idx_zonewise_errors_timestamp ON zonewise_errors(timestamp DESC);
CREATE INDEX idx_zonewise_errors_correlation ON zonewise_errors(correlation_id);
CREATE INDEX idx_zonewise_errors_skill ON zonewise_errors(skill_name);
```

**Common Error Types:**
```
firecrawl_timeout              -- Firecrawl API timeout
firecrawl_api_failed           -- Firecrawl returned error
firecrawl_scrape_failed        -- Scraping failed
ordinance_parse_failed         -- Parsing failed
property_fetch_failed          -- Property data fetch failed
zonewize_analysis_failed       -- Analysis failed
zonewize_unexpected_error      -- Unexpected exception
cache_write_failed             -- Cache write failed
```

---

### **4. Reports & History Tables**

#### **reports**
```sql
-- Generated compliance reports (DOCX/PDF)
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id UUID NOT NULL REFERENCES compliance_analyses(id),
    property_id UUID NOT NULL REFERENCES properties(id),
    report_type TEXT NOT NULL, -- compliance_report, variance_analysis, development_potential
    format TEXT NOT NULL, -- docx, pdf
    file_url TEXT NOT NULL, -- Supabase Storage URL
    file_size_bytes INTEGER,
    generated_at TIMESTAMPTZ DEFAULT NOW(),
    generated_by TEXT DEFAULT 'zonewize_v1.0.0',
    expires_at TIMESTAMPTZ, -- Optional: auto-delete old reports
    metadata JSONB
);

-- Index
CREATE INDEX idx_reports_analysis ON reports(analysis_id);
CREATE INDEX idx_reports_property ON reports(property_id);
CREATE INDEX idx_reports_date ON reports(generated_at DESC);
```

#### **variance_requests**
```sql
-- Track variance requests and outcomes (future ML training data)
CREATE TABLE variance_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID NOT NULL REFERENCES properties(id),
    jurisdiction_id TEXT NOT NULL REFERENCES jurisdictions(id),
    request_type TEXT NOT NULL, -- use_variance, dimensional_variance, special_exception
    requested_use TEXT,
    justification TEXT,
    submission_date DATE,
    hearing_date DATE,
    decision TEXT, -- approved, denied, approved_with_conditions, withdrawn
    decision_date DATE,
    conditions TEXT[], -- Array of conditions if approved
    vote_record JSONB, -- {for: 4, against: 1, abstain: 0}
    case_number TEXT,
    documents JSONB, -- URLs to supporting documents
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index
CREATE INDEX idx_variance_requests_property ON variance_requests(property_id);
CREATE INDEX idx_variance_requests_jurisdiction ON variance_requests(jurisdiction_id);
CREATE INDEX idx_variance_requests_decision ON variance_requests(decision);
```

---

## Dashboard Views

### **Compliance Overview**
```sql
CREATE VIEW compliance_overview AS
SELECT 
    j.full_name AS jurisdiction,
    COUNT(*) AS total_analyses,
    COUNT(*) FILTER (WHERE ca.compliance_status = 'COMPLIANT') AS compliant_count,
    COUNT(*) FILTER (WHERE ca.compliance_status = 'NON_COMPLIANT') AS non_compliant_count,
    COUNT(*) FILTER (WHERE ca.compliance_status = 'MANUAL_REVIEW') AS manual_review_count,
    ROUND(AVG(ca.confidence_score), 1) AS avg_confidence,
    ROUND(AVG(ca.execution_time_ms), 0) AS avg_execution_ms,
    ROUND(SUM(ca.cost_usd), 4) AS total_cost_usd
FROM compliance_analyses ca
JOIN properties p ON ca.property_id = p.id
JOIN jurisdictions j ON p.jurisdiction = j.id
WHERE ca.analyzed_at > NOW() - INTERVAL '30 days'
GROUP BY j.full_name
ORDER BY total_analyses DESC;
```

### **Cache Performance**
```sql
CREATE VIEW cache_performance AS
SELECT 
    j.full_name AS jurisdiction,
    COUNT(*) AS total_requests,
    COUNT(*) FILTER (WHERE ca.cache_hit) AS cache_hits,
    ROUND(COUNT(*) FILTER (WHERE ca.cache_hit) * 100.0 / COUNT(*), 1) AS cache_hit_rate,
    MAX(oc.scraped_at) AS last_cache_update,
    EXTRACT(EPOCH FROM (NOW() - MAX(oc.scraped_at))) / 86400 AS cache_age_days
FROM compliance_analyses ca
JOIN properties p ON ca.property_id = p.id
JOIN jurisdictions j ON p.jurisdiction = j.id
LEFT JOIN ordinance_cache oc ON j.id = oc.jurisdiction_id
WHERE ca.analyzed_at > NOW() - INTERVAL '7 days'
GROUP BY j.full_name
ORDER BY cache_hit_rate DESC;
```

### **Top Violations**
```sql
CREATE VIEW top_violations AS
SELECT 
    v.violation_type,
    v.severity,
    COUNT(*) AS occurrence_count,
    ROUND(AVG(v.estimated_fix_cost), 2) AS avg_fix_cost,
    j.full_name AS most_common_jurisdiction
FROM violations v
JOIN compliance_analyses ca ON v.analysis_id = ca.id
JOIN properties p ON ca.property_id = p.id
JOIN jurisdictions j ON p.jurisdiction = j.id
WHERE ca.analyzed_at > NOW() - INTERVAL '90 days'
GROUP BY v.violation_type, v.severity, j.full_name
ORDER BY occurrence_count DESC
LIMIT 20;
```

### **Skill Performance Metrics**
```sql
CREATE VIEW skill_performance AS
SELECT 
    (labels->>'skill') AS skill_name,
    (labels->>'stage') AS stage,
    COUNT(*) AS execution_count,
    ROUND(AVG(value), 2) AS avg_value,
    ROUND(PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY value), 2) AS p95_value,
    ROUND(MIN(value), 2) AS min_value,
    ROUND(MAX(value), 2) AS max_value
FROM zonewise_metrics
WHERE metric_name LIKE '%_execution_ms'
AND timestamp > NOW() - INTERVAL '7 days'
GROUP BY skill_name, stage
ORDER BY execution_count DESC;
```

---

## Supabase Storage Buckets

### **reports**
```javascript
// Bucket: zonewise-reports
// Policy: Authenticated users can read their own reports

{
  "id": "zonewise-reports",
  "name": "zonewise-reports",
  "public": false,
  "file_size_limit": 10485760, // 10 MB
  "allowed_mime_types": [
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
  ]
}

// Path structure:
// /reports/{user_id}/{analysis_id}/{report_id}.pdf
// /reports/{user_id}/{analysis_id}/{report_id}.docx
```

### **ordinances**
```javascript
// Bucket: zonewise-ordinances
// Policy: Public read, system write

{
  "id": "zonewise-ordinances",
  "name": "zonewise-ordinances",
  "public": true,
  "file_size_limit": 52428800, // 50 MB
  "allowed_mime_types": [
    "application/pdf",
    "text/html"
  ]
}

// Path structure:
// /ordinances/{jurisdiction_id}/full_code.pdf
// /ordinances/{jurisdiction_id}/sections/{section_id}.html
```

### **property-photos**
```javascript
// Bucket: zonewise-property-photos
// Policy: Public read, system write

{
  "id": "zonewise-property-photos",
  "name": "zonewise-property-photos",
  "public": true,
  "file_size_limit": 5242880, // 5 MB
  "allowed_mime_types": [
    "image/jpeg",
    "image/png",
    "image/webp"
  ]
}

// Path structure:
// /property-photos/{parcel_id}/front.jpg
// /property-photos/{parcel_id}/aerial.jpg
// /property-photos/{parcel_id}/streetview.jpg
```

---

## Supabase Edge Functions

### **analyze-property**
```typescript
// supabase/functions/analyze-property/index.ts
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

serve(async (req) => {
  const { property_id } = await req.json()
  
  const supabase = createClient(
    Deno.env.get('SUPABASE_URL')!,
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
  )
  
  // Fetch property
  const { data: property } = await supabase
    .from('properties')
    .select('*, jurisdictions(*)')
    .eq('id', property_id)
    .single()
  
  // Call zonewize skill (via backend service)
  const analysis = await callZoneWizeSkill(property)
  
  // Store results
  await supabase.from('compliance_analyses').insert({
    property_id: property_id,
    correlation_id: crypto.randomUUID(),
    ...analysis
  })
  
  return new Response(JSON.stringify(analysis))
})
```

### **generate-report**
```typescript
// supabase/functions/generate-report/index.ts
serve(async (req) => {
  const { analysis_id, format } = await req.json()
  
  const supabase = createClient(/* ... */)
  
  // Fetch analysis data
  const { data } = await supabase
    .from('compliance_analyses')
    .select('*, properties(*), violations(*)')
    .eq('id', analysis_id)
    .single()
  
  // Generate report (call backend DOCX/PDF generator)
  const reportBuffer = await generateReport(data, format)
  
  // Upload to storage
  const fileName = `${analysis_id}.${format}`
  const { data: upload } = await supabase.storage
    .from('zonewise-reports')
    .upload(fileName, reportBuffer)
  
  // Store metadata
  await supabase.from('reports').insert({
    analysis_id: analysis_id,
    property_id: data.property_id,
    report_type: 'compliance_report',
    format: format,
    file_url: upload.path
  })
  
  return new Response(JSON.stringify({ url: upload.path }))
})
```

---

## Row Level Security (RLS) Policies

### **Properties Table**
```sql
-- Enable RLS
ALTER TABLE properties ENABLE ROW LEVEL SECURITY;

-- Public can read all properties
CREATE POLICY "Public can read properties"
ON properties FOR SELECT
USING (true);

-- Only service role can write
CREATE POLICY "Service role can insert/update properties"
ON properties FOR ALL
USING (auth.role() = 'service_role');
```

### **Compliance Analyses Table**
```sql
ALTER TABLE compliance_analyses ENABLE ROW LEVEL SECURITY;

-- Users can read their own analyses
CREATE POLICY "Users can read their analyses"
ON compliance_analyses FOR SELECT
USING (auth.uid() = user_id); -- Assuming user_id column exists

-- Service role can write
CREATE POLICY "Service role can write analyses"
ON compliance_analyses FOR ALL
USING (auth.role() = 'service_role');
```

### **Reports Table**
```sql
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;

-- Users can read their own reports
CREATE POLICY "Users can read their reports"
ON reports FOR SELECT
USING (auth.uid() = user_id);

-- Service role can write
CREATE POLICY "Service role can write reports"
ON reports FOR ALL
USING (auth.role() = 'service_role');
```

---

## Prompt Engineering Integration

### **zonewize Skill Prompt Templates**

#### **Ordinance Parsing Prompt (Gemini 2.5 Flash)**
```
You are a zoning ordinance parsing specialist. Extract structured zoning information from the following ordinance HTML.

ORDINANCE TEXT:
{ordinance_html}

JURISDICTION: {jurisdiction_name}

Extract the following in valid JSON format:

1. ZONING_DISTRICTS: Array of all zoning district codes (e.g., ["R-1", "R-2", "C-1"])

2. ALLOWED_USES: Object mapping each district to array of permitted uses
   Example: {"R-1": ["single_family_residence", "home_occupation"]}

3. DIMENSIONAL_REQUIREMENTS: Object with setbacks, height limits, lot requirements
   Example: {"R-1": {"front_setback": 25, "height_limit": 35, "min_lot_size": 7200}}

4. ORDINANCE_SECTIONS: Array of ordinance section references
   Example: ["Section 62-1234", "Article IV"]

Return ONLY valid JSON, no markdown formatting, no explanation.

JSON:
```

#### **Compliance Check Prompt (Gemini 2.5 Flash)**
```
You are a zoning compliance analyst. Determine if a property complies with zoning regulations.

PROPERTY:
- Address: {address}
- Zoning District: {zoning_district}
- Current Use: {current_use}
- Lot Size: {lot_size} sqft
- Setbacks: Front {front_setback}ft, Side {side_setback}ft, Rear {rear_setback}ft
- Building Height: {building_height}ft

ZONING RULES FOR {zoning_district}:
- Allowed Uses: {allowed_uses}
- Minimum Lot Size: {min_lot_size} sqft
- Required Setbacks: Front {required_front}ft, Side {required_side}ft, Rear {required_rear}ft
- Maximum Height: {max_height}ft

Analyze compliance and return JSON:
{
  "compliant": boolean,
  "violations": [
    {
      "type": "use|setback|height|lot_size",
      "description": "Human-readable description",
      "severity": "CRITICAL|MAJOR|MINOR"
    }
  ],
  "confidence": 0-100,
  "reasoning": "Brief explanation"
}

JSON:
```

---

## Implementation Checklist

### **Phase 1: Database Setup**
- [ ] Create ZoneWise Supabase project
- [ ] Run schema migration (all CREATE TABLE statements)
- [ ] Insert 17 jurisdiction records
- [ ] Set up PostGIS extension for spatial queries
- [ ] Configure RLS policies
- [ ] Create dashboard views

### **Phase 2: Storage Setup**
- [ ] Create zonewise-reports bucket
- [ ] Create zonewise-ordinances bucket
- [ ] Create zonewise-property-photos bucket
- [ ] Configure bucket policies
- [ ] Test file upload/download

### **Phase 3: Edge Functions**
- [ ] Deploy analyze-property function
- [ ] Deploy generate-report function
- [ ] Test with sample data
- [ ] Monitor function logs

### **Phase 4: zonewize Integration**
- [ ] Update analyzer.py with Supabase client
- [ ] Implement cache_ordinance() function
- [ ] Implement _fetch_property_data() function
- [ ] Test end-to-end with real Supabase
- [ ] Verify metrics logging
- [ ] Verify error tracking

### **Phase 5: Monitoring**
- [ ] Create Grafana dashboards (or Supabase Studio)
- [ ] Set up alerts for high error rates
- [ ] Monitor cache hit rates
- [ ] Track API costs
- [ ] Review performance metrics weekly

---

## Connection Strings

### **Python (Supabase Client)**
```python
from supabase import create_client, Client

url: str = "https://[project-ref].supabase.co"
key: str = "your-anon-key"
supabase: Client = create_client(url, key)

# Example: Fetch property
property = supabase.table('properties').select('*').eq('parcel_id', '123456').single().execute()

# Example: Insert analysis
analysis = supabase.table('compliance_analyses').insert({
    'property_id': property_id,
    'compliance_status': 'COMPLIANT',
    'confidence_score': 95
}).execute()

# Example: Log metric
metric = supabase.table('zonewise_metrics').insert({
    'metric_name': 'zonewize_execution_ms',
    'value': 450,
    'labels': {'jurisdiction': 'indian_harbour_beach'}
}).execute()
```

### **JavaScript/TypeScript (Edge Functions)**
```typescript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  Deno.env.get('SUPABASE_URL')!,
  Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
)

// Example: Real-time subscription
const subscription = supabase
  .channel('compliance-updates')
  .on('postgres_changes', {
    event: 'INSERT',
    schema: 'public',
    table: 'compliance_analyses'
  }, (payload) => {
    console.log('New analysis:', payload.new)
  })
  .subscribe()
```

---

## Cost Estimates

### **Supabase Pricing (Pro Plan - $25/month)**
- Database: 8 GB included (zonewise likely <2 GB)
- Storage: 100 GB included (reports + photos <10 GB)
- Bandwidth: 250 GB included
- Edge Function Requests: 2M included
- **Estimated Cost:** $25/month (Pro plan sufficient)

### **zonewize Skill Costs**
- Firecrawl: $0.005/property (with 85% cache hit = $0.00075 avg)
- Gemini 2.5 Flash: $0.00 (FREE tier)
- Supabase operations: Included in Pro plan
- **Total:** ~$0.00075 per property analysis

### **Monthly Cost (500 analyses)**
- zonewize skill: 500 × $0.00075 = $0.38
- Supabase: $25
- **Total:** $25.38/month

---

## Next Steps

1. **Create Supabase Project:** zonewise.supabase.co
2. **Run Migration:** Execute all CREATE TABLE statements
3. **Configure Storage:** Create 3 buckets
4. **Update zonewize:** Connect Supabase client
5. **Test End-to-End:** Analyze real property
6. **Deploy to Production:** GitHub Actions integration

---

**END OF SUPABASE INTEGRATION DOCUMENTATION**

**Version:** 2.0.0 (with zonewize skill)  
**Last Updated:** January 13, 2026  
**Repository:** breverdbidder/zonewise