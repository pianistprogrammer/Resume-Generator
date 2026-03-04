# Docker Deployment Guide

This guide explains how to deploy JobAlert AI using Docker Compose on your server.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose v2.0+
- At least 2GB RAM (4GB recommended)
- 10GB free disk space
- **External MongoDB instance** (MongoDB Atlas or your own server)

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/pianistprogrammer/Resume-Generator.git
cd Resume-Generator
```

### 2. Configure Environment Variables

#### Set up Backend environment:
```bash
cd backend
cp .env.example .env
nano .env  # Add all API keys and secrets
```

**Required backend environment variables:**
- `MONGODB_URL` - **Your MongoDB connection string** (Atlas or external server)
- `SECRET_KEY` - JWT secret
- `ANTHROPIC_API_KEY` - Claude AI API key
- `S3_ACCESS_KEY_ID` - S3/MinIO access key
- `S3_SECRET_ACCESS_KEY` - S3/MinIO secret
- `S3_ENDPOINT_URL` - S3/MinIO endpoint
- `SMTP_*` - Email configuration
- `CELERY_BROKER_URL` - Will be set to `redis://redis:6379/0` automatically
- `CELERY_RESULT_BACKEND` - Will be set to `redis://redis:6379/0` automatically

**Example MongoDB URLs:**
```env
# MongoDB Atlas
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/jobalert?retryWrites=true&w=majority

# Self-hosted MongoDB
MONGODB_URL=mongodb://username:password@your-server:27017/jobalert?authSource=admin

# Local MongoDB (if running on host)
MONGODB_URL=mongodb://host.docker.internal:27017/jobalert
```

### 3. Start All Services

```bash
docker-compose up -d
```

This will start:
- Redis (port 6379) - Celery broker
- FastAPI Backend (port 8000)
- Celery Worker - Background job processing
- Celery Beat Scheduler - Periodic tasks
- Nuxt.js Frontend (port 3000)

**Note:** MongoDB is NOT included - you must provide your own MongoDB instance via `MONGODB_URL` in `backend/.env`

### 4. Initialize the Database

#### Create admin user:
```bash
docker-compose exec backend python scripts/init_admin.py
```

#### Populate RSS feeds:
```bash
docker-compose exec backend python scripts/populate_feeds.py
```

### 5. Verify Services

Check all services are running:
```bash
docker-compose ps
```

View logs:
```bash
docker-compose logs -f backend
docker-compose logs -f celery-worker
docker-compose logs -f celery-beat
```

Test the API:
```bash
curl http://localhost:8000/api/health
```

Access the frontend:
```bash
open http://localhost:3000
```

## Production Deployment

### Using Docker Compose (Recommended)

1. **Update Frontend Dockerfile for Production:**

   Edit `frontend/Dockerfile`:
   ```dockerfile
   # Uncomment the build line
   RUN npm run build

   # Change CMD to:
   CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0"]
   ```

2. **Update Backend for Production:**

   Edit `docker-compose.yml` backend service:
   ```yaml
   command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

3. **Add Nginx Reverse Proxy:**

   Create `docker-compose.prod.yml`:
   ```yaml
   version: '3.8'

   services:
     nginx:
       image: nginx:alpine
       ports:
         - "80:80"
         - "443:443"
       volumes:
         - ./nginx.conf:/etc/nginx/nginx.conf:ro
         - ./ssl:/etc/nginx/ssl:ro
       depends_on:
         - backend
         - frontend
       networks:
         - jobalert-network
   ```

4. **Deploy:**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

### Using Individual Containers

Build and push images:
```bash
# Backend
docker build -t jobalert-backend:latest ./backend
docker push your-registry/jobalert-backend:latest

# Frontend
docker build -t jobalert-frontend:latest ./frontend
docker push your-registry/jobalert-frontend:latest
```

## Service Management

### Start/Stop Services

```bash
# Start all
docker-compose up -d

# Stop all
docker-compose down

# Restart a service
docker-compose restart backend

# View logs
docker-compose logs -f celery-worker
```

### Scale Workers

```bash
docker-compose up -d --scale celery-worker=4
```

### Database Backup

```bash
# For MongoDB Atlas, use Atlas backup features
# For self-hosted MongoDB:
mongodump --uri="your-mongodb-url" --out=./backup-$(date +%Y%m%d)
```

### Update Application

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Monitoring

### Health Checks

All services have health checks:
```bash
docker-compose ps
```

### Resource Usage

```bash
docker stats
```

### Application Logs

```bash
# All logs
docker-compose logs --tail=100

