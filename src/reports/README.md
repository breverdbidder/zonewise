# ZoneWise.AI Report Generators

## 63 KPI Development Analysis Report

The flagship ZoneWise report template providing comprehensive development analysis across 63 Key Performance Indicators in 10 categories.

### Files

| File | Description |
|------|-------------|
| `zonewise_63kpi_report_generator.js` | Main report generator (Node.js/docx) |
| `zonewise_63kpi_template.json` | Template configuration with all 63 KPIs |

### Categories

| # | Category | KPIs | Description |
|---|----------|------|-------------|
| 1 | Site & Parcel Metrics | 8 | Parcel ID, lot area, frontage, legal description |
| 2 | Existing Building | 5 | Building area, use, year built |
| 3 | Zoning & Regulatory | 10 | District, FAR, height limits, overlays |
| 4 | Development Capacity | 9 | Max area, unused rights, utilization |
| 5 | Residential Capacity | 4 | Density, max units, allowed uses |
| 6 | Lodging Capacity | 4 | Hotel density, max rooms |
| 7 | Commercial/Office | 5 | Max area, expansion potential |
| 8 | Setback Requirements | 5 | Front, side, rear, water setbacks |
| 9 | Allowed Uses | 6 | Civic, educational, infrastructure |
| 10 | Financial Opportunity | 7 | Utilization %, untapped potential |

### Usage

```javascript
const { ZoneWise63KPIReportGenerator } = require('./zonewise_63kpi_report_generator');

const property = {
    parcelId: "28-38-31-54-B-54",
    address: "2715 GARDEN ST",
    city: "MALABAR",
    // ... other fields
};

const zoning = {
    code: "CG",
    name: "Commercial General",
    maxFar: 0.5,
    // ... other fields
};

const generator = new ZoneWise63KPIReportGenerator(property, zoning);
await generator.generate('/output/report.docx');
```

### Data Sources

1. **Supabase** - `parcel_zones`, `zoning_districts`, `dimensional_standards`
2. **BCPAO API** - Property details, sales history
3. **Municode** - Zoning ordinances
4. **GIS Portal** - Parcel geometry

### Dependencies

```bash
npm install docx
```

### Version History

- **v2.0.0** (2026-02-04): Full 63 KPI implementation with Supabase integration
- **v1.0.0** (2026-02-01): Initial template from 169 E Flagler analysis

---
*ZoneWise.AI - USA Real Estate Decoded!*
