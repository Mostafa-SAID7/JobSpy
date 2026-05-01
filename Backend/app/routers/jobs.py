"""
Jobs Router - JobSpy Backend (Clean Architecture)

Thin controllers that delegate all business logic to use cases.
Uses dependency injection for all dependencies.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional
from datetime import datetime
import logging

from dependency_injector.wiring import inject, Provide

from app.core.database import get_db
from app.schemas.job import JobCreate, JobUpdate, JobResponse, JobListResponse
from app.presentation.api.v1.dependencies import Container
from app.utils.security import get_current_user

# Use Cases
from app.application.use_cases.jobs.create_job_use_case import CreateJobUseCase
from app.application.use_cases.jobs.get_job_details_use_case import GetJobDetailsUseCase
from app.application.use_cases.jobs.update_job_use_case import UpdateJobUseCase
from app.application.use_cases.jobs.delete_job_use_case import DeleteJobUseCase
from app.application.use_cases.jobs.list_jobs_use_case import ListJobsUseCase
from app.application.use_cases.search.search_jobs_use_case import SearchJobsUseCase
from app.application.use_cases.search.advanced_search_use_case import AdvancedSearchUseCase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])

@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
@inject
async def create_job(
    job_create: JobCreate,
    db: AsyncSession = Depends(get_db),
    use_case: CreateJobUseCase = Depends(Provide[Container.create_job_use_case]),
):
    """
    Create a new job (admin only).
    
    Thin controller - delegates all business logic to CreateJobUseCase.
    """
    try:
        # Provide db session to container
        Container.db_session.override(db)
        
        # Execute use case
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


@router.get("/debug", tags=["Debug"])
async def debug_jobs(db: AsyncSession = Depends(get_db)):
    """Debug endpoint to check jobs data."""
    from app.repositories.job_repo import JobRepository
    
    job_repo = JobRepository(db)
    
    # Get first few jobs
    jobs = await job_repo.get_all(0, 3)
    count = await job_repo.count()
    
    return {
        "total_jobs": count,
        "sample_jobs": [
            {
                "id": str(job.id),
                "title": job.title,
                "company": job.company,
                "location": job.location
            } for job in jobs
        ],
        "api_working": True,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/api-test", tags=["Test"])
async def test_jobs_endpoint(db: AsyncSession = Depends(get_db)):
    """Test endpoint to verify jobs API is working."""
    from app.repositories.job_repo import JobRepository
    
    job_repo = JobRepository(db)
    count = await job_repo.count()
    
    return {
        "status": "success",
        "message": "Jobs API is working",
        "total_jobs": count,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/{job_id}", response_model=JobResponse)
@inject
async def get_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    use_case: GetJobDetailsUseCase = Depends(Provide[Container.get_job_details_use_case]),
):
    """
    Get job by ID.
    
    Thin controller - delegates to GetJobDetailsUseCase.
    """
    try:
        # Provide db session to container
        Container.db_session.override(db)
        
        # Execute use case
        job = await use_case.execute(job_id)
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        return job
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job {job_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve job"
        )


@router.get("", response_model=JobListResponse)
@inject
async def list_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    source: Optional[str] = Query(None),
    company: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    use_case: ListJobsUseCase = Depends(Provide[Container.list_jobs_use_case]),
):
    """
    List jobs with pagination and filtering.
    
    Thin controller - delegates to ListJobsUseCase.
    Note: Company filtering is handled by repository directly for now.
    """
    try:
        # Provide db session to container
        Container.db_session.override(db)
        
        # If company filter is provided, use repository directly (temporary)
        # TODO: Add company parameter to ListJobsUseCase
        if company:
            from app.repositories.job_repo import JobRepository
            job_repo = JobRepository(db)
            jobs = await job_repo.get_by_company(company, skip, limit)
            total = len(jobs)
            
            return JobListResponse(
                total=total,
                page=skip // limit + 1,
                page_size=limit,
                items=jobs
            )
        
        # Execute use case for source filtering or no filtering
        result = await use_case.execute(
            skip=skip,
            limit=limit,
            source=source
        )
        
        return JobListResponse(
            total=result.total_count,
            page=skip // limit + 1,
            page_size=limit,
            items=result.jobs
        )
        
    except Exception as e:
        logger.error(f"Error listing jobs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list jobs"
        )


@router.post("/search", response_model=JobListResponse)
@inject
async def search_jobs(
    query: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    use_case: SearchJobsUseCase = Depends(Provide[Container.search_jobs_use_case]),
):
    """
    Search jobs by keyword.
    
    Thin controller - delegates to SearchJobsUseCase.
    """
    try:
        # Provide db session to container
        Container.db_session.override(db)
        
        # Execute use case
        result = await use_case.execute(
            query=query,
            skip=skip,
            limit=limit
        )
        
        return JobListResponse(
            total=result.total_count,
            page=skip // limit + 1,
            page_size=limit,
            items=result.jobs
        )
        
    except Exception as e:
        logger.error(f"Error searching jobs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search jobs"
        )


@router.post("/search/advanced")
@inject
async def advanced_search(
    query: str = Query(..., description="Search query"),
    location: Optional[str] = Query(None, description="Job location"),
    job_type: Optional[str] = Query(None, description="Job type (fulltime, parttime, etc.)"),
    experience_level: Optional[str] = Query(None, description="Experience level required"),
    salary_min: Optional[int] = Query(None, description="Minimum salary"),
    salary_max: Optional[int] = Query(None, description="Maximum salary"),
    is_remote: Optional[bool] = Query(None, description="Is remote job"),
    source: Optional[str] = Query(None, description="Job source (LinkedIn, Indeed, etc.)"),
    skip: int = Query(0, ge=0, description="Number of results to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    use_case: AdvancedSearchUseCase = Depends(Provide[Container.advanced_search_use_case]),
):
    """
    Advanced search for jobs with multiple filter criteria.
    
    Thin controller - delegates to AdvancedSearchUseCase.
    
    Query Parameters:
    - query: Search query string (required)
    - location: Filter by job location
    - job_type: Filter by job type
    - experience_level: Filter by experience level
    - salary_min: Filter by minimum salary
    - salary_max: Filter by maximum salary
    - is_remote: Filter by remote work availability
    - source: Filter by job source
    - skip: Pagination offset (default: 0)
    - limit: Results per page (default: 20, max: 100)
    
    Returns:
    - results: List of matching jobs
    - total_count: Total number of matching jobs
    - has_more: Whether there are more results
    """
    try:
        # Provide db session to container
        Container.db_session.override(db)
        
        # Build filters dictionary
        filters = {}
        if location:
            filters["location"] = location
        if job_type:
            filters["job_type"] = job_type
        if experience_level:
            filters["experience_level"] = experience_level
        if salary_min is not None:
            filters["salary_min"] = salary_min
        if salary_max is not None:
            filters["salary_max"] = salary_max
        if is_remote is not None:
            filters["is_remote"] = is_remote
        if source:
            filters["source"] = source
        
        # Execute use case
        result = await use_case.execute(
            query=query,
            filters=filters,
            user_id=current_user.id,
            skip=skip,
            limit=limit
        )
        
        return {
            "results": result.jobs,
            "total_count": result.total_count,
            "has_more": skip + limit < result.total_count,
            "page": skip // limit + 1,
            "page_size": limit
        }
        
    except Exception as e:
        logger.error(f"Error in advanced search: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.put("/{job_id}", response_model=JobResponse)
@inject
async def update_job(
    job_id: UUID,
    job_update: JobUpdate,
    db: AsyncSession = Depends(get_db),
    use_case: UpdateJobUseCase = Depends(Provide[Container.update_job_use_case]),
):
    """
    Update job (admin only).
    
    Thin controller - delegates to UpdateJobUseCase.
    """
    try:
        # Provide db session to container
        Container.db_session.override(db)
        
        # Execute use case
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
@inject
async def delete_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    use_case: DeleteJobUseCase = Depends(Provide[Container.delete_job_use_case]),
):
    """
    Delete job (admin only).
    
    Thin controller - delegates to DeleteJobUseCase.
    """
    try:
        # Provide db session to container
        Container.db_session.override(db)
        
        # Execute use case
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