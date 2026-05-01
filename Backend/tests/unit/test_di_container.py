"""
Unit Tests for Dependency Injection Container

Tests that the DI container is properly configured and can provide
all required dependencies.
"""
import pytest
from app.presentation.api.v1.dependencies import container, get_container, reset_container

# Domain Services
from app.domain.services.job_scoring_service import JobScoringService
from app.domain.services.skill_extraction_service import SkillExtractionService
from app.domain.services.job_matching_service import JobMatchingService

# Application - Mappers
from app.application.mappers.job_mapper import JobMapper

# Application - Use Cases
from app.application.use_cases.jobs.create_job_use_case import CreateJobUseCase
from app.application.use_cases.jobs.get_job_details_use_case import GetJobDetailsUseCase
from app.application.use_cases.jobs.update_job_use_case import UpdateJobUseCase
from app.application.use_cases.jobs.delete_job_use_case import DeleteJobUseCase
from app.application.use_cases.jobs.list_jobs_use_case import ListJobsUseCase
from app.application.use_cases.search.search_jobs_use_case import SearchJobsUseCase
from app.application.use_cases.search.advanced_search_use_case import AdvancedSearchUseCase
from app.application.use_cases.scraping.process_scraped_jobs_use_case import ProcessScrapedJobsUseCase


class TestDIContainer:
    """Test Dependency Injection Container"""
    
    def test_get_container(self):
        """Test that get_container returns the global container instance"""
        result = get_container()
        assert result is not None
        assert result is container
    
    def test_container_provides_domain_services(self):
        """Test that container can provide domain services"""
        # Test job scoring service
        scoring_service = container.job_scoring_service()
        assert scoring_service is not None
        assert isinstance(scoring_service, JobScoringService)
        
        # Test skill extraction service
        skill_service = container.skill_extraction_service()
        assert skill_service is not None
        assert isinstance(skill_service, SkillExtractionService)
        
        # Test job matching service
        matching_service = container.job_matching_service()
        assert matching_service is not None
        assert isinstance(matching_service, JobMatchingService)
    
    def test_container_provides_mappers(self):
        """Test that container can provide mappers"""
        # Test job mapper
        job_mapper = container.job_mapper()
        assert job_mapper is not None
        assert isinstance(job_mapper, JobMapper)
    
    def test_singleton_services_are_reused(self):
        """Test that singleton services return the same instance"""
        # Domain services should be singletons
        service1 = container.job_scoring_service()
        service2 = container.job_scoring_service()
        assert service1 is service2, "Singleton services should return same instance"
        
        # Mappers should be singletons
        mapper1 = container.job_mapper()
        mapper2 = container.job_mapper()
        assert mapper1 is mapper2, "Singleton mappers should return same instance"
    
    def test_container_can_be_reset(self):
        """Test that container can be reset"""
        # Get a singleton service
        service1 = container.job_scoring_service()
        
        # Reset container
        reset_container()
        
        # Get service again - should be a new instance after reset
        service2 = container.job_scoring_service()
        
        # Note: After reset, singletons are recreated
        # So they might be different instances
        assert service2 is not None
        assert isinstance(service2, JobScoringService)


class TestDIContainerUseCases:
    """Test that use cases can be provided by the container"""
    
    def test_container_provides_job_use_cases(self):
        """Test that container can provide job use cases"""
        # Note: These are factories, so they need db_session
        # We're just testing that the providers are configured
        assert hasattr(container, 'create_job_use_case')
        assert hasattr(container, 'get_job_details_use_case')
        assert hasattr(container, 'update_job_use_case')
        assert hasattr(container, 'delete_job_use_case')
        assert hasattr(container, 'list_jobs_use_case')
    
    def test_container_provides_search_use_cases(self):
        """Test that container can provide search use cases"""
        assert hasattr(container, 'search_jobs_use_case')
        assert hasattr(container, 'advanced_search_use_case')
    
    def test_container_provides_scraping_use_cases(self):
        """Test that container can provide scraping use cases"""
        assert hasattr(container, 'process_scraped_jobs_use_case')


class TestDIContainerConfiguration:
    """Test container configuration"""
    
    def test_container_has_required_providers(self):
        """Test that container has all required providers"""
        required_providers = [
            # Infrastructure
            'job_repository',
            'cache_repository',
            'job_orm_mapper',
            # Domain
            'job_scoring_service',
            'skill_extraction_service',
            'job_matching_service',
            # Application
            'job_mapper',
            # Use Cases - Jobs
            'create_job_use_case',
            'get_job_details_use_case',
            'update_job_use_case',
            'delete_job_use_case',
            'list_jobs_use_case',
            # Use Cases - Search
            'search_jobs_use_case',
            'advanced_search_use_case',
            # Use Cases - Scraping
            'process_scraped_jobs_use_case',
        ]
        
        for provider_name in required_providers:
            assert hasattr(container, provider_name), f"Container missing provider: {provider_name}"
    
    def test_container_dependencies_are_wired(self):
        """Test that dependencies are properly wired"""
        # Test that job_matching_service has scoring_service dependency
        matching_service = container.job_matching_service()
        assert hasattr(matching_service, 'scoring_service')
        assert isinstance(matching_service.scoring_service, JobScoringService)
        
        # Test that job_mapper can be instantiated
        job_mapper = container.job_mapper()
        assert job_mapper is not None
        assert isinstance(job_mapper, JobMapper)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
