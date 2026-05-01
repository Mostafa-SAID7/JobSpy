"""
Repository Interfaces

Contracts for data persistence that infrastructure must implement.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from ..entities.job import Job


class IJobRepository(ABC):
    """
    Interface for job repository.
    
    Infrastructure layer must implement this interface.
    Domain layer depends on this abstraction, not concrete implementation.
    """
    
    @abstractmethod
    async def save(self, job: Job) -> Job:
        """
        Save a job.
        
        Args:
            job: Job entity to save
        
        Returns:
            Saved job entity
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, job_id: UUID) -> Optional[Job]:
        """
        Get job by ID.
        
        Args:
            job_id: Job ID
        
        Returns:
            Job entity or None if not found
        """
        pass
    
    @abstractmethod
    async def get_by_source_url(self, source_url: str) -> Optional[Job]:
        """
        Get job by source URL.
        
        Args:
            source_url: Source URL
        
        Returns:
            Job entity or None if not found
        """
        pass
    
    @abstractmethod
    async def exists_by_url(self, source_url: str) -> bool:
        """
        Check if job exists by source URL.
        
        Args:
            source_url: Source URL
        
        Returns:
            True if exists, False otherwise
        """
        pass
    
    @abstractmethod
    async def find_all(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Job]:
        """
        Find all jobs with pagination.
        
        Args:
            skip: Number of jobs to skip
            limit: Maximum number of jobs to return
        
        Returns:
            List of job entities
        """
        pass
    
    @abstractmethod
    async def find_by_source(
        self,
        source: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Job]:
        """
        Find jobs by source.
        
        Args:
            source: Job source (LinkedIn, Indeed, etc.)
            skip: Number of jobs to skip
            limit: Maximum number of jobs to return
        
        Returns:
            List of job entities
        """
        pass
    
    @abstractmethod
    async def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Job]:
        """
        Search jobs by query.
        
        Args:
            query: Search query
            skip: Number of jobs to skip
            limit: Maximum number of jobs to return
        
        Returns:
            List of job entities
        """
        pass
    
    @abstractmethod
    async def update(self, job: Job) -> Job:
        """
        Update a job.
        
        Args:
            job: Job entity to update
        
        Returns:
            Updated job entity
        """
        pass
    
    @abstractmethod
    async def delete(self, job_id: UUID) -> bool:
        """
        Delete a job.
        
        Args:
            job_id: Job ID
        
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    async def count(self) -> int:
        """
        Count total jobs.
        
        Returns:
            Total number of jobs
        """
        pass


class IUserRepository(ABC):
    """Interface for user repository"""
    
    # To be implemented when refactoring user management
    pass


class IAlertRepository(ABC):
    """Interface for alert repository"""
    
    # To be implemented when refactoring alert management
    pass
