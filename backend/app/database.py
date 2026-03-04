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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context manager for database connection."""
    # Startup
    connect_to_mongo()
    yield
    # Shutdown
    close_mongo_connection()


def get_database():
    """Get the database instance (not used with MongoEngine, kept for compatibility)."""
    return None
