from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID
from app.schemas.job import JobResponse


class SavedJobBase(BaseModel):
    job_id: UUID
    notes: Optional[str] = None


class SavedJobCreate(SavedJobBase):
    pass


class SavedJobUpdate(BaseModel):
    notes: Optional[str] = None


class SavedJobResponse(BaseModel):
    id: UUID
    user_id: UUID
    job_id: UUID
    notes: Optional[str] = None
    saved_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SavedJobDetailResponse(BaseModel):
    id: UUID
    user_id: UUID
    job: JobResponse
    notes: Optional[str] = None
    saved_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SavedJobListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[SavedJobDetailResponse]