# Specific service
docker-compose logs -f backend

# Celery worker logs
docker-compose logs -f celery-worker

# Beat scheduler logs
docker-compose logs -f celery-beat
```

## Troubleshooting

### Services Won't Start

1. Check logs:
   ```bash
   docker-compose logs backend
   ```

2. Verify environment variables:
   ```bash
   docker-compose config
   ```

3. Check disk space:
   ```bash
   docker system df
   ```

### Database Connection Issues

```bash
# Test MongoDB connection from backend container
docker-compose exec backend python -c "from app.database import connect_to_mongo; connect_to_mongo(); print('Connected!')"

# Check MongoDB URL in environment
docker-compose exec backend env | grep MONGODB_URL

# If using MongoDB Atlas, ensure:
# 1. IP whitelist includes your server IP (or 0.0.0.0/0 for testing)
# 2. Database user has correct permissions
# 3. Connection string is correct
```

### Celery Not Processing Tasks

```bash
# Check Redis connection
docker-compose exec redis redis-cli ping

# Restart workers
docker-compose restart celery-worker celery-beat

# View worker logs
docker-compose logs -f celery-worker
```

### Feed Ingestion Not Working

```bash
# Manually trigger feed ingestion
docker-compose exec backend python -c "
from celery import Celery
celery_app = Celery('jobalert', broker='redis://redis:6379/0')
celery_app.send_task('app.workers.celery_worker.ingest_all_feeds_task')
"

# Check beat schedule
docker-compose logs celery-beat | grep schedule
```

## Scaling for Production

### High Availability Setup

1. **MongoDB:**
   - Use MongoDB Atlas (recommended) with automatic failover
   - Or set up MongoDB replica set on your infrastructure
   - Update `MONGODB_URL` with replica set connection string

2. **Redis Sentinel:**
   - Set up Redis Sentinel for failover
   - Update `CELERY_BROKER_URL`

3. **Multiple Workers:**
   ```yaml
   celery-worker:
     deploy:
       replicas: 4
   ```

4. **Load Balancer:**
   - Use Nginx or cloud load balancer
   - Distribute traffic across multiple backend instances

### Resource Recommendations

**Minimum (Development):**
- 2 CPU cores
- 2GB RAM
- 10GB storage

**Production (Small):**
- 4 CPU cores
- 4GB RAM
- 20GB storage

**Production (Medium):**
- 8 CPU cores
- 8GB RAM
- 50GB storage

**Note:** MongoDB resources not included - provision separately

## Security Best Practices

1. **Use secrets management:**
   ```bash
   docker secret create mongodb_password /path/to/password
   ```

2. **Enable SSL/TLS:**
   - Use Let's Encrypt for HTTPS
   - Configure SSL in Nginx

3. **Restrict network access:**
   - Use firewall rules
   - Limit MongoDB/Redis to internal network only

4. **Regular updates:**
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

5. **Backup strategy:**
   - MongoDB Atlas automated backups (recommended)
   - Or manual MongoDB backups for self-hosted
   - Backup S3/MinIO storage
   - Store backups offsite

## Environment Variables Reference

### Backend (backend/.env)

See `backend/.env.example` for full list.

**Critical variables:**
- `MONGODB_URL` - **Your MongoDB connection string** (required!)
- `SECRET_KEY` - Application secret
- `CELERY_BROKER_URL` - Redis URL (auto-set to redis://redis:6379/0)
- `CELERY_RESULT_BACKEND` - Redis backend (auto-set to redis://redis:6379/0)
- `ANTHROPIC_API_KEY` - Claude AI key
- `S3_*` - Storage configuration
- `SMTP_*` - Email configuration

### Frontend (set in docker-compose.yml)

- `API_BASE_URL` - Backend API URL (internal)
- `NUXT_PUBLIC_API_BASE` - Public API URL (external)

## Support

For issues and questions:
- GitHub Issues: https://github.com/pianistprogrammer/Resume-Generator/issues
- Documentation: See README.md and ARCHITECTURE.md

## License

See LICENSE file in the repository.
