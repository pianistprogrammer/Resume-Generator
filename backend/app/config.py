"""Application configuration management using pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pathlib import Path


# Check for .env file in project root first, then fall back to local .env
# This allows running from backend/ directory or project root
def get_env_file() -> str:
    """Get the path to the .env file, checking root first, then local directory."""
    root_env = Path(__file__).parent.parent.parent / ".env"
    local_env = Path(__file__).parent.parent / ".env"
    
    # Prefer root .env for consistency with Docker setup
    if root_env.exists():
        return str(root_env)
    elif local_env.exists():
        return str(local_env)
    else:
        # Return root path even if it doesn't exist - pydantic will handle gracefully
        return str(root_env)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=get_env_file(),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    app_name: str = "JobAlert AI"
    environment: str = "development"
    debug: bool = True
    api_prefix: str = "/api"

    # Security
    secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours

    # Admin Credentials
    admin_email: str = ""
    admin_password: str = ""

    # Database
    mongodb_url: str
    mongodb_db_name: str = "jobalert"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Celery
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"

    # Anthropic Claude API
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"
    anthropic_max_tokens: int = 4096

    # LLM Provider
    llm_provider: str = "anthropic"  # anthropic, openai, openrouter, lmstudio, ollama

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4-turbo-preview"
    openai_max_tokens: int = 4096

    # OpenRouter
    openrouter_api_key: str = ""
    openrouter_model: str = "anthropic/claude-3.5-sonnet"
    openrouter_max_tokens: int = 4096

    # LMStudio
    lmstudio_base_url: str = "http://localhost:1234/v1"
    lmstudio_model: str = "local-model"
    lmstudio_max_tokens: int = 4096

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama2"
    ollama_max_tokens: int = 4096

    # SMTP Email Configuration
    email_host: str = "mail.marriageministries.pl"
    email_port: int = 465
    email_user: str = "noreply@marriageministries.pl"
    email_pass: str
    email_from_name: str = "JobAlert AI"
    email_use_tls: bool = False  # For port 465, we use SSL
    email_use_ssl: bool = True   # SSL for port 465

    # SendGrid (deprecated - using SMTP instead)
    sendgrid_api_key: str = ""
    sendgrid_from_email: str = ""
    sendgrid_from_name: str = "JobAlert AI"

    # Stripe
    stripe_api_key: str
    stripe_publishable_key: str
    stripe_webhook_secret: str
    stripe_price_single: str  # Price ID for single credit
    stripe_price_5pack: str   # Price ID for 5-pack
    stripe_price_unlimited: str  # Price ID for unlimited plan

    # S3-Compatible Storage (MinIO/S3)
    s3_bucket_name: str = "resumes"
    s3_endpoint_url: str = "https://s3.primeeralabs.com"
    s3_access_key_id: str
    s3_secret_access_key: str
    s3_region: str = "us-east-1"
    s3_public_url: str = "https://s3.primeeralabs.com"  # Public URL base for PDF access

    # Cloudflare R2 (deprecated - using S3 instead)
    r2_endpoint_url: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket_name: str = ""
    r2_public_url: str = ""

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Features
    free_credits: int = 3
    min_match_score: float = 60.0

    # Email Settings
    digest_hour: int = 18  # 6 PM for daily digests

    # Job Ingestion
    feed_refresh_minutes: int = 30
    max_jobs_per_feed: int = 100


# Global settings instance
settings = Settings()
