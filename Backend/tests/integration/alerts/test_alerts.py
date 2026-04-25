"""
Integration tests for alerts API endpoints
Validates: Requirements 6.1, 6.5
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4
from datetime import datetime, timedelta


@pytest.mark.asyncio
async def test_create_alert(client: AsyncClient, auth_headers: dict):
    """Test creating a new alert"""
    alert_data = {
        "name": "Python Developer Alert",
        "query": "Python Developer",
        "frequency": "daily",
        "notification_method": "email",
        "filters": {"location": "Cairo"}
    }
    
    response = await client.post(
        "/api/v1/alerts",
        json=alert_data,
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == alert_data["name"]
    assert data["query"] == alert_data["query"]
    assert data["frequency"] == alert_data["frequency"]
    assert data["is_active"] is True
    assert "id" in data


@pytest.mark.asyncio
async def test_get_alerts(client: AsyncClient, auth_headers: dict):
    """Test retrieving all alerts for current user"""
    # Create an alert first
    alert_data = {
        "name": "Test Alert",
        "query": "Test Query",
        "frequency": "hourly",
        "notification_method": "in_app"
    }
    
    await client.post(
        "/api/v1/alerts",
        json=alert_data,
        headers=auth_headers
    )
    
    # Get alerts
    response = await client.get(
        "/api/v1/alerts",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_get_alert_by_id(client: AsyncClient, auth_headers: dict):
    """Test retrieving a specific alert by ID"""
    # Create an alert
    alert_data = {
        "name": "Specific Alert",
        "query": "Specific Query",
        "frequency": "weekly",
        "notification_method": "email"
    }
    
    create_response = await client.post(
        "/api/v1/alerts",
        json=alert_data,
        headers=auth_headers
    )
    
    alert_id = create_response.json()["id"]
    
    # Get the alert
    response = await client.get(
        f"/api/v1/alerts/{alert_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == alert_id
    assert data["name"] == alert_data["name"]


@pytest.mark.asyncio
async def test_update_alert(client: AsyncClient, auth_headers: dict):
    """Test updating an alert"""
    # Create an alert
    alert_data = {
        "name": "Original Name",
        "query": "Original Query",
        "frequency": "daily",
        "notification_method": "email"
    }
    
    create_response = await client.post(
        "/api/v1/alerts",
        json=alert_data,
        headers=auth_headers
    )
    
    alert_id = create_response.json()["id"]
    
    # Update the alert
    update_data = {
        "name": "Updated Name",
        "frequency": "weekly",
        "is_active": False
    }
    
    response = await client.put(
        f"/api/v1/alerts/{alert_id}",
        json=update_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["frequency"] == update_data["frequency"]
    assert data["is_active"] is False


@pytest.mark.asyncio
async def test_toggle_alert_active_status(client: AsyncClient, auth_headers: dict):
    """Test toggling alert active/inactive status"""
    # Create an alert
    alert_data = {
        "name": "Toggle Test",
        "query": "Toggle Query",
        "frequency": "daily",
        "notification_method": "email"
    }
    
    create_response = await client.post(
        "/api/v1/alerts",
        json=alert_data,
        headers=auth_headers
    )
    
    alert_id = create_response.json()["id"]
    
    # Disable the alert
    response = await client.put(
        f"/api/v1/alerts/{alert_id}",
        json={"is_active": False},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert response.json()["is_active"] is False
    
    # Enable the alert
    response = await client.put(
        f"/api/v1/alerts/{alert_id}",
        json={"is_active": True},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert response.json()["is_active"] is True


@pytest.mark.asyncio
async def test_delete_alert(client: AsyncClient, auth_headers: dict):
    """Test deleting an alert"""
    # Create an alert
    alert_data = {
        "name": "Delete Test",
        "query": "Delete Query",
        "frequency": "daily",
        "notification_method": "email"
    }
    
    create_response = await client.post(
        "/api/v1/alerts",
        json=alert_data,
        headers=auth_headers
    )
    
    alert_id = create_response.json()["id"]
    
    # Delete the alert
    response = await client.delete(
        f"/api/v1/alerts/{alert_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 204
    
    # Verify it's deleted
    response = await client.get(
        f"/api/v1/alerts/{alert_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_unauthorized_access_to_other_user_alert(
    client: AsyncClient,
    auth_headers: dict,
    other_user_headers: dict
):
    """Test that users cannot access other users' alerts"""
    # Create an alert with first user
    alert_data = {
        "name": "Private Alert",
        "query": "Private Query",
        "frequency": "daily",
        "notification_method": "email"
    }
    
    create_response = await client.post(
        "/api/v1/alerts",
        json=alert_data,
        headers=auth_headers
    )
    
    alert_id = create_response.json()["id"]
    
    # Try to access with different user
    response = await client.get(
        f"/api/v1/alerts/{alert_id}",
        headers=other_user_headers
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_alert_validation(client: AsyncClient, auth_headers: dict):
    """Test alert creation validation"""
    # Missing required fields
    response = await client.post(
        "/api/v1/alerts",
        json={"name": "Test"},
        headers=auth_headers
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_alert_frequency_options(client: AsyncClient, auth_headers: dict):
    """Test different frequency options"""
    frequencies = ["hourly", "daily", "weekly"]
    
    for frequency in frequencies:
        alert_data = {
            "name": f"Alert {frequency}",
            "query": "Test Query",
            "frequency": frequency,
            "notification_method": "email"
        }
        
        response = await client.post(
            "/api/v1/alerts",
            json=alert_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        assert response.json()["frequency"] == frequency


@pytest.mark.asyncio
async def test_alert_notification_methods(client: AsyncClient, auth_headers: dict):
    """Test different notification methods"""
    methods = ["email", "in_app"]
    
    for method in methods:
        alert_data = {
            "name": f"Alert {method}",
            "query": "Test Query",
            "frequency": "daily",
            "notification_method": method
        }
        
        response = await client.post(
            "/api/v1/alerts",
            json=alert_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        assert response.json()["notification_method"] == method
