"""Authentication controller with FastAPI endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
import asyncio
from functools import partial

from app.services.auth_service import AuthService
from app.services.email_service import EmailService
from app.schemas import User
from app.models.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserResponse,
)
from app.models import ApiResponse
from app.middlewares import get_current_user


# Router
router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=ApiResponse[TokenResponse], status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, background_tasks: BackgroundTasks):
    """Register a new user account."""
    # Run registration in thread pool (blocking MongoDB call)
    loop = asyncio.get_event_loop()
    user = await loop.run_in_executor(
        None,
        partial(
            AuthService.register_user,
            request.email,
            request.password,
            request.full_name,
            request.location
        )
    )

    # Generate access token
    access_token = AuthService.create_access_token(data={"sub": str(user.id)})

    # Send welcome email in background
    background_tasks.add_task(
        EmailService.send_welcome_email,
        user.email,
        user.profile.full_name
    )

    token_data = {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.profile.full_name,
            "location": user.profile.location,
            "credits": user.credits,
            "onboarding_completed": user.onboarding_completed,
            "role": user.role
        }
    }

    return ApiResponse[TokenResponse](
        success=True,
        msg="User registered successfully",
        data=token_data
    )


@router.post("/login", response_model=ApiResponse[TokenResponse])
async def login(request: LoginRequest):
    """Login with email and password."""
    # Run authentication in thread pool
    loop = asyncio.get_event_loop()
    user = await loop.run_in_executor(
        None,
        partial(AuthService.authenticate_user, request.email, request.password)
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate access token
    access_token = AuthService.create_access_token(data={"sub": str(user.id)})

    token_data = {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.profile.full_name,
            "location": user.profile.location,
            "credits": user.credits,
            "onboarding_completed": user.onboarding_completed,
            "role": user.role
        }
    }

    return ApiResponse[TokenResponse](
        success=True,
        msg="Login successful",
        data=token_data
    )


@router.get("/me", response_model=ApiResponse[UserResponse])
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    user_data = {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.profile.full_name,
        "location": current_user.profile.location,
        "credits": current_user.credits,
        "onboarding_completed": current_user.onboarding_completed,
        "is_active": current_user.is_active,
        "role": current_user.role
    }

    return ApiResponse[UserResponse](
        success=True,
        msg="User information retrieved successfully",
        data=user_data
    )


@router.post("/refresh", response_model=ApiResponse[TokenResponse])
async def refresh_token(current_user: User = Depends(get_current_user)):
    """Refresh access token."""
    access_token = AuthService.create_access_token(data={"sub": str(current_user.id)})

    token_data = {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(current_user.id),
            "email": current_user.email,
            "full_name": current_user.profile.full_name,
            "location": current_user.profile.location,
            "credits": current_user.credits,
            "onboarding_completed": current_user.onboarding_completed,
            "role": current_user.role
        }
    }

    return ApiResponse[TokenResponse](
        success=True,
        msg="Token refreshed successfully",
        data=token_data
    )
