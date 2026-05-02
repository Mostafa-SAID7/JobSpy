"""
Job Filtering Service - Domain Layer

Pure domain service for filtering jobs based on criteria.
This is a single source of truth for all job filtering operations.
"""

from typing import List, Dict, Any


class JobFilteringService:
    """Domain service for filtering jobs based on various criteria."""

    @staticmethod
    def filter_jobs(
        jobs: List[Dict[str, Any]], 
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Filter jobs based on provided criteria.
        
        Single source of truth for all job filtering operations.
        Used by search, alerts, and any other filtering needs.
        
        Args:
            jobs: List of jobs to filter
            filters: Filter criteria (location, job_type, experience_level, salary_min, salary_max, etc.)
        
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
                if location in JobFilteringService._get_job_field(job, "location", "").lower()
            ]
        
        # Job type filter
        if filters.get("job_type"):
            job_type = filters["job_type"].lower()
            filtered = [
                job for job in filtered 
                if job_type in JobFilteringService._get_job_field(job, "job_type", "").lower()
            ]
        
        # Experience level filter
        if filters.get("experience_level"):
            exp_level = filters["experience_level"].lower()
            filtered = [
                job for job in filtered 
                if exp_level in JobFilteringService._get_job_field(job, "experience_level", "").lower()
            ]
        
        # Salary range filters
        if filters.get("salary_min"):
            min_salary = filters["salary_min"]
            filtered = [
                job for job in filtered 
                if JobFilteringService._get_job_field(job, "salary_max", 0) >= min_salary
            ]
        
        if filters.get("salary_max"):
            max_salary = filters["salary_max"]
            filtered = [
                job for job in filtered 
                if JobFilteringService._get_job_field(job, "salary_min", float('inf')) <= max_salary
            ]
        
        # Remote filter
        if filters.get("is_remote") is not None:
            is_remote = filters["is_remote"]
            filtered = [
                job for job in filtered 
                if JobFilteringService._get_job_field(job, "is_remote", False) == is_remote
            ]
        
        # Company filter
        if filters.get("company"):
            company = filters["company"].lower()
            filtered = [
                job for job in filtered 
                if company in JobFilteringService._get_job_field(job, "company", "").lower()
            ]
        
        # Date posted filter (days ago)
        if filters.get("days_ago"):
            from datetime import datetime, timedelta
            days_ago = filters["days_ago"]
            cutoff_date = datetime.utcnow() - timedelta(days=days_ago)
            filtered = [
                job for job in filtered 
                if JobFilteringService._get_job_field(job, "posted_date") and 
                   JobFilteringService._get_job_field(job, "posted_date") >= cutoff_date
            ]
        
        return filtered

    @staticmethod
    def _get_job_field(job: Dict[str, Any], field: str, default: Any = None) -> Any:
        """
        Safely get a field from a job dictionary.
        
        Handles both dict and object access patterns.
        
        Args:
            job: Job data (dict or object)
            field: Field name to retrieve
            default: Default value if field not found
        
        Returns:
            Field value or default
        """
        if isinstance(job, dict):
            return job.get(field, default)
        else:
            return getattr(job, field, default)
