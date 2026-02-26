"""
Telegram collector - optional. Skips if not configured.
"""
import asyncio, logging, os
from dotenv import load_dotenv
load_dotenv(override=True)  # override: Claude Desktop may set API keys to empty string
logger = logging.getLogger(__name__)
CHANNELS = ["infobae","lacapitalmedia","ambito_com","clarin_ok"]

def collect(hours=6):
    if not all([os.getenv(x) for x in ["TELEGRAM_API_ID","TELEGRAM_API_HASH","TELEGRAM_PHONE"]]):
        logger.warning("Telegram credentials not set, skipping")
        return []
    return []  # Telegram optional feature - add telethon impl if needed
