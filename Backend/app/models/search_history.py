from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=True, index=True)
    query = Column(String(500), nullable=False)
    filters = Column(JSONB, nullable=True)  # Stored search filters
    results_count = Column(Integer, default=0)
    search_type = Column(String(50), nullable=False)  # "keyword", "advanced", "alert"
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User")
    job = relationship("Job", back_populates="search_history")

    __table_args__ = (
        Index("idx_search_history_user_id", "user_id"),
        Index("idx_search_history_job_id", "job_id"),
        Index("idx_search_history_created_at", "created_at"),
        Index("idx_search_history_query", "query"),
    )

    def __repr__(self):
        return f"<SearchHistory(user_id={self.user_id}, query={self.query})>"
