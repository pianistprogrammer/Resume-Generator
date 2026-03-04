"""Debug matching scores for a specific user."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import connect_to_mongo, close_mongo_connection
from app.schemas.user import User, Job
from app.services.matching_service import MatchingService
from mongoengine.connection import get_db


async def debug_user_matching(user_email: str = None):
    """Debug matching for a specific user."""
    print("🔍 Debug Matching Process\n")

    # Disable auto-indexing
    import mongoengine
    mongoengine.Document._auto_index_enabled = False

    # Get user
    if user_email:
        user = User.objects(email=user_email).first()
    else:
        user = User.objects(onboarding_completed=True).first()

    if not user:
        print("❌ No user found")
        return

    print(f"USER: {user.email}")
    print(f"Onboarding Completed: {user.onboarding_completed}")

    if user.profile:
        print(f"\nPROFILE:")
        print(f"  Skills: {user.profile.skills}")
        print(f"  Current Title: {user.profile.current_title}")
        print(f"  Years of Experience: {user.profile.years_of_experience}")

    if user.preferences:
        print(f"\nPREFERENCES:")
        print(f"  Desired Roles: {user.preferences.desired_roles}")
        print(f"  Desired Locations: {user.preferences.desired_locations}")
        print(f"  Remote Preference: {user.preferences.remote_preference}")
        print(f"  Experience Levels: {user.preferences.experience_levels}")
        print(f"  Required Keywords: {user.preferences.required_keywords}")
        print(f"  Exclude Keywords: {user.preferences.exclude_keywords}")

    if user.notification_settings:
        print(f"\nNOTIFICATION SETTINGS:")
        print(f"  Min Score Threshold: {user.notification_settings.min_score_threshold}")

    # Get first 10 jobs
    jobs = list(Job.objects()[:10])
    print(f"\n\n📊 TESTING AGAINST {len(jobs)} JOBS:\n")
    print("=" * 80)

    matched_count = 0

    for i, job in enumerate(jobs, 1):
        print(f"\nJOB #{i}: {job.title} at {job.company}")
        print(f"  Remote: {job.remote}")
        print(f"  Location: {job.location}")
        print(f"  Skills: {job.extracted_skills[:5] if job.extracted_skills else []}")
        print(f"  Experience Level: {job.experience_level}")

        # Calculate scores
        title_score = MatchingService._calculate_title_score(job, user)
        skills_score, matched_skills = MatchingService._calculate_skills_score(job, user)
        location_score = MatchingService._calculate_location_score(job, user)
        experience_score = MatchingService._calculate_experience_score(job, user)
        keyword_score, matched_keywords = MatchingService._calculate_keyword_score(job, user)
        salary_score = MatchingService._calculate_salary_score(job, user)

        overall_score = (
            title_score * MatchingService.WEIGHTS["title"] +
            skills_score * MatchingService.WEIGHTS["skills"] +
            location_score * MatchingService.WEIGHTS["location"] +
            experience_score * MatchingService.WEIGHTS["experience"] +
            keyword_score * MatchingService.WEIGHTS["keyword"] +
            salary_score * MatchingService.WEIGHTS["salary"]
        )

        print(f"\n  SCORES:")
        print(f"    Title:      {title_score:5.1f}  (weight: {MatchingService.WEIGHTS['title']*100:.0f}%)")
        print(f"    Skills:     {skills_score:5.1f}  (weight: {MatchingService.WEIGHTS['skills']*100:.0f}%) - Matched: {matched_skills}")
        print(f"    Location:   {location_score:5.1f}  (weight: {MatchingService.WEIGHTS['location']*100:.0f}%)")
        print(f"    Experience: {experience_score:5.1f}  (weight: {MatchingService.WEIGHTS['experience']*100:.0f}%)")
        print(f"    Keyword:    {keyword_score:5.1f}  (weight: {MatchingService.WEIGHTS['keyword']*100:.0f}%) - Matched: {matched_keywords}")
        print(f"    Salary:     {salary_score:5.1f}  (weight: {MatchingService.WEIGHTS['salary']*100:.0f}%)")
        print(f"  OVERALL:      {overall_score:5.1f}")

        threshold = user.notification_settings.min_score_threshold if user.notification_settings else 60.0
        if overall_score >= threshold:
            print(f"  ✅ MATCH! (above threshold of {threshold})")
            matched_count += 1
        else:
            print(f"  ❌ NO MATCH (below threshold of {threshold})")

        print("-" * 80)

    print(f"\n\n📊 SUMMARY:")
    print(f"Total Jobs Tested: {len(jobs)}")
    print(f"Matches Found: {matched_count}")
    print(f"Match Rate: {matched_count/len(jobs)*100:.1f}%")


async def main():
    """Main function."""
    connect_to_mongo()

    try:
        # Get email from command line if provided
        email = sys.argv[1] if len(sys.argv) > 1 else None
        await debug_user_matching(email)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(main())
