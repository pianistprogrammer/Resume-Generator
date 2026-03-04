# Environment Variables Configuration

## Overview

This project uses a **centralized `.env` file** located in the **project root directory** that is shared between both the frontend and backend services. This ensures consistency and simplifies configuration management, especially for Docker deployments.

## Directory Structure

```
Resume-Generator/
├── .env                    # ← Main environment file (create from .env.example)
├── .env.example            # ← Template with all required variables
├── docker-compose.yml      # Uses root .env file
├── backend/
│   ├── .env (deprecated)   # No longer needed - use root .env
│   └── app/
└── frontend/
    └── app/
```

## Setup Instructions

### 1. Create Your Environment File

Copy the example file to create your actual `.env`:

```bash
cp .env.example .env
```

### 2. Configure Your Variables

Edit `.env` and fill in your actual values:

```bash
# Required for development
MONGODB_URL=mongodb://localhost:27017
ANTHROPIC_API_KEY=sk-ant-your-actual-key
SECRET_KEY=generate-a-secure-random-key

# Admin credentials
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=YourSecurePassword123!

# Configure other services as needed
```

### 3. Local Development

Both services will look for the `.env` file in the project root:

**Backend (FastAPI):**
- The backend config (`backend/app/config.py`) loads from root `.env`
- Falls back to `backend/.env` for backward compatibility

**Frontend (Nuxt):**
- Reads `NUXT_PUBLIC_API_BASE` from root `.env`
- No frontend-specific `.env` file needed

Start services:
```bash
# Backend
cd backend
python -m uvicorn app.main:app --reload

# Frontend (in another terminal)
cd frontend
npm run dev
```

### 4. Docker Deployment

The `docker-compose.yml` is configured to use the root `.env` file:

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Environment Variables Reference

### Application Core
- `APP_NAME` - Application name
- `ENVIRONMENT` - development/staging/production
- `DEBUG` - true/false
- `SECRET_KEY` - JWT secret (generate securely)

### Admin
- `ADMIN_EMAIL` - Initial admin email
- `ADMIN_PASSWORD` - Initial admin password

### Database
- `MONGODB_URL` - MongoDB connection string
- `MONGODB_DB_NAME` - Database name

### Redis & Celery
- `REDIS_URL` - Redis connection URL
- `CELERY_BROKER_URL` - Celery broker (usually Redis)
- `CELERY_RESULT_BACKEND` - Results backend

### LLM Services
- `LLM_PROVIDER` - anthropic/openai/openrouter/lmstudio/ollama
- `ANTHROPIC_API_KEY` - Claude API key
- `OPENAI_API_KEY` - OpenAI API key
- `ANTHROPIC_MODEL` - Model name
- `ANTHROPIC_MAX_TOKENS` - Max tokens per request

### Email (SendGrid)
- `SENDGRID_API_KEY` - SendGrid API key
- `SENDGRID_FROM_EMAIL` - From email address
- `SENDGRID_FROM_NAME` - From name

### Payment (Stripe)
- `STRIPE_API_KEY` - Stripe secret key
- `STRIPE_PUBLISHABLE_KEY` - Stripe public key
- `STRIPE_WEBHOOK_SECRET` - Webhook secret
- `STRIPE_PRICE_*` - Product price IDs

### Storage (Cloudflare R2)
- `R2_ENDPOINT_URL` - R2 endpoint
- `R2_ACCESS_KEY_ID` - Access key
- `R2_SECRET_ACCESS_KEY` - Secret key
- `R2_BUCKET_NAME` - Bucket name
- `R2_PUBLIC_URL` - Public CDN URL

### Frontend
- `API_BASE_URL` - Backend API URL (for Docker internal)
- `NUXT_PUBLIC_API_BASE` - Public API URL (for browser)

### CORS
- `CORS_ORIGINS` - JSON array of allowed origins

### Features
- `FREE_CREDITS` - Free credits for new users
- `MIN_MATCH_SCORE` - Minimum match score threshold
- `DIGEST_HOUR` - Hour for daily digest (0-23)
- `FEED_REFRESH_MINUTES` - Feed refresh interval
- `MAX_JOBS_PER_FEED` - Max jobs per scrape

## Migration from Old Setup

If you have existing `.env` files in `backend/.env`:

1. **Copy values to root `.env`:**
   ```bash
   cp backend/.env ./.env
   ```

2. **Verify the configuration:**
   ```bash
   # Test backend can load config
   cd backend
   python -c "from app.config import settings; print(settings.app_name)"
   ```

3. **Optional: Remove old files**
   ```bash
   # After verifying everything works
   rm backend/.env
   ```

## Security Best Practices

1. **Never commit `.env` files** - They're in `.gitignore`
2. **Use strong secrets** - Generate with `openssl rand -hex 32`
3. **Rotate keys regularly** - Especially API keys
4. **Different environments** - Use separate `.env` files for dev/staging/prod
5. **Docker secrets** - For production, consider Docker secrets or external secret management

## Troubleshooting

### Backend can't find .env
- Ensure `.env` exists in project root
- Check file permissions: `chmod 644 .env`
- Verify no typos in variable names

### Frontend can't connect to API
- Check `NUXT_PUBLIC_API_BASE` in `.env`
- Verify backend is running on correct port
- Check CORS settings if cross-origin

### Docker services failing
- Run `docker-compose config` to validate
- Check logs: `docker-compose logs backend`
- Ensure `.env` is in same directory as `docker-compose.yml`

## Additional Resources

- [FastAPI Settings Management](https://fastapi.tiangolo.com/advanced/settings/)
- [Nuxt Environment Variables](https://nuxt.com/docs/guide/going-further/runtime-config)
- [Docker Compose Environment Files](https://docs.docker.com/compose/environment-variables/)
