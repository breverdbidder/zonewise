# Task: ZoneWise.AI Greptile Security & Code Evaluation

## Objective
Run a comprehensive security and code quality evaluation against the zonewise-desktop and zonewise-web repositories using the Greptile API, then produce a detailed markdown report.

## Prerequisites
- Greptile API Key: stored in `GREPTILE_API_KEY` env var (GitHub Secret)
- GitHub PAT: stored in `GITHUB_TOKEN` env var (GitHub Secret)
- Both repos already indexed in Greptile: `breverdbidder/zonewise-desktop`, `breverdbidder/zonewise-web`

## Execution Steps

### Step 1: Verify repo index status
```bash
# Ensure env vars are set
# PowerShell: $env:GREPTILE_API_KEY = "your-key"; $env:GITHUB_TOKEN = "your-pat"
# Bash: export GREPTILE_API_KEY="your-key"; export GITHUB_TOKEN="your-pat"

for repo in "breverdbidder/zonewise-desktop" "breverdbidder/zonewise-web"; do
  encoded=$(python3 -c "import urllib.parse; print(urllib.parse.quote('github:main:${repo}', safe=''))")
  curl -s "https://api.greptile.com/v2/repositories/${encoded}" \
    -H "Authorization: Bearer ${GREPTILE_API_KEY}" \
    -H "X-Github-Token: ${GITHUB_TOKEN}" | python3 -m json.tool
done
```

If status is not "completed", re-index first:
```bash
curl -s -X POST "https://api.greptile.com/v2/repositories" \
  -H "Authorization: Bearer ${GREPTILE_API_KEY}" \
  -H "X-Github-Token: ${GITHUB_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"remote":"github","repository":"breverdbidder/zonewise-desktop","branch":"main","reload":true}'
```

### Step 2: Run the audit script
```bash
chmod +x greptile-security-audit.sh
bash greptile-security-audit.sh
```

### Step 3: Review and store
1. Review the generated markdown report in `greptile-audit-report/`
2. Push to `docs/assessments/` in the zonewise monorepo per Security & Value Assessment protocol
3. If overall score ≥80: ADOPT. If 60-79: EVALUATE with action items. If <60: flag to Ariel.

## Query Categories (13 total)
1. Executive Summary — architecture, frameworks, top concerns
2. Authentication & Authorization — JWT, sessions, RBAC, privilege escalation
3. API Security & Input Validation — injection, CORS, rate limiting
4. Dependency & Supply Chain — CVEs, version pinning, abandoned packages
5. Secrets & Credential Management — hardcoded keys, .env exposure
6. Data Handling & Privacy — PII, encryption, data leakage
7. Error Handling & Logging — info leakage, unhandled errors
8. Architecture & Code Quality — patterns, maintainability, tech debt
9. Frontend Security — XSS, CSRF, CSP, clickjacking
10. Performance & Scalability — N+1, memory leaks, bundle size
11. Test Coverage & CI/CD — test types, coverage, SAST/DAST
12. Critical Findings — Top 10 prioritized with remediations
13. Security Scorecard — Weighted score, ADOPT/EVALUATE/CONDITIONAL/REJECT verdict

## API Details
- Base URL: `https://api.greptile.com/v2`
- Endpoint: `POST /query`
- Use `genius: true` for enhanced analysis
- Use consistent `sessionId` across all queries for context continuity
- 10-second delay between queries to avoid rate limiting

## Success Criteria
- [ ] All 13 sections populated with Greptile analysis
- [ ] Specific file paths and line numbers cited for vulnerabilities
- [ ] Final weighted security score calculated
- [ ] Report saved to `docs/assessments/zonewise-security-audit-YYYYMMDD.md`
- [ ] GitHub commit with assessment results
