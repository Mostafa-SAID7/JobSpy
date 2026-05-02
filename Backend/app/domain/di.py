from dependency_injector import containers, providers

from app.domain.services.job_scoring_service import JobScoringService
from app.domain.services.skill_extraction_service import SkillExtractionService
from app.domain.services.job_matching_service import JobMatchingService
from app.domain.services.job_filtering_service import JobFilteringService

class DomainContainer(containers.DeclarativeContainer):
    job_scoring_service = providers.Singleton(JobScoringService)
    skill_extraction_service = providers.Singleton(SkillExtractionService)
    job_matching_service = providers.Singleton(JobMatchingService, scoring_service=job_scoring_service)
    job_filtering_service = providers.Singleton(JobFilteringService)
