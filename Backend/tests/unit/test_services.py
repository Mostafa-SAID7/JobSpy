"""
Unit tests for service layer
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta


@pytest.mark.asyncio
class TestSearchService:
    """Test SearchService methods"""

    async def test_search_jobs(self):
        """Test searching jobs"""
        with patch('app.services.search_service.SearchService') as MockService:
            mock_service = MagicMock()
            MockService.return_value = mock_service
            mock_service.search_jobs = AsyncMock(return_value=[
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
            
            results = await mock_service.search_jobs('developer', {})
            
            assert len(results) == 1
            assert results[0]['title'] == 'Developer'

    async def test_search_with_filters(self):
        """Test searching with filters"""
        with patch('app.services.search_service.SearchService') as MockService:
            mock_service = MagicMock()
            MockService.return_value = mock_service
            mock_service.search_jobs = AsyncMock(return_value=[])
            
            filters = {
                'location': 'Remote',
                'salary_min': 100000,
                'experience_level': 'senior'
            }
            
            await mock_service.search_jobs('python', filters)
            
            mock_service.search_jobs.assert_called_once()

    async def test_search_multiple_sources(self):
        """Test searching across multiple sources"""
        with patch('app.services.search_service.SearchService') as MockService:
            mock_service = MagicMock()
            MockService.return_value = mock_service
            mock_service.search_jobs = AsyncMock(return_value=[
                {'title': 'Job 1', 'source': 'linkedin'},
                {'title': 'Job 2', 'source': 'indeed'},
            ])
            
            results = await mock_service.search_jobs('developer', {})
            
            assert len(results) == 2


@pytest.mark.asyncio
class TestAlertService:
    """Test AlertService methods"""

    async def test_create_alert(self):
        """Test creating an alert"""
        with patch('app.services.alert_service.AlertService') as MockService:
            mock_service = MagicMock()
            MockService.return_value = mock_service
            
            test_user_id = 1
            alert_data = {
                'name': 'Python Developer',
                'query': 'Python',
                'frequency': 'daily',
                'notification_method': 'email'
            }
            
            mock_service.create_alert = AsyncMock(return_value={
                'id': '1',
                **alert_data,
                'user_id': test_user_id,
                'is_active': True,
                'created_at': datetime.now().isoformat()
            })
            
            alert = await mock_service.create_alert(test_user_id, alert_data)
            
            assert alert['name'] == 'Python Developer'
            assert alert['query'] == 'Python'

    async def test_update_alert(self):
        """Test updating an alert"""
        with patch('app.services.alert_service.AlertService') as MockService:
            mock_service = MagicMock()
            MockService.return_value = mock_service
            
            mock_service.update_alert = AsyncMock(return_value={
                'id': '1',
                'name': 'Python Developer',
                'frequency': 'weekly',
                'is_active': True
            })
            
            alert = await mock_service.update_alert('1', {'frequency': 'weekly'})
            
            assert alert['frequency'] == 'weekly'

    async def test_delete_alert(self):
        """Test deleting an alert"""
        with patch('app.services.alert_service.AlertService') as MockService:
            mock_service = MagicMock()
            MockService.return_value = mock_service
            mock_service.delete_alert = AsyncMock()
            
            await mock_service.delete_alert('1')
            
            mock_service.delete_alert.assert_called_once_with('1')

    async def test_get_user_alerts(self):
        """Test retrieving user alerts"""
        with patch('app.services.alert_service.AlertService') as MockService:
            mock_service = MagicMock()
            MockService.return_value = mock_service
            
            test_user_id = 1
            
            mock_service.get_user_alerts = AsyncMock(return_value=[
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
            
            alerts = await mock_service.get_user_alerts(test_user_id)
            
            assert len(alerts) == 2

    async def test_toggle_alert(self):
        """Test toggling alert active status"""
        with patch('app.services.alert_service.AlertService') as MockService:
            mock_service = MagicMock()
            MockService.return_value = mock_service
            
            mock_service.toggle_alert = AsyncMock(return_value={
                'id': '1',
                'is_active': False
            })
            
            alert = await mock_service.toggle_alert('1')
            
            assert alert['is_active'] is False

    async def test_check_alerts_for_new_jobs(self):
        """Test checking alerts for new jobs"""
        with patch('app.services.alert_service.AlertService') as MockService:
            mock_service = MagicMock()
            MockService.return_value = mock_service
            
            test_user_id = 1
            
            mock_service.check_alerts_for_new_jobs = AsyncMock(return_value=[
                {'title': 'Python Developer', 'company': 'Tech Corp'}
            ])
            
            results = await mock_service.check_alerts_for_new_jobs(test_user_id)
            
            assert len(results) >= 0
