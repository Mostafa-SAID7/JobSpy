from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from app.presentation.api.v1.schemas.job import JobResponse

class ScrapeRequest(BaseModel):
    query: str = Field(..., min_length=1)
    location: Optional[str] = None
    site_names: Optional[List[str]] = ["linkedin", "indeed", "glassdoor", "zip_recruiter", "google", "bayt", "naukri", "bdjobs"]
    max_results: Optional[int] = Field(50, ge=1, le=200)
    hours_old: Optional[int] = None
    job_type: Optional[str] = None
    is_remote: Optional[bool] = False
    distance: Optional[int] = 50
    easy_apply: Optional[bool] = False
    country_indeed: Optional[str] = "USA"

class ScrapeResponse(BaseModel):
    saved_count: int
    duplicate_count: int
    error_count: int
    total_processed: int
    jobs: List[JobResponse]
