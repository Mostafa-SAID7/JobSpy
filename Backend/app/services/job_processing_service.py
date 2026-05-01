"""
Job Processing Service - JobSpy
Unified job processing pipeline for parsing, filtering, scoring, and output

⚠️ DEPRECATED: This service is deprecated and will be removed in Phase 5.

Migration Path:
- Use ProcessScrapedJobsUseCase instead
- Location: app.application.use_cases.scraping.process_scraped_jobs_use_case
- See: Backend/app/services/DEPRECATION_NOTICE.md

This service is kept temporarily for backward compatibility with:
- services/alert_service.py
- services/search_service.py (also deprecated)
- scripts/seed_sample_jobs.py

Will be removed after Phase 5 (router refactoring) is complete.
"""
import warnings
import logging
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.job_repo import JobRepository
from app.schemas.job import JobCreate

logger = logging.getLogger(__name__)

# Issue deprecation warning
warnings.warn(
    "JobProcessingService is deprecated. Use ProcessScrapedJobsUseCase from "
    "app.application.use_cases.scraping instead. "
    "See Backend/app/services/DEPRECATION_NOTICE.md for migration guide.",
    DeprecationWarning,
    stacklevel=2
)


class JobProcessingService:
    """
    Unified service for all job processing operations.
    
    ⚠️ DEPRECATED: Use ProcessScrapedJobsUseCase instead.
    
    This service consolidates:
    - Job parsing and normalization
    - Skill extraction and matching
    - Job filtering logic
    - Job scoring and ranking
    - Consistent output formatting
    
    Single source of truth for job processing pipeline.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.job_repo = JobRepository(db)
        
        # Skill extraction patterns
        self.skill_patterns = {
            'programming_languages': [
                r'\b(?:python|java|javascript|typescript|c\+\+|c#|php|ruby|go|rust|swift|kotlin|scala|r|matlab)\b',
                r'\b(?:html|css|sql|nosql|bash|shell|powershell)\b'
            ],
            'frameworks': [
                r'\b(?:react|angular|vue|django|flask|fastapi|spring|express|laravel|rails)\b',
                r'\b(?:tensorflow|pytorch|scikit-learn|pandas|numpy|docker|kubernetes)\b'
            ],
            'databases': [
                r'\b(?:mysql|postgresql|mongodb|redis|elasticsearch|cassandra|oracle|sqlite)\b'
            ],
            'cloud_platforms': [
                r'\b(?:aws|azure|gcp|google cloud|amazon web services|microsoft azure)\b'
            ],
            'tools': [
                r'\b(?:git|jenkins|jira|confluence|slack|figma|photoshop|illustrator)\b'
            ]
        }
    
    async def process_scraped_jobs(
        self, 
        jobs_data: List[Dict[str, Any]], 
        source: str
    ) -> Dict[str, Any]:
        """
        Complete processing pipeline for scraped jobs.
        
        Pipeline: Raw Data → Normalize → Extract Skills → Score → Save
        
        Args:
            jobs_data: Raw job data from scraper
            source: Job source (LinkedIn, Indeed, Wuzzuf, Bayt)
        
        Returns:
            Processing statistics
        """
        saved_count = 0
        duplicate_count = 0
        error_count = 0
        processed_jobs = []
        
        for job_data in jobs_data:
            try:
                # Step 1: Normalize job data
                normalized_job = self.normalize_job(job_data, source)
                
                # Step 2: Extract skills from description and requirements
                skills = self.extract_skills(
                    normalized_job.get("description", ""),
                    normalized_job.get("requirements", [])
                )
                normalized_job["skills"] = skills
                
                # Step 3: Calculate job score for ranking
                score = self.calculate_job_score(normalized_job)
                normalized_job["score"] = score
                
                # Step 4: Check for duplicates
                existing_job = await self.job_repo.get_by_source_url(
                    normalized_job.get("source_url")
                )
                if existing_job:
                    duplicate_count += 1
                    continue
                
                # Step 5: Save to database
                job_create_data = {
                    "title": normalized_job["title"],
                    "company": normalized_job["company"],
                    "location": normalized_job["location"],
                    "source": source,
                    "salary_min": normalized_job.get("salary_min"),
                    "salary_max": normalized_job.get("salary_max"),
                    "salary_currency": normalized_job.get("salary_currency"),
                    "job_type": normalized_job.get("job_type"),
                    "description": normalized_job.get("description"),
                    "requirements": normalized_job.get("requirements"),
                    "benefits": normalized_job.get("benefits"),
                    "source_url": normalized_job["source_url"],
                    "source_job_id": normalized_job.get("source_job_id"),
                    "posted_date": normalized_job.get("posted_date"),
                    "deadline": normalized_job.get("deadline"),
                    "company_logo_url": normalized_job.get("company_logo_url"),
                    "company_website": normalized_job.get("company_website"),
                    "experience_level": normalized_job.get("experience_level"),
                    "skills": skills,
                    "is_remote": normalized_job.get("is_remote", 0),
                }
                
                job_create = JobCreate(**job_create_data)
                
                created_job = await self.job_repo.create(job_create)
                processed_jobs.append(created_job)
                saved_count += 1
                
            except Exception as e:
                logger.error(f"Error processing job from {source}: {str(e)}")
                error_count += 1
                continue
        
        await self.db.commit()
        
        return {
            "saved": saved_count,
            "duplicates": duplicate_count,
            "errors": error_count,
            "total_processed": len(jobs_data),
            "processed_jobs": processed_jobs
        }
    
    def normalize_job(self, job_data: Dict[str, Any], source: str) -> Dict[str, Any]:
        """
        Normalize job data from different sources into consistent format.
        
        Args:
            job_data: Raw job data from scraper
            source: Job source
        
        Returns:
            Normalized job data
        """
        return {
            "title": self._clean_text(job_data.get("title", "")),
            "company": self._clean_text(job_data.get("company", "")),
            "location": self._clean_text(job_data.get("location", "")),
            "salary_min": self._parse_salary(job_data.get("salary_min")),
            "salary_max": self._parse_salary(job_data.get("salary_max")),
            "salary_currency": self._clean_text(job_data.get("salary_currency", "USD")),
            "job_type": self._normalize_job_type(job_data.get("job_type", "")),
            "description": self._clean_text(job_data.get("description", "")),
            "requirements": self._normalize_requirements(job_data.get("requirements", [])),
            "benefits": job_data.get("benefits", []),
            "source": source,
            "source_url": self._clean_text(job_data.get("source_url", "")),
            "source_job_id": self._clean_text(job_data.get("source_job_id", "")),
            "posted_date": self._parse_date(job_data.get("posted_date")),
            "deadline": self._parse_date(job_data.get("deadline")),
            "company_logo_url": self._clean_text(job_data.get("company_logo_url", "")),
            "company_website": self._clean_text(job_data.get("company_website", "")),
            "experience_level": self._normalize_experience_level(job_data.get("experience_level", "")),
            "is_remote": self._parse_remote_type(job_data.get("is_remote")),
        }
    
    def extract_skills(
        self, 
        description: str, 
        requirements: List[str]
    ) -> List[str]:
        """
        Extract skills from job description and requirements.
        
        Args:
            description: Job description text
            requirements: List of requirement strings
        
        Returns:
            List of extracted skills
        """
        text = f"{description} {' '.join(requirements)}".lower()
        extracted_skills = set()
        
        for category, patterns in self.skill_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                extracted_skills.update(matches)
        
        return list(extracted_skills)
    
    def calculate_job_score(self, job_data: Dict[str, Any]) -> float:
        """
        Calculate job relevance score for ranking.
        
        Scoring factors:
        - Salary range (higher = better)
        - Company reputation (known companies get bonus)
        - Job type preference (full-time preferred)
        - Remote work availability
        - Skills count
        - Description completeness
        
        Args:
            job_data: Normalized job data
        
        Returns:
            Job score (0.0 to 100.0)
        """
        score = 0.0
        
        # Salary score (0-30 points)
        salary_max = job_data.get("salary_max", 0)
        if salary_max:
            # Normalize salary to 0-30 scale (assuming max salary of 200k)
            score += min(30, (salary_max / 200000) * 30)
        
        # Job type score (0-15 points)
        job_type = job_data.get("job_type", "").lower()
        if "full-time" in job_type or "permanent" in job_type:
            score += 15
        elif "part-time" in job_type:
            score += 10
        elif "contract" in job_type:
            score += 8
        
        # Remote work score (0-10 points)
        is_remote = job_data.get("is_remote", 0)
        if is_remote == 1:  # Remote
            score += 10
        elif is_remote == 2:  # Hybrid
            score += 7
        
        # Skills score (0-20 points)
        skills = job_data.get("skills", [])
        score += min(20, len(skills) * 2)
        
        # Description completeness (0-15 points)
        description = job_data.get("description", "")
        if len(description) > 500:
            score += 15
        elif len(description) > 200:
            score += 10
        elif len(description) > 50:
            score += 5
        
        # Company bonus (0-10 points)
        company = job_data.get("company", "").lower()
        known_companies = ["google", "microsoft", "apple", "amazon", "meta", "netflix", "tesla"]
        if any(comp in company for comp in known_companies):
            score += 10
        
        return min(100.0, score)
    
    def filter_jobs(
        self, 
        jobs: List[Dict[str, Any]], 
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Unified job filtering logic.
        
        Single source of truth for all job filtering operations.
        Used by SearchService, AlertService, and any other filtering needs.
        
        Args:
            jobs: List of jobs to filter
            filters: Filter criteria
        
        Returns:
            Filtered list of jobs
        """
        if not filters:
            return jobs
        
        filtered = jobs
        
        # Location filter
        if filters.get("location"):
            location = filters["location"].lower()
            filtered = [
                job for job in filtered 
                if location in self._get_job_field(job, "location", "").lower()
            ]
        
        # Job type filter
        if filters.get("job_type"):
            job_type = filters["job_type"].lower()
            filtered = [
                job for job in filtered 
                if job_type in self._get_job_field(job, "job_type", "").lower()
            ]
        
        # Experience level filter
        if filters.get("experience_level"):
            exp_level = filters["experience_level"].lower()
            filtered = [
                job for job in filtered 
                if exp_level in self._get_job_field(job, "experience_level", "").lower()
            ]
        
        # Salary range filters
        if filters.get("salary_min"):
            min_salary = filters["salary_min"]
            filtered = [
                job for job in filtered 
                if self._get_job_field(job, "salary_max", 0) >= min_salary
            ]
        
        if filters.get("salary_max"):
            max_salary = filters["salary_max"]
            filtered = [
                job for job in filtered 
                if self._get_job_field(job, "salary_min", float('inf')) <= max_salary
            ]
        
        # Remote work filter
        if filters.get("is_remote") is not None:
            is_remote = filters["is_remote"]
            filtered = [
                job for job in filtered 
                if self._get_job_field(job, "is_remote", 0) == is_remote
            ]
        
        # Skills filter
        if filters.get("skills"):
            required_skills = [skill.lower() for skill in filters["skills"]]
            filtered = [
                job for job in filtered 
                if self._has_required_skills(job, required_skills)
            ]
        
        # Company filter
        if filters.get("company"):
            company = filters["company"].lower()
            filtered = [
                job for job in filtered 
                if company in self._get_job_field(job, "company", "").lower()
            ]
        
        # Source filter
        if filters.get("source"):
            source = filters["source"].lower()
            filtered = [
                job for job in filtered 
                if source == self._get_job_field(job, "source", "").lower()
            ]
        
        return filtered
    
    def score_job_match(
        self, 
        job: Dict[str, Any], 
        user_profile: Dict[str, Any]
    ) -> float:
        """
        Calculate job match score for a specific user.
        
        Args:
            job: Job data
            user_profile: User profile with skills, preferences, etc.
        
        Returns:
            Match score (0.0 to 100.0)
        """
        base_score = job.get("score", 0.0)
        match_bonus = 0.0
        
        # Skill matching bonus (0-30 points)
        user_skills = set(skill.lower() for skill in user_profile.get("skills", []))
        job_skills = set(skill.lower() for skill in job.get("skills", []))
        
        if user_skills and job_skills:
            skill_match_ratio = len(user_skills.intersection(job_skills)) / len(user_skills)
            match_bonus += skill_match_ratio * 30
        
        # Location preference bonus (0-10 points)
        preferred_locations = user_profile.get("preferred_locations", [])
        job_location = job.get("location", "").lower()
        if any(loc.lower() in job_location for loc in preferred_locations):
            match_bonus += 10
        
        # Remote work preference bonus (0-10 points)
        if user_profile.get("prefers_remote") and job.get("is_remote") == 1:
            match_bonus += 10
        
        # Salary expectation match (0-20 points)
        expected_salary = user_profile.get("expected_salary")
        job_salary_max = job.get("salary_max")
        if expected_salary and job_salary_max:
            if job_salary_max >= expected_salary:
                match_bonus += 20
            elif job_salary_max >= expected_salary * 0.8:
                match_bonus += 15
            elif job_salary_max >= expected_salary * 0.6:
                match_bonus += 10
        
        return min(100.0, base_score + match_bonus)
    
    def format_job_output(
        self, 
        jobs: List[Dict[str, Any]], 
        include_score: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Format jobs for consistent output across all endpoints.
        
        Args:
            jobs: List of jobs to format
            include_score: Whether to include score in output
        
        Returns:
            Formatted jobs list
        """
        formatted = []
        
        for job in jobs:
            formatted_job = {
                "id": self._get_job_field(job, "id"),
                "title": self._get_job_field(job, "title"),
                "company": self._get_job_field(job, "company"),
                "location": self._get_job_field(job, "location"),
                "salary_range": self._format_salary_range(job),
                "job_type": self._get_job_field(job, "job_type"),
                "experience_level": self._get_job_field(job, "experience_level"),
                "is_remote": self._get_job_field(job, "is_remote", 0),
                "skills": self._get_job_field(job, "skills", []),
                "source": self._get_job_field(job, "source"),
                "posted_date": self._get_job_field(job, "posted_date"),
                "company_logo_url": self._get_job_field(job, "company_logo_url"),
            }
            
            if include_score:
                formatted_job["score"] = self._get_job_field(job, "score", 0.0)
            
            formatted.append(formatted_job)
        
        return formatted
    
    # Helper methods
    
    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean and normalize text."""
        if not text:
            return ""
        return text.strip()
    
    @staticmethod
    def _parse_salary(salary: Any) -> Optional[float]:
        """Parse salary value from various formats."""
        if not salary:
            return None
        
        try:
            if isinstance(salary, (int, float)):
                return float(salary)
            if isinstance(salary, str):
                # Remove currency symbols, commas, and spaces
                cleaned = re.sub(r'[^\d.]', '', salary)
                return float(cleaned) if cleaned else None
        except (ValueError, TypeError):
            pass
        
        return None
    
    @staticmethod
    def _parse_date(date_value: Any) -> Optional[datetime]:
        """Parse date from various formats."""
        if isinstance(date_value, datetime):
            return date_value
        if isinstance(date_value, str):
            try:
                return datetime.fromisoformat(date_value.replace('Z', '+00:00'))
            except ValueError:
                pass
        return None
    
    @staticmethod
    def _parse_remote_type(remote: Any) -> int:
        """Parse remote work type (0: On-site, 1: Remote, 2: Hybrid)."""
        if isinstance(remote, int):
            return remote
        
        if isinstance(remote, str):
            remote_lower = remote.lower()
            if "remote" in remote_lower and "hybrid" not in remote_lower:
                return 1
            elif "hybrid" in remote_lower:
                return 2
        
        return 0
    
    @staticmethod
    def _normalize_job_type(job_type: str) -> str:
        """Normalize job type to standard values."""
        if not job_type:
            return ""
        
        job_type_lower = job_type.lower()
        
        if any(term in job_type_lower for term in ["full-time", "fulltime", "permanent"]):
            return "Full-time"
        elif any(term in job_type_lower for term in ["part-time", "parttime"]):
            return "Part-time"
        elif any(term in job_type_lower for term in ["contract", "contractor", "freelance"]):
            return "Contract"
        elif any(term in job_type_lower for term in ["intern", "internship"]):
            return "Internship"
        elif any(term in job_type_lower for term in ["temporary", "temp"]):
            return "Temporary"
        
        return job_type.title()
    
    @staticmethod
    def _normalize_experience_level(experience: str) -> str:
        """Normalize experience level to standard values."""
        if not experience:
            return ""
        
        experience_lower = experience.lower()
        
        if any(term in experience_lower for term in ["entry", "junior", "graduate", "0-2"]):
            return "Entry Level"
        elif any(term in experience_lower for term in ["mid", "intermediate", "2-5", "3-5"]):
            return "Mid Level"
        elif any(term in experience_lower for term in ["senior", "lead", "5+", "5-10"]):
            return "Senior Level"
        elif any(term in experience_lower for term in ["executive", "director", "manager", "10+"]):
            return "Executive Level"
        
        return experience.title()
    
    @staticmethod
    def _normalize_requirements(requirements: Any) -> List[str]:
        """Normalize requirements to list format."""
        if isinstance(requirements, list):
            return [str(req).strip() for req in requirements if req]
        elif isinstance(requirements, str):
            # Split by common delimiters
            return [req.strip() for req in re.split(r'[;\n•]', requirements) if req.strip()]
        return []
    
    @staticmethod
    def _get_job_field(job: Any, field: str, default: Any = "") -> Any:
        """Get job field value handling both dict and object formats."""
        if isinstance(job, dict):
            return job.get(field, default)
        else:
            return getattr(job, field, default)
    
    def _has_required_skills(self, job: Any, required_skills: List[str]) -> bool:
        """Check if job has required skills."""
        job_skills = [skill.lower() for skill in self._get_job_field(job, "skills", [])]
        return any(skill in job_skills for skill in required_skills)
    
    def _format_salary_range(self, job: Any) -> str:
        """Format salary range for display."""
        salary_min = self._get_job_field(job, "salary_min")
        salary_max = self._get_job_field(job, "salary_max")
        currency = self._get_job_field(job, "salary_currency", "USD")
        
        if salary_min and salary_max:
            return f"{currency} {salary_min:,.0f} - {salary_max:,.0f}"
        elif salary_max:
            return f"Up to {currency} {salary_max:,.0f}"
        elif salary_min:
            return f"From {currency} {salary_min:,.0f}"
        else:
            return "Salary not specified"