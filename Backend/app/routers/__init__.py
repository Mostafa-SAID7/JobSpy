from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.jobs import router as jobs_router
from app.routers.saved_jobs import router as saved_jobs_router
from app.routers.alerts import router as alerts_router

__all__ = [
    "auth_router",
    "users_router",
    "jobs_router",
    "saved_jobs_router",
    "alerts_router",
]
