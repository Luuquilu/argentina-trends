"""
Sentiment analysis using pysentimiento.
Runs locally, free.
"""
import logging
logger = logging.getLogger(__name__)
_analyzer = None

def _get_analyzer():
    global _analyzer
    if _analyzer is None:
        try:
            from pysentimiento import create_analyzer
            _analyzer = create_analyzer(task="sentiment", lang="es")
        except Exception as e:
            logger.error(f"Could not load pysentimiento: {e}")
    return _analyzer

def analyze(text):
    a = _get_analyzer()
    if not a or not text: return "NEU", 0.0
    try:
        r = a.predict(text[:512])
        return r.output, round(max(r.probas.values()), 4)
    except: return "NEU", 0.0

def enrich_posts(posts):
    return [{**p, **dict(zip(["sentiment","sentiment_score"], analyze(f"{p.get('title','')} {p.get('body','')}")))} for p in posts]
