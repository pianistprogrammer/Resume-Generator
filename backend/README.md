# JobAlert AI - Backend

FastAPI backend for JobAlert AI job matching platform.

## Setup

### Prerequisites
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (fast Python package installer)
- MongoDB
- Redis
- Docker (optional but recommended)

### Installing uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip
pip install uv
```

### Environment Variables

Copy `.env.example` to `.env` (already created with secure secret key):

```bash
# .env is already created with a secure SECRET_KEY
# Update the following keys:
# - ANTHROPIC_API_KEY
# - SENDGRID_API_KEY
# - STRIPE_API_KEY
# - R2_ACCESS_KEY_ID
# - R2_SECRET_ACCESS_KEY
```

### Installation

#### Option 1: Docker Compose (Recommended)

```bash
docker-compose up -d
```

This starts:
- FastAPI application (port 8000)
- MongoDB (port 27017)
- Redis (port 6379)
- Celery worker
- Celery beat scheduler

#### Option 2: Local Development with uv

1. Install dependencies:
```bash
# Using uv (recommended - much faster than pip)
uv sync

# This reads pyproject.toml and installs all dependencies
# Creates a virtual environment automatically in .venv/
```

2. Start MongoDB and Redis locally

3. Run the FastAPI application:
```bash
# Activate the virtual environment
source .venv/bin/activate  # macOS/Linux
# Or on Windows: .venv\Scripts\activate

# Run the app
uvicorn main:app --reload

# Or run directly with uv
uv run uvicorn main:app --reload
```

4. Run Celery worker (in separate terminal):
```bash
uv run celery -A app.workers.celery_worker worker --loglevel=info
```

5. Run Celery beat (in separate terminal):
```bash
uv run celery -A app.workers.celery_worker beat --loglevel=info
```

## Project Structure

```
backend/
├── main.py                   # FastAPI app entry point (NEW LOCATION)
├── pyproject.toml           # uv dependencies & project config
├── uv.lock                  # Locked dependencies (auto-generated)
├── .venv/                   # Virtual environment (auto-created)
├── .env                     # Environment variables (created with real secret)
├── app/
│   ├── config.py            # Settings
│   ├── database.py          # MongoDB connection
│   ├── models.py            # Data models
│   ├── routes.py            # Route registration
│   ├── controllers/         # API endpoints
│   ├── services/            # Business logic
│   └── workers/             # Celery tasks
├── Dockerfile
└── docker-compose.yml
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

## Architecture

### 4-Layer Pattern
- **Route** → **Controller** → **Service** → **Model**

### Key Services
- `auth_service.py` - User authentication and JWT
- `profile_service.py` - User profile management
- `job_service.py` - Job operations
- `matching_service.py` - Weighted scoring algorithm
- `resume_service.py` - AI resume generation with Claude
- `xml_feed_service.py` - RSS/XML feed ingestion
- `url_parser_service.py` - User-submitted URL parsing

### Background Tasks (Celery)
- Feed ingestion every 30 minutes
- Daily digest emails at 6 PM
- Hourly matching runs
- On-demand resume generation
- On-demand URL ingestion

## Database Schema

See `app/models.py` for complete schema. Key collections:
- `users` - User accounts with embedded profile, preferences, notifications
- `jobs` - Job postings with fingerprint deduplication
- `matches` - Scored user-job matches
- `resumes` - AI-generated tailored resumes
- `notifications` - Email tracking
- `payments` - Stripe payment records

## Testing

```bash
# Run health check
curl http://localhost:8000/health

# Register a user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","full_name":"Test User","location":"San Francisco"}'
```

## Development with uv

### Why uv?
- **10-100x faster** than pip
- Better dependency resolution
- Built in Rust
- Automatic virtual environment management
- Project-based workflows

### Common Commands

```bash
# Install dependencies from pyproject.toml
uv sync

# Add a new package
uv add package-name

# Add a dev dependency
uv add --dev pytest

# Remove a package
uv remove package-name

# Run a command in the uv environment
uv run uvicorn main:app --reload

# Update all dependencies
uv sync --upgrade

# Lock dependencies
uv lock
```

### Project Structure with uv

```
backend/
├── pyproject.toml       # Project metadata & dependencies
├── uv.lock             # Locked dependency versions (auto-generated)
├── .venv/              # Virtual environment (auto-created by uv sync)
└── ...
```

## Deployment

Recommended stack:
- **API + Workers**: Railway
- **MongoDB**: MongoDB Atlas
- **Redis**: Railway or Upstash
- **Storage**: Cloudflare R2
- **Email**: SendGrid
- **Payments**: Stripe

See `../DEPLOYMENT.md` for detailed deployment guide.
