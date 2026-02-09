import 'dotenv/config';
import { execSync } from 'child_process';

console.log('🚀 Starting ZoneWise Complete Mission...\n');
console.log('Environment Check:');
console.log(`  SUPABASE_URL: ${process.env.SUPABASE_URL ? '✅ Set' : '❌ Missing'}`);
console.log(`  SUPABASE_KEY: ${process.env.SUPABASE_KEY ? '✅ Set' : '❌ Missing'}`);
console.log(`  FIRECRAWL_API_KEY: ${process.env.FIRECRAWL_API_KEY ? '✅ Set' : '❌ Missing'}`);
console.log('');

if (!process.env.SUPABASE_KEY || !process.env.FIRECRAWL_API_KEY) {
  console.error('❌ Missing required environment variables');
  process.exit(1);
}

// Import and run the mission
import('./zonewise-complete-mission.js');
