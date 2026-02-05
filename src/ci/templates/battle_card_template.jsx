import { useState } from "react";

const TABS = ["⚔️ Competitive Intel", "💰 Cost Strategy", "📊 63 KPIs vs Gridics", "🏗️ Architecture", "📋 Action Plan"];

// Gridics actual API pricing from developer.gridics.com/plans
const GRIDICS_PRICING = {
  basic: { price: 0.29, features: "Address, Zone, FAR, Height, Lot Area, Coverage" },
  enhanced: { price: 0.49, features: "+ Overlays, Uses" },
  premium: { price: 0.69, features: "+ Setbacks, Geometry, Capacity, Lot Type, Frontages" },
};

// Data sources by cost tier
const DATA_SOURCES = [
  { name: "FL GIO Statewide Parcels", records: "10.8M", cost: "$0", type: "Bulk Download", covers: "Boundaries, tax roll, owner, values, sqft, year built", priority: "P0" },
  { name: "FL DOR Tax Roll", records: "10.8M", cost: "$0", type: "Bulk Download", covers: "Assessed values, exemptions, sales, building details", priority: "P0" },
  { name: "County GIS Portals (67)", records: "10.8M", cost: "$0", type: "ArcGIS REST", covers: "Zoning overlay, FLUM, flood zones, parcel geometry", priority: "P0" },
  { name: "Municode (AgentQL)", records: "369 cities", cost: "$99/mo", type: "Semantic Scrape", covers: "Zoning districts, dimensional standards, uses, overlays", priority: "P1" },
  { name: "Census API", records: "67 counties", cost: "$0", type: "REST API", covers: "Demographics, income, population, housing stats", priority: "P1" },
  { name: "FEMA NFHL", records: "Statewide", cost: "$0", type: "GIS Service", covers: "Flood zones, BFE, SFHA designation", priority: "P1" },
  { name: "FDOT GIS", records: "Statewide", cost: "$0", type: "GIS Service", covers: "Road networks, traffic counts, transit routes", priority: "P2" },
  { name: "School Districts", records: "67 counties", cost: "$0", type: "GIS/API", covers: "School assignments, ratings, boundaries", priority: "P2" },
  { name: "BCPAO-style APIs (67)", records: "10.8M", cost: "$0", type: "County APIs", covers: "Photos, detailed building records, sales history", priority: "P2" },
  { name: "OpenStreetMap", records: "Statewide", cost: "$0", type: "Bulk Download", covers: "POIs, amenities, road network for Walk Score calc", priority: "P2" },
];

// 20 Phases framework
const PHASES_20 = [
  { phase: 1, name: "Jurisdiction Metadata", category: "Foundation", gridics: "✅", zonewise: "✅ 17 done", status: "green" },
  { phase: 2, name: "Base Zoning Districts", category: "Zoning", gridics: "✅", zonewise: "✅ 301 done", status: "green" },
  { phase: 3, name: "Dimensional Standards", category: "Zoning", gridics: "✅", zonewise: "✅ Proven", status: "green" },
  { phase: 4, name: "Permitted Uses", category: "Uses", gridics: "✅", zonewise: "⚠️ Partial", status: "yellow" },
  { phase: 5, name: "Conditional Uses", category: "Uses", gridics: "✅", zonewise: "⚠️ Partial", status: "yellow" },
  { phase: 6, name: "Overlay Districts", category: "Zoning", gridics: "✅", zonewise: "❌ Schema only", status: "red" },
  { phase: 7, name: "Development Bonuses", category: "Zoning", gridics: "⚠️", zonewise: "❌ Not started", status: "red" },
  { phase: 8, name: "Parking Requirements", category: "Zoning", gridics: "✅", zonewise: "❌ Not started", status: "red" },
  { phase: 9, name: "Density & Intensity", category: "Zoning", gridics: "✅", zonewise: "⚠️ Partial", status: "yellow" },
  { phase: 10, name: "Future Land Use (FLUM)", category: "Regulatory", gridics: "✅", zonewise: "❌ Not started", status: "red" },
  { phase: 11, name: "Permitted Uses (Detail)", category: "Uses", gridics: "✅", zonewise: "❌ Not started", status: "red" },
  { phase: 12, name: "Conditional Uses (Detail)", category: "Uses", gridics: "✅", zonewise: "❌ Not started", status: "red" },
  { phase: 13, name: "Prohibited Uses", category: "Uses", gridics: "⚠️", zonewise: "❌ Not started", status: "red" },
  { phase: 14, name: "Accessory Uses / ADU", category: "Uses", gridics: "✅", zonewise: "❌ Not started", status: "red" },
  { phase: 15, name: "Use-Specific Standards", category: "Uses", gridics: "⚠️", zonewise: "❌ Not started", status: "red" },
  { phase: 16, name: "Parcel-Zone Assignment", category: "Parcels", gridics: "✅", zonewise: "✅ Proven", status: "green" },
  { phase: 17, name: "Parcel Geometries", category: "Parcels", gridics: "✅", zonewise: "⚠️ FL GIO", status: "yellow" },
  { phase: 18, name: "Cross-Validation", category: "QA", gridics: "✅", zonewise: "✅ Proven", status: "green" },
  { phase: 19, name: "Source Documentation", category: "QA", gridics: "✅", zonewise: "✅ Proven", status: "green" },
  { phase: 20, name: "Quality Scoring", category: "QA", gridics: "✅", zonewise: "✅ Proven", status: "green" },
];

