---
name: everest-github-deployment
description: GitHub deployment operations for Everest Capital projects. Includes automated git operations, GitHub Actions workflow triggers, Cloudflare Pages deployment, and post-deploy verification. Repos include brevard-bidder-scraper, zonewise, life-os, spd-site-plan-dev. Uses REST API (not git clone). Triggers on: deploy, GitHub push, commit, workflow, CI/CD, Cloudflare, GitHub Actions.
---

# Everest GitHub Deployment

## Repository Catalog

| Repo | Purpose | Deploy Target |
|------|---------|---------------|
| `brevard-bidder-scraper` | BidDeed.AI platform | GitHub Actions |
| `zonewise` | Zoning intelligence | Cloudflare Pages |
| `life-os` | ADHD productivity | GitHub Actions |
| `spd-site-plan-dev` | Site plan AI | GitHub Actions |
| `tax-insurance-optimizer` | Tax module | GitHub Actions |

## Quick Start

```python
from scripts.commit_and_push import deploy_file

result = deploy_file(
    repo="breverdbidder/brevard-bidder-scraper",
    path="src/scrapers/new_scraper.py",
    content=file_content,
    message="Add new scraper module"
)
# Returns: {"sha": "abc123", "url": "https://github.com/..."}
```

## GitHub Token

```python
GITHUB_TOKEN = "$GITHUB_TOKEN (from secrets)"
```

Store in environment, never hardcode in committed files.

## API Operations

### Create/Update File
```python
import requests
import base64

def push_file(repo: str, path: str, content: str, message: str) -> dict:
    """Create or update a file via GitHub API."""
    
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Check if file exists (get SHA)
    existing = requests.get(url, headers=headers)
    sha = existing.json().get("sha") if existing.status_code == 200 else None
    
    # Prepare payload
    payload = {
        "message": message,
        "content": base64.b64encode(content.encode()).decode()
    }
    if sha:
        payload["sha"] = sha
    
    # Push
    response = requests.put(url, headers=headers, json=payload)
    return response.json()
```

### Delete File
```python
def delete_file(repo: str, path: str, message: str) -> dict:
    """Delete a file via GitHub API."""
    
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    # Get current SHA
    existing = requests.get(url, headers=headers)
    sha = existing.json()["sha"]
    
    # Delete
    response = requests.delete(url, headers=headers, json={
        "message": message,
        "sha": sha
    })
    return response.json()
```

### List Directory
```python
def list_directory(repo: str, path: str) -> list:
    """List files in a directory."""
    
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    response = requests.get(url, headers=headers)
    return response.json()
```

## Workflow Triggers

### Trigger Workflow Dispatch
```python
def trigger_workflow(repo: str, workflow: str, inputs: dict = None) -> dict:
    """Trigger a GitHub Actions workflow."""
    
    url = f"https://api.github.com/repos/{repo}/actions/workflows/{workflow}/dispatches"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    payload = {
        "ref": "main",
        "inputs": inputs or {}
    }
    
    response = requests.post(url, headers=headers, json=payload)
    return {"triggered": response.status_code == 204}
```

### Check Workflow Status
```python
def get_workflow_runs(repo: str, workflow: str, limit: int = 5) -> list:
    """Get recent workflow runs."""
    
    url = f"https://api.github.com/repos/{repo}/actions/workflows/{workflow}/runs"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    response = requests.get(url, headers=headers, params={"per_page": limit})
    return response.json()["workflow_runs"]
```

## Workflow Templates

### master_scraper.yml
```yaml
name: Master Scraper
on:
  schedule:
    - cron: '0 4 * * *'  # 11 PM EST
  workflow_dispatch:

jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run scraper
        env:
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
          REALFORECLOSE_USER: ${{ secrets.REALFORECLOSE_USER }}
          REALFORECLOSE_PASS: ${{ secrets.REALFORECLOSE_PASS }}
        run: python src/scrapers/master_scraper.py
```

### deploy-cloudflare.yml
```yaml
name: Deploy to Cloudflare
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install dependencies
        run: npm ci
      - name: Build
        run: npm run build
      - name: Deploy
        uses: cloudflare/pages-action@v1
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          projectName: zonewise
          directory: dist
```

## Post-Deploy Verification

### Verify File Exists
```python
def verify_deployment(repo: str, path: str, expected_sha: str = None) -> bool:
    """Verify file was deployed successfully."""
    
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return False
    
    if expected_sha:
        return response.json()["sha"] == expected_sha
    
    return True
```

### Verify Workflow Completed
```python
def wait_for_workflow(repo: str, workflow: str, timeout: int = 300) -> dict:
    """Wait for workflow to complete."""
    
    import time
    start = time.time()
    
    while time.time() - start < timeout:
        runs = get_workflow_runs(repo, workflow, limit=1)
        if runs:
            latest = runs[0]
            if latest["status"] == "completed":
                return {
                    "success": latest["conclusion"] == "success",
                    "conclusion": latest["conclusion"],
                    "url": latest["html_url"]
                }
        time.sleep(10)
    
    return {"success": False, "error": "timeout"}
```

## Deployment Rules

### NEVER Mark Complete Without Verification
```python
async def deploy_and_verify(repo: str, path: str, content: str, message: str):
    """Deploy file and verify it exists."""
    
    # Push file
    result = push_file(repo, path, content, message)
    
    # Verify
    verified = verify_deployment(repo, path, result["content"]["sha"])
    
    if not verified:
        raise DeploymentError(f"Failed to verify {path}")
    
    return result
```

### Commit Message Format
```
<type>: <description>

Types:
- feat: New feature
- fix: Bug fix
- refactor: Code refactoring
- docs: Documentation
- chore: Maintenance
- test: Tests

Examples:
- feat: Add BECA scraper v2 with 12 regex patterns
- fix: Handle session timeout in AcclaimWeb scraper
- docs: Update CLAUDE.md with skills loading section
```

## Secrets Management

### Required Secrets per Repo

**brevard-bidder-scraper:**
- `SUPABASE_KEY`
- `REALFORECLOSE_USER` / `REALFORECLOSE_PASS`
- `ACCLAIMWEB_USER` / `ACCLAIMWEB_PASS`
- `REALTDM_USER` / `REALTDM_PASS`
- `CENSUS_API_KEY`
- `ML_MODEL_KEY`

**zonewise:**
- `SUPABASE_KEY`
- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`

### Add Secret via API
```python
def add_secret(repo: str, name: str, value: str):
    """Add or update repository secret."""
    
    # Requires libsodium for encryption
    # Usually done via GitHub UI or CLI
    pass
```

## Error Handling

### Common Errors
```python
class DeploymentError(Exception):
    pass

class GitHubAPIError(Exception):
    pass

def handle_api_error(response):
    if response.status_code == 401:
        raise GitHubAPIError("Token expired or invalid")
    if response.status_code == 404:
        raise GitHubAPIError("Repository or file not found")
    if response.status_code == 409:
        raise GitHubAPIError("Conflict - file changed since last read")
    if response.status_code == 422:
        raise GitHubAPIError("Invalid request - check SHA")
```

### Retry Pattern
```python
@retry(max_attempts=3, backoff=2.0)
def push_with_retry(repo: str, path: str, content: str, message: str):
    return push_file(repo, path, content, message)
```

## Integration

- **BidDeed.AI**: Daily scraper workflows, model deployments
- **ZoneWise**: Cloudflare Pages auto-deploy
- **Life OS**: Task automation workflows
- **Skills**: Deploy skill updates to repos
