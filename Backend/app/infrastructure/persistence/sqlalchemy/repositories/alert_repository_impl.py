"""
Alert Repository Implementation (Infrastructure Layer)

Implements IAlertRepository using SQLAlchemy.
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_

from app.domain.entities.alert import Alert
from app.domain.interfaces.repositories import IAlertRepository
from app.infrastructure.persistence.sqlalchemy.models.alert_orm import AlertORM
from app.infrastructure.persistence.sqlalchemy.mappers.alert_mapper import AlertMapper


class AlertRepositoryImpl(IAlertRepository):
    """
    SQLAlchemy implementation of IAlertRepository.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, alert: Alert) -> Alert:
        """Create a new alert."""
        orm_alert = AlertMapper.to_orm(alert)
        self.session.add(orm_alert)
        await self.session.flush()
        return AlertMapper.to_domain(orm_alert)

    async def get_by_id(self, alert_id: UUID) -> Optional[Alert]:
        """Get alert by ID."""
        result = await self.session.execute(
            select(AlertORM).where(AlertORM.id == alert_id)
        )
        orm_alert = result.scalar_one_or_none()
        return AlertMapper.to_domain(orm_alert) if orm_alert else None

    async def get_by_user(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Alert]:
        """Get all alerts for a user."""
        result = await self.session.execute(
            select(AlertORM)
            .where(AlertORM.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(AlertORM.created_at.desc())
        )
        orm_alerts = result.scalars().all()
        return [AlertMapper.to_domain(a) for a in orm_alerts]

    async def update(self, alert: Alert) -> Alert:
        """Update an alert."""
        result = await self.session.execute(
            select(AlertORM).where(AlertORM.id == alert.id)
        )
        orm_alert = result.scalar_one_or_none()
        if not orm_alert:
            raise ValueError(f"Alert with ID {alert.id} not found")

        orm_alert.name = alert.name
        orm_alert.query = alert.query
        orm_alert.frequency = alert.frequency
        orm_alert.notification_method = alert.notification_method
        orm_alert.filters = alert.filters
        orm_alert.is_active = alert.is_active
        orm_alert.last_triggered = alert.last_triggered
        orm_alert.next_trigger = alert.next_trigger
        orm_alert.new_jobs_count = alert.new_jobs_count
        orm_alert.updated_at = datetime.utcnow()

        await self.session.flush()
        return AlertMapper.to_domain(orm_alert)

    async def delete(self, alert_id: UUID) -> bool:
        """Delete an alert."""
        result = await self.session.execute(
            select(AlertORM).where(AlertORM.id == alert_id)
        )
        orm_alert = result.scalar_one_or_none()
        if not orm_alert:
            return False

        await self.session.delete(orm_alert)
        await self.session.flush()
        return True

    async def count_by_user(self, user_id: UUID) -> int:
        """Count alerts for a user."""
        result = await self.session.execute(
            select(func.count(AlertORM.id)).where(AlertORM.user_id == user_id)
        )
        return result.scalar() or 0

    async def get_all_active(self) -> List[Alert]:
        """Get all active alerts."""
        result = await self.session.execute(
            select(AlertORM)
            .where(AlertORM.is_active == True)
            .order_by(AlertORM.next_trigger.asc())
        )
        orm_alerts = result.scalars().all()
        return [AlertMapper.to_domain(a) for a in orm_alerts]

    async def get_alerts_to_trigger(self) -> List[Alert]:
        """Get alerts that are due for triggering."""
        now = datetime.utcnow()
        result = await self.session.execute(
            select(AlertORM).where(
                and_(
                    AlertORM.is_active == True,
                    AlertORM.next_trigger <= now
                )
            )
        )
        orm_alerts = result.scalars().all()
        return [AlertMapper.to_domain(a) for a in orm_alerts]
