# ZoneWise Modal Deployment Guide

**Time Required:** ~15 minutes  
**Prerequisites:** GitHub account, credit card (Modal uses pay-as-you-go, ~$0-10/month)

---

## Step 1: Create Modal Account

1. **Go to:** [https://modal.com/signup](https://modal.com/signup)
2. Sign up with GitHub (recommended) or email
3. Verify your email if required

---

## Step 2: Install Modal CLI

Open your terminal and run:

```bash
pip install modal
```

Then authenticate:

```bash
modal token new
```

This opens a browser window. Click **"Authorize"** and return to terminal.

**Verify installation:**
```bash
modal --version
```

---

## Step 3: Create Modal Secrets

Run this command (replace the SUPABASE_KEY with full key):

```bash
modal secret create zonewise-secrets \
  SUPABASE_URL="https://mocerqjnksmhcjzxrewo.supabase.co" \
  SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1vY2VycWpua3NtaGNqenhyZXdvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDUzMjUyNiwiZXhwIjoyMDgwMTA4NTI2fQ.fL255mO0V8-rrU0Il3L41cIdQXUau-HRQXiamTqp9nE" \
  CENSUS_API_KEY="8c6ef3cae05fd24b03c4e541d9eb11c2ba9c6589" \
  FIRECRAWL_API_KEY="fc-fa112951a2564765a2d146302774ac9b"
```

**Verify secrets created:**
- Go to: [https://modal.com/secrets](https://modal.com/secrets)
- You should see `zonewise-secrets` listed

---

## Step 4: Add GitHub Secrets (for CI/CD)

This enables automatic deployment when you push to GitHub.

1. **Find your Modal tokens:**
   ```bash
   cat ~/.modal.toml
   ```
   Copy the `token_id` and `token_secret` values.

2. **Go to:** [https://github.com/breverdbidder/zonewise/settings/secrets/actions](https://github.com/breverdbidder/zonewise/settings/secrets/actions)

3. Click **"New repository secret"** and add:

   | Name | Value |
   |------|-------|
   | `MODAL_TOKEN_ID` | (paste token_id from ~/.modal.toml) |
   | `MODAL_TOKEN_SECRET` | (paste token_secret from ~/.modal.toml) |

---

## Step 5: Execute Supabase Schema

1. **Go to:** [https://supabase.com/dashboard/project/mocerqjnksmhcjzxrewo/sql/new](https://supabase.com/dashboard/project/mocerqjnksmhcjzxrewo/sql/new)

2. **Copy the schema from:** [https://github.com/breverdbidder/zonewise/blob/main/docs/supabase_schema.sql](https://github.com/breverdbidder/zonewise/blob/main/docs/supabase_schema.sql)

3. Paste into the SQL Editor and click **"Run"**

4. **Verify tables created:**
   - Go to: [https://supabase.com/dashboard/project/mocerqjnksmhcjzxrewo/editor](https://supabase.com/dashboard/project/mocerqjnksmhcjzxrewo/editor)
   - You should see new tables: `parcel_zones`, `dimensional_standards`, `permitted_uses`, etc.

---

## Step 6: Clone Repository & Deploy

```bash
# Clone the repo
git clone https://github.com/breverdbidder/zonewise.git
cd zonewise

# Deploy to Modal
modal deploy src/app.py
```

**Expected output:**
```
✓ Created objects.
├── 🔨 Created process_stage_1_zone_assignment.
├── 🔨 Created scrape_phase_2_base_zoning.
├── 🔨 Created nightly_pipeline.
└── 🔨 Created mount /home/claude/zonewise-modal
✓ App deployed! 🎉
```

---

## Step 7: Verify Deployment

1. **Go to Modal Dashboard:** [https://modal.com/apps](https://modal.com/apps)

2. You should see `zonewise` app listed with functions:
   - `process_stage_1_zone_assignment`
   - `scrape_phase_2_base_zoning`
   - `nightly_pipeline`
   - etc.

---

## Step 8: Test Run (Optional)

Run a manual test of the nightly pipeline:

```bash
modal run src/app.py
```

Or run a specific function:

```bash
modal run src/app.py::process_stage_1_zone_assignment --county-id brevard --jurisdiction-id 13
```

---

## Step 9: Verify Cron Schedule

The nightly pipeline runs automatically at 11 PM EST daily.

**Check scheduled runs:** [https://modal.com/apps/zonewise/scheduled](https://modal.com/apps)

---

## Quick Reference Links

| Resource | Link |
|----------|------|
| **Modal Dashboard** | [https://modal.com/apps](https://modal.com/apps) |
| **Modal Secrets** | [https://modal.com/secrets](https://modal.com/secrets) |
| **Modal Docs** | [https://modal.com/docs](https://modal.com/docs) |
| **GitHub Repo** | [https://github.com/breverdbidder/zonewise](https://github.com/breverdbidder/zonewise) |
| **GitHub Actions** | [https://github.com/breverdbidder/zonewise/actions](https://github.com/breverdbidder/zonewise/actions) |
| **GitHub Secrets** | [https://github.com/breverdbidder/zonewise/settings/secrets/actions](https://github.com/breverdbidder/zonewise/settings/secrets/actions) |
| **Supabase Dashboard** | [https://supabase.com/dashboard/project/mocerqjnksmhcjzxrewo](https://supabase.com/dashboard/project/mocerqjnksmhcjzxrewo) |
| **Supabase SQL Editor** | [https://supabase.com/dashboard/project/mocerqjnksmhcjzxrewo/sql/new](https://supabase.com/dashboard/project/mocerqjnksmhcjzxrewo/sql/new) |
| **Supabase Tables** | [https://supabase.com/dashboard/project/mocerqjnksmhcjzxrewo/editor](https://supabase.com/dashboard/project/mocerqjnksmhcjzxrewo/editor) |

---

## Troubleshooting

### "Secret not found" error
```bash
modal secret list
```
If `zonewise-secrets` is missing, re-run Step 3.

### "Module not found" error
Make sure you're in the `zonewise` directory:
```bash
cd zonewise
modal deploy src/app.py
```

### GitHub Actions failing
Check that both secrets are set:
- [https://github.com/breverdbidder/zonewise/settings/secrets/actions](https://github.com/breverdbidder/zonewise/settings/secrets/actions)

### Supabase connection error
Verify the key is correct in Modal secrets:
```bash
modal secret list
```

---

## Cost Estimate

| Service | Monthly Cost |
|---------|--------------|
| Modal | $0-10 (pay per use, $30 free credit) |
| Supabase | $0 (free tier) |
| Census API | $0 (free) |
| **Total** | **$0-10/month** |

---

## What Happens After Deployment

1. **Nightly at 11 PM EST:** Pipeline runs automatically
2. **On GitHub push:** App redeploys via GitHub Actions
3. **Data flows to:** Supabase tables (parcel_zones, zoning_districts, etc.)

---

**Questions?** Ask Claude or check [Modal Docs](https://modal.com/docs).
