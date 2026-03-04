"""Test script to verify admin creation on startup."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pymongo import MongoClient
from app.config import settings


def delete_admin():
    """Delete the admin user to test creation."""
    client = MongoClient(settings.mongodb_url)
    db = client[settings.mongodb_db_name]
    users_collection = db['users']
    
    result = users_collection.delete_one({'email': settings.admin_email})
    if result.deleted_count > 0:
        print(f"✅ Deleted admin user: {settings.admin_email}")
    else:
        print(f"⚠️  Admin user not found: {settings.admin_email}")
    
    client.close()


if __name__ == "__main__":
    delete_admin()
