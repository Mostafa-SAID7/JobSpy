"""
Alerts Router - Clean Architecture - Manual DI Getters
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from uuid import UUID

from app.presentation.api.v1.schemas.alert import AlertCreate, AlertUpdate, AlertResponse, AlertListResponse
from app.shared.security.security import get_current_user
from app.container import container

from app.application.use_cases.alerts.create_alert_use_case import CreateAlertUseCase
from app.application.use_cases.alerts.get_alert_use_case import GetAlertUseCase
from app.application.use_cases.alerts.list_alerts_use_case import ListAlertsUseCase
from app.application.use_cases.alerts.update_alert_use_case import UpdateAlertUseCase
from app.application.use_cases.alerts.delete_alert_use_case import DeleteAlertUseCase
from app.shared.exceptions.application_exceptions import NotFoundException, AuthorizationException

router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])


def get_create_alert_use_case(): return container.application.create_alert_use_case()
def get_get_alert_use_case(): return container.application.get_alert_use_case()
def get_list_alerts_use_case(): return container.application.list_alerts_use_case()
def get_update_alert_use_case(): return container.application.update_alert_use_case()
def get_delete_alert_use_case(): return container.application.delete_alert_use_case()


@router.post("", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(
    alert_create: AlertCreate,
    current_user=Depends(get_current_user),
    use_case: CreateAlertUseCase = Depends(get_create_alert_use_case),
):
    try:
        return await use_case.execute(current_user.id, alert_create)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create alert: {str(e)}")


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: UUID,
    current_user=Depends(get_current_user),
    use_case: GetAlertUseCase = Depends(get_get_alert_use_case),
):
    try:
        return await use_case.execute(alert_id, current_user.id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("", response_model=AlertListResponse)
async def list_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user=Depends(get_current_user),
    use_case: ListAlertsUseCase = Depends(get_list_alerts_use_case),
):
    try:
        return await use_case.execute(current_user.id, skip, limit)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to list alerts: {str(e)}")


@router.put("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: UUID,
    alert_update: AlertUpdate,
    current_user=Depends(get_current_user),
    use_case: UpdateAlertUseCase = Depends(get_update_alert_use_case),
):
    try:
        return await use_case.execute(alert_id, current_user.id, alert_update)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update alert: {str(e)}")


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(
    alert_id: UUID,
    current_user=Depends(get_current_user),
    use_case: DeleteAlertUseCase = Depends(get_delete_alert_use_case),
):
    try:
        await use_case.execute(alert_id, current_user.id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete alert: {str(e)}")
