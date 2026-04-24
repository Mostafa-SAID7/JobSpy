from datetime import datetime
from sqlalchemy import Column, String, DateTime, Float, Integer, Text, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=False, index=True)
    location = Column(String(255), nullable=False)
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    salary_currency = Column(String(10), nullable=True)
    job_type = Column(String(50), nullable=True)  # Full-time, Part-time, Contract, etc.
    description = Column(Text, nullable=True)
    requirements = Column(JSONB, nullable=True)  # Array of requirements
    benefits = Column(JSONB, nullable=True)  # Array of benefits
    source = Column(String(50), nullable=False, index=True)  # LinkedIn, Indeed, Wuzzuf, Bayt
    source_url = Column(String(500), nullable=False, unique=True)
    source_job_id = Column(String(255), nullable=True, index=True)
    posted_date = Column(DateTime, nullable=True)
    deadline = Column(DateTime, nullable=True)
    company_logo_url = Column(String(500), nullable=True)
    company_website = Column(String(500), nullable=True)
    experience_level = Column(String(50), nullable=True)  # Entry, Mid, Senior
    skills = Column(JSONB, nullable=True)  # Array of required skills
    is_remote = Column(Integer, default=0)  # 0: On-site, 1: Remote, 2: Hybrid
    view_count = Column(Integer, default=0)
    apply_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    scraped_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    saved_jobs = relationship("SavedJob", back_populates="job", cascade="all, delete-orphan")
    search_history = relationship("SearchHistory", back_populates="job")

    __table_args__ = (
        Index("idx_job_title", "title"),
        Index("idx_job_company", "company"),
        Index("idx_job_source", "source"),
        Index("idx_job_source_url", "source_url"),
        Index("idx_job_created_at", "created_at"),
        Index("idx_job_posted_date", "posted_date"),
    )

    def __repr__(self):
        return f"<Job(id={self.id}, title={self.title}, company={self.company})>"
