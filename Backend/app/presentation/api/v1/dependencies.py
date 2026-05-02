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

# Application - Use Cases - Auth
from app.application.use_cases.auth.register_user_use_case import RegisterUserUseCase
from app.application.use_cases.auth.login_user_use_case import LoginUserUseCase
from app.application.use_cases.auth.refresh_token_use_case import RefreshTokenUseCase

# Application - Use Cases - Saved Jobs
from app.application.use_cases.saved_jobs.save_job_use_case import SaveJobUseCase
from app.application.use_cases.saved_jobs.list_saved_jobs_use_case import ListSavedJobsUseCase
from app.application.use_cases.saved_jobs.update_saved_job_use_case import UpdateSavedJobUseCase
from app.application.use_cases.saved_jobs.delete_saved_job_use_case import DeleteSavedJobUseCase
from app.application.use_cases.saved_jobs.unsave_job_use_case import UnsaveJobUseCase

# Application - Use Cases - Alerts
from app.application.use_cases.alerts.create_alert_use_case import CreateAlertUseCase
from app.application.use_cases.alerts.get_alert_use_case import GetAlertUseCase
from app.application.use_cases.alerts.list_alerts_use_case import ListAlertsUseCase
from app.application.use_cases.alerts.update_alert_use_case import UpdateAlertUseCase
from app.application.use_cases.alerts.delete_alert_use_case import DeleteAlertUseCase

# Application - Use Cases - Users
from app.application.use_cases.users.get_user_profile_use_case import GetUserProfileUseCase
from app.application.use_cases.users.update_user_profile_use_case import UpdateUserProfileUseCase
from app.application.use_cases.users.delete_user_account_use_case import DeleteUserAccountUseCase
from app.application.use_cases.users.change_password_use_case import ChangePasswordUseCase
from app.application.use_cases.users.verify_email_use_case import VerifyEmailUseCase
from app.application.use_cases.users.request_password_reset_use_case import RequestPasswordResetUseCase
from app.application.use_cases.users.confirm_password_reset_use_case import ConfirmPasswordResetUseCase
from app.application.use_cases.users.update_user_preferences_use_case import UpdateUserPreferencesUseCase
from app.application.use_cases.users.get_user_stats_use_case import GetUserStatsUseCase

# Repositories
from app.repositories.user_repo import UserRepository
from app.repositories.saved_job_repo import SavedJobRepository
from app.repositories.alert_repo import AlertRepository
from app.repositories.stats_repo import StatsRepository
from app.repositories.search_history_repo import SearchHistoryRepository

# Services
from app.services.stats_service import StatsService


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
    
    user_repository = providers.Factory(
        UserRepository,
        session=db_session,
    )
    
    saved_job_repository = providers.Factory(
        SavedJobRepository,
        session=db_session,
    )
    
    alert_repository = providers.Factory(
        AlertRepository,
        session=db_session,
    )
    
    stats_repository = providers.Factory(
        StatsRepository,
        session=db_session,
    )
    
    search_history_repository = providers.Factory(
        SearchHistoryRepository,
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
    
    # Use Cases - Auth (Factory - new instance per request)
    register_user_use_case = providers.Factory(
        RegisterUserUseCase,
        user_repository=user_repository,
    )
    
    login_user_use_case = providers.Factory(
        LoginUserUseCase,
        user_repository=user_repository,
    )
    
    refresh_token_use_case = providers.Factory(
        RefreshTokenUseCase,
    )
    
    # Use Cases - Saved Jobs (Factory - new instance per request)
    save_job_use_case = providers.Factory(
        SaveJobUseCase,
        saved_job_repository=saved_job_repository,
        job_repository=job_repository,
    )
    
    list_saved_jobs_use_case = providers.Factory(
        ListSavedJobsUseCase,
        saved_job_repository=saved_job_repository,
    )
    
    update_saved_job_use_case = providers.Factory(
        UpdateSavedJobUseCase,
        saved_job_repository=saved_job_repository,
    )
    
    delete_saved_job_use_case = providers.Factory(
        DeleteSavedJobUseCase,
        saved_job_repository=saved_job_repository,
    )
    
    unsave_job_use_case = providers.Factory(
        UnsaveJobUseCase,
        saved_job_repository=saved_job_repository,
    )
    
    # Use Cases - Alerts (Factory - new instance per request)
    create_alert_use_case = providers.Factory(
        CreateAlertUseCase,
        alert_repository=alert_repository,
    )
    
    get_alert_use_case = providers.Factory(
        GetAlertUseCase,
        alert_repository=alert_repository,
    )
    
    list_alerts_use_case = providers.Factory(
        ListAlertsUseCase,
        alert_repository=alert_repository,
    )
    
    update_alert_use_case = providers.Factory(
        UpdateAlertUseCase,
        alert_repository=alert_repository,
    )
    
    delete_alert_use_case = providers.Factory(
        DeleteAlertUseCase,
        alert_repository=alert_repository,
    )
    
    # Use Cases - Users (Factory - new instance per request)
    get_user_profile_use_case = providers.Factory(
        GetUserProfileUseCase,
        user_repository=user_repository,
    )
    
    update_user_profile_use_case = providers.Factory(
        UpdateUserProfileUseCase,
        user_repository=user_repository,
    )
    
    delete_user_account_use_case = providers.Factory(
        DeleteUserAccountUseCase,
        user_repository=user_repository,
    )
    
    change_password_use_case = providers.Factory(
        ChangePasswordUseCase,
        user_repository=user_repository,
    )
    
    verify_email_use_case = providers.Factory(
        VerifyEmailUseCase,
        user_repository=user_repository,
    )
    
    request_password_reset_use_case = providers.Factory(
        RequestPasswordResetUseCase,
        user_repository=user_repository,
    )
    
    confirm_password_reset_use_case = providers.Factory(
        ConfirmPasswordResetUseCase,
        user_repository=user_repository,
    )
    
    update_user_preferences_use_case = providers.Factory(
        UpdateUserPreferencesUseCase,
        user_repository=user_repository,
    )
    
    get_user_stats_use_case = providers.Factory(
        GetUserStatsUseCase,
        saved_job_repository=saved_job_repository,
        alert_repository=alert_repository,
        search_history_repository=search_history_repository,
    )
    
    # ========================================================================
    # SERVICES LAYER
    # ========================================================================
    
    # Stats Service (Factory - new instance per request)
    stats_service = providers.Factory(
        StatsService,
        stats_repo=stats_repository,
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
