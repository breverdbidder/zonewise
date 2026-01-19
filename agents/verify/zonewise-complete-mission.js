#!/usr/bin/env node
/**
 * ZONEWISE COMPLETE MISSION
 * Autonomous 7-hour agent for 100% Brevard County zoning data completion
 * 
 * Run: node zonewise-complete-mission.js
 * 
 * NO HUMAN INTERVENTION REQUIRED
 */

import { generateText } from 'ai';
import { anthropic } from '@ai-sdk/anthropic';
import Firecrawl from '@mendable/firecrawl-js';
import { createClient } from '@supabase/supabase-js';

// ═══════════════════════════════════════════════════════════════════════════════
// CONFIGURATION
// ═══════════════════════════════════════════════════════════════════════════════

const CONFIG = {
  supabase: {
    url: 'https://mocerqjnksmhcjzxrewo.supabase.co',
    key: process.env.SUPABASE_KEY || '${SUPABASE_KEY}'
  },
  firecrawl: {
    key: process.env.FIRECRAWL_API_KEY || '${FIRECRAWL_API_KEY}'
  },
  anthropic: {
    model: 'claude-sonnet-4-5-20250514'
  },
  maxRetries: 5,
  delayBetweenJurisdictions: 5000,
  delayBetweenRequests: 2000
};

// Initialize clients
const supabase = createClient(CONFIG.supabase.url, CONFIG.supabase.key);
const firecrawl = new Firecrawl({ apiKey: CONFIG.firecrawl.key });

// Brevard County Jurisdictions
const JURISDICTIONS = [
  { id: 1, name: 'Melbourne', platform: 'municode', slug: 'melbourne', priority: 1 },
  { id: 2, name: 'Palm Bay', platform: 'municode', slug: 'palm_bay', priority: 1 },
  { id: 3, name: 'Indian Harbour Beach', platform: 'municode', slug: 'indian_harbour_beach', priority: 1 },
  { id: 4, name: 'Titusville', platform: 'municode', slug: 'titusville', priority: 2 },
  { id: 5, name: 'Cocoa', platform: 'municode', slug: 'cocoa', priority: 2 },
  { id: 6, name: 'Satellite Beach', platform: 'municode', slug: 'satellite_beach', priority: 1 },
  { id: 7, name: 'Cocoa Beach', platform: 'municode', slug: 'cocoa_beach', priority: 2 },
  { id: 8, name: 'Rockledge', platform: 'municode', slug: 'rockledge', priority: 1 },
  { id: 9, name: 'West Melbourne', platform: 'municode', slug: 'west_melbourne', priority: 2 },
  { id: 10, name: 'Cape Canaveral', platform: 'municode', slug: 'cape_canaveral', priority: 3 },
  { id: 11, name: 'Indialantic', platform: 'municode', slug: 'indialantic', priority: 3 },
  { id: 12, name: 'Melbourne Beach', platform: 'amlegal', slug: 'melbournebeach', priority: 3 },
  { id: 13, name: 'Unincorporated Brevard', platform: 'elaws', slug: 'brevardcounty', priority: 1 },
  { id: 14, name: 'Malabar', platform: 'municode', slug: 'malabar', priority: 3 },
  { id: 15, name: 'Grant-Valkaria', platform: 'custom', slug: 'grant-valkaria', priority: 3 },
  { id: 16, name: 'Palm Shores', platform: 'custom', slug: 'palm-shores', priority: 3 },
  { id: 17, name: 'Melbourne Village', platform: 'custom', slug: 'melbourne-village', priority: 3 }
];

// ═══════════════════════════════════════════════════════════════════════════════
// LOGGING & PERSISTENCE
// ═══════════════════════════════════════════════════════════════════════════════

const missionStart = new Date();
let missionLog = [];

function log(level, message, data = {}) {
  const entry = {
    timestamp: new Date().toISOString(),
    level,
    message,
    ...data
  };
  missionLog.push(entry);
  
  const emoji = { INFO: '📋', SUCCESS: '✅', WARNING: '⚠️', ERROR: '❌', PHASE: '🚀' }[level] || '•';
  console.log(`${emoji} [${entry.timestamp.split('T')[1].split('.')[0]}] ${message}`);
  if (Object.keys(data).length > 0 && level !== 'INFO') {
    console.log(`   ${JSON.stringify(data)}`);
  }
}

