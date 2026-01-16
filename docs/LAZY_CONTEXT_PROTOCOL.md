# Lazy-Context Protocol (LCP)

**Version:** 1.0.0  
**Created:** January 16, 2026  
**Purpose:** Minimize context consumption for long-running development projects  
**Problem Solved:** 200K token chat limit causing frequent session resets

---

## Overview

The Lazy-Context Protocol enables Claude to maintain project continuity across sessions without loading full project state upfront. Instead of consuming 50-100K tokens with complete context, LCP loads only ~5K tokens initially and fetches additional context on-demand.

**Inspired by:** Claude Code's MCP Tool Search lazy-loading pattern (85% token reduction)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SESSION START (~5K tokens)                │
├─────────────────────────────────────────────────────────────┤
│  • Latest checkpoint from Supabase (task, blockers, next)   │
│  • Active file PATHS only (not contents)                    │
│  • Last 3-5 decisions made                                  │
│  • Extraction/progress metrics                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   ON-DEMAND LOADING                          │
├─────────────────────────────────────────────────────────────┤
│  TRIGGER                      │  ACTION                      │
│  ─────────────────────────────┼────────────────────────────  │
│  Editing a file               │  Fetch from GitHub           │
│  Need architecture context    │  Load CLAUDE.md from repo    │
│  Historical decisions needed  │  Query past_chats tool       │
│  Schema questions             │  Fetch specific SQL file     │
│  API integration              │  Load relevant skill docs    │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation

### 1. Checkpoint Table (Supabase)

```sql
CREATE TABLE zonewise_checkpoints (
    id UUID PRIMARY KEY,
    session_id TEXT NOT NULL,
    current_task TEXT NOT NULL,
    task_status TEXT DEFAULT 'in_progress',
    blockers JSONB DEFAULT '[]',
    next_actions JSONB DEFAULT '[]',
    active_files JSONB DEFAULT '[]',      -- Paths only!
    recent_decisions JSONB DEFAULT '[]',
    extraction_progress JSONB DEFAULT '{}',
    token_estimate INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    summary TEXT
);
```

### 2. Session Start Protocol

When user says "resume", "continue", or "where were we":

```python
# Step 1: Load latest checkpoint (~2K tokens)
checkpoint = supabase.from_('zonewise_checkpoints')
    .select('*')
    .order('created_at', desc=True)
    .limit(1)
    .execute()

# Step 2: Search recent conversations (~1K tokens)
recent = recent_chats(n=3)

# Step 3: Search for specific context (~1K tokens)  
context = conversation_search("zonewise blockers progress")

# Step 4: Synthesize and continue
# Total: ~5K tokens vs 50-100K for full load
```

### 3. Auto-Checkpoint Protocol

Create checkpoint when:
- Token usage reaches 75% (150K of 200K)
- Major task completes
- Blocker encountered
- Session about to end
- User requests checkpoint

```python
async def auto_checkpoint(session_id: str, context: dict):
    return await supabase.rpc('create_zonewise_checkpoint', {
        'p_session_id': session_id,
        'p_current_task': context['current_task'],
        'p_task_status': context['status'],
        'p_blockers': context['blockers'],
        'p_next_actions': context['next_actions'],
        'p_active_files': context['active_files'],
        'p_extraction_progress': context['progress'],
        'p_token_estimate': context['tokens_used'],
        'p_summary': context['one_line_summary']
    })
```

---

## Usage Patterns

### Pattern 1: Resume Session

**User says:** "Resume ZoneWise work"

**Claude executes:**
1. `recent_chats(n=3)` - Get last 3 conversations
2. `conversation_search("zonewise extraction progress blockers")` - Find relevant context
3. Query Supabase checkpoint table
4. Synthesize into compact status
5. Continue work without asking clarifying questions

### Pattern 2: Mid-Session Checkpoint

**Trigger:** Token estimate > 150K OR major milestone

**Claude executes:**
1. Summarize current state in structured format
2. Insert checkpoint to Supabase
3. Inform user: "📍 Checkpoint saved. Safe to continue or resume later."

