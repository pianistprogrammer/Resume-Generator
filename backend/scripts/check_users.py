"""Check user records in the database."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import connect_to_mongo
from app.schemas.user import User


def check_users():
    """Display all users in the database."""
    print("🔍 Checking users in database...\n")
    
    # Connect to database
    connect_to_mongo()
    
    # Get all users
    users = User.objects.all()
    
    print(f"📊 Total users: {users.count()}\n")
    
    for user in users:
        print(f"👤 User: {user.email}")
        print(f"   Name: {user.profile.full_name if user.profile else 'N/A'}")
        print(f"   Role: {user.role}")
        print(f"   Active: {user.is_active}")
        print(f"   Credits: {user.credits}")
        print(f"   Created: {user.created_at}")
        print()


if __name__ == "__main__":
    check_users()
