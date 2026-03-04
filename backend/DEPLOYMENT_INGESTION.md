# Job Ingestion - Deployment Guide

JobAlert AI supports **two approaches** for running background job ingestion:

1. **Celery + Redis** (Production, distributed)
2. **Simple Poller Loop** (Lightweight, single-server)

Choose the approach that best fits your deployment requirements.

---

## 🎯 Approach Comparison

| Feature | Celery + Redis | Simple Poller Loop |
|---------|----------------|-------------------|
| **Best for** | Production, scalable deployments | Development, single-server, VPS |
| **Dependencies** | Redis server required | No additional services |
| **Scalability** | Horizontal (multiple workers) | Vertical (single process) |
| **Monitoring** | Flower dashboard available | Log file monitoring |
| **Task Queue** | Full queue with retries, priorities | Simple sequential execution |
| **Resource Usage** | Higher (Redis + workers) | Lower (single Python process) |
| **Setup Complexity** | Moderate | Simple |

---

## 📋 RSS Feed Sources

Both approaches use the same feed registry in `app/services/ingestion/xml_feed_service.py`:

```python
FEEDS = {
    "remoteok": "https://remoteok.com/remote-dev-jobs.rss",
    "weworkremotely": "https://weworkremotely.com/remote-jobs.rss",
    "himalayas": "https://himalayas.app/jobs/rss",
    "realworkfromanywhere": "https://www.realworkfromanywhere.com/rss.xml",
    "rssapp_custom": "https://rss.app/feeds/0bUVsJgEz3RTTsKm.xml",
}
```

To add more feeds, simply update the `FEEDS` dictionary.

---

## 🚀 Approach 1: Celery + Redis (Production)

### Requirements
- Redis server running
- Celery installed (included in dependencies)

### Setup

1. **Install dependencies:**
```bash
uv sync
```

2. **Configure Redis in `.env`:**
```bash
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

3. **Start Redis:**
```bash
# macOS (via Homebrew)
brew services start redis

# Linux
sudo systemctl start redis

# Docker
docker run -d -p 6379:6379 redis:alpine
```

4. **Start Celery Worker:**
```bash
cd backend
uv run celery -A app.workers.celery_worker worker --loglevel=info
```

5. **Start Celery Beat (scheduler):**
```bash
uv run celery -A app.workers.celery_worker beat --loglevel=info
```

### Configuration

Edit `app/workers/celery_worker.py` to adjust schedule:

```python
app.conf.beat_schedule = {
    'ingest-feeds-every-30min': {
        'task': 'app.workers.celery_worker.ingest_all_feeds',
        'schedule': 1800.0,  # 30 minutes in seconds
    },
}
```

### Monitoring

Install Flower for web-based monitoring:
```bash
pip install flower
celery -A app.workers.celery_worker flower
```

Visit http://localhost:5555 for the dashboard.

### Production Deployment

Use Supervisor or systemd to manage processes:

**systemd example (`/etc/systemd/system/celery-worker.service`):**
```ini
[Unit]
Description=Celery Worker for JobAlert AI
After=network.target redis.service

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/opt/jobalert/backend
ExecStart=/opt/jobalert/backend/.venv/bin/celery -A app.workers.celery_worker worker --detach
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## 🔄 Approach 2: Simple Poller Loop (Lightweight)

### Requirements
- No additional services needed
- Python 3.12+

### Setup

1. **Install dependencies:**
```bash
uv sync
```

2. **Test single run:**
```bash
cd backend
python simple_poller.py --once
```

Expected output:
```
[2024-03-03T23:30:00] Initializing database connection...
[2024-03-03T23:30:01] Database connected
[2024-03-03T23:30:01] Starting feed ingestion...
[2024-03-03T23:30:15] Ingestion complete: 12 new jobs
  - weworkremotely: 5 jobs
  - himalayas: 4 jobs
  - remoteok: 3 jobs
[2024-03-03T23:30:15] Done
```

### Running Continuously

**Option A: Direct Python (foreground):**
```bash
python simple_poller.py --interval 1800  # Poll every 30 minutes
```

**Option B: Bash loop with nohup (background):**
```bash
nohup ./exec_loop.sh > loop.log 2>&1 &
```

**Option C: Python in background:**
```bash
nohup python simple_poller.py --interval 1800 > poller.log 2>&1 &
```

