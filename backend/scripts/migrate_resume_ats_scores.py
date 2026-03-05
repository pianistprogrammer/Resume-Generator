"""Migrate ATS scores from resume.content.ats_score to resume.ats_score for existing resumes."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pymongo import MongoClient
from app.config import settings


def migrate_resume_ats_scores():
    """
    Copy ATS scores from content.ats_score to top-level ats_score field.
    
    This ensures compatibility with both old and new resume documents.
    """
    print("🔄 Migrating resume ATS scores...\n")
    
    # Connect with pymongo
    client = MongoClient(settings.mongodb_url)
    db = client[settings.mongodb_db_name]
    resumes_collection = db['resumes']
    
    # Count total resumes
    total_resumes = resumes_collection.count_documents({})
    print(f"📊 Total resumes in database: {total_resumes}")
    
    # Find resumes with content.ats_score but no top-level ats_score
    resumes_needing_migration = list(resumes_collection.find({
        'content.ats_score': {'$exists': True},
        '$or': [
            {'ats_score': {'$exists': False}},
            {'ats_score': None}
        ]
    }))
    
    if not resumes_needing_migration:
        print("\n✅ All resumes already have top-level ats_score - no migration needed!")
        
        # Show stats
        resumes_with_score = resumes_collection.count_documents({'ats_score': {'$exists': True, '$ne': None}})
        print(f"\n📈 ATS Score Coverage:")
        print(f"   - Resumes with ATS score: {resumes_with_score}/{total_resumes}")
        
        client.close()
        return
    
    print(f"🔧 Found {len(resumes_needing_migration)} resumes needing migration\n")
    
    migrated_count = 0
    
    for resume in resumes_needing_migration:
        resume_id = resume['_id']
        content_ats_score = resume.get('content', {}).get('ats_score')
        
        if content_ats_score is not None:
            resumes_collection.update_one(
                {'_id': resume_id},
                {'$set': {'ats_score': float(content_ats_score)}}
            )
            
            migrated_count += 1
            user_id = resume.get('user_id', 'unknown')
            print(f"   ✅ Resume {resume_id} (user: {user_id}) -> ats_score: {content_ats_score}")
    
    print(f"\n✨ Migration complete! Updated {migrated_count} resumes")
    
    # Verify migration
    print("\n🔍 Verifying migration...")
    resumes_without_score = resumes_collection.count_documents({
        '$or': [
            {'ats_score': {'$exists': False}},
            {'ats_score': None}
        ]
    })
    resumes_with_score = resumes_collection.count_documents({'ats_score': {'$exists': True, '$ne': None}})
    
    print(f"   - Total resumes: {total_resumes}")
    print(f"   - Resumes with ATS score: {resumes_with_score}")
    print(f"   - Resumes without ATS score: {resumes_without_score}")
    
    if resumes_without_score == 0:
        print("\n✅ Migration verified successfully! All resumes have ATS scores.")
    else:
        print(f"\n⚠️  Warning: {resumes_without_score} resumes still don't have ATS scores")
        print("   These might be legacy resumes without content.ats_score either")
    
    client.close()


if __name__ == "__main__":
    try:
        migrate_resume_ats_scores()
    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
