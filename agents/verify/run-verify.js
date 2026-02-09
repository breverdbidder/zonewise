import 'dotenv/config';
import { verifyJurisdiction, verifyMultiple } from './zonewise-verify-agent.js';

// CLI handling
const args = process.argv.slice(2);

if (args.length === 0) {
  console.log(`
ZoneWise Verification Agent
Usage: node run-verify.js <jurisdiction_name> <jurisdiction_id>

Examples:
  node run-verify.js "Rockledge" 8
  node run-verify.js "Melbourne" 1
  node run-verify.js "Palm Bay" 2
  node run-verify.js --batch
  `);
  process.exit(0);
}

if (args[0] === '--batch') {
  const brevardJurisdictions = [
    { name: 'Rockledge', id: 8 },
    { name: 'Melbourne', id: 1 },
    { name: 'Palm Bay', id: 2 },
    { name: 'Titusville', id: 4 },
    { name: 'Cocoa', id: 5 },
    { name: 'West Melbourne', id: 9 },
    { name: 'Unincorporated Brevard County', id: 13 },
    { name: 'Indian Harbour Beach', id: 3 },
    { name: 'Satellite Beach', id: 6 },
    { name: 'Cocoa Beach', id: 7 },
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
  const jurisdictionName = args[0];
  const jurisdictionId = parseInt(args[1], 10);

  if (!jurisdictionName || isNaN(jurisdictionId)) {
    console.error('❌ Error: Please provide jurisdiction name and ID');
    process.exit(1);
  }

  verifyJurisdiction(jurisdictionName, jurisdictionId)
    .then(() => process.exit(0))
    .catch(e => { console.error(e); process.exit(1); });
}
