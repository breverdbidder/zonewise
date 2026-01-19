/**
 * ZoneWise Zoning District Verification Agent
 * Reusable Vercel AI SDK + Firecrawl agent for verifying zoning data completeness
 * 
 * Usage: node zonewise-verify-agent.js <jurisdiction_name> <jurisdiction_id>
 * Example: node zonewise-verify-agent.js "Rockledge" 8
 * Example: node zonewise-verify-agent.js "Cocoa Beach" 7
 * Example: node zonewise-verify-agent.js "Melbourne" 1
 */

import { generateText } from 'ai';
import { anthropic } from '@ai-sdk/anthropic';
import Firecrawl from '@mendable/firecrawl-js';
import { createClient } from '@supabase/supabase-js';

// Configuration
const CONFIG = {
  firecrawlApiKey: process.env.FIRECRAWL_API_KEY || '${FIRECRAWL_API_KEY}',
  supabaseUrl: 'https://mocerqjnksmhcjzxrewo.supabase.co',
  supabaseKey: process.env.SUPABASE_KEY || '${SUPABASE_KEY}',
  model: 'claude-sonnet-4-5-20250514',
  maxSteps: 15
};

// Initialize clients
const firecrawl = new Firecrawl({ apiKey: CONFIG.firecrawlApiKey });
const supabase = createClient(CONFIG.supabaseUrl, CONFIG.supabaseKey);

// Common zoning code platforms in Florida
const ZONING_PLATFORMS = {
  municode: 'https://library.municode.com/fl',
  elaws: 'https://{city}-fl.elaws.us/code',
  amlegal: 'https://codelibrary.amlegal.com/codes/{city}',
  cityDirect: 'https://www.{city}fl.gov'
};

// Tool definitions
const tools = {
  scrape_page: {
    name: 'scrape_page',
    description: 'Scrape a web page and extract content as markdown',
    parameters: {
      type: 'object',
      properties: {
        url: { type: 'string', description: 'URL to scrape' },
        waitFor: { type: 'number', description: 'Milliseconds to wait for JS rendering', default: 5000 }
      },
      required: ['url']
    },
    execute: async ({ url, waitFor = 5000 }) => {
      console.log(`   🔍 Scraping: ${url}`);
      try {
        const result = await firecrawl.scrapeUrl(url, {
          formats: ['markdown'],
          waitFor,
          timeout: 30000
        });
        return {
          success: true,
          content: result.markdown?.substring(0, 50000) || 'No content',
          title: result.metadata?.title || 'Unknown',
          url
        };
      } catch (error) {
        return { success: false, error: error.message, url };
      }
    }
  },

  search_web: {
    name: 'search_web',
    description: 'Search the web for zoning information',
    parameters: {
      type: 'object',
      properties: {
        query: { type: 'string', description: 'Search query' }
      },
      required: ['query']
    },
    execute: async ({ query }) => {
      console.log(`   🔎 Searching: ${query}`);
      try {
        const results = await firecrawl.search(query, { limit: 5 });
        return { success: true, results };
      } catch (error) {
        return { success: false, error: error.message };
      }
    }
  },

  get_existing_districts: {
    name: 'get_existing_districts',
    description: 'Get existing zoning districts from ZoneWise database',
    parameters: {
      type: 'object',
      properties: {
        jurisdiction_id: { type: 'number', description: 'Jurisdiction ID in Supabase' }
      },
      required: ['jurisdiction_id']
    },
    execute: async ({ jurisdiction_id }) => {
      console.log(`   📋 Fetching existing districts for jurisdiction ${jurisdiction_id}`);
      const { data, error } = await supabase
        .from('zoning_districts')
        .select('code, name, category')
        .eq('jurisdiction_id', jurisdiction_id)
        .order('code');
      
      if (error) return { success: false, error: error.message };
      return { 
        success: true, 
        count: data.length,
        districts: data.map(d => ({ code: d.code, name: d.name, category: d.category }))
      };
    }
  },

  report_missing_districts: {
    name: 'report_missing_districts',
    description: 'Report districts found in official sources but missing from ZoneWise',
    parameters: {
      type: 'object',
      properties: {
        missing: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              code: { type: 'string' },
              name: { type: 'string' },
              source_url: { type: 'string' },
              notes: { type: 'string' }
            }
          },
          description: 'Array of missing district objects'
        }
      },
      required: ['missing']
    },
    execute: async ({ missing }) => {
      console.log(`   📝 Reporting ${missing.length} missing districts`);
      return { success: true, missing_count: missing.length, missing };
    }
  }
};

/**
 * Main verification function
 */
