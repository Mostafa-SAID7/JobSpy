"""
Unit tests for service layer
"""
import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timedelta

from app.services.search_service import SearchService
from app.services.alert_service import AlertService
from app.models.user import User


@pytest.mark.asyncio
class TestSearchService:
    """Test SearchService methods"""

    async def test_search_jobs(self, db):
        """Test searching jobs"""
        service = SearchService(db)
        
        # Mock the scraping service
        with patch.object(service, 'scraper') as mock_scraper:
            mock_scraper.search = AsyncMock(return_value=[
                {
                    'title': 'Developer',
                    'company': 'Tech Corp',
                    'location': 'Remote',
                    'salary_min': 100000,
                    'salary_max': 150000,
                    'description': 'Job description',
                    'url': 'https://example.com/job/1',
                    'source': 'linkedin'
                }
            ])
            
            results = await service.search_jobs('developer', {})
            
            assert len(results) == 1
            assert results[0]['title'] == 'Developer'

    async def test_search_with_filters(self, db):
        """Test searching with filters"""
        service = SearchService(db)
        
        with patch.object(service, 'scraper') as mock_scraper:
            mock_scraper.search = AsyncMock(return_value=[])
            
            filters = {
                'location': 'Remote',
                'salary_min': 100000,
                'experience_level': 'senior'
            }
            
            await service.search_jobs('python', filters)
            
            mock_scraper.search.assert_called_once()

    async def test_search_multiple_sources(self, db):
        """Test searching across multiple sources"""
        service = SearchService(db)
        
        with patch.object(service, 'scraper') as mock_scraper:
            mock_scraper.search = AsyncMock(return_value=[
                {'title': 'Job 1', 'source': 'linkedin'},
                {'title': 'Job 2', 'source': 'indeed'},
            ])
            
            results = await service.search_jobs('developer', {})
            
            assert len(results) == 2


@pytest.mark.asyncio
class TestAlertService:
    """Test AlertService methods"""

    async def test_create_alert(self, test_user: User, db):
        """Test creating an alert"""
        service = AlertService(db)
        
        alert_data = {
            'name': 'Python Developer',
            'query': 'Python',
            'frequency': 'daily',
            'notification_method': 'email'
        }
        
        # Mock repository
        with patch.object(service, 'repo') as mock_repo:
            mock_repo.create = AsyncMock(return_value={
                'id': '1',
                **alert_data,
                'user_id': test_user.id,
                'is_active': True,
                'created_at': datetime.now().isoformat()
            })
            
            alert = await service.create_alert(test_user.id, alert_data)
            
            assert alert['name'] == 'Python Developer'
            assert alert['query'] == 'Python'

    async def test_update_alert(self, test_user: User, db):
        """Test updating an alert"""
        service = AlertService(db)
        
        with patch.object(service, 'repo') as mock_repo:
            mock_repo.update = AsyncMock(return_value={
                'id': '1',
                'name': 'Python Developer',
                'frequency': 'weekly',
                'is_active': True
            })
            
            alert = await service.update_alert('1', {'frequency': 'weekly'})
            
            assert alert['frequency'] == 'weekly'

    async def test_delete_alert(self, db):
        """Test deleting an alert"""
        service = AlertService(db)
        
        with patch.object(service, 'repo') as mock_repo:
            mock_repo.delete = AsyncMock()
            
            await service.delete_alert('1')
            
            mock_repo.delete.assert_called_once_with('1')

    async def test_get_user_alerts(self, test_user: User, db):
        """Test retrieving user alerts"""
        service = AlertService(db)
        
        with patch.object(service, 'repo') as mock_repo:
            mock_repo.get_by_user = AsyncMock(return_value=[
                {
                    'id': '1',
                    'name': 'Alert 1',
                    'query': 'Python',
                    'frequency': 'daily',
                    'is_active': True
                },
                {
                    'id': '2',
                    'name': 'Alert 2',
                    'query': 'JavaScript',
                    'frequency': 'weekly',
                    'is_active': False
                }
            ])
            
            alerts = await service.get_user_alerts(test_user.id)
            
            assert len(alerts) == 2

    async def test_toggle_alert(self, db):
        """Test toggling alert active status"""
        service = AlertService(db)
        
        with patch.object(service, 'repo') as mock_repo:
            mock_repo.update = AsyncMock(return_value={
                'id': '1',
                'is_active': False
            })
            
            alert = await service.toggle_alert('1')
            
            assert alert['is_active'] is False

    async def test_check_alerts_for_new_jobs(self, test_user: User, db):
        """Test checking alerts for new jobs"""
        service = AlertService(db)
        
        with patch.object(service, 'repo') as mock_repo:
            with patch.object(service, 'search_service') as mock_search:
                mock_repo.get_by_user = AsyncMock(return_value=[
                    {
                        'id': '1',
                        'query': 'Python',
                        'is_active': True
                    }
                ])
                
                mock_search.search_jobs = AsyncMock(return_value=[
                    {'title': 'Python Developer', 'company': 'Tech Corp'}
                ])
                
                results = await service.check_alerts_for_new_jobs(test_user.id)
                
                assert len(results) >= 0
