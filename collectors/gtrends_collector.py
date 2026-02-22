"""
Google Trends collector for Argentina.
Uses pytrends — completely free, no API key needed.
"""
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)

# Keywords to track — mix of evergreen Argentine topics
KEYWORDS = [
    "dólar blue", "dólar oficial", "inflación", "Milei",
    "Banco Central", "AFIP", "paro", "boleto", "nafta precio",
    "Bitcoin Argentina", "Merval", "bonos", "elecciones",
    "corte de luz", "lluvia Buenos Aires",
]

# Google Trends allows max 5 keywords per request
BATCH_SIZE = 5


def collect() -> list[dict]:
    try:
        from pytrends.request import TrendReq
    except ImportError:
        logger.error("pytrends not installed. Run: pip install pytrends")
        return []

    results = []
    now = datetime.utcnow().isoformat()
    pytrends = TrendReq(hl="es-AR", tz=-180, timeout=(10, 25))

    batches = [KEYWORDS[i:i+BATCH_SIZE] for i in range(0, len(KEYWORDS), BATCH_SIZE)]
    for batch in batches:
        try:
            pytrends.build_payload(batch, cat=0, timeframe="now 1-d", geo="AR")
            df = pytrends.interest_over_time()
            if df.empty:
                continue
            last = df.iloc[-1]
            for kw in batch:
                if kw in last:
                    results.append({"keyword": kw, "value": int(last[kw]), "captured_at": now})
            time.sleep(2)
        except Exception as e:
            logger.warning(f"Google Trends error for batch {batch}: {e}")
            time.sleep(10)
    logger.info(f"Google Trends: {len(results)} snapshots")
    return results
