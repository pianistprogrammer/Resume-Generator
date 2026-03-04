"""Profile service for managing user profiles and preferences."""

from datetime import datetime
from typing import Optional
from fastapi import HTTPException, status

from app.schemas import (
    User, UserProfile, JobPreferences, NotificationSettings,
    WorkExperience, Education, Certification
)


class ProfileService:
    """Service for profile management operations."""

    @staticmethod
    def update_profile(
        user: User,
        full_name: Optional[str] = None,
        phone: Optional[str] = None,
        location: Optional[str] = None,
        linkedin_url: Optional[str] = None,
        github_url: Optional[str] = None,
        portfolio_url: Optional[str] = None,
        current_title: Optional[str] = None,
        years_of_experience: Optional[int] = None,
        skills: Optional[list[str]] = None,
        work_experience: Optional[list[dict]] = None,
        education: Optional[list[dict]] = None,
        certifications: Optional[list[dict]] = None,
        summary: Optional[str] = None
    ) -> User:
        """Update user profile information."""

        # Update basic fields
        if full_name is not None:
            user.profile.full_name = full_name
        if phone is not None:
            user.profile.phone = phone
        if location is not None:
            user.profile.location = location
        if linkedin_url is not None:
            user.profile.linkedin_url = linkedin_url
        if github_url is not None:
            user.profile.github_url = github_url
        if portfolio_url is not None:
            user.profile.portfolio_url = portfolio_url
        if current_title is not None:
            user.profile.current_title = current_title
        if years_of_experience is not None:
            user.profile.years_of_experience = years_of_experience
        if skills is not None:
            user.profile.skills = skills
        if summary is not None:
            user.profile.summary = summary

        # Update complex fields
        if work_experience is not None:
            user.profile.work_experience = [
                WorkExperience(**exp) for exp in work_experience
            ]

        if education is not None:
            user.profile.education = [
                Education(**edu) for edu in education
            ]

        if certifications is not None:
            user.profile.certifications = [
                Certification(**cert) for cert in certifications
            ]

        user.updated_at = datetime.utcnow()
        user.save()

        return user

    @staticmethod
    def update_preferences(
        user: User,
        desired_roles: Optional[list[str]] = None,
        desired_locations: Optional[list[str]] = None,
        remote_preference: Optional[str] = None,
        min_salary: Optional[int] = None,
        max_salary: Optional[int] = None,
        experience_levels: Optional[list[str]] = None,
        required_keywords: Optional[list[str]] = None,
        exclude_keywords: Optional[list[str]] = None,
        exclude_companies: Optional[list[str]] = None
    ) -> User:
        """Update user job preferences."""

        if desired_roles is not None:
            user.preferences.desired_roles = desired_roles
        if desired_locations is not None:
            user.preferences.desired_locations = desired_locations
        if remote_preference is not None:
            user.preferences.remote_preference = remote_preference
        if min_salary is not None:
            user.preferences.min_salary = min_salary
        if max_salary is not None:
            user.preferences.max_salary = max_salary
        if experience_levels is not None:
            user.preferences.experience_levels = experience_levels
        if required_keywords is not None:
            user.preferences.required_keywords = required_keywords
        if exclude_keywords is not None:
            user.preferences.exclude_keywords = exclude_keywords
        if exclude_companies is not None:
            user.preferences.exclude_companies = exclude_companies

        user.updated_at = datetime.utcnow()
        user.save()

        # TODO: Trigger matching for user against recent jobs
        # This will be implemented in the matching service

        return user

    @staticmethod
    def update_notification_settings(
        user: User,
        email_enabled: Optional[bool] = None,
        frequency: Optional[str] = None,
        min_score_threshold: Optional[float] = None,
        digest_time_hour: Optional[int] = None,
        notify_resume_ready: Optional[bool] = None
    ) -> User:
        """Update user notification settings."""

        if email_enabled is not None:
            user.notification_settings.email_enabled = email_enabled
        if frequency is not None:
            user.notification_settings.frequency = frequency
        if min_score_threshold is not None:
            user.notification_settings.min_score_threshold = min_score_threshold
        if digest_time_hour is not None:
            user.notification_settings.digest_time_hour = digest_time_hour
        if notify_resume_ready is not None:
            user.notification_settings.notify_resume_ready = notify_resume_ready

        user.updated_at = datetime.utcnow()
        user.save()

        return user

    @staticmethod
    def complete_onboarding(user: User) -> User:
        """Mark onboarding as completed and trigger initial matching."""

        if user.onboarding_completed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Onboarding already completed"
            )

        # Validate required fields
        if not user.profile.full_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Full name is required"
            )

        if not user.preferences.desired_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one desired role is required"
            )

        user.onboarding_completed = True
        user.updated_at = datetime.utcnow()
        user.save()

        # TODO: Trigger initial matching for user
        # This will be implemented in the matching service

        return user

    @staticmethod
    def get_credit_balance(user: User) -> dict:
        """Get user's credit balance and history."""
        return {
            "credits": user.credits,
            "total_credits_purchased": user.total_credits_purchased
        }

    @staticmethod
    def deduct_credit(user: User, amount: int = 1) -> User:
        """Deduct credits from user account (atomic operation)."""

        if user.credits < amount:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Insufficient credits"
            )

        # Atomic decrement
        user.credits -= amount
        user.save()

        return user

    @staticmethod
    def add_credits(user: User, amount: int) -> User:
        """Add credits to user account."""
        user.credits += amount
        user.total_credits_purchased += amount
        user.updated_at = datetime.utcnow()
        user.save()

        return user
