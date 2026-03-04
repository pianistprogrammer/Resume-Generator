"""Models package - Pydantic request/response models."""

from .auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserResponse,
)

from .profile import (
    UpdateProfileRequest,
    UpdatePreferencesRequest,
    UpdateNotificationSettingsRequest,
    ProfileResponse,
    CreditBalanceResponse,
)

from .response import (
    ApiResponse,
    ErrorResponse,
)

__all__ = [
    # Auth models
    "RegisterRequest",
    "LoginRequest",
    "TokenResponse",
    "UserResponse",
    # Profile models
    "UpdateProfileRequest",
    "UpdatePreferencesRequest",
    "UpdateNotificationSettingsRequest",
    "ProfileResponse",
    "CreditBalanceResponse",
    # Generic response models
    "ApiResponse",
    "ErrorResponse",
]
