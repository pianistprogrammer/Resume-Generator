"""Authentication service for user registration, login, and JWT token management."""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import HTTPException, status

from app.config import settings
from app.schemas import User, UserProfile, JobPreferences, NotificationSettings


class AuthService:
    """Authentication service for user management."""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)

        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> dict:
        """Decode and validate a JWT token."""
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    @staticmethod
    def register_user(email: str, password: str, full_name: str, location: str) -> User:
        """Register a new user account."""
        # Check if user already exists
        existing_user = User.objects(email=email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create user profile
        profile = UserProfile(
            full_name=full_name,
            email=email,
            location=location
        )

        # Create user
        user = User(
            email=email,
            hashed_password=AuthService.get_password_hash(password),
            profile=profile,
            preferences=JobPreferences(),
            notification_settings=NotificationSettings(),
            credits=settings.free_credits,
            onboarding_completed=False
        )

        user.save()
        return user

    @staticmethod
    def authenticate_user(email: str, password: str) -> Optional[User]:
        """Authenticate a user by email and password."""
        user = User.objects(email=email).first()

        if not user:
            return None

        if not AuthService.verify_password(password, user.hashed_password):
            return None

        # Update last login
        user.last_login = datetime.utcnow()
        user.save()

        return user

    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[User]:
        """Get user by ID."""
        try:
            user = User.objects(id=user_id).first()
            return user
        except Exception:
            return None

    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """Get user by email."""
        user = User.objects(email=email).first()
        return user
