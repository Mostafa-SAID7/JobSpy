"""
Jobs Router - JobSpy Backend (Clean Architecture)

Thin controllers that delegate all business logic to use cases.
Uses manual dependency injection getters (no @inject/Provide).
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional
from datetime import datetime
import logging

from app.infrastructure.persistence.sqlalchemy.database import get_db
from app.presentation.api.v1.schemas.job import JobCreate, JobUpdate, JobResponse, JobListResponse
from app.presentation.api.v1.schemas.scraping import ScrapeRequest, ScrapeResponse
from app.container import container
from app.shared.security.security import get_current_user

# Use Cases
from app.application.use_cases.jobs.create_job_use_case import CreateJobUseCase
from app.application.use_cases.jobs.get_job_details_use_case import GetJobDetailsUseCase
from app.application.use_cases.jobs.update_job_use_case import UpdateJobUseCase
from app.application.use_cases.jobs.delete_job_use_case import DeleteJobUseCase
from app.application.use_cases.jobs.list_jobs_use_case import ListJobsUseCase
from app.application.use_cases.search.search_jobs_use_case import SearchJobsUseCase
from app.application.use_cases.search.advanced_search_use_case import AdvancedSearchUseCase, AdvancedSearchRequest
from app.application.use_cases.scraping.scrape_jobs_use_case import ScrapeJobsUseCase, ScrapeJobsRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])


def get_create_job_use_case():
    return container.application.create_job_use_case()

def get_get_job_details_use_case():
    return container.application.get_job_details_use_case()

def get_list_jobs_use_case():
    return container.application.list_jobs_use_case()

def get_search_jobs_use_case():
    return container.application.search_jobs_use_case()

def get_advanced_search_use_case():
    return container.application.advanced_search_use_case()

def get_update_job_use_case():
    return container.application.update_job_use_case()

def get_delete_job_use_case():
    return container.application.delete_job_use_case()

def get_scrape_jobs_use_case():
    return container.application.scrape_jobs_use_case()


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    job_create: JobCreate,
    use_case: CreateJobUseCase = Depends(get_create_job_use_case),
):
    """
    Create a new job (admin only).

    Thin controller - delegates all business logic to CreateJobUseCase.
    """
    try:
        job = await use_case.execute(job_create)
        logger.info(f"New job created: {job.id}")
        return job

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating job: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create job"
        )


@router.post("/scrape", response_model=ScrapeResponse)
async def scrape_jobs_trigger(
    request: ScrapeRequest,
    use_case: ScrapeJobsUseCase = Depends(get_scrape_jobs_use_case),
    current_user = Depends(get_current_user)
):
    """
    Trigger a real-time scrape for jobs.
    """
    try:
        scrape_request = ScrapeJobsRequest(
            query=request.query,
            location=request.location,
            site_names=request.site_names,
            max_results=request.max_results,
            hours_old=request.hours_old,
            job_type=request.job_type,
            is_remote=request.is_remote,
            country_indeed=request.country_indeed
        )
        
        result = await use_case.execute(scrape_request)
        
        # Convert domain Job objects to JobResponse DTOs
        job_responses = []
        for job in result.processed_jobs:
            job_responses.append(JobResponse(
                id=job.id,
                title=job.title,
                company=job.company,
                location=job.location.format() if job.location else "Location not specified",
                source=job.source,
                salary_min=job.salary.min_amount if job.salary else None,
                salary_max=job.salary.max_amount if job.salary else None,
                salary_currency=job.salary.currency if job.salary else None,
                job_type=job.job_type.value if job.job_type else None,
                description=job.description,
                requirements=job.requirements,
                benefits=job.benefits,
                source_url=job.source_url,
                source_job_id=job.source_job_id,
                posted_date=job.posted_date,
                deadline=job.deadline,
                company_logo_url=job.company_logo_url,
                company_website=job.company_website,
                experience_level=job.experience_level.value if job.experience_level else None,
                skills=job.skills,
                is_remote=1 if job.is_remote() else 0,
                view_count=job.view_count,
                apply_count=job.apply_count,
                created_at=job.created_at,
                updated_at=job.updated_at,
                scraped_at=job.scraped_at
            ))
        
        return ScrapeResponse(
            saved_count=result.saved_count,
            duplicate_count=result.duplicate_count,
            error_count=result.error_count,
            total_processed=result.total_processed,
            jobs=job_responses
        )

    except Exception as e:
        logger.error(f"Error triggering scrape: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scrape failed: {str(e)}"
        )


@router.get("/search/advanced", response_model=JobListResponse)
async def advanced_search(
    query: Optional[str] = Query(None, description="Search query"),
    location: Optional[str] = Query(None, description="Job location"),
    job_type: Optional[str] = Query(None, description="Job type (fulltime, parttime, etc.)"),
    experience_level: Optional[str] = Query(None, description="Experience level required"),
    salary_min: Optional[float] = Query(None, description="Minimum salary"),
    salary_max: Optional[float] = Query(None, description="Maximum salary"),
    is_remote: Optional[bool] = Query(None, description="Is remote job"),
    source: Optional[str] = Query(None, description="Job source (LinkedIn, Indeed, etc.)"),
    posted_date: Optional[int] = Query(None, description="Posted within days (1, 7, 30, 90)"),
    skip: int = Query(0, ge=0, description="Number of results to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    use_case: AdvancedSearchUseCase = Depends(get_advanced_search_use_case),
):
    """
    Advanced search for jobs with multiple filter criteria.
    """
    try:
        request = AdvancedSearchRequest(
            query=query or "",
            location=location,
            job_type=job_type,
            experience_level=experience_level,
            salary_min=salary_min,
            salary_max=salary_max,
            is_remote=is_remote,
            source=source,
            posted_date=posted_date,
            skip=skip,
            limit=limit
        )
        result = await use_case.execute(request)

        # Convert domain Job objects to JobResponse DTOs
        job_responses = []
        for job in result.jobs:
            job_responses.append(JobResponse(
                id=job.id,
                title=job.title,
                company=job.company,
                location=job.location.format() if job.location else "Location not specified",
                source=job.source,
                salary_min=job.salary.min_amount if job.salary else None,
                salary_max=job.salary.max_amount if job.salary else None,
                salary_currency=job.salary.currency if job.salary else None,
                job_type=job.job_type.value if job.job_type else None,
                description=job.description,
                requirements=job.requirements,
                benefits=job.benefits,
                source_url=job.source_url,
                source_job_id=job.source_job_id,
                posted_date=job.posted_date,
                deadline=job.deadline,
                company_logo_url=job.company_logo_url,
                company_website=job.company_website,
                experience_level=job.experience_level.value if job.experience_level else None,
                skills=job.skills,
                is_remote=1 if job.is_remote() else 0,
                view_count=job.view_count,
                apply_count=job.apply_count,
                created_at=job.created_at,
                updated_at=job.updated_at,
                scraped_at=job.scraped_at
            ))

        return JobListResponse(
            total=result.total_count,
            page=skip // limit + 1,
            page_size=limit,
            items=job_responses
        )

    except Exception as e:
        logger.error(f"Error in advanced search: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/search", response_model=JobListResponse)
async def search_jobs(
    query: str = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    use_case: SearchJobsUseCase = Depends(get_search_jobs_use_case),
):
    """
    Search jobs by keyword.
    """
    try:
        result = await use_case.execute(
            query=query,
            skip=skip,
            limit=limit
        )

        # Convert domain Job objects to JobResponse DTOs
        job_responses = []
        for job in result.jobs:
            job_responses.append(JobResponse(
                id=job.id,
                title=job.title,
                company=job.company,
                location=job.location.format() if job.location else "Location not specified",
                source=job.source,
                salary_min=job.salary.min_amount if job.salary else None,
                salary_max=job.salary.max_amount if job.salary else None,
                salary_currency=job.salary.currency if job.salary else None,
                job_type=job.job_type.value if job.job_type else None,
                description=job.description,
                requirements=job.requirements,
                benefits=job.benefits,
                source_url=job.source_url,
                source_job_id=job.source_job_id,
                posted_date=job.posted_date,
                deadline=job.deadline,
                company_logo_url=job.company_logo_url,
                company_website=job.company_website,
                experience_level=job.experience_level.value if job.experience_level else None,
                skills=job.skills,
                is_remote=1 if job.is_remote() else 0,
                view_count=job.view_count,
                apply_count=job.apply_count,
                created_at=job.created_at,
                updated_at=job.updated_at,
                scraped_at=job.scraped_at
            ))

        return JobListResponse(
            total=result.total_count,
            page=skip // limit + 1,
            page_size=limit,
            items=job_responses
        )

    except Exception as e:
        logger.error(f"Error searching jobs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search jobs"
        )


@router.get("", response_model=JobListResponse)
async def list_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    source: Optional[str] = Query(None),
    use_case: ListJobsUseCase = Depends(get_list_jobs_use_case),
):
    """
    List jobs with pagination and filtering.
    """
    try:
        result = await use_case.execute(
            skip=skip,
            limit=limit,
            source=source
        )

        # Convert domain Job objects to JobResponse DTOs
        job_responses = []
        for job in result.jobs:
            job_responses.append(JobResponse(
                id=job.id,
                title=job.title,
                company=job.company,
                location=job.location.format() if job.location else "Location not specified",
                source=job.source,
                salary_min=job.salary.min_amount if job.salary else None,
                salary_max=job.salary.max_amount if job.salary else None,
                salary_currency=job.salary.currency if job.salary else None,
                job_type=job.job_type.value if job.job_type else None,
                description=job.description,
                requirements=job.requirements,
                benefits=job.benefits,
                source_url=job.source_url,
                source_job_id=job.source_job_id,
                posted_date=job.posted_date,
                deadline=job.deadline,
                company_logo_url=job.company_logo_url,
                company_website=job.company_website,
                experience_level=job.experience_level.value if job.experience_level else None,
                skills=job.skills,
                is_remote=1 if job.is_remote() else 0,
                view_count=job.view_count,
                apply_count=job.apply_count,
                created_at=job.created_at,
                updated_at=job.updated_at,
                scraped_at=job.scraped_at
            ))

        return JobListResponse(
            total=result.total_count,
            page=skip // limit + 1,
            page_size=limit,
            items=job_responses
        )

    except Exception as e:
        logger.error(f"Error listing jobs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list jobs"
        )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: UUID,
    use_case: GetJobDetailsUseCase = Depends(get_get_job_details_use_case),
):
    """
    Get job by ID.
    """
    try:
        job = await use_case.execute(job_id)

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )

        # Convert domain Job object to JobResponse DTO
        return JobResponse(
            id=job.id,
            title=job.title,
            company=job.company,
            location=job.location.format() if job.location else "Location not specified",
            source=job.source,
            salary_min=job.salary.min_amount if job.salary else None,
            salary_max=job.salary.max_amount if job.salary else None,
            salary_currency=job.salary.currency if job.salary else None,
            job_type=job.job_type.value if job.job_type else None,
            description=job.description,
            requirements=job.requirements,
            benefits=job.benefits,
            source_url=job.source_url,
            source_job_id=job.source_job_id,
            posted_date=job.posted_date,
            deadline=job.deadline,
            company_logo_url=job.company_logo_url,
            company_website=job.company_website,
            experience_level=job.experience_level.value if job.experience_level else None,
            skills=job.skills,
            is_remote=1 if job.is_remote() else 0,
            view_count=job.view_count,
            apply_count=job.apply_count,
            created_at=job.created_at,
            updated_at=job.updated_at,
            scraped_at=job.scraped_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job {job_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve job"
        )


@router.put("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: UUID,
    job_update: JobUpdate,
    use_case: UpdateJobUseCase = Depends(get_update_job_use_case),
):
    """
    Update job (admin only).
    """
    try:
        job = await use_case.execute(job_id, job_update)

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )

        logger.info(f"Job updated: {job_id}")
        return job

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating job {job_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update job"
        )


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: UUID,
    use_case: DeleteJobUseCase = Depends(get_delete_job_use_case),
):
    """
    Delete job (admin only).
    """
    try:
        success = await use_case.execute(job_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )

        logger.info(f"Job deleted: {job_id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting job {job_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete job"
        )