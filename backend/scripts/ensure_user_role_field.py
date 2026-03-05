"""Ensure all users have the role field - can be run standalone or automatically on startup."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pymongo import MongoClient
from app.config import settings


def ensure_all_users_have_role():
    """
    Ensure all User documents have the 'role' field.
    
    This function:
    1. Migrates users with 'is_admin' field to 'role' field
    2. Adds 'role' field with default value 'user' to users without it
    3. Can be run multiple times safely (idempotent)
    """
    print("🔄 Checking users for role field...\n")
    
    # Connect directly with pymongo to bypass MongoEngine schema validation
    client = MongoClient(settings.mongodb_url)
    db = client[settings.mongodb_db_name]
    users_collection = db['users']
    
    # Count total users
    total_users = users_collection.count_documents({})
    print(f"📊 Total users in database: {total_users}")
    
    # Find users without role field or with is_admin field
    users_needing_migration = users_collection.count_documents({
        '$or': [
            {'role': {'$exists': False}},
            {'is_admin': {'$exists': True}}
        ]
    })
    
    if users_needing_migration == 0:
        print("\n✅ All users already have the role field - no migration needed!")
        
        # Show role distribution
        admin_count = users_collection.count_documents({'role': 'admin'})
        user_count = users_collection.count_documents({'role': 'user'})
        print(f"\n📈 Role Distribution:")
        print(f"   - Admins: {admin_count}")
        print(f"   - Users: {user_count}")
        
        client.close()
        return
    
    print(f"🔧 Found {users_needing_migration} users needing migration\n")
    
    migrated_count = 0
    
    # 1. Migrate users with is_admin field
    users_with_is_admin = list(users_collection.find({'is_admin': {'$exists': True}}))
    if users_with_is_admin:
        print(f"🔄 Migrating {len(users_with_is_admin)} users from is_admin to role...")
        
        for user in users_with_is_admin:
            email = user.get('email', 'unknown')
            is_admin = user.get('is_admin', False)
            new_role = 'admin' if is_admin else 'user'
            
            users_collection.update_one(
                {'_id': user['_id']},
                {
                    '$set': {'role': new_role},
                    '$unset': {'is_admin': ''}
                }
            )
            
            migrated_count += 1
            print(f"   ✅ {email} -> role: {new_role} (was is_admin: {is_admin})")
    
    # 2. Add role field to users without it (with default 'user')
    users_without_role = list(users_collection.find({'role': {'$exists': False}}))
    if users_without_role:
        print(f"\n🔄 Adding role field to {len(users_without_role)} users...")
        
        for user in users_without_role:
            email = user.get('email', 'unknown')
            
            users_collection.update_one(
                {'_id': user['_id']},
                {'$set': {'role': 'user'}}
            )
            
            migrated_count += 1
            print(f"   ✅ {email} -> role: user (default)")
    
    print(f"\n✨ Migration complete! Updated {migrated_count} users")
    
    # Verify migration
    print("\n🔍 Verifying migration...")
    remaining_without_role = users_collection.count_documents({'role': {'$exists': False}})
    remaining_with_is_admin = users_collection.count_documents({'is_admin': {'$exists': True}})
    users_with_role = users_collection.count_documents({'role': {'$exists': True}})
    
    print(f"   - Total users: {total_users}")
    print(f"   - Users with role field: {users_with_role}")
    print(f"   - Users without role field: {remaining_without_role}")
    print(f"   - Users still with is_admin field: {remaining_with_is_admin}")
    
    # Show role distribution
    admin_count = users_collection.count_documents({'role': 'admin'})
    user_count = users_collection.count_documents({'role': 'user'})
    print(f"\n📈 Role Distribution:")
    print(f"   - Admins: {admin_count}")
    print(f"   - Users: {user_count}")
    
    if remaining_without_role == 0 and remaining_with_is_admin == 0 and users_with_role == total_users:
        print("\n✅ Migration verified successfully! All users have the role field.")
    else:
        print("\n⚠️  Warning: Some users may not have been migrated correctly")
        print("   Please check the database manually")
    
    client.close()


if __name__ == "__main__":
    try:
        ensure_all_users_have_role()
    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
