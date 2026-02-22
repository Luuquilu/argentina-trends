-- Run this in your Supabase SQL Editor
-- Go to: Project Settings → Database ‒ SQL Editor

CREATE TABLE IF NOT EXISTS posts (
    id BIGSERIAL PRIMARY KEY,
    source TEXT NOT NULL,
    external_id TEXT,
    title TEXT,
    body TEXT,
    url TEXT,
    author TEXT,
    sentiment TEXT,
    sentiment_score FLOAT,
    topic_id INTEGER,                        -- set after BERTopic
    published_at TIMESTAMPTZ,
    collected_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(source, external_id)
);

CREATE TABLE IF NOT EXISTS trends (
    id BIGSERIAL PRIMARY KEY,
    period_start TIMESTAMPTZ,
    period_end TIMESTAMPTZ,
    created_at TIMESTAMPTX DEGAULT NOW(),
    topic_label TEXT NOT NULL,
    keywords TEXT[],
    post_count INTEGER,
    avg_sentiment FLOAT,
    top_posts JSONB,
    ai_summary TEXT
);

CREATE TABLE IF NOT EXISTS google_trends (
    id BIGSERIAL PRIMARY KEY,
    keyword TEXT NOT NULL,
    value INTEGER,
    captured_at TIMESTAMPTZ,
    UNIQUE(keyword, captured_at)
);

CREATE INDEX IF NOT EXISTS idx_posts_source ON posts(source);
CREATE INDEX IF NOT EXISTS idx_posts_time ON posts(collected_at DESC);
CREATE INDEX IF NOT EXISTS idx_posts_topic ON posts(topic_id);
CREATE INDEX IF NOT EXISTS idx_trends_time ON trends(created_at DESC);
