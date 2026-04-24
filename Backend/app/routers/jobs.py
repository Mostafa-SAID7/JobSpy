from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional, Dict, Any
from app.core.database import get_db
from app.schemas.job import JobCreate, JobUpdate, JobResponse, JobListResponse
from app.repositories.job_repo import JobRepository
from app.services.search_service import SearchService
from app.utils.security import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(job_create: JobCreate, db: AsyncSession = Depends(get_db)):
    """Create a new job (admin only)."""
    job_repo = JobRepository(db)
    search_service = SearchService(db)
    
    # Check if job already exists
    existing_job = await job_repo.get_by_source_url(job_create.source_url)
    if existing_job:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job with this source URL already exists"
        )
    
    try:
        job = await job_repo.create(job_create)
        await db.commit()
        await db.refresh(job)
        
        # Invalidate all caches when new job is added
        await job_repo.invalidate_all_jobs_cache()
        await search_service.invalidate_all_search_cache()
        logger.info(f"New job created: {job.id}, all caches invalidated")
        
        return job
    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get job by ID."""
    job_repo = JobRepository(db)
    job = await job_repo.get_by_id(job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Increment view count
    await job_repo.increment_view_count(job_id)
    await db.commit()
    
    return job


@router.get("", response_model=JobListResponse)
async def list_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    source: str = Query(None),
    company: str = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """List jobs with pagination and filtering."""
    job_repo = JobRepository(db)
    
    if source:
        jobs = await job_repo.get_by_source(source, skip, limit)
        total = await job_repo.count_by_source(source)
    elif company:
        jobs = await job_repo.get_by_company(company, skip, limit)
        total = len(jobs)
    else:
        jobs = await job_repo.get_all(skip, limit)
        total = await job_repo.count()
    
    return JobListResponse(
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        items=jobs
    )


@router.post("/search", response_model=JobListResponse)
async def search_jobs(
    query: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Search jobs by keyword."""
    job_repo = JobRepository(db)
    jobs = await job_repo.search(query, skip, limit)
    
    return JobListResponse(
        total=len(jobs),
        page=skip // limit + 1,
        page_size=limit,
        items=jobs
    )


@router.post("/search/advanced")
async def advanced_search(
    query: str = Query(..., description="Search query"),
    location: Optional[str] = Query(None, description="Job location"),
    job_type: Optional[str] = Query(None, description="Job type (fulltime, parttime, etc.)"),
    experience_level: Optional[str] = Query(None, description="Experience level required"),
    salary_min: Optional[int] = Query(None, description="Minimum salary"),
    salary_max: Optional[int] = Query(None, description="Maximum salary"),
    is_remote: Optional[bool] = Query(None, description="Is remote job"),
    skip: int = Query(0, ge=0, description="Number of results to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Advanced search for jobs with multiple filter criteria.
    
    This endpoint supports caching of search results with all parameters.
    Cache is automatically invalidated when jobs are added or updated.
    
    Query Parameters:
    - query: Search query string (required)
    - location: Filter by job location
    - job_type: Filter by job type
    - experience_level: Filter by experience level
    - salary_min: Filter by minimum salary
    - salary_max: Filter by maximum salary
    - is_remote: Filter by remote work availability
    - skip: Pagination offset (default: 0)
    - limit: Results per page (default: 20, max: 100)
    
    Returns:
    - results: List of matching jobs
    - total_count: Total number of matching jobs
    - has_more: Whether there are more results
    - cache_key: Cache key used for this search (for debugging)
    """
    try:
        search_service = SearchService(db)
        
        # Build search parameters
        search_params = {
            "query": query,
            "location": location,
            "job_type": job_type,
            "experience_level": experience_level,
            "salary_min": salary_min,
            "salary_max": salary_max,
            "is_remote": is_remote,
            "skip": skip,
            "limit": limit,
        }
        
        # Perform advanced search
        result = await search_service.advanced_search(current_user.id, search_params)
        
        # Generate cache key for debugging
        filters = {k: v for k, v in search_params.items() if v is not None and k not in ["query", "skip", "limit"]}
        cache_key = search_service._generate_search_cache_key(query, filters, skip, limit)
        
        return {
            **result,
            "cache_key": cache_key,
        }
    except Exception as e:
        logger.error(f"Error in advanced search: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.put("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: UUID,
    job_update: JobUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update job (admin only)."""
    job_repo = JobRepository(db)
    search_service = SearchService(db)
    
    job = await job_repo.update(job_id, job_update)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    await db.commit()
    
    # Invalidate all caches when job is updated
    await job_repo.invalidate_job_cache(job_id)
    await job_repo.invalidate_all_jobs_cache()
    await search_service.invalidate_all_search_cache()
    logger.info(f"Job updated: {job_id}, all caches invalidated")
    
    return job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(job_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete job (admin only)."""
    job_repo = JobRepository(db)
    search_service = SearchService(db)
    
    success = await job_repo.delete(job_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    await db.commit()
    
    # Invalidate all caches when job is deleted
    await job_repo.invalidate_job_cache(job_id)
    await job_repo.invalidate_all_jobs_cache()
    await search_service.invalidate_all_search_cache()
    logger.info(f"Job deleted: {job_id}, all caches invalidated")