### Configuration

Adjust polling interval via CLI:
```bash
# Poll every 60 seconds
python simple_poller.py --interval 60

# Poll every hour
python simple_poller.py --interval 3600
```

Or edit `exec_loop.sh`:
```bash
INTERVAL=1800  # 30 minutes
MAX_RETRIES=3
RETRY_DELAY=60
```

### Monitoring

**View logs in real-time:**
```bash
tail -f loop.log
# or
tail -f poller.log
```

**Check if running:**
```bash
ps aux | grep simple_poller
# or
ps aux | grep exec_loop
```

**Stop background process:**
```bash
pkill -f simple_poller.py
# or
pkill -f exec_loop.sh
```

### Production Deployment (VPS)

1. **SSH into your server:**
```bash
ssh user@your-vps-ip
```

2. **Clone repository:**
```bash
cd /opt
git clone https://github.com/yourusername/jobalert-ai.git
cd jobalert-ai/backend
```

3. **Install dependencies:**
```bash
uv sync
```

4. **Start the loop:**
```bash
nohup ./exec_loop.sh > /var/log/jobalert-loop.log 2>&1 &
```

5. **Verify it's running:**
```bash
ps aux | grep exec_loop
tail -f /var/log/jobalert-loop.log
```

6. **Auto-start on reboot** (via crontab):
```bash
crontab -e
```

Add this line:
```cron
@reboot cd /opt/jobalert-ai/backend && nohup ./exec_loop.sh > /var/log/jobalert-loop.log 2>&1 &
```

---

## 🔧 Troubleshooting

### Celery Approach

**Issue: Celery can't connect to Redis**
```bash
# Check Redis is running
redis-cli ping
# Should return: PONG

# Check Redis URL in .env
echo $REDIS_URL
```

**Issue: Tasks not executing**
```bash
# Check Beat scheduler is running
ps aux | grep "celery.*beat"

# Check worker is running
ps aux | grep "celery.*worker"
```

### Simple Poller Approach

**Issue: "ModuleNotFoundError"**
```bash
# Ensure you're using uv run
uv run python simple_poller.py --once

# Or activate venv first
source .venv/bin/activate
python simple_poller.py --once
```

**Issue: Process stops unexpectedly**
```bash
# Check logs for errors
tail -50 loop.log

# Restart with nohup
pkill -f simple_poller
nohup python simple_poller.py --interval 1800 > poller.log 2>&1 &
```

**Issue: Database connection errors**
```bash
# Verify MongoDB is running
mongosh --eval "db.adminCommand('ping')"

# Check MONGODB_URL in .env
cat .env | grep MONGODB_URL
```

---

## 📊 Comparison: When to Use Each

### Use Celery + Redis when:
- ✅ Running on cloud platforms (Railway, Render, AWS)
- ✅ Need horizontal scaling (multiple workers)
- ✅ Require complex task orchestration
- ✅ Want built-in monitoring and retries
- ✅ Processing high volumes of jobs

### Use Simple Poller when:
- ✅ Running on a single VPS (DigitalOcean, Hostinger, Linode)
- ✅ Want minimal dependencies
- ✅ Don't need Redis infrastructure
- ✅ Prefer simpler debugging (just logs)
- ✅ Processing moderate job volumes
- ✅ Following the job_market_intelligence_bot pattern

---

## 🎯 Recommended Setup

**Development:**
```bash
# Simple approach - just one terminal
python simple_poller.py --interval 60
```

**Production (Small VPS):**
```bash
# Simple approach with auto-restart
nohup ./exec_loop.sh > /var/log/jobalert-loop.log 2>&1 &
```

**Production (Cloud Platform):**
```bash
# Celery approach with managed Redis
celery -A app.workers.celery_worker worker -B --loglevel=info
```

---

## 📝 Next Steps

After setting up job ingestion:

1. Configure email notifications (`app/services/notification_service.py`)
2. Set up daily digest schedule
3. Test end-to-end flow: Feed → Job → Match → Resume → Email
4. Monitor logs for errors
5. Adjust polling intervals based on feed freshness

For questions or issues, check the logs first:
- Celery: Check worker and beat logs
- Simple poller: `tail -f loop.log` or `tail -f poller.log`
