"""Migrate is_admin field to role field for all users."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import connect_to_mongo
from pymongo import MongoClient
from app.config import settings


def migrate_users():
    """Migrate all users from is_admin to role field."""
    print("🔄 Starting migration from is_admin to role field...\n")
    
    # Connect directly with pymongo to avoid MongoEngine schema validation
    client = MongoClient(settings.mongodb_url)
    db = client[settings.mongodb_db_name]
    users_collection = db['users']
    
    # Find all users
    users = list(users_collection.find({}))
    print(f"📊 Found {len(users)} users to migrate\n")
    
    updated_count = 0
    
    for user in users:
        email = user.get('email', 'unknown')
        has_is_admin = 'is_admin' in user
        has_role = 'role' in user
        
        if has_is_admin:
            # Determine the role based on is_admin value
            is_admin = user.get('is_admin', False)
            new_role = 'admin' if is_admin else 'user'
            
            # Update the user document
            update_ops = {}
            
            # Add role field if it doesn't exist or update it
            update_ops['$set'] = {'role': new_role}
            
            # Remove is_admin field
            update_ops['$unset'] = {'is_admin': ''}
            
            users_collection.update_one(
                {'_id': user['_id']},
                update_ops
            )
            
            updated_count += 1
            print(f"✅ Migrated user: {email} -> role: {new_role}")
        elif not has_role:
            # No is_admin and no role, set default role
            users_collection.update_one(
                {'_id': user['_id']},
                {'$set': {'role': 'user'}}
            )
            updated_count += 1
            print(f"✅ Set default role for user: {email} -> role: user")
        else:
            print(f"⏭️  User already migrated: {email} -> role: {user.get('role')}")
    
    print(f"\n✨ Migration complete! Updated {updated_count} users")
    
    # Verify migration
    print("\n🔍 Verifying migration...")
    remaining_with_is_admin = users_collection.count_documents({'is_admin': {'$exists': True}})
    users_with_role = users_collection.count_documents({'role': {'$exists': True}})
    total_users = users_collection.count_documents({})
    
    print(f"   - Total users: {total_users}")
    print(f"   - Users with role field: {users_with_role}")
    print(f"   - Users still with is_admin field: {remaining_with_is_admin}")
    
    if remaining_with_is_admin == 0 and users_with_role == total_users:
        print("\n✅ Migration verified successfully!")
    else:
        print("\n⚠️  Warning: Some users may not have been migrated correctly")
    
    client.close()


if __name__ == "__main__":
    migrate_users()
