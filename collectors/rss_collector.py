"""
RSS feed collector for major Argentine news sites.
"""
import hashlib, logging
from datetime import datetime
import feedparser
logger = logging.getLogger(__name__)
FEEDS = {
    # High-volume national news
    "infobae": [
        "https://www.infobae.com/arc/outboundfeeds/rss/",                                       # main
        "https://www.infobae.com/arc/outboundfeeds/rss/?outputType=xml&section=economia",       # economy
        "https://www.infobae.com/arc/outboundfeeds/rss/?outputType=xml&section=politica",       # politics
        "https://www.infobae.com/arc/outboundfeeds/rss/?outputType=xml&section=sociedad",       # society
    ],
    "lanacion":  ["https://www.lanacion.com.ar/arcio/rss/"],
    "clarin":    ["https://www.clarin.com/rss/lo-ultimo/"],
    "tn":        ["https://tn.com.ar/rss.xml"],                      # was /ultimas-noticias.xml (404)

    # Economy / finance
    "ambito":    ["https://www.ambito.com/rss/home.xml"],             # was /rss.xml (404)

    # Opinion / politics (replaces pagina12 & cronista whose RSS are gone)
    "perfil":    ["https://www.perfil.com/feed"],
    "chequeado": ["https://chequeado.com/feed/"],                     # fact-checking site

    # Regional (Córdoba — 2nd largest city)
    "lavoz":     ["https://www.lavoz.com.ar/rss/todas-las-noticias.xml"],
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