async function checkpoint(jurisdiction, status, details = {}) {
  try {
    await supabase.from('zonewise_verification_log').upsert({
      jurisdiction_id: jurisdiction.id,
      jurisdiction_name: jurisdiction.name,
      status,
      details,
      updated_at: new Date().toISOString()
    }, { onConflict: 'jurisdiction_id' });
  } catch (e) {
    log('WARNING', `Checkpoint save failed: ${e.message}`);
  }
}

async function logAudit(action, jurisdiction_id, district_code, before, after, source) {
  try {
    await supabase.from('zonewise_audit_trail').insert({
      action,
      jurisdiction_id,
      district_code,
      before_value: before,
      after_value: after,
      source_url: source,
      created_at: new Date().toISOString()
    });
  } catch (e) {
    // Silent fail for audit log
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SCRAPING TOOLS
// ═══════════════════════════════════════════════════════════════════════════════

async function scrapeWithRetry(url, options = {}, retries = CONFIG.maxRetries) {
  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      log('INFO', `Scraping (attempt ${attempt}): ${url}`);
      const result = await firecrawl.scrapeUrl(url, {
        formats: ['markdown'],
        waitFor: options.waitFor || 5000,
        timeout: options.timeout || 30000
      });
      await delay(CONFIG.delayBetweenRequests);
      return { success: true, content: result.markdown, url };
    } catch (error) {
      log('WARNING', `Scrape attempt ${attempt} failed: ${error.message}`);
      if (attempt < retries) {
        await delay(attempt * 2000); // Exponential backoff
      }
    }
  }
  return { success: false, error: 'Max retries exceeded', url };
}

