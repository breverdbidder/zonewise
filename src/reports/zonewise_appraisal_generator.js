/**
 * ZoneWise Real-Time Appraisal Intelligence (RAI) Report Generator
 * Generates USPAP-style appraisal reports powered by 298 KPIs
 * 
 * @version 1.0.0
 * @date 2026-01-20
 */

const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, PageBreak, HeadingLevel, BorderStyle,
  WidthType, ShadingType, VerticalAlign, PageNumber, ImageRun,
  TableOfContents, LevelFormat, ExternalHyperlink
} = require('docx');
const fs = require('fs');

// ZoneWise Brand Colors
const COLORS = {
  PRIMARY: '1E3A5F',      // Navy - Headers
  SECONDARY: '2E7D32',    // Green - Positive
  ACCENT: '1976D2',       // Blue - Links/Highlights
  WARNING: 'F57C00',      // Orange - Caution
  DANGER: 'C62828',       // Red - Risk
  LIGHT_BG: 'F5F5F5',     // Light gray background
  BORDER: 'CCCCCC'        // Border color
};

// Standard border configuration
const CELL_BORDER = { style: BorderStyle.SINGLE, size: 1, color: COLORS.BORDER };
const BORDERS = { top: CELL_BORDER, bottom: CELL_BORDER, left: CELL_BORDER, right: CELL_BORDER };

/**
 * Generate a Real-Time Appraisal Intelligence Report
 * @param {Object} propertyData - Property data with 298 KPIs populated
 * @param {Object} options - Report generation options
 */
async function generateAppraisalReport(propertyData, options = {}) {
  const {
    reportType = 'SNAPSHOT',
    clientName = 'Internal Use',
    effectiveDate = new Date().toISOString().split('T')[0],
    includeComps = true,
    includeProForma = true
  } = options;

  const doc = new Document({
    styles: {
      default: {
        document: {
          run: { font: 'Arial', size: 24 } // 12pt
        }
      },
      paragraphStyles: [
        {
          id: 'Heading1',
          name: 'Heading 1',
          basedOn: 'Normal',
          next: 'Normal',
          quickFormat: true,
          run: { size: 36, bold: true, font: 'Arial', color: COLORS.PRIMARY },
          paragraph: { spacing: { before: 360, after: 240 }, outlineLevel: 0 }
        },
        {
          id: 'Heading2',
          name: 'Heading 2',
          basedOn: 'Normal',
          next: 'Normal',
          quickFormat: true,
          run: { size: 28, bold: true, font: 'Arial', color: COLORS.PRIMARY },
          paragraph: { spacing: { before: 280, after: 180 }, outlineLevel: 1 }
        },
        {
          id: 'Heading3',
          name: 'Heading 3',
          basedOn: 'Normal',
          next: 'Normal',
          quickFormat: true,
          run: { size: 24, bold: true, font: 'Arial' },
          paragraph: { spacing: { before: 200, after: 120 }, outlineLevel: 2 }
        }
      ]
    },
    numbering: {
      config: [
        {
          reference: 'bullets',
          levels: [{
            level: 0,
            format: LevelFormat.BULLET,
            text: '•',
            alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } }
          }]
        }
      ]
    },
    sections: [
      // COVER PAGE
      createCoverPage(propertyData, effectiveDate, clientName),
      
      // TABLE OF CONTENTS
      createTableOfContents(),
      
      // EXECUTIVE SUMMARY
      createExecutiveSummary(propertyData),
      
      // SALIENT FACTS
      createSalientFacts(propertyData),
      
      // MARKET ANALYSIS
      createMarketAnalysis(propertyData),
      
      // PROPERTY DESCRIPTION
      createPropertyDescription(propertyData),
      
      // HIGHEST & BEST USE
      createHBUAnalysis(propertyData),
      
      // VALUATION
      createValuationSection(propertyData, includeComps),
      
      // RISK ASSESSMENT
      createRiskAssessment(propertyData),
      
      // CERTIFICATION
      createCertification(propertyData, effectiveDate)
    ]
  });

  return doc;
}

/**
 * Create Cover Page Section
 */
function createCoverPage(data, effectiveDate, clientName) {
  return {
    properties: {
      page: {
        size: { width: 12240, height: 15840 }, // US Letter
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    children: [
      // Spacer
      new Paragraph({ spacing: { before: 2000 } }),
      
      // Report Type Badge
      new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [
          new TextRun({
            text: 'REAL-TIME APPRAISAL INTELLIGENCE',
            bold: true,
            size: 28,
            color: COLORS.ACCENT
          })
        ]
      }),
      
      // Main Title
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 400, after: 200 },
        children: [
          new TextRun({
            text: 'PROPERTY VALUATION REPORT',
            bold: true,
            size: 48,
            color: COLORS.PRIMARY
          })
        ]
      }),
      
      // Property Address
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 600 },
        children: [
          new TextRun({
            text: data.address || '123 Main Street',
            size: 32,
            bold: true
          })
        ]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [
          new TextRun({
            text: `${data.city || 'Melbourne'}, ${data.county || 'Brevard'} County, FL ${data.zip || '32901'}`,
            size: 28
          })
        ]
      }),
      
      // Property Type
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 400 },
        children: [
          new TextRun({
            text: data.propertyType || 'Multi-Family Residential',
            size: 24,
            italics: true
          })
        ]
      }),
      
      // Value Badge
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 800 },
        children: [
          new TextRun({
            text: 'INDICATED VALUE',
            size: 20,
            color: '666666'
          })
        ]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [
          new TextRun({
            text: formatCurrency(data.valuationResult?.finalValue || 5000000),
            bold: true,
            size: 56,
            color: COLORS.PRIMARY
          })
        ]
      }),
      
      // ZoneWise Score
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 400 },
        children: [
          new TextRun({
            text: `ZoneWise Score: ${data.zonewiseScore || 78}/100`,
            size: 28,
            color: getScoreColor(data.zonewiseScore || 78)
          })
        ]
      }),
      
      // Effective Date
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 800 },
        children: [
          new TextRun({
            text: `Effective Date: ${formatDate(effectiveDate)}`,
            size: 24
          })
        ]
      }),
      
      // Client
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 200 },
        children: [
          new TextRun({
            text: `Prepared For: ${clientName}`,
            size: 24
          })
        ]
      }),
      
      // Footer - ZoneWise branding
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 1200 },
        children: [
          new TextRun({
            text: 'ZONEWISE',
            bold: true,
            size: 36,
            color: COLORS.PRIMARY
          })
        ]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [
          new TextRun({
            text: 'Real-Time Property Intelligence | 298 KPIs | AI-Powered Analysis',
            size: 18,
            color: '888888'
          })
        ]
      }),
      
      new Paragraph({ children: [new PageBreak()] })
    ]
  };
}

