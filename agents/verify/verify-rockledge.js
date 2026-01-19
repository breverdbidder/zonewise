/**
 * Rockledge FL Zoning District Verification
 * Uses Vercel AI SDK + Firecrawl to scrape and verify complete district list
 * 
 * Run in Claude Code: node verify-rockledge.js
 */

import { generateText } from 'ai';
import { anthropic } from '@ai-sdk/anthropic';
import Firecrawl from '@mendable/firecrawl-js';

// Initialize Firecrawl
const firecrawl = new Firecrawl({ apiKey: process.env.FIRECRAWL_API_KEY });

// Current districts in Supabase (14 total)
const EXISTING_DISTRICTS = [
  'AG', 'C-1', 'C-2', 'I-1', 'MH', 'PUD', 
  'R-1', 'R-1A', 'R-2', 'R-3', 'RCE', 'RMU', 'RVP', 'TH'
];

// Firecrawl tools for Vercel AI SDK
const scrapeZoningPage = {
  name: 'scrape_zoning_page',
  description: 'Scrape a municipal zoning code page and extract district information',
  parameters: {
    type: 'object',
    properties: {
      url: { type: 'string', description: 'URL of the zoning code page to scrape' }
    },
    required: ['url']
  },
  execute: async ({ url }) => {
    console.log(`🔍 Scraping: ${url}`);
    try {
      const result = await firecrawl.scrapeUrl(url, {
        formats: ['markdown', 'html'],
        waitFor: 5000,
        timeout: 30000
      });
      return {
        success: true,
        content: result.markdown || result.html,
        title: result.metadata?.title || 'Unknown'
      };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }
};

const searchZoningInfo = {
  name: 'search_zoning_info',
  description: 'Search for zoning information using Firecrawl search',
  parameters: {
    type: 'object',
    properties: {
      query: { type: 'string', description: 'Search query for zoning information' }
    },
    required: ['query']
  },
  execute: async ({ query }) => {
    console.log(`🔎 Searching: ${query}`);
    try {
      const results = await firecrawl.search(query, { limit: 5 });
      return { success: true, results };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }
};

async function verifyRockledgeDistricts() {
  console.log('='.repeat(60));
  console.log('🏛️  ROCKLEDGE FL ZONING DISTRICT VERIFICATION');
  console.log('='.repeat(60));
  console.log(`\n📋 Current districts in ZoneWise: ${EXISTING_DISTRICTS.length}`);
  console.log(`   ${EXISTING_DISTRICTS.join(', ')}\n`);

  const { text, toolCalls, toolResults } = await generateText({
    model: anthropic('claude-sonnet-4-5-20250514'),
    tools: {
      scrape_zoning_page: scrapeZoningPage,
      search_zoning_info: searchZoningInfo
    },
    maxSteps: 10,
    system: `You are a zoning code research agent. Your task is to find the COMPLETE list of zoning districts for Rockledge, Florida.

CURRENT DISTRICTS IN DATABASE (14):
${EXISTING_DISTRICTS.join(', ')}

YOUR MISSION:
1. Scrape the Rockledge Land Development Regulations from Municode
2. Find Section 62.00 or 62.01 which lists all zoning classifications
3. Extract EVERY zoning district code and name
4. Compare against our current list
5. Identify ANY missing districts

KEY URLS TO TRY:
- https://library.municode.com/fl/rockledge/codes/land_development_regulations_
- https://library.municode.com/fl/rockledge/codes/land_development_regulations_?nodeId=LADERE_PTVIPLDIZO
- https://library.municode.com/fl/rockledge/codes/land_development_regulations_?nodeId=LADERE_PTVIPLDIZO_S62.00ZOCLACUSWIZOCL

OUTPUT FORMAT:
After research, provide a structured summary:
1. COMPLETE DISTRICT LIST FOUND: [list all districts]
2. MISSING FROM DATABASE: [any districts not in our 14]
3. CONFIDENCE LEVEL: HIGH/MEDIUM/LOW
4. SOURCES USED: [URLs scraped]`,
    prompt: `Find the complete list of zoning districts for Rockledge, Florida. 
Start by scraping the Municode Land Development Regulations.
Compare against our existing ${EXISTING_DISTRICTS.length} districts and identify any gaps.`
  });

  console.log('\n' + '='.repeat(60));
  console.log('📊 VERIFICATION RESULTS');
  console.log('='.repeat(60));
  console.log(text);
  
  // Log tool usage
  if (toolCalls && toolCalls.length > 0) {
    console.log(`\n🔧 Tool calls made: ${toolCalls.length}`);
    toolCalls.forEach((call, i) => {
      console.log(`   ${i + 1}. ${call.toolName}`);
    });
  }

  return text;
}

// Run verification
verifyRockledgeDistricts()
  .then(() => {
    console.log('\n✅ Verification complete');
    process.exit(0);
  })
  .catch((error) => {
    console.error('\n❌ Error:', error.message);
    process.exit(1);
  });
