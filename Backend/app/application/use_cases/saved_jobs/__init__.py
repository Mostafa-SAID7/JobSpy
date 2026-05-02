"""
Saved Jobs Use Cases

Use cases for saved jobs operations.
"""

from app.application.use_cases.saved_jobs.save_job_use_case import SaveJobUseCase
from app.application.use_cases.saved_jobs.list_saved_jobs_use_case import ListSavedJobsUseCase
from app.application.use_cases.saved_jobs.update_saved_job_use_case import UpdateSavedJobUseCase
from app.application.use_cases.saved_jobs.delete_saved_job_use_case import DeleteSavedJobUseCase
from app.application.use_cases.saved_jobs.unsave_job_use_case import UnsaveJobUseCase

__all__ = [
    "SaveJobUseCase",
    "ListSavedJobsUseCase",
    "UpdateSavedJobUseCase",
    "DeleteSavedJobUseCase",
    "UnsaveJobUseCase",
]
