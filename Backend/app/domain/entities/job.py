"""
Job Domain Entity

Pure business entity with no infrastructure dependencies.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID, uuid4

from ..value_objects.salary import Salary
from ..value_objects.location import Location
from ..value_objects.job_type import JobType
from ..value_objects.experience_level import ExperienceLevel


@dataclass
class Job:
    """
    Job domain entity - core business object.
    
    This is a pure domain entity with:
    - Business logic methods
    - Invariant validation
    - No infrastructure dependencies (no ORM, no database)
    
    Invariants:
    - Title must be at least 3 characters
    - Company name is required
    - Source and source_url are required for tracking
    - Posted date cannot be in the future
    """
    
    # Identity
    id: UUID
    
    # Core attributes
    title: str
    company: str
    location: Location
    description: str
    
    # Classification
    job_type: JobType
    experience_level: ExperienceLevel
    
    # Compensation
    salary: Optional[Salary]
    
    # Details
    requirements: List[str]
    skills: List[str]
    benefits: List[str]
    
    # Source tracking
    source: str  # LinkedIn, Indeed, Wuzzuf, Bayt
    source_url: str
    source_job_id: Optional[str]
    
    # Dates
    posted_date: datetime
    deadline: Optional[datetime]
    
    # Company info
    company_logo_url: Optional[str] = None
    company_website: Optional[str] = None
    
    # Metrics
    view_count: int = 0
    apply_count: int = 0
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    scraped_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validate domain invariants"""
        self._validate_title()
        self._validate_company()
        self._validate_source()
        self._validate_dates()
    
    def _validate_title(self):
        """Validate job title"""
        if not self.title or len(self.title.strip()) < 3:
            raise ValueError("Job title must be at least 3 characters")
    
    def _validate_company(self):
        """Validate company name"""
        if not self.company or not self.company.strip():
            raise ValueError("Company name is required")
    
    def _validate_source(self):
        """Validate source information"""
        if not self.source or not self.source.strip():
            raise ValueError("Job source is required")
        
        if not self.source_url or not self.source_url.strip():
            raise ValueError("Source URL is required for tracking")
    
    def _validate_dates(self):
        """Validate dates"""
        now = datetime.utcnow()
        
        # Posted date cannot be in the future
        if self.posted_date > now:
            raise ValueError("Posted date cannot be in the future")
        
        # Deadline must be after posted date
        if self.deadline and self.deadline < self.posted_date:
            raise ValueError("Deadline cannot be before posted date")
    
    @classmethod
    def create(
        cls,
        title: str,
        company: str,
        location: Location,
        description: str,
        job_type: JobType,
        experience_level: ExperienceLevel,
        source: str,
        source_url: str,
        posted_date: datetime,
        requirements: Optional[List[str]] = None,
        skills: Optional[List[str]] = None,
        benefits: Optional[List[str]] = None,
        **kwargs
    ) -> "Job":
        """
        Factory method for creating new jobs.
        
        Args:
            title: Job title
            company: Company name
            location: Job location
            description: Job description
            job_type: Type of job
            experience_level: Required experience level
            source: Job source
            source_url: Source URL
            posted_date: When job was posted
            requirements: Job requirements
            skills: Required skills
            benefits: Job benefits
            **kwargs: Additional optional fields
        
        Returns:
            New Job instance
        """
        return cls(
            id=uuid4(),
            title=title,
            company=company,
            location=location,
            description=description,
            job_type=job_type,
            experience_level=experience_level,
            source=source,
            source_url=source_url,
            posted_date=posted_date,
            requirements=requirements or [],
            skills=skills or [],
            benefits=benefits or [],
            **kwargs
        )
    
    # Business logic methods
    
    def is_remote(self) -> bool:
        """Check if job is fully remote"""
        return self.location.is_remote()
    
    def is_hybrid(self) -> bool:
        """Check if job is hybrid"""
        return self.location.is_hybrid()
    
    def is_on_site(self) -> bool:
        """Check if job is on-site"""
        return self.location.is_on_site()
    
    def matches_skills(self, required_skills: List[str]) -> bool:
        """
        Check if job matches required skills.
        
        Args:
            required_skills: List of required skills
        
        Returns:
            True if job has any of the required skills
        """
        if not required_skills:
            return True
        
        job_skills_lower = {skill.lower() for skill in self.skills}
        required_lower = {skill.lower() for skill in required_skills}
        
        return bool(job_skills_lower.intersection(required_lower))
    
    def matches_salary_expectation(self, expected_salary: Decimal) -> bool:
        """
        Check if job meets salary expectation.
        
        Args:
            expected_salary: Expected salary amount
        
        Returns:
            True if job meets expectation
        """
        if not self.salary:
            return False
        
        return self.salary.meets_minimum(expected_salary)
    
    def is_entry_level(self) -> bool:
        """Check if job is entry level"""
        return self.experience_level == ExperienceLevel.ENTRY
    
    def is_senior_level(self) -> bool:
        """Check if job is senior level or above"""
        return self.experience_level.is_senior_or_above()
    
    def is_expired(self, current_date: Optional[datetime] = None) -> bool:
        """
        Check if job posting has expired.
        
        Args:
            current_date: Current date (default: now)
        
        Returns:
            True if expired, False otherwise
        """
        if not self.deadline:
            return False
        
        if current_date is None:
            current_date = datetime.utcnow()
        
        return current_date > self.deadline
    
    def days_since_posted(self, current_date: Optional[datetime] = None) -> int:
        """
        Get number of days since job was posted.
        
        Args:
            current_date: Current date (default: now)
        
        Returns:
            Number of days
        """
        if current_date is None:
            current_date = datetime.utcnow()
        
        return (current_date - self.posted_date).days
    
    def is_recent(self, days: int = 7) -> bool:
        """
        Check if job was posted recently.
        
        Args:
            days: Number of days to consider recent (default: 7)
        
        Returns:
            True if posted within specified days
        """
        return self.days_since_posted() <= days
    
    def increment_views(self) -> None:
        """Increment view count"""
        self.view_count += 1
        self.updated_at = datetime.utcnow()
    
    def increment_applies(self) -> None:
        """Increment apply count"""
        self.apply_count += 1
        self.updated_at = datetime.utcnow()
    
    def update_details(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        requirements: Optional[List[str]] = None,
        benefits: Optional[List[str]] = None,
    ) -> None:
        """
        Update job details.
        
        Args:
            title: New title
            description: New description
            requirements: New requirements
            benefits: New benefits
        """
        if title is not None:
            self.title = title
            self._validate_title()
        
        if description is not None:
            self.description = description
        
        if requirements is not None:
            self.requirements = requirements
        
        if benefits is not None:
            self.benefits = benefits
        
        self.updated_at = datetime.utcnow()
    
    def has_competitive_salary(self, market_average: Decimal) -> bool:
        """
        Check if salary is competitive compared to market average.
        
        Args:
            market_average: Market average salary
        
        Returns:
            True if competitive (>= 90% of market average)
        """
        if not self.salary or not self.salary.max_amount:
            return False
        
        threshold = market_average * Decimal("0.9")
        return self.salary.max_amount >= threshold
    
    def __str__(self) -> str:
        return f"{self.title} at {self.company} ({self.location.format()})"
    
    def __repr__(self) -> str:
        return f"Job(id={self.id}, title='{self.title}', company='{self.company}')"
