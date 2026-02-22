"""
RSS feed collector for major Argentine news sites.
"""
import hashlib, logging
from datetime import datetime
import feedparser
logger = logging.getLogger(__name__)
FEEDS = {
    "infobae":["https://www.infobae.com/feeds/rss/","https://www.infobae.com/economia/feeds/rss/"],
    "lanacion":["https://www.lanacion.com.ar/arcio/rss/"],
    "clarin":["https://www.clarin.com/rss/lo-ultimo/"],
    "ambito":["https://www.ambito.com/rss.xml"],
    "pagina12":["https://www.pagina12.com.ar/rss/portada"],
    "tn":["https://tn.com.ar/rss/ultimas-noticias.xml"],
    "cronista":["https://www.cronista.com/files/rss/home.xml"],
}

def collect():
    posts = []
    for outlet,urls in FEEDS.items():
        for url in urls:
            try:
                for e in feedparser.parse(url).entries:
                    if not e.get("title"): continue
                    posts.append({"source":f"rss_{outlet}","source_id":hashlib.sha1((e.get("link","") or e.get("title","")).encode()).hexdigest()[:16],"title":e.get("title",""),"body":e.get("summary",""),"url":e.get("link",""),"author":outlet,"published_at":datetime.utcnow().isoformat()})
            except Exception: pass
    return posts
