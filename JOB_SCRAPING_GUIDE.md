# Job Scraping URLs & Configuration Guide

## Current RSS Feed URLs

The application currently scrapes jobs from the following RSS/XML feeds (configured in `backend/app/services/ingestion/xml_feed_service.py`):

### Active Feeds

1. **RemoteOK**
   - URL: `https://remoteok.com/remote-dev-jobs.rss`
   - Focus: Remote developer jobs
   - Key: `remoteok`

2. **We Work Remotely**
   - URL: `https://weworkremotely.com/remote-jobs.rss`
   - Focus: Remote jobs across categories
   - Key: `weworkremotely`

3. **Himalayas**
   - URL: `https://himalayas.app/jobs/rss`
   - Focus: Remote tech jobs
   - Key: `himalayas`

4. **Real Work From Anywhere**
   - URL: `https://www.realworkfromanywhere.com/rss.xml`
   - Focus: Remote jobs
   - Key: `realworkfromanywhere`

5. **RSS App Custom Feed**
   - URL: `https://rss.app/feeds/0bUVsJgEz3RTTsKm.xml`
   - Focus: Aggregated custom feed
   - Key: `rssapp_custom`

---

## How to Add New RSS Feed URLs

### Step 1: Edit the Feed Registry

Open: `backend/app/services/ingestion/xml_feed_service.py`

Find the `FEEDS` dictionary (around line 18) and add your new feed:

```python
FEEDS = {
    # ... existing feeds ...

    "your_feed_key": {
        "url": "https://example.com/jobs.rss",
        "name": "Your Feed Name"
    },
}
```

**Example - Adding Indeed RSS Feed:**

```python
FEEDS = {
    # ... existing feeds ...

    "indeed_tech": {
        "url": "https://www.indeed.com/rss?q=software+engineer&l=remote",
        "name": "Indeed Tech Jobs"
    },
}
```

### Step 2: Restart the Backend

```bash
# If using Docker
docker-compose restart backend

# If running locally
# Stop the server (Ctrl+C) and restart
uvicorn app.main:app --reload
```

### Step 3: Test the New Feed

The feed will be automatically scraped on the next scheduled run, or you can trigger it manually via the API.

---

## Adding Specific Company Feeds

### Greenhouse ATS Companies

For companies using Greenhouse, add them to the ingestion logic:

**File:** `backend/app/services/ingestion/xml_feed_service.py`

**Method:** `parse_greenhouse_feed(company_token: str)`

**Usage Example:**
```python
# In your worker/scheduler
jobs = await XMLFeedService.parse_greenhouse_feed("stripe")  # Stripe's token
jobs = await XMLFeedService.parse_greenhouse_feed("coinbase")
```

**How to find the company token:**
- Visit the company's careers page
- Look for URLs like: `https://boards.greenhouse.io/COMPANY_TOKEN/jobs/`
- The `COMPANY_TOKEN` is what you need

### Lever ATS Companies

For companies using Lever:

**Method:** `parse_lever_feed(company_name: str)`

**Usage Example:**
```python
jobs = await XMLFeedService.parse_lever_feed("netflix")
jobs = await XMLFeedService.parse_lever_feed("netflix")
```

**How to find the company name:**
- Visit the company's careers page
- Look for URLs like: `https://jobs.lever.co/COMPANY_NAME/`
- The `COMPANY_NAME` is what you need

---

## User-Submitted URLs (Manual Ingestion)

Users can submit individual job URLs through the frontend. The system automatically detects:

### Supported Platforms

1. **Greenhouse** - `boards.greenhouse.io/*`
2. **Lever** - `jobs.lever.co/*`
3. **Generic Job Boards** - Attempts to parse any job posting

### How It Works

**File:** `backend/app/services/ingestion/url_parser_service.py`

1. User pastes URL in frontend modal
2. Backend fetches the HTML
3. Detects ATS platform (Greenhouse, Lever, or generic)
4. Parses job details (title, company, description)
5. Saves to database
6. Triggers matching for all users

