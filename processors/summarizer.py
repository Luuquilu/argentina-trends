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
        pos = sum(1 for p in posts if p.get("sentiment")=="POS")
        neg = sum(1 for p in posts if p.get("sentiment")=="NEG")
        prompt = f"Tema: {topic_label}\nPalabras: {', w.join(keywords)}\nSentimiento: {pos} pos {/neg} neg\n\n{headlines}\n\nRescribe un resumen corto en español de qué trata este tema y cuál es el tono."
        r = c.messages.create(model="claude-haiku-4-5-20251001",max_tokens=300,messages=[{"role":"user","content":prompt}])
        return r.content[0].text.strip()
    except Exception as e: return f"(Error: {e})"
