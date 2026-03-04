#!/usr/bin/env python
"""Script to populate initial RSS feed sources."""

from app.database import connect_to_mongo
from app.schemas.user import FeedSource

# Popular remote job board RSS feeds
INITIAL_FEEDS = [
    {
        "name": "RemoteOK",
        "url": "https://remoteok.com/remote-jobs.rss",
        "feed_type": "rss",
        "is_active": True
    },
    {
        "name": "WeWorkRemotely",
        "url": "https://weworkremotely.com/categories/remote-programming-jobs.rss",
        "feed_type": "rss",
        "is_active": True
    },
    {
        "name": "Remotive",
        "url": "https://remotive.com/api/remote-jobs/feed",
        "feed_type": "rss",
        "is_active": True
    },
    {
        "name": "RemoteCo",
        "url": "https://remote.co/remote-jobs/developer/feed/",
        "feed_type": "rss",
        "is_active": True
    },
    {
        "name": "JustRemote",
        "url": "https://justremote.co/remote-developer-jobs/rss",
        "feed_type": "rss",
        "is_active": True
    },
]


def main():
    """Add initial feed sources to database."""
    connect_to_mongo()

    print("Adding initial feed sources...")

    added = 0
    skipped = 0

    for feed_data in INITIAL_FEEDS:
        # Check if feed already exists
        existing = FeedSource.objects(url=feed_data["url"]).first()

        if existing:
            print(f"✗ Skipped: {feed_data['name']} (already exists)")
            skipped += 1
            continue

        # Create new feed source
        feed = FeedSource(**feed_data)
        feed.save()
        print(f"✓ Added: {feed_data['name']}")
        added += 1

    print(f"\nSummary:")
    print(f"- Added: {added}")
    print(f"- Skipped: {skipped}")
    print(f"- Total active feeds: {FeedSource.objects(is_active=True).count()}")


if __name__ == "__main__":
    main()
