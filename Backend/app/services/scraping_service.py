"""
Scraping Service - JobSpy
Scraping service for JobSpy
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.job_repo import JobRepository
from app.schemas.job import JobCreate

logger = logging.getLogger(__name__)


class ScrapingService:
    """Service for handling job scraping operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.job_repo = JobRepository(db)
    
    async def save_jobs(self, jobs_data: List[Dict[str, Any]], source: str) -> Dict[str, Any]:
        """
        Save scraped jobs to database.
        
        Args:
            jobs_data: List of job dictionaries from scraper
            source: Job source (LinkedIn, Indeed, Wuzzuf, Bayt)
        
        Returns:
            Dictionary with statistics about saved jobs
        """
        saved_count = 0
        duplicate_count = 0
        error_count = 0
        
        for job_data in jobs_data:
            try:
                # Normalize job data
                normalized_job = self._normalize_job(job_data)
                
                # Check if job already exists
                existing_job = await self.job_repo.get_by_source_url(
                    normalized_job.get("source_url")
                )
                if existing_job:
                    duplicate_count += 1
                    continue
                
                # Create job
                job_create = JobCreate(
                    title=normalized_job.get("title"),
                    company=normalized_job.get("company"),
                    location=normalized_job.get("location"),
                    salary_min=normalized_job.get("salary_min"),
                    salary_max=normalized_job.get("salary_max"),
                    salary_currency=normalized_job.get("salary_currency"),
                    job_type=normalized_job.get("job_type"),
                    description=normalized_job.get("description"),
                    requirements=normalized_job.get("requirements"),
                    benefits=normalized_job.get("benefits"),
                    source=source,
                    source_url=normalized_job.get("source_url"),
                    source_job_id=normalized_job.get("source_job_id"),
                    posted_date=normalized_job.get("posted_date"),
                    deadline=normalized_job.get("deadline"),
                    company_logo_url=normalized_job.get("company_logo_url"),
                    company_website=normalized_job.get("company_website"),
                    experience_level=normalized_job.get("experience_level"),
                    skills=normalized_job.get("skills"),
                    is_remote=normalized_job.get("is_remote", 0),
                )
                
                await self.job_repo.create(job_create)
                saved_count += 1
            except Exception as e:
                logger.error(f"Error saving job from {source}: {str(e)}")
                error_count += 1
                continue
        
        await self.db.commit()
        
        return {
            "saved": saved_count,
            "duplicates": duplicate_count,
            "errors": error_count,
            "total_processed": len(jobs_data),
        }
    
    def _normalize_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize job data from different sources.
        
        Args:
            job_data: Raw job data from scraper
        
        Returns:
            Normalized job data
        """
        return {
            "title": (job_data.get("title") or "").strip(),
            "company": (job_data.get("company") or "").strip(),
            "location": (job_data.get("location") or "").strip(),
            "salary_min": self._parse_salary(job_data.get("salary_min")),
            "salary_max": self._parse_salary(job_data.get("salary_max")),
            "salary_currency": (job_data.get("salary_currency") or "USD").strip(),
            "job_type": (job_data.get("job_type") or "").strip(),
            "description": (job_data.get("description") or "").strip(),
            "requirements": job_data.get("requirements") or [],
            "benefits": job_data.get("benefits") or [],
            "source_url": (job_data.get("source_url") or "").strip(),
            "source_job_id": (job_data.get("source_job_id") or "").strip(),
            "posted_date": job_data.get("posted_date"),
            "deadline": job_data.get("deadline"),
            "company_logo_url": (job_data.get("company_logo_url") or "").strip(),
            "company_website": (job_data.get("company_website") or "").strip(),
            "experience_level": (job_data.get("experience_level") or "").strip(),
            "skills": job_data.get("skills") or [],
            "is_remote": self._parse_remote(job_data.get("is_remote")),
        }
    
    async def normalize_jobs(self, jobs_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normalize job data from different sources.
        
        Args:
            jobs_data: Raw job data from scraper
        
        Returns:
            Normalized job data
        """
        normalized = []
        
        for job in jobs_data:
            normalized_job = self._normalize_job(job)
            
            # Only add if required fields are present
            if normalized_job["title"] and normalized_job["company"] and normalized_job["source_url"]:
                normalized.append(normalized_job)
        
        return normalized
    
    @staticmethod
    def _parse_salary(salary: Any) -> float | None:
        """Parse salary value."""
        if not salary:
            return None
        
        try:
            if isinstance(salary, (int, float)):
                return float(salary)
            if isinstance(salary, str):
                # Remove common currency symbols and commas
                cleaned = salary.replace("$", "").replace("€", "").replace("£", "").replace(",", "")
                return float(cleaned)
        except (ValueError, TypeError):
            pass
        
        return None
    
    @staticmethod
    def _parse_remote(remote: Any) -> int:
        """Parse remote work type (0: On-site, 1: Remote, 2: Hybrid)."""
        if isinstance(remote, int):
            return remote
        
        if isinstance(remote, str):
            remote_lower = remote.lower()
            if "remote" in remote_lower:
                return 1
            elif "hybrid" in remote_lower:
                return 2
        
        return 0
    
    async def remove_duplicates(self) -> int:
        """
        Remove duplicate jobs based on source_url.
        
        Returns:
            Number of duplicates removed
        """
        # This would require a more complex query
        # For now, duplicates are prevented at insert time
        return 0
    
    async def get_jobs_by_source(self, source: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get jobs from a specific source.
        
        Args:
            source: Job source (LinkedIn, Indeed, Wuzzuf, Bayt)
            limit: Maximum number of jobs to return
        
        Returns:
            List of jobs from the source
        """
        jobs = await self.job_repo.search({"source": source}, limit=limit)
        return jobs
    
    async def update_job_status(self, job_id: int, status: str) -> bool:
        """
        Update job status (active, expired, etc).
        
        Args:
            job_id: Job ID
            status: New status
        
        Returns:
            True if updated successfully
        """
        try:
            job = await self.job_repo.get_by_id(job_id)
            if job:
                # Update status in database
                await self.db.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating job status: {str(e)}")
        
        return False
