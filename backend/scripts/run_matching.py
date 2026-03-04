"""Run matching for all users against all jobs."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import connect_to_mongo, close_mongo_connection
from app.schemas.user import User, Job
from app.services.matching_service import MatchingService


async def run_matching_for_all():
    """Run matching for all users against all jobs."""
    print("🔍 Starting matching process...\n")

    # Get all active users with completed onboarding
    users = list(User.objects(onboarding_completed=True, is_active=True))
    print(f"Found {len(users)} users with completed onboarding")

    # Get all jobs
    jobs = list(Job.objects())
    print(f"Found {len(jobs)} jobs in database\n")

    if not users:
        print("❌ No users found with completed onboarding")
        return

    if not jobs:
        print("❌ No jobs found in database")
        return

    total_matches = 0

    for user in users:
        print(f"Processing user: {user.email}")
        print(f"  Profile Skills: {user.profile.skills[:5] if user.profile and user.profile.skills else []}")
        print(f"  Desired Roles: {user.preferences.desired_roles if user.preferences else []}")
        print(f"  Remote Preference: {user.preferences.remote_preference if user.preferences else 'any'}")

        user_matches = 0
        for job in jobs:
            try:
                match = await MatchingService.score_job_for_user(job, user)
                if match:
                    user_matches += 1
            except Exception as e:
                print(f"  ❌ Error matching job {job.id}: {e}")
                continue

        print(f"  ✅ Created {user_matches} matches for {user.email}\n")
        total_matches += user_matches

    print(f"\n✨ Matching complete!")
    print(f"📊 Total matches created: {total_matches}")


async def main():
    """Main function."""
    connect_to_mongo()

    try:
        await run_matching_for_all()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(main())
