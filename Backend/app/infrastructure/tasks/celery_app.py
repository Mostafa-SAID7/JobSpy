"""
Celery Configuration for Background Tasks
"""

from celery import Celery

from app.config.settings import settings
from app.infrastructure.tasks.celery_beat_schedule import CELERY_BEAT_SCHEDULE, CELERY_TIMEZONE

# Create Celery app
celery_app = Celery(
    "jobspy",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone=CELERY_TIMEZONE,
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    beat_schedule=CELERY_BEAT_SCHEDULE,
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["app"])


@celery_app.task(bind=True)
def debug_task(self):
    """
    Debug task for testing Celery
    """
    print(f"Request: {self.request!r}")
