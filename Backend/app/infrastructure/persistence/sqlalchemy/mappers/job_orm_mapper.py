"""
Job ORM Mapper

Converts between ORM Job model and domain Job entity.
"""

import logging
from decimal import Decimal
from typing import Optional

from app.models.job import Job as JobModel  # ORM model
from app.domain.entities.job import Job as JobEntity  # Domain entity
from app.domain.value_objects.salary import Salary
from app.domain.value_objects.location import Location, RemoteType
from app.domain.value_objects.job_type import JobType
from app.domain.value_objects.experience_level import ExperienceLevel

logger = logging.getLogger(__name__)


class JobORMMapper:
    """
    Mapper for converting between ORM Job model and domain Job entity.
    
    Responsibilities:
    - ORM Model → Domain Entity (to_domain)
    - Domain Entity → ORM Model (to_orm)
    - Handle all type conversions
    - Handle value object creation
    """
    
    @staticmethod
    def to_domain(orm_model: JobModel) -> JobEntity:
        """
        Convert ORM model to domain entity.
        
        Args:
            orm_model: SQLAlchemy Job model
        
        Returns:
            Domain Job entity
        """
        try:
            # Parse salary
            salary = None
            if orm_model.salary_min is not None or orm_model.salary_max is not None:
                salary = Salary.from_range(
                    orm_model.salary_min,
                    orm_model.salary_max,
                    orm_model.salary_currency or "USD"
                )
            
            # Parse location
            remote_type = RemoteType.from_int(orm_model.is_remote or 0)
            location = Location.from_string(
                orm_model.location or "",
                remote_type
            )
            
            # Parse job type
            job_type = JobType.from_string(orm_model.job_type)
            
            # Parse experience level
            experience_level = ExperienceLevel.from_string(orm_model.experience_level)
            
            # Create domain entity
            entity = JobEntity(
                id=orm_model.id,
                title=orm_model.title,
                company=orm_model.company,
                location=location,
                description=orm_model.description or "",
                job_type=job_type,
                experience_level=experience_level,
                salary=salary,
                requirements=orm_model.requirements or [],
                skills=orm_model.skills or [],
                benefits=orm_model.benefits or [],
                source=orm_model.source,
                source_url=orm_model.source_url,
                source_job_id=orm_model.source_job_id,
                posted_date=orm_model.posted_date,
                deadline=orm_model.deadline,
                company_logo_url=orm_model.company_logo_url,
                company_website=orm_model.company_website,
                view_count=orm_model.view_count or 0,
                apply_count=orm_model.apply_count or 0,
                created_at=orm_model.created_at,
                updated_at=orm_model.updated_at,
                scraped_at=orm_model.scraped_at,
            )
            
            return entity
            
        except Exception as e:
            logger.error(f"Error converting ORM to domain: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to convert ORM model to domain entity: {str(e)}")
    
    @staticmethod
    def to_orm(entity: JobEntity, orm_model: Optional[JobModel] = None) -> JobModel:
        """
        Convert domain entity to ORM model.
        
        Args:
            entity: Domain Job entity
            orm_model: Existing ORM model to update (creates new if None)
        
        Returns:
            SQLAlchemy Job model
        """
        try:
            # Create new or update existing
            if orm_model is None:
                orm_model = JobModel()
            
            # Map basic fields
            orm_model.id = entity.id
            orm_model.title = entity.title
            orm_model.company = entity.company
            orm_model.location = entity.location.full_address or entity.location.format()
            orm_model.description = entity.description
            orm_model.source = entity.source
            orm_model.source_url = entity.source_url
            orm_model.source_job_id = entity.source_job_id
            orm_model.posted_date = entity.posted_date
            orm_model.deadline = entity.deadline
            orm_model.company_logo_url = entity.company_logo_url
            orm_model.company_website = entity.company_website
            orm_model.view_count = entity.view_count
            orm_model.apply_count = entity.apply_count
            orm_model.created_at = entity.created_at
            orm_model.updated_at = entity.updated_at
            orm_model.scraped_at = entity.scraped_at
            
            # Map value objects
            
            # Salary
            if entity.salary:
                orm_model.salary_min = float(entity.salary.min_amount) if entity.salary.min_amount else None
                orm_model.salary_max = float(entity.salary.max_amount) if entity.salary.max_amount else None
                orm_model.salary_currency = entity.salary.currency
            else:
                orm_model.salary_min = None
                orm_model.salary_max = None
                orm_model.salary_currency = None
            
            # Job type
            orm_model.job_type = entity.job_type.value
            
            # Experience level
            orm_model.experience_level = entity.experience_level.value
            
            # Remote type
            orm_model.is_remote = entity.location.remote_type.value
            
            # Lists
            orm_model.requirements = entity.requirements
            orm_model.skills = entity.skills
            orm_model.benefits = entity.benefits
            
            return orm_model
            
        except Exception as e:
            logger.error(f"Error converting domain to ORM: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to convert domain entity to ORM model: {str(e)}")
    
    @staticmethod
    def update_orm_from_entity(orm_model: JobModel, entity: JobEntity) -> JobModel:
        """
        Update existing ORM model from domain entity.
        
        Useful for updates where you want to preserve ORM relationships.
        
        Args:
            orm_model: Existing ORM model
            entity: Domain entity with updated data
        
        Returns:
            Updated ORM model
        """
        return JobORMMapper.to_orm(entity, orm_model)
