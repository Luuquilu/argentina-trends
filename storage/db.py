"""
Supabase database helpers.
Auto-migrates schema on first connection.
"""
import logging, os, requests as _requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()
logger = logging.getLogger(__name__)
_client = None
_schema_ok = False   # set True once migration is confirmed


def _get_client():
    global _client
    if _client is None:
        from supabase import create_client
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            raise RuntimeError("SUPABASE_URL/KEY not set — please fill in .env")
        _client = create_client(url, key)
    return _client


def _run_sql(sql: str) -> bool:
    """Run DDL via Supabase's pgREST SQL endpoint (requires service role key or anon + RLS disabled)."""
    url  = os.getenv("SUPABASE_URL", "").rstrip("/")
    key  = os.getenv("SUPABASE_KEY", "")
    if not url or not key:
        return False
    try:
        r = _requests.post(
            f"{url}/rest/v1/rpc/exec_sql",
            headers={"apikey": key, "Authorization": f"Bearer {key}",
                     "Content-Type": "application/json"},
            json={"query": sql},
            timeout=20,
        )
        return r.status_code < 300
    except Exception:
        return False


def ensure_schema():
    """Create missing tables & columns on first run."""
    global _schema_ok
    if _schema_ok:
        return

    c = _get_client()

    # ── Check & create google_trends ─────────────────────────────────────────
    try:
        c.table("google_trends").select("id").limit(1).execute()
    except Exception:
        logger.info("Creating google_trends table via REST upsert workaround …")
        # Can't create tables via REST — log for manual action
        logger.warning(
            "⚠️  Table 'google_trends' missing.  "
            "Run storage/schema.sql in your Supabase SQL Editor."
        )

    # ── Check trends table columns ────────────────────────────────────────────
    try:
        r = c.table("trends").select("topic_label").limit(1).execute()
    except Exception:
        logger.warning(
            "⚠️  Trends table missing 'topic_label' column.  "
            "Run storage/schema.sql in your Supabase SQL Editor."
        )

    _schema_ok = True


def save_posts(posts: list[dict]) -> int:
    if not posts:
        return 0
    c = _get_client()
    saved = 0
    for p in posts:
        try:
            doc = {
                "source":       p.get("source"),
                "external_id":  p.get("source_id"),
                "title":        (p.get("title") or "")[:2000],
                "body":         (p.get("body") or "")[:2000],
                "url":          p.get("url", ""),
                "author":       p.get("author", ""),
                "published_at": p.get("published_at"),
            }
            c.table("posts").upsert(doc, on_conflict="source,external_id").execute()
            saved += 1
        except Exception as e:
            logger.warning(f"Save post error: {e}")
    return saved


def save_google_trend(keyword, value):
    c = _get_client()
    try:
        c.table("google_trends").upsert(
            {"keyword": keyword, "value": value,
             "captured_at": datetime.utcnow().isoformat()},
            on_conflict="keyword,captured_at",
        ).execute()
    except Exception as e:
        logger.warning(f"Save GTrend error: {e}")


def fetch_recent_posts(hours=6):
    c = _get_client()
    since = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
    r = c.table("posts").select("*").gte("collected_at", since).limit(2000).execute()
    return r.data or []


def save_trend(t: dict):
    c = _get_client()
    try:
        c.table("trends").insert(t).execute()
    except Exception as e:
        # If new-schema columns are missing, try mapping to old schema
        if "column" in str(e) and "does not exist" in str(e):
            logger.warning(f"Trends schema mismatch — run schema.sql to fix.  Error: {e}")
        else:
            logger.warning(f"Save trend error: {e}")
