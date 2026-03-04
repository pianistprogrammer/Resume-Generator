"""URL parser service for user-submitted job URLs."""

import httpx
from bs4 import BeautifulSoup
from typing import Optional, Dict
from urllib.parse import urlparse

from app.services.job_service import JobService
from app.services.ingestion.normalizer import Normalizer
from app.services.matching_service import MatchingService


class URLParserService:
    """Service for parsing job postings from user-submitted URLs."""

    @staticmethod
    async def fetch_url_content(url: str) -> tuple[str, str]:
        """Fetch HTML content from URL."""
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text, response.url

    @staticmethod
    async def parse_greenhouse_url(url: str, html: str) -> Optional[Dict]:
        """Parse Greenhouse job posting."""
        soup = BeautifulSoup(html, 'html.parser')

        try:
            # Title
            title_elem = soup.find('h1', class_='app-title')
            if not title_elem:
                title_elem = soup.find('h1')
            title = title_elem.get_text(strip=True) if title_elem else None

            # Company
            company_elem = soup.find('span', class_='company-name')
            if not company_elem:
                # Extract from URL
                parsed = urlparse(url)
                company = parsed.netloc.split('.')[0]
            else:
                company = company_elem.get_text(strip=True)

            # Description
            desc_elem = soup.find('div', id='content') or soup.find('div', class_='content')
            description = desc_elem.get_text() if desc_elem else ""

            # Location
            location_elem = soup.find('div', class_='location')
            location = location_elem.get_text(strip=True) if location_elem else None

            if not title:
                return None

            normalized_description = Normalizer.normalize_job_description(description)
            skills = Normalizer.extract_skills(normalized_description)

            return {
                "title": title,
                "company": company,
                "description": description,
                "apply_url": url,
                "source": "user_url",
                "source_url": url,
                "location": location,
                "remote": location and 'remote' in location.lower(),
                "normalized_description": normalized_description,
                "extracted_skills": skills,
                "ats_platform": "greenhouse"
            }

        except Exception as e:
            print(f"Error parsing Greenhouse URL: {e}")
            return None

    @staticmethod
    async def parse_lever_url(url: str, html: str) -> Optional[Dict]:
        """Parse Lever job posting."""
        soup = BeautifulSoup(html, 'html.parser')

        try:
            # Title
            title_elem = soup.find('h2', {'data-qa': 'posting-name'})
            if not title_elem:
                title_elem = soup.find('h2')
            title = title_elem.get_text(strip=True) if title_elem else None

            # Company
            company_elem = soup.find('div', class_='main-header-text-1')
            if not company_elem:
                parsed = urlparse(url)
                company = parsed.path.split('/')[1] if len(parsed.path.split('/')) > 1 else "Unknown"
            else:
                company = company_elem.get_text(strip=True)

            # Description
            desc_elem = soup.find('div', class_='content') or soup.find('div', class_='section-wrapper')
            description = desc_elem.get_text() if desc_elem else ""

            # Location
            location_elem = soup.find('div', class_='location')
            location = location_elem.get_text(strip=True) if location_elem else None

            if not title:
                return None

            normalized_description = Normalizer.normalize_job_description(description)
            skills = Normalizer.extract_skills(normalized_description)

            return {
                "title": title,
                "company": company,
                "description": description,
                "apply_url": url,
                "source": "user_url",
                "source_url": url,
                "location": location,
                "remote": location and 'remote' in location.lower(),
                "normalized_description": normalized_description,
                "extracted_skills": skills,
                "ats_platform": "lever"
            }

        except Exception as e:
            print(f"Error parsing Lever URL: {e}")
            return None

    @staticmethod
    async def parse_generic_url(url: str, html: str) -> Optional[Dict]:
        """Parse generic job posting page."""
        soup = BeautifulSoup(html, 'html.parser')

        try:
            # Try to find title (common patterns)
            title = None
            for selector in ['h1', 'h2', '.job-title', '.position-title', '[class*="title"]']:
                elem = soup.select_one(selector)
                if elem:
                    title = elem.get_text(strip=True)
                    break

            # Try to find company
            company = "Unknown"
            for selector in ['.company-name', '[class*="company"]', 'meta[property="og:site_name"]']:
                elem = soup.select_one(selector)
                if elem:
                    company = elem.get('content') if elem.name == 'meta' else elem.get_text(strip=True)
                    break

            # Get all text as description
            description = soup.get_text()

            if not title:
                return None

            normalized_description = Normalizer.normalize_job_description(description)
            skills = Normalizer.extract_skills(normalized_description)

            return {
                "title": title,
                "company": company,
                "description": description[:5000],  # Limit description length
                "apply_url": url,
                "source": "user_url",
                "source_url": url,
                "location": None,
                "remote": 'remote' in normalized_description.lower(),
                "normalized_description": normalized_description[:5000],
                "extracted_skills": skills,
                "ats_platform": None
            }

        except Exception as e:
            print(f"Error parsing generic URL: {e}")
            return None

    @staticmethod
    async def ingest_from_url(url: str) -> Optional[Dict]:
        """Main entry point: ingest job from URL."""
        try:
            # Fetch content
            html, final_url = await URLParserService.fetch_url_content(url)

            # Detect ATS platform
            ats_platform = Normalizer.detect_ats_platform(final_url, html)

            # Parse based on ATS
            job_data = None

            if ats_platform == "greenhouse":
                job_data = await URLParserService.parse_greenhouse_url(final_url, html)
            elif ats_platform == "lever":
                job_data = await URLParserService.parse_lever_url(final_url, html)
            else:
                job_data = await URLParserService.parse_generic_url(final_url, html)

            if not job_data:
                return None

            # Create job in database
            job = await JobService.create_job(**job_data)

            if job:
                # Trigger matching
                await MatchingService.run_matching_for_job(job)

                return {
                    "job_id": str(job.id),
                    "title": job.title,
                    "company": job.company,
                    "ats_platform": job.ats_platform
                }

            return None

        except Exception as e:
            print(f"Error ingesting URL {url}: {e}")
            raise
