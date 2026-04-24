from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from datetime import datetime
from app.models.alert import Alert
from app.schemas.alert import AlertCreate, AlertUpdate


class AlertRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: UUID, alert_create: AlertCreate) -> Alert:
        """Create a new alert."""
        db_alert = Alert(
            user_id=user_id,
            name=alert_create.name,
            query=alert_create.query,
            filters=alert_create.filters,
            frequency=alert_create.frequency,
            notification_method=alert_create.notification_method,
        )
        self.session.add(db_alert)
        await self.session.flush()
        return db_alert

    async def get_by_id(self, alert_id: UUID) -> Alert | None:
        """Get alert by ID."""
        result = await self.session.execute(
            select(Alert).where(Alert.id == alert_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user(self, user_id: UUID, skip: int = 0, limit: int = 100) -> list[Alert]:
        """Get all alerts for a user."""
        result = await self.session.execute(
            select(Alert)
            .where(Alert.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(Alert.created_at.desc())
        )
        return result.scalars().all()

    async def get_active_alerts(self, skip: int = 0, limit: int = 100) -> list[Alert]:
        """Get all active alerts."""
        result = await self.session.execute(
            select(Alert)
            .where(Alert.is_active == True)
            .offset(skip)
            .limit(limit)
            .order_by(Alert.next_trigger.asc())
        )
        return result.scalars().all()

    async def get_alerts_to_trigger(self) -> list[Alert]:
        """Get alerts that need to be triggered."""
        now = datetime.utcnow()
        result = await self.session.execute(
            select(Alert).where(
                (Alert.is_active == True) &
                (Alert.next_trigger <= now)
            )
        )
        return result.scalars().all()

    async def update(self, alert_id: UUID, alert_update: AlertUpdate) -> Alert | None:
        """Update alert."""
        alert = await self.get_by_id(alert_id)
        if not alert:
            return None

        update_data = alert_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(alert, field, value)

        self.session.add(alert)
        await self.session.flush()
        return alert

    async def delete(self, alert_id: UUID) -> bool:
        """Delete alert."""
        alert = await self.get_by_id(alert_id)
        if not alert:
            return False

        await self.session.delete(alert)
        await self.session.flush()
        return True

    async def update_trigger_info(self, alert_id: UUID, next_trigger: datetime) -> Alert | None:
        """Update alert trigger information."""
        alert = await self.get_by_id(alert_id)
        if not alert:
            return None

        alert.last_triggered = datetime.utcnow()
        alert.next_trigger = next_trigger
        self.session.add(alert)
        await self.session.flush()
        return alert

    async def count_by_user(self, user_id: UUID) -> int:
        """Count alerts for a user."""
        result = await self.session.execute(
            select(Alert).where(Alert.user_id == user_id)
        )
        return len(result.scalars().all())

    async def count_active(self) -> int:
        """Count active alerts."""
        result = await self.session.execute(
            select(Alert).where(Alert.is_active == True)
        )
        return len(result.scalars().all())
