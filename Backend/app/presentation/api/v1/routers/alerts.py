"""
Alerts Router - Clean Architecture

This router handles alert-related endpoints using dependency injection
and use cases following Clean Architecture principles.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from dependency_injector.wiring import inject, Provide

from app.infrastructure.persistence.sqlalchemy.database import get_db
from app.presentation.api.v1.schemas.alert import AlertCreate, AlertUpdate, AlertResponse, AlertListResponse
from app.shared.security.security import get_current_user
from app.container import Container

# Use Cases
from app.application.use_cases.alerts.create_alert_use_case import CreateAlertUseCase
from app.application.use_cases.alerts.get_alert_use_case import GetAlertUseCase
from app.application.use_cases.alerts.list_alerts_use_case import ListAlertsUseCase
from app.application.use_cases.alerts.update_alert_use_case import UpdateAlertUseCase
from app.application.use_cases.alerts.delete_alert_use_case import DeleteAlertUseCase

# Exceptions
from app.shared.exceptions.application_exceptions import NotFoundException, AuthorizationException

router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])


@router.post("", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
@inject
async def create_alert(
    alert_create: AlertCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    use_case: CreateAlertUseCase = Depends(Provide[Container.application.create_alert_use_case]),
):
    """
    Create a new alert.
    
    This endpoint allows users to create job alerts with custom search criteria.
    """
    try:
        alert = await use_case.execute(current_user.id, alert_create)
        await db.commit()
        return alert
    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create alert: {str(e)}"
        )


@router.get("/{alert_id}", response_model=AlertResponse)
@inject
async def get_alert(
    alert_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    use_case: GetAlertUseCase = Depends(Provide[Container.application.get_alert_use_case]),
):
    """
    Get alert by ID.
    
    Retrieves a specific alert with authorization check.
    """
    try:
        alert = await use_case.execute(alert_id, current_user.id)
        return alert
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except AuthorizationException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.get("", response_model=AlertListResponse)
@inject
async def list_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    use_case: ListAlertsUseCase = Depends(Provide[Container.application.list_alerts_use_case]),
):
    """
    Get all alerts for current user.
    
    Returns a paginated list of alerts for the authenticated user.
    """
    try:
        alerts = await use_case.execute(current_user.id, skip, limit)
        return alerts
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list alerts: {str(e)}"
        )


@router.put("/{alert_id}", response_model=AlertResponse)
@inject
async def update_alert(
    alert_id: UUID,
    alert_update: AlertUpdate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    use_case: UpdateAlertUseCase = Depends(Provide[Container.application.update_alert_use_case]),
):
    """
    Update alert.
    
    Updates an existing alert with authorization check.
    """
    try:
        updated_alert = await use_case.execute(alert_id, current_user.id, alert_update)
        await db.commit()
        return updated_alert
    except NotFoundException as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except AuthorizationException as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update alert: {str(e)}"
        )


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_alert(
    alert_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    use_case: DeleteAlertUseCase = Depends(Provide[Container.application.delete_alert_use_case]),
):
    """
    Delete alert.
    
    Deletes an alert with authorization check.
    """
    try:
        await use_case.execute(alert_id, current_user.id)
        await db.commit()
    except NotFoundException as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except AuthorizationException as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete alert: {str(e)}"
        )
