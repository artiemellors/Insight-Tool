-- ============================================================================
-- Insight Tool — Supabase schema migration
-- Run this in the Supabase SQL Editor (Dashboard → SQL Editor → New Query)
-- ============================================================================

-- Studies: top-level research project container
CREATE TABLE IF NOT EXISTS studies (
    study_id       TEXT PRIMARY KEY,
    study_name     TEXT NOT NULL DEFAULT '',
    product_area   TEXT NOT NULL DEFAULT '',
    research_objectives JSONB NOT NULL DEFAULT '[]'::jsonb,
    interview_guide     JSONB,   -- full InterviewGuide (sections, questions, probes)
    codebook            JSONB,   -- full Codebook (themes, codes, indicators)
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Sessions: one per interview transcript, FK to study
CREATE TABLE IF NOT EXISTS sessions (
    session_id       TEXT PRIMARY KEY,
    study_id         TEXT NOT NULL REFERENCES studies(study_id) ON DELETE CASCADE,
    participant_id   TEXT NOT NULL,
    transcript       JSONB NOT NULL DEFAULT '[]'::jsonb,  -- list of Turn objects
    coverage_result  JSONB NOT NULL DEFAULT '[]'::jsonb,  -- list of QuestionCoverageResult
    coded_turns      JSONB NOT NULL DEFAULT '[]'::jsonb,  -- list of CodedTurn
    emergent_themes  JSONB NOT NULL DEFAULT '[]'::jsonb,  -- list of EmergentTheme
    quality_scorecard JSONB,                               -- SessionScorecard
    review_status    TEXT NOT NULL DEFAULT 'pending',
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index for fast study → sessions lookups
CREATE INDEX IF NOT EXISTS idx_sessions_study_id ON sessions(study_id);

-- Index for filtering by review status
CREATE INDEX IF NOT EXISTS idx_sessions_review_status ON sessions(review_status);

-- ============================================================================
-- Row-Level Security (RLS)
-- Enable when Supabase Auth is configured. For now, policies are permissive.
-- ============================================================================

ALTER TABLE studies  ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;

-- Drop existing policies so this migration is re-runnable
DROP POLICY IF EXISTS "Allow all for authenticated users" ON studies;
DROP POLICY IF EXISTS "Allow all for authenticated users" ON sessions;
DROP POLICY IF EXISTS "Service role full access" ON studies;
DROP POLICY IF EXISTS "Service role full access" ON sessions;

-- Allow all operations for authenticated users (tighten per-team in Phase 2)
CREATE POLICY "Allow all for authenticated users" ON studies
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Allow all for authenticated users" ON sessions
    FOR ALL USING (auth.role() = 'authenticated');

-- Allow full access when using the service_role key (server-side)
CREATE POLICY "Service role full access" ON studies
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access" ON sessions
    FOR ALL USING (auth.role() = 'service_role');
