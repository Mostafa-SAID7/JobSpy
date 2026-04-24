from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Optional, List
from uuid import UUID


class JobBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    company: str = Field(..., min_length=1, max_length=255)
    location: str = Field(..., min_length=1, max_length=255)
    source: str = Field(..., min_length=1, max_length=50)


class JobCreate(JobBase):
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: Optional[str] = None
    job_type: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[List[str]] = None
    benefits: Optional[List[str]] = None
    source_url: str
    source_job_id: Optional[str] = None
    posted_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    company_logo_url: Optional[str] = None
    company_website: Optional[str] = None
    experience_level: Optional[str] = None
    skills: Optional[List[str]] = None
    is_remote: int = 0


class JobUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    company: Optional[str] = Field(None, min_length=1, max_length=255)
    location: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    requirements: Optional[List[str]] = None
    benefits: Optional[List[str]] = None


class JobResponse(JobBase):
    id: UUID
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: Optional[str] = None
    job_type: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[List[str]] = None
    benefits: Optional[List[str]] = None
    source_url: str
    source_job_id: Optional[str] = None
    posted_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    company_logo_url: Optional[str] = None
    company_website: Optional[str] = None
    experience_level: Optional[str] = None
    skills: Optional[List[str]] = None
    is_remote: int
    view_count: int
    apply_count: int
    created_at: datetime
    updated_at: datetime
    scraped_at: datetime

    class Config:
        from_attributes = True


class JobDetailResponse(JobResponse):
    pass


class JobListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[JobResponse]
