#!/usr/bin/env python3
"""
Weekly Repository Discovery - Updates GITHUB_REPO_MEGA_LIBRARY.md
Runs every Sunday 11 PM EST via GitHub Actions
"""

import requests
import json
from datetime import datetime
import os

ECOSYSTE_API = "https://awesome.ecosyste.ms/api"
CATEGORIES = [
    "python", "machine-learning", "web-scraping", "real-estate",
    "pdf-processing", "security", "devops", "data-science",
    "ai", "agents", "langchain", "react", "typescript", "docker"
]

def fetch_trending_repos(category, limit=50):
    """Fetch trending repos for category from ecosyste.ms"""
    try:
        url = f"{ECOSYSTE_API}/projects"
        params = {"topic": category, "sort": "stars", "limit": limit}
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"⚠️  Failed to fetch {category}: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error fetching {category}: {e}")
        return []

def quality_score(repo):
    """Calculate 0-100 quality score"""
    score = 0
    
    # Stars (0-30 points)
    stars = repo.get('stars', 0)
    if stars >= 10000:
        score += 30
    elif stars >= 5000:
        score += 25
    elif stars >= 1000:
        score += 20
    elif stars >= 500:
        score += 15
    elif stars >= 100:
        score += 10
    else:
        score += min(10, stars / 10)
    
    # Activity (0-20 points)
    last_pushed = repo.get('last_pushed')
    if last_pushed:
        try:
            last_push_date = datetime.fromisoformat(last_pushed.replace('Z', '+00:00'))
            days_since_update = (datetime.now(last_push_date.tzinfo) - last_push_date).days
            
            if days_since_update < 30:
                score += 20
            elif days_since_update < 90:
                score += 15
            elif days_since_update < 180:
                score += 10
            elif days_since_update < 365:
                score += 5
        except:
            score += 5  # Default if date parsing fails
    
    # Community (0-20 points)
    forks = repo.get('forks', 0)
    if forks >= 1000:
        score += 20
    elif forks >= 500:
        score += 15
    elif forks >= 100:
        score += 10
    else:
        score += min(10, forks / 10)
    
    # Documentation (0-15 points)
    has_readme = repo.get('has_readme', False)
    has_wiki = repo.get('has_wiki', False)
    
    if has_readme:
        score += 10
    if has_wiki:
        score += 5
    
    # Security (0-15 points)
    has_license = repo.get('license') is not None
    if has_license:
        score += 10
    
    # Assume no vulnerabilities if not specified
    score += 5
    
    return int(min(100, score))

def categorize_repo(repo):
    """Determine category based on topics and description"""
    topics = [t.lower() for t in repo.get('topics', [])]
    description = (repo.get('description') or '').lower()
    name = repo.get('name', '').lower()
    
    # Python ecosystem
    if any(t in topics for t in ['python', 'pandas', 'numpy', 'django', 'flask']):
        return 'python'
    
    # AI & ML
    if any(t in topics for t in ['machine-learning', 'ai', 'ml', 'deep-learning', 'neural-network']):
        return 'ai-ml'
    
    # Agents
    if any(t in topics for t in ['agents', 'langchain', 'langgraph', 'autogen', 'crewai']):
        return 'agents'
    
    # Web scraping
    if any(t in topics for t in ['scraping', 'crawler', 'selenium', 'puppeteer', 'playwright']):
        return 'web-scraping'
    
    # Real estate
    if any(word in description or word in name for word in ['real estate', 'property', 'zillow', 'redfin']):
        return 'real-estate'
    
    # Security
    if any(t in topics for t in ['security', 'cybersecurity', 'pentesting', 'vulnerability']):
        return 'security'
    
    # DevOps
    if any(t in topics for t in ['devops', 'docker', 'kubernetes', 'cicd', 'terraform']):
        return 'devops'
    
    # Data Science
    if any(t in topics for t in ['data-science', 'analytics', 'visualization', 'jupyter']):
        return 'data-science'
    
    # Web Development
    if any(t in topics for t in ['react', 'vue', 'angular', 'frontend', 'backend', 'web-development']):
        return 'web-dev'
    
    # Default
    return 'misc'

def update_library():
    """Main update function"""
    print("🔄 Starting weekly repository discovery...")
    print(f"⏰ Time: {datetime.now().isoformat()}")
    
    all_repos = []
    
    for category in CATEGORIES:
        print(f"\n📂 Fetching {category}...")
        repos = fetch_trending_repos(category)
        
        for repo in repos:
            score = quality_score(repo)
            
            # Only include repos with score >= 60
            if score >= 60:
                all_repos.append({
                    'name': repo.get('name', 'Unknown'),
                    'full_name': repo.get('full_name', ''),
                    'url': repo.get('html_url', ''),
                    'stars': repo.get('stars', 0),
                    'forks': repo.get('forks', 0),
                    'description': repo.get('description', ''),
                    'topics': repo.get('topics', []),
                    'category': categorize_repo(repo),
                    'score': score,
                    'status': 'EVALUATE' if score >= 80 else 'CONDITIONAL',
                    'last_pushed': repo.get('last_pushed', ''),
                    'license': repo.get('license', {}).get('name', 'Unknown') if repo.get('license') else 'None'
                })
    
    # Remove duplicates (by full_name)
    seen = set()
    unique_repos = []
    for repo in all_repos:
        if repo['full_name'] not in seen:
            seen.add(repo['full_name'])
            unique_repos.append(repo)
    
    # Sort by score (highest first)
    unique_repos.sort(key=lambda x: x['score'], reverse=True)
    
    # Save to file
    output_file = 'discovered_repos.json'
    with open(output_file, 'w') as f:
        json.dump(unique_repos, f, indent=2)
    
    print(f"\n✅ Discovered {len(unique_repos)} quality repositories")
    print(f"📊 Breakdown by category:")
    
    # Category breakdown
    categories = {}
    for repo in unique_repos:
        cat = repo['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"   {cat}: {count}")
    
    print(f"\n💾 Saved to {output_file}")
    
    return len(unique_repos)

if __name__ == "__main__":
    try:
        total = update_library()
        print(f"\n🎉 Success! Discovered {total} repositories")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise
