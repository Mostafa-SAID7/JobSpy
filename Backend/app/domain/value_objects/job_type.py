"""
Job Type Value Object

Enumeration of job types with normalization logic.
"""

from enum import Enum
from typing import Optional


class JobType(Enum):
    """
    Job type enumeration.
    
    Standardized job types across all job sources.
    """
    
    FULL_TIME = "Full-time"
    PART_TIME = "Part-time"
    CONTRACT = "Contract"
    INTERNSHIP = "Internship"
    TEMPORARY = "Temporary"
    FREELANCE = "Freelance"
    UNKNOWN = "Unknown"
    
    @classmethod
    def from_string(cls, job_type_str: Optional[str]) -> "JobType":
        """
        Normalize job type string to enum value.
        
        Handles various formats from different job sources:
        - "Full-time", "fulltime", "full time", "permanent"
        - "Part-time", "parttime", "part time"
        - "Contract", "contractor", "freelance"
        - "Internship", "intern"
        - "Temporary", "temp"
        
        Args:
            job_type_str: Job type string from source
        
        Returns:
            JobType enum value
        """
        if not job_type_str:
            return cls.UNKNOWN
        
        job_type_lower = job_type_str.lower().strip()
        
        # Full-time variations
        if any(term in job_type_lower for term in [
            "full-time", "fulltime", "full time", "permanent", "regular"
        ]):
            return cls.FULL_TIME
        
        # Part-time variations
        if any(term in job_type_lower for term in [
            "part-time", "parttime", "part time"
        ]):
            return cls.PART_TIME
        
        # Contract variations
        if any(term in job_type_lower for term in [
            "contract", "contractor", "consulting"
        ]):
            return cls.CONTRACT
        
        # Freelance
        if "freelance" in job_type_lower:
            return cls.FREELANCE
        
        # Internship variations
        if any(term in job_type_lower for term in [
            "intern", "internship", "trainee"
        ]):
            return cls.INTERNSHIP
        
        # Temporary variations
        if any(term in job_type_lower for term in [
            "temporary", "temp", "seasonal"
        ]):
            return cls.TEMPORARY
        
        return cls.UNKNOWN
    
    def is_permanent(self) -> bool:
        """Check if job type is permanent (full-time or part-time)"""
        return self in (JobType.FULL_TIME, JobType.PART_TIME)
    
    def is_temporary(self) -> bool:
        """Check if job type is temporary"""
        return self in (JobType.CONTRACT, JobType.TEMPORARY, JobType.FREELANCE, JobType.INTERNSHIP)
    
    def __str__(self) -> str:
        return self.value
