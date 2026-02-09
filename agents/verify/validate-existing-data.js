import 'dotenv/config';
import { createClient } from '@supabase/supabase-js';
import Firecrawl from '@mendable/firecrawl-js';

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_KEY
);

const firecrawl = new Firecrawl({ apiKey: process.env.FIRECRAWL_API_KEY });

const JURISDICTIONS = [
  { id: 1, name: 'Melbourne' },
  { id: 2, name: 'Palm Bay' },
  { id: 3, name: 'Indian Harbour Beach' },
  { id: 4, name: 'Titusville' },
  { id: 5, name: 'Cocoa' },
  { id: 6, name: 'Satellite Beach' },
  { id: 7, name: 'Cocoa Beach' },
  { id: 8, name: 'Rockledge' },
  { id: 9, name: 'West Melbourne' },
  { id: 10, name: 'Cape Canaveral' },
  { id: 11, name: 'Indialantic' },
  { id: 12, name: 'Melbourne Beach' },
  { id: 13, name: 'Unincorporated Brevard County' },
  { id: 14, name: 'Malabar' },
  { id: 15, name: 'Grant-Valkaria' },
  { id: 16, name: 'Palm Shores' },
  { id: 17, name: 'Melbourne Village' }
];

function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function validateJurisdiction(jurisdiction) {
  console.log(`\n${'═'.repeat(80)}`);
  console.log(`🏛️  ${jurisdiction.name} (ID: ${jurisdiction.id})`);
  console.log('═'.repeat(80));

  // Get all districts
  const { data: districts, error } = await supabase
    .from('zoning_districts')
    .select('*')
    .eq('jurisdiction_id', jurisdiction.id)
    .order('code');

  if (error) {
    console.error(`❌ Error fetching districts: ${error.message}`);
    return { jurisdiction, success: false, error: error.message };
  }

  console.log(`📊 Total Districts: ${districts.length}`);

  let stats = {
    total: districts.length,
    with_dims: 0,
    with_source: 0,
    with_verified_date: 0,
    recently_verified: 0,
    needs_review: 0,
    flagged_districts: []
  };

  const oneWeekAgo = new Date();
  oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);

  // Analyze each district
  for (const district of districts) {
    const dimsMatch = district.description?.match(/<!--DIMS:(.*?)-->/s);

    if (dimsMatch) {
      try {
        const dims = JSON.parse(dimsMatch[1]);
        stats.with_dims++;

        if (dims.source_url) stats.with_source++;
        if (dims.verified_date) {
          stats.with_verified_date++;
          const verifiedDate = new Date(dims.verified_date);
          if (verifiedDate >= oneWeekAgo) stats.recently_verified++;
        }

        // Check for issues
        const hasEstimated = district.description.toLowerCase().includes('estimate') ||
                            district.description.toLowerCase().includes('verify with city');

        const hasMinimalDims = !dims.min_lot_sqft && !dims.min_lot_width_ft &&
                               !dims.max_height_ft && !dims.max_stories;

        if (hasEstimated || hasMinimalDims || !dims.source_url || !dims.verified_date) {
          stats.needs_review++;
          stats.flagged_districts.push({
            code: district.code,
            name: district.name,
            issues: [
              hasEstimated && 'Contains estimation notes',
              hasMinimalDims && 'Missing key dimensional data',
              !dims.source_url && 'No source URL',
              !dims.verified_date && 'No verified date'
            ].filter(Boolean)
          });
        }
      } catch (e) {
        stats.needs_review++;
        stats.flagged_districts.push({
          code: district.code,
          name: district.name,
          issues: ['Invalid DIMS JSON']
        });
      }
    } else {
      stats.needs_review++;
      stats.flagged_districts.push({
        code: district.code,
        name: district.name,
        issues: ['No DIMS data']
      });
    }
  }

  // Print stats
  console.log(`\n📈 Data Quality:`);
  console.log(`   With DIMS:           ${stats.with_dims}/${stats.total} (${((stats.with_dims/stats.total)*100).toFixed(1)}%)`);
  console.log(`   With Source URL:     ${stats.with_source}/${stats.total} (${((stats.with_source/stats.total)*100).toFixed(1)}%)`);
  console.log(`   With Verified Date:  ${stats.with_verified_date}/${stats.total} (${((stats.with_verified_date/stats.total)*100).toFixed(1)}%)`);
  console.log(`   Recently Verified:   ${stats.recently_verified}/${stats.total} (${((stats.recently_verified/stats.total)*100).toFixed(1)}%)`);
  console.log(`   Need Review:         ${stats.needs_review}`);

  if (stats.flagged_districts.length > 0) {
    console.log(`\n⚠️  Flagged Districts:`);
    stats.flagged_districts.forEach(d => {
      console.log(`   ${d.code.padEnd(10)} ${d.name.substring(0, 40).padEnd(40)}`);
      d.issues.forEach(issue => console.log(`      - ${issue}`));
    });
  } else {
    console.log(`\n✅ All districts have complete data!`);
  }

  return {
    jurisdiction: jurisdiction.name,
    id: jurisdiction.id,
    success: true,
    stats
  };
}

