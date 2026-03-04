"""Authentication request/response models."""

from pydantic import BaseModel, EmailStr
from typing import Optional


class RegisterRequest(BaseModel):
    """Request model for user registration."""
    email: EmailStr
    password: str
    full_name: str
    location: str


class LoginRequest(BaseModel):
    """Request model for user login."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Response model for authentication tokens."""
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    """Response model for user information."""
    id: str
    email: str
    full_name: str
    location: str
    credits: int
    onboarding_completed: bool
    is_active: bool
