# 🇦🇷 Argentina Social Media Trend Detection Agent

An AI agent that monitors Argentine social media and news in real-time,
detects emerging trends, runs sentiment analysis in Argentine Spanish,
and generates AI briefings — **completely free or nearly free**.

## Cost breakdown

| Component | Cost |
|---|---|
| RSS feeds (8 outlets) | Free |
| Google Trends (pytrends) | Free |
| Reddit API | Free |
| YouTube Data API v3 | Free (10k units/day) |
| Telegram public channels | Free |
| Supabase database | Free (500MB) |
| BERTopic + pysentimiento | Free (runs locally) |
| GitHub Actions (scheduler) | Free |
| Streamlit Cloud (dashboard) | Free |
| Claude Haiku (AI summaries) | ~$1–5/month |
| **Total** | **~$1–5/month** |

---

## Setup (15 minutes)

### 1. Clone and install

```bash
git clone https://github.com/your-username/argentina-trends
cd argentina-trends
pip install -r requirements.txt
cp .env.example .env
```

### 2. Set up Supabase (free)

1. Create account at [supabase.com](https://supabase.com)
2. Create a new project
3. Go to **SQL Editor** and paste the contents of `storage/schema.sql` → Run
4. Go to **Project Settings → API** and copy your URL and anon key
5. Add them to `.env`:
   ```
   SUPABASE_URL=https://xxxxx.supabase.co
   SUPABASE_KEY=eyJhbGc...
   ```

### 3. Set up Reddit API (free)

1. Go to [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)
2. Click **Create App** → select **script**
3. Add to `.env`:
   ```
   REDDIT_CLIENT_ID=your-id
   REDDIT_CLIENT_SECRET=your-secret
   ```

### 4. Set up Anthropic API (cheap)

1. Get key at [console.anthropic.com](https://console.anthropic.com)
2. Add to `.env`:
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ```

### 5. (Optional) YouTube API

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Enable **YouTube Data API v3** → Create credentials → API Key
3. Add to `.env`: `YOUTUBE_API_KEY=AIza...`

### 6. (Optional) Telegram

1. Get credentials at [my.telegram.org/apps](https://my.telegram.org/apps)
2. Add to `.env`: `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`, `TELEGRAM_PHONE`
3. First run will prompt for Verification code (one-time)

---

## Running locally

```bash
# Run once (collect + analyze)
python agent.py --once

# Collect only
python agent.py --collect-only

# Analyze existing data
python agent.py --analyze-only

# Run continuously (collect every 1h, analyze every 6h)
python agent.py

# Launch dashboard
streamlit run dashboard/app.py
```

## Running on GitHub Actions (free, no server needed)

1. Push this repo to GitHub (can be private)
2. Go to **Settings → Secrets → Actions** and add:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `ANTHROPIC_API_KEY`
   - `REDDIT_CLIENT_ID`
   - `REDDIT_CLIENT_SECRET`
   - `YOUTUBE_API_KEY` (optional)
3. GitHub will automatically run collection every hour and analysis every 6 hours

## Deploy dashboard to Streamlit Cloud (free)

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo, set entry point to `dashboard/app.py`
4. Add your Supabase secrets in the Streamlit secrets manager
5. Your dashboard is live at `your-app.streamlit.app`

---

## Architecture

```
[Data Sources]                    [Free/Cheap]
  RSS feeds (8 outlets)     ──┐
  Google Trends (pytrends)  ──┤
  Reddit API                ──┼──┺ GitHub Actions (cron)
  YouTube API               ──┤         │
  Telegram channels         ──┘         ▼
                                  [Supabase DB]
                                        │
                            ┌───────────┴───────────┐
                            ▼                       ▼
                    [pysentimiento]           [BERTopic]
                    Argentine sentiment     Topic clustering
                            └───────────┬───────────┘
                                        ▼
                                [Claude Haiku]
                                AI trend summaries
                                        │
                                        ▼
                              [Streamlit Dashboard]
```

## Project structure

```
argentina-trends/
├── agent.py                    # Main entry point
├── requirements.txt
├── .env.example
├── collectors/
│   ├── rss_collector.py        # 8 Argentine news sites (free)
│   ├── gtrends_collector.py    # Google Trends via pytrends (free)
│   ├── reddit_collector.py     # Argentine subreddits (free)
│   ├── youtube_collector.py    # YouTube search API (free)
│   └── telegram_collector.py  # Public TG channels (free)
├── processors/
│   ├── sentiment.py            # pysentimiento (Argentine Spanish)
│   ├── topics.py               # BERTopic clustering
│   ├── summarizer.py           # Claude Haiku AI summaries
│   └── trend_engine.py         # Orchestrates the pipeline
├── storage/
│   ├── db.py                   # Supabase helpers
│   └── schema.sql              # DB schema (run in Supabase)
├── dashboard/
│   └── app.py                  # Streamlit dashboard
└── .github/workflows/
    └── collect.yml             # GitHub Actions cron jobs
```
