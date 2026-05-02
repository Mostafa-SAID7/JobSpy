from dependency_injector import containers, providers

from app.application.mappers.job_mapper import JobMapper

from app.application.use_cases.jobs.create_job_use_case import CreateJobUseCase
from app.application.use_cases.jobs.get_job_details_use_case import GetJobDetailsUseCase
from app.application.use_cases.jobs.update_job_use_case import UpdateJobUseCase
from app.application.use_cases.jobs.delete_job_use_case import DeleteJobUseCase
from app.application.use_cases.jobs.list_jobs_use_case import ListJobsUseCase

from app.application.use_cases.search.search_jobs_use_case import SearchJobsUseCase
from app.application.use_cases.search.advanced_search_use_case import AdvancedSearchUseCase

from app.application.use_cases.scraping.process_scraped_jobs_use_case import ProcessScrapedJobsUseCase, ProcessingResult
from app.application.use_cases.scraping.scrape_jobs_use_case import ScrapeJobsUseCase, ScrapeJobsRequest

from app.application.use_cases.alert_processing.trigger_alert_use_case import TriggerAlertUseCase

from app.application.use_cases.auth.register_user_use_case import RegisterUserUseCase
from app.application.use_cases.auth.login_user_use_case import LoginUserUseCase
from app.application.use_cases.auth.refresh_token_use_case import RefreshTokenUseCase

from app.application.use_cases.saved_jobs.save_job_use_case import SaveJobUseCase
from app.application.use_cases.saved_jobs.list_saved_jobs_use_case import ListSavedJobsUseCase
from app.application.use_cases.saved_jobs.update_saved_job_use_case import UpdateSavedJobUseCase
from app.application.use_cases.saved_jobs.delete_saved_job_use_case import DeleteSavedJobUseCase
from app.application.use_cases.saved_jobs.unsave_job_use_case import UnsaveJobUseCase

from app.application.use_cases.alerts.create_alert_use_case import CreateAlertUseCase
from app.application.use_cases.alerts.get_alert_use_case import GetAlertUseCase
from app.application.use_cases.alerts.list_alerts_use_case import ListAlertsUseCase
from app.application.use_cases.alerts.update_alert_use_case import UpdateAlertUseCase
from app.application.use_cases.alerts.delete_alert_use_case import DeleteAlertUseCase

from app.application.use_cases.users.get_user_profile_use_case import GetUserProfileUseCase
from app.application.use_cases.users.update_user_profile_use_case import UpdateUserProfileUseCase
from app.application.use_cases.users.delete_user_account_use_case import DeleteUserAccountUseCase
from app.application.use_cases.users.change_password_use_case import ChangePasswordUseCase
from app.application.use_cases.users.verify_email_use_case import VerifyEmailUseCase
from app.application.use_cases.users.request_password_reset_use_case import RequestPasswordResetUseCase
from app.application.use_cases.users.confirm_password_reset_use_case import ConfirmPasswordResetUseCase
from app.application.use_cases.users.update_user_preferences_use_case import UpdateUserPreferencesUseCase
from app.application.use_cases.users.get_user_stats_use_case import GetUserStatsUseCase

from app.application.services.stats_service import StatsService