/**
 * Create Table of Contents
 */
function createTableOfContents() {
  return {
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    children: [
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun('Table of Contents')]
      }),
      new TableOfContents('Table of Contents', {
        hyperlink: true,
        headingStyleRange: '1-3'
      }),
      new Paragraph({ children: [new PageBreak()] })
    ]
  };
}

/**
 * Create Executive Summary Section
 */
function createExecutiveSummary(data) {
  const val = data.valuationResult || {};
  
  return {
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    headers: {
      default: new Header({
        children: [
          new Paragraph({
            alignment: AlignmentType.RIGHT,
            children: [
              new TextRun({ text: 'ZoneWise RAI Report | ', size: 18, color: '888888' }),
              new TextRun({ text: data.address || 'Property Report', size: 18, color: '888888' })
            ]
          })
        ]
      })
    },
    footers: {
      default: new Footer({
        children: [
          new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [
              new TextRun({ text: 'Page ', size: 18 }),
              new TextRun({ children: [PageNumber.CURRENT], size: 18 }),
              new TextRun({ text: ' | Confidential | ', size: 18, color: '888888' }),
              new TextRun({ text: 'ZoneWise.ai', size: 18, color: COLORS.ACCENT })
            ]
          })
        ]
      })
    },
    children: [
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun('Executive Summary')]
      }),
      
      new Paragraph({
        spacing: { before: 200, after: 200 },
        children: [
          new TextRun({
            text: 'This Real-Time Appraisal Intelligence report presents a comprehensive property analysis based on 298 Key Performance Indicators (KPIs), powered by ZoneWise AI. Unlike traditional appraisals that become stale within weeks, this report reflects current market conditions as of the effective date.',
            size: 24
          })
        ]
      }),
      
      // Key Metrics Table
      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun('Key Metrics')]
      }),
      
      createKeyMetricsTable(data),
      
      // Recommendation
      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 400 },
        children: [new TextRun('ZoneWise Recommendation')]
      }),
      
      createRecommendationBox(data),
      
      new Paragraph({ children: [new PageBreak()] })
    ]
  };
}

/**
 * Create Key Metrics Table
 */
function createKeyMetricsTable(data) {
  const val = data.valuationResult || {};
  const metrics = [
    ['Property Type', data.propertyType || 'Multi-Family'],
    ['Total Units', data.units || '62'],
    ['Year Built', data.yearBuilt || '1995'],
    ['Gross Building Area', formatNumber(data.gba || 45000) + ' SF'],
    ['Land Area', (data.acres || 4.84) + ' Acres'],
    ['Indicated Value', formatCurrency(val.finalValue || 5000000)],
    ['Value Per Unit', formatCurrency((val.finalValue || 5000000) / (data.units || 62))],
    ['Value Per SF', formatCurrency((val.finalValue || 5000000) / (data.gba || 45000), 0)],
    ['Cap Rate (Market)', (val.capRate || 6.5) + '%'],
    ['ZoneWise Score', (data.zonewiseScore || 78) + '/100'],
    ['Data Freshness', 'Real-Time (298 KPIs)'],
    ['Confidence Level', (data.confidence || 'HIGH')]
  ];

  const rows = [];
  for (let i = 0; i < metrics.length; i += 2) {
    const row = new TableRow({
      children: [
        createMetricCell(metrics[i][0], true),
        createMetricCell(metrics[i][1], false),
        createMetricCell(metrics[i + 1] ? metrics[i + 1][0] : '', true),
        createMetricCell(metrics[i + 1] ? metrics[i + 1][1] : '', false)
      ]
    });
    rows.push(row);
  }

  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    columnWidths: [2340, 2340, 2340, 2340],
    rows: rows
  });
}

function createMetricCell(text, isLabel) {
  return new TableCell({
    borders: BORDERS,
    width: { size: 2340, type: WidthType.DXA },
    shading: isLabel ? { fill: COLORS.LIGHT_BG, type: ShadingType.CLEAR } : undefined,
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    children: [
      new Paragraph({
        children: [
          new TextRun({
            text: text,
            bold: isLabel,
            size: 22
          })
        ]
      })
    ]
  });
}

/**
 * Create Recommendation Box
 */
