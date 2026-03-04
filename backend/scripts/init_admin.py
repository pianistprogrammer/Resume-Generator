"""Initialize admin user and seed default feeds."""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import connect_to_mongo
from app.schemas.user import User, FeedSource, UserProfile
from app.services.auth_service import AuthService
from app.config import settings


async def create_admin_user():
    """Create the admin user from environment variables."""
    admin_email = settings.admin_email
    admin_password = settings.admin_password

    if not admin_email or not admin_password:
        print("❌ ADMIN_EMAIL and ADMIN_PASSWORD must be set in environment variables")
        return None

    # Check if admin already exists
    existing_admin = User.objects(email=admin_email).first()
    if existing_admin:
        print(f"✅ Admin user already exists: {admin_email}")

        # Ensure role is set to admin
        if existing_admin.role != "admin":
            existing_admin.role = "admin"
            existing_admin.save()
            print("   Updated role to admin")

        return existing_admin

    # Create admin user
    hashed_password = AuthService.get_password_hash(admin_password)

    admin_user = User(
        email=admin_email,
        hashed_password=hashed_password,
        profile=UserProfile(
            full_name="Admin User",
            email=admin_email,
            location="Global"
        ),
        role="admin",
        is_active=True,
        onboarding_completed=True,
        credits=999999  # Unlimited credits for admin
    )
    admin_user.save()

    print(f"✅ Created admin user: {admin_email}")
    return admin_user


async def seed_default_feeds():
    """Seed the database with default RSS feeds."""
    default_feeds = [
        {
            "name": "RemoteOK",
            "url": "https://remoteok.com/remote-dev-jobs.rss",
            "feed_type": "rss"
        },
        {
            "name": "We Work Remotely",
            "url": "https://weworkremotely.com/remote-jobs.rss",
            "feed_type": "rss"
        },
        {
            "name": "Himalayas",
            "url": "https://himalayas.app/jobs/rss",
            "feed_type": "rss"
        },
        {
            "name": "Real Work From Anywhere",
            "url": "https://www.realworkfromanywhere.com/rss.xml",
            "feed_type": "rss"
        },
        {
            "name": "RSS App Custom Feed",
            "url": "https://rss.app/feeds/0bUVsJgEz3RTTsKm.xml",
            "feed_type": "rss"
        },
    ]

    for feed_data in default_feeds:
        # Check if feed already exists
        existing_feed = FeedSource.objects(url=feed_data["url"]).first()
        if existing_feed:
            print(f"✅ Feed already exists: {feed_data['name']}")
            continue

        # Create feed
        feed = FeedSource(
            name=feed_data["name"],
            url=feed_data["url"],
            feed_type=feed_data["feed_type"],
            is_active=True,
            created_by="system"
        )
        feed.save()
        print(f"✅ Created feed: {feed_data['name']}")


async def main():
    """Main initialization function."""
    print("🚀 Initializing admin user and default feeds...\n")

    # Initialize database
    connect_to_mongo()

    # Create admin user
    await create_admin_user()
    print()

    # Seed default feeds
    await seed_default_feeds()
    print()

    print("✨ Initialization complete!")
    print(f"\n📧 Admin email: {settings.admin_email}")
    print("🔑 Use the password from ADMIN_PASSWORD environment variable to login")


if __name__ == "__main__":
    asyncio.run(main())
