"""Admin authentication middleware."""

from fastapi import HTTPException, Depends, status
from app.middlewares.auth_middleware import get_current_user
from app.schemas.user import User


async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to verify the current user is an admin."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user