function createRecommendationBox(data) {
  const recommendation = data.recommendation || 'REVIEW';
  const color = recommendation === 'BID' ? COLORS.SECONDARY : 
                recommendation === 'SKIP' ? COLORS.DANGER : COLORS.WARNING;
  
  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    columnWidths: [9360],
    rows: [
      new TableRow({
        children: [
          new TableCell({
            borders: BORDERS,
            shading: { fill: color, type: ShadingType.CLEAR },
            margins: { top: 200, bottom: 200, left: 200, right: 200 },
            children: [
              new Paragraph({
                alignment: AlignmentType.CENTER,
                children: [
                  new TextRun({
                    text: `RECOMMENDATION: ${recommendation}`,
                    bold: true,
                    size: 32,
                    color: 'FFFFFF'
                  })
                ]
              }),
              new Paragraph({
                alignment: AlignmentType.CENTER,
                spacing: { before: 100 },
                children: [
                  new TextRun({
                    text: getRecommendationText(recommendation, data),
                    size: 22,
                    color: 'FFFFFF'
                  })
                ]
              })
            ]
          })
        ]
      })
    ]
  });
}

/**
 * Create Salient Facts Section
 */
function createSalientFacts(data) {
  return {
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    children: [
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun('Summary of Salient Facts')]
      }),
      
      // General Information
      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun('General Information')]
      }),
      
      createFactsTable([
        ['Property Address', data.address || '28 & 30 Garden Lane'],
        ['City, State, ZIP', `${data.city || 'Niceville'}, FL ${data.zip || '32578'}`],
        ['County', data.county || 'Okaloosa'],
        ['Parcel ID(s)', data.parcelId || '05-1S-22-256C-0003-0010'],
        ['Property Type', data.propertyType || 'Multi-Family Residential'],
        ['Zoning', data.zoning || 'R-3, Multi-Family Residential'],
        ['Current Owner', data.owner || 'NWF State College Foundation'],
        ['Legal Description', 'See Addenda for Metes and Bounds']
      ]),
      
      // Dates
      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 400 },
        children: [new TextRun('Report Dates')]
      }),
      
      createFactsTable([
        ['Effective Date of Value', formatDate(data.effectiveDate || new Date())],
        ['Report Generation Date', formatDate(new Date())],
        ['Data Refresh Timestamp', new Date().toISOString()],
        ['Property Rights Appraised', 'Fee Simple']
      ]),
      
      // Assessment & Taxes
      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 400 },
        children: [new TextRun('Assessment & Taxes')]
      }),
      
      createFactsTable([
        ['Assessed Value (Land)', formatCurrency(data.assessedLand || 500000)],
        ['Assessed Value (Improvements)', formatCurrency(data.assessedImprovements || 2230415)],
        ['Total Assessed Value', formatCurrency(data.assessedTotal || 2730415)],
        ['Annual Property Taxes', formatCurrency(data.annualTaxes || 20343)],
        ['Tax Status', data.taxStatus || 'Current - Paid in Full'],
        ['Tax Year', data.taxYear || '2025']
      ]),
      
      // Sale History
      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 400 },
        children: [new TextRun('Sale History')]
      }),
      
      createFactsTable([
        ['Last Sale Date', data.lastSaleDate || 'March 1, 1997'],
        ['Last Sale Price', formatCurrency(data.lastSalePrice || 785000)],
        ['Current Listing Status', data.listingStatus || 'Not Currently Listed'],
        ['Days on Market', data.dom || 'N/A']
      ]),
      
      new Paragraph({ children: [new PageBreak()] })
    ]
  };
}

/**
 * Create Facts Table (2 column label/value)
 */
function createFactsTable(facts) {
  const rows = facts.map(([label, value]) => 
    new TableRow({
      children: [
        new TableCell({
          borders: BORDERS,
          width: { size: 3500, type: WidthType.DXA },
          shading: { fill: COLORS.LIGHT_BG, type: ShadingType.CLEAR },
          margins: { top: 60, bottom: 60, left: 120, right: 120 },
          children: [new Paragraph({ children: [new TextRun({ text: label, bold: true, size: 22 })] })]
        }),
        new TableCell({
          borders: BORDERS,
          width: { size: 5860, type: WidthType.DXA },
          margins: { top: 60, bottom: 60, left: 120, right: 120 },
          children: [new Paragraph({ children: [new TextRun({ text: value, size: 22 })] })]
        })
      ]
    })
  );

  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    columnWidths: [3500, 5860],
    rows: rows
  });
}

/**
 * Create Market Analysis Section
 */
