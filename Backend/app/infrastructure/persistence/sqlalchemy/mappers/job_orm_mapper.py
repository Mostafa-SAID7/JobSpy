"""
Job ORM Mapper (Infrastructure Layer)

Thin re-export wrapper — delegates to JobMapper.
The original job_orm_mapper.py imported the legacy app.models.job (which causes
duplicate table registration). This version uses the proper infrastructure model.
"""

from app.infrastructure.persistence.sqlalchemy.mappers.job_mapper import JobMapper

# Alias for backward compatibility in the DI container
JobORMMapper = JobMapper
