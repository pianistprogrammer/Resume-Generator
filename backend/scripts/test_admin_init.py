"""Test the admin initialization function."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import connect_to_mongo, initialize_admin_user
from app.schemas.user import User


def test_admin_initialization():
    """Test that admin initialization works."""
    print("🧪 Testing admin initialization...\n")
    
    # Connect to database
    connect_to_mongo()
    
    # Check current state
    users_before = User.objects.count()
    admin_before = User.objects(email="admin@domain.com").first()
    
    print(f"Before initialization:")
    print(f"  Total users: {users_before}")
    print(f"  Admin exists: {'Yes' if admin_before else 'No'}")
    print()
    
    # Run initialization
    initialize_admin_user()
    print()
    
    # Check after
    users_after = User.objects.count()
    admin_after = User.objects(email="admin@domain.com").first()
    
    print(f"After initialization:")
    print(f"  Total users: {users_after}")
    print(f"  Admin exists: {'Yes' if admin_after else 'No'}")
    
    if admin_after:
        print(f"  Admin role: {admin_after.role}")
        print(f"  Admin credits: {admin_after.credits}")
        print(f"  Admin active: {admin_after.is_active}")
    
    print()
    print("✅ Test complete!")


if __name__ == "__main__":
    test_admin_initialization()
