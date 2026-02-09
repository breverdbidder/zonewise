import 'dotenv/config';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_KEY
);

// Known source URLs for each jurisdiction
const JURISDICTION_SOURCES = {
  3: {  // Indian Harbour Beach
    name: 'Indian Harbour Beach',
    baseUrl: 'https://library.municode.com/fl/indian_harbour_beach/codes/code_of_ordinances',
    zoningUrl: 'https://ecode360.com/IN1275'  // eLaws platform
  },
  6: {  // Satellite Beach
    name: 'Satellite Beach',
    baseUrl: 'https://library.municode.com/fl/satellite_beach/codes/code_of_ordinances',
    zoningUrl: 'https://ecode360.com/SA1374'
  },
  7: {  // Cocoa Beach
    name: 'Cocoa Beach',
    baseUrl: 'https://library.municode.com/fl/cocoa_beach/codes/code_of_ordinances',
    zoningUrl: 'https://library.municode.com/fl/cocoa_beach/codes/code_of_ordinances?nodeId=SPBLADECO_CH3ZO'
  },
  13: {  // Unincorporated Brevard
    name: 'Unincorporated Brevard County',
    baseUrl: 'https://library.municode.com/fl/brevard_county/codes/code_of_ordinances',
    zoningUrl: 'https://library.municode.com/fl/brevard_county/codes/code_of_ordinances?nodeId=COOR_CH62ZO'
  }
};

async function updateSourceUrls(jurisdictionId) {
  const config = JURISDICTION_SOURCES[jurisdictionId];

  if (!config) {
    console.log(`⏭️  Skipping jurisdiction ${jurisdictionId} - already has source URLs\n`);
    return { skipped: true };
  }

  console.log(`\n${'═'.repeat(80)}`);
  console.log(`📝 UPDATING SOURCE URLs: ${config.name} (ID: ${jurisdictionId})`);
  console.log('═'.repeat(80));

  // Get districts missing source URLs
  const { data: districts, error } = await supabase
    .from('zoning_districts')
    .select('*')
    .eq('jurisdiction_id', jurisdictionId);

  if (error) {
    console.error(`❌ Error: ${error.message}`);
    return { error: error.message };
  }

  console.log(`📊 Total districts: ${districts.length}`);

  let updated = 0;
  let alreadyHad = 0;

  for (const district of districts) {
    const dimsMatch = district.description?.match(/<!--DIMS:(.*?)-->/s);

    if (dimsMatch) {
      try {
        const dims = JSON.parse(dimsMatch[1]);

        // Check if already has source_url
        if (dims.source_url && dims.source_url !== '') {
          alreadyHad++;
          continue;
        }

        // Add source URL
        dims.source_url = config.zoningUrl;

        // Update description with new DIMS
        const updatedDescription = district.description.replace(
          /<!--DIMS:.*?-->/s,
          `<!--DIMS:${JSON.stringify(dims, null, 0)}-->`
        );

        // Update in database
        const { error: updateError } = await supabase
          .from('zoning_districts')
          .update({ description: updatedDescription })
          .eq('id', district.id);

        if (updateError) {
          console.error(`   ❌ Error updating ${district.code}: ${updateError.message}`);
        } else {
          console.log(`   ✅ Updated ${district.code} - ${district.name}`);
          updated++;
        }

      } catch (e) {
        console.error(`   ⚠️  Invalid JSON for ${district.code}`);
      }
    }
  }

  console.log(`\n📈 Results:`);
  console.log(`   Updated: ${updated}`);
  console.log(`   Already had source: ${alreadyHad}`);
  console.log(`   Total: ${districts.length}`);

  return { updated, alreadyHad, total: districts.length };
}

async function updateAll() {
  console.log('\n' + '═'.repeat(80));
  console.log('🎯 ADDING MISSING SOURCE URLs');
  console.log('═'.repeat(80));
  console.log(`Started: ${new Date().toISOString()}\n`);

  const results = [];

  for (const [jid, config] of Object.entries(JURISDICTION_SOURCES)) {
    const result = await updateSourceUrls(parseInt(jid));
    results.push({ jurisdiction_id: parseInt(jid), name: config.name, ...result });
    await new Promise(resolve => setTimeout(resolve, 500));
  }

  console.log(`\n\n${'═'.repeat(80)}`);
  console.log('📊 UPDATE SUMMARY');
  console.log('═'.repeat(80));

  const totalUpdated = results.reduce((sum, r) => sum + (r.updated || 0), 0);

  console.log(`\nJurisdictions Processed: ${results.length}`);
  console.log(`Total Districts Updated: ${totalUpdated}`);

  results.forEach(r => {
    if (!r.skipped) {
      console.log(`\n${r.name}:`);
      console.log(`   Updated: ${r.updated || 0}`);
      console.log(`   Already had source: ${r.alreadyHad || 0}`);
    }
  });

  // Save checkpoint
  try {
    await supabase.from('claude_context_checkpoints').insert({
      session_type: 'zonewise_source_url_update',
      checkpoint_data: {
        timestamp: new Date().toISOString(),
        results,
        total_updated: totalUpdated
      },
      created_at: new Date().toISOString()
    });
    console.log('\n✅ Update saved to Supabase');
  } catch (e) {
    console.error(`\n⚠️  Warning: ${e.message}`);
  }

  console.log('\n' + '═'.repeat(80));
  console.log('✅ SOURCE URL UPDATE COMPLETE');
  console.log('═'.repeat(80) + '\n');
}

updateAll()
  .then(() => process.exit(0))
  .catch(error => {
    console.error('\n❌ Update failed:', error);
    process.exit(1);
  });
