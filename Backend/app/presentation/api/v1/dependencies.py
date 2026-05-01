"""
Dependency Injection Container - JobSpy Backend

This module sets up the dependency injection container using dependency-injector.
It wires up all dependencies for the application following Clean Architecture principles.

Usage:
    from app.presentation.api.v1.dependencies import container
    
    # In FastAPI routes:
    @router.post("/jobs")
    @inject
    async def create_job(
        request: CreateJobRequest,
        use_case: CreateJobUseCase = Depends(Provide[Container.create_job_use_case]),
    ):
        return await use_case.execute(request)
"""
from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession

# Domain Services
from app.domain.services.job_scoring_service import JobScoringService
from app.domain.services.skill_extraction_service import SkillExtractionService
from app.domain.services.job_matching_service import JobMatchingService

# Infrastructure - Repositories
from app.infrastructure.persistence.sqlalchemy.repositories.job_repository_impl import JobRepositoryImpl
from app.infrastructure.persistence.redis.cache_repository_impl import CacheRepositoryImpl

# Infrastructure - Mappers
from app.infrastructure.persistence.sqlalchemy.mappers.job_orm_mapper import JobORMMapper

# Application - Mappers
from app.application.mappers.job_mapper import JobMapper

# Application - Use Cases - Jobs
from app.application.use_cases.jobs.create_job_use_case import CreateJobUseCase
from app.application.use_cases.jobs.get_job_details_use_case import GetJobDetailsUseCase
from app.application.use_cases.jobs.update_job_use_case import UpdateJobUseCase
from app.application.use_cases.jobs.delete_job_use_case import DeleteJobUseCase
from app.application.use_cases.jobs.list_jobs_use_case import ListJobsUseCase

# Application - Use Cases - Search
from app.application.use_cases.search.search_jobs_use_case import SearchJobsUseCase
from app.application.use_cases.search.advanced_search_use_case import AdvancedSearchUseCase

# Application - Use Cases - Scraping
from app.application.use_cases.scraping.process_scraped_jobs_use_case import ProcessScrapedJobsUseCase


class Container(containers.DeclarativeContainer):
    """
    Dependency Injection Container
    
    This container manages all application dependencies and their lifecycles.
    It follows the dependency inversion principle by injecting interfaces
    rather than concrete implementations.
    
    Lifecycle Scopes:
    - Singleton: Created once and reused (e.g., domain services, mappers)
    - Factory: Created new instance each time (e.g., use cases, repositories)
    """
    
    # Configuration
    config = providers.Configuration()
    
    # Database Session (injected from FastAPI dependency)
    db_session = providers.Dependency(instance_of=AsyncSession)
    
    # ========================================================================
    # INFRASTRUCTURE LAYER
    # ========================================================================
    
    # Repositories
    job_repository = providers.Factory(
        JobRepositoryImpl,
        session=db_session,
    )
    
    cache_repository = providers.Singleton(
        CacheRepositoryImpl,
    )
    
    # ORM Mappers
    job_orm_mapper = providers.Singleton(
        JobORMMapper,
    )
    
    # ========================================================================
    # DOMAIN LAYER
    # ========================================================================
    
    # Domain Services (Singleton - stateless, can be reused)
    job_scoring_service = providers.Singleton(
        JobScoringService,
    )
    
    skill_extraction_service = providers.Singleton(
        SkillExtractionService,
    )
    
    job_matching_service = providers.Singleton(
        JobMatchingService,
        scoring_service=job_scoring_service,
    )
    
    # ========================================================================
    # APPLICATION LAYER
    # ========================================================================
    
    # Application Mappers (Singleton - stateless)
    job_mapper = providers.Singleton(
        JobMapper,
        skill_service=skill_extraction_service,
    )
    
    # Use Cases - Jobs (Factory - new instance per request)
    create_job_use_case = providers.Factory(
        CreateJobUseCase,
        job_repository=job_repository,
        job_mapper=job_mapper,
        scoring_service=job_scoring_service,
    )
    
    get_job_details_use_case = providers.Factory(
        GetJobDetailsUseCase,
        job_repository=job_repository,
        cache_repository=cache_repository,
    )
    
    update_job_use_case = providers.Factory(
        UpdateJobUseCase,
        job_repository=job_repository,
        cache_repository=cache_repository,
        scoring_service=job_scoring_service,
    )
    
    delete_job_use_case = providers.Factory(
        DeleteJobUseCase,
        job_repository=job_repository,
        cache_repository=cache_repository,
    )
    
    list_jobs_use_case = providers.Factory(
        ListJobsUseCase,
        job_repository=job_repository,
        cache_repository=cache_repository,
    )
    
    # Use Cases - Search (Factory - new instance per request)
    search_jobs_use_case = providers.Factory(
        SearchJobsUseCase,
        job_repository=job_repository,
        cache_repository=cache_repository,
        scoring_service=job_scoring_service,
    )
    
    advanced_search_use_case = providers.Factory(
        AdvancedSearchUseCase,
        job_repository=job_repository,
        cache_repository=cache_repository,
        scoring_service=job_scoring_service,
        matching_service=job_matching_service,
    )
    
    # Use Cases - Scraping (Factory - new instance per request)
    process_scraped_jobs_use_case = providers.Factory(
        ProcessScrapedJobsUseCase,
        job_repository=job_repository,
        scoring_service=job_scoring_service,
        skill_service=skill_extraction_service,
        job_mapper=job_mapper,
    )


# Global container instance
container = Container()


def get_container() -> Container:
    """
    Get the global DI container instance.
    
    Returns:
        Container: The dependency injection container
    """
    return container


def wire_container(modules: list[str]) -> None:
    """
    Wire the container to specified modules.
    
    This enables @inject decorator to work in the specified modules.
    
    Args:
        modules: List of module paths to wire (e.g., ["app.routers.jobs"])
    """
    container.wire(modules=modules)


def reset_container() -> None:
    """
    Reset the container (useful for testing).
    """
    container.reset_singletons()
