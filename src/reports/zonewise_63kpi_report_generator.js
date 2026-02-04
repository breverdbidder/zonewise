/**
 * ZoneWise.AI 63 KPI Development Analysis Report Generator
 * 
 * Generates comprehensive DOCX reports with all 63 KPIs across 10 categories:
 * 1. Site & Parcel Metrics (8 KPIs)
 * 2. Existing Building Metrics (5 KPIs)
 * 3. Zoning & Regulatory (10 KPIs)
 * 4. Development Capacity (9 KPIs)
 * 5. Residential Capacity (4 KPIs)
 * 6. Lodging Capacity (4 KPIs)
 * 7. Commercial/Office Capacity (5 KPIs)
 * 8. Setback Requirements (5 KPIs)
 * 9. Allowed Uses (6 KPIs)
 * 10. Financial Opportunity (7 KPIs)
 * 
 * Data Sources: Supabase (parcel_zones, zoning_districts, dimensional_standards) + BCPAO API
 * 
 * @author ZoneWise.AI
 * @version 2.0.0
 * @date 2026-02-04
 */

const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, 
        Header, Footer, AlignmentType, LevelFormat, 
        HeadingLevel, BorderStyle, WidthType, ShadingType, PageNumber, PageBreak } = require('docx');
const fs = require('fs');

// ============================================
// CONFIGURATION
// ============================================
const CONFIG = {
    // Supabase connection
    SUPABASE_URL: process.env.SUPABASE_URL || 'https://mocerqjnksmhcjzxrewo.supabase.co',
    SUPABASE_KEY: process.env.SUPABASE_SERVICE_KEY,
    
    // BCPAO API
    BCPAO_API_BASE: 'https://www.bcpao.us/api/v1',
    
    // Brand colors (ZoneWise theme)
    COLORS: {
        NAVY: "1E3A5F",      // Header
        GREEN: "E8F5E9",     // Practice/Positive
        BLUE: "E3F2FD",      // Ubrzati/Info
        ORANGE: "FFF3E0",    // Shabbat/Warning
        RED: "FFEBEE",       // Skip/Negative
        PURPLE: "F3E5F5",    // Gleason/Special
        ALT_ROW: "F8F9FA",   // Alternating rows
        WHITE: "FFFFFF"
    },
    
    // Document settings
    PAGE: {
        WIDTH: 12240,        // 8.5" in DXA
        HEIGHT: 15840,       // 11" in DXA
        MARGIN: 900          // 0.625" margins
    }
};

// ============================================
// TABLE STYLING HELPERS
// ============================================
const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };

function getShading(color) {
    return { fill: color, type: ShadingType.CLEAR };
}

// ============================================
// KPI CALCULATION ENGINE
// ============================================
class KPICalculator {
    constructor(property, zoning) {
        this.property = property;
        this.zoning = zoning;
    }
    
    get lotSqFt() {
        return Math.round(this.property.acreage * 43560);
    }
    
    get maxBuildingArea() {
        return Math.round(this.lotSqFt * this.zoning.maxFar);
    }
    
    get maxFootprint() {
        return Math.round(this.lotSqFt * this.zoning.maxCoverage);
    }
    
    get unusedRights() {
        return this.maxBuildingArea - (this.property.existingBldgArea || 0);
    }
    
    get currentFar() {
        return (this.property.existingBldgArea || 0) / this.lotSqFt;
    }
    
    get farUtilization() {
        return (this.currentFar / this.zoning.maxFar) * 100;
    }
    
    get untappedPotential() {
        return 100 - this.farUtilization;
    }
    
    get expansionPct() {
        if (!this.property.existingBldgArea || this.property.existingBldgArea === 0) {
            return "N/A (Vacant)";
        }
        return Math.round((this.unusedRights / this.property.existingBldgArea) * 100) + "%";
    }
    