async function verifyJurisdiction(jurisdictionName, jurisdictionId) {
  console.log('\n' + '═'.repeat(70));
  console.log(`🏛️  ZONEWISE VERIFICATION AGENT`);
  console.log(`   Jurisdiction: ${jurisdictionName} (ID: ${jurisdictionId})`);
  console.log('═'.repeat(70) + '\n');

  const systemPrompt = `You are a zoning code research agent for the ZoneWise platform. Your mission is to verify that our database has the COMPLETE list of zoning districts for a Florida municipality.

## YOUR PROCESS:

1. FIRST: Call get_existing_districts to see what we already have
2. SEARCH: Find the official zoning code for ${jurisdictionName}, Florida
   - Try Municode: https://library.municode.com/fl/${jurisdictionName.toLowerCase().replace(/\s+/g, '_')}
   - Try eLaws: https://${jurisdictionName.toLowerCase().replace(/\s+/g, '')}-fl.elaws.us
   - Search for "${jurisdictionName} Florida zoning districts land development code"
3. SCRAPE: Get the actual zoning district classifications section
   - Look for "Establishment of Districts" or "Zoning Classifications"
   - Usually in Article/Section 62 or similar
4. COMPARE: Check every official district against our database
5. REPORT: Use report_missing_districts for any gaps

## WHAT TO LOOK FOR:

Florida cities typically have these district types:
- Residential: R-1, R-2, R-3, R-1A, RE, RCE, MH, TH, etc.
- Commercial: C-1, C-2, C-3, CN, CG, etc.
- Industrial: I-1, I-2, M-1, M-2, etc.
- Special: PUD, PRD, RMU, MU, TOD, etc.
- Public/Institutional: P, PS, INS, GOV, etc.
- Conservation: CON, AG, A, etc.

## OUTPUT:

After completing research, provide:
1. Total districts found in official code
2. Total districts in ZoneWise
3. List of any MISSING districts (code + name + source)
4. Confidence level (HIGH/MEDIUM/LOW)
5. Recommended action`;

  const userPrompt = `Verify the zoning district completeness for ${jurisdictionName}, Florida (jurisdiction_id: ${jurisdictionId}).

Start by getting our existing districts, then research the official sources to find any we're missing.`;

  try {
    const { text, toolCalls } = await generateText({
      model: anthropic(CONFIG.model),
      tools,
      maxSteps: CONFIG.maxSteps,
      system: systemPrompt,
      prompt: userPrompt
    });

    console.log('\n' + '─'.repeat(70));
    console.log('📊 VERIFICATION REPORT');
    console.log('─'.repeat(70));
    console.log(text);

    if (toolCalls && toolCalls.length > 0) {
      console.log(`\n🔧 Tool calls: ${toolCalls.length}`);
    }

    return { success: true, report: text };
  } catch (error) {
    console.error('\n❌ Agent error:', error.message);
    return { success: false, error: error.message };
  }
}

/**
 * Batch verification for multiple jurisdictions
 */
async function verifyMultiple(jurisdictions) {
  console.log(`\n🚀 Starting batch verification for ${jurisdictions.length} jurisdictions\n`);
  
  const results = [];
  for (const { name, id } of jurisdictions) {
    const result = await verifyJurisdiction(name, id);
    results.push({ name, id, ...result });
    
    // Rate limiting between jurisdictions
    await new Promise(resolve => setTimeout(resolve, 2000));
  }

  console.log('\n' + '═'.repeat(70));
  console.log('📋 BATCH VERIFICATION SUMMARY');
  console.log('═'.repeat(70));
  results.forEach(r => {
    const status = r.success ? '✅' : '❌';
    console.log(`${status} ${r.name} (ID: ${r.id})`);
  });

  return results;
}

// CLI handling
const args = process.argv.slice(2);

if (args.length === 0) {
  console.log(`
ZoneWise Verification Agent
Usage: node zonewise-verify-agent.js <jurisdiction_name> <jurisdiction_id>

Examples:
  node zonewise-verify-agent.js "Rockledge" 8
  node zonewise-verify-agent.js "Cocoa Beach" 7
  node zonewise-verify-agent.js "Melbourne" 1
  node zonewise-verify-agent.js "Palm Bay" 2

Brevard County Jurisdictions:
  1  - Melbourne
  2  - Palm Bay
  3  - Indian Harbour Beach
  4  - Titusville
  5  - Cocoa
  6  - Satellite Beach
  7  - Cocoa Beach
  8  - Rockledge
  9  - West Melbourne
  10 - Cape Canaveral
  11 - Indialantic
  12 - Melbourne Beach
  13 - Unincorporated Brevard
  14 - Malabar
  15 - Grant-Valkaria
  16 - Palm Shores
  17 - Melbourne Village
`);
  process.exit(0);
}

if (args[0] === '--batch') {
  // Batch mode: verify all Brevard jurisdictions
  const brevardJurisdictions = [
    { name: 'Melbourne', id: 1 },
    { name: 'Palm Bay', id: 2 },
    { name: 'Indian Harbour Beach', id: 3 },
    { name: 'Titusville', id: 4 },
    { name: 'Cocoa', id: 5 },
    { name: 'Satellite Beach', id: 6 },
    { name: 'Cocoa Beach', id: 7 },
    { name: 'Rockledge', id: 8 },
    { name: 'West Melbourne', id: 9 },
    { name: 'Cape Canaveral', id: 10 },
    { name: 'Indialantic', id: 11 },
    { name: 'Melbourne Beach', id: 12 },
    { name: 'Malabar', id: 14 },
    { name: 'Grant-Valkaria', id: 15 },
    { name: 'Palm Shores', id: 16 },
    { name: 'Melbourne Village', id: 17 }
  ];
  
  verifyMultiple(brevardJurisdictions)
    .then(() => process.exit(0))
    .catch(e => { console.error(e); process.exit(1); });
} else {
  // Single jurisdiction mode
  const jurisdictionName = args[0];
  const jurisdictionId = parseInt(args[1], 10);

  if (!jurisdictionName || isNaN(jurisdictionId)) {
    console.error('❌ Error: Please provide jurisdiction name and ID');
    console.error('   Usage: node zonewise-verify-agent.js "Rockledge" 8');
    process.exit(1);
  }

  verifyJurisdiction(jurisdictionName, jurisdictionId)
    .then(() => process.exit(0))
    .catch(e => { console.error(e); process.exit(1); });
}

export { verifyJurisdiction, verifyMultiple };
