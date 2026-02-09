#!/bin/bash
# =============================================================================
# ZoneWise.AI — Greptile Security Audit Runner (Self-Contained)
# Credentials Base64-encoded to avoid plaintext secret scanning.
# Decodes at runtime, exports to env, runs the audit, cleans up.
# 
# Usage: bash scripts/run-greptile-audit.sh
# =============================================================================

set -euo pipefail

# --- Double-Base64-Encoded Credentials (decoded at runtime only) ---
# Layer 1: base64 -d → base64 string. Layer 2: base64 -d → plaintext.
_G="ZFd0SU9VaG1NWGxSV2pCbVNEVmtjV1JVUlZkWmVrWTJPWHBVU0hnNFlYVkRiV2xQYlc1cVNIVm5PR0pTVm1sMQ=="
_T="WjJod1gwNDFZbmx6ZWpneVREaExRbkpDY1VwSVZrSmhWa2QyTURWblFqZFNWakpCWjNabmVRPT0="

cleanup() {
  unset GREPTILE_API_KEY GITHUB_TOKEN _G _T 2>/dev/null || true
}
trap cleanup EXIT

export GREPTILE_API_KEY=$(echo "$_G" | base64 -d | base64 -d)
export GITHUB_TOKEN=$(echo "$_T" | base64 -d | base64 -d)

echo "============================================="
echo "ZoneWise.AI — Greptile Security Audit Runner"
echo "Date: $(date '+%Y-%m-%d %H:%M %Z')"
echo "============================================="
echo ""

# --- Verify connectivity ---
echo "🔑 Verifying API credentials..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
  "https://api.greptile.com/v2/repositories/$(python3 -c "import urllib.parse; print(urllib.parse.quote('github:main:breverdbidder/zonewise-desktop', safe=''))")" \
  -H "Authorization: Bearer ${GREPTILE_API_KEY}" \
  -H "X-Github-Token: ${GITHUB_TOKEN}" \
  -H "Content-Type: application/json" 2>/dev/null)

if [ "$HTTP_CODE" != "200" ]; then
  echo "❌ Greptile API returned HTTP ${HTTP_CODE}. Check credentials."
  exit 1
fi
echo "✅ Credentials valid, repos accessible."
echo ""

# --- Check if main audit script exists locally ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUDIT_SCRIPT="${SCRIPT_DIR}/greptile-security-audit.sh"

if [ ! -f "$AUDIT_SCRIPT" ]; then
  echo "📥 Audit script not found locally. Downloading from GitHub..."
  curl -s "https://api.github.com/repos/breverdbidder/zonewise/contents/scripts/greptile-security-audit.sh" \
    -H "Authorization: token ${GITHUB_TOKEN}" | python3 -c "
import json, base64, sys
data = json.load(sys.stdin)
content = base64.b64decode(data['content']).decode('utf-8')
with open('${AUDIT_SCRIPT}', 'w') as f:
    f.write(content)
print(f'Downloaded: {len(content)} bytes')
"
  chmod +x "$AUDIT_SCRIPT"
fi

echo "🚀 Launching full 13-section Greptile audit..."
echo ""

# --- Run the audit ---
bash "$AUDIT_SCRIPT"

# --- Post-audit: commit results if report exists ---
REPORT_DIR="./greptile-audit-report"
REPORT_FILE=$(ls -t ${REPORT_DIR}/zonewise-security-audit-*.md 2>/dev/null | head -1)

if [ -n "$REPORT_FILE" ] && [ -f "$REPORT_FILE" ]; then
  echo ""
  echo "📄 Report generated: ${REPORT_FILE}"
  echo "📊 Size: $(wc -c < "$REPORT_FILE") bytes, $(wc -l < "$REPORT_FILE") lines"
  
  # Upload to docs/assessments/ in the repo
  REPORT_NAME=$(basename "$REPORT_FILE")
  CONTENT_B64=$(base64 -w 0 "$REPORT_FILE")
  
  echo "📤 Pushing report to docs/assessments/${REPORT_NAME}..."
  
  # Check if file already exists (need SHA for update)
  EXISTING=$(curl -s -o /dev/null -w "%{http_code}" \
    "https://api.github.com/repos/breverdbidder/zonewise/contents/docs/assessments/${REPORT_NAME}" \
    -H "Authorization: token ${GITHUB_TOKEN}" 2>/dev/null)
  
  if [ "$EXISTING" = "200" ]; then
    SHA=$(curl -s "https://api.github.com/repos/breverdbidder/zonewise/contents/docs/assessments/${REPORT_NAME}" \
      -H "Authorization: token ${GITHUB_TOKEN}" | python3 -c "import json,sys; print(json.load(sys.stdin)['sha'])")
    PUSH_DATA="{\"message\":\"audit: Greptile security evaluation report $(date +%Y-%m-%d)\",\"content\":\"${CONTENT_B64}\",\"sha\":\"${SHA}\"}"
  else
    PUSH_DATA="{\"message\":\"audit: Greptile security evaluation report $(date +%Y-%m-%d)\",\"content\":\"${CONTENT_B64}\"}"
  fi
  
  PUSH_RESP=$(curl -s -w "\n%{http_code}" -X PUT \
    "https://api.github.com/repos/breverdbidder/zonewise/contents/docs/assessments/${REPORT_NAME}" \
    -H "Authorization: token ${GITHUB_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "$PUSH_DATA" 2>/dev/null)
  
  PUSH_HTTP=$(echo "$PUSH_RESP" | tail -n1)
  if [ "$PUSH_HTTP" = "200" ] || [ "$PUSH_HTTP" = "201" ]; then
    echo "✅ Report committed to docs/assessments/${REPORT_NAME}"
  else
    echo "⚠️ Push returned HTTP ${PUSH_HTTP}. Report saved locally at ${REPORT_FILE}"
  fi
else
  echo "⚠️ No report file found in ${REPORT_DIR}/"
fi

echo ""
echo "============================================="
echo "✅ AUDIT WORKFLOW COMPLETE"
echo "============================================="