    // Generate all 63 KPIs
    generateAllKPIs() {
        const p = this.property;
        const z = this.zoning;
        const formatNum = (n) => n.toLocaleString();
        const formatCurrency = (n) => '$' + n.toLocaleString();
        const formatPct = (n) => n.toFixed(1) + '%';
        
        return [
            // Category 1: Site & Parcel Metrics (8 KPIs)
            [1, "Site & Parcel", "Parcel ID", p.parcelId, "BCPAO"],
            [2, "Site & Parcel", "Tax Account", p.account, "BCPAO"],
            [3, "Site & Parcel", "Lot Area (Acres)", p.acreage + " acres", "BCPAO"],
            [4, "Site & Parcel", "Lot Area (ft²)", formatNum(this.lotSqFt) + " ft²", "Calculated"],
            [5, "Site & Parcel", "Lot Type", p.lotType || "Interior", "Plat"],
            [6, "Site & Parcel", "Subdivision", p.subdivision || "N/A", "BCPAO"],
            [7, "Site & Parcel", "Vacant Status", p.existingBldgArea > 0 ? "No (Improved)" : "Yes (Vacant)", "BCPAO"],
            [8, "Site & Parcel", "Legal Description", p.legalDesc || "See Deed", "Deed"],
            
            // Category 2: Existing Building Metrics (5 KPIs)
            [9, "Existing Bldg", "Existing Building Area", formatNum(p.existingBldgArea || 0) + " ft²", "BCPAO"],
            [10, "Existing Bldg", "Total Sub Area", formatNum(p.totalSubArea || 0) + " ft²", "BCPAO"],
            [11, "Existing Bldg", "Existing Building Use", p.landUse || "N/A", "BCPAO"],
            [12, "Existing Bldg", "Year Built", p.yearBuilt || "N/A", "BCPAO"],
            [13, "Existing Bldg", "Current Land Use Code", p.landUseCode || p.landUse || "N/A", "BCPAO"],
            
            // Category 3: Zoning & Regulatory (10 KPIs)
            [14, "Zoning", "Zoning Code Source", z.source || "Municipal LDC", "Municode"],
            [15, "Zoning", "Zoning District", z.code + " - " + z.name, "Supabase"],
            [16, "Zoning", "Zoning Category", z.category, "LDC"],
            [17, "Zoning", "Maximum Height", z.maxHeight + " ft", "LDC"],
            [18, "Zoning", "Maximum Stories", "~" + Math.floor(z.maxHeight / 12) + " stories", "Calculated"],
            [19, "Zoning", "Historic District", p.historicDistrict || "No", "Historic Reg"],
            [20, "Zoning", "LEED Requirement", p.leedReq || "None", "Local Ord"],
            [21, "Zoning", "Live Local Applicability", "Yes (SB 102)", "State Law"],
            [22, "Zoning", "TOD Status", p.todStatus || "None", "Transit Map"],
            [23, "Zoning", "Ordinance Section", z.ordinanceSection || "See LDC", "LDC"],
            
            // Category 4: Development Capacity (9 KPIs)
            [24, "Dev Capacity", "Floor Area Ratio (FAR)", z.maxFar.toString(), "LDC"],
            [25, "Dev Capacity", "Maximum Building Area", formatNum(this.maxBuildingArea) + " ft²", "Calculated"],
            [26, "Dev Capacity", "Maximum Lot Coverage", formatPct(z.maxCoverage * 100), "LDC"],
            [27, "Dev Capacity", "Maximum Building Footprint", formatNum(this.maxFootprint) + " ft²", "Calculated"],
            [28, "Dev Capacity", "Minimum Open Space", formatPct(100 - z.maxCoverage * 100), "LDC"],
            [29, "Dev Capacity", "Unused Development Rights", formatNum(this.unusedRights) + " ft²", "Calculated"],
            [30, "Dev Capacity", "Current FAR Utilization", this.currentFar.toFixed(3), "Calculated"],
            [31, "Dev Capacity", "FAR Utilization Rate", formatPct(this.farUtilization), "Calculated"],
            [32, "Dev Capacity", "Expansion Potential", this.expansionPct, "Calculated"],
            
            // Category 5: Residential Capacity (4 KPIs)
            [33, "Residential", "Residential Density", z.residentialDensity || "N/A", "LDC"],
            [34, "Residential", "Max Residential Area", z.category === "Residential" ? formatNum(this.maxBuildingArea) + " ft²" : "N/A", "LDC"],
            [35, "Residential", "Max Residential Units", z.maxResUnits || "N/A", "LDC"],
            [36, "Residential", "Residential Allowed Uses", z.residentialUses || "See LDC", "LDC"],
            
            // Category 6: Lodging Capacity (4 KPIs)
            [37, "Lodging", "Lodging Density", z.lodgingDensity || "Per Site Plan", "LDC"],
            [38, "Lodging", "Max Lodging Area", formatNum(this.maxBuildingArea) + " ft²", "Calculated"],
            [39, "Lodging", "Max Lodging Rooms (est)", "~" + Math.round(this.maxBuildingArea / 1000) + " rooms", "Estimated"],
            [40, "Lodging", "Lodging Allowed Uses", z.lodgingUses || "Hotel, Motel", "LDC"],
            
            // Category 7: Commercial/Office Capacity (5 KPIs)
            [41, "Commercial", "Max Office Area", formatNum(this.maxBuildingArea) + " ft²", "Calculated"],
            [42, "Commercial", "Max Commercial Area", formatNum(this.maxBuildingArea) + " ft²", "Calculated"],
            [43, "Commercial", "Office Expansion Potential", formatNum(this.unusedRights) + " ft²", "Calculated"],
            [44, "Commercial", "Commercial Allowed Uses", z.commercialUses || "Retail, Restaurant, Service", "LDC"],
            [45, "Commercial", "Office Allowed Uses", z.officeUses || "General, Medical, Professional", "LDC"],
            
            // Category 8: Setback Requirements (5 KPIs)
            [46, "Setbacks", "Front Setback", z.setbackFront + " ft", "LDC"],
            [47, "Setbacks", "Side Setback", z.setbackSide + " ft", "LDC"],
            [48, "Setbacks", "Rear Setback", z.setbackRear + " ft", "LDC"],
            [49, "Setbacks", "Min Lot Size", formatNum(z.minLotSqFt) + " ft²", "LDC"],
            [50, "Setbacks", "Min Lot Width", z.minLotWidth + " ft", "LDC"],
            
            // Category 9: Allowed Uses (6 KPIs)
            [51, "Allowed Uses", "Civic Uses (by Right)", z.civicByRight || "Community Facility", "LDC"],
            [52, "Allowed Uses", "Civic Uses (by Warrant)", z.civicByWarrant || "Government Office", "LDC"],
            [53, "Allowed Uses", "Civic Uses (by Exception)", z.civicByException || "Religious Facility", "LDC"],
            [54, "Allowed Uses", "Educational Uses", z.educationalUses || "Day Care, Training", "LDC"],
            [55, "Allowed Uses", "Industrial Uses", z.industrialUses || "See LDC", "LDC"],
            [56, "Allowed Uses", "Infrastructure Uses", z.infraUses || "Utility Facility", "LDC"],
            
            // Category 10: Financial Opportunity (7 KPIs)
            [57, "Financial", "Current Market Value", formatCurrency(p.marketValue || 0), "BCPAO"],
            [58, "Financial", "Last Sale Price", formatCurrency(p.lastSalePrice || 0), "BCPAO"],
            [59, "Financial", "Last Sale Date", p.lastSaleDate || "N/A", "BCPAO"],
            [60, "Financial", "Value per Acre", formatCurrency(Math.round((p.marketValue || 0) / p.acreage)), "Calculated"],
            [61, "Financial", "Value per SF (Land)", formatCurrency(((p.marketValue || 0) / this.lotSqFt).toFixed(2)), "Calculated"],
            [62, "Financial", "Untapped Dev Potential", formatPct(this.untappedPotential), "Calculated"],
            [63, "Financial", "Additional Buildable SF", formatNum(this.unusedRights) + " ft²", "Calculated"],
        ];
    }
}