async function validateAll() {
  console.log('\n' + '═'.repeat(80));
  console.log('🎯 ZONEWISE DATA VALIDATION');
  console.log('   Brevard County, Florida - All 17 Jurisdictions');
  console.log('═'.repeat(80));
  console.log(`Started: ${new Date().toISOString()}\n`);

  const results = [];
  const startTime = Date.now();

  for (const jurisdiction of JURISDICTIONS) {
    const result = await validateJurisdiction(jurisdiction);
    results.push(result);
    await delay(1000);
  }

  // Overall summary
  console.log(`\n\n${'═'.repeat(80)}`);
  console.log('📊 OVERALL SUMMARY');
  console.log('═'.repeat(80));

  const totalDistricts = results.reduce((sum, r) => sum + (r.stats?.total || 0), 0);
  const totalWithDims = results.reduce((sum, r) => sum + (r.stats?.with_dims || 0), 0);
  const totalWithSource = results.reduce((sum, r) => sum + (r.stats?.with_source || 0), 0);
  const totalNeedingReview = results.reduce((sum, r) => sum + (r.stats?.needs_review || 0), 0);

  console.log(`\nJurisdictions Validated:  ${results.length}`);
  console.log(`Total Districts:          ${totalDistricts}`);
  console.log(`With DIMS Data:           ${totalWithDims} (${((totalWithDims/totalDistricts)*100).toFixed(1)}%)`);
  console.log(`With Source URLs:         ${totalWithSource} (${((totalWithSource/totalDistricts)*100).toFixed(1)}%)`);
  console.log(`Needing Review:           ${totalNeedingReview} (${((totalNeedingReview/totalDistricts)*100).toFixed(1)}%)`);

  const duration = (Date.now() - startTime) / 1000;
  console.log(`\nDuration: ${duration.toFixed(1)}s`);

  // Save checkpoint
  try {
    await supabase.from('claude_context_checkpoints').insert({
      session_type: 'zonewise_validation',
      checkpoint_data: {
        timestamp: new Date().toISOString(),
        duration_seconds: duration,
        results,
        summary: {
          total_jurisdictions: results.length,
          total_districts: totalDistricts,
          total_with_dims: totalWithDims,
          total_with_source: totalWithSource,
          total_needing_review: totalNeedingReview,
          dims_coverage_percent: ((totalWithDims/totalDistricts)*100).toFixed(1)
        }
      },
      created_at: new Date().toISOString()
    });
    console.log('\n✅ Validation results saved to Supabase');
  } catch (e) {
    console.error(`\n⚠️  Warning: Could not save checkpoint: ${e.message}`);
  }

  console.log('\n' + '═'.repeat(80));
  console.log(`✅ VALIDATION COMPLETE`);
  console.log('═'.repeat(80) + '\n');

  return results;
}

// Run validation
validateAll()
  .then(() => process.exit(0))
  .catch(error => {
    console.error('\n❌ Validation failed:', error);
    process.exit(1);
  });
