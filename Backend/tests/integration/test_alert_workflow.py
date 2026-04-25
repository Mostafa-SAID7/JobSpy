"""
Integration tests for alert management workflow
"""
import pytest
from httpx import AsyncClient

from app.models.user import User


@pytest.mark.asyncio
class TestAlertWorkflow:
    """Test complete alert management workflow"""

    async def test_create_and_manage_alerts_workflow(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict
    ):
        """Test creating and managing alerts"""
        alert_data = {
            "name": "Python Developer",
            "query": "Python",
            "frequency": "daily",
            "notification_method": "email"
        }
        
        # Create alert
        create_response = await client.post(
            "/alerts",
            json=alert_data,
            headers=auth_headers
        )
        
        assert create_response.status_code == 201
        alert = create_response.json()
        alert_id = alert['id']
        
        # Get alerts
        get_response = await client.get(
            "/alerts",
            headers=auth_headers
        )
        
        assert get_response.status_code == 200
        alerts = get_response.json()
        assert any(a['id'] == alert_id for a in alerts)

    async def test_update_alert_workflow(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict
    ):
        """Test updating an alert"""
        # Create alert
        alert_data = {
            "name": "Python Developer",
            "query": "Python",
            "frequency": "daily",
            "notification_method": "email"
        }
        
        create_response = await client.post(
            "/alerts",
            json=alert_data,
            headers=auth_headers
        )
        
        alert = create_response.json()
        alert_id = alert['id']
        
        # Update alert
        update_data = {
            "frequency": "weekly",
            "notification_method": "in_app"
        }
        
        update_response = await client.put(
            f"/alerts/{alert_id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert update_response.status_code == 200
        updated_alert = update_response.json()
        assert updated_alert['frequency'] == 'weekly'
        assert updated_alert['notification_method'] == 'in_app'

    async def test_toggle_alert_workflow(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict
    ):
        """Test toggling alert active status"""
        # Create alert
        alert_data = {
            "name": "Python Developer",
            "query": "Python",
            "frequency": "daily",
            "notification_method": "email"
        }
        
        create_response = await client.post(
            "/alerts",
            json=alert_data,
            headers=auth_headers
        )
        
        alert = create_response.json()
        alert_id = alert['id']
        initial_status = alert['is_active']
        
        # Toggle alert
        toggle_response = await client.patch(
            f"/alerts/{alert_id}/toggle",
            headers=auth_headers
        )
        
        assert toggle_response.status_code == 200
        toggled_alert = toggle_response.json()
        assert toggled_alert['is_active'] != initial_status

    async def test_delete_alert_workflow(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict
    ):
        """Test deleting an alert"""
        # Create alert
        alert_data = {
            "name": "Python Developer",
            "query": "Python",
            "frequency": "daily",
            "notification_method": "email"
        }
        
        create_response = await client.post(
            "/alerts",
            json=alert_data,
            headers=auth_headers
        )
        
        alert = create_response.json()
        alert_id = alert['id']
        
        # Delete alert
        delete_response = await client.delete(
            f"/alerts/{alert_id}",
            headers=auth_headers
        )
        
        assert delete_response.status_code == 204
        
        # Verify deletion
        get_response = await client.get(
            "/alerts",
            headers=auth_headers
        )
        
        alerts = get_response.json()
        assert not any(a['id'] == alert_id for a in alerts)

    async def test_alert_validation_workflow(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict
    ):
        """Test alert validation"""
        # Try to create alert with invalid data
        invalid_data = {
            "name": "",  # Empty name
            "query": "Python",
            "frequency": "invalid_frequency",
            "notification_method": "email"
        }
        
        response = await client.post(
            "/alerts",
            json=invalid_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422  # Validation error

    async def test_get_alert_stats_workflow(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict
    ):
        """Test getting alert statistics"""
        response = await client.get(
            "/alerts/stats",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        stats = response.json()
        assert 'total_alerts' in stats
        assert 'active_alerts' in stats
        assert 'total_new_jobs' in stats
