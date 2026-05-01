"""
Job Repository Implementation

Implements IJobRepository interface using SQLAlchemy.
NO caching logic here - that's handled by use cases with ICacheRepository.
"""

import logging
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from app.domain.entities.job import Job as JobEntity
from app.domain.interfaces.repositories import IJobRepository
from app.models.job import Job as JobModel
from app.infrastructure.persistence.sqlalchemy.mappers.job_orm_mapper import JobORMMapper

logger = logging.getLogger(__name__)


class JobRepositoryImpl(IJobRepository):
    """
    SQLAlchemy implementation of IJobRepository.
    
    Responsibilities:
    - Implement domain repository interface
    - Convert between ORM and domain using mapper
    - Handle database operations
    - NO caching (that's in use cases)
    - NO business logic (that's in domain)
    """
    
    def __init__(self, session: AsyncSession):
        """
        Initialize repository.
        
        Args:
            session: SQLAlchemy async session
        """
        self.session = session
        self.mapper = JobORMMapper()
    
    async def save(self, job: JobEntity) -> JobEntity:
        """
        Save a job.
        
        Args:
            job: Job entity to save
        
        Returns:
            Saved job entity
        
        Raises:
            ValueError: If job with same source_url already exists
        """
        try:
            # Convert domain entity to ORM model
            orm_model = self.mapper.to_orm(job)
            
            # Add to session
            self.session.add(orm_model)
            await self.session.flush()
            
            # Convert back to domain entity
            saved_entity = self.mapper.to_domain(orm_model)
            
            logger.debug(f"Job saved: {saved_entity.id}")
            
            return saved_entity
            
        except IntegrityError as e:
            await self.session.rollback()
            logger.error(f"Integrity error saving job: {str(e)}")
            raise ValueError(f"Job with source_url {job.source_url} already exists")
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error saving job: {str(e)}", exc_info=True)
            raise
    
    async def get_by_id(self, job_id: UUID) -> Optional[JobEntity]:
        """
        Get job by ID.
        
        Args:
            job_id: Job ID
        
        Returns:
            Job entity or None if not found
        """
        try:
            result = await self.session.execute(
                select(JobModel).where(JobModel.id == job_id)
            )
            orm_model = result.scalar_one_or_none()
            
            if orm_model is None:
                return None
            
            return self.mapper.to_domain(orm_model)
            
        except Exception as e:
            logger.error(f"Error getting job by ID {job_id}: {str(e)}")
            return None
    
    async def get_by_source_url(self, source_url: str) -> Optional[JobEntity]:
        """
        Get job by source URL.
        
        Args:
            source_url: Source URL
        
        Returns:
            Job entity or None if not found
        """
        try:
            result = await self.session.execute(
                select(JobModel).where(JobModel.source_url == source_url)
            )
            orm_model = result.scalar_one_or_none()
            
            if orm_model is None:
                return None
            
            return self.mapper.to_domain(orm_model)
            
        except Exception as e:
            logger.error(f"Error getting job by source URL: {str(e)}")
            return None
    
    async def exists_by_url(self, source_url: str) -> bool:
        """
        Check if job exists by source URL.
        
        Args:
            source_url: Source URL
        
        Returns:
            True if exists, False otherwise
        """
        try:
            result = await self.session.execute(
                select(JobModel.id).where(JobModel.source_url == source_url)
            )
            return result.scalar_one_or_none() is not None
            
        except Exception as e:
            logger.error(f"Error checking job existence: {str(e)}")
            return False
    
    async def find_all(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[JobEntity]:
        """
        Find all jobs with pagination.
        
        Args:
            skip: Number of jobs to skip
            limit: Maximum number of jobs to return
        
        Returns:
            List of job entities
        """
        try:
            result = await self.session.execute(
                select(JobModel)
                .offset(skip)
                .limit(limit)
                .order_by(JobModel.created_at.desc())
            )
            orm_models = result.scalars().all()
            
            return [self.mapper.to_domain(model) for model in orm_models]
            
        except Exception as e:
            logger.error(f"Error finding all jobs: {str(e)}")
            return []
    
    async def find_by_source(
        self,
        source: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[JobEntity]:
        """
        Find jobs by source.
        
        Args:
            source: Job source (LinkedIn, Indeed, etc.)
            skip: Number of jobs to skip
            limit: Maximum number of jobs to return
        
        Returns:
            List of job entities
        """
        try:
            result = await self.session.execute(
                select(JobModel)
                .where(JobModel.source == source)
                .offset(skip)
                .limit(limit)
                .order_by(JobModel.created_at.desc())
            )
            orm_models = result.scalars().all()
            
            return [self.mapper.to_domain(model) for model in orm_models]
            
        except Exception as e:
            logger.error(f"Error finding jobs by source: {str(e)}")
            return []
    
    async def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[JobEntity]:
        """
        Search jobs by query.
        
        Args:
            query: Search query
            skip: Number of jobs to skip
            limit: Maximum number of jobs to return
        
        Returns:
            List of job entities
        """
        try:
            result = await self.session.execute(
                select(JobModel)
                .where(
                    (JobModel.title.ilike(f"%{query}%")) |
                    (JobModel.description.ilike(f"%{query}%"))
                )
                .offset(skip)
                .limit(limit)
                .order_by(JobModel.created_at.desc())
            )
            orm_models = result.scalars().all()
            
            return [self.mapper.to_domain(model) for model in orm_models]
            
        except Exception as e:
            logger.error(f"Error searching jobs: {str(e)}")
            return []
    
    async def update(self, job: JobEntity) -> JobEntity:
        """
        Update a job.
        
        Args:
            job: Job entity to update
        
        Returns:
            Updated job entity
        """
        try:
            # Get existing ORM model
            result = await self.session.execute(
                select(JobModel).where(JobModel.id == job.id)
            )
            orm_model = result.scalar_one_or_none()
            
            if orm_model is None:
                raise ValueError(f"Job not found: {job.id}")
            
            # Update ORM model from entity
            orm_model = self.mapper.update_orm_from_entity(orm_model, job)
            
            # Flush changes
            await self.session.flush()
            
            # Convert back to domain entity
            updated_entity = self.mapper.to_domain(orm_model)
            
            logger.debug(f"Job updated: {updated_entity.id}")
            
            return updated_entity
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating job: {str(e)}", exc_info=True)
            raise
    
    async def delete(self, job_id: UUID) -> bool:
        """
        Delete a job.
        
        Args:
            job_id: Job ID
        
        Returns:
            True if deleted, False if not found
        """
        try:
            result = await self.session.execute(
                select(JobModel).where(JobModel.id == job_id)
            )
            orm_model = result.scalar_one_or_none()
            
            if orm_model is None:
                return False
            
            await self.session.delete(orm_model)
            await self.session.flush()
            
            logger.debug(f"Job deleted: {job_id}")
            
            return True
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error deleting job: {str(e)}")
            return False
    
    async def count(self) -> int:
        """
        Count total jobs.
        
        Returns:
            Total number of jobs
        """
        try:
            result = await self.session.execute(select(JobModel))
            jobs = result.scalars().all()
            return len(jobs)
            
        except Exception as e:
            logger.error(f"Error counting jobs: {str(e)}")
            return 0