// 63 KPIs mapped to Gridics equivalents
const KPI_CATEGORIES = [
  {
    name: "Site & Parcel Metrics", count: 8, gridicsMatch: 8,
    kpis: ["Parcel ID", "Tax Account", "Lot Area (Acres)", "Lot Area (ft²)", "Lot Type", "Subdivision", "Vacant Status", "Legal Description"],
    advantage: "MATCH - Both from county data"
  },
  {
    name: "Existing Building", count: 5, gridicsMatch: 3,
    kpis: ["Building Area", "Current Use", "Year Built", "Construction Type", "Neighborhood"],
    advantage: "ZW WINS +2 KPIs (construction, neighborhood)"
  },
  {
    name: "Zoning & Regulatory", count: 10, gridicsMatch: 8,
    kpis: ["Zone Code", "Zone Name", "FAR", "Max Height", "Max Stories", "Lot Coverage", "Min Open Space", "FLUM", "Overlays", "Historic District"],
    advantage: "ZW WINS +2 (FLUM source linking, historic detail)"
  },
  {
    name: "Development Capacity", count: 9, gridicsMatch: 9,
    kpis: ["Max Buildable Area", "Max Footprint", "Unused Dev Rights", "Current FAR", "FAR Utilization %", "Expansion Potential", "Form Max Area", "Podium Area", "Tower Area"],
    advantage: "MATCH - Gridics patented engine is strong here"
  },
  {
    name: "Residential Capacity", count: 4, gridicsMatch: 4,
    kpis: ["Density (units/acre)", "Max Residential Units", "Max Residential Area", "Allowed Residential Uses"],
    advantage: "MATCH"
  },
  {
    name: "Lodging Capacity", count: 4, gridicsMatch: 4,
    kpis: ["Lodging Density", "Max Rooms", "Max Lodging Area", "Allowed Lodging Types"],
    advantage: "MATCH"
  },
  {
    name: "Commercial/Office", count: 5, gridicsMatch: 5,
    kpis: ["Max Commercial Area", "Max Office Area", "Max Industrial Area", "Max Civic Area", "Expansion Potential"],
    advantage: "MATCH"
  },
  {
    name: "Setback Requirements", count: 5, gridicsMatch: 5,
    kpis: ["Front Setback", "Side Setback", "Rear Setback", "Water Setback", "Tower Setbacks"],
    advantage: "MATCH - Gridics has podium/tower/penthouse detail"
  },
  {
    name: "Allowed Uses", count: 6, gridicsMatch: 3,
    kpis: ["Residential Uses", "Commercial Uses", "Civic Uses", "Educational Uses", "Infrastructure Uses", "STR Allowed"],
    advantage: "ZW WINS +3 (STR, educational, infrastructure)"
  },
  {
    name: "Financial Opportunity", count: 7, gridicsMatch: 0,
    kpis: ["FAR Utilization %", "Untapped Potential %", "Expansion %", "Est. Unit Potential", "PropZone Score Equiv", "Market Value", "Last Sale Price"],
    advantage: "ZW WINS +7 (Gridics has PropZone Score but no financials)"
  },
];

const StatusDot = ({ status }) => {
  const colors = { green: "#22c55e", yellow: "#eab308", red: "#ef4444" };
  return <span style={{ display: "inline-block", width: 10, height: 10, borderRadius: "50%", background: colors[status], marginRight: 6 }} />;
};

