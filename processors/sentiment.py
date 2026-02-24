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

_LABEL_MAP = {"POS": "positive", "NEG": "negative", "NEU": "neutral"}

def analyze(text):
    a = _get_analyzer()
    if not a or not text: return "neutral", 0.0
    try:
        r = a.predict(text[:512])
        label = _LABEL_MAP.get(r.output, r.output.lower())
        return label, round(max(r.probas.values()), 4)
    except: return "neutral", 0.0

def enrich_posts(posts):
    return [{**p, **dict(zip(["sentiment","sentiment_score"], analyze(f"{p.get('title','')} {p.get('body','')}")))} for p in posts]
