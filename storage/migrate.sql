-- ============================================================
-- Argentina Trends — Full Schema Migration
-- Paste this entire file into Supabase SQL Editor → Run
-- Safe to run multiple times (idempotent)
-- ============================================================

-- 1. Fix trends table (drop old schema, create correct one)
DROP TABLE IF EXISTS trends CASCADE;
CREATE TABLE trends (
  id            BIGSERIAL PRIMARY KEY,
  period_start  TIMESTAMPTZ,
  period_end    TIMESTAMPTZ,
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  topic_label   TEXT,
  keywords      TEXT[],
  post_count    INTEGER,
  avg_sentiment FLOAT,
  top_posts     JSONB,
  ai_summary    TEXT
);

-- 2. Create google_trends table
DROP TABLE IF EXISTS google_trends CASCADE;
CREATE TABLE google_trends (
  id          BIGSERIAL PRIMARY KEY,
  keyword     TEXT NOT NULL,
  value       INTEGER,
  captured_at TIMESTAMPTZ,
  UNIQUE(keyword, captured_at)
);

-- 3. Add missing columns to posts table
ALTER TABLE posts ADD COLUMN IF NOT EXISTS sentiment       TEXT;
ALTER TABLE posts ADD COLUMN IF NOT EXISTS sentiment_score FLOAT;
ALTER TABLE posts ADD COLUMN IF NOT EXISTS topic_id        INTEGER;

-- 4. Performance indexes
CREATE INDEX IF NOT EXISTS idx_posts_source  ON posts(source);
CREATE INDEX IF NOT EXISTS idx_posts_time    ON posts(collected_at DESC);
CREATE INDEX IF NOT EXISTS idx_trends_time   ON trends(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_gtrends_time  ON google_trends(captured_at DESC);
