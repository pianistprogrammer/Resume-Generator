#!/usr/bin/env python3
"""Test script for email service."""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.email_service import EmailService
from app.database import connect_to_mongo


async def test_email():
    """Test email sending functionality."""
    print("=" * 60)
    print("JobAlert AI - Email Service Test")
    print("=" * 60)
    print()

    # Initialize database (not needed for email, but good practice)
    print("[1/2] Connecting to database...")
    try:
        await connect_to_mongo()
        print("✓ Connected\n")
    except Exception as e:
        print(f"⚠ Database connection failed (not critical for email test): {e}\n")

    # Test welcome email
    print("[2/2] Sending test welcome email...")
    test_email = "jeremiahabimbola@gmail.com"  # Change this to your test email
    test_name = "Test User"

    success = EmailService.send_welcome_email(test_email, test_name)

    if success:
        print(f"\n✅ Test email sent successfully to {test_email}!")
        print("Check your inbox (and spam folder)")
    else:
        print(f"\n❌ Failed to send test email")
        return False

    return True


if __name__ == "__main__":
    success = asyncio.run(test_email())
    sys.exit(0 if success else 1)
