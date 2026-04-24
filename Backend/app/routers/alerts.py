from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.core.database import get_db
from app.schemas.alert import AlertCreate, AlertUpdate, AlertResponse, AlertListResponse
from app.repositories.alert_repo import AlertRepository
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])


@router.post("", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(
    alert_create: AlertCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new alert."""
    alert_repo = AlertRepository(db)
    
    try:
        alert = await alert_repo.create(current_user.id, alert_create)
        await db.commit()
        await db.refresh(alert)
        return alert
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get alert by ID."""
    alert_repo = AlertRepository(db)
    alert = await alert_repo.get_by_id(alert_id)
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    if alert.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this alert"
        )
    
    return alert


@router.get("", response_model=AlertListResponse)
async def list_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all alerts for current user."""
    alert_repo = AlertRepository(db)
    alerts = await alert_repo.get_by_user(current_user.id, skip, limit)
    total = await alert_repo.count_by_user(current_user.id)
    
    return AlertListResponse(
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        items=alerts
    )


@router.put("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: UUID,
    alert_update: AlertUpdate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update alert."""
    alert_repo = AlertRepository(db)
    alert = await alert_repo.get_by_id(alert_id)
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    if alert.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this alert"
        )
    
    updated_alert = await alert_repo.update(alert_id, alert_update)
    await db.commit()
    return updated_alert


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(
    alert_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete alert."""
    alert_repo = AlertRepository(db)
    alert = await alert_repo.get_by_id(alert_id)
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    if alert.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this alert"
        )
    
    success = await alert_repo.delete(alert_id)
    await db.commit()
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
