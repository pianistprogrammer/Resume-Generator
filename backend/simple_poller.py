#!/usr/bin/env python3
"""
Standalone job ingestion poller - simple alternative to Celery/Redis.

This script runs continuously and polls RSS feeds at regular intervals.
No external dependencies required beyond the app's existing packages.

Usage:
    python simple_poller.py              # Run with default 30-minute interval
    python simple_poller.py --interval 60 # Run with custom interval (seconds)

To run in background:
    nohup python simple_poller.py > poller.log 2>&1 &
"""

import asyncio
import sys
import os
import argparse
from datetime import datetime
from pathlib import Path

# Add backend root to Python path
backend_root = Path(__file__).parent
sys.path.insert(0, str(backend_root))

from app.services.ingestion.xml_feed_service import XMLFeedService
from app.services.matching_service import MatchingService
from app.database import connect_to_mongo, close_mongo_connection


async def poll_feeds():
    """Poll all RSS feeds and trigger matching for new jobs."""
    print(f"[{datetime.now().isoformat()}] Starting feed ingestion...")

    try:
        # Ingest from all registered feeds
        results = await XMLFeedService.ingest_all_feeds()

        total_jobs = sum(results.values())
        print(f"[{datetime.now().isoformat()}] Ingestion complete: {total_jobs} new jobs")

        for feed_key, count in results.items():
            if count > 0:
                print(f"  - {feed_key}: {count} jobs")

        if total_jobs == 0:
            print("  - No new jobs found in this cycle")

    except Exception as e:
        print(f"[{datetime.now().isoformat()}] ERROR during ingestion: {e}")
        import traceback
        traceback.print_exc()


async def run_poller(interval_seconds: int = 1800):
    """
    Run the poller in an infinite loop.

    Args:
        interval_seconds: Time to wait between polls (default: 1800 = 30 minutes)
    """
    # Initialize database connection
    print(f"[{datetime.now().isoformat()}] Initializing database connection...")
    await connect_to_mongo()
    print(f"[{datetime.now().isoformat()}] Database connected")

    print(f"[{datetime.now().isoformat()}] Starting poller with {interval_seconds}s interval")
    print(f"[{datetime.now().isoformat()}] Press Ctrl+C to stop")
    print("-" * 60)

    iteration = 0

    while True:
        iteration += 1
        print(f"\n[Iteration {iteration}]")

        try:
            await poll_feeds()
        except KeyboardInterrupt:
            print(f"\n[{datetime.now().isoformat()}] Received shutdown signal")
            break
        except Exception as e:
            print(f"[{datetime.now().isoformat()}] Unexpected error: {e}")
            import traceback
            traceback.print_exc()

        # Wait for next cycle
        next_run = datetime.now().timestamp() + interval_seconds
        next_run_time = datetime.fromtimestamp(next_run).strftime("%H:%M:%S")
        print(f"[{datetime.now().isoformat()}] Next run at {next_run_time}")
        print("-" * 60)

        try:
            await asyncio.sleep(interval_seconds)
        except KeyboardInterrupt:
            print(f"\n[{datetime.now().isoformat()}] Received shutdown signal")
            break

    print(f"[{datetime.now().isoformat()}] Poller stopped")


def main():
    """Main entry point with CLI argument parsing."""
    parser = argparse.ArgumentParser(
        description="Simple RSS feed poller for JobAlert AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python simple_poller.py                    # Poll every 30 minutes (default)
  python simple_poller.py --interval 60      # Poll every 60 seconds
  python simple_poller.py --interval 3600    # Poll every hour

  Run in background:
  nohup python simple_poller.py > poller.log 2>&1 &

  Check background process:
  ps aux | grep simple_poller.py

  Stop background process:
  pkill -f simple_poller.py
        """
    )

    parser.add_argument(
        '--interval',
        type=int,
        default=1800,
        help='Polling interval in seconds (default: 1800 = 30 minutes)'
    )

    parser.add_argument(
        '--once',
        action='store_true',
        help='Run once and exit (useful for testing)'
    )

    args = parser.parse_args()

    if args.interval < 10:
        print("ERROR: Interval must be at least 10 seconds to avoid rate limiting")
        sys.exit(1)

    async def run_once():
        """Helper to run single cycle."""
        print(f"[{datetime.now().isoformat()}] Running single ingestion cycle...")
        await connect_to_mongo()
        await poll_feeds()
        await close_mongo_connection()
        print(f"[{datetime.now().isoformat()}] Done")

    try:
        if args.once:
            # Run once and exit
            asyncio.run(run_once())
        else:
            # Run continuously
            asyncio.run(run_poller(args.interval))
    except KeyboardInterrupt:
        print("\nShutdown complete")
        sys.exit(0)


if __name__ == "__main__":
    main()