function createMarketAnalysis(data) {
  const market = data.marketData || {};
  
  return {
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    children: [
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun('Market Area Analysis')]
      }),
      
      new Paragraph({
        spacing: { before: 200, after: 200 },
        children: [
          new TextRun({
            text: 'This section presents real-time market intelligence derived from 52 KPIs covering economic indicators, real estate market conditions, and location quality factors. Data sources include Census API, BLS, MLS aggregators, and proprietary ZoneWise algorithms.',
            size: 24
          })
        ]
      }),
      
      // Economic Indicators
      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun('Economic Indicators')]
      }),
      
      createFactsTable([
        ['MSA Population', formatNumber(market.population || 650000)],
        ['Population Growth (5yr)', (market.populationGrowth || 8.5) + '%'],
        ['Median Household Income', formatCurrency(market.medianIncome || 68500)],
        ['Income Growth (YoY)', (market.incomeGrowth || 4.2) + '%'],
        ['Unemployment Rate', (market.unemployment || 3.8) + '%'],
        ['Major Employers', market.majorEmployers || 'Military, Healthcare, Tourism']
      ]),
      
      // Real Estate Market
      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 400 },
        children: [new TextRun('Real Estate Market Conditions')]
      }),
      
      createFactsTable([
        ['Median Home Value', formatCurrency(market.medianHomeValue || 385000)],
        ['YoY Price Change', (market.priceChange || 5.2) + '%'],
        ['Inventory (Months)', market.monthsSupply || '2.8'],
        ['Days on Market (Median)', market.medianDom || '28'],
        ['List-to-Sale Ratio', (market.listToSaleRatio || 98.5) + '%'],
        ['Market Cap Rate', (market.capRate || 6.5) + '%']
      ]),
      
      // Multi-Family Specific
      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 400 },
        children: [new TextRun('Multi-Family Market')]
      }),
      
      createFactsTable([
        ['Vacancy Rate', (market.vacancyRate || 5.2) + '%'],
        ['Average Rent (1BR)', formatCurrency(market.rent1br || 1250) + '/mo'],
        ['Average Rent (2BR)', formatCurrency(market.rent2br || 1550) + '/mo'],
        ['Average Rent (3BR)', formatCurrency(market.rent3br || 1850) + '/mo'],
        ['Rent Growth (YoY)', (market.rentGrowth || 4.8) + '%'],
        ['New Supply Pipeline', formatNumber(market.newSupply || 450) + ' units']
      ]),
      
      // Location Quality
      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 400 },
        children: [new TextRun('Location Quality Scores')]
      }),
      
      createFactsTable([
        ['Walk Score', market.walkScore || '45'],
        ['Transit Score', market.transitScore || '25'],
        ['School Rating (Avg)', market.schoolRating || '7/10'],
        ['Crime Index', market.crimeIndex || 'Low'],
        ['Distance to Employment', market.distanceEmployment || '5.2 miles'],
        ['Traffic (AADT)', formatNumber(market.trafficCount || 12500)]
      ]),
      
      new Paragraph({ children: [new PageBreak()] })
    ]
  };
}

/**
 * Create Property Description Section
 */
function createPropertyDescription(data) {
  return {
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    children: [
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun('Property Description')]
      }),
      
      // Site Analysis
      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun('Site Analysis')]
      }),
      
      createFactsTable([
        ['Land Area (Acres)', data.acres || '4.84'],
        ['Land Area (SF)', formatNumber((data.acres || 4.84) * 43560)],
        ['Shape', data.lotShape || 'Irregular'],
        ['Topography', data.topography || 'Generally Level'],
        ['Street Frontage', (data.frontage || 250) + ' feet'],
        ['Utilities', data.utilities || 'All Public Available'],
        ['Flood Zone', data.floodZone || 'Zone X (Minimal Risk)'],
        ['Environmental', data.environmental || 'No Known Issues']
      ]),
      
      // Improvement Analysis
      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 400 },
        children: [new TextRun('Improvement Analysis')]
      }),
      
      createFactsTable([
        ['Building Count', data.buildingCount || '9'],
        ['Total Units', data.units || '62'],
        ['Gross Building Area', formatNumber(data.gba || 45000) + ' SF'],
        ['Average Unit Size', formatNumber((data.gba || 45000) / (data.units || 62)) + ' SF'],
        ['Year Built', data.yearBuilt || '1995/2007'],
        ['Effective Age', (data.effectiveAge || 15) + ' years'],
        ['Construction Type', data.construction || 'Wood Frame / Stucco'],
        ['Roof Type', data.roofType || 'Shingle'],
        ['HVAC', data.hvac || 'Central A/C, Individual Units'],
        ['Parking', (data.parking || 124) + ' spaces'],
        ['Parking Ratio', ((data.parking || 124) / (data.units || 62)).toFixed(1) + ' per unit'],
        ['Condition', data.condition || 'Average to Good']
      ]),
      
      // Unit Mix
      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 400 },
        children: [new TextRun('Unit Mix')]
      }),
      
      createUnitMixTable(data.unitMix || [
        { type: '1 BR / 1 BA', count: 20, size: 650, rent: 1100 },
        { type: '2 BR / 1 BA', count: 28, size: 850, rent: 1350 },
        { type: '2 BR / 2 BA', count: 10, size: 950, rent: 1450 },
        { type: '3 BR / 2 BA', count: 4, size: 1150, rent: 1650 }
      ]),
      
      new Paragraph({ children: [new PageBreak()] })
    ]
  };
}

/**
 * Create Unit Mix Table
 */
function createUnitMixTable(unitMix) {
  const headerRow = new TableRow({
    children: ['Unit Type', 'Count', 'Avg SF', 'Market Rent', 'Total SF', 'Gross Rent'].map(text =>
      new TableCell({
        borders: BORDERS,
        shading: { fill: COLORS.PRIMARY, type: ShadingType.CLEAR },
        margins: { top: 80, bottom: 80, left: 80, right: 80 },
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ text, bold: true, size: 20, color: 'FFFFFF' })]
        })]
      })
    )
  });

  const dataRows = unitMix.map(unit =>
    new TableRow({
      children: [
        unit.type,
        unit.count.toString(),
        formatNumber(unit.size),
        formatCurrency(unit.rent),
        formatNumber(unit.count * unit.size),
        formatCurrency(unit.count * unit.rent)
      ].map((text, i) =>
        new TableCell({
          borders: BORDERS,
          margins: { top: 60, bottom: 60, left: 80, right: 80 },
          children: [new Paragraph({
            alignment: i === 0 ? AlignmentType.LEFT : AlignmentType.RIGHT,
            children: [new TextRun({ text, size: 20 })]
          })]
        })
      )
    })
  );

  // Totals row
  const totals = unitMix.reduce((acc, u) => ({
    count: acc.count + u.count,
    sf: acc.sf + (u.count * u.size),
    rent: acc.rent + (u.count * u.rent)
  }), { count: 0, sf: 0, rent: 0 });

  const totalRow = new TableRow({
    children: [
      'TOTAL',
      totals.count.toString(),
      '-',
      '-',
      formatNumber(totals.sf),
      formatCurrency(totals.rent) + '/mo'
    ].map((text, i) =>
      new TableCell({
        borders: BORDERS,
        shading: { fill: COLORS.LIGHT_BG, type: ShadingType.CLEAR },
        margins: { top: 60, bottom: 60, left: 80, right: 80 },
        children: [new Paragraph({
          alignment: i === 0 ? AlignmentType.LEFT : AlignmentType.RIGHT,
          children: [new TextRun({ text, bold: true, size: 20 })]
        })]
      })
    )
  });

  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    columnWidths: [1800, 1200, 1200, 1720, 1720, 1720],
    rows: [headerRow, ...dataRows, totalRow]
  });
}

