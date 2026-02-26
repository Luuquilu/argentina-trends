"""
Argentina Social Media Trend Detection Agent
============================================
Main entry point. Can be run:
  - Once:      python agent.py --once
  - Scheduled: python agent.py          (runs collection every hour, trend engine every 6h)
  - GitHub Actions: python agent.py --once  (triggered by cron workflow)
"""
import argparse
import logging
import sys
import time
from datetime import datetime

import schedule
from dotenv import load_dotenv

load_dotenv(override=True)  # override=True needed: Claude Desktop sets ANTHROPIC_API_KEY='' in env

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("agent")

# ── Import collectors ─────────────────────────────────────────────────────────
from collectors import rss_collector, gtrends_collector, reddit_collector
from collectors import youtube_collector, telegram_collector
from storage.db import save_posts, save_google_trend
from processors.trend_engine import run as run_trend_engine


def collect_all():
    """Run all collectors and persist to Supabase."""
    logger.info(f"\n{'='*60}")
    logger.info(f"Collection run started at {datetime.utcnow().isoformat()}")

    # RSS — always runs, no credentials needed
    rss_posts = rss_collector.collect()
    saved = save_posts(rss_posts)
    logger.info(f"RSS: {saved} new posts saved")

    # Google Trends
    gtrends = gtrends_collector.collect()
    for item in gtrends:
        save_google_trend(item["keyword"], item["value"])
    logger.info(f"Google Trends: {len(gtrends)} snapshots saved")

    # Reddit
    reddit_posts = reddit_collector.collect()
    saved = save_posts(reddit_posts)
    logger.info(f"Reddit: {saved} new posts saved")

    # YouTube
    yt_posts = youtube_collector.collect()
    saved = save_posts(yt_posts)
    logger.info(f"YouTube: {saved} new posts saved")

    # Telegram (optional — skips gracefully if not configured)
    tg_posts = telegram_collector.collect()
    saved = save_posts(tg_posts)
    logger.info(f"Telegram: {saved} new posts saved")

    logger.info("Collection run complete\n")


def run_analysis():
    """Run the trend analysis pipeline."""
    logger.info("Starting trend analysis...")
    trends = run_trend_engine(hours=6)
    logger.info(f"Analysis complete: {len(trends)} trends detected")


def main():
    parser = argparse.ArgumentParser(description="Argentina Trend Detection Agent")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--collect-only", action="store_true", help="Only collect, no analysis")
    parser.add_argument("--analyze-only", action="store_true", help="Only analyze existing data")
    args = parser.parse_args()

    if args.once:
        if not args.analyze_only:
            collect_all()
        if not args.collect_only:
            run_analysis()
        return

    # Scheduled mode
    logger.info("Starting scheduled agent (Ctrl+C to stop)")
    logger.info("Schedule: collect every 1h, analyze every 6h")

    # Run immediately on start
    collect_all()
    run_analysis()

    schedule.every(1).hours.do(collect_all)
    schedule.every(6).hours.do(run_analysis)

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
