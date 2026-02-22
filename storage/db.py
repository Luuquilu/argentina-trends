"""
Supabase database helpers.
"""
import logging, os
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()
logger = logging.getLogger(__name__)
_client = None

def _get_client():
    global _client
    if _client is None:
        from supabase import create_client
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key: raise RuntimeError("SUPABASE_URL/KEY not set")
        _client = create_client(url, key)
    return _client

def save_posts(posts: list[dict]) -> int:
    if not posts: return 0
    c = _get_client()
    saved = 0
    for p in posts:
        try:
            doc = {"source":p.get("source"),"external_id":p.get("source_id"),"title":p.get("title","")[:2000],"body":p.get("body","")[:2000],"url":p.get("url",""),"author":p.get("author",""),"published_at":p.get("published_at")}
            c.table("posts").upsert(doc,on_conflict="source,external_id").execute()
            saved += 1
        except Exception as e: logger.warning(f"Save post error: {e}")
    return saved

def save_google_trend(keyword, value):
    c = _get_client()
    try: c.table("google_trends").upsert({"keyword":keyword,"value":value,"captured_at":datetime.utcnow().isoformat()},on_conflict="keyword,captured_at").execute()
    except Exception as e: logger.warning(f"Save GTrend error: {e}")

def fetch_recent_posts(hours=6):
    c = _get_client()
    since = (datetime.utcnow()-timedelta(hours=hours)).isoformat()
    r = c.table("posts").select("*").gte("collected_at",since).limit(2000).execute()
    return r.data or []

def save_trend(t):
    c = _get_client()
    try: c.table("trends").insert(t).execute()
    except Exception as e: logger.warning(f"Save trend error: {e}")
