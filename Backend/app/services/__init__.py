"""
JobSpy Services
Business Logic Services Package

REFACTORED: Most services have been migrated to Clean Architecture.
- ScrapingService → ProcessScrapedJobsUseCase
- SearchService → SearchJobsUseCase, AdvancedSearchUseCase
- JobProcessingService → Deleted (logic moved to domain services and use cases)

Active Services:
- AlertService: Thin wrapper around use cases (for background jobs)
- EmailService: Email notification service
- StatsService: Statistics service (integrated with DI)
"""

from app.services.alert_service import AlertService
from app.services.email_service import EmailService
from app.services.stats_service import StatsService

__all__ = [
    "AlertService",
    "EmailService",
    "StatsService",
]
