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

# Scrapers
from app.infrastructure.scrapers.mock_scraper import MockScraper

# Optional: JobSpy scraper (requires python-jobspy package)
try:
    from app.infrastructure.scrapers.jobspy_scraper_impl import JobSpyLibraryScraper
    JOBSPY_AVAILABLE = True
except ImportError:
    JOBSPY_AVAILABLE = False
    JobSpyLibraryScraper = None

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
    
    # Scrapers
    mock_scraper = providers.Singleton(MockScraper)
    
    # Optional: JobSpy scraper (only if package is installed)
    if JOBSPY_AVAILABLE:
        jobspy_scraper = providers.Singleton(JobSpyLibraryScraper)
    else:
        jobspy_scraper = providers.Singleton(MockScraper)  # Fallback to mock scraper
