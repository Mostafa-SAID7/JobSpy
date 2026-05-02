from datetime import datetime
import uuid
from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey, Index, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.infrastructure.persistence.sqlalchemy.database import Base


class AlertORM(Base):
    """SQLAlchemy model for Alert entities."""
    
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    query = Column(String(500), nullable=False)
    filters = Column(JSON, nullable=True)
    frequency = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    last_triggered = Column(DateTime, nullable=True)
    next_trigger = Column(DateTime, nullable=True)
    notification_method = Column(String(50), nullable=False)
    new_jobs_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("UserORM")

    __table_args__ = (
        Index("idx_alert_user_id", "user_id"),
        Index("idx_alert_is_active", "is_active"),
        Index("idx_alert_next_trigger", "next_trigger"),
        Index("idx_alert_created_at", "created_at"),
    )

    def __repr__(self):
        return f"<AlertORM(id={self.id}, user_id={self.user_id}, name={self.name})>"
