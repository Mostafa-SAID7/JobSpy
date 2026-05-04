from datetime import datetime
import uuid
from sqlalchemy import Column, String, DateTime, Float, Integer, Text, Index, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.infrastructure.persistence.sqlalchemy.database import Base


class JobORM(Base):
    """SQLAlchemy model for Job entities."""
    
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=False, index=True)
    location = Column(String(255), nullable=False, index=True)
    salary_min = Column(Float, nullable=True, index=True)
    salary_max = Column(Float, nullable=True, index=True)
    salary_currency = Column(String(10), nullable=True)
    job_type = Column(String(50), nullable=True, index=True)
    description = Column(Text, nullable=True)
    requirements = Column(JSON, nullable=True)
    benefits = Column(JSON, nullable=True)
    source = Column(String(50), nullable=False, index=True)
    source_url = Column(String(500), nullable=False, unique=True)
    source_url_direct = Column(String(500), nullable=True)
    source_job_id = Column(String(255), nullable=True, index=True)
    posted_date = Column(DateTime, nullable=True)
    deadline = Column(DateTime, nullable=True)
    company_logo_url = Column(String(500), nullable=True)
    company_website = Column(String(500), nullable=True)
    company_industry = Column(String(255), nullable=True)
    company_addresses = Column(Text, nullable=True)
    company_num_employees = Column(String(100), nullable=True)
    company_revenue = Column(String(100), nullable=True)
    company_description = Column(Text, nullable=True)
    company_rating = Column(Float, nullable=True)
    company_reviews_count = Column(Integer, nullable=True)
    
    job_level = Column(String(100), nullable=True)
    job_function = Column(String(255), nullable=True)
    experience_level = Column(String(50), nullable=True)
    experience_range = Column(String(100), nullable=True)
    emails = Column(JSON, nullable=True)
    banner_photo_url = Column(String(500), nullable=True)
    vacancy_count = Column(Integer, nullable=True)
    work_from_home_type = Column(String(100), nullable=True)
    
    skills = Column(JSON, nullable=True)
    is_remote = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    apply_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    scraped_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    saved_jobs = relationship("SavedJobORM", back_populates="job", cascade="all, delete-orphan")
    search_history = relationship("SearchHistoryORM", back_populates="job")

    __table_args__ = (
        Index("idx_job_title", "title"),
        Index("idx_job_company", "company"),
        Index("idx_job_source", "source"),
        Index("idx_job_source_url", "source_url"),
        Index("idx_job_created_at", "created_at"),
        Index("idx_job_posted_date", "posted_date"),
    )

    def __repr__(self):
        return f"<JobORM(id={self.id}, title={self.title}, company={self.company})>"
