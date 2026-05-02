from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from app.domain.entities.job import Job
from app.domain.interfaces.scraper_interface import IJobScraper
from app.domain.value_objects.location import Location, RemoteType
from app.domain.value_objects.salary import Salary
from app.domain.value_objects.job_type import JobType
from app.domain.value_objects.experience_level import ExperienceLevel


class MockScraper(IJobScraper):
    """
    Mock implementation of IJobScraper for testing and demonstration.
    """

    async def scrape_jobs(self, query: str, location: str = "", limit: int = 10) -> List[Dict[str, Any]]:
        """Return a list of mock raw job data."""
        mock_jobs = []
        for i in range(limit):
            mock_jobs.append({
                "title": f"Software Engineer {i} ({query})",
                "company": f"Tech Corp {i}",
                "location": location or "Cairo, Egypt",
                "salary_min": 50000 + (i * 1000),
                "salary_max": 70000 + (i * 1000),
                "salary_currency": "USD",
                "job_type": "Full-time",
                "description": f"This is a mock job description for position {i}.",
                "requirements": ["Python", "FastAPI", "SQLAlchemy"],
                "benefits": ["Health Insurance", "Remote Work"],
                "source_url": f"https://mock-jobs.com/{uuid.uuid4()}",
                "source_job_id": str(uuid.uuid4()),
                "posted_date": datetime.utcnow().isoformat(),
                "experience_level": "Mid-level",
                "is_remote": i % 2 == 0
            })
        return mock_jobs

    async def get_job_details(self, job_url: str) -> Optional[Dict[str, Any]]:
        """Return mock details for a single job."""
        return {
            "description": "Full detailed description here.",
            "requirements": ["Python", "React"],
            "benefits": ["Free snacks"]
        }

    async def health_check(self) -> bool:
        """Always healthy."""
        return True
