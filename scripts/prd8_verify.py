import json, urllib.request, sys, os

MGMT = os.environ["SUPABASE_MGMT_TOKEN"]
PROJ = "mocerqjnksmhcjzxrewo"

def sql(q):
    data = json.dumps({"query": q}).encode()
    req = urllib.request.Request(
        f"https://api.supabase.com/v1/projects/{PROJ}/database/query",
        data=data,
        headers={"Authorization": f"Bearer {MGMT}", "Content-Type": "application/json",
                 "User-Agent": "ZoneWise-PRD8-Verify"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.load(r)

r1 = sql("SELECT COUNT(*) as c FROM zone_standards WHERE confidence_score IS NULL")
r2 = sql("SELECT ROUND(confidence_score::numeric,2) as s, COUNT(*) c FROM zone_standards WHERE confidence_score IS NOT NULL GROUP BY 1 ORDER BY 1")
null_count = r1[0]['c']
print(f"NULL confidence remaining: {null_count} (target: 0)")
print(f"Score distribution: {r2}")
sys.exit(0 if null_count == 0 else 1)
