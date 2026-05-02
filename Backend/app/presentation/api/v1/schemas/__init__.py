from app.presentation.api.v1.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserDetailResponse,
)
from app.presentation.api.v1.schemas.job import (
    JobBase,
    JobCreate,
    JobUpdate,
    JobResponse,
    JobDetailResponse,
    JobListResponse,
)
from app.presentation.api.v1.schemas.saved_job import (
    SavedJobBase,
    SavedJobCreate,
    SavedJobUpdate,
    SavedJobResponse,
    SavedJobDetailResponse,
    SavedJobListResponse,
)
from app.presentation.api.v1.schemas.search_history import (
    SearchHistoryBase,
    SearchHistoryCreate,
    SearchHistoryResponse,
    SearchHistoryListResponse,
)
from app.presentation.api.v1.schemas.alert import (
    AlertBase,
    AlertCreate,
    AlertUpdate,
    AlertResponse,
    AlertListResponse,
)

__all__ = [
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserDetailResponse",
    "JobBase",
    "JobCreate",
    "JobUpdate",
    "JobResponse",
    "JobDetailResponse",
    "JobListResponse",
    "SavedJobBase",
    "SavedJobCreate",
    "SavedJobUpdate",
    "SavedJobResponse",
    "SavedJobDetailResponse",
    "SavedJobListResponse",
    "SearchHistoryBase",
    "SearchHistoryCreate",
    "SearchHistoryResponse",
    "SearchHistoryListResponse",
    "AlertBase",
    "AlertCreate",
    "AlertUpdate",
    "AlertResponse",
    "AlertListResponse",
]