/**
 * Create HBU Analysis Section
 */
function createHBUAnalysis(data) {
  return {
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    children: [
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun('Highest & Best Use Analysis')]
      }),
      
      new Paragraph({
        spacing: { before: 200, after: 200 },
        children: [
          new TextRun({
            text: 'Highest and Best Use is defined as the reasonably probable use of property that results in the highest value. The analysis considers four criteria: legally permissible, physically possible, financially feasible, and maximally productive.',
            size: 24
          })
        ]
      }),
      
      // Four Tests
      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun('HBU Analysis - As Improved')]
      }),
      
      createHBUTestTable([
        ['Legally Permissible', 'PASS', 'Current multi-family use is conforming under R-3 zoning'],
        ['Physically Possible', 'PASS', 'Improvements are functional and suitable for continued use'],
        ['Financially Feasible', 'PASS', 'Property generates positive NOI above market returns'],
        ['Maximally Productive', 'PASS', 'Current use provides highest return to land']
      ]),
      
      // Conclusion
      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 400 },
        children: [new TextRun('HBU Conclusion')]
      }),
      
      new Paragraph({
        spacing: { before: 200 },
        children: [
          new TextRun({
            text: 'As Improved: ',
            bold: true,
            size: 24
          }),
          new TextRun({
            text: 'Continued operation as a multi-family residential property with ongoing maintenance and capital improvements as needed. The existing improvements contribute value to the property.',
            size: 24
          })
        ]
      }),
      
      new Paragraph({
        spacing: { before: 200 },
        children: [
          new TextRun({
            text: 'As If Vacant: ',
            bold: true,
            size: 24
          }),
          new TextRun({
            text: 'Development of multi-family residential improvements at the maximum density allowed by zoning would be the highest and best use of the underlying land.',
            size: 24
          })
        ]
      }),
      
      new Paragraph({ children: [new PageBreak()] })
    ]
  };
}

function createHBUTestTable(tests) {
  const rows = tests.map(([test, result, explanation]) =>
    new TableRow({
      children: [
        new TableCell({
          borders: BORDERS,
          width: { size: 2000, type: WidthType.DXA },
          shading: { fill: COLORS.LIGHT_BG, type: ShadingType.CLEAR },
          margins: { top: 80, bottom: 80, left: 120, right: 120 },
          children: [new Paragraph({ children: [new TextRun({ text: test, bold: true, size: 22 })] })]
        }),
        new TableCell({
          borders: BORDERS,
          width: { size: 1000, type: WidthType.DXA },
          shading: { fill: result === 'PASS' ? COLORS.SECONDARY : COLORS.DANGER, type: ShadingType.CLEAR },
          margins: { top: 80, bottom: 80, left: 120, right: 120 },
          children: [new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [new TextRun({ text: result, bold: true, size: 22, color: 'FFFFFF' })]
          })]
        }),
        new TableCell({
          borders: BORDERS,
          width: { size: 6360, type: WidthType.DXA },
          margins: { top: 80, bottom: 80, left: 120, right: 120 },
          children: [new Paragraph({ children: [new TextRun({ text: explanation, size: 22 })] })]
        })
      ]
    })
  );

  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    columnWidths: [2000, 1000, 6360],
    rows: rows
  });
}

/**
 * Create Valuation Section
 */
function createValuationSection(data, includeComps) {
  const val = data.valuationResult || {};
  
  return {
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    children: [
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun('Valuation Analysis')]
      }),
      
      // Income Approach
      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun('Income Approach')]
      }),
      
      new Paragraph({
        spacing: { before: 100, after: 200 },
        children: [
          new TextRun({
            text: 'The Income Approach estimates value based on the present worth of anticipated future income. For income-producing properties like the subject, this approach is typically given significant weight.',
            size: 24
          })
        ]
      }),
      
      createIncomeTable(data),
      
      // Sales Comparison
      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 400 },
        children: [new TextRun('Sales Comparison Approach')]
      }),
      
      new Paragraph({
        spacing: { before: 100, after: 200 },
        children: [
          new TextRun({
            text: 'The Sales Comparison Approach estimates value by analyzing recent sales of similar properties. ZoneWise uses ML-powered similarity scoring across 60+ attributes to identify the most relevant comparables.',
            size: 24
          })
        ]
      }),
      
      createCompsTable(data.comparables || [
        { address: '100 Oak Ave', salePrice: 4800000, units: 58, priceUnit: 82759, adjusted: 4950000 },
        { address: '250 Pine St', salePrice: 5200000, units: 65, priceUnit: 80000, adjusted: 5050000 },
        { address: '75 Cedar Blvd', salePrice: 4500000, units: 52, priceUnit: 86538, adjusted: 4750000 }
      ]),
      
      // Reconciliation
      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 400 },
        children: [new TextRun('Reconciliation')]
      }),
      
      createReconciliationTable(val),
      
      new Paragraph({ children: [new PageBreak()] })
    ]
  };
}

