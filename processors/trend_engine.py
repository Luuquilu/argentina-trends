"""
Trend engine — orchestrates sentiment + topics + summaries.
"""
import logging
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from processors.sentiment import enrich_posts
from processors.topics import cluster_posts
from processors.summarizer import summarize_trend, generate_daily_briefing
from storage.db import fetch_recent_posts, save_trend
logger = logging.getLogger(__name__)

def run(hours=6):
    posts = fetch_recent_posts(hours=hours)
    if not posts: return []
    posts = enrich_posts(posts)
    posts, meta = cluster_posts(posts)
    by_t = defaultdict(list)
    for p in posts:
        if p.get("topic_id",-1)!=-1: by_t[p["topic_id"]].append(p)
    now = datetime.now(timezone.utc)
    trends = []
    for tid,tposts in sorted(by_t.items(), key=lambda x:-len(x[1])):
        m = meta.get(tid,{})
        label = m.get("label",f"topic_{tid}")
        kw = m.get("keywords",[])
        pos=sum(1 for p in tposts if p.get("sentiment")=="positive")
        neg=sum(1 for p in tposts if p.get("sentiment")=="negative")
        total=len(tposts)
        trend = {"period_start":(now-timedelta(hours=hours)).isoformat(),"period_end":now.isoformat(),"topic_label":label,"keywords":kw,"post_count":total,"avg_sentiment":round((pos-neg)/total if total else 0,4),"top_posts":[{"title":p.get("title"),"url":p.get("url"),"source":p.get("source")} for p in tposts[:5]],"ai_summary":summarize_trend(label,kw,tposts)}
        trends.append(trend)
        save_trend(trend)
    if trends: generate_daily_briefing(trends)
    return trends