### Pattern 3: On-Demand File Load

**User says:** "Fix the parser.py bug"

**Claude executes:**
1. Check if file path in active_files
2. Fetch file content from GitHub (not pre-loaded)
3. Make edits
4. Commit changes
5. Update checkpoint with modified_files

---

## Token Budget Guidelines

| Component | Max Tokens | Purpose |
|-----------|------------|---------|
| System prompt + memory | 15-20K | Fixed overhead |
| Checkpoint load | 2-3K | Session state |
| Recent chats context | 2-3K | Continuity |
| Working buffer | 150-170K | Actual development |
| **Checkpoint threshold** | **150K** | When to save |

---

## Checkpoint Content Structure

```json
{
  "session_id": "zonewise-2026-01-16-abc123",
  "checkpoint_number": 5,
  "current_task": "Extracting Titusville zoning districts via Browserless",
  "task_status": "in_progress",
  "blockers": [
    "eLaws sites returning HTTP 503 (6 jurisdictions affected)",
    "Rockledge Municode needs waitForSelector parameter"
  ],
  "next_actions": [
    "Complete Titusville extraction (10 districts)",
    "Test Rockledge with extended waits",
    "Try PDF fallback for small jurisdictions"
  ],
  "active_files": [
    "municipal_code_extractor.py",
    "zonewise_extraction_results.json",
    "database/cache_schema.sql"
  ],
  "recent_decisions": [
    {
      "decision": "Use Browserless for Municode sites",
      "rationale": "JavaScript rendering required, Firecrawl fails",
      "timestamp": "2026-01-16T02:00:00Z"
    },
    {
      "decision": "Skip Zoneomics API, build Firecrawl cache",
      "rationale": "$489/mo vs $40/mo, 10x cost savings",
      "timestamp": "2026-01-15T22:00:00Z"
    }
  ],
  "extraction_progress": {
    "total_jurisdictions": 17,
    "completed": 5,
    "districts_extracted": 47,
    "percent_complete": 25,
    "jurisdictions_done": ["indian_harbour_beach", "satellite_beach", "melbourne", "cocoa", "titusville"]
  },
  "token_estimate": 145000,
  "summary": "ZoneWise 25% complete. Browserless working for Municode. eLaws down."
}
```

---

## Integration with Existing Tools

### past_chats Tools
- `conversation_search` - Find specific context by keywords
- `recent_chats` - Get chronological history

### GitHub Integration
- Fetch files on-demand instead of pre-loading
- Commit changes immediately (no local state)
- Use repo as source of truth

### Supabase Integration
- `zonewise_checkpoints` table for structured state
- `create_zonewise_checkpoint()` function for atomic saves
- `v_latest_checkpoints` view for quick lookup

---

## Anti-Patterns (What NOT to Do)

❌ **Don't** load full file contents at session start  
❌ **Don't** include entire conversation history in context  
❌ **Don't** repeat information already in memory/preferences  
❌ **Don't** ask "where did we leave off?" - search and synthesize instead  
❌ **Don't** wait until token limit hit to checkpoint  

---

## Success Metrics

| Metric | Before LCP | After LCP | Improvement |
|--------|------------|-----------|-------------|
| Session start overhead | 50-100K tokens | 5-10K tokens | 80-90% |
| Usable working buffer | 100-150K tokens | 170-180K tokens | 20-30% |
| Context loss on resume | High | Minimal | Eliminated |
| Checkpoint recovery | Manual | Automated | 100% |

---

## Commands

**For Users:**
- "resume" / "continue" / "where were we" → Triggers LCP resume
- "checkpoint" / "save state" → Manual checkpoint
- "show checkpoint" → Display current state

**For Claude:**
- Always checkpoint at 150K tokens
- Never claim "no context" without checking all 3 sources
- Synthesize, don't ask redundant questions

---

## Version History

- **1.0.0** (2026-01-16): Initial release for ZoneWise project