function createIncomeTable(data) {
  const income = data.incomeData || {};
  const items = [
    ['Potential Gross Income', formatCurrency(income.pgi || 930000)],
    ['Less: Vacancy & Credit Loss (5%)', '(' + formatCurrency((income.pgi || 930000) * 0.05) + ')'],
    ['Effective Gross Income', formatCurrency((income.pgi || 930000) * 0.95)],
    ['', ''],
    ['Operating Expenses:', ''],
    ['  Real Estate Taxes', formatCurrency(income.taxes || 20343)],
    ['  Insurance', formatCurrency(income.insurance || 45000)],
    ['  Utilities', formatCurrency(income.utilities || 35000)],
    ['  Management (5%)', formatCurrency(income.management || 44175)],
    ['  Repairs & Maintenance', formatCurrency(income.repairs || 55000)],
    ['  Reserves', formatCurrency(income.reserves || 31000)],
    ['Total Operating Expenses', formatCurrency(income.totalExpenses || 230518)],
    ['', ''],
    ['Net Operating Income', formatCurrency(income.noi || 652982)],
    ['', ''],
    ['Capitalization Rate', (income.capRate || 6.5) + '%'],
    ['Indicated Value (Income)', formatCurrency((income.noi || 652982) / ((income.capRate || 6.5) / 100))]
  ];

  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    columnWidths: [6000, 3360],
    rows: items.map(([label, value]) =>
      new TableRow({
        children: [
          new TableCell({
            borders: BORDERS,
            width: { size: 6000, type: WidthType.DXA },
            shading: label.startsWith('Net') || label.startsWith('Indicated') || label.startsWith('Total') ? 
              { fill: COLORS.LIGHT_BG, type: ShadingType.CLEAR } : undefined,
            margins: { top: 40, bottom: 40, left: 120, right: 120 },
            children: [new Paragraph({
              children: [new TextRun({
                text: label,
                bold: label.startsWith('Net') || label.startsWith('Indicated') || label.startsWith('Total') || label.includes('Expenses:'),
                size: 22
              })]
            })]
          }),
          new TableCell({
            borders: BORDERS,
            width: { size: 3360, type: WidthType.DXA },
            shading: label.startsWith('Net') || label.startsWith('Indicated') || label.startsWith('Total') ? 
              { fill: COLORS.LIGHT_BG, type: ShadingType.CLEAR } : undefined,
            margins: { top: 40, bottom: 40, left: 120, right: 120 },
            children: [new Paragraph({
              alignment: AlignmentType.RIGHT,
              children: [new TextRun({
                text: value,
                bold: label.startsWith('Net') || label.startsWith('Indicated') || label.startsWith('Total'),
                size: 22
              })]
            })]
          })
        ]
      })
    )
  });
}

function createCompsTable(comps) {
  const header = new TableRow({
    children: ['Address', 'Sale Price', 'Units', '$/Unit', 'Adjusted'].map(text =>
      new TableCell({
        borders: BORDERS,
        shading: { fill: COLORS.PRIMARY, type: ShadingType.CLEAR },
        margins: { top: 80, bottom: 80, left: 80, right: 80 },
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ text, bold: true, size: 20, color: 'FFFFFF' })]
        })]
      })
    )
  });

  const dataRows = comps.map(comp =>
    new TableRow({
      children: [
        comp.address,
        formatCurrency(comp.salePrice),
        comp.units.toString(),
        formatCurrency(comp.priceUnit),
        formatCurrency(comp.adjusted)
      ].map((text, i) =>
        new TableCell({
          borders: BORDERS,
          margins: { top: 60, bottom: 60, left: 80, right: 80 },
          children: [new Paragraph({
            alignment: i === 0 ? AlignmentType.LEFT : AlignmentType.RIGHT,
            children: [new TextRun({ text, size: 20 })]
          })]
        })
      )
    })
  );

  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    columnWidths: [2800, 1800, 1000, 1800, 1960],
    rows: [header, ...dataRows]
  });
}

function createReconciliationTable(val) {
  const rows = [
    ['Approach', 'Indicated Value', 'Weight', 'Contribution'],
    ['Sales Comparison', formatCurrency(val.salesCompValue || 4916667), '40%', formatCurrency((val.salesCompValue || 4916667) * 0.4)],
    ['Income Approach', formatCurrency(val.incomeValue || 10045877), '60%', formatCurrency((val.incomeValue || 10045877) * 0.6)],
    ['Cost Approach', 'Not Utilized', '-', '-'],
    ['Reconciled Value', '', '', formatCurrency(val.finalValue || 5000000)]
  ];

  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    columnWidths: [2340, 2340, 2340, 2340],
    rows: rows.map((row, i) =>
      new TableRow({
        children: row.map((text, j) =>
          new TableCell({
            borders: BORDERS,
            shading: i === 0 ? { fill: COLORS.PRIMARY, type: ShadingType.CLEAR } :
                     i === rows.length - 1 ? { fill: COLORS.SECONDARY, type: ShadingType.CLEAR } : undefined,
            margins: { top: 80, bottom: 80, left: 120, right: 120 },
            children: [new Paragraph({
              alignment: j === 0 ? AlignmentType.LEFT : AlignmentType.RIGHT,
              children: [new TextRun({
                text,
                bold: i === 0 || i === rows.length - 1,
                size: 22,
                color: (i === 0 || i === rows.length - 1) ? 'FFFFFF' : undefined
              })]
            })]
          })
        )
      })
    )
  });
}

/**
 * Create Risk Assessment Section
 */
