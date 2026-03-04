"""Admin service for managing the application."""

import asyncio
from functools import partial
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from mongoengine import Q

from app.schemas.user import User, Job, Match, Resume, FeedSource, Payment, Notification


class AdminService:
    """Service for admin operations."""

    # ===== Dashboard Stats =====
    @staticmethod
    async def get_dashboard_stats() -> Dict[str, Any]:
        """Get overview statistics for admin dashboard."""
        loop = asyncio.get_event_loop()

        # Get counts
        total_users = await loop.run_in_executor(None, User.objects.count)
        total_jobs = await loop.run_in_executor(None, Job.objects.count)
        total_matches = await loop.run_in_executor(None, Match.objects.count)
        total_resumes = await loop.run_in_executor(None, Resume.objects.count)
        active_feeds = await loop.run_in_executor(
            None, lambda: FeedSource.objects(is_active=True).count()
        )

        # Users registered in last 7 days
        week_ago = datetime.utcnow() - timedelta(days=7)
        new_users_week = await loop.run_in_executor(
            None, lambda: User.objects(created_at__gte=week_ago).count()
        )

        # Jobs ingested in last 24 hours
        day_ago = datetime.utcnow() - timedelta(days=1)
        new_jobs_today = await loop.run_in_executor(
            None, lambda: Job.objects(ingested_at__gte=day_ago).count()
        )

        # Resumes generated in last 7 days
        new_resumes_week = await loop.run_in_executor(
            None, lambda: Resume.objects(created_at__gte=week_ago).count()
        )

        return {
            "total_users": total_users,
            "total_jobs": total_jobs,
            "total_matches": total_matches,
            "total_resumes": total_resumes,
            "active_feeds": active_feeds,
            "new_users_week": new_users_week,
            "new_jobs_today": new_jobs_today,
            "new_resumes_week": new_resumes_week,
        }

    # ===== User Management =====
    @staticmethod
    async def get_all_users(
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        is_admin: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """Get all users with pagination and filtering."""
        loop = asyncio.get_event_loop()

        def _query():
            query = User.objects

            # Apply filters
            if search:
                query = query.filter(
                    Q(email__icontains=search) |
                    Q(profile__full_name__icontains=search)
                )

            if is_admin is not None:
                query = query.filter(is_admin=is_admin)

            return list(query.skip(skip).limit(limit).order_by('-created_at'))

        users = await loop.run_in_executor(None, _query)

        return [
            {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.profile.full_name if user.profile else None,
                "is_admin": user.is_admin,
                "is_active": user.is_active,
                "credits": user.credits,
                "onboarding_completed": user.onboarding_completed,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_login": user.last_login.isoformat() if user.last_login else None,
            }
            for user in users
        ]

    @staticmethod
    async def get_user_details(user_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific user."""
        loop = asyncio.get_event_loop()

        user = await loop.run_in_executor(None, partial(User.objects.get, id=user_id))

        # Get user's matches, resumes, payments
        match_count = await loop.run_in_executor(
            None, lambda: Match.objects(user_id=str(user.id)).count()
        )
        resume_count = await loop.run_in_executor(
            None, lambda: Resume.objects(user_id=str(user.id)).count()
        )
        payment_count = await loop.run_in_executor(
            None, lambda: Payment.objects(user_id=str(user.id), status="completed").count()
        )

        return {
            "id": str(user.id),
            "email": user.email,
            "profile": {
                "full_name": user.profile.full_name if user.profile else None,
                "location": user.profile.location if user.profile else None,
                "current_title": user.profile.current_title if user.profile else None,
                "years_of_experience": user.profile.years_of_experience if user.profile else None,
                "skills": user.profile.skills if user.profile else [],
            },
            "preferences": {
                "desired_roles": user.preferences.desired_roles if user.preferences else [],
                "remote_preference": user.preferences.remote_preference if user.preferences else None,
            },
            "is_admin": user.is_admin,
            "is_active": user.is_active,
            "onboarding_completed": user.onboarding_completed,
            "credits": user.credits,
            "total_credits_purchased": user.total_credits_purchased,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "stats": {
                "match_count": match_count,
                "resume_count": resume_count,
                "payment_count": payment_count,
            }
        }

    @staticmethod
    async def update_user_credits(user_id: str, credits: int) -> Dict[str, Any]:
        """Update user's credit balance."""
        loop = asyncio.get_event_loop()

        def _update():
            user = User.objects.get(id=user_id)
            user.credits = credits
            user.updated_at = datetime.utcnow()
            user.save()
            return user

        user = await loop.run_in_executor(None, _update)

        return {
            "id": str(user.id),
            "email": user.email,
            "credits": user.credits,
        }

    @staticmethod
    async def toggle_user_admin(user_id: str) -> Dict[str, Any]:
        """Toggle user's admin status."""
        loop = asyncio.get_event_loop()

        def _update():
            user = User.objects.get(id=user_id)
            user.is_admin = not user.is_admin
            user.updated_at = datetime.utcnow()
            user.save()
            return user

        user = await loop.run_in_executor(None, _update)

        return {
            "id": str(user.id),
            "email": user.email,
            "is_admin": user.is_admin,
        }

    @staticmethod
    async def toggle_user_active(user_id: str) -> Dict[str, Any]:
        """Toggle user's active status."""
        loop = asyncio.get_event_loop()

        def _update():
            user = User.objects.get(id=user_id)
            user.is_active = not user.is_active
            user.updated_at = datetime.utcnow()
            user.save()
            return user

        user = await loop.run_in_executor(None, _update)

        return {
            "id": str(user.id),
            "email": user.email,
            "is_active": user.is_active,
        }

    # ===== Feed Source Management =====
    @staticmethod
    async def get_all_feeds(include_inactive: bool = False) -> List[Dict[str, Any]]:
        """Get all feed sources."""
        loop = asyncio.get_event_loop()

        def _query():
            query = FeedSource.objects
            if not include_inactive:
                query = query.filter(is_active=True)
            return list(query.order_by('-created_at'))

        feeds = await loop.run_in_executor(None, _query)

        return [
            {
                "id": str(feed.id),
                "name": feed.name,
                "url": feed.url,
                "feed_type": feed.feed_type,
                "company_token": feed.company_token,
                "is_active": feed.is_active,
                "last_scraped_at": feed.last_scraped_at.isoformat() if feed.last_scraped_at else None,
                "last_scrape_success": feed.last_scrape_success,
                "last_scrape_error": feed.last_scrape_error,
                "total_jobs_scraped": feed.total_jobs_scraped,
                "last_scrape_job_count": feed.last_scrape_job_count,
                "created_at": feed.created_at.isoformat() if feed.created_at else None,
            }
            for feed in feeds
        ]

    @staticmethod
    async def create_feed(
        name: str,
        url: str,
        feed_type: str,
        company_token: Optional[str],
        admin_id: str
    ) -> Dict[str, Any]:
        """Create a new feed source."""
        loop = asyncio.get_event_loop()

        def _create():
            feed = FeedSource(
                name=name,
                url=url,
                feed_type=feed_type,
                company_token=company_token,
                created_by=admin_id,
            )
            feed.save()
            return feed

        feed = await loop.run_in_executor(None, _create)

        return {
            "id": str(feed.id),
            "name": feed.name,
            "url": feed.url,
            "feed_type": feed.feed_type,
            "company_token": feed.company_token,
            "is_active": feed.is_active,
        }

    @staticmethod
    async def update_feed(
        feed_id: str,
        name: Optional[str] = None,
        url: Optional[str] = None,
        feed_type: Optional[str] = None,
        company_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update a feed source."""
        loop = asyncio.get_event_loop()

        def _update():
            feed = FeedSource.objects.get(id=feed_id)
            if name is not None:
                feed.name = name
            if url is not None:
                feed.url = url
            if feed_type is not None:
                feed.feed_type = feed_type
            if company_token is not None:
                feed.company_token = company_token
            feed.updated_at = datetime.utcnow()
            feed.save()
            return feed

        feed = await loop.run_in_executor(None, _update)

        return {
            "id": str(feed.id),
            "name": feed.name,
            "url": feed.url,
            "feed_type": feed.feed_type,
            "is_active": feed.is_active,
        }

    @staticmethod
    async def toggle_feed_active(feed_id: str) -> Dict[str, Any]:
        """Toggle feed's active status."""
        loop = asyncio.get_event_loop()

        def _update():
            feed = FeedSource.objects.get(id=feed_id)
            feed.is_active = not feed.is_active
            feed.updated_at = datetime.utcnow()
            feed.save()
            return feed

        feed = await loop.run_in_executor(None, _update)

        return {
            "id": str(feed.id),
            "name": feed.name,
            "is_active": feed.is_active,
        }

    @staticmethod
    async def delete_feed(feed_id: str) -> None:
        """Delete a feed source."""
        loop = asyncio.get_event_loop()

        def _delete():
            feed = FeedSource.objects.get(id=feed_id)
            feed.delete()

        await loop.run_in_executor(None, _delete)

    # ===== Job Management =====
    @staticmethod
    async def get_all_jobs(
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        source: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all jobs with pagination and filtering."""
        loop = asyncio.get_event_loop()

        def _query():
            query = Job.objects

            if search:
                query = query.filter(
                    Q(title__icontains=search) |
                    Q(company__icontains=search)
                )

            if source:
                query = query.filter(source=source)

            return list(query.skip(skip).limit(limit).order_by('-ingested_at'))

        jobs = await loop.run_in_executor(None, _query)

        return [
            {
                "id": str(job.id),
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "remote": job.remote,
                "source": job.source,
                "ats_platform": job.ats_platform,
                "apply_url": job.apply_url,
                "ingested_at": job.ingested_at.isoformat() if job.ingested_at else None,
            }
            for job in jobs
        ]

    @staticmethod
    async def delete_job(job_id: str) -> None:
        """Delete a job posting."""
        loop = asyncio.get_event_loop()

        def _delete():
            job = Job.objects.get(id=job_id)
            # Also delete associated matches
            Match.objects(job_id=str(job.id)).delete()
            job.delete()

        await loop.run_in_executor(None, _delete)

    # ===== Resume Management =====
    @staticmethod
    async def get_all_resumes(
        skip: int = 0,
        limit: int = 50,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all resumes with pagination and filtering."""
        loop = asyncio.get_event_loop()

        def _query():
            query = Resume.objects

            if user_id:
                query = query.filter(user_id=user_id)

            return list(query.skip(skip).limit(limit).order_by('-created_at'))

        resumes = await loop.run_in_executor(None, _query)

        result = []
        for resume in resumes:
            # Get user and job info
            try:
                user = await loop.run_in_executor(None, partial(User.objects.get, id=resume.user_id))
                job = await loop.run_in_executor(None, partial(Job.objects.get, id=resume.job_id))

                result.append({
                    "id": str(resume.id),
                    "user_email": user.email,
                    "job_title": job.title,
                    "job_company": job.company,
                    "pdf_url": resume.pdf_url,
                    "ats_score": resume.ats_score,
                    "created_at": resume.created_at.isoformat() if resume.created_at else None,
                })
            except Exception:
                continue

        return result
