"""Database connection and initialization for MongoDB with MongoEngine."""

from mongoengine import connect, disconnect
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.config import settings


def connect_to_mongo():
    """Connect to MongoDB using MongoEngine."""
    connect(
        db=settings.mongodb_db_name,
        host=settings.mongodb_url,
        alias='default'
    )
    print(f"Connected to MongoDB: {settings.mongodb_db_name}")


def close_mongo_connection():
    """Close MongoDB connection."""
    disconnect(alias='default')
    print("Closed MongoDB connection")


def initialize_admin_user():
    """Initialize admin user if it doesn't exist."""
    try:
        from app.schemas.user import User, UserProfile
        from app.services.auth_service import AuthService
        
        admin_email = settings.admin_email
        admin_password = settings.admin_password

        if not admin_email or not admin_password:
            print("⚠️  ADMIN_EMAIL and ADMIN_PASSWORD not set, skipping admin creation")
            return

        # Check if admin already exists
        existing_admin = User.objects(email=admin_email).first()
        if existing_admin:
            # Ensure role is set to admin
            if existing_admin.role != "admin":
                existing_admin.role = "admin"
                existing_admin.save()
                print(f"✅ Updated admin role for: {admin_email}")
            else:
                print(f"✅ Admin user already exists: {admin_email}")
            return

        # Create admin user
        hashed_password = AuthService.get_password_hash(admin_password)

        admin_user = User(
            email=admin_email,
            hashed_password=hashed_password,
            profile=UserProfile(
                full_name="Admin User",
                email=admin_email,
                location="Global"
            ),
            role="admin",
            is_active=True,
            onboarding_completed=True,
            credits=999999  # Unlimited credits for admin
        )
        admin_user.save()

        print(f"✅ Created admin user: {admin_email}")
    except Exception as e:
        print(f"❌ Failed to initialize admin user: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context manager for database connection."""
    # Startup
    connect_to_mongo()
    initialize_admin_user()
    yield
    # Shutdown
    close_mongo_connection()


def get_database():
    """Get the database instance (not used with MongoEngine, kept for compatibility)."""
    return None