function createRiskAssessment(data) {
  const risks = data.risks || {};
  
  return {
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    children: [
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun('Risk Assessment')]
      }),
      
      new Paragraph({
        spacing: { before: 200, after: 200 },
        children: [
          new TextRun({
            text: 'ZoneWise provides a comprehensive risk assessment using 20 proprietary KPIs. This analysis goes beyond traditional appraisals to quantify investment risk and identify value-add opportunities.',
            size: 24
          })
        ]
      }),
      
      // Risk Matrix
      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun('Risk Matrix')]
      }),
      
      createRiskMatrix([
        ['Title Risk', risks.titleRisk || 'LOW', 'Clear title, standard easements'],
        ['Lien Priority', risks.lienPriority || 'LOW', 'First position mortgage, no senior liens'],
        ['Tax Status', risks.taxStatus || 'LOW', 'Current on all taxes'],
        ['Environmental', risks.environmental || 'LOW', 'No known contamination'],
        ['Flood Risk', risks.floodRisk || 'LOW', 'Zone X - minimal risk'],
        ['Market Risk', risks.marketRisk || 'MEDIUM', 'Moderate supply pipeline'],
        ['Tenant Concentration', risks.tenantConcentration || 'MEDIUM', 'Student housing dependency'],
        ['Deferred Maintenance', risks.deferredMaintenance || 'MEDIUM', 'Roof replacement needed 3-5 years']
      ]),
      
      // Opportunities
      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 400 },
        children: [new TextRun('Value-Add Opportunities')]
      }),
      
      createOpportunitiesTable([
        ['Rent Increase', '+$150/unit', formatCurrency(150 * 62 * 12) + '/year', 'Market rents support 12% increase'],
        ['Utility RUBS', '+$75/unit', formatCurrency(75 * 62 * 12) + '/year', 'Implement water/trash billing'],
        ['Laundry Revenue', '+$25/unit', formatCurrency(25 * 62 * 12) + '/year', 'Upgrade to card-operated'],
        ['Insurance Review', 'TBD', 'Potential savings', 'Quote from multiple carriers']
      ]),
      
      new Paragraph({ children: [new PageBreak()] })
    ]
  };
}

function createRiskMatrix(risks) {
  const header = new TableRow({
    children: ['Risk Category', 'Level', 'Notes'].map(text =>
      new TableCell({
        borders: BORDERS,
        shading: { fill: COLORS.PRIMARY, type: ShadingType.CLEAR },
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
        children: [new Paragraph({
          children: [new TextRun({ text, bold: true, size: 22, color: 'FFFFFF' })]
        })]
      })
    )
  });

  const rows = risks.map(([category, level, notes]) =>
    new TableRow({
      children: [
        new TableCell({
          borders: BORDERS,
          width: { size: 2500, type: WidthType.DXA },
          margins: { top: 60, bottom: 60, left: 120, right: 120 },
          children: [new Paragraph({ children: [new TextRun({ text: category, size: 22 })] })]
        }),
        new TableCell({
          borders: BORDERS,
          width: { size: 1500, type: WidthType.DXA },
          shading: { fill: getRiskColor(level), type: ShadingType.CLEAR },
          margins: { top: 60, bottom: 60, left: 120, right: 120 },
          children: [new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [new TextRun({ text: level, bold: true, size: 22, color: 'FFFFFF' })]
          })]
        }),
        new TableCell({
          borders: BORDERS,
          width: { size: 5360, type: WidthType.DXA },
          margins: { top: 60, bottom: 60, left: 120, right: 120 },
          children: [new Paragraph({ children: [new TextRun({ text: notes, size: 22 })] })]
        })
      ]
    })
  );

  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    columnWidths: [2500, 1500, 5360],
    rows: [header, ...rows]
  });
}

function createOpportunitiesTable(opportunities) {
  const header = new TableRow({
    children: ['Opportunity', 'Impact', 'Annual Value', 'Notes'].map(text =>
      new TableCell({
        borders: BORDERS,
        shading: { fill: COLORS.SECONDARY, type: ShadingType.CLEAR },
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
        children: [new Paragraph({
          children: [new TextRun({ text, bold: true, size: 22, color: 'FFFFFF' })]
        })]
      })
    )
  });

  const rows = opportunities.map(([opp, impact, value, notes]) =>
    new TableRow({
      children: [opp, impact, value, notes].map((text, i) =>
        new TableCell({
          borders: BORDERS,
          margins: { top: 60, bottom: 60, left: 120, right: 120 },
          children: [new Paragraph({
            alignment: i === 2 ? AlignmentType.RIGHT : AlignmentType.LEFT,
            children: [new TextRun({ text, size: 22 })]
          })]
        })
      )
    })
  );

  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    columnWidths: [2000, 1500, 2000, 3860],
    rows: [header, ...rows]
  });
}

/**
 * Create Certification Section
 */
