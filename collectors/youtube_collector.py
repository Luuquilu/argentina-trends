"""
YouTube Data API v3 collector.
Free — 10k units/day. Each search costs 100 units.
"""
import logging, os
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv
load_dotenv(override=True)  # override: Claude Desktop may set API keys to empty string
logger = logging.getLogger(__name__)
SEARCH_QUERIES = ["argentina noticias","economia argentina","milei","dolar argentina"]

def collect(max_results=10):
    key = os.getenv("YOUTUBE_API_KEY","")
    if not key: return []
    posts = []
    after = (datetime.utcnow()-timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    for q in SEARCH_QUERIES:
        try:
            r = requests.get("https://www.googleapis.com/youtube/v3/search",params={"part":"snippet","q":q,"type":"video","regionCode":"AR","publishedAfter":after,"maxResults":max_results,"order":"viewCount","key":key},timeout=15)
            for item in r.json().get("items",[]):
                s=item["snippet"];vid=item["id"].get("videoId","")
                posts.append({"source":"youtube","source_id":vid,"title":s.get("title",""),"body":s.get("description","")[:1000],"url":f"https://youtube.com/watch?v={vid}","author":s.get("channelTitle",""),"published_at":s.get("publishedAt")})
        except Exception: pass
    return posts
