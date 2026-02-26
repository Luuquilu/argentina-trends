"""
Reddit collector for Argentine subreddits.
Free — requires a Reddit app at reddit.com/prefs/apps.
"""
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv(override=True)  # override: Claude Desktop may set API keys to empty string
logger = logging.getLogger(__name__)
SUBREDDITS = ["argentina", "merval", "AsesoresDeFe", "ArgEnglish", "buenosaires"]

def collect(limit=150):
    try: import praw
    except ImportError: return []
    cid = os.getenv("REDDIT_CLIENT_ID")
    csec = os.getenv("REDDIT_CLIENT_SECRET")
    if not cid or not csec: return []
    reddit = praw.Reddit(client_id=cid, client_secret=csec, user_agent="ArgentinaTrendsBot/1.0")
    posts = []
    for sub in SUBREDDITS:
        try:
            for s in reddit.subreddit(sub).hot(limit=limit):
                posts.append({"source":"reddit","source_id":s.id,"title":s.title,"body":s.selftext[:2000],"url":f"https://reddit.com{s.permalink}","author":str(s.author),"published_at":datetime.utcfromtimestamp(s.created_utc).isoformat(),"metadata":{"subreddit":sub,"score":s.score}})
        except Exception: pass
    return posts