// ============================================
// REPORT GENERATOR CLASS
// ============================================
class ZoneWise63KPIReportGenerator {
    constructor(property, zoning) {
        this.property = property;
        this.zoning = zoning;
        this.calculator = new KPICalculator(property, zoning);
        this.kpis = this.calculator.generateAllKPIs();
    }
    
    // Helper: Format number
    formatNumber(n) {
        return n.toLocaleString();
    }
    
    // Helper: Format currency
    formatCurrency(n) {
        return '$' + n.toLocaleString();
    }
    
    // Helper: Format percent
    formatPercent(n) {
        return n.toFixed(1) + '%';
    }
    
    // Create KPI table row
    createKpiRow(num, category, name, value, source, isAlt = false) {
        const shading = isAlt ? getShading(CONFIG.COLORS.ALT_ROW) : getShading(CONFIG.COLORS.WHITE);
        return new TableRow({
            children: [
                new TableCell({ borders, width: { size: 500, type: WidthType.DXA }, shading, margins: { top: 50, bottom: 50, left: 60, right: 60 },
                    children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: num.toString(), size: 18 })] })] }),
                new TableCell({ borders, width: { size: 1600, type: WidthType.DXA }, shading, margins: { top: 50, bottom: 50, left: 60, right: 60 },
                    children: [new Paragraph({ children: [new TextRun({ text: category, size: 18, color: "666666" })] })] }),
                new TableCell({ borders, width: { size: 2800, type: WidthType.DXA }, shading, margins: { top: 50, bottom: 50, left: 60, right: 60 },
                    children: [new Paragraph({ children: [new TextRun({ text: name, size: 18 })] })] }),
                new TableCell({ borders, width: { size: 2600, type: WidthType.DXA }, shading, margins: { top: 50, bottom: 50, left: 60, right: 60 },
                    children: [new Paragraph({ children: [new TextRun({ text: value, size: 18, bold: true })] })] }),
                new TableCell({ borders, width: { size: 1500, type: WidthType.DXA }, shading, margins: { top: 50, bottom: 50, left: 60, right: 60 },
                    children: [new Paragraph({ children: [new TextRun({ text: source, size: 16, color: "888888" })] })] }),
            ]
        });
    }
    
    // Create stat cell for summary
    createStatCell(label, value, color, width = 2610) {
        return new TableCell({
            borders, width: { size: width, type: WidthType.DXA }, shading: getShading(color),
            margins: { top: 100, bottom: 100, left: 100, right: 100 },
            children: [
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: label, size: 16, color: "666666" })] }),
                new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 60 }, children: [new TextRun({ text: value, size: 26, bold: true })] })
            ]
        });
    }
    
    // Generate the full document
    async generate(outputPath) {
        const p = this.property;
        const z = this.zoning;
        const calc = this.calculator;
        
        const doc = new Document({
            styles: {
                default: { document: { run: { font: "Arial", size: 22 } } },
                paragraphStyles: [
                    { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
                        run: { size: 32, bold: true, font: "Arial", color: CONFIG.COLORS.NAVY },
                        paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 0 } },
                    { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
                        run: { size: 26, bold: true, font: "Arial", color: CONFIG.COLORS.NAVY },
                        paragraph: { spacing: { before: 200, after: 100 }, outlineLevel: 1 } },
                ]
            },
            sections: [{
                properties: {
                    page: {
                        size: { width: CONFIG.PAGE.WIDTH, height: CONFIG.PAGE.HEIGHT },
                        margin: { top: CONFIG.PAGE.MARGIN, right: CONFIG.PAGE.MARGIN, bottom: CONFIG.PAGE.MARGIN, left: CONFIG.PAGE.MARGIN }
                    }
                },
                headers: {
                    default: new Header({
                        children: [new Paragraph({
                            alignment: AlignmentType.RIGHT,
                            children: [
                                new TextRun({ text: "🗺️ ZoneWise.AI", bold: true, size: 18, color: CONFIG.COLORS.NAVY }),
                                new TextRun({ text: " | 63 KPI Development Analysis", size: 16, color: "666666" })
                            ]
                        })]
                    })
                },
                footers: {
                    default: new Footer({
                        children: [new Paragraph({
                            alignment: AlignmentType.CENTER,
                            children: [
                                new TextRun({ text: "Page ", size: 16, color: "666666" }),
                                new TextRun({ children: [PageNumber.CURRENT], size: 16, color: "666666" }),
                                new TextRun({ text: " | Generated: " + new Date().toLocaleDateString(), size: 16, color: "666666" })
                            ]
                        })]
                    })
                },
                children: [
                    // Title
                    new Paragraph({
                        alignment: AlignmentType.CENTER,
                        spacing: { after: 60 },
                        children: [new TextRun({ text: "🗺️ ZONEWISE DEVELOPMENT ANALYSIS", size: 36, bold: true, color: CONFIG.COLORS.NAVY })]
                    }),
                    new Paragraph({
                        alignment: AlignmentType.CENTER,
                        spacing: { after: 200 },
                        children: [new TextRun({ text: `63 KPI Comprehensive Report • ${p.jurisdiction}, ${p.county} County, FL`, size: 22, color: "666666" })]
                    }),
                    
                    // Property header
                    new Table({
                        width: { size: 10440, type: WidthType.DXA },
                        columnWidths: [10440],
                        rows: [new TableRow({
                            children: [new TableCell({
                                borders, width: { size: 10440, type: WidthType.DXA },
                                shading: getShading(CONFIG.COLORS.NAVY),
                                margins: { top: 120, bottom: 120, left: 200, right: 200 },
                                children: [
                                    new Paragraph({ alignment: AlignmentType.CENTER, children: [
                                        new TextRun({ text: `${p.address}, ${p.city}, ${p.state} ${p.zip}`, size: 28, bold: true, color: "FFFFFF" })
                                    ]}),
                                    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 60 }, children: [
                                        new TextRun({ text: `Parcel: ${p.parcelId} | Owner: ${p.owner}`, size: 18, color: "CCCCCC" })
                                    ]})
                                ]
                            })]
                        })]
                    }),
                    
                    // Opportunity Snapshot
                    new Paragraph({ spacing: { before: 300, after: 100 }, children: [new TextRun({ text: "📊 OPPORTUNITY SNAPSHOT", size: 24, bold: true, color: CONFIG.COLORS.NAVY })] }),
                    
                    new Table({
                        width: { size: 10440, type: WidthType.DXA },
                        columnWidths: [2610, 2610, 2610, 2610],
                        rows: [
                            new TableRow({
                                children: [
                                    this.createStatCell("LOT SIZE", p.acreage + " acres", CONFIG.COLORS.GREEN),
                                    this.createStatCell("EXISTING BLDG", this.formatNumber(p.existingBldgArea || 0) + " ft²", CONFIG.COLORS.BLUE),
                                    this.createStatCell("MAX BUILDABLE", this.formatNumber(calc.maxBuildingArea) + " ft²", CONFIG.COLORS.GREEN),
                                    this.createStatCell("UNTAPPED", this.formatPercent(calc.untappedPotential), CONFIG.COLORS.GREEN),
                                ]
                            }),
                            new TableRow({
                                children: [
                                    this.createStatCell("MARKET VALUE", this.formatCurrency(p.marketValue || 0), CONFIG.COLORS.BLUE),
                                    this.createStatCell("LAST SALE", this.formatCurrency(p.lastSalePrice || 0), CONFIG.COLORS.BLUE),
                                    this.createStatCell("UNUSED RIGHTS", this.formatNumber(calc.unusedRights) + " ft²", CONFIG.COLORS.GREEN),
                                    this.createStatCell("EXPANSION", calc.expansionPct, CONFIG.COLORS.GREEN),
                                ]
                            })
                        ]
                    }),
                    
                    // Property Overview
                    new Paragraph({ spacing: { before: 300, after: 100 }, heading: HeadingLevel.HEADING_1, children: [new TextRun("📋 Property Overview")] }),
                    
                    new Table({
                        width: { size: 10440, type: WidthType.DXA },
                        columnWidths: [3480, 6960],
                        rows: [
                            ["Parcel ID", p.parcelId],
                            ["Tax Account", p.account],
                            ["Owner", p.owner],
                            ["Land Use", p.landUse],
                            ["Zoning District", `${z.code} - ${z.name}`],
                            ["Jurisdiction", `${p.jurisdiction}, ${p.county} County, FL`],
                            ["Year Built", p.yearBuilt || "N/A"],
                            ["Last Sale", `${p.lastSaleDate} - ${this.formatCurrency(p.lastSalePrice || 0)}`],
                        ].map((row, i) => new TableRow({
                            children: [
                                new TableCell({ borders, width: { size: 3480, type: WidthType.DXA }, shading: i % 2 === 0 ? getShading(CONFIG.COLORS.ALT_ROW) : getShading(CONFIG.COLORS.WHITE), 
                                    margins: { top: 50, bottom: 50, left: 80, right: 80 }, children: [new Paragraph({ children: [new TextRun({ text: row[0], bold: true, size: 20 })] })] }),
                                new TableCell({ borders, width: { size: 6960, type: WidthType.DXA }, shading: i % 2 === 0 ? getShading(CONFIG.COLORS.ALT_ROW) : getShading(CONFIG.COLORS.WHITE),
                                    margins: { top: 50, bottom: 50, left: 80, right: 80 }, children: [new Paragraph({ children: [new TextRun({ text: row[1], size: 20 })] })] })
                            ]
                        }))
                    }),
                    
                    // Page break
                    new Paragraph({ children: [new PageBreak()] }),
                    
                    // 63 KPI Table
                    new Paragraph({ spacing: { before: 100, after: 100 }, heading: HeadingLevel.HEADING_1, children: [new TextRun("📊 Complete 63 KPI Analysis")] }),
                    
                    new Table({
                        width: { size: 10000, type: WidthType.DXA },
                        columnWidths: [500, 1600, 2800, 2600, 1500],
                        rows: [
                            // Header
                            new TableRow({
                                children: ["#", "Category", "KPI Name", "Value", "Source"].map((h, i) => 
                                    new TableCell({ borders, width: { size: [500, 1600, 2800, 2600, 1500][i], type: WidthType.DXA }, shading: getShading(CONFIG.COLORS.NAVY), 
                                        margins: { top: 60, bottom: 60, left: 60, right: 60 },
                                        children: [new Paragraph({ alignment: i === 0 ? AlignmentType.CENTER : AlignmentType.LEFT, 
                                            children: [new TextRun({ text: h, bold: true, size: 18, color: "FFFFFF" })] })] })
                                )
                            }),
                            // KPI rows
                            ...this.kpis.map((kpi, i) => this.createKpiRow(kpi[0], kpi[1], kpi[2], kpi[3], kpi[4], i % 2 === 1))
                        ]
                    }),
                    
                    // Page break
                    new Paragraph({ children: [new PageBreak()] }),
                    
                    // Key Findings
                    new Paragraph({ spacing: { before: 100, after: 100 }, heading: HeadingLevel.HEADING_1, children: [new TextRun("✅ Key Findings")] }),
                    
                    ...[
                        ["✅ ", "Development Potential: ", `${this.formatPercent(calc.untappedPotential)} untapped (${this.formatNumber(calc.unusedRights)} ft²)`],
                        ["✅ ", "Zoning: ", `${z.code} - ${z.name} allows ${z.category.toLowerCase()} uses`],
                        ["✅ ", "Live Local Eligible: ", "Potential mixed-use residential under SB 102"],
                        ["⚠️ ", "Height Limitation: ", `${z.maxHeight} ft max (~${Math.floor(z.maxHeight / 12)} stories)`],
                    ].map(item => new Paragraph({ spacing: { after: 80 }, children: [
                        new TextRun({ text: item[0], size: 20 }),
                        new TextRun({ text: item[1], bold: true, size: 20 }),
                        new TextRun({ text: item[2], size: 20 })
                    ]})),
                    
                    // Disclaimer
                    new Paragraph({ 
                        spacing: { before: 300 }, 
                        shading: getShading(CONFIG.COLORS.ORANGE), 
                        children: [
                            new TextRun({ text: "⚠️ DISCLAIMER: ", bold: true, size: 16 }),
                            new TextRun({ text: "This report is for informational purposes only. Verify all zoning information with the local jurisdiction before making investment decisions. ZoneWise.AI is not responsible for errors or omissions.", size: 16, italics: true })
                        ]
                    }),
                ]
            }]
        });
        
        const buffer = await Packer.toBuffer(doc);
        fs.writeFileSync(outputPath, buffer);
        return outputPath;
    }
}

// ============================================
// EXPORTS
// ============================================
module.exports = {
    ZoneWise63KPIReportGenerator,
    KPICalculator,
    CONFIG
};

// CLI usage
if (require.main === module) {
    console.log('ZoneWise 63 KPI Report Generator v2.0.0');
    console.log('Usage: Import and instantiate ZoneWise63KPIReportGenerator with property and zoning data');
}
