"""Profile request/response models."""

from pydantic import BaseModel, EmailStr
from typing import Optional, List


class UpdateProfileRequest(BaseModel):
    """Request model for updating user profile."""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    current_title: Optional[str] = None
    years_of_experience: Optional[int] = None
    skills: Optional[List[str]] = None
    work_experience: Optional[List[dict]] = None
    education: Optional[List[dict]] = None
    certifications: Optional[List[dict]] = None
    summary: Optional[str] = None


class UpdatePreferencesRequest(BaseModel):
    """Request model for updating job preferences."""
    desired_roles: Optional[List[str]] = None
    desired_locations: Optional[List[str]] = None
    remote_preference: Optional[str] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    experience_levels: Optional[List[str]] = None
    required_keywords: Optional[List[str]] = None
    exclude_keywords: Optional[List[str]] = None
    exclude_companies: Optional[List[str]] = None


class UpdateNotificationSettingsRequest(BaseModel):
    """Request model for updating notification settings."""
    email_enabled: Optional[bool] = None
    frequency: Optional[str] = None
    min_score_threshold: Optional[float] = None
    digest_time_hour: Optional[int] = None
    notify_resume_ready: Optional[bool] = None


class ProfileResponse(BaseModel):
    """Response model for user profile."""
    id: str
    email: str
    profile: dict
    preferences: dict
    notification_settings: dict
    credits: int
    onboarding_completed: bool


class CreditBalanceResponse(BaseModel):
    """Response model for credit balance."""
    credits: int
    total_credits_purchased: int
