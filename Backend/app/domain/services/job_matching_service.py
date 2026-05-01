"""
Job Matching Service

Domain service for matching jobs to user profiles.
Single responsibility: job-user matching algorithm.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional

from ..entities.job import Job
from .job_scoring_service import JobScoringService


@dataclass
class UserProfile:
    """
    User profile for job matching.
    
    This is a simplified profile focused on job matching.
    Full user entity would be in domain/entities/user.py
    """
    
    skills: List[str]
    preferred_locations: List[str]
    expected_salary: Optional[Decimal]
    prefers_remote: bool
    preferred_job_types: List[str]
    experience_years: int


class JobMatchingService:
    """
    Domain service for matching jobs to user profiles.
    
    Single Responsibility: Calculate job-user match scores.
    
    Match score breakdown (0-100 points):
    - Base job score: 0-50 points (from JobScoringService)
    - Skill match: 0-30 points
    - Location match: 0-10 points
    - Salary match: 0-20 points
    - Remote preference: 0-10 points (bonus)
    - Job type preference: 0-10 points (bonus)
    """
    
    def __init__(self, scoring_service: JobScoringService = None):
        """
        Initialize matching service.
        
        Args:
            scoring_service: Job scoring service (creates default if not provided)
        """
        self.scoring_service = scoring_service or JobScoringService()
    
    def calculate_match_score(
        self,
        job: Job,
        user_profile: UserProfile
    ) -> float:
        """
        Calculate job-user match score.
        
        Args:
            job: Job entity
            user_profile: User profile
        
        Returns:
            Match score from 0.0 to 100.0
        """
        # Start with base job score (scaled to 50 points)
        base_score = self.scoring_service.calculate_score(job) * 0.5
        
        # Add match bonuses
        skill_bonus = self._calculate_skill_match(job, user_profile)
        location_bonus = self._calculate_location_match(job, user_profile)
        salary_bonus = self._calculate_salary_match(job, user_profile)
        remote_bonus = self._calculate_remote_match(job, user_profile)
        job_type_bonus = self._calculate_job_type_match(job, user_profile)
        
        total_score = (
            base_score +
            skill_bonus +
            location_bonus +
            salary_bonus +
            remote_bonus +
            job_type_bonus
        )
        
        return min(100.0, total_score)
    
    def _calculate_skill_match(
        self,
        job: Job,
        user_profile: UserProfile
    ) -> float:
        """
        Calculate skill match bonus (0-30 points).
        
        Args:
            job: Job entity
            user_profile: User profile
        
        Returns:
            Skill match score
        """
        if not user_profile.skills or not job.skills:
            return 0.0
        
        user_skills_set = {skill.lower() for skill in user_profile.skills}
        job_skills_set = {skill.lower() for skill in job.skills}
        
        matching_skills = user_skills_set.intersection(job_skills_set)
        
        if not job_skills_set:
            return 0.0
        
        # Calculate match ratio
        match_ratio = len(matching_skills) / len(job_skills_set)
        
        return match_ratio * 30.0
    
    def _calculate_location_match(
        self,
        job: Job,
        user_profile: UserProfile
    ) -> float:
        """
        Calculate location match bonus (0-10 points).
        
        Args:
            job: Job entity
            user_profile: User profile
        
        Returns:
            Location match score
        """
        if not user_profile.preferred_locations:
            return 5.0  # Neutral score if no preference
        
        job_location_str = job.location.format().lower()
        
        for preferred_location in user_profile.preferred_locations:
            if preferred_location.lower() in job_location_str:
                return 10.0
        
        return 0.0
    
    def _calculate_salary_match(
        self,
        job: Job,
        user_profile: UserProfile
    ) -> float:
        """
        Calculate salary match bonus (0-20 points).
        
        Args:
            job: Job entity
            user_profile: User profile
        
        Returns:
            Salary match score
        """
        if not user_profile.expected_salary:
            return 10.0  # Neutral score if no expectation
        
        if not job.salary or not job.salary.max_amount:
            return 0.0
        
        expected = user_profile.expected_salary
        offered = job.salary.max_amount
        
        # Perfect match or better
        if offered >= expected:
            return 20.0
        
        # Close match (80-99% of expected)
        if offered >= expected * Decimal("0.8"):
            return 15.0
        
        # Acceptable match (60-79% of expected)
        if offered >= expected * Decimal("0.6"):
            return 10.0
        
        # Below expectations
        return 0.0
    
    def _calculate_remote_match(
        self,
        job: Job,
        user_profile: UserProfile
    ) -> float:
        """
        Calculate remote work preference match (0-10 points bonus).
        
        Args:
            job: Job entity
            user_profile: User profile
        
        Returns:
            Remote match score
        """
        if user_profile.prefers_remote:
            if job.is_remote():
                return 10.0
            elif job.is_hybrid():
                return 7.0
            else:
                return 0.0
        else:
            # User doesn't prefer remote, so any option is fine
            return 5.0
    
    def _calculate_job_type_match(
        self,
        job: Job,
        user_profile: UserProfile
    ) -> float:
        """
        Calculate job type preference match (0-10 points bonus).
        
        Args:
            job: Job entity
            user_profile: User profile
        
        Returns:
            Job type match score
        """
        if not user_profile.preferred_job_types:
            return 5.0  # Neutral score if no preference
        
        job_type_str = job.job_type.value.lower()
        
        for preferred_type in user_profile.preferred_job_types:
            if preferred_type.lower() in job_type_str:
                return 10.0
        
        return 0.0
    
    def match_with_breakdown(
        self,
        job: Job,
        user_profile: UserProfile
    ) -> dict:
        """
        Calculate match score with detailed breakdown.
        
        Useful for explaining match scores to users.
        
        Args:
            job: Job entity
            user_profile: User profile
        
        Returns:
            Dictionary with total score and breakdown
        """
        base_score = self.scoring_service.calculate_score(job) * 0.5
        
        breakdown = {
            "base_score": base_score,
            "skill_match": self._calculate_skill_match(job, user_profile),
            "location_match": self._calculate_location_match(job, user_profile),
            "salary_match": self._calculate_salary_match(job, user_profile),
            "remote_match": self._calculate_remote_match(job, user_profile),
            "job_type_match": self._calculate_job_type_match(job, user_profile),
        }
        
        total = sum(breakdown.values())
        
        return {
            "total_score": min(100.0, total),
            "breakdown": breakdown,
            "recommendation": self._get_recommendation(total),
        }
    
    def _get_recommendation(self, score: float) -> str:
        """
        Get recommendation based on match score.
        
        Args:
            score: Match score
        
        Returns:
            Recommendation string
        """
        if score >= 80:
            return "Excellent match - Highly recommended"
        elif score >= 60:
            return "Good match - Worth applying"
        elif score >= 40:
            return "Fair match - Consider if interested"
        else:
            return "Low match - May not be ideal"
    
    def rank_jobs(
        self,
        jobs: List[Job],
        user_profile: UserProfile
    ) -> List[tuple[Job, float]]:
        """
        Rank jobs by match score.
        
        Args:
            jobs: List of job entities
            user_profile: User profile
        
        Returns:
            List of (job, score) tuples sorted by score (highest first)
        """
        scored_jobs = [
            (job, self.calculate_match_score(job, user_profile))
            for job in jobs
        ]
        
        # Sort by score descending
        scored_jobs.sort(key=lambda x: x[1], reverse=True)
        
        return scored_jobs