class ApplicationContainer(containers.DeclarativeContainer):
    infrastructure = providers.DependenciesContainer()
    domain = providers.DependenciesContainer()
    
    job_mapper = providers.Singleton(JobMapper)
    
    # Jobs
    create_job_use_case = providers.Factory(CreateJobUseCase, job_repository=infrastructure.job_repository, skill_service=domain.skill_extraction_service, job_mapper=job_mapper)
    get_job_details_use_case = providers.Factory(GetJobDetailsUseCase, job_repository=infrastructure.job_repository, cache_repository=infrastructure.cache_repository)
    update_job_use_case = providers.Factory(UpdateJobUseCase, job_repository=infrastructure.job_repository, cache_repository=infrastructure.cache_repository, scoring_service=domain.job_scoring_service)
    delete_job_use_case = providers.Factory(DeleteJobUseCase, job_repository=infrastructure.job_repository, cache_repository=infrastructure.cache_repository)
    list_jobs_use_case = providers.Factory(ListJobsUseCase, job_repository=infrastructure.job_repository, cache_repository=infrastructure.cache_repository)
    
    # Search
    search_jobs_use_case = providers.Factory(SearchJobsUseCase, job_repository=infrastructure.job_repository, cache_repository=infrastructure.cache_repository, scoring_service=domain.job_scoring_service)
    advanced_search_use_case = providers.Factory(AdvancedSearchUseCase, job_repository=infrastructure.job_repository, cache_repository=infrastructure.cache_repository, scoring_service=domain.job_scoring_service)
    
    # Scraping
    process_scraped_jobs_use_case = providers.Factory(
        ProcessScrapedJobsUseCase,
        job_repository=infrastructure.job_repository,
        cache_repository=infrastructure.cache_repository,
        scoring_service=domain.job_scoring_service,
        skill_service=domain.skill_extraction_service,
        job_mapper=job_mapper
    )
    scrape_jobs_use_case = providers.Factory(ScrapeJobsUseCase, scraper=infrastructure.jobspy_scraper, process_use_case=process_scraped_jobs_use_case)
    
    # Alert Processing
    trigger_alert_use_case = providers.Factory(TriggerAlertUseCase, alert_repository=infrastructure.alert_repository, job_repository=infrastructure.job_repository, filtering_service=domain.job_filtering_service)
    
    # Auth
    register_user_use_case = providers.Factory(RegisterUserUseCase, user_repository=infrastructure.user_repository)
    login_user_use_case = providers.Factory(LoginUserUseCase, user_repository=infrastructure.user_repository)
    refresh_token_use_case = providers.Factory(RefreshTokenUseCase)
    
    # Saved Jobs
    save_job_use_case = providers.Factory(SaveJobUseCase, saved_job_repository=infrastructure.saved_job_repository, job_repository=infrastructure.job_repository)
    list_saved_jobs_use_case = providers.Factory(ListSavedJobsUseCase, saved_job_repository=infrastructure.saved_job_repository)
    update_saved_job_use_case = providers.Factory(UpdateSavedJobUseCase, saved_job_repository=infrastructure.saved_job_repository)
    delete_saved_job_use_case = providers.Factory(DeleteSavedJobUseCase, saved_job_repository=infrastructure.saved_job_repository)
    unsave_job_use_case = providers.Factory(UnsaveJobUseCase, saved_job_repository=infrastructure.saved_job_repository)
    
    # Alerts
    create_alert_use_case = providers.Factory(CreateAlertUseCase, alert_repository=infrastructure.alert_repository)
    get_alert_use_case = providers.Factory(GetAlertUseCase, alert_repository=infrastructure.alert_repository)
    list_alerts_use_case = providers.Factory(ListAlertsUseCase, alert_repository=infrastructure.alert_repository)
    update_alert_use_case = providers.Factory(UpdateAlertUseCase, alert_repository=infrastructure.alert_repository)
    delete_alert_use_case = providers.Factory(DeleteAlertUseCase, alert_repository=infrastructure.alert_repository)
    
    # Users
    get_user_profile_use_case = providers.Factory(GetUserProfileUseCase, user_repository=infrastructure.user_repository)
    update_user_profile_use_case = providers.Factory(UpdateUserProfileUseCase, user_repository=infrastructure.user_repository)
    delete_user_account_use_case = providers.Factory(DeleteUserAccountUseCase, user_repository=infrastructure.user_repository)
    change_password_use_case = providers.Factory(ChangePasswordUseCase, user_repository=infrastructure.user_repository)
    verify_email_use_case = providers.Factory(VerifyEmailUseCase, user_repository=infrastructure.user_repository)
    request_password_reset_use_case = providers.Factory(RequestPasswordResetUseCase, user_repository=infrastructure.user_repository)
    confirm_password_reset_use_case = providers.Factory(ConfirmPasswordResetUseCase, user_repository=infrastructure.user_repository)
    update_user_preferences_use_case = providers.Factory(UpdateUserPreferencesUseCase, user_repository=infrastructure.user_repository)
    get_user_stats_use_case = providers.Factory(GetUserStatsUseCase, saved_job_repository=infrastructure.saved_job_repository, alert_repository=infrastructure.alert_repository, search_history_repository=infrastructure.search_history_repository)
    
    # Services
    stats_service = providers.Factory(StatsService, stats_repo=infrastructure.stats_repository)
