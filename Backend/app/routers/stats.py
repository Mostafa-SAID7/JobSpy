"""
Statistics API Endpoints
Provides endpoints for retrieving cached statistics
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.stats_repo import StatsRepository
from app.services.stats_service import StatsService

router = APIRouter(prefix="/api/v1/stats", tags=["Statistics"])


async def get_stats_service(session: AsyncSession = Depends(get_db)) -> StatsService:
    """Dependency to get stats service"""
    stats_repo = StatsRepository(session)
    return StatsService(stats_repo)


@router.get("/jobs", summary="Get Job Statistics")
async def get_job_statistics(
    use_cache: bool = True,
    stats_service: StatsService = Depends(get_stats_service),
):
    """
    Get comprehensive job statistics
    
    **Query Parameters:**
    - `use_cache` (bool, default: True): Whether to use cached results
    
    **Returns:**
    - `total_jobs`: Total number of jobs
    - `jobs_by_source`: Count of jobs by source
    - `jobs_by_type`: Count of jobs by type
    - `remote_jobs`: Count of remote jobs
    - `salary_stats`: Salary statistics (min, max, average)
    - `jobs_posted_today`: Jobs posted today
    - `jobs_posted_this_week`: Jobs posted this week
    - `top_companies`: Top 10 companies by job count
    - `top_locations`: Top 10 locations by job count
    - `timestamp`: When statistics were computed
    """
    try:
        stats = await stats_service.get_job_statistics(use_cache=use_cache)
        return {
            "status": "success",
            "data": stats,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users", summary="Get User Statistics")
async def get_user_statistics(
    use_cache: bool = True,
    stats_service: StatsService = Depends(get_stats_service),
):
    """
    Get user statistics
    
    **Query Parameters:**
    - `use_cache` (bool, default: True): Whether to use cached results
    
    **Returns:**
    - `total_users`: Total number of users
    - `active_users_30d`: Active users in last 30 days
    - `active_users_7d`: Active users in last 7 days
    - `active_users_1d`: Active users in last 1 day
    - `timestamp`: When statistics were computed
    """
    try:
        stats = await stats_service.get_user_statistics(use_cache=use_cache)
        return {
            "status": "success",
            "data": stats,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/searches", summary="Get Search Statistics")
async def get_search_statistics(
    use_cache: bool = True,
    stats_service: StatsService = Depends(get_stats_service),
):
    """
    Get search statistics
    
    **Query Parameters:**
    - `use_cache` (bool, default: True): Whether to use cached results
    
    **Returns:**
    - `total_searches`: Total number of searches
    - `unique_users`: Number of unique users who searched
    - `avg_searches_per_user`: Average searches per user
    - `trending_searches`: Top 10 trending searches from last 7 days
    - `timestamp`: When statistics were computed
    """
    try:
        stats = await stats_service.get_search_statistics(use_cache=use_cache)
        return {
            "status": "success",
            "data": stats,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/saved-jobs", summary="Get Saved Jobs Statistics")
async def get_saved_jobs_statistics(
    use_cache: bool = True,
    stats_service: StatsService = Depends(get_stats_service),
):
    """
    Get saved jobs statistics
    
    **Query Parameters:**
    - `use_cache` (bool, default: True): Whether to use cached results
    
    **Returns:**
    - `total_saved_jobs`: Total number of saved jobs
    - `timestamp`: When statistics were computed
    """
    try:
        stats = await stats_service.get_saved_jobs_statistics(use_cache=use_cache)
        return {
            "status": "success",
            "data": stats,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard", summary="Get Dashboard Statistics")
async def get_dashboard_statistics(
    use_cache: bool = True,
    stats_service: StatsService = Depends(get_stats_service),
):
    """
    Get comprehensive dashboard statistics
    
    **Query Parameters:**
    - `use_cache` (bool, default: True): Whether to use cached results
    
    **Returns:**
    - `jobs`: Job statistics
    - `users`: User statistics
    - `searches`: Search statistics
    - `saved_jobs`: Saved jobs statistics
    - `timestamp`: When statistics were computed
    """
    try:
        stats = await stats_service.get_dashboard_statistics(use_cache=use_cache)
        return {
            "status": "success",
            "data": stats,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/invalidate/jobs", summary="Invalidate Job Statistics Cache")
async def invalidate_job_statistics(
    stats_service: StatsService = Depends(get_stats_service),
):
    """
    Invalidate job statistics cache
    
    **Returns:**
    - `status`: Success or error status
    - `message`: Status message
    """
    try:
        success = await stats_service.invalidate_job_statistics()
        if success:
            return {
                "status": "success",
                "message": "Job statistics cache invalidated",
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to invalidate cache")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/invalidate/users", summary="Invalidate User Statistics Cache")
async def invalidate_user_statistics(
    stats_service: StatsService = Depends(get_stats_service),
):
    """
    Invalidate user statistics cache
    
    **Returns:**
    - `status`: Success or error status
    - `message`: Status message
    """
    try:
        success = await stats_service.invalidate_user_statistics()
        if success:
            return {
                "status": "success",
                "message": "User statistics cache invalidated",
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to invalidate cache")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/invalidate/searches", summary="Invalidate Search Statistics Cache")
async def invalidate_search_statistics(
    stats_service: StatsService = Depends(get_stats_service),
):
    """
    Invalidate search statistics cache
    
    **Returns:**
    - `status`: Success or error status
    - `message`: Status message
    """
    try:
        success = await stats_service.invalidate_search_statistics()
        if success:
            return {
                "status": "success",
                "message": "Search statistics cache invalidated",
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to invalidate cache")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/invalidate/saved-jobs", summary="Invalidate Saved Jobs Statistics Cache")
async def invalidate_saved_jobs_statistics(
    stats_service: StatsService = Depends(get_stats_service),
):
    """
    Invalidate saved jobs statistics cache
    
    **Returns:**
    - `status`: Success or error status
    - `message`: Status message
    """
    try:
        success = await stats_service.invalidate_saved_jobs_statistics()
        if success:
            return {
                "status": "success",
                "message": "Saved jobs statistics cache invalidated",
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to invalidate cache")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/invalidate/all", summary="Invalidate All Statistics Cache")
async def invalidate_all_statistics(
    stats_service: StatsService = Depends(get_stats_service),
):
    """
    Invalidate all statistics cache
    
    **Returns:**
    - `status`: Success or error status
    - `message`: Status message
    """
    try:
        success = await stats_service.invalidate_all_statistics()
        if success:
            return {
                "status": "success",
                "message": "All statistics cache invalidated",
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to invalidate cache")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
