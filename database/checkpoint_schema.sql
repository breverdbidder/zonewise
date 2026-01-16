-- ==========================================
-- ZONEWISE SESSION CHECKPOINT SCHEMA
-- Purpose: Enable lazy-context loading for Claude sessions
-- Solves: 200K token limit causing frequent session resets
-- ==========================================

-- Drop existing if needed (comment out in production)
-- DROP TABLE IF EXISTS zonewise_checkpoints CASCADE;

-- Main checkpoint table
CREATE TABLE IF NOT EXISTS zonewise_checkpoints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Session identification
    session_id TEXT NOT NULL,                    -- Claude conversation ID or custom ID
    checkpoint_number INTEGER DEFAULT 1,         -- Auto-increment per session
    
    -- Minimal context (always loaded ~2K tokens)
    current_task TEXT NOT NULL,                  -- What Claude was working on
    task_status TEXT DEFAULT 'in_progress' CHECK (task_status IN ('in_progress', 'blocked', 'completed', 'deferred')),
    blockers JSONB DEFAULT '[]'::jsonb,          -- Array of blocker descriptions
    next_actions JSONB DEFAULT '[]'::jsonb,      -- Array of next steps
    
    -- File references (paths only, not contents ~500 tokens)
    active_files JSONB DEFAULT '[]'::jsonb,      -- ["src/skills/zonewize/analyzer.py", ...]
    modified_files JSONB DEFAULT '[]'::jsonb,    -- Files changed this session
    
    -- Decision log (last 5 decisions ~1K tokens)
    recent_decisions JSONB DEFAULT '[]'::jsonb,  -- [{decision, rationale, timestamp}, ...]
    
    -- Progress tracking
    extraction_progress JSONB DEFAULT '{}'::jsonb, -- {"total_jurisdictions": 17, "completed": 5, "districts": 47}
    
    -- Metadata
    token_estimate INTEGER,                      -- Estimated tokens when checkpoint created
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by TEXT DEFAULT 'claude',            -- 'claude' or 'user'
    
    -- Searchability
    tags TEXT[] DEFAULT '{}',                    -- ['extraction', 'municode', 'blocked']
    summary TEXT                                 -- One-line human-readable summary
);

-- Index for fast session lookups
CREATE INDEX IF NOT EXISTS idx_zonewise_checkpoints_session 
    ON zonewise_checkpoints(session_id, created_at DESC);

-- Index for finding recent checkpoints
CREATE INDEX IF NOT EXISTS idx_zonewise_checkpoints_recent 
    ON zonewise_checkpoints(created_at DESC);

-- Index for tag-based search
CREATE INDEX IF NOT EXISTS idx_zonewise_checkpoints_tags 
    ON zonewise_checkpoints USING GIN(tags);

-- Auto-cleanup: Keep only last 50 checkpoints per session
CREATE OR REPLACE FUNCTION cleanup_old_checkpoints()
RETURNS TRIGGER AS $$
BEGIN
    DELETE FROM zonewise_checkpoints
    WHERE session_id = NEW.session_id
    AND id NOT IN (
        SELECT id FROM zonewise_checkpoints
        WHERE session_id = NEW.session_id
        ORDER BY created_at DESC
        LIMIT 50
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_cleanup_checkpoints ON zonewise_checkpoints;
CREATE TRIGGER trigger_cleanup_checkpoints
    AFTER INSERT ON zonewise_checkpoints
    FOR EACH ROW
    EXECUTE FUNCTION cleanup_old_checkpoints();

-- View for latest checkpoint per session
CREATE OR REPLACE VIEW v_latest_checkpoints AS
SELECT DISTINCT ON (session_id)
    id,
    session_id,
    current_task,
    task_status,
    blockers,
    next_actions,
    active_files,
    extraction_progress,
    summary,
    created_at
FROM zonewise_checkpoints
ORDER BY session_id, created_at DESC;

-- Function to create checkpoint (callable from Claude)
CREATE OR REPLACE FUNCTION create_zonewise_checkpoint(
    p_session_id TEXT,
    p_current_task TEXT,
    p_task_status TEXT DEFAULT 'in_progress',
    p_blockers JSONB DEFAULT '[]'::jsonb,
    p_next_actions JSONB DEFAULT '[]'::jsonb,
    p_active_files JSONB DEFAULT '[]'::jsonb,
    p_modified_files JSONB DEFAULT '[]'::jsonb,
    p_recent_decisions JSONB DEFAULT '[]'::jsonb,
    p_extraction_progress JSONB DEFAULT '{}'::jsonb,
    p_token_estimate INTEGER DEFAULT NULL,
    p_tags TEXT[] DEFAULT '{}',
    p_summary TEXT DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    v_checkpoint_number INTEGER;
    v_new_id UUID;
BEGIN
    -- Get next checkpoint number for this session
    SELECT COALESCE(MAX(checkpoint_number), 0) + 1 
    INTO v_checkpoint_number
    FROM zonewise_checkpoints
    WHERE session_id = p_session_id;
    
    -- Insert new checkpoint
    INSERT INTO zonewise_checkpoints (
        session_id,
        checkpoint_number,
        current_task,
        task_status,
        blockers,
        next_actions,
        active_files,
        modified_files,
        recent_decisions,
        extraction_progress,
        token_estimate,
        tags,
        summary
    ) VALUES (
        p_session_id,
        v_checkpoint_number,
        p_current_task,
        p_task_status,
        p_blockers,
        p_next_actions,
        p_active_files,
        p_modified_files,
        p_recent_decisions,
        p_extraction_progress,
        p_token_estimate,
        p_tags,
        p_summary
    )
    RETURNING id INTO v_new_id;
    
    RETURN v_new_id;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions (adjust role as needed)
-- GRANT ALL ON zonewise_checkpoints TO authenticated;
-- GRANT ALL ON v_latest_checkpoints TO authenticated;
-- GRANT EXECUTE ON FUNCTION create_zonewise_checkpoint TO authenticated;

-- ==========================================
-- EXAMPLE USAGE
-- ==========================================

-- Creating a checkpoint:
/*
SELECT create_zonewise_checkpoint(
    'zonewise-session-2026-01-16',
    'Extracting Titusville zoning districts via Browserless',
    'in_progress',
    '["eLaws sites returning 503", "Rockledge Municode needs waitForSelector"]'::jsonb,
    '["Complete Titusville extraction", "Test Rockledge with extended waits", "Try PDF fallback for small jurisdictions"]'::jsonb,
    '["municipal_code_extractor.py", "zonewise_extraction_results.json"]'::jsonb,
    '["zonewise_extraction_results.json"]'::jsonb,
    '[{"decision": "Use Browserless for Municode", "rationale": "JavaScript rendering required", "timestamp": "2026-01-16T02:00:00Z"}]'::jsonb,
    '{"total_jurisdictions": 17, "completed": 5, "districts_extracted": 47, "percent_complete": 25}'::jsonb,
    5000,
    ARRAY['extraction', 'browserless', 'municode'],
    'ZoneWise extraction 25% complete, Browserless working for Titusville'
);
*/

-- Retrieving latest checkpoint:
/*
SELECT * FROM v_latest_checkpoints 
WHERE session_id LIKE 'zonewise%'
ORDER BY created_at DESC
LIMIT 1;
*/
