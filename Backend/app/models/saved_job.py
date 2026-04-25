from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class SavedJob(Base):
    __tablename__ = "saved_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    notes = Column(DateTime, nullable=True)  # User notes about the job
    saved_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User")
    job = relationship("Job", back_populates="saved_jobs")

    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="uq_user_job"),
        Index("idx_saved_job_user_id", "user_id"),
        Index("idx_saved_job_job_id", "job_id"),
        Index("idx_saved_job_saved_at", "saved_at"),
    )

    def __repr__(self):
        return f"<SavedJob(user_id={self.user_id}, job_id={self.job_id})>"

