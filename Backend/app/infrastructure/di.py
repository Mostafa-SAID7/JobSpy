from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession

# Repositories
from app.infrastructure.persistence.sqlalchemy.repositories.job_repository_impl import JobRepositoryImpl
from app.infrastructure.persistence.sqlalchemy.repositories.user_repository_impl import UserRepositoryImpl
from app.infrastructure.persistence.sqlalchemy.repositories.saved_job_repository_impl import SavedJobRepositoryImpl
from app.infrastructure.persistence.sqlalchemy.repositories.alert_repository_impl import AlertRepositoryImpl
from app.infrastructure.persistence.sqlalchemy.repositories.stats_repository_impl import StatsRepositoryImpl
from app.infrastructure.persistence.sqlalchemy.repositories.search_history_repository_impl import SearchHistoryRepositoryImpl
from app.infrastructure.persistence.redis.cache_repository_impl import CacheRepositoryImpl

# Mappers
from app.infrastructure.persistence.sqlalchemy.mappers.job_orm_mapper import JobORMMapper

class InfrastructureContainer(containers.DeclarativeContainer):
    db_session = providers.Dependency(instance_of=AsyncSession)
    
    job_repository = providers.Factory(JobRepositoryImpl, session=db_session)
    user_repository = providers.Factory(UserRepositoryImpl, session=db_session)
    saved_job_repository = providers.Factory(SavedJobRepositoryImpl, session=db_session)
    alert_repository = providers.Factory(AlertRepositoryImpl, session=db_session)
    stats_repository = providers.Factory(StatsRepositoryImpl, session=db_session)
    search_history_repository = providers.Factory(SearchHistoryRepositoryImpl, session=db_session)
    
    cache_repository = providers.Singleton(CacheRepositoryImpl)
    job_orm_mapper = providers.Singleton(JobORMMapper)
