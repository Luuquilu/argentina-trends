-- Run this in your Supabase SQL editor

CREATE TABLE IF NOT EXISTS posts (
    id BIGSERIAL PRIMARY KEY,
    source TEXT NOT NULL,
    external_id TEXT,
    title TEXT,
    body TEXT,
    url TEXT,
    author TEXT,
    score INTEGER DEFAULT 0,
    published_at TIMESTAMPTz,
    collected_at TIMESTAMPTz DEFAULT NOW(),
    UNIQUE(source, external_id)
);

CREATE TABLE IF NOT EXISTS trends (
    id BIGSERIAL PRIMARY KEY,
    detected_at TIMESTAMPTZ DEFAULT NOW(),
    topic TEXT NOT NULL,
    source TEXT NOT NULL,
    score FLOAT,
    post_count INTEGER DEFAULT 0,
    sample_titles TEXT[],
    metadata JSONB
);

CREATE TABLE IF NOT EXISTS briefings (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    period_start TIMESTAMPTZ,
    period_end TIMESTAMPTZ,
    summary TEXT NOT NULL,
    top_topics TEXT[],
    sentiment TEXT,
    raw_data JSONB
);

CREATE INDEX IF NOT EXISTS idx_posts_source ON posts(source);
CREATE INDEX IF NOT EXISTS idx_posts_published_at ON posts(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_trends_detected_at ON trends(detected_at DESC);
CREATE INDEX IF NOT EXISTS idx_trends_topic ON trends(topic);
CREATE INDEX IF NOT EXISTS idx_briefings_created_at ON briefings(created_at DESC);

ALTER TABLE posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE trends ENABLE ROW LEVEL SECURITY;
ALTER TABLE briefings ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public read posts" ON posts FOR SELECT USING (true);
CREATE POLICY "Public read trends" ON trends FOR SELECT USING (true);
CREATE POLICY "Public read briefings" ON briefings FOR SELECT USING (true);
CREATE POLICY "Service insert posts" ON posts FOR INSERTWITH CHECK (true);
CREATE POLICY "Service insert trends" ON trends FOR INSERT WITH CHECK (true);
CREATE POLICY "Service insert briefings" ON briefings FOR INSERT WITH CHECK (true);
