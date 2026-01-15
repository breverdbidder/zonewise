# ZoneWise Development Workflow
## Solving the 200K Context Limit Problem

### The Problem
- Claude.ai chat: 200K token limit (ALL models including Opus 4.5)
- Tonight you hit limits multiple times
- Context fills up → lose history → restart → repeat info

### Solution: Chunked Development + Auto-Checkpoint

## Option 1: Claude Code (RECOMMENDED FOR TONIGHT)

```bash
# Terminal on your machine
cd /path/to/zonewise
claude
```

**Why it works:**
- Reads CLAUDE.md automatically (just deployed)
- Auto-compacts when hitting limit (keeps working)
- No message limits on Max plan
- 7-hour autonomous sessions

**Start command:**
```
Build the CrewAI Compliance Agent using the zoning_districts data in Supabase.
Test with 3 properties. Deploy to Render.com when ready.
```

---

## Option 2: Chunked Chat Sessions (If Claude Code unavailable)

### Session Structure

| Chat | Focus | Token Budget | Key Files |
|------|-------|--------------|-----------|
| 1 | Agent Architecture | 150K | pipeline/, CLAUDE.md |
| 2 | Frontend | 150K | frontend/ |
| 3 | API/Backend | 150K | zonewise_api.py, backend/ |
| 4 | Database/Queries | 150K | sql/, supabase/ |

### Start Each Session With:
```
Resume ZoneWise [component] development.
Load checkpoint from Supabase.
Current focus: [specific task]
```

### End Each Session With:
```
Checkpoint this session to Supabase before we hit the limit.
```

---

## Option 3: Claude Project (Persistent Context)

1. Go to claude.ai → Projects → New Project
2. Name: "ZoneWise Development"
3. Upload these files:
   - CLAUDE.md
   - POC_STATUS.md
   - docs/PRD_AI_FIRST.md
   - docs/TECHNICAL_SPECS.md
4. Set Project Instructions (keeps context small)

**RAG Benefit:** Only loads relevant chunks, not entire files

---

## Auto-Checkpoint Protocol

At 75% context (150K tokens), I will:

1. Save to Supabase:
```bash
curl -X POST "https://mocerqjnksmhcjzxrewo.supabase.co/rest/v1/claude_context_checkpoints" \
  -H "apikey: $SUPABASE_SERVICE_KEY" \
  -d '{
    "conversation_id": "zonewise-agent-2026-01-15",
    "checkpoint_number": 1,
    "context_percent": 75,
    "checkpoint_summary": "...",
    "active_tasks": ["..."],
    "key_points": {...}
  }'
```

2. Tell you: "📌 CHECKPOINT SAVED. Start new chat with 'resume zonewise'"

3. In new chat, I query:
```bash
curl "https://mocerqjnksmhcjzxrewo.supabase.co/rest/v1/claude_context_checkpoints?conversation_id=like.zonewise*&order=created_at.desc&limit=1"
```

---

## Tonight's Action Plan

### If you want to continue in Claude.ai:
1. Start NEW chat now (fresh 200K)
2. Say: "Resume ZoneWise. Build CrewAI Compliance Agent."
3. I'll load checkpoint + CLAUDE.md from GitHub

### If you want Claude Code:
1. Open terminal
2. `cd zonewise && claude`
3. Paste: "Build CrewAI Compliance Agent using zoning_districts data. Test with 3 properties."

### Keys you need (for Claude Code):
- GITHUB_TOKEN: In your .zshrc or .bashrc
- SUPABASE_SERVICE_KEY: In .env file

---

## What I Commit To

✅ Checkpoint at 75% (150K) - NOT 80% (less margin)
✅ Save to Supabase claude_context_checkpoints
✅ Resume with full context in new chat
✅ Use CLAUDE.md for project memory
✅ Deploy code autonomously to GitHub
