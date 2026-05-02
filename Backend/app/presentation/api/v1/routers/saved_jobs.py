"""
Saved Jobs Router - JobSpy Backend (Clean Architecture) - Manual DI Getters
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from uuid import UUID
import logging

from app.infrastructure.persistence.sqlalchemy.database import get_db
from app.presentation.api.v1.schemas.saved_job import SavedJobCreate, SavedJobUpdate, SavedJobDetailResponse, SavedJobListResponse
from app.container import container
from app.shared.security.security import get_current_user

from app.application.use_cases.saved_jobs.save_job_use_case import SaveJobUseCase
from app.application.use_cases.saved_jobs.list_saved_jobs_use_case import ListSavedJobsUseCase
from app.application.use_cases.saved_jobs.update_saved_job_use_case import UpdateSavedJobUseCase
from app.application.use_cases.saved_jobs.delete_saved_job_use_case import DeleteSavedJobUseCase
from app.application.use_cases.saved_jobs.unsave_job_use_case import UnsaveJobUseCase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/saved-jobs", tags=["saved-jobs"])


def get_save_job_uc(): return container.application.save_job_use_case()
def get_list_saved_jobs_uc(): return container.application.list_saved_jobs_use_case()
def get_update_saved_job_uc(): return container.application.update_saved_job_use_case()
def get_delete_saved_job_uc(): return container.application.delete_saved_job_use_case()
def get_unsave_job_uc(): return container.application.unsave_job_use_case()


@router.post("", response_model=SavedJobDetailResponse, status_code=status.HTTP_201_CREATED)
async def save_job(
    saved_job_create: SavedJobCreate,
    current_user=Depends(get_current_user),
    use_case: SaveJobUseCase = Depends(get_save_job_uc),
):
    try:
        saved_job = await use_case.execute(current_user.id, saved_job_create)
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
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error saving job: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save job")


@router.get("", response_model=SavedJobListResponse)
async def list_saved_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user=Depends(get_current_user),
    use_case: ListSavedJobsUseCase = Depends(get_list_saved_jobs_uc),
):
    try:
        result = await use_case.execute(current_user.id, skip, limit)
        items = [
            SavedJobDetailResponse(
                id=sj.id, user_id=sj.user_id, job=sj.job,
                notes=sj.notes, saved_at=sj.saved_at, updated_at=sj.updated_at
            )
            for sj in result.saved_jobs
        ]
        return SavedJobListResponse(
            total=result.total_count,
            page=result.page,
            page_size=result.page_size,
            items=items
        )
    except Exception as e:
        logger.error(f"Error listing saved jobs: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to list saved jobs")


@router.put("/{saved_job_id}", response_model=SavedJobDetailResponse)
async def update_saved_job(
    saved_job_id: UUID,
    saved_job_update: SavedJobUpdate,
    current_user=Depends(get_current_user),
    use_case: UpdateSavedJobUseCase = Depends(get_update_saved_job_uc),
):
    try:
        sj = await use_case.execute(saved_job_id, current_user.id, saved_job_update)
        logger.info(f"Saved job updated: {saved_job_id}")
        return SavedJobDetailResponse(
            id=sj.id, user_id=sj.user_id, job=sj.job,
            notes=sj.notes, saved_at=sj.saved_at, updated_at=sj.updated_at
        )
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        if "not authorized" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating saved job: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update saved job")


@router.delete("/{saved_job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_saved_job(
    saved_job_id: UUID,
    current_user=Depends(get_current_user),
    use_case: DeleteSavedJobUseCase = Depends(get_delete_saved_job_uc),
):
    try:
        success = await use_case.execute(saved_job_id, current_user.id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved job not found")
        logger.info(f"Saved job deleted: {saved_job_id}")
    except HTTPException:
        raise
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        if "not authorized" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting saved job: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete saved job")


@router.delete("/job/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unsave_job(
    job_id: UUID,
    current_user=Depends(get_current_user),
    use_case: UnsaveJobUseCase = Depends(get_unsave_job_uc),
):
    try:
        success = await use_case.execute(current_user.id, job_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved job not found")
        logger.info(f"Job unsaved: {job_id}")
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error unsaving job: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to unsave job")
