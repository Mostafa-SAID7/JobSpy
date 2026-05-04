"""
Job Mapper

Converts between raw data and domain entities.
Handles all the messy parsing and normalization.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import uuid4

from app.domain.entities.job import Job
from app.domain.value_objects.salary import Salary
from app.domain.value_objects.location import Location, RemoteType
from app.domain.value_objects.job_type import JobType
from app.domain.value_objects.experience_level import ExperienceLevel

logger = logging.getLogger(__name__)


class JobMapper:
    """
    Mapper for converting raw job data to domain entities.
    
    Single Responsibility: Handle all parsing and normalization logic.
    This was previously scattered across JobProcessingService.
    """
    
    def from_dict(self, job_data: Dict[str, Any], source: str) -> Job:
        """
        Convert raw job dictionary to domain entity.
        
        Handles:
        - Data cleaning and normalization
        - Type conversion
        - Value object creation
        - Default values
        
        Args:
            job_data: Raw job dictionary from scraper
            source: Job source (LinkedIn, Indeed, etc.)
        
        Returns:
            Job domain entity
        
        Raises:
            ValueError: If required fields are missing or invalid
        """
        try:
            # Parse core fields
            title = self._clean_text(job_data.get("title", ""))
            company = self._clean_text(job_data.get("company", ""))
            description = self._clean_text(job_data.get("description", ""))
            
            # Validate required fields
            if not title:
                raise ValueError("Job title is required")
            if not company:
                raise ValueError("Company name is required")
            
            # Parse value objects
            salary = self._parse_salary(job_data)
            location = self._parse_location(job_data)
            job_type = self._parse_job_type(job_data)
            experience_level = self._parse_experience_level(job_data)
            
            # Parse lists
            requirements = self._parse_requirements(job_data.get("requirements", []))
            benefits = self._parse_list(job_data.get("benefits", []))
            
            # Parse dates
            posted_date = self._parse_date(job_data.get("posted_date")) or datetime.utcnow()
            deadline = self._parse_date(job_data.get("deadline"))
            
            # Parse source information
            source_url = self._clean_text(job_data.get("source_url", ""))
            if not source_url:
                raise ValueError("Source URL is required")
            
            source_job_id = self._clean_text(job_data.get("source_job_id", ""))
            
            # Parse company info
            company_logo_url = self._clean_text(job_data.get("company_logo_url", ""))
            company_website = self._clean_text(job_data.get("company_website", ""))
            
            # Create job entity
            job = Job.create(
                title=title,
                company=company,
                location=location,
                description=description,
                job_type=job_type,
                experience_level=experience_level,
                source=source,
                source_url=source_url,
                posted_date=posted_date,
                salary=salary,
                requirements=requirements,
                skills=[],  # Will be populated by SkillExtractionService
                benefits=benefits,
                source_job_id=source_job_id if source_job_id else None,
                deadline=deadline,
                company_logo_url=company_logo_url if company_logo_url else None,
                company_website=company_website if company_website else None,
                source_url_direct=self._clean_text(job_data.get("job_url_direct", "")),
                company_industry=self._clean_text(job_data.get("company_industry", "")),
                company_addresses=self._clean_text(job_data.get("company_addresses", "")),
                company_num_employees=self._clean_text(job_data.get("company_num_employees", "")),
                company_revenue=self._clean_text(job_data.get("company_revenue", "")),
                company_description=self._clean_text(job_data.get("company_description", "")),
                company_rating=job_data.get("company_rating"),
                company_reviews_count=job_data.get("company_reviews_count"),
                job_level=self._clean_text(job_data.get("job_level", "")),
                job_function=self._clean_text(job_data.get("job_function", "")),
                experience_range=self._clean_text(job_data.get("experience_range", "")),
                emails=self._parse_list(job_data.get("emails", [])),
                banner_photo_url=self._clean_text(job_data.get("banner_photo_url", "")),
                vacancy_count=job_data.get("vacancy_count"),
                work_from_home_type=self._clean_text(job_data.get("work_from_home_type", "")),
            )
            
            return job
            
        except Exception as e:
            logger.error(f"Error mapping job data: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to map job data: {str(e)}")
    
    def _parse_salary(self, job_data: Dict[str, Any]) -> Optional[Salary]:
        """Parse salary from job data"""
        try:
            salary_min = job_data.get("salary_min")
            salary_max = job_data.get("salary_max")
            currency = job_data.get("salary_currency", "USD")
            
            # If we have a salary string, try to parse it
            if "salary" in job_data and isinstance(job_data["salary"], str):
                return Salary.from_string(job_data["salary"], currency)
            
            # Otherwise use min/max if available
            if salary_min is not None or salary_max is not None:
                return Salary.from_range(salary_min, salary_max, currency)
            
            return None
            
        except Exception as e:
            logger.warning(f"Error parsing salary: {str(e)}")
            return None
    
    def _parse_location(self, job_data: Dict[str, Any]) -> Location:
        """Parse location from job data"""
        try:
            location_str = job_data.get("location", "")
            
            # Parse remote type
            remote_value = job_data.get("is_remote", 0)
            if isinstance(remote_value, int):
                remote_type = RemoteType.from_int(remote_value)
            elif isinstance(remote_value, str):
                remote_type = RemoteType.from_string(remote_value)
            else:
                remote_type = RemoteType.ON_SITE
            
            # Parse location string
            if location_str:
                return Location.from_string(location_str, remote_type)
            else:
                # If no location but remote, create remote location
                if remote_type == RemoteType.REMOTE:
                    return Location.remote()
                else:
                    return Location(None, None, remote_type, "Location not specified")
                    
        except Exception as e:
            logger.warning(f"Error parsing location: {str(e)}")
            return Location(None, None, RemoteType.ON_SITE, "Location not specified")
    
    def _parse_job_type(self, job_data: Dict[str, Any]) -> JobType:
        """Parse job type from job data"""
        job_type_str = job_data.get("job_type", "")
        return JobType.from_string(job_type_str)
    
    def _parse_experience_level(self, job_data: Dict[str, Any]) -> ExperienceLevel:
        """Parse experience level from job data"""
        experience_str = job_data.get("experience_level", "")
        return ExperienceLevel.from_string(experience_str)
    
    def _parse_requirements(self, requirements: Any) -> list[str]:
        """Parse requirements list"""
        if isinstance(requirements, list):
            return [str(req).strip() for req in requirements if req]
        elif isinstance(requirements, str):
            # Split by common delimiters
            import re
            return [req.strip() for req in re.split(r'[;\n•]', requirements) if req.strip()]
        return []
    
    def _parse_list(self, value: Any) -> list[str]:
        """Parse generic list field"""
        if isinstance(value, list):
            return [str(item).strip() for item in value if item]
        elif isinstance(value, str):
            return [value.strip()] if value.strip() else []
        return []
    
    def _parse_date(self, date_value: Any) -> Optional[datetime]:
        """Parse date from various formats"""
        if isinstance(date_value, datetime):
            return date_value
        
        if isinstance(date_value, str):
            try:
                # Try ISO format
                return datetime.fromisoformat(date_value.replace('Z', '+00:00'))
            except ValueError:
                try:
                    # Try common formats
                    from dateutil import parser
                    return parser.parse(date_value)
                except:
                    logger.warning(f"Could not parse date: {date_value}")
                    return None
        
        return None
    
    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        return text.strip()
    
    def to_dict(self, job: Job) -> Dict[str, Any]:
        """
        Convert job entity to dictionary.
        
        Useful for serialization and API responses.
        
        Args:
            job: Job entity
        
        Returns:
            Dictionary representation
        """
        return {
            "id": str(job.id),
            "title": job.title,
            "company": job.company,
            "location": job.location.to_dict(),
            "description": job.description,
            "job_type": job.job_type.value,
            "experience_level": job.experience_level.value,
            "salary": job.salary.to_dict() if job.salary else None,
            "requirements": job.requirements,
            "skills": job.skills,
            "benefits": job.benefits,
            "source": job.source,
            "source_url": job.source_url,
            "source_job_id": job.source_job_id,
            "posted_date": job.posted_date.isoformat() if job.posted_date else None,
            "deadline": job.deadline.isoformat() if job.deadline else None,
            "company_logo_url": job.company_logo_url,
            "company_website": job.company_website,
            "source_url_direct": job.source_url_direct,
            "company_industry": job.company_industry,
            "company_addresses": job.company_addresses,
            "company_num_employees": job.company_num_employees,
            "company_revenue": job.company_revenue,
            "company_description": job.company_description,
            "company_rating": job.company_rating,
            "company_reviews_count": job.company_reviews_count,
            "job_level": job.job_level,
            "job_function": job.job_function,
            "experience_range": job.experience_range,
            "emails": job.emails,
            "banner_photo_url": job.banner_photo_url,
            "vacancy_count": job.vacancy_count,
            "work_from_home_type": job.work_from_home_type,
            "view_count": job.view_count,
            "apply_count": job.apply_count,
            "created_at": job.created_at.isoformat(),
            "updated_at": job.updated_at.isoformat(),
            "scraped_at": job.scraped_at.isoformat(),
        }