const Tab1_CompetitiveIntel = () => (
  <div>
    <h2 style={{ fontSize: 20, fontWeight: 700, color: "#1a1a2e", marginBottom: 16, fontFamily: "'DM Sans', sans-serif" }}>
      Gridics/PropZone — Reverse Engineering Report
    </h2>

    <div style={{ background: "#fff8f0", border: "1px solid #f59e0b", borderRadius: 8, padding: 16, marginBottom: 20 }}>
      <div style={{ fontWeight: 700, color: "#92400e", marginBottom: 8 }}>⚡ Gridics Weakness We Exploit</div>
      <div style={{ fontSize: 14, color: "#78350f", lineHeight: 1.6 }}>
        Gridics charges <strong>$0.69/parcel</strong> for Premium API data. At 10.8M FL parcels = <strong>$7.45M</strong> to replicate their Florida dataset via their own API.
        They built this over 10 years with a team of architects and urban planners. We replicate it with AI agents pulling from the <strong>same free public data sources</strong> they use,
        then add financial analysis they completely lack. Their "patented rules engine" is just zoning math — our 63 KPI calculator does the same thing.
      </div>
    </div>

    <div style={{ fontWeight: 700, fontSize: 16, marginBottom: 12, color: "#1a1a2e" }}>Gridics API Pricing (developer.gridics.com)</div>
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12, marginBottom: 24 }}>
      {Object.entries(GRIDICS_PRICING).map(([tier, data]) => (
        <div key={tier} style={{ background: "#f8fafc", border: "1px solid #e2e8f0", borderRadius: 8, padding: 14 }}>
          <div style={{ fontWeight: 700, fontSize: 15, textTransform: "capitalize", color: tier === "premium" ? "#7c3aed" : "#334155" }}>
            {tier} — ${data.price}/call
          </div>
          <div style={{ fontSize: 12, color: "#64748b", marginTop: 6 }}>{data.features}</div>
          <div style={{ fontSize: 12, color: "#ef4444", marginTop: 8, fontWeight: 600 }}>
            FL cost: ${(data.price * 10800000).toLocaleString()}
          </div>
        </div>
      ))}
    </div>

    <div style={{ fontWeight: 700, fontSize: 16, marginBottom: 12, color: "#1a1a2e" }}>What Gridics Has That We Need</div>
    <div style={{ fontSize: 14, lineHeight: 1.8, color: "#334155" }}>
      <div>✅ <strong>Patented zoning rules engine</strong> — We replicate with KPI Calculator (dimensional_standards → max buildable area)</div>
      <div>✅ <strong>3D building envelope visualization</strong> — We skip this for MVP, add later with Three.js</div>
      <div>✅ <strong>30+ zoning attributes per parcel</strong> — Our 63 KPIs exceed this by 2x</div>
      <div>✅ <strong>Municipal partnerships</strong> — We scrape Municode instead (same data, no partnerships needed)</div>
      <div>✅ <strong>PropZone Score</strong> — Our Financial Opportunity category (7 KPIs) goes deeper</div>
    </div>

    <div style={{ fontWeight: 700, fontSize: 16, marginBottom: 12, marginTop: 20, color: "#1a1a2e" }}>What Gridics Lacks (Our Advantage)</div>
    <div style={{ fontSize: 14, lineHeight: 1.8, color: "#334155" }}>
      <div>❌ <strong>No financial analysis</strong> — No market value, sale prices, ROI, IRR</div>
      <div>❌ <strong>No STR analysis</strong> — Doesn't tell you if short-term rentals are allowed</div>
      <div>❌ <strong>No ADU detail</strong> — Missing accessory dwelling unit specifics</div>
      <div>❌ <strong>No demographics</strong> — No census data, income levels, population trends</div>
      <div>❌ <strong>No foreclosure data</strong> — This is our BidDeed.AI crossover advantage</div>
      <div>❌ <strong>No AI chat interface</strong> — Static maps only, no NLP queries</div>
      <div>❌ <strong>$650/report</strong> — Their expert reports cost $650 each. Ours are automated and free</div>
    </div>
  </div>
);

