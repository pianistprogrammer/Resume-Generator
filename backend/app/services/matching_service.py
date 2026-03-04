"""Matching service for scoring jobs against user profiles."""

import asyncio
from functools import partial
from typing import List, Optional
from datetime import datetime, timedelta

from app.schemas.user import User, Job, Match, ScoreBreakdown, MatchStatus
from app.config import settings


class MatchingService:
    """Service for matching jobs to users with weighted scoring."""

    # Scoring weights (must sum to 1.0)
    WEIGHTS = {
        "title": 0.30,
        "skills": 0.30,
        "location": 0.15,
        "experience": 0.10,
        "keyword": 0.10,
        "salary": 0.05
    }

    @staticmethod
    def _normalize_text(text: str) -> str:
        """Normalize text for comparison."""
        return text.lower().strip()

    @staticmethod
    def _calculate_title_score(job: Job, user: User) -> float:
        """Calculate title match score (0-100)."""
        job_title = MatchingService._normalize_text(job.title)
        desired_roles = [MatchingService._normalize_text(role) for role in user.preferences.desired_roles]

        # Exact match
        if job_title in desired_roles:
            return 100.0

        # Partial match - check if any desired role is in job title or vice versa
        for role in desired_roles:
            if role in job_title or job_title in role:
                return 75.0

        # Check for common keywords
        job_words = set(job_title.split())
        for role in desired_roles:
            role_words = set(role.split())
            overlap = job_words.intersection(role_words)
            if len(overlap) >= 2:  # At least 2 words match
                return 50.0

        return 0.0

    @staticmethod
    def _calculate_skills_score(job: Job, user: User) -> tuple[float, List[str]]:
        """Calculate skills match score (0-100) and return matched skills."""
        user_skills = set(MatchingService._normalize_text(skill) for skill in user.profile.skills)
        job_skills = set(MatchingService._normalize_text(skill) for skill in job.extracted_skills)

        if not job_skills or not user_skills:
            return 0.0, []

        # Find matches
        matched = user_skills.intersection(job_skills)

        if not matched:
            return 0.0, []

        # Score based on percentage of job skills matched
        match_ratio = len(matched) / len(job_skills)
        score = min(match_ratio * 100, 100.0)

        return score, list(matched)

    @staticmethod
    def _calculate_location_score(job: Job, user: User) -> float:
        """Calculate location match score (0-100)."""
        # Remote jobs get full score if user accepts remote
        if job.remote and user.preferences.remote_preference in ["any", "remote_only", "hybrid"]:
            return 100.0

        # Non-remote jobs
        if not job.location:
            return 50.0  # Unknown location

        job_location = MatchingService._normalize_text(job.location)
        desired_locations = [
            MatchingService._normalize_text(loc) for loc in user.preferences.desired_locations
        ]

        # Check for matches
        for desired in desired_locations:
            if desired in job_location or job_location in desired:
                return 100.0

        # No match and user only wants remote
        if user.preferences.remote_preference == "remote_only":
            return 0.0

        return 25.0  # Different location but user might relocate

    @staticmethod
    def _calculate_experience_score(job: Job, user: User) -> float:
        """Calculate experience level match score (0-100)."""
        if not job.experience_level or not user.preferences.experience_levels:
            return 50.0  # Unknown, neutral score

        if job.experience_level in user.preferences.experience_levels:
            return 100.0

        # Adjacent levels get partial credit
        level_order = ["entry", "junior", "mid", "senior", "lead", "executive"]

        if job.experience_level not in level_order:
            return 50.0

        job_index = level_order.index(job.experience_level)

        for user_level in user.preferences.experience_levels:
            if user_level in level_order:
                user_index = level_order.index(user_level)
                distance = abs(job_index - user_index)

                if distance == 1:
                    return 70.0  # One level away
                elif distance == 2:
                    return 40.0  # Two levels away

        return 20.0

    @staticmethod
    def _calculate_keyword_score(job: Job, user: User) -> tuple[float, List[str]]:
        """Calculate required keywords match score (0-100) and return matched keywords."""
        if not user.preferences.required_keywords:
            return 100.0, []  # No requirements = full score

        job_text = MatchingService._normalize_text(
            f"{job.title} {job.description} {job.normalized_description or ''}"
        )

        matched_keywords = []
        for keyword in user.preferences.required_keywords:
            normalized_keyword = MatchingService._normalize_text(keyword)
            if normalized_keyword in job_text:
                matched_keywords.append(keyword)

        if not user.preferences.required_keywords:
            return 100.0, []

        match_ratio = len(matched_keywords) / len(user.preferences.required_keywords)
        score = match_ratio * 100

        return score, matched_keywords

    @staticmethod
    def _calculate_salary_score(job: Job, user: User) -> float:
        """Calculate salary match score (0-100)."""
        # If no salary info, return neutral score
        if not job.salary_min and not job.salary_max:
            return 50.0

        if not user.preferences.min_salary and not user.preferences.max_salary:
            return 100.0  # User has no salary requirements

        # Check if salary range overlaps with user preferences
        job_min = job.salary_min or 0
        job_max = job.salary_max or float('inf')
        user_min = user.preferences.min_salary or 0
        user_max = user.preferences.max_salary or float('inf')

        # Check if ranges overlap
        if job_max >= user_min and job_min <= user_max:
            return 100.0

        # Job pays less than user wants
        if job_max < user_min:
            gap_percentage = (user_min - job_max) / user_min * 100
            return max(0, 100 - gap_percentage)

        # Job requires more than user wants
        if job_min > user_max:
            return 50.0  # Still possible they might pay in range

        return 50.0

    @staticmethod
    def _apply_hard_filters(job: Job, user: User) -> bool:
        """Apply hard filters that disqualify a job completely."""
        job_text = MatchingService._normalize_text(
            f"{job.title} {job.company} {job.description}"
        )

        # Exclude keywords
        for keyword in user.preferences.exclude_keywords:
            if MatchingService._normalize_text(keyword) in job_text:
                return False

        # Exclude companies
        job_company = MatchingService._normalize_text(job.company)
        for company in user.preferences.exclude_companies:
            if MatchingService._normalize_text(company) in job_company:
                return False

        return True

    @staticmethod
    async def score_job_for_user(job: Job, user: User) -> Optional[Match]:
        """Score a job for a user and create a match if above threshold."""
        loop = asyncio.get_event_loop()

        # Apply hard filters first
        if not MatchingService._apply_hard_filters(job, user):
            return None

        # Calculate individual scores
        title_score = MatchingService._calculate_title_score(job, user)
        skills_score, matched_skills = MatchingService._calculate_skills_score(job, user)
        location_score = MatchingService._calculate_location_score(job, user)
        experience_score = MatchingService._calculate_experience_score(job, user)
        keyword_score, matched_keywords = MatchingService._calculate_keyword_score(job, user)
        salary_score = MatchingService._calculate_salary_score(job, user)

        # Calculate weighted overall score
        overall_score = (
            title_score * MatchingService.WEIGHTS["title"] +
            skills_score * MatchingService.WEIGHTS["skills"] +
            location_score * MatchingService.WEIGHTS["location"] +
            experience_score * MatchingService.WEIGHTS["experience"] +
            keyword_score * MatchingService.WEIGHTS["keyword"] +
            salary_score * MatchingService.WEIGHTS["salary"]
        )

        # Only create match if above threshold
        threshold = user.notification_settings.min_score_threshold if user.notification_settings else settings.min_match_score
        if overall_score < threshold:
            return None

        # Check if match already exists (MongoEngine)
        def _check_existing():
            return Match.objects(user_id=str(user.id), job_id=str(job.id)).first()

        existing_match = await loop.run_in_executor(None, _check_existing)

        if existing_match:
            return existing_match

        # Create score breakdown
        score_breakdown = ScoreBreakdown(
            title_score=title_score,
            skills_score=skills_score,
            location_score=location_score,
            experience_score=experience_score,
            keyword_score=keyword_score,
            salary_score=salary_score,
            matched_skills=matched_skills,
            matched_keywords=matched_keywords
        )

        # Create match (MongoEngine)
        def _create_match():
            match = Match(
                user_id=str(user.id),
                job_id=str(job.id),
                overall_score=overall_score,
                score_breakdown=score_breakdown,
                status=MatchStatus.NEW.value
            )
            match.save()
            return match

        match = await loop.run_in_executor(None, _create_match)
        return match

    @staticmethod
    async def run_matching_for_job(job: Job) -> List[Match]:
        """Score a new job against all active users."""
        loop = asyncio.get_event_loop()

        # Get all users with completed onboarding (MongoEngine)
        def _get_users():
            return list(User.objects(onboarding_completed=True, is_active=True))

        users = await loop.run_in_executor(None, _get_users)

        matches = []
        for user in users:
            match = await MatchingService.score_job_for_user(job, user)
            if match:
                matches.append(match)

        return matches

    @staticmethod
    async def run_matching_for_user(user: User, days: int = 7) -> List[Match]:
        """Score a user against recent jobs."""
        loop = asyncio.get_event_loop()

        # Get recent jobs (MongoEngine)
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        def _get_jobs():
            return list(Job.objects(ingested_at__gte=cutoff_date))

        jobs = await loop.run_in_executor(None, _get_jobs)

        matches = []
        for job in jobs:
            match = await MatchingService.score_job_for_user(job, user)
            if match:
                matches.append(match)

        return matches
