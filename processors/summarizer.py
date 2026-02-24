"""
AI trend summarizer using Claude Haiku.
Cost: ~$0.001 per summary.
"""
import logging, os
from dotenv import load_dotenv
load_dotenv()
logger = logging.getLogger(__name__)

def summarize_trend(topic_label, keywords, posts):
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key: return "(Anthropic API key not set)"
    try:
        import anthropic
        c = anthropic.Anthropic(api_key=key)
        headlines = "\n".join([f"- {p.get('title','')}" for p in posts[:15]])
        pos = sum(1 for p in posts if p.get("sentiment") == "positive")
        neg = sum(1 for p in posts if p.get("sentiment") == "negative")
        prompt = f"Tema: {topic_label}\nPalabras: {', '.join(keywords)}\nSentimiento: {pos} pos {neg} neg\n\n{headlines}\n\nEscribe un resumen corto en español de qué trata este tema y cuál es el tono."
        r = c.messages.create(model="claude-3-5-haiku-20241022", max_tokens=300, messages=[{"role":"user","content":prompt}])
        return r.content[0].text.strip()
    except Exception as e: return f"(Error: {e})"

def generate_daily_briefing(trends):
    """Generate a daily executive briefing across all detected trends."""
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key or not trends:
        return
    try:
        import anthropic
        c = anthropic.Anthropic(api_key=key)
        summaries = "\n".join([
            f"- {t.get('topic_label','')}: {t.get('post_count',0)} posts"
            for t in trends[:10]
        ])
        prompt = (
            f"Tendencias del día en Argentina:\n{summaries}\n\n"
            "Escribe un briefing ejecutivo en español de 3-4 oraciones "
            "resumiendo lo más importante que está pasando hoy en Argentina."
        )
        r = c.messages.create(model="claude-3-5-haiku-20241022", max_tokens=400,
                               messages=[{"role": "user", "content": prompt}])
        logger.info(f"Daily briefing:\n{r.content[0].text.strip()}")
    except Exception as e:
        logger.warning(f"Daily briefing error: {e}")
