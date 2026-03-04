"""Job service for managing job postings."""

import asyncio
from functools import partial
from typing import Optional, List
from datetime import datetime, timedelta
from fastapi import HTTPException, status

from app.schemas.user import Job, Match


class JobService:
    """Service for job-related operations."""

    @staticmethod
    async def get_job_by_id(job_id: str) -> Optional[Job]:
        """Get a job by ID."""
        loop = asyncio.get_event_loop()

        def _get():
            try:
                return Job.objects(id=job_id).first()
            except Exception:
                return None

        return await loop.run_in_executor(None, _get)

    @staticmethod
    async def get_jobs(
        skip: int = 0,
        limit: int = 20,
        company: Optional[str] = None,
        remote: Optional[bool] = None,
        search: Optional[str] = None
    ) -> List[Job]:
        """Get jobs with optional filters."""
        loop = asyncio.get_event_loop()

        def _query():
            query = Job.objects

            if company:
                query = query.filter(company__icontains=company)

            if remote is not None:
                query = query.filter(remote=remote)

            if search:
                from mongoengine import Q
                query = query.filter(
                    Q(title__icontains=search) | Q(description__icontains=search)
                )

            return list(query.skip(skip).limit(limit).order_by('-ingested_at'))

        return await loop.run_in_executor(None, _query)

    @staticmethod
    async def get_recent_jobs(days: int = 7) -> List[Job]:
        """Get jobs ingested in the last N days."""
        loop = asyncio.get_event_loop()
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        def _query():
            return list(Job.objects(ingested_at__gte=cutoff_date).order_by('-ingested_at'))

        return await loop.run_in_executor(None, _query)

    @staticmethod
    async def create_job(
        title: str,
        company: str,
        description: str,
        apply_url: str,
        source: str,
        source_url: str,
        location: Optional[str] = None,
        remote: bool = False,
        salary_min: Optional[int] = None,
        salary_max: Optional[int] = None,
        experience_level: Optional[str] = None,
        ats_platform: Optional[str] = None,
        normalized_description: Optional[str] = None,
        extracted_skills: Optional[List[str]] = None,
        posted_at: Optional[datetime] = None
    ) -> Optional[Job]:
        """Create a new job posting with deduplication."""
        loop = asyncio.get_event_loop()

        # Generate fingerprint
        fingerprint = Job.generate_fingerprint(title, company, apply_url)

        def _create():
            # Check if job already exists
            existing_job = Job.objects(fingerprint=fingerprint).first()
            if existing_job:
                return None  # Job already exists

            # Create new job
            job = Job(
                title=title,
                company=company,
                description=description,
                apply_url=apply_url,
                location=location,
                remote=remote,
                salary_min=salary_min,
                salary_max=salary_max,
                experience_level=experience_level,
                source=source,
                source_url=source_url,
                ats_platform=ats_platform,
                fingerprint=fingerprint,
                normalized_description=normalized_description,
                extracted_skills=extracted_skills or [],
                posted_at=posted_at,
                ingested_at=datetime.utcnow()
            )
            job.save()
            return job

        return await loop.run_in_executor(None, _create)

    @staticmethod
    async def get_user_matches(
        user_id: str,
        skip: int = 0,
        limit: int = 20,
        status_filter: Optional[str] = None,
        min_score: Optional[float] = None
    ) -> List[dict]:
        """Get matches for a user with job details."""
        loop = asyncio.get_event_loop()

        def _query():
            query = Match.objects(user_id=user_id)

            if status_filter:
                query = query.filter(status=status_filter)

            if min_score is not None:
                query = query.filter(overall_score__gte=min_score)

            return list(query.skip(skip).limit(limit).order_by('-overall_score'))

        matches = await loop.run_in_executor(None, _query)

        # Enrich with job details
        enriched_matches = []
        for match in matches:
            job = await JobService.get_job_by_id(match.job_id)
            if job:
                enriched_matches.append({
                    "match": match,
                    "job": job
                })

        return enriched_matches

    @staticmethod
    async def get_match_by_id(match_id: str, user_id: str) -> Optional[Match]:
        """Get a match by ID, ensuring it belongs to the user."""
        loop = asyncio.get_event_loop()

        def _get():
            try:
                match = Match.objects(id=match_id).first()
                if match and match.user_id != user_id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Access denied"
                    )
                return match
            except HTTPException:
                raise
            except Exception:
                return None

        return await loop.run_in_executor(None, _get)

    @staticmethod
    async def update_match_status(match_id: str, user_id: str, new_status: str) -> Match:
        """Update the status of a match."""
        match = await JobService.get_match_by_id(match_id, user_id)

        if not match:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Match not found"
            )

        loop = asyncio.get_event_loop()

        def _update():
            match.status = new_status
            match.updated_at = datetime.utcnow()

            if new_status == "applied":
                match.applied_at = datetime.utcnow()

            match.save()
            return match

        return await loop.run_in_executor(None, _update)

    @staticmethod
    async def get_dashboard_stats(user_id: str) -> dict:
        """Get dashboard statistics for a user."""
        loop = asyncio.get_event_loop()

        def _get_stats():
            # Total matches
            total_matches = Match.objects(user_id=user_id).count()

            # New matches (last 24 hours)
            yesterday = datetime.utcnow() - timedelta(days=1)
            new_matches = Match.objects(
                user_id=user_id,
                created_at__gte=yesterday
            ).count()

            # Applied
            applied_count = Match.objects(
                user_id=user_id,
                status="applied"
            ).count()

            # Average score
            all_matches = list(Match.objects(user_id=user_id))
            avg_score = sum(m.overall_score for m in all_matches) / len(all_matches) if all_matches else 0

            return {
                "total_matches": total_matches,
                "new_matches": new_matches,
                "applied_count": applied_count,
                "average_score": round(avg_score, 1)
            }

        return await loop.run_in_executor(None, _get_stats)
