from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.core.database import get_db
from app.schemas.saved_job import SavedJobCreate, SavedJobUpdate, SavedJobDetailResponse, SavedJobListResponse
from app.repositories.saved_job_repo import SavedJobRepository
from app.repositories.job_repo import JobRepository
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/v1/saved-jobs", tags=["saved-jobs"])


@router.post("", response_model=SavedJobDetailResponse, status_code=status.HTTP_201_CREATED)
async def save_job(
    saved_job_create: SavedJobCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Save a job."""
    saved_job_repo = SavedJobRepository(db)
    job_repo = JobRepository(db)
    
    # Check if job exists
    job = await job_repo.get_by_id(saved_job_create.job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check if already saved
    is_saved = await saved_job_repo.is_saved(current_user.id, saved_job_create.job_id)
    if is_saved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job is already saved"
        )
    
    try:
        saved_job = await saved_job_repo.create(current_user.id, saved_job_create)
        await db.commit()
        await db.refresh(saved_job)
        
        # Reload with job details
        saved_job = await saved_job_repo.get_by_id(saved_job.id)
        return SavedJobDetailResponse(
            id=saved_job.id,
            user_id=saved_job.user_id,
            job=job,
            notes=saved_job.notes,
            saved_at=saved_job.saved_at,
            updated_at=saved_job.updated_at
        )
    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("", response_model=SavedJobListResponse)
async def list_saved_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all saved jobs for current user."""
    saved_job_repo = SavedJobRepository(db)
    saved_jobs = await saved_job_repo.get_by_user(current_user.id, skip, limit)
    total = await saved_job_repo.count_by_user(current_user.id)
    
    items = []
    for saved_job in saved_jobs:
        items.append(SavedJobDetailResponse(
            id=saved_job.id,
            user_id=saved_job.user_id,
            job=saved_job.job,
            notes=saved_job.notes,
            saved_at=saved_job.saved_at,
            updated_at=saved_job.updated_at
        ))
    
    return SavedJobListResponse(
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        items=items
    )


@router.put("/{saved_job_id}", response_model=SavedJobDetailResponse)
async def update_saved_job(
    saved_job_id: UUID,
    saved_job_update: SavedJobUpdate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update saved job notes."""
    saved_job_repo = SavedJobRepository(db)
    saved_job = await saved_job_repo.get_by_id(saved_job_id)
    
    if not saved_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved job not found"
        )
    
    if saved_job.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this saved job"
        )
    
    updated_saved_job = await saved_job_repo.update(saved_job_id, saved_job_update)
    await db.commit()
    
    return SavedJobDetailResponse(
        id=updated_saved_job.id,
        user_id=updated_saved_job.user_id,
        job=updated_saved_job.job,
        notes=updated_saved_job.notes,
        saved_at=updated_saved_job.saved_at,
        updated_at=updated_saved_job.updated_at
    )


@router.delete("/{saved_job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_saved_job(
    saved_job_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete saved job."""
    saved_job_repo = SavedJobRepository(db)
    saved_job = await saved_job_repo.get_by_id(saved_job_id)
    
    if not saved_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved job not found"
        )
    
    if saved_job.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this saved job"
        )
    
    success = await saved_job_repo.delete(saved_job_id)
    await db.commit()
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved job not found"
        )


@router.delete("/job/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unsave_job(
    job_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Unsave a job."""
    saved_job_repo = SavedJobRepository(db)
    success = await saved_job_repo.delete_by_user_and_job(current_user.id, job_id)
    await db.commit()
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved job not found"
        )
