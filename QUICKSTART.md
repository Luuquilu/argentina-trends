# 🇦🇷 Argentina Trends — Quickstart (5 min)

> Everything is installed and working. You just need credentials.

---

## Step 1 — Supabase (2 min)

1. Go to **[supabase.com/dashboard](https://supabase.com/dashboard)**
2. Click **New project** → name it `argentina-trends` → region **South America (São Paulo)**
3. Wait ~2 min for it to provision
4. Go to **Project Settings → API** and copy:
   - **Project URL** → `SUPABASE_URL`
   - **anon public** key → `SUPABASE_KEY`
5. Go to **SQL Editor** → paste the contents of `storage/schema.sql` → click **Run**

---

## Step 2 — Edit .env

Open `.env` (in this folder) and fill in:

```
SUPABASE_URL=https://YOUR-PROJECT.supabase.co
SUPABASE_KEY=eyJhbGc...
ANTHROPIC_API_KEY=sk-ant-...   ← get from console.anthropic.com
REDDIT_CLIENT_ID=...            ← optional, from reddit.com/prefs/apps
REDDIT_CLIENT_SECRET=...        ← optional
```

---

## Step 3 — Test it works

Open Terminal, paste this:

```bash
export PATH="$HOME/Library/Python/3.9/bin:$PATH"
cd ~/Desktop/Argentina\ Trends
bash setup.sh
```

If it shows ✅, everything works. Then run:

```bash
python3 agent.py --once          # collect + analyze data
streamlit run dashboard/app.py   # open dashboard in browser
```

---

## Step 4 — Push fixes to GitHub (1 min)

The code has been fixed locally. To push to GitHub:

1. Go to **[github.com/settings/tokens](https://github.com/settings/tokens)**
2. Click **Generate new token (classic)** → check **repo** scope → copy the token
3. In Terminal:

```bash
cd ~/Desktop/Argentina\ Trends
git push https://YOUR_TOKEN@github.com/Luuquilu/argentina-trends.git main
```

Replace `YOUR_TOKEN` with the token you just copied.

---

## Step 5 — Add GitHub Secrets for auto-collection

Go to **github.com/Luuquilu/argentina-trends → Settings → Secrets → Actions** and add:
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `ANTHROPIC_API_KEY`
- `REDDIT_CLIENT_ID` (optional)
- `REDDIT_CLIENT_SECRET` (optional)

GitHub Actions will then collect data every hour automatically — **no server needed**.

---

## Step 6 — Deploy Dashboard (free)

1. Go to **[share.streamlit.io](https://share.streamlit.io)**
2. Sign in with GitHub → **New app**
3. Repo: `Luuquilu/argentina-trends` · Branch: `main` · File: `dashboard/app.py`
4. In **Advanced settings → Secrets**, add `SUPABASE_URL` and `SUPABASE_KEY`
5. Click **Deploy** — your dashboard will be live at `your-app.streamlit.app`

---

## What was fixed in this session

| Bug | File | Fix |
|-----|------|-----|
| Syntax error in f-string | `processors/summarizer.py` | `', w.join` → `', '.join` and `{/neg}` → `{neg}` |
| Missing `generate_daily_briefing` | `processors/summarizer.py` | Added the function |
| Sentiment labels mismatch | `processors/sentiment.py` | Normalized `POS/NEG/NEU` → `positive/negative/neutral` |
| Typo in env var name | `collectors/reddit_collector.py` | `REDDITECLIENT_ID` → `REDDIT_CLIENT_ID` |
| Stray variable | `collectors/youtube_collector.py` | Removed `lood_dotenv = load_dotenv` |
| Outdated dependencies | `requirements.txt` | Bumped `anthropic`, `supabase`, added `requests` + `sentence-transformers` |