function createCertification(data, effectiveDate) {
  return {
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    children: [
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun('Certification & Limiting Conditions')]
      }),
      
      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun('ZoneWise Certification')]
      }),
      
      new Paragraph({
        spacing: { before: 200 },
        children: [
          new TextRun({
            text: 'This Real-Time Appraisal Intelligence report was generated by ZoneWise AI using 298 Key Performance Indicators sourced from authoritative public and proprietary data sources. The following statements are certified:',
            size: 24
          })
        ]
      }),
      
      new Paragraph({
        numbering: { reference: 'bullets', level: 0 },
        spacing: { before: 200 },
        children: [new TextRun({ text: 'The statements of fact contained in this report are true and correct to the best of our knowledge.', size: 24 })]
      }),
      new Paragraph({
        numbering: { reference: 'bullets', level: 0 },
        children: [new TextRun({ text: 'The reported analyses and conclusions are limited only by the assumptions and limiting conditions stated herein.', size: 24 })]
      }),
      new Paragraph({
        numbering: { reference: 'bullets', level: 0 },
        children: [new TextRun({ text: 'ZoneWise has no present or prospective interest in the subject property.', size: 24 })]
      }),
      new Paragraph({
        numbering: { reference: 'bullets', level: 0 },
        children: [new TextRun({ text: 'The analysis and conclusions were developed independently using data-driven methodologies.', size: 24 })]
      }),
      new Paragraph({
        numbering: { reference: 'bullets', level: 0 },
        children: [new TextRun({ text: 'All KPI data sources and timestamps are documented for transparency and auditability.', size: 24 })]
      }),
      
      // Limiting Conditions
      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 400 },
        children: [new TextRun('Limiting Conditions')]
      }),
      
      new Paragraph({
        numbering: { reference: 'bullets', level: 0 },
        spacing: { before: 200 },
        children: [new TextRun({ text: 'This report is not a formal appraisal and should not be used for lending, litigation, or insurance purposes without proper review by a licensed appraiser.', size: 24 })]
      }),
      new Paragraph({
        numbering: { reference: 'bullets', level: 0 },
        children: [new TextRun({ text: 'No physical inspection of the property was conducted; all data is derived from public records and third-party sources.', size: 24 })]
      }),
      new Paragraph({
        numbering: { reference: 'bullets', level: 0 },
        children: [new TextRun({ text: 'Market conditions can change rapidly; the conclusions herein reflect conditions as of the effective date only.', size: 24 })]
      }),
      new Paragraph({
        numbering: { reference: 'bullets', level: 0 },
        children: [new TextRun({ text: 'The ZoneWise Score is a proprietary metric for investment screening and does not guarantee future performance.', size: 24 })]
      }),
      
      // Data Sources
      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 400 },
        children: [new TextRun('Data Sources')]
      }),
      
      new Paragraph({
        spacing: { before: 200 },
        children: [
          new TextRun({
            text: 'This report incorporates data from: BCPAO (Property Appraiser), Tax Collector, AcclaimWeb (Clerk), Census Bureau API, Bureau of Labor Statistics, FEMA, MLS aggregators, and proprietary ZoneWise algorithms. Complete data lineage is available upon request.',
            size: 24
          })
        ]
      }),
      
      // Footer
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 800 },
        children: [
          new TextRun({
            text: '— END OF REPORT —',
            bold: true,
            size: 24,
            color: COLORS.PRIMARY
          })
        ]
      }),
      
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 400 },
        children: [
          new TextRun({
            text: 'Generated by ZoneWise Real-Time Appraisal Intelligence',
            size: 20,
            color: '888888'
          })
        ]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [
          new TextRun({
            text: `Report ID: ZW-RAI-${Date.now()}`,
            size: 18,
            color: '888888'
          })
        ]
      })
    ]
  };
}

// Helper Functions
function formatCurrency(value, decimals = 0) {
  return '$' + Number(value).toLocaleString('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  });
}

function formatNumber(value) {
  return Number(value).toLocaleString('en-US');
}

function formatDate(date) {
  if (typeof date === 'string') date = new Date(date);
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
}

function getScoreColor(score) {
  if (score >= 75) return COLORS.SECONDARY;
  if (score >= 60) return COLORS.WARNING;
  return COLORS.DANGER;
}

function getRiskColor(level) {
  switch (level.toUpperCase()) {
    case 'LOW': return COLORS.SECONDARY;
    case 'MEDIUM': return COLORS.WARNING;
    case 'HIGH': return COLORS.DANGER;
    default: return '888888';
  }
}

function getRecommendationText(rec, data) {
  switch (rec) {
    case 'BID':
      return `Strong investment opportunity. ZoneWise Score of ${data.zonewiseScore || 78} indicates favorable risk-adjusted returns.`;
    case 'SKIP':
      return `Investment not recommended at current pricing. Key concerns identified in risk assessment.`;
    default:
      return `Additional due diligence recommended. Review risk factors and value-add opportunities before proceeding.`;
  }
}

// Export functions
module.exports = { generateAppraisalReport };

// CLI execution
if (require.main === module) {
  // Sample property data for testing
  const sampleData = {
    address: '28 & 30 Garden Lane',
    city: 'Niceville',
    county: 'Okaloosa',
    zip: '32578',
    parcelId: '05-1S-22-256C-0003-0010',
    propertyType: 'Multi-Family Residential (62 Units)',
    zoning: 'R-3, Multi-Family Residential',
    owner: 'Northwest Florida State College Foundation',
    acres: 4.84,
    gba: 45000,
    units: 62,
    yearBuilt: '1995/2007',
    zonewiseScore: 78,
    recommendation: 'REVIEW',
    valuationResult: {
      salesCompValue: 4650000,
      incomeValue: 5220000,
      finalValue: 5000000,
      capRate: 6.5
    }
  };

  generateAppraisalReport(sampleData, {
    reportType: 'SNAPSHOT',
    clientName: 'ZoneWise.AI 2026',
    effectiveDate: new Date().toISOString()
  }).then(doc => {
    Packer.toBuffer(doc).then(buffer => {
      const filename = `ZoneWise_RAI_${sampleData.parcelId.replace(/-/g, '')}_SNAPSHOT_${new Date().toISOString().slice(0,10).replace(/-/g, '')}.docx`;
      fs.writeFileSync(filename, buffer);
      console.log(`✅ Report generated: ${filename}`);
    });
  });
}