const Tab2_CostStrategy = () => {
  const totalFree = DATA_SOURCES.filter(d => d.cost === "$0").length;
  const totalPaid = DATA_SOURCES.filter(d => d.cost !== "$0").length;

  return (
    <div>
      <h2 style={{ fontSize: 20, fontWeight: 700, color: "#1a1a2e", marginBottom: 16, fontFamily: "'DM Sans', sans-serif" }}>
        Cost-Optimized Data Acquisition — 10.8M Parcels
      </h2>

      <div style={{ background: "#f0fdf4", border: "1px solid #22c55e", borderRadius: 8, padding: 16, marginBottom: 20 }}>
        <div style={{ fontWeight: 700, color: "#166534", fontSize: 18 }}>Total Monthly Cost: $99/mo (AgentQL Pro)</div>
        <div style={{ fontSize: 14, color: "#15803d", marginTop: 4 }}>
          {totalFree} data sources are FREE | {totalPaid} paid source (Municode scraping via AgentQL)
        </div>
        <div style={{ fontSize: 14, color: "#15803d", marginTop: 4 }}>
          vs Gridics equivalent: $7.45M (Premium API for all FL parcels)
        </div>
      </div>

      <div style={{ overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
          <thead>
            <tr style={{ background: "#1e293b", color: "#f8fafc" }}>
              <th style={{ padding: "10px 8px", textAlign: "left" }}>Priority</th>
              <th style={{ padding: "10px 8px", textAlign: "left" }}>Source</th>
              <th style={{ padding: "10px 8px", textAlign: "right" }}>Records</th>
              <th style={{ padding: "10px 8px", textAlign: "right" }}>Cost</th>
              <th style={{ padding: "10px 8px", textAlign: "left" }}>Type</th>
              <th style={{ padding: "10px 8px", textAlign: "left" }}>Covers</th>
            </tr>
          </thead>
          <tbody>
            {DATA_SOURCES.map((src, i) => (
              <tr key={i} style={{ background: i % 2 === 0 ? "#ffffff" : "#f8fafc", borderBottom: "1px solid #e2e8f0" }}>
                <td style={{ padding: "8px", fontWeight: 700, color: src.priority === "P0" ? "#16a34a" : src.priority === "P1" ? "#2563eb" : "#9333ea" }}>
                  {src.priority}
                </td>
                <td style={{ padding: 8, fontWeight: 600 }}>{src.name}</td>
                <td style={{ padding: 8, textAlign: "right", fontFamily: "monospace" }}>{src.records}</td>
                <td style={{ padding: 8, textAlign: "right", fontWeight: 700, color: src.cost === "$0" ? "#16a34a" : "#dc2626" }}>{src.cost}</td>
                <td style={{ padding: 8, fontSize: 12 }}>{src.type}</td>
                <td style={{ padding: 8, fontSize: 12, color: "#64748b" }}>{src.covers}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div style={{ marginTop: 24 }}>
        <div style={{ fontWeight: 700, fontSize: 16, marginBottom: 12, color: "#1a1a2e" }}>Upgrade Path</div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12 }}>
          <div style={{ background: "#dbeafe", borderRadius: 8, padding: 14, border: "2px solid #3b82f6" }}>
            <div style={{ fontWeight: 700, color: "#1e40af", fontSize: 14 }}>NOW: AgentQL Pro $99/mo</div>
            <div style={{ fontSize: 12, color: "#1e3a5f", marginTop: 6 }}>10,000 calls/mo. Covers 67 FL counties × ~50 pages each = 3,350 calls. Immediate deep scrape for all 369 cities.</div>
          </div>
          <div style={{ background: "#f3e8ff", borderRadius: 8, padding: 14, border: "1px solid #c084fc" }}>
            <div style={{ fontWeight: 700, color: "#6b21a8", fontSize: 14 }}>Q2: AgentQL Ultimate</div>
            <div style={{ fontSize: 12, color: "#581c87", marginTop: 6 }}>When scaling to national (3,143 counties). ~31K calls/mo = $99 + $321 overage = $420/mo for ALL US counties.</div>
          </div>
          <div style={{ background: "#fef3c7", borderRadius: 8, padding: 14, border: "1px solid #f59e0b" }}>
            <div style={{ fontWeight: 700, color: "#92400e", fontSize: 14 }}>Q3: Enterprise</div>
            <div style={{ fontSize: 12, color: "#78350f", marginTop: 6 }}>$0.008/call at volume. 150K calls/mo for national coverage = ~$1,200/mo. Full "USA Real Estate Decoded" scale.</div>
          </div>
        </div>
      </div>

      <div style={{ marginTop: 24, background: "#fef2f2", border: "1px solid #ef4444", borderRadius: 8, padding: 16 }}>
        <div style={{ fontWeight: 700, color: "#991b1b", marginBottom: 8 }}>⚠️ Critical: Do NOT Scrape Individual Parcels with AgentQL</div>
        <div style={{ fontSize: 13, color: "#7f1d1d" }}>
          10.8M parcels × $0.015/call = $162,000. The strategy is: AgentQL discovers data source URLs/APIs for each county → 
          Then use FREE county ArcGIS REST APIs and FL GIO bulk downloads to get the actual parcel data. AgentQL = discovery tool, not data extractor.
        </div>
      </div>
    </div>
  );
};

const Tab3_KPIs = () => {
  const totalOurs = KPI_CATEGORIES.reduce((sum, c) => sum + c.count, 0);
  const totalGridics = KPI_CATEGORIES.reduce((sum, c) => sum + c.gridicsMatch, 0);
  const advantages = KPI_CATEGORIES.filter(c => c.count > c.gridicsMatch).length;

  return (
    <div>
      <h2 style={{ fontSize: 20, fontWeight: 700, color: "#1a1a2e", marginBottom: 16, fontFamily: "'DM Sans', sans-serif" }}>
        63 KPIs vs Gridics — Feature Parity Analysis
      </h2>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12, marginBottom: 20 }}>
        <div style={{ background: "#dbeafe", borderRadius: 8, padding: 14, textAlign: "center" }}>
          <div style={{ fontSize: 28, fontWeight: 800, color: "#1e40af" }}>{totalOurs}</div>
          <div style={{ fontSize: 12, color: "#3b82f6" }}>ZoneWise KPIs</div>
        </div>
        <div style={{ background: "#f3e8ff", borderRadius: 8, padding: 14, textAlign: "center" }}>
          <div style={{ fontSize: 28, fontWeight: 800, color: "#6b21a8" }}>{totalGridics}</div>
          <div style={{ fontSize: 12, color: "#9333ea" }}>Gridics Equivalent</div>
        </div>
        <div style={{ background: "#dcfce7", borderRadius: 8, padding: 14, textAlign: "center" }}>
          <div style={{ fontSize: 28, fontWeight: 800, color: "#16a34a" }}>{advantages}</div>
          <div style={{ fontSize: 12, color: "#22c55e" }}>Categories Where ZW Wins</div>
        </div>
      </div>

      {KPI_CATEGORIES.map((cat, i) => {
        const diff = cat.count - cat.gridicsMatch;
        const barColor = diff > 0 ? "#22c55e" : diff === 0 ? "#3b82f6" : "#ef4444";
        return (
          <div key={i} style={{ marginBottom: 16, background: "#f8fafc", borderRadius: 8, padding: 12, border: "1px solid #e2e8f0" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
              <div style={{ fontWeight: 700, fontSize: 14, color: "#1a1a2e" }}>
                {i + 1}. {cat.name}
              </div>
              <div style={{ fontSize: 12, fontWeight: 600, color: barColor }}>
                ZW: {cat.count} | Gridics: {cat.gridicsMatch} {diff > 0 ? `(+${diff} ZW)` : diff === 0 ? "(MATCH)" : ""}
              </div>
            </div>
            <div style={{ display: "flex", gap: 4, marginBottom: 6 }}>
              <div style={{ height: 6, background: "#3b82f6", borderRadius: 3, flex: cat.count }} title={`ZoneWise: ${cat.count}`} />
              <div style={{ height: 6, background: "#c084fc", borderRadius: 3, flex: cat.gridicsMatch, opacity: 0.6 }} title={`Gridics: ${cat.gridicsMatch}`} />
            </div>
            <div style={{ fontSize: 11, color: "#64748b" }}>{cat.kpis.join(" · ")}</div>
            <div style={{ fontSize: 12, fontWeight: 600, color: barColor, marginTop: 4 }}>{cat.advantage}</div>
          </div>
        );
      })}
    </div>
  );
};

const Tab4_Architecture = () => (
  <div>
    <h2 style={{ fontSize: 20, fontWeight: 700, color: "#1a1a2e", marginBottom: 16, fontFamily: "'DM Sans', sans-serif" }}>
      Data Pipeline Architecture — 10.8M Parcels
    </h2>

    <div style={{ background: "#1e293b", borderRadius: 12, padding: 20, color: "#e2e8f0", fontFamily: "monospace", fontSize: 12, lineHeight: 2, marginBottom: 24, overflowX: "auto" }}>
      <div style={{ color: "#60a5fa", fontWeight: 700 }}>═══ LAYER 1: DATA ACQUISITION (P0 — FREE) ═══</div>
      <div>FL GIO Bulk Download ─── 10.8M parcels + geometries ──→ PostGIS/Supabase</div>
      <div>FL DOR Tax Roll ─────── Values, sales, buildings ──────→ parcel_details table</div>
      <div>67 County GIS APIs ──── Zoning overlay + FLUM ────────→ parcel_zones table</div>
      <div style={{ color: "#34d399", marginTop: 4 }}>Cost: $0 | Time: 2-3 days (bulk download + parse)</div>

      <div style={{ color: "#f59e0b", fontWeight: 700, marginTop: 16 }}>═══ LAYER 2: ZONING INTELLIGENCE (P1 — $99/mo) ═══</div>
      <div>AgentQL Pro ──── 369 FL cities on Municode ──→ zoning_districts table</div>
      <div>AgentQL Pro ──── Dimensional standards ──────→ dimensional_standards table</div>
      <div>AgentQL Pro ──── Permitted/conditional uses ─→ zoning_uses table</div>
      <div>Census API ───── Demographics per tract ─────→ census_data table</div>
      <div>FEMA NFHL ────── Flood zone per parcel ──────→ flood_zones table</div>
      <div style={{ color: "#34d399", marginTop: 4 }}>Cost: $99/mo | Time: 1-2 weeks (scrape + validate)</div>

      <div style={{ color: "#a78bfa", fontWeight: 700, marginTop: 16 }}>═══ LAYER 3: ENRICHMENT (P2 — FREE) ═══</div>
      <div>School Boundaries ── Assignments per parcel ──→ school_data table</div>
      <div>County Photo APIs ── Property photos ──────────→ CDN/Supabase Storage</div>
      <div>OSM/Overpass ─────── Walk Score calculation ───→ location_scores table</div>
      <div>FDOT ───────────────  Traffic + transit ────────→ transportation table</div>
      <div style={{ color: "#34d399", marginTop: 4 }}>Cost: $0 | Time: 1-2 weeks</div>

      <div style={{ color: "#f472b6", fontWeight: 700, marginTop: 16 }}>═══ LAYER 4: COMPUTATION (63 KPIs) ═══</div>
      <div>KPI Calculator ──── parcel + zone + dims ────→ 63 KPIs per parcel</div>
      <div>Dev Capacity ────── FAR × lot area = max bldg ──→ development_capacity</div>
      <div>Financial Opp ───── utilization % + untapped ──→ opportunity_scores</div>
      <div>Report Generator ── DOCX + PDF per parcel ────→ on-demand generation</div>
      <div style={{ color: "#34d399", marginTop: 4 }}>Cost: Compute only | Time: ~4 hours for 10.8M parcels</div>

      <div style={{ color: "#fb923c", fontWeight: 700, marginTop: 16 }}>═══ LAYER 5: DELIVERY ═══</div>
      <div>Mapbox GL JS ────── Interactive map (split-screen) ──→ ZoneWise.AI UI</div>
      <div>NLP Chat ──────────  "Show me CG parcels in Malabar" ──→ Chat left panel</div>
      <div>Report Gen ────────  63 KPI DOCX/PDF on-demand ──────→ Artifacts right panel</div>
      <div>API ───────────────  REST + WebSocket for agents ────→ /api/v1/parcels</div>
    </div>

    <div style={{ fontWeight: 700, fontSize: 16, marginBottom: 12, color: "#1a1a2e" }}>Supabase Schema (New Tables)</div>
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, fontSize: 12 }}>
      {[
        { table: "fl_parcels", rows: "10.8M", desc: "FL GIO parcel boundaries + tax roll core" },
        { table: "parcel_details", rows: "10.8M", desc: "Building details, sales, values from DOR" },
        { table: "parcel_zones", rows: "10.8M", desc: "Zone code assignment from county GIS" },
        { table: "zoning_districts", rows: "~5K", desc: "All FL zoning codes + dims (301 done)" },
        { table: "dimensional_standards", rows: "~5K", desc: "Setbacks, FAR, height, coverage per zone" },
        { table: "zoning_uses", rows: "~50K", desc: "Permitted/conditional/prohibited per zone" },
        { table: "flood_zones", rows: "10.8M", desc: "FEMA zone per parcel" },
        { table: "census_data", rows: "~4K", desc: "Demographics per census tract" },
        { table: "school_assignments", rows: "10.8M", desc: "School district per parcel" },
        { table: "kpi_cache", rows: "10.8M", desc: "Pre-computed 63 KPIs per parcel" },
      ].map((t, i) => (
        <div key={i} style={{ background: "#f1f5f9", borderRadius: 6, padding: 10, border: "1px solid #e2e8f0" }}>
          <div style={{ fontWeight: 700, fontFamily: "monospace", color: "#1e40af" }}>{t.table}</div>
          <div style={{ color: "#64748b" }}>{t.rows} rows — {t.desc}</div>
        </div>
      ))}
    </div>
  </div>
);

const Tab5_ActionPlan = () => (
  <div>
    <h2 style={{ fontSize: 20, fontWeight: 700, color: "#1a1a2e", marginBottom: 16, fontFamily: "'DM Sans', sans-serif" }}>
      Execution Plan — Florida Complete Coverage
    </h2>

    <div style={{ background: "#eff6ff", border: "2px solid #3b82f6", borderRadius: 8, padding: 16, marginBottom: 20 }}>
      <div style={{ fontWeight: 700, color: "#1e40af", fontSize: 16 }}>Total Budget: $99/mo + Compute</div>
      <div style={{ fontSize: 14, color: "#1e3a5f", marginTop: 4 }}>
        Timeline: 6 weeks to full Florida coverage with all 63 KPIs on 10.8M parcels
      </div>
    </div>

    {[
      {
        week: "Week 1", title: "Foundation Data Load", cost: "$0",
        tasks: [
          "✅ Upgrade AgentQL to Pro ($99/mo) — APPROVE THIS",
          "Download FL GIO statewide parcels (10.8M boundaries + attributes)",
          "Download FL DOR tax roll (values, sales, building details)",
          "Create fl_parcels + parcel_details tables in Supabase",
          "Load and index 10.8M records (~12 hours bulk insert)",
          "Verify: random sample 100 parcels across 10 counties",
        ]
      },
      {
        week: "Week 2", title: "County GIS Integration", cost: "$0",
        tasks: [
          "Map all 67 county ArcGIS REST endpoints (zoning + FLUM layers)",
          "Build universal GIS scraper (handles varying schemas)",
          "Assign zoning codes to 10.8M parcels via spatial join",
          "Load FEMA flood zone data (NFHL service)",
          "Verify: match BCPAO zoning vs GIS zoning for Brevard (baseline)",
        ]
      },
      {
        week: "Week 3", title: "Municode Deep Scrape", cost: "$99/mo",
        tasks: [
          "AgentQL Pro: Complete scraping for remaining 347 cities",
          "Extract: dimensional standards, permitted uses, conditional uses",
          "Parse overlays, bonuses, parking requirements",
          "Link districts to Supabase zoning_districts table",
          "Cross-validate: Malabar (known good) → extend patterns",
        ]
      },
      {
        week: "Week 4", title: "Enrichment Layer", cost: "$0",
        tasks: [
          "Census API: demographics for all FL tracts",
          "School district boundaries and assignments",
          "OSM-based location scoring (walkability, amenities)",
          "County photo API integration (Brevard pattern → 66 more)",
          "FDOT transportation data layer",
        ]
      },
      {
        week: "Week 5", title: "63 KPI Computation", cost: "Compute only",
        tasks: [
          "Deploy KPI Calculator for all 10.8M parcels",
          "Batch compute: dev capacity, FAR utilization, unused rights",
          "Financial opportunity scoring (untapped potential %)",
          "Generate kpi_cache table for instant lookups",
          "Benchmark: compare 100 parcels vs Gridics PropZone data",
        ]
      },
      {
        week: "Week 6", title: "UI + Reports", cost: "$0",
        tasks: [
          "Mapbox GL JS map with parcel boundaries (Mapbox token: verified)",
          "Split-screen UI: chat left, map/reports right",
          "NLP query parsing: 'Show CG parcels under 50% FAR utilization'",
          "On-demand 63 KPI DOCX report generation",
          "Deploy to Cloudflare Pages → zonewise.ai",
        ]
      },
    ].map((phase, i) => (
      <div key={i} style={{ marginBottom: 16, background: "#fff", borderRadius: 8, border: "1px solid #e2e8f0", overflow: "hidden" }}>
        <div style={{ background: "#1e293b", color: "#f8fafc", padding: "10px 14px", display: "flex", justifyContent: "space-between" }}>
          <span style={{ fontWeight: 700 }}>{phase.week}: {phase.title}</span>
          <span style={{ fontWeight: 700, color: phase.cost === "$0" ? "#34d399" : "#fbbf24" }}>{phase.cost}</span>
        </div>
        <div style={{ padding: 14 }}>
          {phase.tasks.map((task, j) => (
            <div key={j} style={{ fontSize: 13, padding: "4px 0", color: "#334155", borderBottom: j < phase.tasks.length - 1 ? "1px solid #f1f5f9" : "none" }}>
              {task}
            </div>
          ))}
        </div>
      </div>
    ))}

    <div style={{ marginTop: 20, background: "#faf5ff", border: "2px solid #9333ea", borderRadius: 8, padding: 16 }}>
      <div style={{ fontWeight: 700, color: "#6b21a8", fontSize: 16, marginBottom: 8 }}>🎯 End State: ZoneWise.AI Florida MVP</div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, fontSize: 13 }}>
        <div>📦 10.8M parcels with boundaries</div>
        <div>🏗️ 63 KPIs per parcel</div>
        <div>🗺️ Interactive Mapbox map</div>
        <div>💬 NLP chat interface</div>
        <div>📄 On-demand DOCX/PDF reports</div>
        <div>🔍 Zoning search + filter</div>
        <div>📊 Development capacity analysis</div>
        <div>💰 Financial opportunity scoring</div>
        <div>🏫 School + demographics data</div>
        <div>🌊 Flood zone integration</div>
        <div style={{ gridColumn: "1 / -1", fontWeight: 700, color: "#6b21a8", marginTop: 4 }}>
          Total cost: $99/mo AgentQL + $0 free data sources = LESS than $600 total to launch
        </div>
      </div>
    </div>
  </div>
);

