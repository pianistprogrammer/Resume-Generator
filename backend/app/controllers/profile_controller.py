"""Profile controller with FastAPI endpoints."""

from fastapi import APIRouter, Depends, status
import asyncio
from functools import partial

from app.middlewares import get_current_user
from app.services.profile_service import ProfileService
from app.schemas import User
from app.models.profile import (
    UpdateProfileRequest,
    UpdatePreferencesRequest,
    UpdateNotificationSettingsRequest,
    ProfileResponse,
    CreditBalanceResponse,
)
from app.models import ApiResponse


# Router
router = APIRouter(prefix="/profile", tags=["Profile"])


def _serialize_embedded_doc(obj):
    """Convert MongoEngine embedded document to dict."""
    if hasattr(obj, 'to_mongo'):
        return obj.to_mongo().to_dict()
    return obj


@router.get("", response_model=ApiResponse[ProfileResponse])
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get current user's full profile."""
    profile_data = {
        "id": str(current_user.id),
        "email": current_user.email,
        "profile": _serialize_embedded_doc(current_user.profile),
        "preferences": _serialize_embedded_doc(current_user.preferences),
        "notification_settings": _serialize_embedded_doc(current_user.notification_settings),
        "credits": current_user.credits,
        "onboarding_completed": current_user.onboarding_completed
    }

    return ApiResponse[ProfileResponse](
        success=True,
        msg="Profile retrieved successfully",
        data=profile_data
    )


@router.put("", response_model=ApiResponse[ProfileResponse])
async def update_profile(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_user)
):
    """Update user profile information."""
    # Run in thread pool
    loop = asyncio.get_event_loop()
    user = await loop.run_in_executor(
        None,
        partial(
            ProfileService.update_profile,
            user=current_user,
            **request.model_dump(exclude_unset=True)
        )
    )

    profile_data = {
        "id": str(user.id),
        "email": user.email,
        "profile": _serialize_embedded_doc(user.profile),
        "preferences": _serialize_embedded_doc(user.preferences),
        "notification_settings": _serialize_embedded_doc(user.notification_settings),
        "credits": user.credits,
        "onboarding_completed": user.onboarding_completed
    }

    return ApiResponse[ProfileResponse](
        success=True,
        msg="Profile updated successfully",
        data=profile_data
    )


@router.put("/preferences", response_model=ApiResponse[ProfileResponse])
async def update_preferences(
    request: UpdatePreferencesRequest,
    current_user: User = Depends(get_current_user)
):
    """Update user job preferences."""
    # Run in thread pool
    loop = asyncio.get_event_loop()
    user = await loop.run_in_executor(
        None,
        partial(
            ProfileService.update_preferences,
            user=current_user,
            **request.model_dump(exclude_unset=True)
        )
    )

    profile_data = {
        "id": str(user.id),
        "email": user.email,
        "profile": _serialize_embedded_doc(user.profile),
        "preferences": _serialize_embedded_doc(user.preferences),
        "notification_settings": _serialize_embedded_doc(user.notification_settings),
        "credits": user.credits,
        "onboarding_completed": user.onboarding_completed
    }

    return ApiResponse[ProfileResponse](
        success=True,
        msg="Preferences updated successfully",
        data=profile_data
    )


@router.put("/notifications", response_model=ApiResponse[ProfileResponse])
async def update_notification_settings(
    request: UpdateNotificationSettingsRequest,
    current_user: User = Depends(get_current_user)
):
    """Update user notification settings."""
    # Run in thread pool
    loop = asyncio.get_event_loop()
    user = await loop.run_in_executor(
        None,
        partial(
            ProfileService.update_notification_settings,
            user=current_user,
            **request.model_dump(exclude_unset=True)
        )
    )

    profile_data = {
        "id": str(user.id),
        "email": user.email,
        "profile": _serialize_embedded_doc(user.profile),
        "preferences": _serialize_embedded_doc(user.preferences),
        "notification_settings": _serialize_embedded_doc(user.notification_settings),
        "credits": user.credits,
        "onboarding_completed": user.onboarding_completed
    }

    return ApiResponse[ProfileResponse](
        success=True,
        msg="Notification settings updated successfully",
        data=profile_data
    )


@router.post("/onboarding/complete", response_model=ApiResponse[ProfileResponse])
async def complete_onboarding(current_user: User = Depends(get_current_user)):
    """Mark onboarding as completed."""
    # Run in thread pool
    loop = asyncio.get_event_loop()
    user = await loop.run_in_executor(
        None,
        partial(ProfileService.complete_onboarding, user=current_user)
    )

    profile_data = {
        "id": str(user.id),
        "email": user.email,
        "profile": _serialize_embedded_doc(user.profile),
        "preferences": _serialize_embedded_doc(user.preferences),
        "notification_settings": _serialize_embedded_doc(user.notification_settings),
        "credits": user.credits,
        "onboarding_completed": user.onboarding_completed
    }

    return ApiResponse[ProfileResponse](
        success=True,
        msg="Onboarding completed successfully",
        data=profile_data
    )


@router.get("/credits", response_model=ApiResponse[CreditBalanceResponse])
async def get_credit_balance(current_user: User = Depends(get_current_user)):
    """Get user's credit balance."""
    # Run in thread pool
    loop = asyncio.get_event_loop()
    balance = await loop.run_in_executor(
        None,
        partial(ProfileService.get_credit_balance, user=current_user)
    )

    return ApiResponse[CreditBalanceResponse](
        success=True,
        msg="Credit balance retrieved successfully",
        data=balance
    )
