"""
Job Scoring Service

Domain service for calculating job relevance scores.
Single responsibility: scoring algorithm.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import List

from ..entities.job import Job
from ..value_objects.job_type import JobType
from ..value_objects.experience_level import ExperienceLevel


@dataclass
class ScoringConfig:
    """
    Configuration for job scoring algorithm.
    
    All magic numbers are now explicit configuration.
    """
    
    # Scoring weights (total: 100 points)
    SALARY_WEIGHT: float = 30.0
    JOB_TYPE_WEIGHT: float = 15.0
    REMOTE_WEIGHT: float = 10.0
    SKILLS_WEIGHT: float = 20.0
    DESCRIPTION_WEIGHT: float = 15.0
    COMPANY_WEIGHT: float = 10.0
    
    # Salary scoring
    MAX_SALARY_REFERENCE: Decimal = Decimal("200000")
    
    # Job type scores
    FULL_TIME_SCORE: float = 15.0
    PART_TIME_SCORE: float = 10.0
    CONTRACT_SCORE: float = 8.0
    INTERNSHIP_SCORE: float = 5.0
    TEMPORARY_SCORE: float = 5.0
    FREELANCE_SCORE: float = 8.0
    
    # Remote work scores
    REMOTE_SCORE: float = 10.0
    HYBRID_SCORE: float = 7.0
    ON_SITE_SCORE: float = 0.0
    
    # Skills scoring
    POINTS_PER_SKILL: float = 2.0
    
    # Description scoring thresholds
    DESCRIPTION_EXCELLENT_LENGTH: int = 500
    DESCRIPTION_GOOD_LENGTH: int = 200
    DESCRIPTION_FAIR_LENGTH: int = 50
    
    DESCRIPTION_EXCELLENT_SCORE: float = 15.0
    DESCRIPTION_GOOD_SCORE: float = 10.0
    DESCRIPTION_FAIR_SCORE: float = 5.0
    
    # Known reputable companies (bonus points)
    KNOWN_COMPANIES: List[str] = None
    
    def __post_init__(self):
        """Initialize default known companies if not provided"""
        if self.KNOWN_COMPANIES is None:
            object.__setattr__(self, 'KNOWN_COMPANIES', [
                "google", "microsoft", "apple", "amazon", "meta", "facebook",
                "netflix", "tesla", "nvidia", "intel", "ibm", "oracle",
                "salesforce", "adobe", "spotify", "uber", "airbnb", "stripe"
            ])


class JobScoringService:
    """
    Domain service for calculating job relevance scores.
    
    Single Responsibility: Implement scoring algorithm.
    
    Score breakdown (0-100 points):
    - Salary: 0-30 points
    - Job Type: 0-15 points
    - Remote Work: 0-10 points
    - Skills: 0-20 points
    - Description: 0-15 points
    - Company: 0-10 points
    """
    
    def __init__(self, config: ScoringConfig = None):
        """
        Initialize scoring service.
        
        Args:
            config: Scoring configuration (uses defaults if not provided)
        """
        self.config = config or ScoringConfig()
    
    def calculate_score(self, job: Job) -> float:
        """
        Calculate overall job relevance score.
        
        Args:
            job: Job entity
        
        Returns:
            Score from 0.0 to 100.0
        """
        score = 0.0
        
        score += self._score_salary(job)
        score += self._score_job_type(job)
        score += self._score_remote(job)
        score += self._score_skills(job)
        score += self._score_description(job)
        score += self._score_company(job)
        
        return min(100.0, score)
    
    def _score_salary(self, job: Job) -> float:
        """
        Score based on salary (0-30 points).
        
        Higher salaries get higher scores, normalized against reference salary.
        
        Args:
            job: Job entity
        
        Returns:
            Salary score
        """
        if not job.salary or not job.salary.max_amount:
            return 0.0
        
        # Normalize salary against reference
        normalized = float(job.salary.max_amount) / float(self.config.MAX_SALARY_REFERENCE)
        
        # Cap at maximum weight
        return min(self.config.SALARY_WEIGHT, normalized * self.config.SALARY_WEIGHT)
    
    def _score_job_type(self, job: Job) -> float:
        """
        Score based on job type (0-15 points).
        
        Full-time positions typically preferred, followed by part-time, contract, etc.
        
        Args:
            job: Job entity
        
        Returns:
            Job type score
        """
        type_scores = {
            JobType.FULL_TIME: self.config.FULL_TIME_SCORE,
            JobType.PART_TIME: self.config.PART_TIME_SCORE,
            JobType.CONTRACT: self.config.CONTRACT_SCORE,
            JobType.FREELANCE: self.config.FREELANCE_SCORE,
            JobType.INTERNSHIP: self.config.INTERNSHIP_SCORE,
            JobType.TEMPORARY: self.config.TEMPORARY_SCORE,
            JobType.UNKNOWN: 0.0,
        }
        
        return type_scores.get(job.job_type, 0.0)
    
    def _score_remote(self, job: Job) -> float:
        """
        Score based on remote work availability (0-10 points).
        
        Remote work is increasingly valued, hybrid is also good.
        
        Args:
            job: Job entity
        
        Returns:
            Remote work score
        """
        if job.is_remote():
            return self.config.REMOTE_SCORE
        elif job.is_hybrid():
            return self.config.HYBRID_SCORE
        else:
            return self.config.ON_SITE_SCORE
    
    def _score_skills(self, job: Job) -> float:
        """
        Score based on number of skills (0-20 points).
        
        More skills indicate more detailed job posting and learning opportunities.
        
        Args:
            job: Job entity
        
        Returns:
            Skills score
        """
        skill_count = len(job.skills)
        score = skill_count * self.config.POINTS_PER_SKILL
        
        return min(self.config.SKILLS_WEIGHT, score)
    
    def _score_description(self, job: Job) -> float:
        """
        Score based on description completeness (0-15 points).
        
        Longer, more detailed descriptions indicate serious postings.
        
        Args:
            job: Job entity
        
        Returns:
            Description score
        """
        description_length = len(job.description)
        
        if description_length >= self.config.DESCRIPTION_EXCELLENT_LENGTH:
            return self.config.DESCRIPTION_EXCELLENT_SCORE
        elif description_length >= self.config.DESCRIPTION_GOOD_LENGTH:
            return self.config.DESCRIPTION_GOOD_SCORE
        elif description_length >= self.config.DESCRIPTION_FAIR_LENGTH:
            return self.config.DESCRIPTION_FAIR_SCORE
        else:
            return 0.0
    
    def _score_company(self, job: Job) -> float:
        """
        Score based on company reputation (0-10 points).
        
        Known reputable companies get bonus points.
        
        Args:
            job: Job entity
        
        Returns:
            Company score
        """
        company_lower = job.company.lower()
        
        for known_company in self.config.KNOWN_COMPANIES:
            if known_company in company_lower:
                return self.config.COMPANY_WEIGHT
        
        return 0.0
    
    def score_with_breakdown(self, job: Job) -> dict:
        """
        Calculate score with detailed breakdown.
        
        Useful for debugging and explaining scores to users.
        
        Args:
            job: Job entity
        
        Returns:
            Dictionary with total score and breakdown
        """
        breakdown = {
            "salary": self._score_salary(job),
            "job_type": self._score_job_type(job),
            "remote": self._score_remote(job),
            "skills": self._score_skills(job),
            "description": self._score_description(job),
            "company": self._score_company(job),
        }
        
        total = sum(breakdown.values())
        
        return {
            "total_score": min(100.0, total),
            "breakdown": breakdown,
        }
