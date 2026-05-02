"""
Celery Beat Schedule
Celery Beat Schedule Configuration for JobSpy
"""

from celery.schedules import crontab
from datetime import timedelta

# Celery Beat Schedule Configuration
CELERY_BEAT_SCHEDULE = {
    # Scraping Tasks - Run every hour
    "scrape-linkedin-hourly": {
        "task": "app.tasks.scrape_linkedin_jobs",
        "schedule": timedelta(hours=1),
        "args": ("python developer",),
        "options": {"queue": "scraping"},
    },
    "scrape-indeed-hourly": {
        "task": "app.tasks.scrape_indeed_jobs",
        "schedule": timedelta(hours=1),
        "args": ("python developer",),
        "options": {"queue": "scraping"},
    },
    "scrape-wuzzuf-hourly": {
        "task": "app.tasks.scrape_wuzzuf_jobs",
        "schedule": timedelta(hours=1),
        "args": ("python developer",),
        "options": {"queue": "scraping"},
    },
    "scrape-bayt-hourly": {
        "task": "app.tasks.scrape_bayt_jobs",
        "schedule": timedelta(hours=1),
        "args": ("python developer",),
        "options": {"queue": "scraping"},
    },
    
    # Alert Tasks - Run every 30 minutes
    "check-alerts": {
        "task": "app.tasks.check_alerts",
        "schedule": timedelta(minutes=30),
        "options": {"queue": "alerts"},
    },
    "schedule-alerts": {
        "task": "app.tasks.schedule_alerts",
        "schedule": timedelta(hours=1),
        "options": {"queue": "alerts"},
    },
    
    # Maintenance Tasks - Run daily at 2 AM UTC
    "daily-maintenance": {
        "task": "app.tasks.run_daily_maintenance",
        "schedule": crontab(hour=2, minute=0),
        "options": {"queue": "maintenance"},
    },
    "cleanup-old-data": {
        "task": "app.tasks.cleanup_old_data",
        "schedule": crontab(hour=3, minute=0),
        "args": (90,),
        "options": {"queue": "maintenance"},
    },
    "update-statistics": {
        "task": "app.tasks.update_statistics",
        "schedule": crontab(hour=4, minute=0),
        "options": {"queue": "maintenance"},
    },
    "backup-database": {
        "task": "app.tasks.backup_database",
        "schedule": crontab(hour=5, minute=0),
        "options": {"queue": "maintenance"},
    },
}

# Celery Beat Configuration
CELERY_BEAT_SCHEDULER = "celery.beat:PersistentScheduler"

# Celery Timezone
CELERY_TIMEZONE = "UTC"
