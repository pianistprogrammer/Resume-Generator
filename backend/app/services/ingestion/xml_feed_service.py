"""RSS/XML feed ingestion service for job aggregation."""

import feedparser
import httpx
import asyncio
from functools import partial
from typing import List, Dict, Optional
from datetime import datetime

from app.services.job_service import JobService
from app.services.ingestion.normalizer import Normalizer
from app.services.matching_service import MatchingService
from app.config import settings
from app.schemas.user import FeedSource


class XMLFeedService:
    """Service for ingesting jobs from RSS/XML feeds."""

    @staticmethod
    async def get_active_feeds() -> List[FeedSource]:
        """Get all active feed sources from database."""
        loop = asyncio.get_event_loop()

        def _query():
            return list(FeedSource.objects(is_active=True))

        return await loop.run_in_executor(None, _query)

    @staticmethod
    async def parse_rss_feed(feed_url: str, source_name: str) -> List[Dict]:
        """Parse an RSS feed and extract job data."""
        jobs = []

        try:
            # Fetch feed with timeout
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(feed_url)
                response.raise_for_status()
                feed_content = response.text

            # Parse with feedparser
            feed = feedparser.parse(feed_content)

            for entry in feed.entries[:settings.max_jobs_per_feed]:
                try:
                    # Extract basic info
                    title = entry.get('title', '').strip()
                    link = entry.get('link', '').strip()
                    description = entry.get('description', '') or entry.get('summary', '')

                    if not title or not link:
                        continue

                    # Try to extract company from title (common format: "Company | Job Title")
                    company = "Unknown"
                    if '|' in title:
                        parts = title.split('|')
                        company = parts[0].strip()
                        title = parts[1].strip() if len(parts) > 1 else title
                    elif ' at ' in title:
                        parts = title.split(' at ')
                        title = parts[0].strip()
                        company = parts[1].strip() if len(parts) > 1 else company

                    # Normalize description
                    normalized_description = Normalizer.normalize_job_description(description)

                    # Extract skills
                    skills = Normalizer.extract_skills(normalized_description)

                    # Parse posted date
                    posted_at = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        posted_at = datetime(*entry.published_parsed[:6])

                    # Detect remote
                    remote = 'remote' in title.lower() or 'remote' in normalized_description.lower()

                    jobs.append({
                        "title": title,
                        "company": company,
                        "description": description,
                        "apply_url": link,
                        "source": f"rss_{source_name}",
                        "source_url": feed_url,
                        "location": None,  # RSS feeds typically don't include location
                        "remote": remote,
                        "normalized_description": normalized_description,
                        "extracted_skills": skills,
                        "posted_at": posted_at,
                        "ats_platform": None
                    })

                except Exception as e:
                    print(f"Error parsing feed entry: {e}")
                    continue

        except Exception as e:
            print(f"Error fetching RSS feed {feed_url}: {e}")

        return jobs

    @staticmethod
    async def parse_greenhouse_feed(company_token: str) -> List[Dict]:
        """Parse Greenhouse JSON feed for a company."""
        jobs = []
        url = f"https://boards-api.greenhouse.io/v1/boards/{company_token}/jobs"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()

            for job_data in data.get('jobs', [])[:settings.max_jobs_per_feed]:
                try:
                    title = job_data.get('title', '').strip()
                    job_id = job_data.get('id')
                    location = job_data.get('location', {}).get('name', '')

                    if not title or not job_id:
                        continue

                    apply_url = f"https://boards.greenhouse.io/{company_token}/jobs/{job_id}"
                    description = job_data.get('content', '')

                    normalized_description = Normalizer.normalize_job_description(description)
                    skills = Normalizer.extract_skills(normalized_description)

                    jobs.append({
                        "title": title,
                        "company": company_token,  # Will be overridden if known
                        "description": description,
                        "apply_url": apply_url,
                        "source": "api_greenhouse",
                        "source_url": url,
                        "location": location,
                        "remote": location and 'remote' in location.lower(),
                        "normalized_description": normalized_description,
                        "extracted_skills": skills,
                        "posted_at": None,
                        "ats_platform": "greenhouse"
                    })

                except Exception as e:
                    print(f"Error parsing Greenhouse job: {e}")
                    continue

        except Exception as e:
            print(f"Error fetching Greenhouse feed for {company_token}: {e}")

        return jobs

    @staticmethod
    async def parse_lever_feed(company_name: str) -> List[Dict]:
        """Parse Lever JSON feed for a company."""
        jobs = []
        url = f"https://api.lever.co/v0/postings/{company_name}"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()

            for job_data in data[:settings.max_jobs_per_feed]:
                try:
                    title = job_data.get('text', '').strip()
                    job_id = job_data.get('id')
                    location = job_data.get('categories', {}).get('location', '')

                    if not title or not job_id:
                        continue

                    apply_url = job_data.get('hostedUrl', f"https://jobs.lever.co/{company_name}/{job_id}")
                    description = job_data.get('description', '') or job_data.get('descriptionPlain', '')

                    normalized_description = Normalizer.normalize_job_description(description)
                    skills = Normalizer.extract_skills(normalized_description)

                    jobs.append({
                        "title": title,
                        "company": company_name,
                        "description": description,
                        "apply_url": apply_url,
                        "source": "api_lever",
                        "source_url": url,
                        "location": location,
                        "remote": location and 'remote' in location.lower(),
                        "normalized_description": normalized_description,
                        "extracted_skills": skills,
                        "posted_at": None,
                        "ats_platform": "lever"
                    })

                except Exception as e:
                    print(f"Error parsing Lever job: {e}")
                    continue

        except Exception as e:
            print(f"Error fetching Lever feed for {company_name}: {e}")

        return jobs

    @staticmethod
    async def ingest_all_feeds() -> Dict[str, int]:
        """Ingest jobs from all active feeds in database."""
        results = {}
        loop = asyncio.get_event_loop()

        # Get all active feeds from database
        feeds = await XMLFeedService.get_active_feeds()

        for feed in feeds:
            try:
                jobs = []

                # Parse based on feed type
                if feed.feed_type == "rss":
                    jobs = await XMLFeedService.parse_rss_feed(feed.url, feed.name)
                elif feed.feed_type == "greenhouse":
                    jobs = await XMLFeedService.parse_greenhouse_feed(feed.company_token or feed.name)
                elif feed.feed_type == "lever":
                    jobs = await XMLFeedService.parse_lever_feed(feed.company_token or feed.name)

                saved_count = 0
                for job_data in jobs:
                    job = await JobService.create_job(**job_data)
                    if job:
                        saved_count += 1
                        # Trigger matching for new job
                        await MatchingService.run_matching_for_job(job)

                # Update feed stats
                def _update_feed():
                    feed.last_scraped_at = datetime.utcnow()
                    feed.last_scrape_success = True
                    feed.last_scrape_job_count = saved_count
                    feed.total_jobs_scraped += saved_count
                    feed.last_scrape_error = None
                    feed.save()

                await loop.run_in_executor(None, _update_feed)

                results[feed.name] = saved_count

            except Exception as e:
                # Update feed with error
                def _update_feed_error():
                    feed.last_scraped_at = datetime.utcnow()
                    feed.last_scrape_success = False
                    feed.last_scrape_error = str(e)
                    feed.save()

                await loop.run_in_executor(None, _update_feed_error)

                results[feed.name] = 0
                print(f"Error ingesting feed {feed.name}: {e}")

        return results