async function searchWeb(query) {
  try {
    log('INFO', `Searching: ${query}`);
    const results = await firecrawl.search(query, { limit: 5 });
    await delay(CONFIG.delayBetweenRequests);
    return { success: true, results };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// ═══════════════════════════════════════════════════════════════════════════════
// PLATFORM-SPECIFIC URL BUILDERS
// ═══════════════════════════════════════════════════════════════════════════════

function getZoningUrls(jurisdiction) {
  const { platform, slug, name } = jurisdiction;
  const urls = [];
  
  switch (platform) {
    case 'municode':
      urls.push(
        `https://library.municode.com/fl/${slug}/codes/code_of_ordinances`,
        `https://library.municode.com/fl/${slug}/codes/land_development_code`,
        `https://library.municode.com/fl/${slug}/codes/land_development_regulations_`
      );
      break;
    case 'elaws':
      urls.push(
        `https://${slug}.elaws.us/code`,
        `https://${slug}-fl.elaws.us/code`
      );
      break;
    case 'amlegal':
      urls.push(
        `https://codelibrary.amlegal.com/codes/${slug}/latest/${slug}_fl/0-0-0-1`
      );
      break;
    case 'custom':
      // Will use search-based discovery
      break;
  }
  
  return urls;
}

// ═══════════════════════════════════════════════════════════════════════════════
// AI AGENT FOR DISTRICT EXTRACTION
// ═══════════════════════════════════════════════════════════════════════════════

async function extractDistrictsWithAI(jurisdiction, scrapedContent, existingDistricts) {
  const systemPrompt = `You are a zoning code data extraction expert. Extract ALL zoning districts from the provided content.

EXISTING DISTRICTS IN DATABASE FOR ${jurisdiction.name}:
${existingDistricts.map(d => `- ${d.code}: ${d.name}`).join('\n') || 'None'}

EXTRACT FOR EACH DISTRICT:
1. code (e.g., "R-1", "C-2", "PUD")
2. name (e.g., "Single-Family Residential")
3. category (Residential, Commercial, Industrial, Mixed Use, Agricultural, Other)
4. Dimensional standards if found:
   - min_lot_sqft
   - min_lot_width_ft
   - max_height_ft
   - max_stories
   - coverage_pct
   - front_setback_ft
   - side_setback_ft
   - rear_setback_ft
   - density (units/acre)
   - floor_area_ratio

OUTPUT FORMAT (JSON array):
[
  {
    "code": "R-1",
    "name": "Single-Family Residential",
    "category": "Residential",
    "dims": {
      "min_lot_sqft": 10000,
      "min_lot_width_ft": 80,
      "max_height_ft": 35,
      "max_stories": 2,
      "coverage_pct": 40,
      "front_setback_ft": 25,
      "side_setback_ft": 10,
      "rear_setback_ft": 20,
      "density": 4
    },
    "source_section": "Section 62.10",
    "is_new": true
  }
]

Set is_new=true if district is NOT in existing list.
Set any unknown dimensional values to null.
Return ONLY the JSON array, no other text.`;

  try {
    const { text } = await generateText({
      model: anthropic(CONFIG.anthropic.model),
      system: systemPrompt,
      prompt: `Extract all zoning districts from this ${jurisdiction.name} zoning code content:\n\n${scrapedContent.substring(0, 100000)}`,
      maxTokens: 8000
    });

    // Parse JSON from response
    const jsonMatch = text.match(/\[[\s\S]*\]/);
    if (jsonMatch) {
      return JSON.parse(jsonMatch[0]);
    }
    return [];
  } catch (error) {
    log('ERROR', `AI extraction failed for ${jurisdiction.name}: ${error.message}`);
    return [];
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// DATABASE OPERATIONS
// ═══════════════════════════════════════════════════════════════════════════════

async function getExistingDistricts(jurisdictionId) {
  const { data, error } = await supabase
    .from('zoning_districts')
    .select('id, code, name, category, description')
    .eq('jurisdiction_id', jurisdictionId);
  
  if (error) {
    log('ERROR', `Failed to fetch districts: ${error.message}`);
    return [];
  }
  return data || [];
}

function formatDIMSDescription(district, sourceUrl) {
  const dims = district.dims || {};
  const dimsJson = {
    min_lot_sqft: dims.min_lot_sqft || null,
    min_lot_width_ft: dims.min_lot_width_ft || null,
    max_height_ft: dims.max_height_ft || null,
    max_stories: dims.max_stories || null,
    coverage_pct: dims.coverage_pct || null,
    setbacks_ft: {
      front: dims.front_setback_ft || null,
      side: dims.side_setback_ft || null,
      rear: dims.rear_setback_ft || null,
      corner: null
    },
    density: dims.density || null,
    floor_area_ratio: dims.floor_area_ratio || null,
    source_url: sourceUrl,
    source_section: district.source_section || '',
    verified_date: new Date().toISOString().split('T')[0]
  };

  // Build human-readable description
  let desc = `${district.name} district.`;
  if (dims.min_lot_sqft) desc += ` Min lot: ${dims.min_lot_sqft.toLocaleString()} sqft.`;
  if (dims.min_lot_width_ft) desc += ` Min width: ${dims.min_lot_width_ft} ft.`;
  if (dims.max_height_ft) desc += ` Max height: ${dims.max_height_ft} ft.`;
  if (dims.max_stories) desc += ` Max stories: ${dims.max_stories}.`;
  if (dims.coverage_pct) desc += ` Coverage: ${dims.coverage_pct}%.`;
  if (dims.front_setback_ft || dims.side_setback_ft || dims.rear_setback_ft) {
    desc += ` Setbacks: F:${dims.front_setback_ft || '?'}/S:${dims.side_setback_ft || '?'}/R:${dims.rear_setback_ft || '?'} ft.`;
  }
  if (dims.density) desc += ` Density: ${dims.density} units/acre.`;

  return `${desc} <!--DIMS:${JSON.stringify(dimsJson)}-->`;
}

async function upsertDistrict(jurisdictionId, district, sourceUrl) {
  const description = formatDIMSDescription(district, sourceUrl);
  
  // Check if exists
  const { data: existing } = await supabase
    .from('zoning_districts')
    .select('id, description')
    .eq('jurisdiction_id', jurisdictionId)
    .eq('code', district.code)
    .single();

  if (existing) {
    // Update if missing DIMS
    if (!existing.description?.includes('<!--DIMS:')) {
      const { error } = await supabase
        .from('zoning_districts')
        .update({ description, category: district.category })
        .eq('id', existing.id);
      
      if (!error) {
        await logAudit('UPDATE', jurisdictionId, district.code, existing.description, description, sourceUrl);
        return { action: 'updated', code: district.code };
      }
    }
    return { action: 'unchanged', code: district.code };
  } else {
    // Insert new
    const { error } = await supabase
      .from('zoning_districts')
      .insert({
        jurisdiction_id: jurisdictionId,
        code: district.code,
        name: district.name,
        category: district.category,
        description
      });
    
    if (!error) {
      await logAudit('INSERT', jurisdictionId, district.code, null, description, sourceUrl);
      return { action: 'inserted', code: district.code };
    }
    return { action: 'error', code: district.code };
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// MAIN JURISDICTION PROCESSOR
// ═══════════════════════════════════════════════════════════════════════════════

async function processJurisdiction(jurisdiction) {
  log('PHASE', `Processing: ${jurisdiction.name} (ID: ${jurisdiction.id})`);
  await checkpoint(jurisdiction, 'IN_PROGRESS');

  const results = {
    jurisdiction: jurisdiction.name,
    existing: 0,
    found: 0,
    inserted: 0,
    updated: 0,
    unchanged: 0,
    errors: 0,
    source: null
  };

  try {
    // Step 1: Get existing districts
    const existing = await getExistingDistricts(jurisdiction.id);
    results.existing = existing.length;
    log('INFO', `Existing districts: ${existing.length}`);

    // Step 2: Find and scrape zoning code
    let scrapedContent = null;
    let sourceUrl = null;

    // Try known URLs first
    const urls = getZoningUrls(jurisdiction);
    for (const url of urls) {
      const result = await scrapeWithRetry(url, { waitFor: 8000 });
      if (result.success && result.content?.length > 5000) {
        scrapedContent = result.content;
        sourceUrl = url;
        break;
      }
    }

    // Fallback to search if no direct URL worked
    if (!scrapedContent) {
      log('INFO', `Direct URLs failed, searching for ${jurisdiction.name}`);
      const searchResult = await searchWeb(`${jurisdiction.name} Florida zoning code land development regulations`);
      if (searchResult.success && searchResult.results?.length > 0) {
        for (const result of searchResult.results) {
          if (result.url && (result.url.includes('municode') || result.url.includes('elaws') || result.url.includes('.gov'))) {
            const scrapeResult = await scrapeWithRetry(result.url, { waitFor: 10000 });
            if (scrapeResult.success && scrapeResult.content?.length > 5000) {
              scrapedContent = scrapeResult.content;
              sourceUrl = result.url;
              break;
            }
          }
        }
      }
    }

    if (!scrapedContent) {
      log('WARNING', `Could not scrape zoning code for ${jurisdiction.name}`);
      await checkpoint(jurisdiction, 'SOURCE_UNAVAILABLE', results);
      return results;
    }

    results.source = sourceUrl;
    log('SUCCESS', `Scraped from: ${sourceUrl}`);

    // Step 3: Extract districts with AI
    const extractedDistricts = await extractDistrictsWithAI(jurisdiction, scrapedContent, existing);
    results.found = extractedDistricts.length;
    log('INFO', `AI extracted ${extractedDistricts.length} districts`);

    // Step 4: Upsert to database
    for (const district of extractedDistricts) {
      const result = await upsertDistrict(jurisdiction.id, district, sourceUrl);
      results[result.action === 'inserted' ? 'inserted' : 
              result.action === 'updated' ? 'updated' : 
              result.action === 'error' ? 'errors' : 'unchanged']++;
    }

    log('SUCCESS', `${jurisdiction.name} complete`, {
      inserted: results.inserted,
      updated: results.updated,
      unchanged: results.unchanged
    });

    await checkpoint(jurisdiction, 'COMPLETED', results);
    return results;

  } catch (error) {
    log('ERROR', `Failed processing ${jurisdiction.name}: ${error.message}`);
    await checkpoint(jurisdiction, 'ERROR', { error: error.message });
    results.errors++;
    return results;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// FINAL AUDIT
// ═══════════════════════════════════════════════════════════════════════════════

async function runFinalAudit() {
  log('PHASE', 'Running final audit...');

  const { data: districts } = await supabase
    .from('zoning_districts')
    .select('jurisdiction_id, description')
    .in('jurisdiction_id', JURISDICTIONS.map(j => j.id));

  const { data: jurisdictions } = await supabase
    .from('jurisdictions')
    .select('id, name')
    .eq('county', 'Brevard');

  const summary = {
    total_districts: districts?.length || 0,
    with_dims: districts?.filter(d => d.description?.includes('<!--DIMS:')).length || 0,
    by_jurisdiction: {}
  };

  for (const j of jurisdictions || []) {
    const jDistricts = districts?.filter(d => d.jurisdiction_id === j.id) || [];
    summary.by_jurisdiction[j.name] = {
      total: jDistricts.length,
      with_dims: jDistricts.filter(d => d.description?.includes('<!--DIMS:')).length
    };
  }

  summary.dims_coverage = `${((summary.with_dims / summary.total_districts) * 100).toFixed(1)}%`;

  return summary;
}

// ═══════════════════════════════════════════════════════════════════════════════
// MAIN MISSION EXECUTION
// ═══════════════════════════════════════════════════════════════════════════════

async function executeMission() {
  console.log('\n' + '═'.repeat(80));
  console.log('  ZONEWISE AUTONOMOUS MISSION - BREVARD COUNTY 100% COMPLETION');
  console.log('  Started: ' + missionStart.toISOString());
  console.log('  Jurisdictions: 17 | Max Duration: 7 hours | Human Intervention: NONE');
  console.log('═'.repeat(80) + '\n');

  // Sort by priority
  const sortedJurisdictions = [...JURISDICTIONS].sort((a, b) => a.priority - b.priority);

  const missionResults = {
    jurisdictions_processed: 0,
    jurisdictions_completed: 0,
    jurisdictions_failed: 0,
    total_inserted: 0,
    total_updated: 0,
    total_unchanged: 0,
    total_errors: 0,
    details: []
  };

  // Process each jurisdiction
  for (const jurisdiction of sortedJurisdictions) {
    const result = await processJurisdiction(jurisdiction);
    missionResults.jurisdictions_processed++;
    
    if (result.errors === 0 && (result.inserted > 0 || result.updated > 0 || result.unchanged > 0)) {
      missionResults.jurisdictions_completed++;
    } else if (result.errors > 0) {
      missionResults.jurisdictions_failed++;
    }

    missionResults.total_inserted += result.inserted;
    missionResults.total_updated += result.updated;
    missionResults.total_unchanged += result.unchanged;
    missionResults.total_errors += result.errors;
    missionResults.details.push(result);

    // Delay between jurisdictions
    await delay(CONFIG.delayBetweenJurisdictions);
  }

  // Final audit
  const audit = await runFinalAudit();

  // Generate completion report
  const missionEnd = new Date();
  const durationMs = missionEnd - missionStart;
  const durationHours = (durationMs / (1000 * 60 * 60)).toFixed(2);

  const completionReport = {
    mission: 'ZoneWise Brevard County Complete',
    started_at: missionStart.toISOString(),
    completed_at: missionEnd.toISOString(),
    duration_hours: parseFloat(durationHours),
    jurisdictions: {
      total: 17,
      processed: missionResults.jurisdictions_processed,
      completed: missionResults.jurisdictions_completed,
      failed: missionResults.jurisdictions_failed
    },
    districts: {
      total: audit.total_districts,
      with_dims: audit.with_dims,
      inserted: missionResults.total_inserted,
      updated: missionResults.total_updated,
      unchanged: missionResults.total_unchanged,
      errors: missionResults.total_errors
    },
    data_quality: {
      dims_coverage: audit.dims_coverage
    },
    by_jurisdiction: audit.by_jurisdiction
  };

  // Save completion report
  try {
    await supabase.from('zonewise_completion_reports').insert({
      report: completionReport,
      created_at: missionEnd.toISOString()
    });
  } catch (e) {
    // Continue even if report save fails
  }

  // Print final report
  console.log('\n' + '═'.repeat(80));
  console.log('  MISSION COMPLETE');
  console.log('═'.repeat(80));
  console.log(JSON.stringify(completionReport, null, 2));
  console.log('═'.repeat(80) + '\n');

  // Check success
  if (audit.dims_coverage === '100.0%') {
    log('SUCCESS', '🎯 MISSION SUCCESS: 100% DIMS coverage achieved!');
  } else {
    log('WARNING', `Mission complete but only ${audit.dims_coverage} coverage achieved`);
  }

  return completionReport;
}

// ═══════════════════════════════════════════════════════════════════════════════
// ENTRY POINT
// ═══════════════════════════════════════════════════════════════════════════════

executeMission()
  .then((report) => {
    console.log('\n✅ ZoneWise mission finished successfully');
    process.exit(0);
  })
  .catch((error) => {
    console.error('\n❌ Mission failed:', error.message);
    process.exit(1);
  });