**API Endpoint:**
```
POST /api/jobs/ingest-url
Body: { "url": "https://jobs.lever.co/company/job-id" }
```

---

## Configuration Settings

**File:** `backend/app/config.py`

```python
class Settings(BaseSettings):
    # Maximum jobs to fetch per feed (prevents overload)
    max_jobs_per_feed: int = 100

    # Other relevant settings...
```

---

## Automated Scraping Schedule

**File:** `backend/app/workers/celery_worker.py`

The system uses Celery Beat to schedule automatic scraping:

```python
# Scheduled tasks
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Scrape all RSS feeds every 30 minutes
    sender.add_periodic_task(
        crontab(minute='*/30'),
        ingest_all_feeds.s(),
        name='ingest-rss-feeds'
    )
```

### Modify Schedule

To change how often feeds are scraped:

```python
# Every hour
crontab(minute=0, hour='*/1')

# Every 15 minutes
crontab(minute='*/15')

# Daily at 9 AM
crontab(hour=9, minute=0)

# Every 6 hours
crontab(minute=0, hour='*/6')
```

---

## Common RSS Feed Sources

### Tech Job Boards
- **Stack Overflow Jobs**: `https://stackoverflow.com/jobs/feed`
- **GitHub Jobs**: Custom RSS via RSS aggregators
- **AngelList**: Company-specific feeds
- **Hacker News Who's Hiring**: Via third-party RSS services

### RSS Aggregators (Combine Multiple Sources)
- **RSS.app**: Create custom feeds from multiple sources
- **Zapier RSS**: Automated feed creation
- **Feedly**: Export combined feeds

### How to Find RSS Feeds
1. Visit job board website
2. Look for RSS icon or "Subscribe" link
3. Use browser extensions like "RSS Feed Finder"
4. Check page source for `<link rel="alternate" type="application/rss+xml">`
5. Try appending `/rss` or `/feed` to URLs

---

## Testing New Feeds

### Manual Test

```python
# In Python shell or test script
import asyncio
from app.services.ingestion.xml_feed_service import XMLFeedService

async def test_feed():
    jobs = await XMLFeedService.parse_rss_feed(
        "https://example.com/jobs.rss",
        "Test Feed"
    )
    print(f"Found {len(jobs)} jobs")
    for job in jobs[:3]:
        print(f"- {job['title']} at {job['company']}")

asyncio.run(test_feed())
```

---

## Best Practices

1. **Verify Feed Format**: Ensure RSS/XML is valid before adding
2. **Rate Limiting**: Don't scrape too frequently (respect robots.txt)
3. **Deduplication**: System automatically deduplicates via fingerprints
4. **Monitor Logs**: Check for parsing errors after adding new feeds
5. **Test First**: Test new feeds manually before adding to production

---

## Troubleshooting

### Feed Not Working

1. **Check URL is accessible**: `curl https://feed-url.com/rss`
2. **Verify it's valid RSS**: Use RSS validator online
3. **Check logs**: Look for parsing errors in backend logs
4. **Timeout issues**: Increase timeout in `httpx.AsyncClient(timeout=30.0)`

### No Jobs Being Saved

1. **Check fingerprint collisions**: Jobs might already exist
2. **Verify matching is enabled**: Check MatchingService calls
3. **Database connection**: Ensure MongoDB is running
4. **Check max_jobs_per_feed**: Might be set too low

---

## Summary

**To add a new RSS feed:**
1. Add to `FEEDS` dict in `xml_feed_service.py`
2. Restart backend
3. Feed will be scraped automatically

**To add company-specific feeds:**
- Use `parse_greenhouse_feed()` or `parse_lever_feed()`
- Add company tokens/names to your scheduler

**Users can submit individual URLs:**
- Via frontend "Add Job URL" button
- System auto-detects and parses