const PHASE_STATUS_SUMMARY = () => {
  const green = PHASES_20.filter(p => p.status === "green").length;
  const yellow = PHASES_20.filter(p => p.status === "yellow").length;
  const red = PHASES_20.filter(p => p.status === "red").length;
  return { green, yellow, red };
};

export default function ZoneWiseBattlePlan() {
  const [activeTab, setActiveTab] = useState(0);
  const { green, yellow, red } = PHASE_STATUS_SUMMARY();

  const renderTab = () => {
    switch (activeTab) {
      case 0: return <Tab1_CompetitiveIntel />;
      case 1: return <Tab2_CostStrategy />;
      case 2: return <Tab3_KPIs />;
      case 3: return <Tab4_Architecture />;
      case 4: return <Tab5_ActionPlan />;
      default: return null;
    }
  };

  return (
    <div style={{ fontFamily: "'DM Sans', -apple-system, sans-serif", maxWidth: 900, margin: "0 auto", background: "#ffffff" }}>
      <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;800&display=swap" rel="stylesheet" />
      
      <div style={{ background: "linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #1e40af 100%)", color: "#fff", padding: "28px 24px", borderRadius: "12px 12px 0 0" }}>
        <div style={{ fontSize: 26, fontWeight: 800, letterSpacing: "-0.5px" }}>ZoneWise.AI vs PropZone/Gridics</div>
        <div style={{ fontSize: 14, color: "#93c5fd", marginTop: 4 }}>Competitive Intelligence & Execution Battle Plan</div>
        
        <div style={{ display: "flex", gap: 16, marginTop: 16 }}>
          <div style={{ background: "rgba(255,255,255,0.1)", borderRadius: 8, padding: "8px 14px", textAlign: "center" }}>
            <div style={{ fontSize: 22, fontWeight: 800 }}>10.8M</div>
            <div style={{ fontSize: 11, color: "#93c5fd" }}>FL Parcels</div>
          </div>
          <div style={{ background: "rgba(255,255,255,0.1)", borderRadius: 8, padding: "8px 14px", textAlign: "center" }}>
            <div style={{ fontSize: 22, fontWeight: 800 }}>63</div>
            <div style={{ fontSize: 11, color: "#93c5fd" }}>KPIs per Parcel</div>
          </div>
          <div style={{ background: "rgba(255,255,255,0.1)", borderRadius: 8, padding: "8px 14px", textAlign: "center" }}>
            <div style={{ fontSize: 22, fontWeight: 800 }}>$99<span style={{ fontSize: 12, fontWeight: 400 }}>/mo</span></div>
            <div style={{ fontSize: 11, color: "#93c5fd" }}>Total Data Cost</div>
          </div>
          <div style={{ background: "rgba(255,255,255,0.1)", borderRadius: 8, padding: "8px 14px", textAlign: "center" }}>
            <div style={{ fontSize: 22, fontWeight: 800 }}>
              <span style={{ color: "#4ade80" }}>{green}</span>/<span style={{ color: "#facc15" }}>{yellow}</span>/<span style={{ color: "#f87171" }}>{red}</span>
            </div>
            <div style={{ fontSize: 11, color: "#93c5fd" }}>20 Phases ✅/⚠️/❌</div>
          </div>
        </div>
      </div>

      <div style={{ display: "flex", background: "#f8fafc", borderBottom: "1px solid #e2e8f0", overflowX: "auto" }}>
        {TABS.map((tab, i) => (
          <button
            key={i}
            onClick={() => setActiveTab(i)}
            style={{
              padding: "12px 16px",
              fontSize: 13,
              fontWeight: activeTab === i ? 700 : 500,
              color: activeTab === i ? "#1e40af" : "#64748b",
              background: activeTab === i ? "#ffffff" : "transparent",
              border: "none",
              borderBottom: activeTab === i ? "3px solid #3b82f6" : "3px solid transparent",
              cursor: "pointer",
              whiteSpace: "nowrap",
              fontFamily: "'DM Sans', sans-serif",
            }}
          >
            {tab}
          </button>
        ))}
      </div>

      <div style={{ padding: 24, minHeight: 500 }}>
        {renderTab()}
      </div>

      <div style={{ background: "#f8fafc", borderTop: "1px solid #e2e8f0", padding: "12px 24px", borderRadius: "0 0 12px 12px", fontSize: 11, color: "#94a3b8", display: "flex", justifyContent: "space-between" }}>
        <span>ZoneWise.AI — USA Real Estate Decoded!</span>
        <span>Ariel Shapira · Everest Capital USA · Feb 2026</span>
      </div>
    </div>
  );
}
