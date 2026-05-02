"""
Saved Jobs Router - JobSpy Backend (Clean Architecture)

Thin controllers that delegate all business logic to use cases.
Uses dependency injection for all dependencies.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import logging

from dependency_injector.wiring import inject, Provide

from app.core.database import get_db
from app.schemas.saved_job import SavedJobCreate, SavedJobUpdate, SavedJobDetailResponse, SavedJobListResponse
from app.presentation.api.v1.dependencies import Container
from app.utils.security import get_current_user

# Use Cases
from app.application.use_cases.saved_jobs.save_job_use_case import SaveJobUseCase
from app.application.use_cases.saved_jobs.list_saved_jobs_use_case import ListSavedJobsUseCase
from app.application.use_cases.saved_jobs.update_saved_job_use_case import UpdateSavedJobUseCase
from app.application.use_cases.saved_jobs.delete_saved_job_use_case import DeleteSavedJobUseCase
from app.application.use_cases.saved_jobs.unsave_job_use_case import UnsaveJobUseCase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/saved-jobs", tags=["saved-jobs"])


@router.post("", response_model=SavedJobDetailResponse, status_code=status.HTTP_201_CREATED)
@inject
async def save_job(
    saved_job_create: SavedJobCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    use_case: SaveJobUseCase = Depends(Provide[Container.save_job_use_case]),
):
    """
    Save a job.
    
    Thin controller - delegates to SaveJobUseCase.
    """
    try:
        # Provide db session to container
        Container.db_session.override(db)
        
        # Execute use case
        saved_job = await use_case.execute(current_user.id, saved_job_create)
        
        # Commit transaction
        await db.commit()
        await db.refresh(saved_job)
        
        # Reload with job details
        saved_job = await use_case.saved_job_repository.get_by_id(saved_job.id)
        
        logger.info(f"Job saved: {saved_job.id}")
        
        return SavedJobDetailResponse(
            id=saved_job.id,
            user_id=saved_job.user_id,
            job=saved_job.job,
            notes=saved_job.notes,
            saved_at=saved_job.saved_at,
            updated_at=saved_job.updated_at
        )
        
    except ValueError as e:
        await db.rollback()
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Error saving job: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save job"
        )


@router.get("", response_model=SavedJobListResponse)
@inject
async def list_saved_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    use_case: ListSavedJobsUseCase = Depends(Provide[Container.list_saved_jobs_use_case]),
):
    """
    Get all saved jobs for current user.
    
    Thin controller - delegates to ListSavedJobsUseCase.
    """
    try:
        # Provide db session to container
        Container.db_session.override(db)
        
        # Execute use case
        result = await use_case.execute(current_user.id, skip, limit)
        
        # Build response items
        items = []
        for saved_job in result.saved_jobs:
            items.append(SavedJobDetailResponse(
                id=saved_job.id,
                user_id=saved_job.user_id,
                job=saved_job.job,
                notes=saved_job.notes,
                saved_at=saved_job.saved_at,
                updated_at=saved_job.updated_at
            ))
        
        return SavedJobListResponse(
            total=result.total_count,
            page=result.page,
            page_size=result.page_size,
            items=items
        )
        
    except Exception as e:
        logger.error(f"Error listing saved jobs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list saved jobs"
        )


@router.put("/{saved_job_id}", response_model=SavedJobDetailResponse)
@inject
async def update_saved_job(
    saved_job_id: UUID,
    saved_job_update: SavedJobUpdate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    use_case: UpdateSavedJobUseCase = Depends(Provide[Container.update_saved_job_use_case]),
):
    """
    Update saved job notes.
    
    Thin controller - delegates to UpdateSavedJobUseCase.
    """
    try:
        # Provide db session to container
        Container.db_session.override(db)
        
        # Execute use case
        updated_saved_job = await use_case.execute(saved_job_id, current_user.id, saved_job_update)
        
        # Commit transaction
        await db.commit()
        
        logger.info(f"Saved job updated: {saved_job_id}")
        
        return SavedJobDetailResponse(
            id=updated_saved_job.id,
            user_id=updated_saved_job.user_id,
            job=updated_saved_job.job,
            notes=updated_saved_job.notes,
            saved_at=updated_saved_job.saved_at,
            updated_at=updated_saved_job.updated_at
        )
        
    except ValueError as e:
        await db.rollback()
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        if "not authorized" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating saved job: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update saved job"
        )


@router.delete("/{saved_job_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_saved_job(
    saved_job_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    use_case: DeleteSavedJobUseCase = Depends(Provide[Container.delete_saved_job_use_case]),
):
    """
    Delete saved job.
    
    Thin controller - delegates to DeleteSavedJobUseCase.
    """
    try:
        # Provide db session to container
        Container.db_session.override(db)
        
        # Execute use case
        success = await use_case.execute(saved_job_id, current_user.id)
        
        # Commit transaction
        await db.commit()
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Saved job not found"
            )
        
        logger.info(f"Saved job deleted: {saved_job_id}")
        
    except ValueError as e:
        await db.rollback()
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        if "not authorized" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting saved job: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete saved job"
        )


@router.delete("/job/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def unsave_job(
    job_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    use_case: UnsaveJobUseCase = Depends(Provide[Container.unsave_job_use_case]),
):
    """
    Unsave a job.
    
    Thin controller - delegates to UnsaveJobUseCase.
    """
    try:
        # Provide db session to container
        Container.db_session.override(db)
        
        # Execute use case
        success = await use_case.execute(current_user.id, job_id)
        
        # Commit transaction
        await db.commit()
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Saved job not found"
            )
        
        logger.info(f"Job unsaved: {job_id}")
        
    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error unsaving job: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unsave job"
        )
