from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID


class AlertBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    query: str = Field(..., min_length=1, max_length=500)
    frequency: str = Field(..., min_length=1, max_length=50)
    notification_method: str = Field(..., min_length=1, max_length=50)


class AlertCreate(AlertBase):
    filters: Optional[Dict[str, Any]] = None


class AlertUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    query: Optional[str] = Field(None, min_length=1, max_length=500)
    filters: Optional[Dict[str, Any]] = None
    frequency: Optional[str] = Field(None, min_length=1, max_length=50)
    notification_method: Optional[str] = Field(None, min_length=1, max_length=50)
    is_active: Optional[bool] = None


class AlertResponse(AlertBase):
    id: UUID
    user_id: UUID
    filters: Optional[Dict[str, Any]] = None
    is_active: bool
    last_triggered: Optional[datetime] = None
    next_trigger: Optional[datetime] = None
    new_jobs_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AlertListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[AlertResponse]
