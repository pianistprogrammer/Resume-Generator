"""Text normalization and extraction utilities for job ingestion."""

import re
from bs4 import BeautifulSoup
from typing import List, Optional


class Normalizer:
    """Text normalization and extraction utilities."""

    @staticmethod
    def normalize_job_description(html_or_text: str) -> str:
        """Strip HTML and clean text from job description."""
        # Parse HTML
        soup = BeautifulSoup(html_or_text, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text
        text = soup.get_text()

        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)

        return text

    @staticmethod
    def extract_skills(job_description: str) -> List[str]:
        """Extract technical skills from job description."""
        # Common tech skills to look for
        common_skills = [
            # Programming languages
            "python", "javascript", "java", "c++", "c#", "ruby", "go", "rust", "php",
            "typescript", "swift", "kotlin", "scala", "r",

            # Frontend
            "react", "vue", "angular", "svelte", "html", "css", "sass", "tailwind",
            "next.js", "nuxt", "gatsby",

            # Backend
            "node.js", "express", "django", "flask", "fastapi", "spring boot",
            "rails", "laravel", ".net",

            # Databases
            "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
            "dynamodb", "cassandra", "oracle",

            # DevOps/Cloud
            "docker", "kubernetes", "aws", "azure", "gcp", "terraform", "ansible",
            "jenkins", "github actions", "gitlab ci", "circleci",

            # Tools
            "git", "jira", "confluence", "figma", "postman",

            # Data/AI
            "pandas", "numpy", "tensorflow", "pytorch", "scikit-learn", "spark",
            "airflow", "kafka",

            # Mobile
            "ios", "android", "react native", "flutter",

            # Other
            "api", "rest", "graphql", "microservices", "agile", "scrum"
        ]

        # Normalize description
        normalized_desc = job_description.lower()

        # Find skills
        found_skills = []
        for skill in common_skills:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, normalized_desc):
                found_skills.append(skill)

        return found_skills

    @staticmethod
    def detect_ats_platform(url: str, html: str = "") -> Optional[str]:
        """Detect ATS platform from URL or HTML content."""
        url_lower = url.lower()
        html_lower = html.lower() if html else ""

        # Check URL patterns
        if "greenhouse.io" in url_lower or "boards.greenhouse.io" in url_lower:
            return "greenhouse"
        elif "lever.co" in url_lower or "jobs.lever.co" in url_lower:
            return "lever"
        elif "workday.com" in url_lower:
            return "workday"
        elif "myworkdayjobs.com" in url_lower:
            return "workday"
        elif "breezy.hr" in url_lower:
            return "breezy"
        elif "ashbyhq.com" in url_lower:
            return "ashby"
        elif "jobvite.com" in url_lower:
            return "jobvite"
        elif "smartrecruiters.com" in url_lower:
            return "smartrecruiters"
        elif "icims.com" in url_lower:
            return "icims"

        # Check HTML content
        if html_lower:
            if "greenhouse" in html_lower and "grnhse" in html_lower:
                return "greenhouse"
            elif "lever" in html_lower and "lever-frame" in html_lower:
                return "lever"

        return None

    @staticmethod
    def extract_salary_from_text(text: str) -> tuple[Optional[int], Optional[int]]:
        """Extract salary range from text."""
        # Common patterns: $100k-$150k, $100,000 - $150,000, 100k-150k
        patterns = [
            r'\$?(\d{1,3}),?(\d{3}),?(\d{3})\s*-\s*\$?(\d{1,3}),?(\d{3}),?(\d{3})',  # $100,000-$150,000
            r'\$?(\d{1,3})k\s*-\s*\$?(\d{1,3})k',  # $100k-$150k
            r'\$(\d{1,3}),?(\d{3})',  # $100,000 or $100k (single value)
        ]

        text_lower = text.lower()

        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                groups = match.groups()

                if len(groups) >= 6:  # Range with full numbers
                    min_val = int(groups[0] + groups[1] + groups[2])
                    max_val = int(groups[3] + groups[4] + groups[5])
                    return min_val, max_val
                elif len(groups) == 2:  # Range in k format
                    min_val = int(groups[0]) * 1000
                    max_val = int(groups[1]) * 1000
                    return min_val, max_val

        return None, None
