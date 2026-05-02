from app.domain.entities.alert import Alert
from app.infrastructure.persistence.sqlalchemy.models.alert_orm import AlertORM


class AlertMapper:
    """Mapper to convert between Alert domain entity and AlertORM model."""

    @staticmethod
    def to_domain(orm_alert: AlertORM) -> Alert:
        """Convert SQLAlchemy AlertORM to Alert domain entity."""
        if not orm_alert:
            return None

        return Alert(
            id=orm_alert.id,
            user_id=orm_alert.user_id,
            name=orm_alert.name,
            query=orm_alert.query,
            frequency=orm_alert.frequency,
            notification_method=orm_alert.notification_method,
            filters=orm_alert.filters or {},
            is_active=orm_alert.is_active,
            last_triggered=orm_alert.last_triggered,
            next_trigger=orm_alert.next_trigger,
            new_jobs_count=orm_alert.new_jobs_count or 0,
            created_at=orm_alert.created_at,
            updated_at=orm_alert.updated_at,
        )

    @staticmethod
    def to_orm(domain_alert: Alert) -> AlertORM:
        """Convert Alert domain entity to SQLAlchemy AlertORM."""
        if not domain_alert:
            return None

        return AlertORM(
            id=domain_alert.id,
            user_id=domain_alert.user_id,
            name=domain_alert.name,
            query=domain_alert.query,
            frequency=domain_alert.frequency,
            notification_method=domain_alert.notification_method,
            filters=domain_alert.filters,
            is_active=domain_alert.is_active,
            last_triggered=domain_alert.last_triggered,
            next_trigger=domain_alert.next_trigger,
            new_jobs_count=domain_alert.new_jobs_count,
            created_at=domain_alert.created_at,
            updated_at=domain_alert.updated_at,
        )
